# learning_star_web_app

一个网站、一个账号，两个学习栏目：

- **韩语 TOPIK**：视频、听力音频、学习资料（原 [player3](https://github.com/Wk-P/player3)）
- **课程**：按科目整理的 B 站课程、学习路线图、思维导图（原 [m22-Course-System](https://github.com/Wk-P/m22-Course-System)）

## 结构

```
web/              唯一的前端（Vue 3 + Vite）
  src/core/       整站框架：门户首页、统一登录、个人中心、管理后台、主题、登录状态
  src/topik/      韩语栏目页面与管理页
  src/course/     课程栏目页面与管理页（原样式套件构建时自动加 .mod-course 作用域）
  src/shared/     设计系统：动效 motion.css、滚动入场 v-reveal、静态资源 asset()
topik/backend/    Django：账号与登录（统一账号以此为准）、韩语资源、学习权限
course/backend/   Django：科目、B 站链接、路线图；信任 topik 签发的登录令牌
images/src/       图片原图；web/public 下的图片由 scripts/optimize_images.py 生成
deploy/           nginx、systemd、环境变量模板（deploy/.env 为服务器信息）
scripts/          开发与部署脚本，按平台分开，两边命令一一对应
  unix/           macOS / Linux：dev.sh、deploy.sh（根目录 Makefile 转发到这里）
  windows/        Windows：dev.ps1、deploy.ps1（部署用 Git Bash 运行 unix/deploy.sh，不需要 WSL）
  optimize_images.py  图片生成（跨平台，uv run）
```

### 统一登录

- 登录、注册、改密码、用户管理都在 topik 后端。
- 两个后端配置相同的 `JWT_SIGNING_KEY`；course 后端用它校验 topik 签发的令牌，
  按用户名对应到本地用户（首次访问自动创建），管理员身份跟随 topik 的 `is_staff`。
- 原 course 站的账号用 `manage.py import_course_users <course db>` 并入 topik：
  只在 course 存在的用户原样保留密码哈希（原密码可直接登录），同名用户以 topik 为准并列出供核对。
  默认只预览，加 `--apply` 写入。

### 网址

| 路径 | 内容 |
|---|---|
| `/` | 门户首页 |
| `/login` | 登录 / 注册 |
| `/topik`、`/topik/video`、`/topik/audio`、`/topik/file` | 韩语栏目 |
| `/course`、`/course/path` | 课程栏目 |
| `/me` | 我的账户 |
| `/admin/...` | 管理后台（两个栏目合并） |

原站的旧网址（`/user/video`、`/home`、`/admin/login` 等）会自动跳到新地址；原课程站的 8080 端口整体跳到 80。

## 本地开发

依赖：[uv](https://docs.astral.sh/uv/)、Node `^20.19` 或 `>=22.12`、pnpm。

| 操作 | macOS / Linux | Windows（PowerShell） |
|---|---|---|
| 首次准备 | `make setup` | `.\scripts\windows\dev.ps1 setup` |
| 同时启动三个服务 | `make dev` | `.\scripts\windows\dev.ps1 all` |
| topik 后端 :8000 | `make dev-topik-api` | `.\scripts\windows\dev.ps1 topik-api` |
| course 后端 :8001 | `make dev-course-api` | `.\scripts\windows\dev.ps1 course-api` |
| 前端 :5173 | `make dev-web` | `.\scripts\windows\dev.ps1 web` |
| 构建前端 | `make build` | `.\scripts\windows\dev.ps1 build` |
| 重新生成图片 | `make images` | `.\scripts\windows\dev.ps1 images` |

`make` 只是转发到 `./scripts/unix/dev.sh`，不带参数运行脚本会列出全部用法。
前端 :5173 会把 `/api/topik`、`/api/course`、`/media` 代理到两个后端。

两个后端都是 uv 项目（`pyproject.toml` + `uv.lock`），各自一个 `.venv`：topik 为 Python 3.10 / Django 5.2，
course 为 Python 3.13 / Django 6，与生产环境一致。改依赖用 `uv add` / `uv remove`（在 `topik/` 或 `course/` 下），不要手动 pip install。
`setup` 对两个后端执行 `uv sync`、安装前端依赖，并在缺少时由模板生成 `topik/backend/.env.develop`（按需修改）。
开发环境两个后端默认使用同一个开发用 `JWT_SIGNING_KEY`，无需额外配置。
**任何 `.env*` 文件都不要提交到 git。**

### 跨平台字符约定

| | 约定 | 由谁保证 |
|---|---|---|
| 换行 | 一律 LF；只有 `.ps1` / `.cmd` / `.bat` 用 CRLF | `.gitattributes`（检出时生效，不受 Windows `core.autocrlf` 影响） |
| 文件编码 | 一律 UTF-8 无 BOM；`.ps1` 为 UTF-8 **带 BOM**（PowerShell 5.1 否则按 GBK 读中文） | `.editorconfig`、`.vscode/settings.json` |
| Python 读写文件 | 必须写 `encoding='utf-8'`（Windows 上 `open()` 默认是 GBK） | 代码 + 开发脚本设置 `PYTHONUTF8=1` 兜底 |

服务器是 Linux，以上约定保证在 Windows / macOS 上开发、部署出去的文件与在 Linux 上完全相同。

## 部署

先把 `deploy/.env.example` 复制为 `deploy/.env`，填写服务器的 SSH 地址、端口、私钥路径和部署目录（`deploy/.env` 不进 git）。

首次部署前，在服务器上按 `deploy/env/` 的模板准备两个后端的环境变量文件，
`JWT_SIGNING_KEY` 两边必须相同，且必须是新生成的随机值（旧的生产密钥曾泄露在 git 历史中，已作废）。
生成：`python3 -c "import secrets; print(secrets.token_urlsafe(50))"`（Windows 上用 `python`）

| 操作 | macOS / Linux | Windows（PowerShell） |
|---|---|---|
| 预览 course 账号并入 topik | `./scripts/unix/deploy.sh users` | `.\scripts\windows\deploy.ps1 users` |
| 写入 | `./scripts/unix/deploy.sh users --apply` | `.\scripts\windows\deploy.ps1 users --apply` |
| 全部：topik → course → 前端 → nginx | `make deploy-all` | `.\scripts\windows\deploy.ps1 all` |
| 单项 | `make deploy-web` 等 | `.\scripts\windows\deploy.ps1 web` 等 |

B 站链接数据单独同步：`pull-data` 拉到本地修改，再用 `push-data` 推回（服务器在此期间被改过会中止）。

Windows 部署需要 [Git for Windows](https://git-scm.com/download/win)：`deploy.ps1` 用它自带的 bash 运行同一份 `deploy.sh`。
本机没有 `rsync` 时（Windows 默认如此）脚本自动改用 tar + ssh 整包上传，排除规则与删除保护和 rsync 一致。

部署永不覆盖服务器上的 `media/`、`db.sqlite3`、`.env*`、`staticfiles/` 与课程站 `bilibili/` 数据。

## 图片

原图放在 `images/src/`，运行 `make images`（Windows：`.\scripts\windows\dev.ps1 images`）生成 `web/public` 下的 WebP（多尺寸）与 PNG 兜底。
模板里引用 `public/` 资源用 `asset('img/x.webp')`，不要写死路径。
