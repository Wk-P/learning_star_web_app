import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse, Http404
from django.views import View
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from .models import MediaPermission

User = get_user_model()

FOLDER_TO_TYPE = {'videos': 'video', 'audios': 'audio', 'pdfs': 'pdf'}

# ─────────────────────────────────────────────────────────────
# Auth helper: validate JWT from header OR cookie
# ─────────────────────────────────────────────────────────────

def _authenticate_request(request) -> 'User | None':
    token_str = ''

    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token_str = auth_header[7:]
    else:
        token_str = request.COOKIES.get('access_token', '')

    if not token_str:
        return None
    try:
        token = AccessToken(token_str)
        return User.objects.get(id=token['user_id'])
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Protected media file server
# ─────────────────────────────────────────────────────────────

def _stream_file(path: Path, request) -> HttpResponse:
    """Stream a file with Range request support (needed for audio seeking)."""
    file_size = path.stat().st_size
    content_type, _ = mimetypes.guess_type(str(path))
    content_type = content_type or 'application/octet-stream'

    range_header = request.META.get('HTTP_RANGE', '').strip()
    if range_header:
        m = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if m:
            first = int(m.group(1))
            last = int(m.group(2)) if m.group(2) else file_size - 1
            last = min(last, file_size - 1)
            length = last - first + 1

            def iterator():
                with open(path, 'rb') as f:
                    f.seek(first)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(8192, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            resp = StreamingHttpResponse(iterator(), status=206, content_type=content_type)
            resp['Content-Range'] = f'bytes {first}-{last}/{file_size}'
            resp['Content-Length'] = length
            resp['Accept-Ranges'] = 'bytes'
            return resp

    resp = StreamingHttpResponse(open(path, 'rb'), content_type=content_type)
    resp['Content-Length'] = file_size
    resp['Accept-Ranges'] = 'bytes'
    return resp


class ProtectedMediaView(View):
    """Replaces Django static media serving — checks auth + per-directory permission."""

    def get(self, request, filepath: str):
        # ── 1. authenticate ──────────────────────────
        user = _authenticate_request(request)
        if user is None:
            return HttpResponse(status=401)

        # ── 2. parse path ─────────────────────────────
        parts = filepath.strip('/').split('/')
        if len(parts) < 2:
            return HttpResponse(status=404)

        media_folder = parts[0]          # 'videos' | 'audios' | 'pdfs'
        root_dir     = parts[1]          # top-level directory name
        media_type   = FOLDER_TO_TYPE.get(media_folder)

        if not media_type:
            return HttpResponse(status=404)

        # ── 3. permission check ────────────────────────
        if not user.is_staff:
            has_perm = MediaPermission.objects.filter(
                user=user,
                media_type=media_type,
                root_dir=root_dir,
            ).exists()
            if not has_perm:
                return HttpResponse(status=403)

        # ── 4. path traversal guard ───────────────────
        media_root = Path(settings.MEDIA_ROOT).resolve()
        full_path  = (media_root / filepath).resolve()
        try:
            full_path.relative_to(media_root)
        except ValueError:
            return HttpResponse(status=403)

        if not full_path.exists() or not full_path.is_file():
            return HttpResponse(status=404)

        return _stream_file(full_path, request)


# ─────────────────────────────────────────────────────────────
# Admin: available filesystem root dirs per media type
# ─────────────────────────────────────────────────────────────

def _scan_roots() -> dict:
    roots = {}
    for folder, mt in FOLDER_TO_TYPE.items():
        root = Path(getattr(settings, folder.upper()[:-1] + '_ROOT',
                            settings.MEDIA_ROOT / folder))
        if root.exists():
            roots[mt] = sorted(
                p.name for p in root.iterdir() if p.is_dir()
            )
        else:
            roots[mt] = []
    return roots


class MediaRootsView(APIView):
    """GET /api/permission/roots/ — list available top-level dirs per media type."""
    permission_classes = [IsAdminUser]

    def get(self, request: Request):
        return Response(_scan_roots())


# ─────────────────────────────────────────────────────────────
# Admin: get / replace a user's full permission set
# ─────────────────────────────────────────────────────────────

class UserPermissionsView(APIView):
    """
    GET  /api/permission/users/<user_id>/  → {video:[...], audio:[...], pdf:[...]}
    PUT  /api/permission/users/<user_id>/  → replace all permissions
    """
    permission_classes = [IsAdminUser]

    def _get_perms(self, user_id: int) -> dict:
        qs = MediaPermission.objects.filter(user_id=user_id)
        result: dict = {'video': [], 'audio': [], 'pdf': []}
        for p in qs:
            result[p.media_type].append(p.root_dir)
        return result

    def get(self, request: Request, user_id: int):
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(self._get_perms(user_id))

    def put(self, request: Request, user_id: int):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data  # {video:[...], audio:[...], pdf:[...]}

        # delete all existing and recreate
        MediaPermission.objects.filter(user=user).delete()
        to_create = []
        for mt in ('video', 'audio', 'pdf'):
            for root_dir in data.get(mt, []):
                if isinstance(root_dir, str) and root_dir.strip():
                    to_create.append(
                        MediaPermission(user=user, media_type=mt, root_dir=root_dir.strip())
                    )
        MediaPermission.objects.bulk_create(to_create)

        return Response(self._get_perms(user_id))
