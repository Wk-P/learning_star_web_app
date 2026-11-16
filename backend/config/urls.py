from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import TokenView
from languages.views import ProtectedMediaView

urlpatterns = [
    path('api/auth/token/', TokenView.as_view()),
    path('api/auth/token/refresh/', TokenRefreshView.as_view()),
    path('api/accounts/', include('accounts.urls')),
    path('api/languages/', include('languages.urls')),
    path('api/courses/', include('courses.urls')),
    path('django-admin/', admin.site.urls),
    path('media/<path:filepath>', ProtectedMediaView.as_view()),
]
