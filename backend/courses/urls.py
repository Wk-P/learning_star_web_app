from django.urls import path

from . import views

urlpatterns = [
    path('subjects/', views.SubjectListView.as_view()),
    path('subjects/<int:subject_id>/videos/', views.SubjectVideosView.as_view()),
    path('admin/subjects/', views.AdminSubjectListView.as_view()),
    path('admin/subjects/<int:subject_id>/', views.AdminSubjectDetailView.as_view()),
    path('admin/subjects/<int:subject_id>/videos/', views.AdminSubjectVideosView.as_view()),
    path('admin/subjects/<int:subject_id>/videos/<int:video_id>/', views.AdminSubjectVideoDetailView.as_view()),
]
