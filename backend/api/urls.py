from django.urls import path
from .views.auth_views import UserMeView, ChangePasswordView, UpdateDisplayView, UpdateUsernameView
from .views.course_views import (
    SubjectListView, SubjectCoursesView, SubjectVideosView,
    CourseListView, CourseDetailView,
)
from .views.admin_views import (
    AdminSubjectListView, AdminSubjectDetailView,
    AdminSubjectVideosView, AdminSubjectVideoDetailView,
    AdminUserListView, AdminUserDetailView, AdminUserResetPasswordView,
    AdminCourseListView, AdminCourseDetailView,
)

urlpatterns = [
    # ── 用户自身 ──────────────────────────────────────────────────────────────
    path('users/me/', UserMeView.as_view()),
    path('users/me/change-password/', ChangePasswordView.as_view()),
    path('users/me/update-display/', UpdateDisplayView.as_view()),
    path('users/me/update-username/', UpdateUsernameView.as_view()),

    # ── 科目 ──────────────────────────────────────────────────────────────────
    path('subjects/', SubjectListView.as_view()),
    path('subjects/<int:subject_id>/courses/', SubjectCoursesView.as_view()),
    path('subjects/<int:subject_id>/videos/', SubjectVideosView.as_view()),

    # ── 课程 ──────────────────────────────────────────────────────────────────
    path('courses/', CourseListView.as_view()),
    path('courses/<int:course_id>/', CourseDetailView.as_view()),

    # ── Admin：用户管理 ───────────────────────────────────────────────────────
    path('admin/users/', AdminUserListView.as_view()),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view()),
    path('admin/users/<int:user_id>/reset-password/', AdminUserResetPasswordView.as_view()),

    # ── Admin：科目管理 ───────────────────────────────────────────────────────
    path('admin/subjects/', AdminSubjectListView.as_view()),
    path('admin/subjects/<int:subject_id>/', AdminSubjectDetailView.as_view()),
    path('admin/subjects/<int:subject_id>/videos/', AdminSubjectVideosView.as_view()),
    path('admin/subjects/<int:subject_id>/videos/<int:index>/', AdminSubjectVideoDetailView.as_view()),

    # ── Admin：课程管理 ───────────────────────────────────────────────────────
    path('admin/courses/', AdminCourseListView.as_view()),
    path('admin/courses/<int:course_id>/', AdminCourseDetailView.as_view()),
]
