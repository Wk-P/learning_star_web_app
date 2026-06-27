import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Subject

User = get_user_model()


def _snake_to_camel(name: str) -> str:
    parts = name.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])


def _camel_to_snake(name: str) -> str:
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


class CamelCaseMixin:
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {_snake_to_camel(k): v for k, v in data.items()}

    def to_internal_value(self, data):
        converted = {_camel_to_snake(k): v for k, v in data.items()}
        return super().to_internal_value(converted)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token


class UserSerializer(CamelCaseMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email', 'role', 'display_name']


class AdminUserSerializer(CamelCaseMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email', 'role', 'display_name', 'date_joined', 'is_active']
        read_only_fields = ['date_joined', 'user_id']


class AdminUserCreateSerializer(CamelCaseMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email', 'role', 'password']
        read_only_fields = ['user_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SubjectSerializer(CamelCaseMixin, serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'icon', 'color']


