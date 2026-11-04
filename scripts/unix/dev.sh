#!/usr/bin/env bash
# macOS / Linux 本地开发入口（Makefile 转发到这里；Windows 用 scripts/windows/dev.ps1）
#   ./scripts/unix/dev.sh setup        首次：安装两个后端（uv sync）与前端依赖，生成 .env.develop
#   ./scripts/unix/dev.sh all          同时启动下面三个服务，Ctrl-C 全部停止
#   ./scripts/unix/dev.sh topik-api    topik 后端 :8000
#   ./scripts/unix/dev.sh course-api   course 后端 :8001
#   ./scripts/unix/dev.sh web          前端 :5173（代理 /api/topik、/api/course、/media）
#   ./scripts/unix/dev.sh build        构建前端
#   ./scripts/unix/dev.sh images       由 images/src 重新生成 web/public 图片
#
# 依赖：uv（https://docs.astral.sh/uv/）、Node ^20.19 或 >=22.12、pnpm
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# Python 文件读写统一 UTF-8（macOS/Linux 本来就是；在 Windows 的 Git Bash 里运行时才起作用）
export PYTHONUTF8=1

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "缺少 $1：$2" >&2; exit 1; }; }

setup() {
  need uv 'https://docs.astral.sh/uv/getting-started/installation/'
  need pnpm 'corepack enable 或 npm i -g pnpm'
  # 两个后端都是 uv 项目：各自的 .venv 由 uv sync 按 uv.lock 创建（topik 为 Python 3.10，course 为 3.13）
  (cd "$ROOT/topik" && uv sync)
  local env_dev="$ROOT/topik/backend/.env.develop"
  if [ ! -f "$env_dev" ]; then
    cp "$env_dev.example" "$env_dev"
    echo "已生成 topik/backend/.env.develop，按需修改"
  fi
  (cd "$ROOT/course" && uv sync)
  (cd "$ROOT/web" && pnpm install)
  echo "完成。启动：$0 all"
}

ALL_PIDS=()
stop_all() {
  trap - INT TERM EXIT
  # Git Bash：Windows 原生进程（python.exe、node.exe）收不到 kill 信号，按进程树结束
  if command -v taskkill >/dev/null 2>&1; then
    local p
    for p in ${ALL_PIDS[@]+"${ALL_PIDS[@]}"}; do
      [ -r "/proc/$p/winpid" ] && taskkill //F //T //PID "$(cat "/proc/$p/winpid")" >/dev/null 2>&1
    done
  fi
  kill 0 2>/dev/null
}

run_all() {
  # 任一服务退出或 Ctrl-C 时停止全部
  trap stop_all INT TERM EXIT
  local t
  for t in topik-api course-api web; do "$0" "$t" & ALL_PIDS+=($!); done
  wait -n 2>/dev/null || wait
}

case "${1:-}" in
  setup)      setup ;;
  all)        run_all ;;
  topik-api)  cd "$ROOT/topik/backend" && exec uv run python manage.py runserver 8000 ;;
  course-api) cd "$ROOT/course" && exec uv run python backend/manage.py runserver 8001 ;;
  web)        cd "$ROOT/web" && exec pnpm dev ;;
  build)      cd "$ROOT/web" && exec pnpm run build ;;
  images)     cd "$ROOT" && exec uv run scripts/optimize_images.py ;;
  *)          usage ;;
esac
