"""
教师专属视图（role='staff'）。
教师只能操作自己被分配的课程/课节/作业。
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Course, ClassSession, Homework, HomeworkSubmission, AttendanceRecord
from ..permissions import IsStaff
from ..serializers import (
    CourseSerializer,
    ClassSessionSerializer,
    HomeworkSerializer,
    HomeworkSubmissionSerializer,
    AttendanceRecordSerializer,
)


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def _teacher_course_ids(user):
    """返回该教师归属的课程 ID 集合（直接指定 + 课节关联）。"""
    from_course = set(Course.objects.filter(teacher=user).values_list('id', flat=True))
    from_class = set(ClassSession.objects.filter(teacher=user).values_list('course_id', flat=True))
    return from_course | from_class


def _teacher_can_access_course(user, course_id: int) -> bool:
    return course_id in _teacher_course_ids(user)


def _teacher_can_access_class(user, cls) -> bool:
    return cls.teacher_id == user.id or _teacher_can_access_course(user, cls.course_id)


# ── 课程 ──────────────────────────────────────────────────────────────────────

class TeacherCourseListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        ids = _teacher_course_ids(request.user)
        courses = Course.objects.filter(id__in=ids).order_by('start_time')
        return Response(CourseSerializer(courses, many=True, context={'request': request}).data)


class TeacherCourseDetailView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, course_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权访问该课程'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CourseSerializer(course, context={'request': request}).data)

    def patch(self, request, course_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权修改该课程'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = CourseSerializer(course, data=request.data, partial=True, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)


# ── 课节 ──────────────────────────────────────────────────────────────────────

class TeacherClassListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, course_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权访问该课程'}, status=status.HTTP_403_FORBIDDEN)
        sessions = (
            ClassSession.objects.filter(course_id=course_id)
            .select_related('teacher').prefetch_related('files')
        )
        return Response(ClassSessionSerializer(sessions, many=True, context={'request': request}).data)

    def post(self, request, course_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权在该课程添加课节'}, status=status.HTTP_403_FORBIDDEN)
        # 自动将教师自己设为讲课人
        data = {**request.data, 'courseId': course_id}
        if not data.get('teacherId'):
            data = {**data, 'teacherId': request.user.id}
        s = ClassSessionSerializer(data=data, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class TeacherClassDetailView(APIView):
    permission_classes = [IsStaff]

    def _get(self, course_id, class_id):
        try:
            return ClassSession.objects.select_related('teacher').prefetch_related('files').get(
                pk=class_id, course_id=course_id
            )
        except ClassSession.DoesNotExist:
            return None

    def get(self, request, course_id, class_id):
        cls = self._get(course_id, class_id)
        if not cls:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not _teacher_can_access_class(request.user, cls):
            return Response({'detail': '无权访问该课节'}, status=status.HTTP_403_FORBIDDEN)
        return Response(ClassSessionSerializer(cls, context={'request': request}).data)

    def patch(self, request, course_id, class_id):
        cls = self._get(course_id, class_id)
        if not cls:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not _teacher_can_access_class(request.user, cls):
            return Response({'detail': '无权修改该课节'}, status=status.HTTP_403_FORBIDDEN)
        s = ClassSessionSerializer(cls, data=request.data, partial=True, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, course_id, class_id):
        cls = self._get(course_id, class_id)
        if not cls:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not _teacher_can_access_class(request.user, cls):
            return Response({'detail': '无权删除该课节'}, status=status.HTTP_403_FORBIDDEN)
        cls.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 出勤 ──────────────────────────────────────────────────────────────────────

class TeacherAttendanceView(APIView):
    permission_classes = [IsStaff]

    def _check(self, user, course_id, class_id):
        cls = ClassSession.objects.filter(pk=class_id, course_id=course_id).first()
        if not cls:
            return None, False
        return cls, _teacher_can_access_class(user, cls)

    def get(self, request, course_id, class_id):
        cls, ok = self._check(request.user, course_id, class_id)
        if not cls:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not ok:
            return Response({'detail': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        records = AttendanceRecord.objects.filter(class_session_id=class_id)
        return Response(AttendanceRecordSerializer(records, many=True).data)

    def put(self, request, course_id, class_id):
        cls, ok = self._check(request.user, course_id, class_id)
        if not cls:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not ok:
            return Response({'detail': '无权修改'}, status=status.HTTP_403_FORBIDDEN)
        if not isinstance(request.data, list):
            return Response({'detail': '请提供列表数据'}, status=status.HTTP_400_BAD_REQUEST)
        for item in request.data:
            AttendanceRecord.objects.update_or_create(
                class_session_id=class_id, user_id=item.get('userId'),
                defaults={'present': item.get('present', True), 'note': item.get('note', '')},
            )
        records = AttendanceRecord.objects.filter(class_session_id=class_id)
        return Response(AttendanceRecordSerializer(records, many=True).data)


# ── 作业 ──────────────────────────────────────────────────────────────────────

class TeacherHomeworkListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, course_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        homework = Homework.objects.filter(course_id=course_id).select_related('course').order_by('start_time')
        return Response(HomeworkSerializer(homework, many=True, context={'request': request}).data)

    def post(self, request, course_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权在该课程创建作业'}, status=status.HTTP_403_FORBIDDEN)
        data = {**request.data, 'courseId': course_id}
        s = HomeworkSerializer(data=data, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class TeacherHomeworkDetailView(APIView):
    permission_classes = [IsStaff]

    def _get(self, homework_id, course_id):
        try:
            return Homework.objects.select_related('course').get(pk=homework_id, course_id=course_id)
        except Homework.DoesNotExist:
            return None

    def get(self, request, course_id, homework_id):
        hw = self._get(homework_id, course_id)
        if not hw:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        return Response(HomeworkSerializer(hw, context={'request': request}).data)

    def patch(self, request, course_id, homework_id):
        hw = self._get(homework_id, course_id)
        if not hw:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权修改'}, status=status.HTTP_403_FORBIDDEN)
        s = HomeworkSerializer(hw, data=request.data, partial=True, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, course_id, homework_id):
        hw = self._get(homework_id, course_id)
        if not hw:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权删除'}, status=status.HTTP_403_FORBIDDEN)
        hw.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 作业提交列表 & 评分 ───────────────────────────────────────────────────────

class TeacherHomeworkSubmissionsView(APIView):
    """查看某作业的全部学生提交，用于教师批改。"""
    permission_classes = [IsStaff]

    def get(self, request, course_id, homework_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        submissions = HomeworkSubmission.objects.filter(homework_id=homework_id).select_related('user')
        return Response(HomeworkSubmissionSerializer(submissions, many=True, context={'request': request}).data)


class TeacherGradeSubmissionView(APIView):
    """教师给单份提交评分。"""
    permission_classes = [IsStaff]

    def patch(self, request, course_id, homework_id, submission_id):
        if not _teacher_can_access_course(request.user, course_id):
            return Response({'detail': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        try:
            submission = HomeworkSubmission.objects.get(pk=submission_id, homework_id=homework_id)
        except HomeworkSubmission.DoesNotExist:
            return Response({'detail': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        score = request.data.get('score')
        if score is None:
            return Response({'detail': '请提供分数'}, status=status.HTTP_400_BAD_REQUEST)
        submission.score = int(score)
        submission.graded = True
        submission.save()
        return Response(HomeworkSubmissionSerializer(submission, context={'request': request}).data)
