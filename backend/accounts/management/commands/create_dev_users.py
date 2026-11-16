"""本地开发测试账号：一个管理员、一个普通学员。

    python manage.py create_dev_users

- 账号名与密码来自 .env 的 DEV_ADMIN_USERNAME / DEV_ADMIN_PASSWORD / DEV_USER_USERNAME / DEV_USER_PASSWORD
  （默认 dev_admin / dev_user，密码 dev123456），与线上导入的账号不重名。
- 不存在则创建；已存在则把密码重置为 .env 中的值，保证 `scripts/task.py info` 显示的账号一定能登录。
- 只允许在 DEBUG=True 时运行，避免误在生产环境建出弱密码账号。
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


DEFAULT_PASSWORD = 'dev123456'


def dev_accounts() -> list[tuple[str, str, bool]]:
    """[(用户名, 密码, 是否管理员)]"""
    return [
        (os.environ.get('DEV_ADMIN_USERNAME') or 'dev_admin', os.environ.get('DEV_ADMIN_PASSWORD') or DEFAULT_PASSWORD, True),
        (os.environ.get('DEV_USER_USERNAME') or 'dev_user', os.environ.get('DEV_USER_PASSWORD') or DEFAULT_PASSWORD, False),
    ]


class Command(BaseCommand):
    help = '创建 / 重置本地开发测试账号（管理员 + 普通学员），仅 DEBUG 下可用'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('只能在本地开发（DEBUG=True）时创建测试账号')
        User = get_user_model()
        for username, password, is_admin in dev_accounts():
            user, created = User.objects.get_or_create(username=username)
            user.is_staff = user.is_superuser = is_admin
            user.is_active = True
            user.display_name = user.display_name or ('测试管理员' if is_admin else '测试学员')
            user.set_password(password)
            user.save()
            self.stdout.write(f'{"已创建" if created else "已重置密码"}：{username}（{"管理员" if is_admin else "学员"}）')
