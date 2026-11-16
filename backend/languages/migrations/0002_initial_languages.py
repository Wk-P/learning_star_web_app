from django.db import migrations


def create(apps, schema_editor):
    Category = apps.get_model('languages', 'LanguageCategory')
    Language = apps.get_model('languages', 'Language')
    east_asia, _ = Category.objects.get_or_create(name='东亚语言', defaults={'description': '韩语、日语、汉语等', 'sort_order': 1})
    Language.objects.get_or_create(slug='ko', defaults={
        'category': east_asia, 'name': '韩语', 'native_name': '한국어',
        'description': 'TOPIK 视频课程、听力音频与学习资料', 'color': '#2ec4c0', 'sort_order': 1,
    })


class Migration(migrations.Migration):
    dependencies = [('languages', '0001_initial')]
    operations = [migrations.RunPython(create, migrations.RunPython.noop)]
