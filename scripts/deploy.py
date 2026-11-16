"""部署到生产服务器（Windows / macOS / Linux 通用，只需要 Python 3.10+ 与 ssh）。

    uv run scripts/deploy.py <命令>

命令：
    check          只读检查：SSH、目录、服务状态、sudo
    api            部署后端：上传 backend/ 与依赖清单 → uv sync → migrate → collectstatic → 重启
    web            构建并部署前端
    nginx          安装 nginx 配置与 systemd 单元
    all            api → web → nginx
    backup [标签]  立即备份数据库与 .env（服务器 data/backups/，默认标签 manual，不自动清理），并下载到本地 data/remote-backups/

自动备份：
    nginx / all 会安装 systemd 定时器 learning-star-backup.timer：每天 03:30 备份，标签 auto，保留最近 14 份；
    api / all 上传代码前先备份一次，标签 predeploy，保留最近 10 份。

上传代码的命令（api / web / nginx / all）只允许在 main 分支执行，
且工作区无未提交改动、与 origin/main 一致，保证线上运行的就是远端 main。

服务器信息读取 deploy/.env（不进 git，模板 deploy/.env.example）。
部署永不覆盖服务器上的 data/（数据库与媒体）。

线上 .env：本地维护（deploy/.env 的 ENV_LOCAL，默认 deploy/.env.production，不进 git），
由部署脚本送到服务器的 ENV_REMOTE（默认 APP_DIR/.env，权限 600）：
    env            上传线上 .env 并重启后端（all 若本地有该文件也会自动上传）
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


def deployed_stamp() -> bytes:
    try:
        rev = subprocess.run(['git', 'log', '-1', '--format=%H %ci %s'], cwd=ROOT, capture_output=True,
                             text=True, encoding='utf-8').stdout.strip()
    except OSError:
        rev = ''
    return f'{rev or "unknown"}\ndeployed {time.strftime("%Y-%m-%d %H:%M:%S")}\n'.encode()


def code_items() -> dict[str, Path | bytes]:
    return {
        'DEPLOYED': deployed_stamp(),
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
        f'{SERVICE}-backup.service': render((ROOT / f'deploy/systemd/{SERVICE}-backup.service').read_text(encoding='utf-8'), cfg).encode(),
        f'{SERVICE}-backup.timer': (ROOT / f'deploy/systemd/{SERVICE}-backup.timer').read_bytes(),
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
cp .staging/pyproject.toml .staging/uv.lock .staging/.python-version .staging/DEPLOYED .
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
sudo cp "$SERVICE.service" "$SERVICE-backup.service" "$SERVICE-backup.timer" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE-backup.timer" >/dev/null 2>&1
echo "  自动备份：$(systemctl list-timers "$SERVICE-backup.timer" --no-legend | awk '{print "下次 "$1" "$2" "$3}')"
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
        die('服务器上没有 .merged 标记，部署目录不是预期的状态，先用 check 查看')


# ── 命令 ──────────────────────────────────────────────────────────────────────

def cmd_check(cfg, _args) -> None:
    remote(cfg, r'''
echo "已连接 $(whoami)@$(hostname)"
echo "  部署目录 $APP：$([ -d "$APP" ] && echo 存在 || echo 不存在)"
echo "  .env（$ENV_FILE）：$([ -f "$ENV_FILE" ] && echo 存在 || echo 缺少)"
echo "  数据库：$([ -f "$APP/data/db.sqlite3" ] && du -h "$APP/data/db.sqlite3" | cut -f1 || echo 无)"
for s in "$SERVICE" "$SERVICE-backup.timer" nginx; do echo "  服务 $s=$(systemctl is-active $s 2>/dev/null || true)"; done
echo "  uv：$("$UV" --version 2>/dev/null || echo 未找到)"
sudo -n true 2>/dev/null && echo '  sudo 免密可用' || echo '  sudo 需要密码（部署会失败）'
''', APP=cfg['APP_DIR'], SERVICE=SERVICE)


def cmd_api(cfg, _args) -> None:
    require_merged(cfg)
    predeploy_backup(cfg)
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
    predeploy_backup(cfg)
    push_code(cfg)
    build_web(cfg)
    push_web(cfg)
    push_nginx(cfg)
    restart(cfg)


BACKUP = r'''
cd "$APP/backend"
if [ -f accounts/management/commands/backup_db.py ]; then
  ../.venv/bin/python manage.py backup_db --label "$LABEL" --keep "$KEEP"
else
  # 服务器上的代码还没有 backup_db（首次部署它之前）：直接用 SQLite 在线备份
  B="$APP/data/backups"; T=$(mktemp -d); umask 077; mkdir -p "$B"
  ../.venv/bin/python -c 'import sqlite3,sys; s=sqlite3.connect(f"file:{sys.argv[1]}?mode=ro",uri=True); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close()' \
    "$APP/data/db.sqlite3" "$T/db.sqlite3"
  [ -f "$ENV_FILE" ] && cp "$ENV_FILE" "$T/.env"
  out="$B/learning-star-$(date +%Y%m%d-%H%M%S)-$LABEL.tar.gz"
  tar -czf "$out" -C "$T" .; rm -rf "$T"; echo "$out"
fi
'''


def remote_backup(cfg, label: str, keep: int = 0) -> str:
    out = remote(cfg, BACKUP, capture=True, APP=cfg['APP_DIR'], LABEL=label, KEEP=str(keep))
    return out.strip().splitlines()[-1]


@step('部署前备份')
def predeploy_backup(cfg) -> None:
    print(f'  {remote_backup(cfg, "predeploy", keep=10)}')


def cmd_backup(cfg, args) -> None:
    require_merged(cfg)
    path = remote_backup(cfg, args[0] if args else 'manual')
    local = ROOT / 'data' / 'remote-backups' / Path(path).name
    local.parent.mkdir(parents=True, exist_ok=True)
    with open(local, 'wb') as f:
        r = subprocess.run(ssh_base(cfg) + [f'cat {shlex.quote(path)}'], stdout=f)
    if r.returncode != 0:
        die('下载失败')
    print(f'服务器：{path}\n本地：  {local}（{local.stat().st_size / 1024:.0f} KB）')


# ── 只从 main 部署 ────────────────────────────────────────────────────────────
# 部署上传的是本地工作区的文件，所以要求：在 main 分支、没有未提交改动、与 origin/main 完全一致。
DEPLOY_BRANCH = 'main'
SHIPS_CODE = {'api', 'web', 'nginx', 'all'}


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
    'backup': cmd_backup,
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
    if cmd in SHIPS_CODE:
        require_main()
    cfg = load_config()
    t0 = time.time()
    fn(cfg, sys.argv[2:])
    print(f'总用时 {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
