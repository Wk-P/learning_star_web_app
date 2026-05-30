from django.urls import path
from .views.auth_views import UserMeView, ChangePasswordView, UpdateDisplayView, UpdateUsernameView
from .views.course_views import (
    SubjectListView, SubjectCoursesView,
    CourseListView, CourseDetailView, CourseEnrollView,
    MyEnrollmentsView, MyScoresView,
    ClassListView, ClassDetailView,
    HomeworkByCourseView, MyHomeworkListView, HomeworkDetailView,
    MyHomeworkSubmissionView, SubmitHomeworkView,
)
from .views.admin_views import (
    AdminSubjectListView, AdminSubjectDetailView,
    AdminCourseGenerateClassesView,
    AdminUserListView, AdminUserDetailView, AdminUserResetPasswordView,
    AdminUserEnrollmentListView, AdminUserEnrollmentDetailView,
    AdminUserHomeworkListView, AdminUserHomeworkDetailView,
    AdminCourseListView, AdminCourseDetailView,
    AdminAttendanceView,
    AdminCourseFileView, AdminCourseFileDeleteView,
    AdminClassFileView, AdminClassFileDeleteView,
    AdminClassListView, AdminClassDetailView,
    AdminHomeworkListView, AdminHomeworkDetailView,
    AdminHomeworkSubmissionsView, AdminGradeSubmissionView,
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

    # ── 课程 ──────────────────────────────────────────────────────────────────
    path('courses/', CourseListView.as_view()),
    path('courses/my-enrollments/', MyEnrollmentsView.as_view()),
    path('courses/my-scores/', MyScoresView.as_view()),
    path('courses/<int:course_id>/', CourseDetailView.as_view()),
    path('courses/<int:course_id>/enroll/', CourseEnrollView.as_view()),
    path('courses/<int:course_id>/classes/', ClassListView.as_view()),
    path('courses/<int:course_id>/classes/<int:class_id>/', ClassDetailView.as_view()),
    path('courses/<int:course_id>/homework/', HomeworkByCourseView.as_view()),

    # ── 作业 ──────────────────────────────────────────────────────────────────
    path('homework/my-list/', MyHomeworkListView.as_view()),
    path('homework/<int:homework_id>/', HomeworkDetailView.as_view()),
    path('homework/<int:homework_id>/my-submission/', MyHomeworkSubmissionView.as_view()),
    path('homework/<int:homework_id>/submit/', SubmitHomeworkView.as_view()),

    # ── Admin：用户管理 ───────────────────────────────────────────────────────
    path('admin/users/', AdminUserListView.as_view()),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view()),
    path('admin/users/<int:user_id>/reset-password/', AdminUserResetPasswordView.as_view()),
    path('admin/users/<int:user_id>/enrollments/', AdminUserEnrollmentListView.as_view()),
    path('admin/users/<int:user_id>/enrollments/<int:course_id>/', AdminUserEnrollmentDetailView.as_view()),
    path('admin/users/<int:user_id>/homework/', AdminUserHomeworkListView.as_view()),
    path('admin/users/<int:user_id>/homework/<int:homework_id>/', AdminUserHomeworkDetailView.as_view()),

    # ── Admin：科目管理 ───────────────────────────────────────────────────────
    path('admin/subjects/', AdminSubjectListView.as_view()),
    path('admin/subjects/<int:subject_id>/', AdminSubjectDetailView.as_view()),

    # ── Admin：课程管理 ───────────────────────────────────────────────────────
    path('admin/courses/', AdminCourseListView.as_view()),
    path('admin/courses/<int:course_id>/', AdminCourseDetailView.as_view()),
    path('admin/courses/<int:course_id>/classes/', AdminClassListView.as_view()),
    path('admin/courses/<int:course_id>/classes/generate/', AdminCourseGenerateClassesView.as_view()),
    path('admin/courses/<int:course_id>/classes/<int:class_id>/', AdminClassDetailView.as_view()),
    path('admin/courses/<int:course_id>/classes/<int:class_id>/attendance/', AdminAttendanceView.as_view()),
    path('admin/courses/<int:course_id>/classes/<int:class_id>/files/', AdminClassFileView.as_view()),
    path('admin/courses/<int:course_id>/classes/<int:class_id>/files/<int:file_id>/', AdminClassFileDeleteView.as_view()),
    path('admin/courses/<int:course_id>/files/', AdminCourseFileView.as_view()),
    path('admin/courses/<int:course_id>/files/<int:file_id>/', AdminCourseFileDeleteView.as_view()),

    # ── Admin：作业管理 ───────────────────────────────────────────────────────
    path('admin/homework/', AdminHomeworkListView.as_view()),
    path('admin/homework/<int:homework_id>/', AdminHomeworkDetailView.as_view()),
    path('admin/homework/<int:homework_id>/submissions/', AdminHomeworkSubmissionsView.as_view()),
    path('admin/homework/<int:homework_id>/submissions/<int:submission_id>/grade/', AdminGradeSubmissionView.as_view()),
]
