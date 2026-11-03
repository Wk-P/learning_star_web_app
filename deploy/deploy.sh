#!/usr/bin/env bash
# 部署到生产服务器。服务器信息读取 deploy/.env（不进 git），模板见 deploy/.env.example
#   ./deploy/deploy.sh web      构建并部署前端（web/）
#   ./deploy/deploy.sh topik    部署 topik 后端（账号/登录、韩语资源）
#   ./deploy/deploy.sh course   部署 course 后端（只有代码，不碰数据）
#   ./deploy/deploy.sh pull-data 把服务器上的 B 站链接数据拉到本地（course/backend/bilibili/）
#   ./deploy/deploy.sh push-data 把本地改好的 B 站链接数据推回服务器（需先 pull-data）
#   ./deploy/deploy.sh nginx    安装 80 端口统一入口 + systemd 单元（首次/变更时）
#   ./deploy/deploy.sh users    预览 course 账号并入 topik；加 --apply 真正写入
#   ./deploy/deploy.sh all      topik → course → web → nginx
#
# 代码部署永不覆盖服务器上的数据：media/、db.sqlite3、.env*、staticfiles/、course 的 bilibili/
# bilibili/ 只能用 pull-data / push-data 单独同步；push-data 会在服务器自 pull-data 后被改过时中止
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${DEPLOY_ENV:-$ROOT/deploy/.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "缺少 ${ENV_FILE}：cp deploy/.env.example deploy/.env 后填写服务器信息" >&2; exit 1
fi
# 已在环境变量中设置的值优先（便于临时覆盖），其余从 .env 读取
_preset=$(env | grep -E '^(SSH_|REMOTE_HOME=|TOPIK_DIR=|COURSE_DIR=|WEB_DIR=)' || true)
set -a; . "$ENV_FILE"; set +a
[ -n "$_preset" ] && while IFS= read -r kv; do export "$kv"; done <<< "$_preset"

for v in SSH_HOST SSH_PORT SSH_KEY REMOTE_HOME; do
  [ -n "${!v:-}" ] || { echo "${ENV_FILE} 缺少 ${v}" >&2; exit 1; }
done
SSH_KEY="${SSH_KEY/#\~/$HOME}"
SSH_OPTS=(-p "$SSH_PORT" -i "$SSH_KEY" -o ServerAliveInterval=60)
TOPIK_DIR="${TOPIK_DIR:-$REMOTE_HOME/player3}"
COURSE_DIR="${COURSE_DIR:-$REMOTE_HOME/course_system}"
WEB_DIR="${WEB_DIR:-$REMOTE_HOME/learning_star}"

# ── 计时：每一步单独计时，结束（含失败）时打印汇总 ──
START_TS=$(date +%s)
TIMINGS=()
CURRENT_STEP=

fmt_secs() { local t=$1; (( t >= 60 )) && printf '%dm%02ds' $((t / 60)) $((t % 60)) || printf '%ds' "$t"; }

# step <名称> <命令...>：运行并记录耗时
step() {
  local name=$1; shift
  local t0=$(date +%s)
  CURRENT_STEP=$name
  echo "▶ ${name} …"
  "$@"
  local dt=$(( $(date +%s) - t0 ))
  TIMINGS+=("$name|$dt")
  CURRENT_STEP=
  echo "✔ ${name} 完成，用时 $(fmt_secs "$dt")"
}

print_timing() {
  local rc=$?
  (( ${#TIMINGS[@]} > 1 )) && { echo "── 各步骤用时 ──"; for e in "${TIMINGS[@]}"; do printf '  %-10s %s\n' "${e%%|*}" "$(fmt_secs "${e##*|}")"; done; }
  local total=$(fmt_secs $(( $(date +%s) - START_TS )))
  (( rc == 0 )) && echo "全部完成，总用时 ${total}" || echo "${CURRENT_STEP:+[${CURRENT_STEP}] }失败（退出码 ${rc}），已运行 ${total}" >&2
}

ssh_run() { ssh "${SSH_OPTS[@]}" "$SSH_HOST" "$@"; }
sync() { rsync -az -e "ssh ${SSH_OPTS[*]}" "$@"; }

BACKEND_EXCLUDES=(
  --exclude '__pycache__/' --exclude '*.pyc'
  --exclude 'media/' --exclude 'staticfiles/'
  --exclude 'db.sqlite3*' --exclude '.env*'
)

# 统一登录要求两个后端的 JWT_SIGNING_KEY 一致
check_jwt_key() {
  ssh_run "set -e
    t=\$(grep -s '^JWT_SIGNING_KEY=' $TOPIK_DIR/backend/.env.production | cut -d= -f2-)
    c=\$(grep -s '^JWT_SIGNING_KEY=' $COURSE_DIR/.env | cut -d= -f2-)
    if [ -z \"\$t\" ] || [ \"\$t\" != \"\$c\" ]; then
      echo '两个后端的 JWT_SIGNING_KEY 缺失或不一致，见 deploy/env/*.example' >&2; exit 1
    fi"
}

deploy_web() {
  (cd "$ROOT/web" && pnpm install --frozen-lockfile && pnpm run build)
  ssh_run "mkdir -p $WEB_DIR/web"
  sync --delete "$ROOT/web/dist/" "$SSH_HOST:$WEB_DIR/web/dist/"
}

deploy_topik() {
  sync "${BACKEND_EXCLUDES[@]}" "$ROOT/topik/backend/" "$SSH_HOST:$TOPIK_DIR/backend/"
  sync "$ROOT/topik/requirements.txt" "$SSH_HOST:$TOPIK_DIR/"
  ssh_run "set -e; cd $TOPIK_DIR
    .venv/bin/pip install -q -r requirements.txt
    cd backend && export DJANGO_ENV=production
    ../.venv/bin/python manage.py migrate --noinput
    ../.venv/bin/python manage.py collectstatic --noinput -v 0
    sudo systemctl restart player3 && systemctl is-active player3"
}

BILI_DIR="$ROOT/course/backend/bilibili"
BILI_SNAPSHOT="$BILI_DIR/.remote-snapshot"

# 服务器上 bilibili/*.txt 的整体指纹
remote_bili_hash() {
  ssh_run "cd $COURSE_DIR/backend/bilibili && find . -maxdepth 1 -name '*.txt' -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1"
}

pull_data() {
  mkdir -p "$BILI_DIR"
  sync --include '*.txt' --exclude '*' "$SSH_HOST:$COURSE_DIR/backend/bilibili/" "$BILI_DIR/"
  remote_bili_hash > "$BILI_SNAPSHOT"
  echo "已拉取服务器数据到 ${BILI_DIR}，修改后用 ./deploy/deploy.sh course 推送"
}

push_data() {
  if [ ! -f "$BILI_SNAPSHOT" ]; then
    echo "本地没有 pull-data 快照，请先 ./deploy/deploy.sh pull-data" >&2; exit 1
  fi
  if [ "$(remote_bili_hash)" != "$(cat "$BILI_SNAPSHOT")" ]; then
    echo "服务器上的 B 站链接数据在 pull-data 之后被改过（后台编辑？），为避免覆盖已中止推送。" >&2
    echo "请先 ./deploy/deploy.sh pull-data 重新拉取，再在本地修改。" >&2
    exit 1
  fi
  ssh_run "cp -a $COURSE_DIR/backend/bilibili $COURSE_DIR/backend/bilibili.bak-\$(date +%Y%m%d%H%M%S)"
  sync --include '*.txt' --exclude '*' "$BILI_DIR/" "$SSH_HOST:$COURSE_DIR/backend/bilibili/"
  remote_bili_hash > "$BILI_SNAPSHOT"
  echo "B 站链接数据已推送（服务器旧数据已备份为 bilibili.bak-*）"
}

deploy_course() {
  sync "${BACKEND_EXCLUDES[@]}" --exclude 'bilibili/' "$ROOT/course/backend/" "$SSH_HOST:$COURSE_DIR/backend/"
  sync "$ROOT/course/pyproject.toml" "$ROOT/course/uv.lock" "$SSH_HOST:$COURSE_DIR/"
  ssh_run "set -e; cd $COURSE_DIR
    test -f .env || { echo '缺少 $COURSE_DIR/.env，模板见 deploy/env/course.env.example' >&2; exit 1; }
    /snap/bin/uv sync --frozen --no-dev -q
    cd backend && set -a && . ../.env && set +a
    ../.venv/bin/python manage.py migrate --noinput
    sudo systemctl restart course-backend && systemctl is-active course-backend"
}

deploy_nginx() {
  ssh_run "mkdir -p $WEB_DIR"
  sync --delete --exclude deploy.sh --exclude '.env*' "$ROOT/deploy/" "$SSH_HOST:$WEB_DIR/deploy/"
  ssh_run "set -e; cd $WEB_DIR/deploy
    sudo mkdir -p /etc/nginx/snippets
    sudo cp nginx/learning_star_proxy.conf /etc/nginx/snippets/
    sudo cp nginx/learning_star.conf /etc/nginx/conf.d/
    # 旧的分站配置（:80 player3 / :8080 course）停用，保留 .bak 便于回滚
    for f in player3 course_system; do
      [ -f /etc/nginx/conf.d/\$f.conf ] && sudo mv /etc/nginx/conf.d/\$f.conf /etc/nginx/conf.d/\$f.conf.bak || true
    done
    sudo cp systemd/player3.service systemd/course-backend.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo nginx -t && sudo systemctl reload nginx"
}

import_users() {
  ssh_run "cd $TOPIK_DIR/backend && DJANGO_ENV=production ../.venv/bin/python manage.py import_course_users $COURSE_DIR/backend/db.sqlite3 $*"
}

case "${1:-}" in
  web|topik|course|pull-data|push-data|nginx|users|all) trap print_timing EXIT ;;
esac

case "${1:-}" in
  web)    step web deploy_web ;;
  topik)  step topik deploy_topik ;;
  course) step course deploy_course ;;
  pull-data) step pull-data pull_data ;;
  push-data) step push-data push_data ;;
  nginx)  step jwt-check check_jwt_key; step nginx deploy_nginx ;;
  users)  shift; step users import_users "$@" ;;
  # nginx 步骤会更新 systemd 单元（含 EnvironmentFile），之后再重启一次两个后端使其生效
  all)    step jwt-check check_jwt_key; step topik deploy_topik; step course deploy_course
          step web deploy_web; step nginx deploy_nginx
          step restart ssh_run "sudo systemctl restart player3 course-backend && systemctl is-active player3 course-backend" ;;
  *) sed -n '2,13p' "$0"; exit 1 ;;
esac
