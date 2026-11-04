#!/usr/bin/env bash
# macOS / Linux 开发入口（Makefile 只是对它的转发）
#   ./scripts/unix/dev.sh topik-api | course-api | web | build | images
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

case "${1:-}" in
  topik-api)  cd "$ROOT/topik/backend" && ../.venv/bin/python manage.py runserver 8000 ;;
  course-api) cd "$ROOT/course" && uv run python backend/manage.py runserver 8001 ;;
  web)        cd "$ROOT/web" && pnpm dev ;;
  build)      cd "$ROOT/web" && pnpm run build ;;
  images)     cd "$ROOT" && uv run scripts/optimize_images.py ;;
  *) sed -n '2,3p' "$0"; exit 1 ;;
esac
