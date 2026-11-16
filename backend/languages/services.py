"""扫描语言资源目录，生成「文件夹 → 条目」列表，并按用户权限过滤。

目录约定（<kind_dir> = videos / audios / files）：
    MEDIA_ROOT/languages/<slug>/videos/<目录...>/<视频名>/playlist.m3u8   ← 视频名 = m3u8 所在文件夹名
    MEDIA_ROOT/languages/<slug>/audios/<目录...>/<音频名>.mp3
    MEDIA_ROOT/languages/<slug>/files/<目录...>/<资料名>.pdf|.xlsx|.hwp|...
"""
import time
import zlib
from pathlib import Path

from django.conf import settings

from config.utils import natural_key

from .models import Language, MediaPermission

# 「资料」只提供下载，不在线预览，所以不限于 PDF
DOC_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.hwp', '.hwpx'}

# 视频目录有 20 万+ 个文件，扫描结果短暂缓存，避免每次请求都遍历磁盘
_CACHE_SECONDS = 60
_cache: dict[tuple, tuple[float, list]] = {}


def _is_doc(p: Path) -> bool:
    # 跳过隐藏文件与 Office 打开文件时生成的 ~$ 临时文件
    return p.is_file() and p.suffix.lower() in DOC_EXTENSIONS and not p.name.startswith(('.', '~$'))


def _iter_items(kind: str, root: Path):
    """产出 (所在文件夹路径 tuple, 标题, 相对 root 的文件路径 tuple, 扩展名)。"""
    if kind == 'video':
        for f in root.rglob('*.m3u8'):
            parts = f.relative_to(root).parts
            if len(parts) == 1:
                yield (), f.stem, parts, 'm3u8'
            else:
                yield parts[:-2], parts[-2], parts, 'm3u8'
    elif kind == 'audio':
        for f in root.rglob('*.mp3'):
            parts = f.relative_to(root).parts
            yield parts[:-1], f.stem, parts, 'mp3'
    else:
        for f in root.rglob('*'):
            if _is_doc(f):
                parts = f.relative_to(root).parts
                yield parts[:-1], f.stem, parts, f.suffix.lower().lstrip('.')


def scan(language: Language, kind: str) -> list[dict]:
    """全部文件夹（不过滤权限）：[{id, path: [...], items: [{id, title, url, ext}]}]"""
    key = (language.slug, kind)
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < _CACHE_SECONDS:
        return hit[1]

    root = language.media_dir(kind)
    base_url = f'{settings.MEDIA_URL}languages/{language.slug}/{root.name}/'
    folders: dict[tuple, list] = {}
    if root.exists():
        for folder, title, parts, ext in _iter_items(kind, root):
            rel = '/'.join(parts)
            folders.setdefault(folder, []).append({
                # 稳定 id：同一文件每次扫描、每个进程都相同（前端用于播放记录）
                'id': zlib.crc32(f'{language.slug}/{kind}/{rel}'.encode()),
                'title': title,
                'url': base_url + rel,
                'ext': ext,
            })

    result = [
        {'id': i + 1, 'path': list(folder), 'items': sorted(items, key=lambda x: natural_key(x['title']))}
        for i, (folder, items) in enumerate(sorted(folders.items(), key=lambda x: [natural_key(p) for p in x[0]]))
    ]
    _cache[key] = (time.monotonic(), result)
    return result


def allowed_dirs(user, language: Language, kind: str) -> set[str] | None:
    """None 表示不受限（管理员）。"""
    if user.is_staff:
        return None
    return set(MediaPermission.objects.filter(user=user, language=language, media_type=kind)
               .values_list('root_dir', flat=True))


def path_allowed(path: list[str] | tuple, allowed: set[str] | None) -> bool:
    if allowed is None:
        return True
    for ap in allowed:
        parts = ap.split('/')
        if list(path[:len(parts)]) == parts:
            return True
    return False


def list_for_user(user, language: Language, kind: str) -> list[dict]:
    allowed = allowed_dirs(user, language, kind)
    return [f for f in scan(language, kind) if path_allowed(f['path'], allowed)]


def build_tree(path_lists: list[list[str]]) -> list[dict]:
    """[['a','b'], ['a','c']] → [{path:'a', label:'a', children:[{path:'a/b',...}, ...]}]"""
    all_paths: set[tuple] = set()
    for p in path_lists:
        for i in range(1, len(p) + 1):
            all_paths.add(tuple(p[:i]))

    def level(parent: tuple) -> list[dict]:
        children = sorted((p for p in all_paths if len(p) == len(parent) + 1 and p[:-1] == parent),
                          key=lambda p: natural_key(p[-1]))
        return [{'path': '/'.join(c), 'label': c[-1], 'children': level(c)} for c in children]

    return level(())
