# course + topik 合并方案（merge 分支）

> 本文件是合并工作的唯一进度记录。每完成一步：勾选清单、在「进度日志」追加一行、git commit。
> compact / 换会话后从「进度清单」第一个未勾选项继续。

## 已定决策（2026-11-16，用户确认）

| 议题 | 决定 |
|---|---|
| 后端形态 | **单一 Django 项目**：一个 `backend/`、一个数据库、一张用户表、一个 gunicorn 服务 |
| Python 环境 | 根目录唯一 `pyproject.toml` + `uv.lock` + `.python-version`(3.13) → 根目录唯一 `.venv`；Django 6 |
| 栏目 | 两部分：**语言学习**（替代“韩语 TOPIK”）+ **课程** |
| 语言层级 | 语言学习 → 语言分类 → 具体语言；分类与语言是数据库记录，后台可增删改；初始：东亚语言 → 韩语（slug `ko`），现有 TOPIK 资源全部归入韩语 |
| 课程链接 | bilibili/*.txt **迁入数据库**（CourseVideo 表），去掉 pull-data / push-data |
| 线上目录 | 统一到 `~/learning_star`（代码、.venv、db、media）；player3 的 media 用 `mv` 移入（同盘改名，不复制）；旧目录保留作回滚 |
| 脚本 | 删除 Makefile、scripts/unix、scripts/windows；改为跨平台 Python 脚本 `scripts/dev.py`、`scripts/deploy.py` |

## 线上现状（来自 `_migration/backups/merge_backup_20261116-100534/`，未提交，本地保留）

采集脚本：`_migration/tools/collect_server_info.py`（只读，服务器上另留一份 `~/merge_backup_20261116-100534.zip`）。

- 服务器：Ubuntu，系统 Python 3.10.12；uv 0.12（/snap/bin/uv），已装 uv Python 3.14.5；磁盘剩余 70G
- topik：`~/player3`，Python 3.10 / Django 5.2，gunicorn :8000，服务 `player3`
  - DB 有数据的表：`user_user`(4)、`permission_mediapermission`(28)；video/audio/pdf 相关表 **全为 0 行**（资源靠扫描文件系统）
  - media：videos 82G（m3u8+ts，约 20 万文件）、audios 876M、pdfs 122M（含 1 个 xlsx、1 个 hwp）
  - 顶层目录（= 权限 root_dir）：video：102届TOPIK保命班 / topik韩语课 / 延世韩国语 / 直播回放 / 直播课 / 釜山班；audio：47/52/64/83_TOPIK2；pdf：TOPIK2_真题 / TOPIK_文档资料
- course：`~/course_system`，Python 3.14 / Django 6，gunicorn :8001，服务 `course-backend`
  - DB 有数据的表：`auth_user`(4，含 display_name/role/user_id)、`api_subject`(9)
  - `backend/bilibili/*.txt` 9 个科目文件（每行「标题 URL |等级 |标签」）+ template.html
  - `backend/media/course_files/` 若干 pdf/html：CourseFile 模型已在迁移 0010/0011 删除，**已是孤儿文件**，只归档不迁移
- 用户对照：
  - topik：admin(1)、soar009(2)、海盐薄荷(3)、bot(5)
  - course：admin、xujiahui(display_name 海盐薄荷冰激凌，**仅 course 有，带真实密码哈希**)、bot / 海盐薄荷（不可用密码，由统一登录自动创建）
  - ⇒ 合并后以 topik 为准保留 id 与密码；xujiahui 原样并入（保留密码哈希）；display_name 并入统一用户表
- 环境变量键：topik `DEBUG SECRET_KEY ALLOWED_HOSTS DB_ENGINE DB_NAME CORS_ALLOW_ALL_ORIGINS CORS_ALLOWED_ORIGINS JWT_SIGNING_KEY`；course `SECRET_KEY DEBUG ALLOWED_HOSTS CORS_ALLOWED_ORIGINS JWT_SIGNING_KEY`

## 目标结构

```
pyproject.toml  uv.lock  .python-version     # 唯一 Python 环境 → ./.venv
backend/
  manage.py
  config/          settings / urls / wsgi（读取根目录 .env）
  accounts/        统一用户（含 display_name）、登录/刷新令牌、注册、改密码、用户管理
  languages/       LanguageCategory、Language、MediaPermission(+language)、视频/音频/资料扫描、受保护媒体
  courses/         Subject、CourseVideo（原 txt）、等级/标签/平台识别
  data/            db.sqlite3、media/（不进 git）
web/               前端：src/topik → src/language；路由 /language/...
scripts/           dev.py、deploy.py、optimize_images.py（全部 Python，跨平台）
deploy/            nginx、systemd（单服务 learning-star）、env 模板
```

### 媒体目录

`data/media/languages/<语言slug>/{videos,audios,files}/<root_dir>/...`
（原 pdfs 改名 files，因已支持 xlsx/hwp）。URL：`/media/languages/ko/videos/...`。

### API（统一前缀 /api/）

| 旧 | 新 |
|---|---|
| /api/topik/auth/token[/refresh]/ | /api/auth/token[/refresh]/ |
| /api/topik/user/... | /api/accounts/...（me、password、register、管理员用户管理） |
| /api/topik/video|audio|pdf/list/ | /api/languages/<slug>/video|audio|file/ |
| /api/topik/permission/... | /api/languages/permissions/...（按语言） |
| — | /api/languages/categories/（分类+语言树，含当前用户可见性） |
| /api/course/subjects/... | /api/courses/subjects/...（视频改为数据库行，按 id 而非行号） |

### 前端路由

`/language`（分类与语言列表）→ `/language/:lang`（概览）→ `/language/:lang/video|audio|file`；
旧 `/topik/*`、`/user/*` 跳到 `/language/ko/*`；课程 `/course` 不变。管理后台：用户、语言（分类/语言管理）、语言资源与权限、课程。
文案中“韩语 / TOPIK”只保留在数据（语言名、目录名）里，代码与界面用“语言学习”。

### 数据迁移

全新迁移（各 app 0001），再用管理命令 `import_legacy --topik <db> --course <db> --bilibili <dir>` 导入：
用户（topik 为准，保留 id/哈希；course 独有用户并入；display_name 合并）→ 初始分类/语言 → 权限（全部挂到 ko）→ 科目 → 课程视频。
命令幂等、默认预览，`--apply` 写入；本地先用备份快照验证。

### 线上切换（需用户授权，单独执行）

1. 停 player3、course-backend；再做一次数据库快照
2. 部署新代码到 ~/learning_star，`uv sync`，migrate，`import_legacy --apply`
3. `mv ~/player3/backend/media/{videos,audios,pdfs}` → `~/learning_star/backend/data/media/languages/ko/{videos,audios,files}`
4. 安装 learning-star.service 与新 nginx 配置，启动；禁用旧两个服务（不删除）
5. 回滚：停新服务、把 media mv 回去、启用旧服务、恢复旧 nginx 配置

## 进度清单

- [x] 1. 线上只读采集（结构、数据快照、媒体清单、配置）
- [x] 2. 下载到本地 `_migration/backups/`
- [x] 3. 创建 merge 分支、写本方案
- [x] 4. 根目录统一 uv 项目（pyproject/uv.lock/.python-version=3.13）；旧 course/、topik/ 的 pyproject 在第 11 步随旧代码删除
- [x] 5. 新建 backend/ 单一 Django 项目：config、accounts、languages、courses（模型 + 迁移）
- [x] 6. 移植 API：账号/登录、语言资源扫描与受保护媒体、权限、课程科目与视频
- [x] 7. `import_legacy` 命令，用备份快照本地验证
- [ ] 8. 前端：API 层统一、topik → language、路由与文案、管理后台语言管理
- [ ] 9. scripts/dev.py（setup/migrate/info/dev/api/web/build/images/import-legacy），删除 Makefile 与旧脚本
- [ ] 10. scripts/deploy.py + deploy/（单服务 systemd、nginx、env 模板、cutover/rollback）
- [ ] 11. 删除 course/、topik/ 旧代码；README 更新；本地全流程验证
- [ ] 12. 线上切换（需用户授权）

## 进度日志

- 2026-11-16 完成 1–3：备份 `merge_backup_20261116-100534`；决策见上表。
- 2026-11-16 完成 4–7：backend/（config、accounts、languages、courses）；`import_legacy` 用备份快照验证：5 用户（xujiahui 新 id 6）、28 权限、9 科目、52 视频，可重复执行。
  冒烟测试 `_migration/tools/smoke_backend.py`（需先 import_legacy；运行：`.venv/Scripts/python -W ignore _migration/tools/smoke_backend.py backend`）。
  修复：受保护媒体可被 `有权目录/../无权目录` 绕过（旧代码同样存在）。
  本地开发用根目录 `.env`（DEBUG=True 等，不进 git）；数据在 backend/data/。
