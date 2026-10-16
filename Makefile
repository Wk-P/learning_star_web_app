# 本地开发：topik 后端 :8000，course 后端 :8001，前端 web/ :5173（代理 /api/topik、/api/course、/media）
.PHONY: dev-topik-api dev-course-api dev-web build images deploy-web deploy-topik deploy-course deploy-nginx

dev-topik-api:
	cd topik/backend && ../.venv/bin/python manage.py runserver 8000
dev-course-api:
	cd course && uv run python backend/manage.py runserver 8001
dev-web:
	cd web && pnpm dev

build:
	cd web && pnpm run build
images:
	uv run scripts/optimize_images.py

deploy-web:    ; ./deploy/deploy.sh web
deploy-topik:  ; ./deploy/deploy.sh topik
deploy-course: ; ./deploy/deploy.sh course
deploy-nginx:  ; ./deploy/deploy.sh nginx
