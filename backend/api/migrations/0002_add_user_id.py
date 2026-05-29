import secrets
from django.db import migrations, models


def populate_user_id(apps, schema_editor):
    User = apps.get_model('api', 'User')
    used = set()
    for user in User.objects.all():
        while True:
            uid = secrets.token_hex(4)
            if uid not in used:
                used.add(uid)
                break
        user.user_id = uid
        user.save(update_fields=['user_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        # 第一步：加列，暂不加唯一约束，允许空值
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.CharField(max_length=8, blank=True, default='', verbose_name='用户ID (8位hex)'),
        ),
        # 第二步：为已有用户填充唯一 hex 值
        migrations.RunPython(populate_user_id, migrations.RunPython.noop),
        # 第三步：加唯一约束
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.CharField(max_length=8, unique=True, blank=True, verbose_name='用户ID (8位hex)'),
        ),
    ]
