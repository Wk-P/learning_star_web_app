import os
import re
from urllib.parse import parse_qs, urlparse

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
    """接受列表或逗号分隔字符串，只保留合法等级并按 入门→基础→进阶 排序。每个视频只允许一个阶段，写入时由 admin 校验。"""
    if isinstance(raw, str):
        raw = raw.replace('，', ',').split(',')
    picked = {str(x).strip() for x in (raw or [])}
    return [lv for lv in LEVELS if lv in picked]


def parse_tags(raw) -> list[str]:
    """自定义标签：列表或逗号分隔字符串，去空、去重、保持顺序；| 与逗号是文件分隔符，不允许出现在标签里。"""
    if isinstance(raw, str):
        raw = re.split(r'[,，、]', raw)
    tags = []
    for x in raw or []:
        t = str(x).replace('|', '').replace(',', '').replace('，', '').strip()[:20]
        if t and t not in tags:
            tags.append(t)
    return tags


# 视频链接解析：识别平台并提取视频 ID。规则与前端 web/src/course/videoLink.ts 保持一致；新增平台两边各加一条
BILI_HOST = re.compile(r'(^|\.)(bilibili\.com|b23\.tv|bili2233\.cn)$')
YT_HOST = re.compile(r'(^|\.)(youtube\.com|youtu\.be|youtube-nocookie\.com)$')
PLATFORM_LABELS = {'bilibili': 'B站', 'youtube': 'YouTube'}


def parse_video_link(url: str) -> tuple[str, str]:
    """返回 (platform, id)；platform 为 bilibili / youtube / other，识别不出 ID 时 id 为空。"""
    u = urlparse(re.sub(r'^http://', 'https://', url.strip(), flags=re.I))
    host = (u.hostname or '').lower()
    if BILI_HOST.search(host):
        m = re.search(r'BV[0-9A-Za-z]{10}', url)
        return 'bilibili', m.group(0) if m else ''
    if YT_HOST.search(host):
        vid = (u.path[1:12] if host.endswith('youtu.be') else '') \
            or (parse_qs(u.query).get('v') or [''])[0]
        if not vid:
            m = re.match(r'^/(?:shorts|embed|live|v)/([\w-]{11})', u.path)
            vid = m.group(1) if m else ''
        return 'youtube', vid if re.fullmatch(r'[\w-]{11}', vid) else ''
    return 'other', ''


def platform_tag(url: str) -> str | None:
    return PLATFORM_LABELS.get(parse_video_link(url)[0])


def with_platform_tag(url: str, tags: list[str]) -> list[str]:
    """平台标签放在最前；已有则不重复，换了平台时去掉旧的。"""
    t = platform_tag(url)
    rest = [x for x in tags if x not in PLATFORM_LABELS.values()]
    return [t, *rest] if t else rest


def video_key(url: str) -> str:
    """查重键：能识别出视频 ID 的按「平台:ID」（同一 BV 的不同分P也算重复），否则按去掉协议与参数的链接。"""
    platform, vid = parse_video_link(url)
    if vid:
        return f'{platform}:{vid}'
    return re.sub(r'^https?://', '', url.strip().split('?')[0].split('#')[0], flags=re.I).rstrip('/').lower()


def _read_videos(filepath: str) -> list[dict]:
    """每行：「标题 https://... |入门 |标签1,标签2」，等级与标签后缀均可省略。"""
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
                videos.append({'index': i, 'title': line, 'url': '', 'levels': [], 'tags': []})
                continue
            title = line[:idx].strip()
            # 链接本身不含空格：其后若有「 |等级」即为元数据
            url, _, meta = line[idx:].strip().partition(' ')
            # meta 形如「|入门 |标签1,标签2」：第一段为等级，第二段为标签
            parts = meta.split('|')[1:]
            videos.append({
                'index': i, 'title': title, 'url': url,
                'levels': parse_levels(parts[0]) if parts else [],
                'tags': with_platform_tag(url, parse_tags(parts[1]) if len(parts) > 1 else []),
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

