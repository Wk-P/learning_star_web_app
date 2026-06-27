import os
import secrets
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Subject
from ..permissions import IsAdmin
from ..serializers import SubjectSerializer, AdminUserSerializer, AdminUserCreateSerializer
from .course_views import _subject_filepath, _read_videos, ROADMAP_FILE

User = get_user_model()

BILIBILI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bilibili')


def _random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))



def _write_videos(filepath: str, videos: list[dict]) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for v in videos:
            f.write(f"{v['title']} {v['url']}\n")


# ── 用户管理（仅 admin） ──────────────────────────────────────────────────────

class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by('id')
        return Response(AdminUserSerializer(users, many=True).data)

    def post(self, request):
        s = AdminUserCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(AdminUserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminUserSerializer(user).data)

    def patch(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = AdminUserSerializer(user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserResetPasswordView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        new_pw = _random_password()
        user.set_password(new_pw)
        user.save()
        return Response({'newPassword': new_pw})


# ── 科目管理（仅 admin） ──────────────────────────────────────────────────────

class AdminSubjectListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(SubjectSerializer(Subject.objects.all().order_by('id'), many=True).data)

    def post(self, request):
        s = SubjectSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class AdminSubjectDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get(self, subject_id):
        try:
            return Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return None

    def get(self, request, subject_id):
        obj = self._get(subject_id)
        if not obj:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(SubjectSerializer(obj).data)

    def patch(self, request, subject_id):
        obj = self._get(subject_id)
        if not obj:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = SubjectSerializer(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, subject_id):
        obj = self._get(subject_id)
        if not obj:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 科目视频管理（仅 admin） ──────────────────────────────────────────────────

class AdminSubjectVideosView(APIView):
    """管理员管理某科目的 B 站视频列表（文件存储）。"""
    permission_classes = [IsAdmin]

    def _get_subject(self, subject_id):
        try:
            return Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return None

    def get(self, request, subject_id):
        subject = self._get_subject(subject_id)
        if not subject:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(_read_videos(_subject_filepath(subject)))

    def post(self, request, subject_id):
        """追加一条视频。body: {line}，格式与 txt 文件一致：「标题 https://...」"""
        subject = self._get_subject(subject_id)
        if not subject:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        line = request.data.get('line', '').strip()
        if not line:
            return Response({'detail': '请提供 line'}, status=status.HTTP_400_BAD_REQUEST)
        idx = line.find(' http')
        if idx == -1:
            return Response({'detail': '格式错误，找不到链接（应包含 http）'}, status=status.HTTP_400_BAD_REQUEST)
        title = line[:idx].strip()
        url = line[idx:].strip()
        if not title or not url:
            return Response({'detail': '格式错误，标题或链接为空'}, status=status.HTTP_400_BAD_REQUEST)
        filepath = _subject_filepath(subject)
        videos = _read_videos(filepath)
        videos.append({'title': title, 'url': url})
        _write_videos(filepath, videos)
        return Response({'index': len(videos) - 1, 'title': title, 'url': url}, status=status.HTTP_201_CREATED)

    def put(self, request, subject_id):
        """整体替换视频列表。body: [{title, url}, ...]"""
        subject = self._get_subject(subject_id)
        if not subject:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not isinstance(request.data, list):
            return Response({'detail': '请提供列表数据'}, status=status.HTTP_400_BAD_REQUEST)
        videos = [{'title': v.get('title', '').strip(), 'url': v.get('url', '').strip()} for v in request.data]
        filepath = _subject_filepath(subject)
        _write_videos(filepath, videos)
        return Response(_read_videos(filepath))


class AdminRoadmapView(APIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]

    def get(self, request):
        if not os.path.exists(ROADMAP_FILE):
            return Response({'exists': False})
        stat = os.stat(ROADMAP_FILE)
        return Response({'exists': True, 'size': stat.st_size, 'updatedAt': stat.st_mtime})

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        if not file.name.lower().endswith('.html'):
            return Response({'detail': '只支持 .html 文件'}, status=status.HTTP_400_BAD_REQUEST)
        if file.size > 5 * 1024 * 1024:
            return Response({'detail': '文件不能超过 5MB'}, status=status.HTTP_400_BAD_REQUEST)
        content = file.read().decode('utf-8')
        os.makedirs(os.path.dirname(ROADMAP_FILE), exist_ok=True)
        with open(ROADMAP_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        stat = os.stat(ROADMAP_FILE)
        return Response({'exists': True, 'size': stat.st_size, 'updatedAt': stat.st_mtime})


class AdminSubjectVideoDetailView(APIView):
    """对单条视频进行修改或删除（按行号索引）。"""
    permission_classes = [IsAdmin]

    def _get_subject(self, subject_id):
        try:
            return Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return None

    def patch(self, request, subject_id, index):
        subject = self._get_subject(subject_id)
        if not subject:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        filepath = _subject_filepath(subject)
        videos = _read_videos(filepath)
        real_index = next((i for i, v in enumerate(videos) if v['index'] == index), None)
        if real_index is None:
            return Response({'detail': '视频不存在'}, status=status.HTTP_404_NOT_FOUND)
        if 'title' in request.data:
            videos[real_index]['title'] = request.data['title'].strip()
        if 'url' in request.data:
            videos[real_index]['url'] = request.data['url'].strip()
        _write_videos(filepath, videos)
        return Response({'index': real_index, **{k: v for k, v in videos[real_index].items() if k != 'index'}})

    def delete(self, request, subject_id, index):
        subject = self._get_subject(subject_id)
        if not subject:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        filepath = _subject_filepath(subject)
        videos = _read_videos(filepath)
        real_index = next((i for i, v in enumerate(videos) if v['index'] == index), None)
        if real_index is None:
            return Response({'detail': '视频不存在'}, status=status.HTTP_404_NOT_FOUND)
        videos.pop(real_index)
        _write_videos(filepath, videos)
        return Response(status=status.HTTP_204_NO_CONTENT)


