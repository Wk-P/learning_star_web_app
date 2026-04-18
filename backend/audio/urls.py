from rest_framework.urls import path
from .views import AudioListView, AudioDetailView

urlpatterns = [
    path('list/', AudioListView.as_view(), name='videos-list'),
    path('detail/', AudioDetailView.as_view(), name='video-detail')
]