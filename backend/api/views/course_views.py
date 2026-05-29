from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Subject, Course, ClassSession, Homework, Enrollment, HomeworkSubmission
from ..serializers import (
    SubjectSerializer,
    CourseSerializer,
    ClassSessionSerializer,
    HomeworkSerializer,
    EnrollmentRecordSerializer,
    HomeworkSubmissionSerializer,
    CourseScoreSerializer,
)

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


# ── 科目 ──────────────────────────────────────────────────────────────────────

class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all().order_by('id')
        return Response(SubjectSerializer(subjects, many=True).data)


class SubjectCoursesView(APIView):
    """返回某个科目下的所有课程（含用户申请状态）"""
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        courses = Course.objects.filter(subject_id=subject_id).select_related('subject')
        return Response(CourseSerializer(courses, many=True, context={'request': request}).data)


# ── 课程 ──────────────────────────────────────────────────────────────────────

class CourseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.all()
        return Response(CourseSerializer(courses, many=True, context={'request': request}).data)


class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CourseSerializer(course, context={'request': request}).data)


class CourseEnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)

        if course.status == 'ended':
            return Response({'detail': '课程已结束，不可申请'}, status=status.HTTP_400_BAD_REQUEST)

        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        if not created:
            return Response({'detail': '已申请该课程'}, status=status.HTTP_409_CONFLICT)

        return Response(EnrollmentRecordSerializer(enrollment, context={'request': request}).data, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = (
            Enrollment.objects.filter(user=request.user)
            .select_related('course')
        )
        return Response(EnrollmentRecordSerializer(enrollments, many=True, context={'request': request}).data)


class MyScoresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = (
            Enrollment.objects.filter(user=request.user)
            .select_related('course')
        )
        result = []
        for enrollment in enrollments:
            course = enrollment.course
            submissions = HomeworkSubmission.objects.filter(
                user=request.user,
                homework__course=course,
                graded=True,
            )
            scores = [s.score for s in submissions if s.score is not None]
            final_score = round(sum(scores) / len(scores), 1) if scores else None
            result.append({
                'courseId': course.id,
                'courseName': course.name,
                'courseStatus': course.status,
                'finalScore': final_score,
                'graded': bool(scores),
            })
        return Response(result)


# ── 课节 ──────────────────────────────────────────────────────────────────────

class ClassListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        sessions = (
            ClassSession.objects.filter(course_id=course_id)
            .select_related('teacher')
            .prefetch_related('files')
        )
        return Response(ClassSessionSerializer(sessions, many=True, context={'request': request}).data)


class ClassDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id, class_id):
        try:
            session = (
                ClassSession.objects.select_related('teacher')
                .prefetch_related('files')
                .get(pk=class_id, course_id=course_id)
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClassSessionSerializer(session, context={'request': request}).data)


# ── 作业 ──────────────────────────────────────────────────────────────────────

class HomeworkByCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        homework = Homework.objects.filter(course_id=course_id).select_related('course')
        return Response(HomeworkSerializer(homework, many=True, context={'request': request}).data)


class MyHomeworkListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrolled_course_ids = list(
            Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
        )
        all_hw = Homework.objects.filter(course_id__in=enrolled_course_ids).select_related('course')
        result = [h for h in all_hw if h.status != 'not_started']
        return Response(HomeworkSerializer(result, many=True, context={'request': request}).data)


class HomeworkDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, homework_id):
        try:
            hw = Homework.objects.select_related('course').get(pk=homework_id)
        except Homework.DoesNotExist:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 未申请的用户无法访问
        if not Enrollment.objects.filter(user=request.user, course=hw.course).exists():
            return Response({'detail': '未申请该课程'}, status=status.HTTP_403_FORBIDDEN)
        return Response(HomeworkSerializer(hw, context={'request': request}).data)


class MyHomeworkSubmissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, homework_id):
        try:
            submission = HomeworkSubmission.objects.get(homework_id=homework_id, user=request.user)
        except HomeworkSubmission.DoesNotExist:
            return Response({'detail': '暂无提交记录'}, status=status.HTTP_404_NOT_FOUND)
        return Response(HomeworkSubmissionSerializer(submission, context={'request': request}).data)


class SubmitHomeworkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, homework_id):
        try:
            hw = Homework.objects.select_related('course').get(pk=homework_id)
        except Homework.DoesNotExist:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not Enrollment.objects.filter(user=request.user, course=hw.course).exists():
            return Response({'detail': '未申请该课程'}, status=status.HTTP_403_FORBIDDEN)

        if hw.status != 'in_progress':
            return Response({'detail': '不在提交期限内'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        if uploaded.size > MAX_UPLOAD_BYTES:
            return Response({'detail': '文件不能超过 50MB'}, status=status.HTTP_400_BAD_REQUEST)

        submission, created = HomeworkSubmission.objects.get_or_create(
            homework=hw, user=request.user,
            defaults={'file': uploaded, 'file_name': uploaded.name},
        )
        if not created:
            # 重新提交：替换文件，重置评分
            submission.file = uploaded
            submission.file_name = uploaded.name
            submission.submitted_at = timezone.now()
            submission.score = None
            submission.graded = False
            submission.save()

        return Response(
            HomeworkSubmissionSerializer(submission, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
