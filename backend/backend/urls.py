from django.urls import path, include
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView

from user.serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from permission.views import ProtectedMediaView


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    path('api/user/', include('user.urls')),
    path('api/video/', include('video.urls')),
    path('api/audio/', include('audio.urls')),
    path('api/pdf/', include('pdf.urls')),
    path('api/permission/', include('permission.urls')),

    path('api/auth/token/', CustomTokenObtainPairView.as_view()),
    path('api/auth/token/refresh/', TokenRefreshView.as_view()),

    path('media/<path:filepath>', ProtectedMediaView.as_view()),
]
