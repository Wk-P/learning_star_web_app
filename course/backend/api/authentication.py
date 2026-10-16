"""统一登录：course 不再自己签发令牌，而是信任 topik 后端签发的 JWT。

两个后端用同一个 JWT_SIGNING_KEY。topik 的令牌里带有 username 与 is_staff，
这里按 username 对应到 course 的本地用户（不存在则自动创建），
管理员身份随 topik 的 is_staff 同步。账号、密码只在 topik 维护。
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from .models import User


class TopikJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        username = validated_token.get('username')
        if not username:
            raise InvalidToken('令牌缺少 username，请重新登录')

        role = 'admin' if validated_token.get('is_staff') else 'user'
        user, created = User.objects.get_or_create(username=username, defaults={'role': role})
        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])
        elif user.role != role:
            user.role = role
            user.save(update_fields=['role'])

        if not user.is_active:
            raise InvalidToken('账号已停用')
        return user
