from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .services import get_pdf, get_pdf_list


class PdfListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        data = get_pdf_list(user=request.user)
        return Response(data=data, status=status.HTTP_200_OK)


class PdfDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        pk = request.query_params.get('id')
        data = get_pdf(pk=pk)
        if data:
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data=None, status=status.HTTP_404_NOT_FOUND)
