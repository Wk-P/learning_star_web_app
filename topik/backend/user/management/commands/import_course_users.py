"""把 course 站的账号并入 topik（统一账号以 topik 为准）。

    python manage.py import_course_users /path/to/course/db.sqlite3            # 只预览
    python manage.py import_course_users /path/to/course/db.sqlite3 --apply    # 真正写入

规则：
- 只在 course 存在的用户：在 topik 创建，原样复制密码哈希（原密码照常可用），
  course 管理员 → is_staff。
- 两边同名：保留 topik 账号不动，列入“同名冲突”供人工核对。
- 邮箱在 topik 已被其他账号占用：仍创建账号，但邮箱留空，并在报告中注明。
直接读取 course 的 SQLite 文件，不依赖 course 的 Django 代码。
"""
import sqlite3

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

User = get_user_model()


def _aware(value):
    # course 库里存的是 UTC 的朴素时间字符串
    dt = parse_datetime(value) if isinstance(value, str) else value
    if dt is None:
        return timezone.now()
    return dt if timezone.is_aware(dt) else timezone.make_aware(dt, timezone.utc)


class Command(BaseCommand):
    help = '把 course 站的用户并入 topik（默认只预览，加 --apply 写入）'

    def add_arguments(self, parser):
        parser.add_argument('course_db', help='course 后端的 db.sqlite3 路径')
        parser.add_argument('--apply', action='store_true', help='真正写入（默认只预览）')

    def handle(self, course_db, apply, **opts):
        try:
            conn = sqlite3.connect(f'file:{course_db}?mode=ro', uri=True)
            rows = conn.execute(
                'SELECT username, password, email, role, is_active, date_joined FROM auth_user'
            ).fetchall()
        except sqlite3.Error as e:
            raise CommandError(f'读取 course 数据库失败：{e}')

        created, conflicts, email_dropped = [], [], []
        with transaction.atomic():
            for username, password, email, role, is_active, date_joined in rows:
                if User.objects.filter(username=username).exists():
                    conflicts.append(username)
                    continue
                email = (email or '').strip() or None
                if email and User.objects.filter(email__iexact=email).exists():
                    email_dropped.append(f'{username} <{email}>')
                    email = None
                if apply:
                    User.objects.create(
                        username=username,
                        password=password,          # Django 密码哈希，可直接沿用
                        email=email,
                        is_staff=(role == 'admin'),
                        is_active=bool(is_active),
                        date_joined=_aware(date_joined),
                    )
                created.append(f"{username}{' (管理员)' if role == 'admin' else ''}")

        mode = '已写入' if apply else '预览（未写入，加 --apply 执行）'
        self.stdout.write(self.style.MIGRATE_HEADING(f'course 用户共 {len(rows)} 个 · {mode}'))
        self.stdout.write(self.style.SUCCESS(f'新建 {len(created)} 个：') + ', '.join(created))
        self.stdout.write(self.style.WARNING(f'同名冲突 {len(conflicts)} 个（保留 topik 账号）：') + ', '.join(conflicts))
        if email_dropped:
            self.stdout.write(self.style.WARNING(f'邮箱已被占用、已留空 {len(email_dropped)} 个：') + ', '.join(email_dropped))
