from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """全站唯一的用户表：语言学习与课程共用。管理员身份 = is_staff。"""
    email = models.EmailField('邮箱', unique=True, blank=True, null=True)
    display_name = models.CharField('显示名称', max_length=50, blank=True, default='')

    def save(self, *args, **kwargs):
        # 空字符串会触发 unique 冲突，统一存为 NULL
        if not self.email:
            self.email = None
        super().save(*args, **kwargs)
