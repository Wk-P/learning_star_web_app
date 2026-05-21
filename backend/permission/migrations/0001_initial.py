from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('video', '视频'), ('audio', '音频'), ('pdf', 'PDF')], max_length=10)),
                ('root_dir', models.CharField(max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'media_type', 'root_dir')},
            },
        ),
    ]
