from rest_framework.serializers import ModelSerializer
from .models import Audio, AudioFolder


class AudioFolderSerializer(ModelSerializer):
    class Meta:
        model = AudioFolder
        fields = '__all__'


class AudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = ['id', 'url', 'title']