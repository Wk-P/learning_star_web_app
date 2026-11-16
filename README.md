# learning_star_web_app

一个网站、一个账号、一个后端，两个学习栏目：

- **语言学习**：语言分类 → 具体语言（如 东亚语言 → 韩语），每门语言有视频、听力音频、学习资料；分类与语言在管理后台增删改
- **课程**：按科目整理的 B 站 / YouTube 课程链接、学习路线图、思维导图

> 本仓库由原 topik（[player3](https://github.com/Wk-P/player3)）与 course（[m22-Course-System](https://github.com/Wk-P/m22-Course-System)）两个项目合并而来，合并记录见 [_migration/PLAN.md](_migration/PLAN.md)。

## 结构

```
pyproject.toml uv.lock .python-version   唯一的 Python 环境（Python 3.13 / Django 6）→ 根目录 .venv
.env.example      后端环境变量模板（本地与服务器都用根目录 .env，不进 git）
backend/          Django 后端
  config/         settings、urls
  accounts/       统一账号：登录、注册、改密码、显示名称、用户管理
  languages/      语言学习：分类、语言、媒体扫描、学习权限、受保护媒体 /media/
  courses/        课程：科目、视频链接
data/             数据库 db.sqlite3 与 media/（不进 git，部署不覆盖）
web/              前端（Vue 3 + Vite）
  src/core/       整站框架：门户首页、登录、我的账户、管理后台、统一 API 封装
  src/language/   语言学习页面与管理页
  src/course/     课程页面与管理页（原样式套件构建时自动加 .mod-course 作用域）
  src/shared/     设计系统：动效、v-reveal、asset()
images/src/       图片原图；web/public 下的图片由 scripts/optimize_images.py 生成
scripts/          task.py（本地开发）、deploy.py（部署），Windows / macOS / Linux 通用
deploy/           nginx、systemd 模板；deploy/.env 为服务器信息（不进 git）
```

**Python 只有一个环境**：根目录 `.venv`，由 `uv sync` 按 `uv.lock` 生成。改依赖在根目录用 `uv add` / `uv remove`，不要手动 pip install，不要在子目录另建环境。

### 媒体目录

```
data/media/languages/<语言标识>/videos/<目录...>/<视频名>/playlist.m3u8 (+ ts)
data/media/languages/<语言标识>/audios/<目录...>/<音频名>.mp3
data/media/languages/<语言标识>/files/<目录...>/<资料名>.pdf|.xlsx|.hwp|...
```

第一层目录就是「学习权限」中可授权的单位。管理员不受限；普通用户只看到被授权的目录。

### 网址

| 路径 | 内容 |
|---|---|
| `/` | 门户首页 |
| `/login` | 登录 / 注册 |
| `/language` | 全部语言（按分类） |
| `/language/:lang`、`/language/:lang/video` `audio` `file` | 某门语言的概览与资源，如 `/language/ko` |
| `/course`、`/course/path` | 课程栏目 |
| `/me` | 我的账户 |
| `/admin/...` | 管理后台 |

旧网址（`/topik/*`、`/user/*`、`/home`、`/admin/login` 等）自动跳到新地址；原课程站的 8080 端口整体跳到 80。

API 统一在 `/api/` 下：`auth/`（令牌）、`accounts/`、`languages/`、`courses/`。

## 本地开发

依赖：[uv](https://docs.astral.sh/uv/)、Node `^20.19` 或 `>=22.12`、pnpm。所有平台命令相同：

| 操作 | 命令 |
|---|---|
| 首次准备 | `uv run scripts/task.py setup` |
| 后台启动后端 :8000 与前端 :5173（显示地址与测试账号） | `uv run scripts/task.py dev all` |
| 停止 / 重启 / 状态 / 日志 | `uv run scripts/task.py dev stop` / `restart` / `status` / `logs` |
| 前台单独运行后端 / 前端（调试） | `uv run scripts/task.py api` / `web` |
| 数据库迁移 | `uv run scripts/task.py migrate` |
| 访问地址与测试账号 | `uv run scripts/task.py info` |
| 创建 / 重置测试账号 | `uv run scripts/task.py users` |
| 任意 manage.py 命令 | `uv run scripts/task.py manage <参数>` |
| 构建前端 | `uv run scripts/task.py build` |
| 重新生成图片 | `uv run scripts/task.py images` |
| 导入线上数据快照 | `uv run scripts/task.py import-legacy <备份目录> [--apply]` |

`setup` 执行 `uv sync`、安装前端依赖、由 `.env.example` 生成 `.env`（本地开 DEBUG）、迁移数据库，
并创建本地测试账号：管理员 `dev_admin`、学员 `dev_user`（密码默认都是 `dev123456`，见 `.env` 的 `DEV_*`）。
测试账号与线上导入的账号不重名；`setup`、`migrate`、`users` 每次都会把它们的密码重置为 `.env` 中的值，学员自动拥有本地全部学习权限。
前端 :5173 把 `/api`、`/media` 代理到后端 :8000。不带参数运行脚本会列出全部用法。

### 跨平台字符约定

| | 约定 | 由谁保证 |
|---|---|---|
| 换行 | 一律 LF | `.gitattributes`（检出时生效，不受 Windows `core.autocrlf` 影响） |
| 文件编码 | 一律 UTF-8 无 BOM | `.editorconfig`、`.vscode/settings.json` |
| Python 读写文件 | 必须写 `encoding='utf-8'`（Windows 上 `open()` 默认是 GBK） | 代码 + `task.py` 设置 `PYTHONUTF8=1` 兜底 |

## 部署

先把 `deploy/.env.example` 复制为 `deploy/.env`，填写 SSH 地址、端口、私钥路径和服务器主目录。
部署只需要本机有 Python（经 uv）与 `ssh`（Windows 10+ 自带），不需要 rsync、Git Bash 或 WSL。

| 操作 | 命令 |
|---|---|
| 只读检查 | `uv run scripts/deploy.py check` |
| 部署后端 / 前端 / nginx 与 systemd | `uv run scripts/deploy.py api` / `web` / `nginx` |
| 全部 | `uv run scripts/deploy.py all` |
| 立即备份线上数据库与 .env（并下载到本地 data/remote-backups/） | `uv run scripts/deploy.py backup` |
| 自动备份 | 每天 03:30（保留 14 份）+ 每次部署代码前（保留 10 份），在服务器 `data/backups/`；不含媒体文件 |

服务器布局：`~/learning_star/`（`backend/`、`.venv/`、`web/dist/`、`data/`、`.env`、`log/`），
systemd 服务 `learning-star`（gunicorn 127.0.0.1:8010），nginx 80 端口统一入口。
部署永不覆盖服务器上的 `data/`；线上 `.env` 只有本地存在 `deploy/.env.production` 时才会上传覆盖（`deploy.py env` / `all`）。

部署上传的是本地工作区，所以 `api` / `web` / `nginx` / `all` 只能在 `main` 分支执行，且须无未提交改动、与 `origin/main` 一致（脚本会检查）。

合并上线已于 2026-11-16 完成（过程与一次性的 cutover / rollback 脚本见 git 历史与 `_migration/PLAN.md`）。出问题时用 `data/backups/` 里的备份恢复数据库。

## 图片

原图放在 `images/src/`，运行 `uv run scripts/task.py images` 生成 `web/public` 下的 WebP（多尺寸）与 PNG 兜底。
模板里引用 `public/` 资源用 `asset('img/x.webp')`，不要写死路径。
