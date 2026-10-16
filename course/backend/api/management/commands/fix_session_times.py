"""
将旧数据（TIME_ZONE=UTC 时生成）的课节时间向前平移 8 小时，
使其变为正确的 Asia/Shanghai 对应 UTC 时间。

例：旧存储 2026-06-01T09:00:00Z（意图 09:00 上海时间）
    修正后 2026-06-01T01:00:00Z（= 09:00+08:00）
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import ClassSession

OFFSET = timedelta(hours=8)


class Command(BaseCommand):
    help = '将旧课节时间（UTC 误存）向前修正 8 小时'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅预览，不实际写入',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        sessions = ClassSession.objects.all()
        count = sessions.count()

        self.stdout.write(f'共 {count} 条课节记录，{"预览模式" if dry_run else "开始修正"}...')

        updated = 0
        for s in sessions:
            old_time = s.class_time
            new_time = old_time - OFFSET
            if dry_run:
                self.stdout.write(
                    f'  [{s.pk}] {s} : {old_time.strftime("%Y-%m-%d %H:%M %Z")} → {new_time.strftime("%Y-%m-%d %H:%M %Z")}'
                )
            else:
                s.class_time = new_time
                s.save(update_fields=['class_time'])
            updated += 1

        verb = '预览' if dry_run else '修正'
        self.stdout.write(self.style.SUCCESS(f'{verb}完成，共 {updated} 条。'))
        if dry_run:
            self.stdout.write('确认无误后去掉 --dry-run 重新运行。')
