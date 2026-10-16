from rest_framework.serializers import ModelSerializer
from .models import Pdf, PdfFolder


class PdfFolderSerializer(ModelSerializer):
    class Meta:
        model = PdfFolder
        fields = '__all__'


class PdfSerializer(ModelSerializer):
    class Meta:
        model = Pdf
        fields = ['id', 'title', 'url']
