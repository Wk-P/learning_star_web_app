"""视频链接的解析与规范化：平台识别、查重键、阶段、标签。

平台规则与前端 web/src/course/videoLink.ts 保持一致；新增平台两边各加一条。
"""
import re
from urllib.parse import parse_qs, urlparse

LEVELS = ('入门', '基础', '进阶')

BILI_HOST = re.compile(r'(^|\.)(bilibili\.com|b23\.tv|bili2233\.cn)$')
YT_HOST = re.compile(r'(^|\.)(youtube\.com|youtu\.be|youtube-nocookie\.com)$')
PLATFORM_LABELS = {'bilibili': 'B站', 'youtube': 'YouTube'}


def parse_levels(raw) -> list[str]:
    """列表或逗号分隔字符串 → 合法阶段，按 入门→基础→进阶 排序。"""
    if isinstance(raw, str):
        raw = raw.replace('，', ',').split(',')
    picked = {str(x).strip() for x in (raw or [])}
    return [lv for lv in LEVELS if lv in picked]


def parse_tags(raw) -> list[str]:
    """自定义标签：去空、去重、保持顺序，单个最长 20 字。"""
    if isinstance(raw, str):
        raw = re.split(r'[,，、]', raw)
    tags = []
    for x in raw or []:
        t = str(x).replace('|', '').replace(',', '').replace('，', '').strip()[:20]
        if t and t not in tags:
            tags.append(t)
    return tags


def parse_video_link(url: str) -> tuple[str, str]:
    """返回 (platform, id)；platform 为 bilibili / youtube / other，识别不出 ID 时 id 为空。"""
    u = urlparse(re.sub(r'^http://', 'https://', url.strip(), flags=re.I))
    host = (u.hostname or '').lower()
    if BILI_HOST.search(host):
        m = re.search(r'BV[0-9A-Za-z]{10}', url)
        return 'bilibili', m.group(0) if m else ''
    if YT_HOST.search(host):
        vid = (u.path[1:12] if host.endswith('youtu.be') else '')             or (parse_qs(u.query).get('v') or [''])[0]
        if not vid:
            m = re.match(r'^/(?:shorts|embed|live|v)/([\w-]{11})', u.path)
            vid = m.group(1) if m else ''
        return 'youtube', vid if re.fullmatch(r'[\w-]{11}', vid) else ''
    return 'other', ''


def with_platform_tag(url: str, tags: list[str]) -> list[str]:
    """平台标签放在最前；已有则不重复，换了平台时去掉旧的。"""
    t = PLATFORM_LABELS.get(parse_video_link(url)[0])
    rest = [x for x in tags if x not in PLATFORM_LABELS.values()]
    return [t, *rest] if t else rest


def video_key(url: str) -> str:
    """查重键：能识别出视频 ID 的按「平台:ID」（同一 BV 的不同分P也算重复），否则按去掉协议与参数的链接。"""
    platform, vid = parse_video_link(url)
    if vid:
        return f'{platform}:{vid}'
    return re.sub(r'^https?://', '', url.strip().split('?')[0].split('#')[0], flags=re.I).rstrip('/').lower()[:300]


def parse_line(line: str) -> dict | None:
    """原 txt 一行：「标题 https://... |入门 |标签1,标签2」，阶段与标签后缀可省略。没有链接返回 None。"""
    line = line.strip()
    idx = line.find(' http')
    if not line or idx == -1:
        return None
    title = line[:idx].strip()
    url, _, meta = line[idx:].strip().partition(' ')
    parts = meta.split('|')[1:]
    levels = parse_levels(parts[0]) if parts else []
    return {
        'title': title, 'url': url,
        'level': levels[0] if levels else '',
        'tags': with_platform_tag(url, parse_tags(parts[1]) if len(parts) > 1 else []),
    }
