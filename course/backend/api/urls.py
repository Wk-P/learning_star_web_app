from django.urls import path
from .views.auth_views import UserMeView
from .views.course_views import SubjectListView, SubjectVideosView, RoadmapView
from .views.admin_views import (
    AdminSubjectListView, AdminSubjectDetailView,
    AdminSubjectVideosView, AdminSubjectVideoDetailView,
    AdminRoadmapView,
)

urlpatterns = [
    # ── 用户自身（账号、密码统一在 topik 后端维护） ───────────────────────────
    path('users/me/', UserMeView.as_view()),

    # ── 科目（学生只读） ──────────────────────────────────────────────────────
    path('subjects/', SubjectListView.as_view()),
    path('subjects/<int:subject_id>/videos/', SubjectVideosView.as_view()),

    # ── 学习路线图（已登录用户只读） ─────────────────────────────────────────
    path('roadmap/', RoadmapView.as_view()),

    # ── Admin：科目 + 视频管理 ────────────────────────────────────────────────
    path('admin/subjects/', AdminSubjectListView.as_view()),
    path('admin/subjects/<int:subject_id>/', AdminSubjectDetailView.as_view()),
    path('admin/subjects/<int:subject_id>/videos/', AdminSubjectVideosView.as_view()),
    path('admin/subjects/<int:subject_id>/videos/<int:index>/', AdminSubjectVideoDetailView.as_view()),

    # ── Admin：路线图管理 ─────────────────────────────────────────────────────
    path('admin/roadmap/', AdminRoadmapView.as_view()),
]
