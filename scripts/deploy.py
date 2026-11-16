"""部署到生产服务器（Windows / macOS / Linux 通用，只需要 Python 3.10+ 与 ssh）。

    uv run scripts/deploy.py <命令>

日常（合并切换完成后）：
    check          只读检查：SSH、目录、服务状态、sudo
    api            部署后端：上传 backend/ 与依赖清单 → uv sync → migrate → collectstatic → 重启
    web            构建并部署前端
    nginx          安装 nginx 配置与 systemd 单元
    all            api → web → nginx
    backup         在服务器上备份数据库（data/backups/），并下载一份到本地 _migration/backups/

一次性（course + topik 合并为统一后端）：
    cutover        预览切换步骤；加 --yes 执行。旧服务停机时间约为导入数据 + 移动媒体目录（同盘 mv，秒级）
    rollback       回到合并前的两个旧服务（加 --yes 执行）；切换后新产生的数据不会带回旧库

上传代码的命令（api / web / nginx / all / cutover --yes）只允许在 main 分支执行，
且工作区无未提交改动、与 origin/main 一致，保证线上运行的就是远端 main。

服务器信息读取 deploy/.env（不进 git，模板 deploy/.env.example）。
部署永不覆盖服务器上的 data/（数据库与媒体）。

线上 .env：本地维护（deploy/.env 的 ENV_LOCAL，默认 deploy/.env.production，不进 git），
由部署脚本送到服务器的 ENV_REMOTE（默认 APP_DIR/.env，权限 600）：
    env            上传线上 .env 并重启后端（all、cutover 若本地有该文件也会自动上传）
    env-pull       把服务器当前的 .env 下载到 ENV_LOCAL（首次建立本地副本用；已存在时加 --force 覆盖）
"""
from __future__ import annotations

import io
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = Path(os.environ.get('DEPLOY_ENV') or ROOT / 'deploy' / '.env')
SERVICE = 'learning-star'
LEGACY_SERVICES = ('player3', 'course-backend')

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


# ── 配置 ──────────────────────────────────────────────────────────────────────

def load_config() -> dict[str, str]:
    if not ENV_FILE.exists():
        die(f'缺少 {ENV_FILE}：复制 deploy/.env.example 为 deploy/.env 后填写服务器信息')
    cfg: dict[str, str] = {}
    for line in ENV_FILE.read_text(encoding='utf-8-sig').splitlines():
        m = re.match(r'^\s*([A-Z_]+)=(.*)$', line.rstrip('\r'))
        if m:
            cfg[m.group(1)] = m.group(2).strip().strip('"\'')
    cfg.update({k: v for k, v in os.environ.items() if k in cfg or k in DEFAULTS})  # 环境变量可临时覆盖
    for k in ('SSH_HOST', 'SSH_PORT', 'SSH_KEY', 'REMOTE_HOME'):
        if not cfg.get(k):
            die(f'{ENV_FILE} 缺少 {k}')
    home = cfg['REMOTE_HOME'].rstrip('/')
    for k, v in DEFAULTS.items():
        cfg.setdefault(k, v.format(home=home, user=cfg['SSH_HOST'].split('@')[0]))
    cfg.setdefault('ENV_REMOTE', cfg['APP_DIR'].rstrip('/') + '/.env')
    local_env = Path(os.path.expanduser(cfg['ENV_LOCAL']))
    cfg['ENV_LOCAL'] = str(local_env if local_env.is_absolute() else ROOT / local_env)
    key = Path(os.path.expanduser(cfg['SSH_KEY']))
    if not key.is_file():
        die(f'找不到 SSH 私钥：{key}（deploy/.env 的 SSH_KEY）')
    cfg['SSH_KEY'] = str(key)
    return cfg


DEFAULTS = {
    'APP_DIR': '{home}/learning_star',        # 统一后的部署目录
    'APP_PORT': '8010',                       # gunicorn 端口（与旧服务的 8000/8001 不冲突，便于回滚）
    'APP_USER': '{user}',                     # systemd 运行用户
    'TOPIK_DIR': '{home}/player3',            # 合并前的旧目录（cutover / rollback 用）
    'COURSE_DIR': '{home}/course_system',
    'ENV_LOCAL': 'deploy/.env.production',   # 本地的线上 .env（相对仓库根目录或绝对路径，不进 git）
    # ENV_REMOTE 默认 APP_DIR/.env，见 load_config
}


# ── SSH 与上传 ────────────────────────────────────────────────────────────────

def ssh_base(cfg) -> list[str]:
    return ['ssh', '-p', cfg['SSH_PORT'], '-i', cfg['SSH_KEY'], '-o', 'ServerAliveInterval=60', cfg['SSH_HOST']]


def remote(cfg, script: str, check: bool = True, capture: bool = False, **env: str) -> str:
    """在服务器上用 bash 执行脚本；env 作为变量放在脚本开头（已转义）。"""
    head = ''.join(f'{k}={shlex.quote(str(v))}\n' for k, v in env.items())
    body = ('set -euo pipefail\nUV=$(command -v uv || echo /snap/bin/uv)\n'
            f'export ENV_FILE={shlex.quote(cfg["ENV_REMOTE"])}\n' + head + script)
    r = subprocess.run(ssh_base(cfg) + ['bash -s'], input=body.encode(),
                       stdout=subprocess.PIPE if capture else None)
    if check and r.returncode != 0:
        die(f'服务器上的步骤失败（退出码 {r.returncode}）')
    return r.stdout.decode('utf-8', 'replace') if capture else ''


SKIP_DIRS = {'__pycache__', 'node_modules', '.venv', 'data', 'staticfiles', '.pytest_cache'}


def _skip(path: Path) -> bool:
    return (any(p in SKIP_DIRS for p in path.parts) or path.suffix in ('.pyc', '.sqlite3')
            or path.name.startswith('.env'))


def make_tar(items: dict[str, Path | bytes]) -> bytes:
    """{服务器上的相对路径: 本地文件/目录 或 文件内容}"""
    buf = io.BytesIO()

    def reset(ti: tarfile.TarInfo) -> tarfile.TarInfo:
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = ''
        return ti

    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        for arc, src in items.items():
            if isinstance(src, bytes):
                ti = reset(tarfile.TarInfo(arc))
                ti.size, ti.mode, ti.mtime = len(src), 0o644, int(time.time())
                tar.addfile(ti, io.BytesIO(src))
            elif src.is_dir():
                for f in sorted(src.rglob('*')):
                    rel = f.relative_to(src)
                    if f.is_file() and not _skip(rel):
                        tar.add(f, f'{arc}/{rel.as_posix()}', filter=reset)
            else:
                tar.add(src, arc, filter=reset)
    return buf.getvalue()


def upload(cfg, dest: str, items: dict[str, Path | bytes]) -> None:
    """清空并解压到服务器目录 dest。"""
    data = make_tar(items)
    cmd = f'rm -rf {shlex.quote(dest)} && mkdir -p {shlex.quote(dest)} && tar -xzf - --no-same-owner -C {shlex.quote(dest)}'
    r = subprocess.run(ssh_base(cfg) + [cmd], input=data)
    if r.returncode != 0:
        die('上传失败')
    print(f'  已上传 {len(data) / 1024:.0f} KB → {dest}')


def render(text: str, cfg) -> str:
    return (text.replace('{{APP_DIR}}', cfg['APP_DIR']).replace('{{PORT}}', cfg['APP_PORT'])
            .replace('{{USER}}', cfg['APP_USER']).replace('{{ENV_FILE}}', cfg['ENV_REMOTE']))


def code_items() -> dict[str, Path | bytes]:
    return {
        'backend': ROOT / 'backend',
        'pyproject.toml': ROOT / 'pyproject.toml',
        'uv.lock': ROOT / 'uv.lock',
        '.python-version': ROOT / '.python-version',
    }


def deploy_items(cfg) -> dict[str, Path | bytes]:
    return {
        'learning_star.conf': render((ROOT / 'deploy/nginx/learning_star.conf').read_text(encoding='utf-8'), cfg).encode(),
        'learning_star_proxy.conf': (ROOT / 'deploy/nginx/learning_star_proxy.conf').read_bytes(),
        f'{SERVICE}.service': render((ROOT / f'deploy/systemd/{SERVICE}.service').read_text(encoding='utf-8'), cfg).encode(),
    }


# ── 步骤 ──────────────────────────────────────────────────────────────────────

def step(name: str):
    def deco(fn):
        def wrapper(*a, **kw):
            t0 = time.time()
            print(f'▶ {name} …')
            fn(*a, **kw)
            print(f'✔ {name}（{time.time() - t0:.0f}s）')
        return wrapper
    return deco


INSTALL_CODE = r'''
cd "$APP"
mkdir -p log data
rm -rf backend.old
if [ -d backend ]; then mv backend backend.old; fi
mv .staging/backend backend
cp .staging/pyproject.toml .staging/uv.lock .staging/.python-version .
rm -rf .staging backend.old
# 项目的 Python（.python-version）。服务器在国内：先用 npmmirror（同步及时），
# 再试服务器自己配置的镜像（nju/tuna 常缺新版本），最后才走 GitHub（国内慢）
PY=$(cat .python-version)
if ! "$UV" python find "$PY" >/dev/null 2>&1; then
  for M in https://registry.npmmirror.com/-/binary/python-build-standalone "" \
           https://github.com/astral-sh/python-build-standalone/releases/download; do
    if [ -n "$M" ]; then UV_PYTHON_INSTALL_MIRROR="$M" "$UV" python install "$PY" && break
    else "$UV" python install "$PY" && break; fi
  done
fi
# 依赖：按 uv.lock 的精确版本安装，但从服务器配置的国内源（uv.toml）下载。
# 直接 uv sync --frozen 会用锁文件里记录的 pypi.org 地址，在国内很慢。
[ -x .venv/bin/python ] && .venv/bin/python -c 'import sys; sys.exit(sys.version_info[:2] != tuple(map(int, "'"$PY"'".split("."))))' \
  || "$UV" venv --clear --python "$PY" .venv
"$UV" export --frozen --no-dev --no-hashes --no-emit-project -q -o .requirements.txt
"$UV" pip install --python .venv/bin/python -r .requirements.txt
rm -f .requirements.txt
cd backend
../.venv/bin/python manage.py migrate --noinput
../.venv/bin/python manage.py collectstatic --noinput -v 0
'''


@step('上传并安装后端')
def push_code(cfg) -> None:
    upload(cfg, f'{cfg["APP_DIR"]}/.staging', code_items())
    remote(cfg, INSTALL_CODE, APP=cfg['APP_DIR'])


@step('重启后端')
def restart(cfg) -> None:
    remote(cfg, f'sudo systemctl restart {SERVICE}; sleep 2; systemctl is-active {SERVICE}')


@step('构建前端')
def build_web(cfg) -> None:
    pnpm = shutil.which('pnpm') or die('缺少 pnpm：corepack enable 或 npm i -g pnpm')
    for args in (['install', '--frozen-lockfile'], ['run', 'build']):
        if subprocess.call([pnpm, *args], cwd=ROOT / 'web') != 0:
            die('前端构建失败')


@step('上传前端')
def push_web(cfg, live: bool = True) -> None:
    upload(cfg, f'{cfg["APP_DIR"]}/web/dist.new', {'.': ROOT / 'web' / 'dist'})
    if live:
        remote(cfg, 'cd "$APP/web" && rm -rf dist.old && { [ -d dist ] && mv dist dist.old || true; } && mv dist.new dist && rm -rf dist.old',
               APP=cfg['APP_DIR'])


INSTALL_NGINX = r'''
cd "$APP/.deploy"
sudo mkdir -p /etc/nginx/snippets
sudo cp learning_star_proxy.conf /etc/nginx/snippets/
sudo cp learning_star.conf /etc/nginx/conf.d/learning_star.conf
sudo cp "$SERVICE.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo nginx -t
sudo systemctl reload nginx
'''


@step('安装 nginx 与 systemd 配置')
def push_nginx(cfg) -> None:
    upload(cfg, f'{cfg["APP_DIR"]}/.deploy', deploy_items(cfg))
    remote(cfg, INSTALL_NGINX, APP=cfg['APP_DIR'], SERVICE=SERVICE)


def check_env_file(path: Path) -> bytes:
    """上传前检查本地的线上 .env：不能进 git、必须是生产配置。"""
    if path.is_relative_to(ROOT):
        r = subprocess.run(['git', 'check-ignore', '-q', str(path)], cwd=ROOT)
        if r.returncode != 0:
            die(f'{path} 没有被 .gitignore 忽略，可能被提交进 git。先把它加入 .gitignore')
    data = path.read_bytes().replace(b'\r\n', b'\n')
    values = {}
    for line in data.decode('utf-8-sig').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k, v = line.split('=', 1)
            values[k.strip()] = v.strip().strip('"\'')
    if values.get('DEBUG') == 'True':
        die(f'{path} 里 DEBUG=True，不能用于线上')
    if len(values.get('SECRET_KEY', '')) < 32:
        die(f'{path} 的 SECRET_KEY 缺失或太短（至少 32 字符）')
    return data


@step('上传线上 .env')
def push_env(cfg) -> None:
    path = Path(cfg['ENV_LOCAL'])
    data = check_env_file(path)
    dest = shlex.quote(cfg['ENV_REMOTE'])
    cmd = (f'umask 077 && mkdir -p "$(dirname {dest})" && cat > {dest}.new && chmod 600 {dest}.new '
           f'&& mv {dest}.new {dest}')
    if subprocess.run(ssh_base(cfg) + [cmd], input=data).returncode != 0:
        die('上传 .env 失败')
    print(f'  {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path} → {cfg["ENV_REMOTE"]}')


def push_env_if_present(cfg) -> None:
    if Path(cfg['ENV_LOCAL']).is_file():
        push_env(cfg)
    else:
        print(f'  （本地没有 {cfg["ENV_LOCAL"]}，沿用服务器上的 {cfg["ENV_REMOTE"]}）')


def require_merged(cfg) -> None:
    out = remote(cfg, '[ -f "$APP/.merged" ] && echo yes || echo no', capture=True, APP=cfg['APP_DIR'])
    if out.strip() != 'yes':
        die('服务器还没有完成合并切换（缺少 .merged 标记）。先运行：uv run scripts/deploy.py cutover')


# ── 命令 ──────────────────────────────────────────────────────────────────────

def cmd_check(cfg, _args) -> None:
    remote(cfg, r'''
echo "已连接 $(whoami)@$(hostname)"
echo "  部署目录 $APP：$([ -d "$APP" ] && echo 存在 || echo 不存在)，合并标记：$([ -f "$APP/.merged" ] && echo 已切换 || echo 未切换)"
echo "  .env（$ENV_FILE）：$([ -f "$ENV_FILE" ] && echo 存在 || echo 缺少)"
echo "  数据库：$([ -f "$APP/data/db.sqlite3" ] && du -h "$APP/data/db.sqlite3" | cut -f1 || echo 无)"
for s in "$SERVICE" player3 course-backend nginx; do echo "  服务 $s=$(systemctl is-active $s 2>/dev/null || true)"; done
echo "  uv：$("$UV" --version 2>/dev/null || echo 未找到)"
sudo -n true 2>/dev/null && echo '  sudo 免密可用' || echo '  sudo 需要密码（部署会失败）'
''', APP=cfg['APP_DIR'], SERVICE=SERVICE)


def cmd_api(cfg, _args) -> None:
    require_merged(cfg)
    push_code(cfg)
    restart(cfg)


def cmd_web(cfg, _args) -> None:
    require_merged(cfg)
    build_web(cfg)
    push_web(cfg)


def cmd_nginx(cfg, _args) -> None:
    require_merged(cfg)
    push_nginx(cfg)


def cmd_env(cfg, _args) -> None:
    require_merged(cfg)
    push_env(cfg)
    push_nginx(cfg)   # systemd 单元里的 ENV_FILE 路径可能变了
    restart(cfg)


def cmd_env_pull(cfg, args) -> None:
    path = Path(cfg['ENV_LOCAL'])
    if path.exists() and '--force' not in args:
        die(f'{path} 已存在。确认要用服务器上的版本覆盖时加 --force')
    data = subprocess.run(ssh_base(cfg) + [f'cat {shlex.quote(cfg["ENV_REMOTE"])}'], capture_output=True)
    if data.returncode != 0:
        die(f'读取服务器 {cfg["ENV_REMOTE"]} 失败：{data.stderr.decode("utf-8", "replace").strip()}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.stdout)
    check_env_file(path)
    print(f'✔ 已下载 {cfg["ENV_REMOTE"]} → {path}（以后改这份，再 uv run scripts/deploy.py env 送上去）')


def cmd_all(cfg, args) -> None:
    require_merged(cfg)
    push_env_if_present(cfg)
    push_code(cfg)
    build_web(cfg)
    push_web(cfg)
    push_nginx(cfg)
    restart(cfg)


BACKUP = r'''
mkdir -p "$APP/data/backups"
out="$APP/data/backups/db-$(date +%Y%m%d-%H%M%S).sqlite3"
"$APP/.venv/bin/python" - "$APP/data/db.sqlite3" "$out" <<'PY'
import sqlite3, sys
s = sqlite3.connect(f'file:{sys.argv[1]}?mode=ro', uri=True); d = sqlite3.connect(sys.argv[2]); s.backup(d); d.close()
PY
echo "$out"
'''


def cmd_backup(cfg, _args) -> None:
    require_merged(cfg)
    path = remote(cfg, BACKUP, capture=True, APP=cfg['APP_DIR']).strip().splitlines()[-1]
    local = ROOT / '_migration' / 'backups' / Path(path).name
    local.parent.mkdir(parents=True, exist_ok=True)
    with open(local, 'wb') as f:
        r = subprocess.run(ssh_base(cfg) + [f'cat {shlex.quote(path)}'], stdout=f)
    if r.returncode != 0:
        die('下载失败')
    print(f'服务器：{path}\n本地：{local}')


# ── 一次性：合并切换 ──────────────────────────────────────────────────────────

PREFLIGHT = r'''
[ -f "$APP/.merged" ] && { echo '已经切换过（存在 .merged）。日常部署用 api / web / all' >&2; exit 1; }
for f in "$TOPIK/backend/db.sqlite3" "$COURSE/backend/db.sqlite3" "$TOPIK/backend/.env.production"; do
  [ -f "$f" ] || { echo "缺少 $f" >&2; exit 1; }
done
mkdir -p "$APP/data/media"
# 媒体必须与新目录在同一文件系统，mv 才是瞬间完成的改名而不是复制 80G
[ "$(stat -c %d "$TOPIK/backend/media")" = "$(stat -c %d "$APP/data/media")" ] || { echo '旧媒体目录与新数据目录不在同一文件系统' >&2; exit 1; }
if [ -e "$APP/data/media/languages/ko" ]; then echo "$APP/data/media/languages/ko 已存在，请先确认其内容" >&2; exit 1; fi
if [ -f "$APP/data/db.sqlite3" ]; then
  mv "$APP/data/db.sqlite3" "$APP/data/db.sqlite3.aborted-$(date +%Y%m%d-%H%M%S)"
  echo '  上次未完成的新数据库已改名保留'
fi
# 生成 .env：新的 SECRET_KEY；沿用旧 topik 的 JWT_SIGNING_KEY（已登录用户不掉线）与 ALLOWED_HOSTS
if [ ! -f "$ENV_FILE" ]; then
  mkdir -p "$(dirname "$ENV_FILE")"
  get() { grep -s "^$1=" "$TOPIK/backend/.env.production" | tail -1 | cut -d= -f2-; }
  jwt=$(get JWT_SIGNING_KEY); [ -n "$jwt" ] || jwt=$(get SECRET_KEY)
  umask 077
  {
    echo 'DEBUG=False'
    echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
    echo "JWT_SIGNING_KEY=$jwt"
    echo "ALLOWED_HOSTS=$(get ALLOWED_HOSTS)"
  } > "$ENV_FILE"
  echo "  已生成 $ENV_FILE（SECRET_KEY 新生成，JWT_SIGNING_KEY 与 ALLOWED_HOSTS 沿用旧 topik）"
fi
echo "  磁盘剩余：$(df -h "$APP" | tail -1 | awk '{print $4}')"
'''

SWITCH = r'''
L="$APP/data/legacy"
fail() { echo; echo "✘ 切换在「$STEP」失败。旧服务已停止，请运行：uv run scripts/deploy.py rollback --yes" >&2; }
trap fail ERR

STEP='停止旧服务'; echo "▶ $STEP"
sudo systemctl stop player3 course-backend

STEP='旧数据快照'; echo "▶ $STEP"
mkdir -p "$L"
"$APP/.venv/bin/python" - "$TOPIK/backend/db.sqlite3" "$L/topik.sqlite3" "$COURSE/backend/db.sqlite3" "$L/course.sqlite3" <<'PY'
import sqlite3, sys
for src, dst in zip(sys.argv[1::2], sys.argv[2::2]):
    s = sqlite3.connect(f'file:{src}?mode=ro', uri=True); d = sqlite3.connect(dst); s.backup(d); d.close(); s.close()
PY
rm -rf "$L/bilibili"; cp -a "$COURSE/backend/bilibili" "$L/bilibili"
sudo cp /etc/nginx/conf.d/learning_star.conf "$L/nginx_learning_star.conf"

STEP='导入旧数据'; echo "▶ $STEP"
cd "$APP/backend"
../.venv/bin/python manage.py import_legacy --topik "$L/topik.sqlite3" --course "$L/course.sqlite3" --bilibili "$L/bilibili" --apply

STEP='移动媒体目录'; echo "▶ $STEP"
K="$APP/data/media/languages/ko"; mkdir -p "$K"
: > "$L/media_moves.tsv"
for pair in videos:videos audios:audios pdfs:files; do
  src="$TOPIK/backend/media/${pair%%:*}"; dst="$K/${pair##*:}"
  if [ -d "$src" ]; then mv "$src" "$dst"; printf '%s\t%s\n' "$src" "$dst" >> "$L/media_moves.tsv"; echo "  $src → $dst"; fi
done

STEP='启动新后端'; echo "▶ $STEP"
sudo systemctl enable --now "$SERVICE"
sleep 3
systemctl is-active "$SERVICE"
code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/api/languages/")
[ "$code" = 401 ] || { echo "  健康检查：期望 401（需要登录），实际 $code" >&2; false; }
echo "  健康检查通过"

STEP='切换前端'; echo "▶ $STEP"
cd "$APP/web"
rm -rf dist.legacy
if [ -d dist ]; then mv dist dist.legacy; fi
mv dist.new dist

STEP='切换 nginx'; echo "▶ $STEP"
cd "$APP/.deploy"
sudo cp learning_star_proxy.conf /etc/nginx/snippets/
sudo cp learning_star.conf /etc/nginx/conf.d/learning_star.conf
sudo nginx -t
sudo systemctl reload nginx

STEP='停用旧服务'; echo "▶ $STEP"
sudo systemctl disable player3 course-backend
date > "$APP/.merged"
trap - ERR
echo "✔ 切换完成"
'''


def cmd_cutover(cfg, args) -> None:
    print(f'''合并切换计划（服务器 {cfg["SSH_HOST"]}）：
  旧：{cfg["TOPIK_DIR"]}（player3 :8000）+ {cfg["COURSE_DIR"]}（course-backend :8001）
  新：{cfg["APP_DIR"]}（{SERVICE} :{cfg["APP_PORT"]}），数据在 {cfg["APP_DIR"]}/data/

  准备（不停机）：检查 → 生成 .env → 上传后端、uv sync、建新库 → 构建并上传前端（不上线）→ 安装 systemd 单元
  切换（停机）：停旧服务 → 旧库快照到 data/legacy/ → import_legacy → mv 媒体到 data/media/languages/ko/
               → 启动新后端并检查 → 换前端 → 换 nginx → 停用旧服务（不删除，可 rollback）''')
    if '--yes' not in args:
        print('\n这是预览。确认后执行：uv run scripts/deploy.py cutover --yes')
        return
    env = dict(APP=cfg['APP_DIR'], TOPIK=cfg['TOPIK_DIR'], COURSE=cfg['COURSE_DIR'], SERVICE=SERVICE, PORT=cfg['APP_PORT'])
    push_env_if_present(cfg)
    step('预检')(lambda: remote(cfg, PREFLIGHT, **env))()
    push_code(cfg)
    build_web(cfg)
    push_web(cfg, live=False)
    upload(cfg, f'{cfg["APP_DIR"]}/.deploy', deploy_items(cfg))
    step('安装 systemd 单元')(lambda: remote(
        cfg, 'sudo cp "$APP/.deploy/$SERVICE.service" /etc/systemd/system/ && sudo systemctl daemon-reload', **env))()
    t0 = time.time()
    remote(cfg, SWITCH, **env)
    print(f'停机时长约 {time.time() - t0:.0f}s')


ROLLBACK = r'''
L="$APP/data/legacy"
echo "▶ 停止新后端"
sudo systemctl disable --now "$SERVICE" 2>/dev/null || true
echo "▶ 媒体目录移回"
if [ -f "$L/media_moves.tsv" ]; then
  while IFS=$'\t' read -r src dst; do
    [ -n "$src" ] || continue
    if [ -d "$dst" ] && [ ! -e "$src" ]; then mv "$dst" "$src"; echo "  $dst → $src"; fi
  done < "$L/media_moves.tsv"
  mv "$L/media_moves.tsv" "$L/media_moves.tsv.rolledback-$(date +%Y%m%d-%H%M%S)"
fi
echo "▶ 恢复前端"
cd "$APP/web"
if [ -d dist.legacy ]; then rm -rf dist.failed; [ -d dist ] && mv dist dist.failed; mv dist.legacy dist; fi
echo "▶ 恢复 nginx"
if [ -f "$L/nginx_learning_star.conf" ]; then
  sudo cp "$L/nginx_learning_star.conf" /etc/nginx/conf.d/learning_star.conf
  sudo nginx -t && sudo systemctl reload nginx
fi
echo "▶ 启动旧服务"
sudo systemctl enable --now player3 course-backend
systemctl is-active player3 course-backend
rm -f "$APP/.merged"
echo "✔ 已回到合并前的状态（新数据库保留在 $APP/data/db.sqlite3）"
'''


def cmd_rollback(cfg, args) -> None:
    if '--yes' not in args:
        print('回滚：停止新后端、媒体移回旧目录、恢复旧前端与 nginx、启动 player3 / course-backend。\n'
              '切换后在新站产生的数据（新用户、权限、课程修改）不会带回旧库。\n'
              '确认后执行：uv run scripts/deploy.py rollback --yes')
        return
    remote(cfg, ROLLBACK, APP=cfg['APP_DIR'], SERVICE=SERVICE)


# ── 只从 main 部署 ────────────────────────────────────────────────────────────
# 部署上传的是本地工作区的文件，所以要求：在 main 分支、没有未提交改动、与 origin/main 完全一致。
DEPLOY_BRANCH = 'main'
SHIPS_CODE = {'api', 'web', 'nginx', 'all', 'cutover'}


def git(*args: str) -> str:
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        die(f'git {" ".join(args)} 失败：{r.stderr.strip()}')
    return r.stdout.strip()


def require_main() -> None:
    branch = git('rev-parse', '--abbrev-ref', 'HEAD')
    if branch != DEPLOY_BRANCH:
        die(f'线上只从 {DEPLOY_BRANCH} 部署，当前在 {branch}。先合并到 {DEPLOY_BRANCH}，再 git switch {DEPLOY_BRANCH}')
    if git('status', '--porcelain', '--untracked-files=no'):
        die('有未提交的改动，部署会把它们一起带上线。先提交或 git stash')
    print(f'▶ 同步 origin/{DEPLOY_BRANCH}')
    git('fetch', 'origin', DEPLOY_BRANCH)
    local, upstream = git('rev-parse', 'HEAD'), git('rev-parse', f'origin/{DEPLOY_BRANCH}')
    if local != upstream:
        ahead = git('rev-list', '--count', f'origin/{DEPLOY_BRANCH}..HEAD')
        behind = git('rev-list', '--count', f'HEAD..origin/{DEPLOY_BRANCH}')
        die(f'本地 {DEPLOY_BRANCH} 与 origin/{DEPLOY_BRANCH} 不一致（领先 {ahead}、落后 {behind} 个提交）。'
            f'先 git pull / git push，保证线上代码就是远端 {DEPLOY_BRANCH}')
    print(f'  部署提交 {local[:8]} {git("log", "-1", "--format=%s")}')


COMMANDS = {
    'check': cmd_check, 'api': cmd_api, 'web': cmd_web, 'nginx': cmd_nginx, 'all': cmd_all,
    'backup': cmd_backup, 'cutover': cmd_cutover, 'rollback': cmd_rollback,
    'env': cmd_env, 'env-pull': cmd_env_pull,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', 'help'):
        print(__doc__)
        return
    fn = COMMANDS.get(sys.argv[1])
    if not fn:
        print(f'未知命令：{sys.argv[1]}\n', file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    if not shutil.which('ssh'):
        die('缺少 ssh（Windows 10+ 自带 OpenSSH 客户端；或安装 Git for Windows）')
    cmd = sys.argv[1]
    if cmd in SHIPS_CODE and (cmd != 'cutover' or '--yes' in sys.argv[2:]):
        require_main()
    cfg = load_config()
    t0 = time.time()
    fn(cfg, sys.argv[2:])
    print(f'总用时 {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
