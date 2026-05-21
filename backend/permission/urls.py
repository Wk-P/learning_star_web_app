from django.urls import path
from .views import MediaRootsView, UserPermissionsView

urlpatterns = [
    path('roots/', MediaRootsView.as_view()),
    path('users/<int:user_id>/', UserPermissionsView.as_view()),
]
