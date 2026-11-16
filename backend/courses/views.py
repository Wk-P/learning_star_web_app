import re

from django.db import transaction
from django.db.models import Count, Max
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .links import parse_levels, parse_tags, video_key, with_platform_tag
from .models import CourseVideo, Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'icon', 'color', 'keywords']


def video_data(v: CourseVideo) -> dict:
    # levels 保持列表形式（最多一个），与原接口一致
    return {'id': v.id, 'title': v.title, 'url': v.url, 'levels': [v.level] if v.level else [], 'tags': v.tags}


def _bad(detail: str, code=status.HTTP_400_BAD_REQUEST):
    return Response({'detail': detail}, status=code)


def _one_level(raw) -> tuple[str, Response | None]:
    levels = parse_levels(raw)
    if len(levels) > 1:
        return '', _bad('每个视频只能选择一个阶段')
    return (levels[0] if levels else ''), None


def _duplicate(subject: Subject, url: str, exclude_id: int | None = None) -> CourseVideo | None:
    qs = subject.videos.filter(video_key=video_key(url))
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.first()


# ── 学习者 ────────────────────────────────────────────────────────────────────

class SubjectListView(APIView):
    def get(self, request):
        return Response(SubjectSerializer(Subject.objects.all(), many=True).data)


class SubjectVideosView(APIView):
    def get(self, request, subject_id: int):
        subject = Subject.objects.filter(pk=subject_id).first()
        if not subject:
            return _bad('科目不存在', status.HTTP_404_NOT_FOUND)
        return Response([video_data(v) for v in subject.videos.all()])


# ── 管理员 ────────────────────────────────────────────────────────────────────

class AdminSubjectListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        subjects = Subject.objects.annotate(video_count=Count('videos'))
        return Response([{**SubjectSerializer(s).data, 'video_count': s.video_count} for s in subjects])

    def post(self, request):
        s = SubjectSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class AdminSubjectDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, subject_id: int):
        obj = Subject.objects.filter(pk=subject_id).first()
        return Response(SubjectSerializer(obj).data) if obj else _bad('科目不存在', status.HTTP_404_NOT_FOUND)

    def patch(self, request, subject_id: int):
        obj = Subject.objects.filter(pk=subject_id).first()
        if not obj:
            return _bad('科目不存在', status.HTTP_404_NOT_FOUND)
        s = SubjectSerializer(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, subject_id: int):
        obj = Subject.objects.filter(pk=subject_id).first()
        if not obj:
            return _bad('科目不存在', status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminSubjectVideosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, subject_id: int):
        subject = Subject.objects.filter(pk=subject_id).first()
        if not subject:
            return _bad('科目不存在', status.HTTP_404_NOT_FOUND)
        return Response([video_data(v) for v in subject.videos.all()])

    @transaction.atomic
    def post(self, request, subject_id: int):
        """追加一条。body: {line: "标题 https://...", levels: [...], tags: [...]}"""
        subject = Subject.objects.filter(pk=subject_id).first()
        if not subject:
            return _bad('科目不存在', status.HTTP_404_NOT_FOUND)
        line = str(request.data.get('line') or '').strip()
        m = re.search(r'https?://\S+', line)
        if not m:
            return _bad('格式错误，找不到链接（应包含 http）')
        url = m.group(0)
        title = line[:m.start()].strip().replace('|', '/')
        if not title:
            return _bad('缺少标题：请在链接前面写上视频标题，用空格隔开')
        dup = _duplicate(subject, url)
        if dup:
            return _bad(f'该视频已存在：「{dup.title}」', status.HTTP_409_CONFLICT)
        level, err = _one_level(request.data.get('levels'))
        if err:
            return err
        last = subject.videos.aggregate(m=Max('sort_order'))['m'] or 0
        v = CourseVideo.objects.create(
            subject=subject, title=title, url=url, level=level, sort_order=last + 1,
            tags=with_platform_tag(url, parse_tags(request.data.get('tags'))), video_key=video_key(url),
        )
        return Response(video_data(v), status=status.HTTP_201_CREATED)


class AdminSubjectVideoDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get(self, subject_id: int, video_id: int):
        return CourseVideo.objects.filter(subject_id=subject_id, pk=video_id).select_related('subject').first()

    def patch(self, request, subject_id: int, video_id: int):
        v = self._get(subject_id, video_id)
        if not v:
            return _bad('视频不存在', status.HTTP_404_NOT_FOUND)
        if 'title' in request.data:
            title = str(request.data['title']).strip()
            if not title:
                return _bad('标题不能为空')
            v.title = title
        if 'url' in request.data:
            url = str(request.data['url']).strip()
            dup = _duplicate(v.subject, url, exclude_id=v.id)
            if dup:
                return _bad(f'该视频已存在：「{dup.title}」', status.HTTP_409_CONFLICT)
            v.url, v.video_key = url, video_key(url)
        if 'levels' in request.data:
            level, err = _one_level(request.data['levels'])
            if err:
                return err
            v.level = level
        if 'tags' in request.data:
            v.tags = parse_tags(request.data['tags'])
        # 链接换了平台，平台标签也跟着换
        v.tags = with_platform_tag(v.url, v.tags)
        v.save()
        return Response(video_data(v))

    def delete(self, request, subject_id: int, video_id: int):
        v = self._get(subject_id, video_id)
        if not v:
            return _bad('视频不存在', status.HTTP_404_NOT_FOUND)
        v.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
