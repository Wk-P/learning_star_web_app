import os

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Subject
from ..serializers import SubjectSerializer

BILIBILI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bilibili')


def _subject_filepath(subject: Subject) -> str:
    slug = subject.name.lower().replace(' ', '_')
    return os.path.join(BILIBILI_DIR, f'{slug}.txt')


def _read_videos(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    videos = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            idx = line.find(' http')
            if idx != -1:
                title = line[:idx].strip()
                url = line[idx:].strip()
            else:
                title = line
                url = ''
            videos.append({'index': i, 'title': title, 'url': url})
    return videos


class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all().order_by('id')
        return Response(SubjectSerializer(subjects, many=True).data)


class SubjectVideosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(_read_videos(_subject_filepath(subject)))
