from django.db import migrations
from django.utils import timezone as dj_tz


def recompute_week_session(apps, schema_editor):
    """
    按 class_time 升序重新计算所有课节的 week / session。
    - week : (class_date - course_start_date).days // 7 + 1
    - session : 同一周内按 class_time 先后从 1 编号
    """
    Course = apps.get_model('api', 'Course')
    ClassSession = apps.get_model('api', 'ClassSession')

    tz = dj_tz.get_current_timezone()

    for course in Course.objects.all():
        sessions = list(
            ClassSession.objects.filter(course=course).order_by('class_time')
        )
        if not sessions:
            continue

        start_date = course.start_time.astimezone(tz).date()
        week_counter: dict = {}
        to_update = []

        for s in sessions:
            class_date = s.class_time.astimezone(tz).date()
            week = (class_date - start_date).days // 7 + 1
            week_counter[week] = week_counter.get(week, 0) + 1
            s.week = week
            s.session = week_counter[week]
            to_update.append(s)

        ClassSession.objects.bulk_update(to_update, ['week', 'session'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_add_display_name'),
    ]

    operations = [
        migrations.RunPython(
            recompute_week_session,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
