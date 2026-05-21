from django.urls import path
from .views import UserListView, UserDetailView, UserCreateView, UserDeleteView, UserRegisterView

urlpatterns = [
    path('', UserListView.as_view()),
    path('detail/', UserDetailView.as_view()),
    path('create/', UserCreateView.as_view()),
    path('<int:pk>/delete/', UserDeleteView.as_view()),
    path('register/', UserRegisterView.as_view()),
]
