# macOS / Linux 入口，实际逻辑在 scripts/unix/；Windows 用 scripts/windows/*.ps1
.PHONY: setup dev dev-topik-api dev-course-api dev-web build images \
        deploy-web deploy-topik deploy-course deploy-nginx deploy-all

setup:          ; ./scripts/unix/dev.sh setup
dev:            ; ./scripts/unix/dev.sh all
dev-topik-api:  ; ./scripts/unix/dev.sh topik-api
dev-course-api: ; ./scripts/unix/dev.sh course-api
dev-web:        ; ./scripts/unix/dev.sh web
build:          ; ./scripts/unix/dev.sh build
images:         ; ./scripts/unix/dev.sh images

deploy-web:    ; ./scripts/unix/deploy.sh web
deploy-topik:  ; ./scripts/unix/deploy.sh topik
deploy-course: ; ./scripts/unix/deploy.sh course
deploy-nginx:  ; ./scripts/unix/deploy.sh nginx
deploy-all:    ; ./scripts/unix/deploy.sh all
