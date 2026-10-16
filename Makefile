# 本地开发：topik 后端 :8000，course 后端 :8001，前端各自 vite (:5173 / :5174)
.PHONY: dev-topik-api dev-topik-web dev-course-api dev-course-web build deploy-topik deploy-course deploy-nginx

dev-topik-api:
	cd topik/backend && ../.venv/bin/python manage.py runserver 8000
dev-topik-web:
	cd topik/frontend && pnpm dev --port 5173
dev-course-api:
	cd course && uv run python backend/manage.py runserver 8001
dev-course-web:
	cd course/frontend && pnpm dev --port 5174

build:
	cd topik/frontend && pnpm run build
	cd course/frontend && pnpm run build

deploy-topik:  ; ./deploy/deploy.sh topik
deploy-course: ; ./deploy/deploy.sh course
deploy-nginx:  ; ./deploy/deploy.sh nginx
