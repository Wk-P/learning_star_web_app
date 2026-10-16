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
deploy/           nginx、systemd、环境变量模板、部署脚本
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
| `/course`、`/course/roadmap`、`/course/mindmap` | 课程栏目 |
| `/me` | 我的账户 |
| `/admin/...` | 管理后台（两个栏目合并） |

原站的旧网址（`/user/video`、`/home`、`/admin/login` 等）会自动跳到新地址；原课程站的 8080 端口整体跳到 80。

## 本地开发

```bash
make dev-topik-api    # :8000
make dev-course-api   # :8001
make dev-web          # :5173，代理 /api/topik、/api/course、/media 到两个后端
```

首次开发：`cp topik/backend/.env.develop.example topik/backend/.env.develop` 并按需修改。
开发环境两个后端默认使用同一个开发用 `JWT_SIGNING_KEY`，无需额外配置。
**任何 `.env*` 文件都不要提交到 git。**

## 部署（上海节点 `shanghai_node`，139.224.222.27）

首次部署前，在服务器上按 `deploy/env/` 的模板准备两个后端的环境变量文件，
`JWT_SIGNING_KEY` 两边必须相同，且必须是新生成的随机值（旧的生产密钥曾泄露在 git 历史中，已作废）。
生成：`python3 -c "import secrets; print(secrets.token_urlsafe(50))"`

```bash
./deploy/deploy.sh users            # 预览 course 账号并入 topik
./deploy/deploy.sh users --apply    # 写入
./deploy/deploy.sh all              # topik 后端 → course 后端 → 前端 → nginx
```

部署永不覆盖服务器上的 `media/`、`db.sqlite3`、`.env*`、`staticfiles/` 与课程站 `bilibili/` 数据。

## 图片

原图放在 `images/src/`，运行 `make images` 生成 `web/public` 下的 WebP（多尺寸）与 PNG 兜底。
模板里引用 `public/` 资源用 `asset('img/x.webp')`，不要写死路径。
