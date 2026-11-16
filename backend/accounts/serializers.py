from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'display_name', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = fields


class TokenSerializer(TokenObtainPairSerializer):
    """令牌里带上 username / is_staff，前端据此显示用户名、判断管理员。"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token
