from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

# 登录 / 刷新令牌统一由 topik 后端提供（见 api/authentication.py）
urlpatterns = [
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
