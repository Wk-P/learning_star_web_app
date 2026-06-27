import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


def _generate_user_id() -> str:
    return secrets.token_hex(4)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', '学生'),
        ('admin', '管理员'),
    ]
    display_name = models.CharField(max_length=50, blank=True, default='')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    user_id = models.CharField(
        max_length=8, unique=True, blank=True,
        verbose_name='用户ID (8位hex)',
    )

    def save(self, *args, **kwargs):
        if not self.user_id:
            uid = _generate_user_id()
            while User.objects.filter(user_id=uid).exists():
                uid = _generate_user_id()
            self.user_id = uid
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'auth_user'


class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True, default='📖')
    color = models.CharField(max_length=7, blank=True, default='#6366f1')

    def __str__(self):
        return self.name


class Course(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
