from rest_framework.urls import path
from .views import PdfListView, PdfDetailView

urlpatterns = [
    path('list/', PdfListView.as_view(), name='pdf-list'),
    path('detail/', PdfDetailView.as_view(), name='pdf-detail'),
]
