from pathlib import Path
from django.conf import settings

from backend.utils import natural_key
from .models import Audio
from .serializers import AudioSerializer


def get_audio_list(user=None) -> list[dict]:
    """
    Scan AUDIO_ROOT for .mp3 files.

    Expected layout:
        AUDIO_ROOT/
        └── {folder...}/
            └── filename.mp3     ← file itself is the audio item
    """
    root = Path(settings.AUDIO_ROOT)
    if not root.exists():
        return []

    folders_map: dict[tuple, list] = {}

    for mp3 in sorted(root.rglob('*.mp3')):
        rel        = mp3.relative_to(root)
        parts      = rel.parts          # e.g. ('分类1', '分类2', 'file.mp3')
        folder_key = parts[:-1]         # all dirs above the file
        title      = mp3.stem           # filename without extension
        url        = settings.MEDIA_URL + 'audios/' + '/'.join(parts)

        if folder_key not in folders_map:
            folders_map[folder_key] = []
        folders_map[folder_key].append({
            'id':    abs(hash(str(mp3))) % (2 ** 31),
            'title': title,
            'url':   url,
        })

    result = []
    for i, (key, audios) in enumerate(sorted(folders_map.items(), key=lambda x: [natural_key(p) for p in x[0]])):
        result.append({
            'id':     i + 1,
            'path':   list(key),
            'audios': sorted(audios, key=lambda a: natural_key(a['title'])),
        })

    if user is None or user.is_staff:
        return result

    from permission.models import MediaPermission
    allowed = set(
        MediaPermission.objects.filter(user=user, media_type='audio')
        .values_list('root_dir', flat=True)
    )
    return [f for f in result if _path_allowed(f['path'], allowed)]


def _path_allowed(path: list, allowed: set) -> bool:
    for ap in allowed:
        parts = ap.split('/')
        if path[:len(parts)] == parts:
            return True
    return False


def get_audio(pk: int):
    try:
        return AudioSerializer(Audio.objects.get(id=pk)).data
    except Audio.DoesNotExist:
        return None
