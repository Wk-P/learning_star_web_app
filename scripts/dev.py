"""本地开发入口（Windows / macOS / Linux 通用）。

    uv run scripts/dev.py <命令>

    setup          首次：uv sync（根目录唯一 .venv）、安装前端依赖、生成 .env、迁移数据库、创建测试管理员
    migrate        数据库迁移（拉取新代码后出现 unapplied migrations 提示时）
    info           显示本地访问地址与测试账号
    all            同时启动后端与前端，Ctrl-C 全部停止
    api            后端 :8000（backend/，Django）
    web            前端 :5173（代理 /api、/media 到后端）
    build          构建前端
    images         由 images/src 重新生成 web/public 图片
    import-legacy  <备份目录> [--apply]  把合并前的线上数据快照导入本地数据库（默认预览）
    manage         <参数...>  执行任意 manage.py 命令，如：manage createsuperuser

依赖：uv（https://docs.astral.sh/uv/）、Node ^20.19 或 >=22.12、pnpm
只用标准库，不依赖 .venv 也能运行；所有 Python 命令经 uv run 使用根目录的 .venv。
"""
from __future__ import annotations

import os
import shutil
import signal
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


# ── 命令 ──────────────────────────────────────────────────────────────────────

def cmd_info(_args) -> None:
    user = env_value('ADMIN_USERNAME', 'admin')
    print(f'''────────────────────────────────────────────────────────
 前端        http://localhost:5173
 登录页      http://localhost:5173/login
 管理后台    http://localhost:5173/admin
 后端 API    http://localhost:8000/api/

 本地测试账号（管理员）
   用户名    {user}
   密码      {env_value('ADMIN_PASSWORD', 'change-me')}
   来源      根目录 .env 的 ADMIN_USERNAME / ADMIN_PASSWORD
   改密码    uv run scripts/dev.py manage changepassword {user}
             （setup 只在账号不存在时创建，不会覆盖已有账号的密码）
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
    print('▶ 创建本地测试管理员')
    manage('create_admin')
    print('\n✔ 完成。启动：uv run scripts/dev.py all')
    cmd_info(None)


def cmd_migrate(_args) -> None:
    print('▶ 数据库迁移')
    manage('migrate')


def cmd_api(_args) -> None:
    sys.exit(manage('runserver', '8000', check=False))


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


def _stop(procs: list[subprocess.Popen]) -> None:
    for p in procs:
        if p.poll() is not None:
            continue
        if WINDOWS:
            # 结束整个进程树（uv → python → runserver 子进程；pnpm → node）
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass


def cmd_all(_args) -> None:
    """后端与前端一起跑；任一退出或 Ctrl-C 时全部停止。"""
    cmd_info(None)
    extra = {} if WINDOWS else {'start_new_session': True}
    procs = [
        subprocess.Popen([uv(), 'run', 'python', 'manage.py', 'runserver', '8000'], cwd=BACKEND, **extra),
        subprocess.Popen([pnpm(), 'dev'], cwd=WEB, **extra),
    ]
    try:
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        _stop(procs)


COMMANDS = {
    'setup': cmd_setup,
    'migrate': cmd_migrate,
    'info': cmd_info,
    'all': cmd_all,
    'api': cmd_api,
    'web': cmd_web,
    'build': cmd_build,
    'images': cmd_images,
    'import-legacy': cmd_import_legacy,
    'manage': cmd_manage,
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
