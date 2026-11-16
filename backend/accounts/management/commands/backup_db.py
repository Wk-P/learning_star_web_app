"""备份数据库与线上 .env 为一个压缩包（服务器上由 systemd 定时器每天执行）。

    python manage.py backup_db [--label manual] [--keep 14]

- 输出 DATA_DIR/backups/learning-star-<时间>-<label>.tar.gz，内含：
  db.sqlite3（SQLite 在线备份 API，服务运行中也能得到一致的快照）、.env（若存在）、
  DEPLOYED（部署的代码版本，若存在）
- --keep N：只清理同一 label 的旧备份，保留最近 N 个（0 表示不清理）。
  自动备份用 label=auto；手动备份默认 label=manual、不自动清理。
- 媒体文件（视频等，80G+）不在此备份内。
"""
import io
import os
import sqlite3
import tarfile
import tempfile
import time
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = '备份数据库与 .env（data/backups/），可按 label 保留最近 N 个'

    def add_arguments(self, parser):
        parser.add_argument('--label', default='manual', help='备份标签，如 auto / manual / before-xxx')
        parser.add_argument('--keep', type=int, default=0, help='同一标签只保留最近 N 个（0 = 不清理）')

    def handle(self, *args, label, keep, **options):
        if not label.replace('-', '').replace('_', '').isalnum():
            raise CommandError('label 只能包含字母、数字、- 和 _')
        db = Path(settings.DATABASES['default']['NAME'])
        if not db.is_file():
            raise CommandError(f'找不到数据库：{db}')
        out_dir = Path(settings.DATA_DIR) / 'backups'
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f'learning-star-{datetime.now():%Y%m%d-%H%M%S}-{label}.tar.gz'

        with tempfile.TemporaryDirectory() as tmp:
            snap = Path(tmp) / 'db.sqlite3'
            src = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
            dst = sqlite3.connect(snap)
            src.backup(dst)
            dst.close()
            src.close()

            old_umask = os.umask(0o077)          # 内含密钥：只有本用户可读
            try:
                with tarfile.open(out, 'w:gz') as tar:
                    tar.add(snap, 'db.sqlite3')
                    env_file = Path(os.environ.get('ENV_FILE') or settings.ROOT_DIR / '.env')
                    if env_file.is_file():
                        tar.add(env_file, '.env')
                    deployed = settings.ROOT_DIR / 'DEPLOYED'
                    if deployed.is_file():
                        tar.add(deployed, 'DEPLOYED')
                    stamp = f'{datetime.now().isoformat(timespec="seconds")} label={label}\n'.encode()
                    info = tarfile.TarInfo('BACKUP_INFO')
                    info.size, info.mtime = len(stamp), int(time.time())
                    tar.addfile(info, io.BytesIO(stamp))
            finally:
                os.umask(old_umask)

        self.stdout.write(str(out))
        if keep > 0:
            same = sorted(out_dir.glob(f'learning-star-*-{label}.tar.gz'))
            for old in same[:-keep]:
                old.unlink()
                self.stderr.write(f'已清理旧备份 {old.name}')
