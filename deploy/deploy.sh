#!/usr/bin/env bash
# 部署到上海节点（sshgo 中的 shanghai_node）
#   ./deploy/deploy.sh web      构建并部署前端（web/）
#   ./deploy/deploy.sh topik    部署 topik 后端（账号/登录、韩语资源）
#   ./deploy/deploy.sh course   部署 course 后端（科目、B 站链接、路线图）
#   ./deploy/deploy.sh nginx    安装 80 端口统一入口 + systemd 单元（首次/变更时）
#   ./deploy/deploy.sh users    预览 course 账号并入 topik；加 --apply 真正写入
#   ./deploy/deploy.sh all      topik → course → web → nginx
#
# 永不覆盖服务器上的：media/、db.sqlite3、.env*、staticfiles/、course 的 bilibili/ 数据
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH_HOST="${SSH_HOST:-ecs-user@139.224.222.27}"
SSH_OPTS=(-p "${SSH_PORT:-20022}" -i "${SSH_KEY:-$HOME/.ssh/ssh-key/shanghai_node/returnNodeKey.pem}" -o ServerAliveInterval=60)
REMOTE_HOME=/home/ecs-user
TOPIK_DIR=$REMOTE_HOME/player3
COURSE_DIR=$REMOTE_HOME/course_system
WEB_DIR=$REMOTE_HOME/learning_star

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
  sync --delete "$ROOT/deploy/" "$SSH_HOST:$WEB_DIR/deploy/"
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
  web)    deploy_web ;;
  topik)  deploy_topik ;;
  course) deploy_course ;;
  nginx)  check_jwt_key; deploy_nginx ;;
  users)  shift; import_users "$@" ;;
  all)    check_jwt_key; deploy_topik; deploy_course; deploy_web; deploy_nginx ;;
  *) sed -n '2,10p' "$0"; exit 1 ;;
esac
