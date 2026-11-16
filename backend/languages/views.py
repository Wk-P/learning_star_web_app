import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.http import HttpResponse, StreamingHttpResponse
from django.views import View
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .models import MEDIA_KINDS, Language, LanguageCategory
from .services import list_for_user

User = get_user_model()
KIND_BY_DIR = {v: k for k, v in MEDIA_KINDS.items()}


# ── 序列化 ────────────────────────────────────────────────────────────────────

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'category', 'name', 'slug', 'native_name', 'description', 'color', 'sort_order', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageCategory
        fields = ['id', 'name', 'description', 'sort_order']


def _category_tree(include_inactive: bool) -> list[dict]:
    out = []
    for c in LanguageCategory.objects.prefetch_related('languages'):
        langs = [lg for lg in c.languages.all() if include_inactive or lg.is_active]
        out.append({**CategorySerializer(c).data, 'languages': LanguageSerializer(langs, many=True).data})
    return out


def _get_language(slug: str, user) -> Language | None:
    qs = Language.objects.all() if user.is_staff else Language.objects.filter(is_active=True)
    return qs.filter(slug=slug).first()


# ── 学习者 ────────────────────────────────────────────────────────────────────

class CategoryTreeView(APIView):
    """GET /api/languages/ — 分类 → 语言（管理员可看到未启用的语言）。"""

    def get(self, request):
        return Response(_category_tree(include_inactive=request.user.is_staff))


class LanguageMediaView(APIView):
    """GET /api/languages/<slug>/<kind>/ — 该语言的全部文件夹与条目（登录即可）。"""

    def get(self, request, slug: str, kind: str):
        if kind not in MEDIA_KINDS:
            return Response(status=status.HTTP_404_NOT_FOUND)
        language = _get_language(slug, request.user)
        if not language:
            return Response({'detail': '语言不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(list_for_user(request.user, language, kind))


# ── 管理员：分类与语言 ────────────────────────────────────────────────────────

class _CrudView(APIView):
    permission_classes = [IsAdminUser]
    model = None
    serializer = None

    def get_obj(self, pk):
        return self.model.objects.filter(pk=pk).first()


class AdminCategoryListView(_CrudView):
    def get(self, request):
        return Response(_category_tree(include_inactive=True))

    def post(self, request):
        s = CategorySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class AdminCategoryDetailView(_CrudView):
    model, serializer = LanguageCategory, CategorySerializer

    def patch(self, request, pk):
        obj = self.get_obj(pk)
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        s = CategorySerializer(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        obj = self.get_obj(pk)
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            obj.delete()
        except ProtectedError:
            return Response({'detail': '分类下还有语言，请先移走或删除'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminLanguageListView(_CrudView):
    def post(self, request):
        s = LanguageSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        lang = s.save()
        for d in MEDIA_KINDS:
            lang.media_dir(d).mkdir(parents=True, exist_ok=True)
        return Response(s.data, status=status.HTTP_201_CREATED)


class AdminLanguageDetailView(_CrudView):
    model = Language

    def patch(self, request, pk):
        obj = self.get_obj(pk)
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if 'slug' in request.data and request.data['slug'] != obj.slug:
            return Response({'detail': '标识创建后不能修改（媒体目录以它命名）'}, status=status.HTTP_400_BAD_REQUEST)
        s = LanguageSerializer(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        """只删除数据库记录与相关权限，媒体文件保留在磁盘上。"""
        obj = self.get_obj(pk)
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 受保护的媒体文件 ──────────────────────────────────────────────────────────

def _user_from_request(request):
    """令牌可以来自 Authorization 头，也可以来自 access_token cookie（<video>/<audio> 标签无法带请求头）。"""
    header = request.META.get('HTTP_AUTHORIZATION', '')
    raw = header[7:] if header.startswith('Bearer ') else request.COOKIES.get('access_token', '')
    if not raw:
        return None
    try:
        return User.objects.filter(pk=AccessToken(raw)['user_id'], is_active=True).first()
    except Exception:  # noqa: BLE001 — 令牌无效 / 过期
        return None


def _stream(path: Path, request) -> HttpResponse:
    """支持 Range（音频拖动进度需要）。"""
    size = path.stat().st_size
    ctype = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
    m = re.match(r'bytes=(\d+)-(\d*)', request.META.get('HTTP_RANGE', '').strip())
    if m:
        first = int(m.group(1))
        last = min(int(m.group(2)) if m.group(2) else size - 1, size - 1)
        if first > last:
            resp = HttpResponse(status=416)
            resp['Content-Range'] = f'bytes */{size}'
            return resp
        length = last - first + 1

        def chunks():
            with open(path, 'rb') as f:
                f.seek(first)
                left = length
                while left > 0:
                    buf = f.read(min(65536, left))
                    if not buf:
                        break
                    left -= len(buf)
                    yield buf

        resp = StreamingHttpResponse(chunks(), status=206, content_type=ctype)
        resp['Content-Range'] = f'bytes {first}-{last}/{size}'
        resp['Content-Length'] = length
    else:
        resp = StreamingHttpResponse(open(path, 'rb'), content_type=ctype)
        resp['Content-Length'] = size
    resp['Accept-Ranges'] = 'bytes'
    return resp


class ProtectedMediaView(View):
    """/media/languages/<slug>/<videos|audios|files>/<目录...>/<文件>：登录即可访问（未启用的语言仅管理员）。"""

    def get(self, request, filepath: str):
        user = _user_from_request(request)
        if user is None:
            return HttpResponse(status=401)

        parts = filepath.strip('/').split('/')
        # 排除 . / .. / 空段，防止路径穿越
        if any(p in ('', '.', '..') or '\\' in p for p in parts):
            return HttpResponse(status=404)
        if len(parts) < 5 or parts[0] != 'languages' or parts[2] not in KIND_BY_DIR:
            return HttpResponse(status=404)
        if not user.is_staff and not Language.objects.filter(slug=parts[1], is_active=True).exists():
            return HttpResponse(status=404)

        root = Path(settings.MEDIA_ROOT).resolve()
        full = (root / filepath).resolve()
        if not full.is_relative_to(root):
            return HttpResponse(status=403)
        if not full.is_file():
            return HttpResponse(status=404)
        return _stream(full, request)
