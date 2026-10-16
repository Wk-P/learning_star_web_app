# learning_star_web_app

合并仓库，包含两个独立子项目（各自保留完整 git 历史，通过 `git subtree` 合并）：

- `course/` — 课程网站（原 [m22-Course-System](https://github.com/Wk-P/m22-Course-System)）
- `topik/` — TOPIK 学习网站·韩途（原 [player3](https://github.com/Wk-P/player3)）

两站计划合并部署到同一上海节点 IP 的 80 端口下，路径分别为 `/course/` 与 `/topik/`。

## 部署结构（上海节点 `shanghai_node`，139.224.222.27）

| 路径 | 前端 dist | 后端 |
|---|---|---|
| `/` | `~/learning_star/landing` | — |
| `/topik/` | `~/player3/frontend/dist` | `player3.service` → gunicorn `127.0.0.1:8000`，`/topik/api/`、`/topik/media/`（经 Django 鉴权） |
| `/course/` | `~/course_system/frontend/dist` | `course-backend.service` → gunicorn `127.0.0.1:8001`，`/course/api/` |

nginx 去掉 `/topik`、`/course` 前缀后转发给后端，因此后端路由无需改动；前端在 production 模式下使用对应 `base` 与 API 前缀。

```bash
./deploy/deploy.sh nginx    # 首次：安装统一 80 端口配置 + systemd 单元（旧配置改名为 .bak）
./deploy/deploy.sh topik    # 构建并部署韩途
./deploy/deploy.sh course   # 构建并部署课程站
```

部署永不覆盖服务器上的 `media/`、`db.sqlite3`、`.env*`、`staticfiles/` 与课程站 `bilibili/` 数据。
服务器端环境变量模板见 `deploy/env/`。

## 本地开发

```bash
make dev-topik-api   # :8000      make dev-topik-web   # :5173
make dev-course-api  # :8001      make dev-course-web  # :5174
```
