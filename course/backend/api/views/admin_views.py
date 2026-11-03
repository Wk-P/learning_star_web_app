import os
import secrets
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Subject
from ..permissions import IsAdmin
from ..serializers import SubjectSerializer, AdminUserSerializer, AdminUserCreateSerializer
from .course_views import _subject_filepath, _read_videos, parse_levels, parse_tags, video_key, with_platform_tag

User = get_user_model()

BILIBILI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bilibili')


def _random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))



def _write_videos(filepath: str, videos: list[dict]) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for v in videos:
            levels = v.get('levels') or []
            tags = v.get('tags') or []
            suffix = f" |{','.join(levels)}" if levels or tags else ''
            if tags:
                suffix += f" |{','.join(tags)}"
            f.write(f"{v['title']} {v['url']}{suffix}\n")


def _find_duplicate(videos: list[dict], url: str, skip: int | None = None):
    key = video_key(url)
    return next((v for i, v in enumerate(videos) if i != skip and video_key(v['url']) == key), None)


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
        url = line[idx:].split()[0]
        if not title or not url:
            return Response({'detail': '格式错误，标题或链接为空'}, status=status.HTTP_400_BAD_REQUEST)
        filepath = _subject_filepath(subject)
        videos = _read_videos(filepath)
        dup = _find_duplicate(videos, url)
        if dup:
            return Response({'detail': f'该视频已存在：「{dup["title"]}」'}, status=status.HTTP_409_CONFLICT)
        levels = parse_levels(request.data.get('levels'))
        if len(levels) > 1:
            return Response({'detail': '每个视频只能选择一个阶段'}, status=status.HTTP_400_BAD_REQUEST)
        tags = with_platform_tag(url, parse_tags(request.data.get('tags')))
        videos.append({'title': title, 'url': url, 'levels': levels, 'tags': tags})
        _write_videos(filepath, videos)
        return Response({'index': len(videos) - 1, 'title': title, 'url': url, 'levels': levels, 'tags': tags}, status=status.HTTP_201_CREATED)

    def put(self, request, subject_id):
        """整体替换视频列表。body: [{title, url}, ...]"""
        subject = self._get_subject(subject_id)
        if not subject:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not isinstance(request.data, list):
            return Response({'detail': '请提供列表数据'}, status=status.HTTP_400_BAD_REQUEST)
        videos = [{'title': v.get('title', '').strip(), 'url': v.get('url', '').strip(), 'levels': parse_levels(v.get('levels')), 'tags': with_platform_tag(v.get('url', '').strip(), parse_tags(v.get('tags')))}
                  for v in request.data]
        if any(len(v['levels']) > 1 for v in videos):
            return Response({'detail': '每个视频只能选择一个阶段'}, status=status.HTTP_400_BAD_REQUEST)
        seen = set()
        for v in videos:
            key = video_key(v['url'])
            if key in seen:
                return Response({'detail': f'列表中有重复视频：「{v["title"]}」'}, status=status.HTTP_409_CONFLICT)
            seen.add(key)
        filepath = _subject_filepath(subject)
        _write_videos(filepath, videos)
        return Response(_read_videos(filepath))


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
            url = request.data['url'].strip()
            dup = _find_duplicate(videos, url, skip=real_index)
            if dup:
                return Response({'detail': f'该视频已存在：「{dup["title"]}」'}, status=status.HTTP_409_CONFLICT)
            videos[real_index]['url'] = url
        if 'levels' in request.data:
            levels = parse_levels(request.data['levels'])
            if len(levels) > 1:
                return Response({'detail': '每个视频只能选择一个阶段'}, status=status.HTTP_400_BAD_REQUEST)
            videos[real_index]['levels'] = levels
        if 'tags' in request.data:
            videos[real_index]['tags'] = parse_tags(request.data['tags'])
        # 链接改了平台也要跟着变：先去掉旧平台标签，再按新链接补上
        videos[real_index]['tags'] = with_platform_tag(
            videos[real_index]['url'], [t for t in videos[real_index].get('tags', []) if t not in ('B站', 'YouTube')])
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


