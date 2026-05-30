import secrets
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers import CustomTokenObtainPairSerializer, UserSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('oldPassword')
        new_password = request.data.get('newPassword')

        if not old_password or not new_password:
            return Response({'detail': '请提供旧密码和新密码'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(old_password):
            return Response({'detail': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 6:
            return Response({'detail': '新密码至少6位'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        return Response({'detail': '密码修改成功'})

class UpdateDisplayView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        display_name = request.data.get('displayName', '').strip()
        if len(display_name) > 50:
            return Response({'detail': '显示名称不能超过50个字符'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.display_name = display_name
        request.user.save()
        return Response({'detail': '显示名称更新成功'})


class UpdateUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        if request.user.role == 'admin':
            return Response({'detail': '管理员不允许修改用户名'}, status=status.HTTP_403_FORBIDDEN)
        username = request.data.get('username', '').strip()
        if not username:
            return Response({'detail': '用户名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if len(username) > 50:
            return Response({'detail': '用户名不能超过50个字符'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.exclude(pk=request.user.pk).filter(username=username).exists():
            return Response({'detail': '用户名已被占用'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.username = username
        request.user.save()
        return Response(UserSerializer(request.user).data)


def _generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
