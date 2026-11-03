import os
import re

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Subject
from ..serializers import SubjectSerializer

BILIBILI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bilibili')


def _subject_filepath(subject: Subject) -> str:
    slug = subject.name.lower().replace(' ', '_')
    return os.path.join(BILIBILI_DIR, f'{slug}.txt')


LEVELS = ('入门', '基础', '进阶')


def parse_levels(raw) -> list[str]:
    """接受列表或逗号分隔字符串，只保留合法等级并按 入门→基础→进阶 排序。"""
    if isinstance(raw, str):
        raw = raw.replace('，', ',').split(',')
    picked = {str(x).strip() for x in (raw or [])}
    return [lv for lv in LEVELS if lv in picked]


def video_key(url: str) -> str:
    """查重用：B 站只看 BV 号（同一 BV 的不同分P也算重复），其他链接去掉查询参数与协议。"""
    m = re.search(r'BV[0-9A-Za-z]{10}', url)
    if m:
        return m.group(0)
    return re.sub(r'^https?://', '', url.split('?')[0].split('#')[0]).rstrip('/').lower()


def _read_videos(filepath: str) -> list[dict]:
    """每行：「标题 https://... |入门,基础」，等级后缀可省略。"""
    if not os.path.exists(filepath):
        return []
    videos = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            idx = line.find(' http')
            if idx == -1:
                videos.append({'index': i, 'title': line, 'url': '', 'levels': []})
                continue
            title = line[:idx].strip()
            # 链接本身不含空格：其后若有「 |等级」即为元数据
            url, _, meta = line[idx:].strip().partition(' ')
            lv = re.search(r'\|(.*)$', meta)
            videos.append({
                'index': i, 'title': title, 'url': url,
                'levels': parse_levels(lv.group(1)) if lv else [],
            })
    return videos


class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all().order_by('id')
        return Response(SubjectSerializer(subjects, many=True).data)


class SubjectVideosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(_read_videos(_subject_filepath(subject)))

