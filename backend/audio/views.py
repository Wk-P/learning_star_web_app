from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .services import get_audio, get_audio_list

# Create your views here.


class AudioListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        data = get_audio_list(user=request.user)
        return Response(data=data, status=status.HTTP_200_OK)
    

class AudioDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        pk = request.query_params.get('id')
        data = get_audio(pk=pk)

        return Response(data=data, status=status.HTTP_200_OK)
