from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import TokenSerializer, UserSerializer

MIN_PASSWORD = 6


def _text(request, key: str) -> str:
    return str(request.data.get(key) or '').strip()


def _bad(detail: str, code=status.HTTP_400_BAD_REQUEST):
    return Response({'detail': detail}, status=code)


class TokenView(TokenObtainPairView):
    serializer_class = TokenSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username, password = _text(request, 'username'), _text(request, 'password')
        if not username or not password:
            return _bad('用户名和密码不能为空')
        if len(password) < MIN_PASSWORD:
            return _bad(f'密码至少 {MIN_PASSWORD} 位')
        if User.objects.filter(username=username).exists():
            return _bad('用户名已存在')
        user = User.objects.create_user(username=username, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        """目前只允许修改显示名称。"""
        if 'display_name' in request.data:
            name = _text(request, 'display_name')
            if len(name) > 50:
                return _bad('显示名称不能超过 50 个字符')
            request.user.display_name = name
            request.user.save(update_fields=['display_name'])
        return Response(UserSerializer(request.user).data)


class MePasswordView(APIView):
    def post(self, request):
        old, new = _text(request, 'old_password'), _text(request, 'new_password')
        if not old or not new:
            return _bad('请填写完整')
        if len(new) < MIN_PASSWORD:
            return _bad(f'新密码至少 {MIN_PASSWORD} 位')
        if not request.user.check_password(old):
            return _bad('原密码不正确')
        request.user.set_password(new)
        request.user.save()
        return Response({'detail': '密码已修改'})


# ── 管理员：用户管理 ─────────────────────────────────────────────────────────

class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(UserSerializer(User.objects.order_by('id'), many=True).data)

    def post(self, request):
        username, password, email = _text(request, 'username'), _text(request, 'password'), _text(request, 'email')
        if not username or not password:
            return _bad('用户名和密码不能为空')
        if len(password) < MIN_PASSWORD:
            return _bad(f'密码至少 {MIN_PASSWORD} 位')
        if User.objects.filter(username=username).exists():
            return _bad('用户名已存在')
        if email and User.objects.filter(email=email).exists():
            return _bad('邮箱已被使用')
        user = User.objects.create_user(username=username, password=password, email=email or None)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk: int):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user.is_staff:
            return _bad('不能删除管理员账户')
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserResetPasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk: int):
        new = _text(request, 'new_password')
        if len(new) < MIN_PASSWORD:
            return _bad(f'新密码至少 {MIN_PASSWORD} 位')
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.set_password(new)
        user.save()
        return Response({'detail': '密码已重置'})
