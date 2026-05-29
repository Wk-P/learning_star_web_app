import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def _generate_user_id() -> str:
    """生成 8 位十六进制 user_id，确保唯一。"""
    return secrets.token_hex(4)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', '学生'),
        ('staff', '教师'),
        ('admin', '管理员'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    user_id = models.CharField(
        max_length=8, unique=True, blank=True,
        verbose_name='用户ID (8位hex)',
    )

    def save(self, *args, **kwargs):
        if not self.user_id:
            # 循环直到生成唯一值（碰撞概率极低）
            uid = _generate_user_id()
            while User.objects.filter(user_id=uid).exists():
                uid = _generate_user_id()
            self.user_id = uid
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'auth_user'


class Subject(models.Model):
    """科目分类，如：数学、英语、物理"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True, default='📖')   # emoji 图标
    color = models.CharField(max_length=7, blank=True, default='#6366f1')  # hex 颜色

    def __str__(self):
        return self.name


class Course(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses',
    )
    teacher = models.ForeignKey(
        'User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='teaching_courses',
        verbose_name='主讲教师',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    schedule = models.CharField(max_length=200, blank=True)  # 如：每周二 09:00-11:00

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'not_started'
        if now > self.end_time:
            return 'ended'
        return 'in_progress'

    def __str__(self):
        return self.name


class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    week = models.PositiveIntegerField()
    session = models.PositiveIntegerField()
    class_time = models.DateTimeField()
    meeting_url = models.URLField(blank=True, max_length=500)
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_classes'
    )

    @property
    def title(self):
        return f'第{self.week}周第{self.session}课'

    class Meta:
        ordering = ['week', 'session']

    def __str__(self):
        return f'{self.course.name} {self.title}'


class CourseFile(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='files')
    class_session = models.ForeignKey(
        ClassSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='files'
    )
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_files/')

    def __str__(self):
        return self.name


class Homework(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='homework')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'not_started'
        if now > self.end_time:
            return 'ended'
        return 'in_progress'

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f'{self.course.name} — {self.name}'


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.username} → {self.course.name}'


class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='homework_submissions')
    submitted_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='homework_submissions/')
    file_name = models.CharField(max_length=200, blank=True)
    score = models.IntegerField(null=True, blank=True)
    graded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('homework', 'user')

    def __str__(self):
        return f'{self.user.username} — {self.homework.name}'


class AttendanceRecord(models.Model):
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    present = models.BooleanField(default=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('class_session', 'user')
