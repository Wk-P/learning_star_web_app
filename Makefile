# macOS / Linux 的入口，实际逻辑在 scripts/unix/；Windows 见 scripts/windows/
.PHONY: dev-topik-api dev-course-api dev-web build images deploy-web deploy-topik deploy-course deploy-nginx

dev-topik-api:  ; ./scripts/unix/dev.sh topik-api
dev-course-api: ; ./scripts/unix/dev.sh course-api
dev-web:        ; ./scripts/unix/dev.sh web
build:          ; ./scripts/unix/dev.sh build
images:         ; ./scripts/unix/dev.sh images

deploy-web:    ; ./scripts/unix/deploy.sh web
deploy-topik:  ; ./scripts/unix/deploy.sh topik
deploy-course: ; ./scripts/unix/deploy.sh course
deploy-nginx:  ; ./scripts/unix/deploy.sh nginx
