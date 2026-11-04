from pathlib import Path
from django.conf import settings

from backend.utils import natural_key
from .models import Pdf
from .serializers import PdfSerializer

# 「学习资料」可下载的文档类型（前端为下载链接，不在线预览，所以不限于 PDF）
DOC_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.hwp', '.hwpx'}


def _is_doc(path: Path) -> bool:
    # 跳过隐藏文件与 Office 打开文件时生成的 ~$ 临时文件
    return (path.is_file() and path.suffix.lower() in DOC_EXTENSIONS
            and not path.name.startswith(('.', '~$')))


def get_pdf_list(user=None) -> list[dict]:
    """
    Scan PDF_ROOT for document files (see DOC_EXTENSIONS).

    Expected layout:
        PDF_ROOT/
        └── {folder...}/
            └── filename.pdf     ← file itself is the item (also .xlsx/.hwp/...)
    """
    root = Path(settings.PDF_ROOT)
    if not root.exists():
        return []

    folders_map: dict[tuple, list] = {}

    for pdf in sorted(p for p in root.rglob('*') if _is_doc(p)):
        rel        = pdf.relative_to(root)
        parts      = rel.parts
        folder_key = parts[:-1]
        title      = pdf.stem
        url        = settings.MEDIA_URL + 'pdfs/' + '/'.join(parts)

        if folder_key not in folders_map:
            folders_map[folder_key] = []
        folders_map[folder_key].append({
            'id':    abs(hash(str(pdf))) % (2 ** 31),
            'title': title,
            'url':   url,
            'ext':   pdf.suffix.lower().lstrip('.'),
        })

    result = []
    for i, (key, pdfs) in enumerate(sorted(folders_map.items(), key=lambda x: [natural_key(p) for p in x[0]])):
        result.append({
            'id':   i + 1,
            'path': list(key),
            'pdfs': sorted(pdfs, key=lambda p: natural_key(p['title'])),
        })

    if user is None or user.is_staff:
        return result

    from permission.models import MediaPermission
    allowed = set(
        MediaPermission.objects.filter(user=user, media_type='pdf')
        .values_list('root_dir', flat=True)
    )
    return [f for f in result if _path_allowed(f['path'], allowed)]


def _path_allowed(path: list, allowed: set) -> bool:
    for ap in allowed:
        parts = ap.split('/')
        if path[:len(parts)] == parts:
            return True
    return False


def get_pdf(pk: int):
    try:
        return PdfSerializer(Pdf.objects.get(id=pk)).data
    except Pdf.DoesNotExist:
        return None
