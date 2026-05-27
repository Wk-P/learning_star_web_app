from pathlib import Path
from django.conf import settings

from backend.utils import natural_key
from .models import Video
from .serializers import VideoSerializer


def get_video_list(user=None) -> list[dict]:
    """
    Scan VIDEO_ROOT for .m3u8 files.

    Expected layout:
        VIDEO_ROOT/
        └── {folder...}/
            └── {video_name}/       ← named folder = video title
                ├── playlist.m3u8
                └── *.ts
    """
    root = Path(settings.VIDEO_ROOT)
    if not root.exists():
        return []

    folders_map: dict[tuple, list] = {}

    for m3u8 in sorted(root.rglob('*.m3u8')):
        rel   = m3u8.relative_to(root)
        parts = rel.parts          # e.g. ('分类1', '分类2', '课程名', 'playlist.m3u8')

        if len(parts) == 1:
            # m3u8 sits directly in VIDEO_ROOT (no named subfolder)
            folder_key = ()
            title = m3u8.stem
        else:
            # parts[-1] = filename, parts[-2] = video folder (title)
            folder_key = parts[:-2]
            title      = parts[-2]

        url = settings.MEDIA_URL + 'videos/' + '/'.join(rel.parts)

        if folder_key not in folders_map:
            folders_map[folder_key] = []
        folders_map[folder_key].append({
            'id':    abs(hash(str(m3u8))) % (2 ** 31),
            'title': title,
            'url':   url,
        })

    result = []
    for i, (key, videos) in enumerate(sorted(folders_map.items(), key=lambda x: [natural_key(p) for p in x[0]])):
        result.append({
            'id':     i + 1,
            'path':   list(key),
            'videos': sorted(videos, key=lambda v: natural_key(v['title'])),
        })

    if user is None or user.is_staff:
        return result

    from permission.models import MediaPermission
    allowed = set(
        MediaPermission.objects.filter(user=user, media_type='video')
        .values_list('root_dir', flat=True)
    )
    return [f for f in result if _path_allowed(f['path'], allowed)]


def _path_allowed(path: list, allowed: set) -> bool:
    for ap in allowed:
        parts = ap.split('/')
        if path[:len(parts)] == parts:
            return True
    return False


def get_video(pk: int):
    try:
        return VideoSerializer(Video.objects.get(id=pk)).data
    except Video.DoesNotExist:
        return None
