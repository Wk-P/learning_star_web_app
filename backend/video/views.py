from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .services import get_video, get_video_list


class VideoListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        data = get_video_list()
        return Response(data=data, status=status.HTTP_200_OK)


class VideoDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        pk = request.query_params.get('id')
        data = get_video(pk=pk)
        return Response(data=data, status=status.HTTP_200_OK)
