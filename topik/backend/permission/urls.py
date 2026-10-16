from django.urls import path
from .views import MediaRootsView, MediaTreeView, UserPermissionsView

urlpatterns = [
    path('roots/', MediaRootsView.as_view()),
    path('tree/',  MediaTreeView.as_view()),
    path('users/<int:user_id>/', UserPermissionsView.as_view()),
]
