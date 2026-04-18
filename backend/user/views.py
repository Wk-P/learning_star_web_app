from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from .services import get_user_list, get_user

# Create your views here.
class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: Request):
        data = get_user_list()
        return Response(data=data, status=status.HTTP_200_OK)
    


class UserDetailView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        pk = request.query_params.get('id')
        data = get_user(pk=pk)

        if data:
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        