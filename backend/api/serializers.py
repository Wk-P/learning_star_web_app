import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Subject, Course, ClassSession, CourseFile, Homework, Enrollment, HomeworkSubmission, AttendanceRecord

User = get_user_model()


# ── camelCase 互转工具 ────────────────────────────────────────────────────────

def _snake_to_camel(name: str) -> str:
    parts = name.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])


def _camel_to_snake(name: str) -> str:
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


class CamelCaseMixin:
    """自动将序列化输出的 snake_case key 转为 camelCase，反序列化时将 camelCase key 转为 snake_case。"""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {_snake_to_camel(k): v for k, v in data.items()}

    def to_internal_value(self, data):
        converted = {_camel_to_snake(k): v for k, v in data.items()}
        return super().to_internal_value(converted)


# ── JWT ────────────────────────────────────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token


# ── User ──────────────────────────────────────────────────────────────────────

class UserSerializer(CamelCaseMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email', 'role']


class AdminUserSerializer(CamelCaseMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email', 'role', 'date_joined', 'is_active']
        read_only_fields = ['date_joined', 'user_id']


class AdminUserCreateSerializer(CamelCaseMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email', 'role', 'password']
        read_only_fields = ['user_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ── Subject ───────────────────────────────────────────────────────────────────

class SubjectSerializer(CamelCaseMixin, serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'icon', 'color', 'course_count']

    def get_course_count(self, obj):
        return obj.courses.count()


# ── Course ────────────────────────────────────────────────────────────────────

class CourseSerializer(CamelCaseMixin, serializers.ModelSerializer):
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source='subject', allow_null=True, required=False
    )
    subject_name = serializers.CharField(source='subject.name', read_only=True, default='')
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='staff'),
        source='teacher', allow_null=True, required=False
    )
    teacher_name = serializers.CharField(source='teacher.username', read_only=True, default='')
    status = serializers.SerializerMethodField()
    duration_weeks = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'subject_id', 'subject_name',
            'teacher_id', 'teacher_name',
            'name', 'description', 'schedule',
            'status', 'start_time', 'end_time', 'duration_weeks',
        ]

    def get_status(self, obj):
        return obj.status

    def get_duration_weeks(self, obj):
        delta = obj.end_time - obj.start_time
        return max(1, round(delta.days / 7))


# ── CourseFile ────────────────────────────────────────────────────────────────

class CourseFileSerializer(CamelCaseMixin, serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = CourseFile
        fields = ['id', 'name', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else ''


# ── ClassSession ──────────────────────────────────────────────────────────────

class ClassSessionSerializer(CamelCaseMixin, serializers.ModelSerializer):
    # 显式声明可写 FK 字段
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', required=False
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='staff'),
        source='teacher', allow_null=True, required=False
    )
    # 只读展示字段
    title = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    files = CourseFileSerializer(many=True, read_only=True)

    class Meta:
        model = ClassSession
        fields = [
            'id', 'course_id', 'week', 'session', 'title',
            'class_time', 'meeting_url', 'teacher_id', 'teacher_name', 'students', 'files',
        ]

    def get_title(self, obj):
        return obj.title

    def get_teacher_name(self, obj):
        return obj.teacher.username if obj.teacher else ''

    def get_students(self, obj):
        return list(
            Enrollment.objects.filter(course=obj.course)
            .select_related('user')
            .values_list('user__username', flat=True)
        )


# ── Homework ──────────────────────────────────────────────────────────────────

class HomeworkSerializer(CamelCaseMixin, serializers.ModelSerializer):
    # 显式声明可写 FK 字段
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course'
    )
    status = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Homework
        fields = ['id', 'course_id', 'course_name', 'name', 'description', 'start_time', 'end_time', 'max_score', 'status']

    def get_status(self, obj):
        return obj.status


# ── Enrollment ────────────────────────────────────────────────────────────────

class EnrollmentRecordSerializer(CamelCaseMixin, serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_status = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['course_id', 'course_name', 'enrolled_at', 'course_status']

    def get_course_status(self, obj):
        return obj.course.status


# ── HomeworkSubmission ────────────────────────────────────────────────────────

class HomeworkSubmissionSerializer(CamelCaseMixin, serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = HomeworkSubmission
        fields = ['id', 'homework_id', 'user_id', 'submitted_at', 'file_url', 'file_name', 'score', 'graded']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else ''


# ── AttendanceRecord ──────────────────────────────────────────────────────────

class AttendanceRecordSerializer(CamelCaseMixin, serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['class_session_id', 'user_id', 'present', 'note']


# ── CourseScore ───────────────────────────────────────────────────────────────

class CourseScoreSerializer(serializers.Serializer):
    courseId = serializers.IntegerField()
    courseName = serializers.CharField()
    courseStatus = serializers.CharField()
    finalScore = serializers.FloatField(allow_null=True)
    graded = serializers.BooleanField()
