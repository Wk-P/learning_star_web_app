"""本地开发测试账号：一个管理员、一个普通学员。

    python manage.py create_dev_users

- 账号名与密码来自 .env 的 DEV_ADMIN_USERNAME / DEV_ADMIN_PASSWORD / DEV_USER_USERNAME / DEV_USER_PASSWORD
  （默认 dev_admin / dev_user，密码 dev123456），与线上导入的账号不重名。
- 不存在则创建；已存在则把密码重置为 .env 中的值，保证 `scripts/dev.py info` 显示的账号一定能登录。
- 普通学员自动获得本地所有语言、所有资源类型第一层目录的学习权限，方便测试学员视角。
- 只允许在 DEBUG=True 时运行，避免误在生产环境建出弱密码账号。
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from languages.models import MEDIA_KINDS, Language, MediaPermission
from languages.services import scan

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
            if not is_admin:
                n = self.grant_all(user)
                self.stdout.write(f'  学习权限：本地全部第一层目录 {n} 项')

    @staticmethod
    def grant_all(user) -> int:
        n = 0
        for lang in Language.objects.all():
            for kind in MEDIA_KINDS:
                for top in {f['path'][0] for f in scan(lang, kind) if f['path']}:
                    MediaPermission.objects.get_or_create(user=user, language=lang, media_type=kind, root_dir=top)
                    n += 1
        return n
