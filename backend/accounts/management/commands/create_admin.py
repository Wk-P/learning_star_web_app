import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '按 .env 的 ADMIN_USERNAME / ADMIN_PASSWORD 创建本地测试管理员（已存在则跳过）'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD', 'change-me')
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'管理员 "{username}" 已存在，跳过')
            return
        User.objects.create_superuser(username=username, password=password, email=None)
        self.stdout.write(self.style.SUCCESS(f'已创建管理员 "{username}"'))
