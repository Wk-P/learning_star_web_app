from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_add_classsession_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursefile',
            name='class_session',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='files',
                to='api.classsession',
            ),
        ),
    ]
