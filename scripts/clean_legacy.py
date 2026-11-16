"""清理合并前遗留的散落环境（旧 course/、topik/ 目录及其中的 .venv 等）。

合并后 Python 只有根目录一个 .venv。其他机器 git pull 之后，旧目录里
git 不管的文件（.venv、node_modules、数据库、.env）还留在磁盘上，用本脚本清掉。

用法（在仓库根目录，用系统 Python 或 uv run 都行，只用标准库）：
    python scripts/clean_legacy.py            # 只列出要删什么，不动文件
    python scripts/clean_legacy.py --yes      # 先备份数据库 / .env / media，再删除
    python scripts/clean_legacy.py --yes --sync   # 删完后 uv sync 重建根目录 .venv
"""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY_DIRS = ['course', 'topik']           # 合并前的旧项目，已从仓库删除
VENV_NAMES = {'.venv', 'venv', 'env', '.env'}  # 带 pyvenv.cfg 才算虚拟环境
SKIP = {'.git', 'node_modules'}
KEEP_PATTERNS = ['*.sqlite3', '.env', '.env.*', 'media']  # 删除前备份
BACKUP_ROOT = ROOT / '_migration' / 'backups'           # 已在 .gitignore


def find_stray_venvs() -> list[Path]:
    """仓库内除根目录 .venv 以外的所有虚拟环境。"""
    found = []
    for dirpath, dirnames, _ in os.walk(ROOT):
        here = Path(dirpath)
        for name in list(dirnames):
            p = here / name
            if name in SKIP or p == ROOT / '.venv':
                dirnames.remove(name)
            elif name in VENV_NAMES and (p / 'pyvenv.cfg').is_file():
                found.append(p)
                dirnames.remove(name)
    return found


def find_keep(base: Path) -> list[Path]:
    """旧目录里值得留底的文件（跳过 venv / node_modules 内部；.env 是环境目录时也跳过）。"""
    out = []
    for pattern in KEEP_PATTERNS:
        for p in base.rglob(pattern):
            inner = p.relative_to(base).parts[:-1]
            if any(part in SKIP or part in VENV_NAMES for part in inner):
                continue
            if p.is_dir() and (p / 'pyvenv.cfg').exists():
                continue
            out.append(p)
    return out


def _force_remove(func, path, _exc):
    # Windows 下只读文件（如 .git 对象、某些包文件）需先去掉只读位
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove(p: Path) -> None:
    if p.is_dir():
        shutil.rmtree(p, onexc=_force_remove) if sys.version_info >= (3, 12) \
            else shutil.rmtree(p, onerror=_force_remove)
    else:
        p.unlink()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--yes', action='store_true', help='真正执行删除（默认只预览）')
    ap.add_argument('--sync', action='store_true', help='完成后运行 uv sync 重建根目录 .venv')
    args = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass

    legacy = [ROOT / d for d in LEGACY_DIRS if (ROOT / d).exists()]
    venvs = [v for v in find_stray_venvs() if not any(v.is_relative_to(l) for l in legacy)]
    keep = [k for l in legacy for k in find_keep(l)]

    if not legacy and not venvs:
        print('没有遗留环境，已经是干净的。')
    else:
        for l in legacy:
            print(f'[删除旧项目目录] {l.relative_to(ROOT)}')
        for v in venvs:
            print(f'[删除散落 venv ] {v.relative_to(ROOT)}')
        for k in keep:
            print(f'[先备份      ] {k.relative_to(ROOT)}')

    tracked = legacy and subprocess.run(['git', 'ls-files', '--', *[str(l) for l in legacy]],
                                        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if tracked:
        print('\n这些目录里还有 git 跟踪的文件，说明还没 pull 到合并后的版本，先 git pull 再运行：')
        print(tracked[:500])
        return 1

    if not args.yes:
        if legacy or venvs:
            print('\n以上为预览，加 --yes 执行。')
        return 0

    if keep:
        dest = BACKUP_ROOT / f'legacy-{datetime.now():%Y%m%d-%H%M%S}'
        for k in keep:
            target = dest / k.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree if k.is_dir() else shutil.copy2)(k, target)
        print(f'\n已备份到 {dest.relative_to(ROOT)}')

    for p in legacy + venvs:
        remove(p)
        print(f'已删除 {p.relative_to(ROOT)}')

    if args.sync:
        print('\n运行 uv sync ...')
        return subprocess.run(['uv', 'sync'], cwd=ROOT).returncode
    return 0


if __name__ == '__main__':
    sys.exit(main())
