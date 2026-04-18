from rest_framework.urls import path
from .views import VideoListView, VideoDetailView, VideoStreamView

urlpatterns = [
    path('list/', VideoListView.as_view(), name='videos-list'),
    path('detail/', VideoDetailView.as_view(), name='video-detail'),
]