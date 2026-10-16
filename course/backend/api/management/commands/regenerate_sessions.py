"""
用正确时区（Asia/Shanghai）重新生成所有课程的课节。
等价于在管理后台对每门课点一次"重新生成课节"。
"""
import re
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import ClassSession, Course

_FULL_DAY_MAP = {
    '周一': 0, '周二': 1, '周三': 2, '周四': 3,
    '周五': 4, '周六': 5, '周日': 6, '周天': 6,
}
_CHAR_DAY_MAP = {
    '一': 0, '二': 1, '三': 2, '四': 3,
    '五': 4, '六': 5, '日': 6, '天': 6,
}


def _parse_schedule(schedule: str):
    time_match = re.search(r'(\d{1,2}):(\d{2})', schedule)
    hour   = int(time_match.group(1)) if time_match else 9
    minute = int(time_match.group(2)) if time_match else 0

    day_part = schedule[:time_match.start()] if time_match else schedule
    weekdays: set[int] = set()

    for name, wd in _FULL_DAY_MAP.items():
        if name in day_part:
            weekdays.add(wd)
            day_part = day_part.replace(name, '')

    for ch, wd in _CHAR_DAY_MAP.items():
        if ch in day_part:
            weekdays.add(wd)

    return sorted(weekdays), hour, minute


class Command(BaseCommand):
    help = '用正确时区重新生成所有课程的课节（修复时区偏移导致的日期错误）'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='仅预览，不写入')
        parser.add_argument('--course-id', type=int, help='只处理指定 course_id')

    def handle(self, *args, **options):
        dry_run   = options['dry_run']
        course_id = options.get('course_id')

        qs = Course.objects.all()
        if course_id:
            qs = qs.filter(pk=course_id)

        for course in qs:
            if not course.schedule:
                self.stdout.write(f'  跳过 [{course.pk}] {course.name}（无日程）')
                continue

            weekdays, hour, minute = _parse_schedule(course.schedule)
            if not weekdays:
                self.stdout.write(f'  跳过 [{course.pk}] {course.name}（日程解析失败）')
                continue

            # 以本地时区取日期，避免 UTC 跨天偏差
            start_date = timezone.localtime(course.start_time).date()
            end_date   = timezone.localtime(course.end_time).date()

            to_create = []
            current = start_date
            while current <= end_date:
                wd = current.weekday()
                if wd in weekdays:
                    week_num    = (current - start_date).days // 7 + 1
                    session_num = weekdays.index(wd) + 1
                    class_dt    = timezone.make_aware(
                        datetime(current.year, current.month, current.day, hour, minute)
                    )
                    to_create.append(ClassSession(
                        course=course,
                        week=week_num,
                        session=session_num,
                        class_time=class_dt,
                        teacher=course.teacher,
                    ))
                current += timedelta(days=1)

            if dry_run:
                first = to_create[0].class_time if to_create else None
                self.stdout.write(
                    f'  [{course.pk}] {course.name}: {len(to_create)} 节'
                    + (f'，第一节 {timezone.localtime(first).strftime("%Y-%m-%d %H:%M")}' if first else '')
                )
            else:
                ClassSession.objects.filter(course=course).delete()
                ClassSession.objects.bulk_create(to_create)
                first = to_create[0].class_time if to_create else None
                self.stdout.write(self.style.SUCCESS(
                    f'  [{course.pk}] {course.name}: 重新生成 {len(to_create)} 节'
                    + (f'，第一节 {timezone.localtime(first).strftime("%Y-%m-%d %H:%M")}' if first else '')
                ))

        action = '预览' if dry_run else '完成'
        self.stdout.write(self.style.SUCCESS(f'{action}。'))
