from rest_framework.serializers import ModelSerializer
from .models import Video, VideoFolder


class VideoFolderSerializer(ModelSerializer):
    class Meta:
        model = VideoFolder
        fields = '__all__'


class VideoSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'url']