"""本地开发入口（Windows / macOS / Linux 通用）。

    uv run scripts/task.py <命令>

  开发服务（后台运行，关掉终端也不停；日志在 data/.dev/）
    dev all             后台启动后端 :8000 与前端 :5173，就绪后显示访问地址与测试账号
    dev stop            停止后台的后端与前端
    dev restart         重启（stop + all）
    dev status          查看是否在运行
    dev logs [api|web]  查看最近日志（默认两个都看）

  其他
    setup          首次：uv sync（根目录唯一 .venv）、安装前端依赖、生成 .env、迁移数据库、创建测试账号
    migrate        数据库迁移（拉取新代码后出现 unapplied migrations 提示时），并确保测试账号可用
    users          创建 / 重置本地测试账号（管理员 + 学员，密码以 .env 为准）
    info           显示本地访问地址与测试账号
    api / web      前台运行单个服务（看实时输出、调试用，Ctrl-C 结束）
    build          构建前端
    images         由 images/src 重新生成 web/public 图片
    import-legacy  <备份目录> [--apply]  把合并前的线上数据快照导入本地数据库（默认预览）
    manage         <参数...>  执行任意 manage.py 命令，如：manage createsuperuser
    deploy         <参数...>  转给 scripts/deploy.py（线上部署）

依赖：uv（https://docs.astral.sh/uv/）、Node ^20.19 或 >=22.12、pnpm
只用标准库，不依赖 .venv 也能运行；所有 Python 命令经 uv run 使用根目录的 .venv。
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / 'backend'
WEB = ROOT / 'web'
ENV_FILE = ROOT / '.env'
ENV_EXAMPLE = ROOT / '.env.example'
WINDOWS = os.name == 'nt'

DEV_DIR = ROOT / 'data' / '.dev'          # 后台服务的 pid 与日志（data/ 不进 git）
PID_FILE = DEV_DIR / 'pids.json'
SERVICES = {'api': 8000, 'web': 5173}
LABELS = {'api': '后端', 'web': '前端'}

# Python 读写文件统一 UTF-8（Windows 默认 GBK）
os.environ['PYTHONUTF8'] = '1'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def which(cmd: str, hint: str) -> str:
    path = shutil.which(cmd)
    if not path:
        die(f'缺少 {cmd}：{hint}')
    return path


def uv() -> str:
    return which('uv', 'https://docs.astral.sh/uv/getting-started/installation/')


def pnpm() -> str:
    return which('pnpm', 'corepack enable 或 npm i -g pnpm')


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> int:
    rc = subprocess.call(cmd, cwd=cwd)
    if check and rc != 0:
        die(f'命令失败（退出码 {rc}）：{" ".join(cmd)}')
    return rc


def manage(*args: str, check: bool = True) -> int:
    return run([uv(), 'run', 'python', 'manage.py', *args], cwd=BACKEND, check=check)


def env_value(key: str, default: str) -> str:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
            if line.strip().startswith(f'{key}='):
                return line.split('=', 1)[1].strip().strip('"\'') or default
    return default


# ── 常用命令 ──────────────────────────────────────────────────────────────────

def cmd_info(_args) -> None:
    # 默认值与 backend/accounts/management/commands/create_dev_users.py 一致
    admin = env_value('DEV_ADMIN_USERNAME', 'dev_admin'), env_value('DEV_ADMIN_PASSWORD', 'dev123456')
    user = env_value('DEV_USER_USERNAME', 'dev_user'), env_value('DEV_USER_PASSWORD', 'dev123456')
    print(f'''────────────────────────────────────────────────────────
 前端        http://localhost:5173
 登录页      http://localhost:5173/login
 管理后台    http://localhost:5173/admin
 后端 API    http://localhost:8000/api/

 本地测试账号
   管理员    {admin[0]:<16} 密码 {admin[1]}
   学员      {user[0]:<16} 密码 {user[1]}
   来源      根目录 .env 的 DEV_ADMIN_* / DEV_USER_*
   重置      uv run scripts/task.py users（setup、migrate 时也会自动执行）
────────────────────────────────────────────────────────''')


def cmd_setup(_args) -> None:
    run([uv(), 'sync'])
    if not ENV_FILE.exists():
        text = ENV_EXAMPLE.read_text(encoding='utf-8')
        # 本地开发默认开启 DEBUG
        text = text.replace('DEBUG=False', 'DEBUG=True')
        ENV_FILE.write_text(text, encoding='utf-8', newline='\n')
        print('已由 .env.example 生成 .env（本地开发用，按需修改）')
    run([pnpm(), 'install'], cwd=WEB)
    cmd_migrate(None)
    print('\n✔ 完成。启动：uv run scripts/task.py dev all')
    cmd_info(None)


def cmd_migrate(_args) -> None:
    print('▶ 数据库迁移')
    manage('migrate')
    cmd_users(None)


def cmd_users(_args) -> None:
    print('▶ 本地测试账号')
    manage('create_dev_users')


def cmd_api(_args) -> None:
    sys.exit(manage('runserver', str(SERVICES['api']), check=False))


def cmd_web(_args) -> None:
    sys.exit(run([pnpm(), 'dev'], cwd=WEB, check=False))


def cmd_build(_args) -> None:
    run([pnpm(), 'install', '--frozen-lockfile'], cwd=WEB)
    run([pnpm(), 'run', 'build'], cwd=WEB)


def cmd_images(_args) -> None:
    run([uv(), 'run', 'python', str(ROOT / 'scripts' / 'optimize_images.py')])


def cmd_manage(args: list[str]) -> None:
    sys.exit(manage(*args, check=False))


def cmd_import_legacy(args: list[str]) -> None:
    if not args:
        die('用法：import-legacy <备份目录> [--apply]\n'
            '备份目录为 _migration/backups/merge_backup_*（内含 db/topik.sqlite3、db/course.sqlite3、course/bilibili/）')
    src = Path(args[0]).resolve()
    manage('migrate', '-v', '0')
    manage('import_legacy',
           '--topik', str(src / 'db' / 'topik.sqlite3'),
           '--course', str(src / 'db' / 'course.sqlite3'),
           '--bilibili', str(src / 'course' / 'bilibili'),
           *args[1:])
    if '--apply' in args[1:]:
        cmd_users(None)


def cmd_deploy(args: list[str]) -> None:
    sys.exit(run([sys.executable, str(ROOT / 'scripts' / 'deploy.py'), *args], check=False))


# ── 后台开发服务（dev all / stop / restart / status / logs） ───────────────────

def _service_cmd(name: str) -> tuple[list[str], Path]:
    if name == 'api':
        return [uv(), 'run', 'python', 'manage.py', 'runserver', str(SERVICES['api'])], BACKEND
    return [pnpm(), 'dev'], WEB


def _port_open(port: int) -> bool:
    for host in ('127.0.0.1', '::1'):          # vite 可能只监听 IPv6 的 localhost
        try:
            with socket.create_connection((host, port), timeout=0.3):
                return True
        except OSError:
            pass
    return False


def _pid_alive(pid: int) -> bool:
    if WINDOWS:
        out = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/NH', '/FO', 'CSV'],
                             capture_output=True, text=True, errors='replace').stdout
        return f'"{pid}"' in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _running() -> dict[str, int]:
    try:
        pids = {k: int(v) for k, v in json.loads(PID_FILE.read_text(encoding='utf-8')).items()}
    except (OSError, ValueError):
        return {}
    return {k: pid for k, pid in pids.items() if _pid_alive(pid)}


def _spawn(name: str) -> int:
    cmd, cwd = _service_cmd(name)
    log = open(DEV_DIR / f'{name}.log', 'w', encoding='utf-8')
    if WINDOWS:
        # 不弹窗、脱离当前终端与 uv 的进程作业：task.py 退出、关掉终端后服务继续运行
        extra = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
                 | subprocess.CREATE_BREAKAWAY_FROM_JOB}
    else:
        extra = {'start_new_session': True}
    env = {**os.environ, 'PYTHONUNBUFFERED': '1', 'NO_COLOR': '1'}
    p = subprocess.Popen(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         env=env, **extra)
    log.close()
    return p.pid


def _kill_tree(pid: int) -> None:
    if WINDOWS:
        # 结束整个进程树（uv → python → runserver 子进程；pnpm → node）
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    else:
        try:
            os.killpg(pid, signal.SIGTERM)
        except OSError:
            pass


def _tail(name: str, n: int = 15) -> str:
    try:
        lines = (DEV_DIR / f'{name}.log').read_text(encoding='utf-8', errors='replace').splitlines()
    except OSError:
        return '（无日志）'
    return '\n'.join(lines[-n:]) or '（日志为空）'


def dev_all() -> None:
    DEV_DIR.mkdir(parents=True, exist_ok=True)
    running = _running()
    busy = [f'{LABELS[k]} :{p}' for k, p in SERVICES.items() if k not in running and _port_open(p)]
    if busy:
        die(f'端口已被占用：{", ".join(busy)}（不是 task.py 后台启动的，请先关掉它）')
    pids = dict(running)
    for name in SERVICES:
        if name not in pids:
            pids[name] = _spawn(name)
    PID_FILE.write_text(json.dumps(pids), encoding='utf-8')

    print('▶ 后台启动中…' if len(running) < len(SERVICES) else '▶ 已在后台运行')
    pending = set(SERVICES)
    deadline = time.time() + 90
    while pending and time.time() < deadline:
        pending = {n for n in pending if not _port_open(SERVICES[n])}
        if any(not _pid_alive(pids[n]) for n in pending):
            break
        time.sleep(0.5)
    for name, port in SERVICES.items():
        if name in pending:
            print(f'  ✘ {LABELS[name]} :{port} 启动失败，最近日志：\n{_tail(name)}')
        else:
            print(f'  ✔ {LABELS[name]} :{port}')
    if pending:
        dev_stop(quiet=True)
        sys.exit(1)
    cmd_info(None)
    print(' 停止 uv run scripts/task.py dev stop   重启 dev restart   日志 dev logs（data/.dev/）')


def dev_stop(quiet: bool = False) -> None:
    pids = _running()
    for pid in pids.values():
        _kill_tree(pid)
    PID_FILE.unlink(missing_ok=True)
    if quiet:
        return
    print('✔ 已停止后端与前端' if pids else '没有在运行的后台服务')
    time.sleep(0.5)
    left = [f':{p}' for p in SERVICES.values() if _port_open(p)]
    if left:
        print(f'  注意：端口 {", ".join(left)} 仍被占用（可能是别处启动的进程）')


def dev_status() -> None:
    pids = _running()
    for name, port in SERVICES.items():
        if name not in pids:
            state = '未运行'
        else:
            state = ('运行中' if _port_open(port) else '启动中') + f'  pid {pids[name]}'
        print(f'  {LABELS[name]} :{port}  {state}')


def cmd_dev(args: list[str]) -> None:
    sub = args[0] if args else ''
    if sub == 'all':
        dev_all()
    elif sub == 'stop':
        dev_stop()
    elif sub == 'restart':
        dev_stop(quiet=True)
        time.sleep(1)
        dev_all()
    elif sub == 'status':
        dev_status()
    elif sub == 'logs':
        for name in (args[1:] or list(SERVICES)):
            if name not in SERVICES:
                die(f'未知服务：{name}（api 或 web）')
            print(f'── {name}.log（最近 40 行）──\n{_tail(name, 40)}\n')
    else:
        die('用法：uv run scripts/task.py dev all | stop | restart | status | logs [api|web]')


COMMANDS = {
    'dev': cmd_dev,
    'setup': cmd_setup,
    'migrate': cmd_migrate,
    'users': cmd_users,
    'info': cmd_info,
    'api': cmd_api,
    'web': cmd_web,
    'build': cmd_build,
    'images': cmd_images,
    'import-legacy': cmd_import_legacy,
    'manage': cmd_manage,
    'deploy': cmd_deploy,
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
    fn(sys.argv[2:])


if __name__ == '__main__':
    main()
