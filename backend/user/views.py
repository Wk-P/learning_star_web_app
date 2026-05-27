from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import status

from .models import User
from .services import get_user_list, get_user
from .serializers import UserSerializer


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: Request):
        return Response(get_user_list())


class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: Request):
        pk = request.query_params.get('id')
        data = get_user(pk=pk)
        if data:
            return Response(data)
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request: Request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        email    = request.data.get('email', '').strip()

        if not username or not password:
            return Response({'detail': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'detail': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        email    = request.data.get('email', '').strip()

        if not username or not password:
            return Response({'detail': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({'detail': '密码至少 6 位'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'detail': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MePermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        from permission.models import MediaPermission
        perms = MediaPermission.objects.filter(user=request.user)
        video = [p.root_dir for p in perms if p.media_type == 'video']
        audio = [p.root_dir for p in perms if p.media_type == 'audio']
        pdf   = [p.root_dir for p in perms if p.media_type == 'pdf']
        return Response({'video': video, 'audio': audio, 'pdf': pdf})


class MePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        old = request.data.get('old_password', '').strip()
        new = request.data.get('new_password', '').strip()
        if not old or not new:
            return Response({'detail': '请填写完整'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new) < 6:
            return Response({'detail': '新密码至少 6 位'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.check_password(old):
            return Response({'detail': '原密码不正确'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new)
        request.user.save()
        return Response({'detail': '密码已修改'})


class UserDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request: Request, pk: int):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if user.is_staff:
            return Response({'detail': '不能删除管理员账户'}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
