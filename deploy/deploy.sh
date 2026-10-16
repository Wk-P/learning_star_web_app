#!/usr/bin/env bash
# 部署到上海节点（sshgo 中的 shanghai_node）
#   ./deploy/deploy.sh topik    构建并部署韩途
#   ./deploy/deploy.sh course   构建并部署课程站
#   ./deploy/deploy.sh nginx    安装 80 端口统一入口 + systemd 单元（首次/变更时）
#   ./deploy/deploy.sh all
#
# 永不覆盖服务器上的：media/、db.sqlite3、.env*、staticfiles/、course 的 bilibili/ 数据
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH_HOST="${SSH_HOST:-ecs-user@139.224.222.27}"
SSH_OPTS=(-p "${SSH_PORT:-20022}" -i "${SSH_KEY:-$HOME/.ssh/ssh-key/shanghai_node/returnNodeKey.pem}" -o ServerAliveInterval=60)
REMOTE_HOME=/home/ecs-user

ssh_run() { ssh "${SSH_OPTS[@]}" "$SSH_HOST" "$@"; }
sync() { rsync -az --info=stats1 -e "ssh ${SSH_OPTS[*]}" "$@"; }

BACKEND_EXCLUDES=(
  --exclude '__pycache__/' --exclude '*.pyc'
  --exclude 'media/' --exclude 'staticfiles/'
  --exclude 'db.sqlite3*' --exclude '.env*'
)

build_frontend() {
  (cd "$ROOT/$1/frontend" && pnpm install --frozen-lockfile && pnpm run build)
}

deploy_topik() {
  local dst="$REMOTE_HOME/player3"
  build_frontend topik
  sync --delete "$ROOT/topik/frontend/dist/" "$SSH_HOST:$dst/frontend/dist/"
  sync "${BACKEND_EXCLUDES[@]}" "$ROOT/topik/backend/" "$SSH_HOST:$dst/backend/"
  sync "$ROOT/topik/requirements.txt" "$SSH_HOST:$dst/"
  ssh_run "set -e; cd $dst
    grep -q '^MEDIA_URL=' backend/.env.production || echo 'MEDIA_URL=/topik/media/' >> backend/.env.production
    grep -q '^STATIC_URL=' backend/.env.production || echo 'STATIC_URL=/topik/static/' >> backend/.env.production
    .venv/bin/pip install -q -r requirements.txt
    cd backend && export DJANGO_ENV=production
    ../.venv/bin/python manage.py migrate --noinput
    ../.venv/bin/python manage.py collectstatic --noinput -v 0
    sudo systemctl restart player3 && systemctl is-active player3"
}

deploy_course() {
  local dst="$REMOTE_HOME/course_system"
  build_frontend course
  sync --delete "$ROOT/course/frontend/dist/" "$SSH_HOST:$dst/frontend/dist/"
  sync "${BACKEND_EXCLUDES[@]}" --exclude 'bilibili/' "$ROOT/course/backend/" "$SSH_HOST:$dst/backend/"
  sync "$ROOT/course/pyproject.toml" "$ROOT/course/uv.lock" "$SSH_HOST:$dst/"
  ssh_run "set -e; cd $dst
    test -f .env || { echo '缺少 $dst/.env，模板见 deploy/env/course.env.example' >&2; exit 1; }
    /snap/bin/uv sync --frozen --no-dev -q
    cd backend && set -a && . ../.env && set +a
    ../.venv/bin/python manage.py migrate --noinput
    sudo systemctl restart course-backend && systemctl is-active course-backend"
}

deploy_nginx() {
  local dst="$REMOTE_HOME/learning_star"
  ssh_run "mkdir -p $dst"
  sync --delete "$ROOT/deploy/" "$SSH_HOST:$dst/deploy/"
  sync --delete "$ROOT/deploy/landing/" "$SSH_HOST:$dst/landing/"
  ssh_run "set -e; cd $dst/deploy
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

case "${1:-}" in
  topik)  deploy_topik ;;
  course) deploy_course ;;
  nginx)  deploy_nginx ;;
  all)    deploy_nginx; deploy_topik; deploy_course ;;
  *) sed -n '2,8p' "$0"; exit 1 ;;
esac
