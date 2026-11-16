from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('me/', views.MeView.as_view()),
    path('me/password/', views.MePasswordView.as_view()),
    path('users/', views.UserListView.as_view()),
    path('users/<int:pk>/', views.UserDetailView.as_view()),
    path('users/<int:pk>/reset-password/', views.UserResetPasswordView.as_view()),
]
