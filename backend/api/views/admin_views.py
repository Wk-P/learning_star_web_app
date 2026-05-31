import re
import secrets
import string
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Subject, Course, ClassSession, CourseFile, Homework, Enrollment, HomeworkSubmission, AttendanceRecord
from ..permissions import IsAdmin, IsAdminOrStaff
from ..serializers import (
    SubjectSerializer,
    AdminUserSerializer,
    AdminUserCreateSerializer,
    CourseSerializer,
    ClassSessionSerializer,
    CourseFileSerializer,
    HomeworkSerializer,
    EnrollmentRecordSerializer,
    HomeworkSubmissionSerializer,
    AttendanceRecordSerializer,
)

User = get_user_model()
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


def _random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ── 用户管理（仅 admin） ──────────────────────────────────────────────────────

class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by('id')
        return Response(AdminUserSerializer(users, many=True).data)

    def post(self, request):
        s = AdminUserCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(AdminUserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminUserSerializer(user).data)

    def patch(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = AdminUserSerializer(user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserResetPasswordView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        new_pw = _random_password()
        user.set_password(new_pw)
        user.save()
        return Response({'newPassword': new_pw})


# ── 用户课程关联管理（仅 admin） ───────────────────────────────────────────────

class AdminUserEnrollmentListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, user_id):
        enrollments = Enrollment.objects.filter(user_id=user_id).select_related('course')
        return Response(EnrollmentRecordSerializer(enrollments, many=True).data)

    def post(self, request, user_id):
        course_id = request.data.get('courseId')
        enrolled_at = request.data.get('enrolledAt')
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        defaults = {'enrolled_at': enrolled_at} if enrolled_at else {}
        enrollment, created = Enrollment.objects.get_or_create(
            user_id=user_id, course=course, defaults=defaults,
        )
        if not created:
            return Response({'detail': '已申请该课程'}, status=status.HTTP_409_CONFLICT)
        return Response(EnrollmentRecordSerializer(enrollment).data, status=status.HTTP_201_CREATED)


class AdminUserEnrollmentDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, user_id, course_id):
        try:
            enrollment = Enrollment.objects.get(user_id=user_id, course_id=course_id)
        except Enrollment.DoesNotExist:
            return Response({'detail': '关联不存在'}, status=status.HTTP_404_NOT_FOUND)
        enrolled_at = request.data.get('enrolledAt')
        if enrolled_at:
            enrollment.enrolled_at = enrolled_at
            enrollment.save()
        return Response(EnrollmentRecordSerializer(enrollment).data)

    def delete(self, request, user_id, course_id):
        try:
            enrollment = Enrollment.objects.get(user_id=user_id, course_id=course_id)
        except Enrollment.DoesNotExist:
            return Response({'detail': '关联不存在'}, status=status.HTTP_404_NOT_FOUND)
        enrollment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 用户作业管理（仅 admin） ──────────────────────────────────────────────────

class AdminUserHomeworkListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, user_id):
        submissions = (
            HomeworkSubmission.objects.filter(user_id=user_id)
            .select_related('homework__course')
        )
        return Response(HomeworkSubmissionSerializer(submissions, many=True, context={'request': request}).data)


class AdminUserHomeworkDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, user_id, homework_id):
        try:
            submission = HomeworkSubmission.objects.get(user_id=user_id, homework_id=homework_id)
        except HomeworkSubmission.DoesNotExist:
            return Response({'detail': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        score = request.data.get('score')
        if score is None:
            return Response({'detail': '请提供分数'}, status=status.HTTP_400_BAD_REQUEST)
        submission.score = int(score)
        submission.graded = True
        submission.save()
        return Response(HomeworkSubmissionSerializer(submission, context={'request': request}).data)


# ── 教师归属辅助函数 ──────────────────────────────────────────────────────────

def _teaching_course_ids(user):
    """返回该 staff 用户归属的所有课程 ID（course.teacher 或任意课节 teacher）。"""
    from_course = set(Course.objects.filter(teacher=user).values_list('id', flat=True))
    from_class = set(ClassSession.objects.filter(teacher=user).values_list('course_id', flat=True))
    return from_course | from_class


def _can_access_course(user, course_id: int) -> bool:
    if user.role == 'admin':
        return True
    return course_id in _teaching_course_ids(user)


# ── 课程管理（admin + staff） ─────────────────────────────────────────────────

class AdminCourseListView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        # admin 看全部；staff 只看被指定为讲课人的课程（course.teacher 或任意课节 teacher）
        if request.user.role == 'admin':
            courses = Course.objects.all()
        else:
            ids = _teaching_course_ids(request.user)
            courses = Course.objects.filter(id__in=ids)
        return Response(CourseSerializer(courses.order_by('start_time'), many=True, context={'request': request}).data)

    def post(self, request):
        # 只有 admin 可创建课程（staff 通过 admin 分配）
        if request.user.role != 'admin':
            return Response({'detail': '仅管理员可创建课程'}, status=status.HTTP_403_FORBIDDEN)
        s = CourseSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class AdminCourseDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def _get_course(self, course_id):
        try:
            return Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return None

    def get(self, request, course_id):
        course = self._get_course(course_id)
        if not course:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CourseSerializer(course, context={'request': request}).data)

    def patch(self, request, course_id):
        course = self._get_course(course_id)
        if not course:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = CourseSerializer(course, data=request.data, partial=True, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, course_id):
        if request.user.role != 'admin':
            return Response({'detail': '仅管理员可删除课程'}, status=status.HTTP_403_FORBIDDEN)
        course = self._get_course(course_id)
        if not course:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 出勤管理 ──────────────────────────────────────────────────────────────────

class AdminAttendanceView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request, course_id, class_id):
        records = AttendanceRecord.objects.filter(class_session_id=class_id)
        return Response(AttendanceRecordSerializer(records, many=True).data)

    def put(self, request, course_id, class_id):
        if not isinstance(request.data, list):
            return Response({'detail': '请提供列表数据'}, status=status.HTTP_400_BAD_REQUEST)

        for item in request.data:
            user_id = item.get('userId')
            present = item.get('present', True)
            note = item.get('note', '')
            AttendanceRecord.objects.update_or_create(
                class_session_id=class_id,
                user_id=user_id,
                defaults={'present': present, 'note': note},
            )
        records = AttendanceRecord.objects.filter(class_session_id=class_id)
        return Response(AttendanceRecordSerializer(records, many=True).data)


# ── 课程文件管理 ───────────────────────────────────────────────────────────────

class AdminCourseFileView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, course_id):
        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded.size > MAX_UPLOAD_BYTES:
            return Response({'detail': '文件不能超过 50MB'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        cf = CourseFile.objects.create(course=course, name=uploaded.name, file=uploaded)
        return Response(CourseFileSerializer(cf, context={'request': request}).data, status=status.HTTP_201_CREATED)


class AdminCourseFileDeleteView(APIView):
    permission_classes = [IsAdminOrStaff]

    def delete(self, request, course_id, file_id):
        try:
            cf = CourseFile.objects.get(pk=file_id, course_id=course_id)
        except CourseFile.DoesNotExist:
            return Response({'detail': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        cf.file.delete(save=False)
        cf.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 课节资料文件管理 ────────────────────────────────────────────────────────────

class AdminClassFileView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, course_id, class_id):
        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded.size > MAX_UPLOAD_BYTES:
            return Response({'detail': '文件不能超过 50MB'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(pk=course_id)
            cls = ClassSession.objects.get(pk=class_id, course_id=course_id)
        except (Course.DoesNotExist, ClassSession.DoesNotExist):
            return Response({'detail': '课程或课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        cf = CourseFile.objects.create(
            course=course, class_session=cls, name=uploaded.name, file=uploaded
        )
        return Response(CourseFileSerializer(cf, context={'request': request}).data, status=status.HTTP_201_CREATED)


class AdminClassFileDeleteView(APIView):
    permission_classes = [IsAdminOrStaff]

    def delete(self, request, course_id, class_id, file_id):
        try:
            cf = CourseFile.objects.get(pk=file_id, course_id=course_id, class_session_id=class_id)
        except CourseFile.DoesNotExist:
            return Response({'detail': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        cf.file.delete(save=False)
        cf.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 课节 week/session 重新编号 ────────────────────────────────────────────────

def _recompute_all_sessions(course):
    """
    按 class_time 升序重新计算所有课节的 week 和 session，并批量写回。
    - week: 从课程开始日期算起，每 7 天为一周
    - session: 同一周内按 class_time 先后从 1 开始编号
    """
    from django.utils import timezone as dj_tz
    sessions = list(
        ClassSession.objects.filter(course=course).order_by('class_time')
    )
    if not sessions:
        return

    # 课程开始日期（用 Asia/Shanghai，与前端一致）
    tz = dj_tz.get_current_timezone()
    start_date = course.start_time.astimezone(tz).date()

    week_counter: dict[int, int] = {}
    to_update = []
    for s in sessions:
        class_date = s.class_time.astimezone(tz).date()
        week = (class_date - start_date).days // 7 + 1
        week_counter[week] = week_counter.get(week, 0) + 1
        s.week = week
        s.session = week_counter[week]
        to_update.append(s)

    ClassSession.objects.bulk_update(to_update, ['week', 'session'])


# ── 课节管理（admin + staff） ─────────────────────────────────────────────────

class AdminClassListView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request, course_id):
        sessions = (
            ClassSession.objects.filter(course_id=course_id)
            .select_related('teacher').prefetch_related('files')
            .order_by('class_time')
        )
        return Response(ClassSessionSerializer(sessions, many=True, context={'request': request}).data)

    def post(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        # week/session 由后端自动推算，不接受客户端传入
        data = {**request.data, 'courseId': course_id, 'week': 1, 'session': 1}
        s = ClassSessionSerializer(data=data, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        # 新增后重新编号所有课节
        _recompute_all_sessions(course)
        # 返回更新后的该课节
        updated = ClassSession.objects.select_related('teacher').prefetch_related('files').get(pk=s.instance.pk)
        return Response(ClassSessionSerializer(updated, context={'request': request}).data, status=status.HTTP_201_CREATED)


class AdminClassDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def _get_session(self, course_id, class_id):
        try:
            return ClassSession.objects.select_related('teacher').prefetch_related('files').get(
                pk=class_id, course_id=course_id
            )
        except ClassSession.DoesNotExist:
            return None

    def get(self, request, course_id, class_id):
        session = self._get_session(course_id, class_id)
        if not session:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClassSessionSerializer(session, context={'request': request}).data)

    def patch(self, request, course_id, class_id):
        session = self._get_session(course_id, class_id)
        if not session:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = ClassSessionSerializer(session, data=request.data, partial=True, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        # 修改时间后重新编号
        if 'classTime' in request.data or 'class_time' in request.data:
            _recompute_all_sessions(session.course)
            session.refresh_from_db()
        return Response(ClassSessionSerializer(session, context={'request': request}).data)

    def delete(self, request, course_id, class_id):
        session = self._get_session(course_id, class_id)
        if not session:
            return Response({'detail': '课节不存在'}, status=status.HTTP_404_NOT_FOUND)
        course = session.course
        session.delete()
        # 删除后重新编号剩余课节
        _recompute_all_sessions(course)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 作业管理（admin + staff） ─────────────────────────────────────────────────

class AdminHomeworkListView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        # admin 看全部；staff 只看自己所教课程的作业
        if request.user.role == 'admin':
            homework = Homework.objects.all()
        else:
            ids = _teaching_course_ids(request.user)
            homework = Homework.objects.filter(course_id__in=ids)
        return Response(HomeworkSerializer(homework.select_related('course').order_by('-start_time'), many=True, context={'request': request}).data)

    def post(self, request):
        s = HomeworkSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class AdminHomeworkDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def _get_hw(self, homework_id):
        try:
            return Homework.objects.select_related('course').get(pk=homework_id)
        except Homework.DoesNotExist:
            return None

    def get(self, request, homework_id):
        hw = self._get_hw(homework_id)
        if not hw:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(HomeworkSerializer(hw, context={'request': request}).data)

    def patch(self, request, homework_id):
        hw = self._get_hw(homework_id)
        if not hw:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = HomeworkSerializer(hw, data=request.data, partial=True, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, homework_id):
        hw = self._get_hw(homework_id)
        if not hw:
            return Response({'detail': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        hw.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminHomeworkSubmissionsView(APIView):
    """列出某作业的全部学生提交，供 admin/staff 批改。"""
    permission_classes = [IsAdminOrStaff]

    def get(self, request, homework_id):
        submissions = (
            HomeworkSubmission.objects.filter(homework_id=homework_id)
            .select_related('user')
        )
        return Response(HomeworkSubmissionSerializer(submissions, many=True, context={'request': request}).data)


class AdminGradeSubmissionView(APIView):
    """给单份提交评分。"""
    permission_classes = [IsAdminOrStaff]

    def patch(self, request, homework_id, submission_id):
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


# ── 科目管理（仅 admin 可写，staff 可读） ────────────────────────────────────

class AdminSubjectListView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrStaff()]
        return [IsAdmin()]

    def get(self, request):
        return Response(SubjectSerializer(Subject.objects.all().order_by('id'), many=True).data)

    def post(self, request):
        s = SubjectSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class AdminSubjectDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrStaff()]
        return [IsAdmin()]

    def _get(self, subject_id):
        try:
            return Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return None

    def get(self, request, subject_id):
        obj = self._get(subject_id)
        if not obj:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(SubjectSerializer(obj).data)

    def patch(self, request, subject_id):
        obj = self._get(subject_id)
        if not obj:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        s = SubjectSerializer(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, subject_id):
        obj = self._get(subject_id)
        if not obj:
            return Response({'detail': '科目不存在'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── 根据日程自动生成课节 ──────────────────────────────────────────────────────

_FULL_DAY_MAP = {
    '周一': 0, '周二': 1, '周三': 2, '周四': 3,
    '周五': 4, '周六': 5, '周日': 6, '周天': 6,
}
_CHAR_DAY_MAP = {
    '一': 0, '二': 1, '三': 2, '四': 3,
    '五': 4, '六': 5, '日': 6, '天': 6,
}


def _parse_schedule(schedule: str):
    """
    解析日程字符串，返回 (weekdays: list[int], hour: int, minute: int)。
    支持格式：
      '每周一、三 09:00–11:00'   ← 首项全称，后项省略"周"
      '每周一、周三 09:00–11:00' ← 全称
    """
    time_match = re.search(r'(\d{1,2}):(\d{2})', schedule)
    hour   = int(time_match.group(1)) if time_match else 9
    minute = int(time_match.group(2)) if time_match else 0

    # 只在时间之前的部分找星期
    day_part = schedule[:time_match.start()] if time_match else schedule

    weekdays: set[int] = set()

    # 先找完整名称（周一 ~ 周日）
    for name, wd in _FULL_DAY_MAP.items():
        if name in day_part:
            weekdays.add(wd)
            day_part = day_part.replace(name, '')  # 移除已匹配，避免重复

    # 再找剩余的单字（处理 "每周一、三" 中缩略的"三"）
    for char, wd in _CHAR_DAY_MAP.items():
        if char in day_part:
            weekdays.add(wd)

    return sorted(weekdays), hour, minute


class AdminCourseGenerateClassesView(APIView):
    """
    POST：根据课程日程自动生成所有课节。
    body: { "clearExisting": true }  （默认清空现有课节再重新生成）
    """
    permission_classes = [IsAdminOrStaff]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not course.schedule:
            return Response({'detail': '课程尚未设置上课日程'}, status=status.HTTP_400_BAD_REQUEST)

        weekdays, hour, minute = _parse_schedule(course.schedule)
        if not weekdays:
            return Response({'detail': '无法从日程中解析出上课日期，请检查格式'}, status=status.HTTP_400_BAD_REQUEST)

        clear_existing = request.data.get('clearExisting', True)
        if clear_existing:
            ClassSession.objects.filter(course=course).delete()

        # 使用客户端时区解析日期和时间，避免服务器时区与用户时区不一致导致的偏差
        from datetime import timezone as dt_tz
        utc_offset_min = request.data.get('utcOffsetMinutes')
        if utc_offset_min is not None:
            client_tz = dt_tz(timedelta(minutes=int(utc_offset_min)))
        else:
            client_tz = timezone.get_current_timezone()

        start_date = course.start_time.astimezone(client_tz).date()
        end_date   = course.end_time.astimezone(client_tz).date()

        to_create = []
        current = start_date
        while current <= end_date:
            wd = current.weekday()  # 0=Monday
            if wd in weekdays:
                # 用客户端时区构造课节时间，保证"11:00"就是用户所在时区的 11:00
                class_dt = datetime(
                    current.year, current.month, current.day, hour, minute,
                    tzinfo=client_tz
                )
                to_create.append(ClassSession(
                    course=course,
                    week=1,     # 占位，下面统一由 _recompute_all_sessions 重算
                    session=1,
                    class_time=class_dt,
                    teacher=course.teacher,
                ))
            current += timedelta(days=1)

        ClassSession.objects.bulk_create(to_create)
        # 统一按 class_time 重新计算 week / session
        _recompute_all_sessions(course)

        sessions = ClassSession.objects.filter(course=course).select_related('teacher').prefetch_related('files')
        return Response({
            'count': len(to_create),
            'sessions': ClassSessionSerializer(sessions, many=True, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)
