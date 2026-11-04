#!/usr/bin/env bash
# 部署到生产服务器。服务器信息读取 deploy/.env（不进 git），模板见 deploy/.env.example
#   ./scripts/unix/deploy.sh check      只读检查：SSH 连接、目录、JWT 密钥一致、服务状态（部署前先跑）
#   ./scripts/unix/deploy.sh web        构建并部署前端（web/）
#   ./scripts/unix/deploy.sh topik      部署 topik 后端（账号/登录、韩语资源）
#   ./scripts/unix/deploy.sh course     部署 course 后端（只有代码，不碰数据）
#   ./scripts/unix/deploy.sh pull-data  把服务器上的 B 站链接数据拉到本地（course/backend/bilibili/）
#   ./scripts/unix/deploy.sh push-data  把本地改好的 B 站链接数据推回服务器（需先 pull-data）
#   ./scripts/unix/deploy.sh nginx      安装 80 端口统一入口 + systemd 单元（首次/变更时）
#   ./scripts/unix/deploy.sh users      预览 course 账号并入 topik；加 --apply 真正写入
#   ./scripts/unix/deploy.sh all        topik → course → web → nginx
#
# 代码部署永不覆盖服务器上的数据：media/、db.sqlite3、.env*、staticfiles/、course 的 bilibili/
# bilibili/ 只能用 pull-data / push-data 单独同步；push-data 会在服务器自 pull-data 后被改过时中止
# 本机有 rsync 时增量同步；没有时（如 Windows 的 Git Bash）自动改用 tar + ssh 全量上传，效果相同。
# Windows 请用 .\scripts\windows\deploy.ps1，参数相同。
set -euo pipefail

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 1; }
case "${1:-}" in
  check|web|topik|course|pull-data|push-data|nginx|users|all) ;;
  *) usage ;;
esac

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_FILE="${DEPLOY_ENV:-$ROOT/deploy/.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "缺少 ${ENV_FILE}：复制 deploy/.env.example 为 deploy/.env 后填写服务器信息" >&2; exit 1
fi

# 逐行读取 .env 而不是 source：兼容 Windows 记事本保存的 CRLF，以及 C:\ 形式的路径
# 已在环境变量中设置的值优先（便于临时覆盖，如 SSH_HOST=… ./scripts/unix/deploy.sh web）
load_env() {
  local line k v
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    [[ $line =~ ^[[:space:]]*([A-Z_]+)=(.*)$ ]] || continue
    k=${BASH_REMATCH[1]}; v=${BASH_REMATCH[2]}
    case $k in SSH_HOST|SSH_PORT|SSH_KEY|REMOTE_HOME|TOPIK_DIR|COURSE_DIR|WEB_DIR) ;; *) continue ;; esac
    if [[ $v =~ ^\"(.*)\"$ || $v =~ ^\'(.*)\'$ ]]; then v=${BASH_REMATCH[1]}; fi
    [ -n "${!k:-}" ] || printf -v "$k" '%s' "$v"
  done < "$1"
}
load_env "$ENV_FILE"

for v in SSH_HOST SSH_PORT SSH_KEY REMOTE_HOME; do
  [ -n "${!v:-}" ] || { echo "${ENV_FILE} 缺少 ${v}" >&2; exit 1; }
done
SSH_KEY="${SSH_KEY/#\~/$HOME}"
# Git Bash：把 C:\Users\… 转成 /c/Users/…
command -v cygpath >/dev/null 2>&1 && SSH_KEY="$(cygpath -u "$SSH_KEY")"
[ -f "$SSH_KEY" ] || { echo "找不到 SSH 私钥：${SSH_KEY}（deploy/.env 的 SSH_KEY）" >&2; exit 1; }
SSH_OPTS=(-p "$SSH_PORT" -i "$SSH_KEY" -o ServerAliveInterval=60)
TOPIK_DIR="${TOPIK_DIR:-$REMOTE_HOME/player3}"
COURSE_DIR="${COURSE_DIR:-$REMOTE_HOME/course_system}"
WEB_DIR="${WEB_DIR:-$REMOTE_HOME/learning_star}"

for c in ssh tar pnpm; do
  command -v "$c" >/dev/null 2>&1 || { echo "缺少命令：${c}" >&2; exit 1; }
done
HAVE_RSYNC=; command -v rsync >/dev/null 2>&1 && HAVE_RSYNC=1

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

# ── 文件同步：有 rsync 用 rsync，否则 tar + ssh ──
# 服务器端解压：不改属主，不改已存在目录的权限
UNTAR="tar -xzf - --no-same-owner --no-overwrite-dir"
# COPYFILE_DISABLE：macOS 的 bsdtar 不要打包 ._* 元数据文件
tar_up() { local dir=$1; shift; COPYFILE_DISABLE=1 tar -C "$dir" -czf - "$@"; }

# push_dir [--delete] <本地目录> <远程目录> [排除模式...]
#   排除的内容不上传；--delete 删除服务器上多余的文件，但排除的内容保留（同 rsync --delete --exclude）
push_dir() {
  local del=; [ "$1" = --delete ] && { del=1; shift; }
  local src=$1 dst=$2; shift 2
  local p ex=()
  if [ -n "$HAVE_RSYNC" ]; then
    for p in "$@"; do ex+=(--exclude "$p"); done
    rsync -az ${del:+--delete} ${ex[@]+"${ex[@]}"} -e "ssh ${SSH_OPTS[*]}" "$src/" "$SSH_HOST:$dst/"
    return
  fi
  for p in "$@"; do ex+=("--exclude=${p%/}"); done
  if [ -z "$del" ]; then
    tar_up "$src" ${ex[@]+"${ex[@]}"} . | ssh_run "mkdir -p '$dst' && $UNTAR -C '$dst'"
  else
    # 解压到临时目录 → 带回被排除的旧内容 → 整体替换，避免出现半更新状态
    local keep=; for p in "$@"; do keep+=" ${p%/}"; done
    local restore=
    [ -n "$keep" ] && restore="(cd \"\$d\" && for f in $keep; do if [ -e \"\$f\" ]; then cp -a \"\$f\" \"\$new/\"; fi; done)"
    tar_up "$src" ${ex[@]+"${ex[@]}"} . | ssh_run "set -e
      d='$dst'; new=\"\$d.new.\$\$\"; old=\"\$d.old.\$\$\"
      mkdir -p \"\$d\" \"\$new\"
      $UNTAR -C \"\$new\"
      $restore
      mv \"\$d\" \"\$old\"; mv \"\$new\" \"\$d\"; rm -rf \"\$old\""
  fi
}

# push_files <本地目录> <远程目录> <文件名...>
push_files() {
  local src=$1 dst=$2; shift 2
  if [ -n "$HAVE_RSYNC" ]; then
    rsync -az -e "ssh ${SSH_OPTS[*]}" "${@/#/$src/}" "$SSH_HOST:$dst/"
  else
    tar_up "$src" "$@" | ssh_run "mkdir -p '$dst' && $UNTAR -C '$dst'"
  fi
}

BACKEND_EXCLUDES=('__pycache__/' '*.pyc' 'media/' 'staticfiles/' 'db.sqlite3*' '.env*')

# 统一登录要求两个后端的 JWT_SIGNING_KEY 一致
check_jwt_key() {
  ssh_run "set -e
    t=\$(grep -s '^JWT_SIGNING_KEY=' $TOPIK_DIR/backend/.env.production | cut -d= -f2-)
    c=\$(grep -s '^JWT_SIGNING_KEY=' $COURSE_DIR/.env | cut -d= -f2-)
    if [ -z \"\$t\" ] || [ \"\$t\" != \"\$c\" ]; then
      echo '两个后端的 JWT_SIGNING_KEY 缺失或不一致，见 deploy/env/*.example' >&2; exit 1
    fi"
}

# 只读：不改动服务器上的任何内容
check_server() {
  ssh_run "echo \"已连接 \$(whoami)@\$(hostname)\"
    for d in $TOPIK_DIR/.venv $COURSE_DIR/.venv $WEB_DIR; do
      [ -d \"\$d\" ] && echo \"  目录 \$d\" || echo \"  缺少目录 \$d\"
    done
    echo \"  服务 player3=\$(systemctl is-active player3) course-backend=\$(systemctl is-active course-backend) nginx=\$(systemctl is-active nginx)\"
    sudo -n true 2>/dev/null && echo '  sudo 免密可用' || echo '  sudo 需要密码（部署中的 systemctl/nginx 步骤会失败）'"
  check_jwt_key && echo "  两个后端的 JWT_SIGNING_KEY 一致"
}

deploy_web() {
  (cd "$ROOT/web" && pnpm install --frozen-lockfile && pnpm run build)
  ssh_run "mkdir -p $WEB_DIR/web"
  push_dir --delete "$ROOT/web/dist" "$WEB_DIR/web/dist"
}

deploy_topik() {
  push_dir "$ROOT/topik/backend" "$TOPIK_DIR/backend" "${BACKEND_EXCLUDES[@]}"
  push_files "$ROOT/topik" "$TOPIK_DIR" pyproject.toml uv.lock .python-version
  # 与 course 相同：按 uv.lock 精确同步 .venv（systemd 仍使用 .venv/bin/gunicorn）
  ssh_run "set -e; cd $TOPIK_DIR
    rm -f requirements.txt
    /snap/bin/uv sync --frozen --no-dev -q
    cd backend && export DJANGO_ENV=production
    ../.venv/bin/python manage.py migrate --noinput
    ../.venv/bin/python manage.py collectstatic --noinput -v 0
    sudo systemctl restart player3 && systemctl is-active player3"
}

BILI_DIR="$ROOT/course/backend/bilibili"
BILI_REMOTE="$COURSE_DIR/backend/bilibili"
BILI_SNAPSHOT="$BILI_DIR/.remote-snapshot"

# 服务器上 bilibili/*.txt 的整体指纹
remote_bili_hash() {
  ssh_run "cd $BILI_REMOTE && find . -maxdepth 1 -name '*.txt' -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1"
}

# 只同步 bilibili/ 下的 *.txt，不删除任何一侧的文件
pull_txt() {
  if [ -n "$HAVE_RSYNC" ]; then
    rsync -az --include '*.txt' --exclude '*' -e "ssh ${SSH_OPTS[*]}" "$SSH_HOST:$BILI_REMOTE/" "$BILI_DIR/"
  else
    ssh_run "cd $BILI_REMOTE && find . -maxdepth 1 -name '*.txt' -print0 | tar -czf - --null -T -" | tar -xzf - -C "$BILI_DIR"
  fi
}
push_txt() {
  if [ -n "$HAVE_RSYNC" ]; then
    rsync -az --include '*.txt' --exclude '*' -e "ssh ${SSH_OPTS[*]}" "$BILI_DIR/" "$SSH_HOST:$BILI_REMOTE/"
  else
    (cd "$BILI_DIR" && find . -maxdepth 1 -name '*.txt' -print0 | tar -czf - --null -T -) | ssh_run "$UNTAR -C $BILI_REMOTE"
  fi
}

pull_data() {
  mkdir -p "$BILI_DIR"
  pull_txt
  remote_bili_hash > "$BILI_SNAPSHOT"
  echo "已拉取服务器数据到 ${BILI_DIR}，修改后用 push-data 推送"
}

push_data() {
  if [ ! -f "$BILI_SNAPSHOT" ]; then
    echo "本地没有 pull-data 快照，请先运行 pull-data" >&2; exit 1
  fi
  if [ "$(remote_bili_hash)" != "$(cat "$BILI_SNAPSHOT")" ]; then
    echo "服务器上的 B 站链接数据在 pull-data 之后被改过（后台编辑？），为避免覆盖已中止推送。" >&2
    echo "请先重新 pull-data，再在本地修改。" >&2
    exit 1
  fi
  ssh_run "cp -a $BILI_REMOTE $BILI_REMOTE.bak-\$(date +%Y%m%d%H%M%S)"
  push_txt
  remote_bili_hash > "$BILI_SNAPSHOT"
  echo "B 站链接数据已推送（服务器旧数据已备份为 bilibili.bak-*）"
}

deploy_course() {
  push_dir "$ROOT/course/backend" "$COURSE_DIR/backend" "${BACKEND_EXCLUDES[@]}" 'bilibili/'
  push_files "$ROOT/course" "$COURSE_DIR" pyproject.toml uv.lock
  ssh_run "set -e; cd $COURSE_DIR
    test -f .env || { echo '缺少 $COURSE_DIR/.env，模板见 deploy/env/course.env.example' >&2; exit 1; }
    /snap/bin/uv sync --frozen --no-dev -q
    cd backend && set -a && . ../.env && set +a
    ../.venv/bin/python manage.py migrate --noinput
    sudo systemctl restart course-backend && systemctl is-active course-backend"
}

deploy_nginx() {
  ssh_run "mkdir -p $WEB_DIR"
  push_dir --delete "$ROOT/deploy" "$WEB_DIR/deploy" '.env*'
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

[ -n "$HAVE_RSYNC" ] || echo "（未找到 rsync，改用 tar + ssh 上传）"
trap print_timing EXIT

case "$1" in
  check)  step check check_server ;;
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
esac
