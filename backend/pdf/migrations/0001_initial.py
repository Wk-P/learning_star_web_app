from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PdfFolder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('path', models.JSONField(blank=True, default=list, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pdf',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, default='#', max_length=1024, null=True)),
                ('url', models.CharField(blank=True, max_length=2048, null=True)),
                ('path', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pdfs_list', to='pdf.pdffolder')),
            ],
        ),
    ]
