from django.db import models


class AudioFolder(models.Model):
    # path = ['root', 'level2', 'level3', ...]
    id = models.AutoField(primary_key=True, unique=True)
    path = models.JSONField(default=list, null=True, blank=True)



# Create your models here.
class Audio(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=1024, default='#', blank=True, null=True)
    url = models.URLField(max_length=1024, default="-", blank=True, null=True, unique=True)
    path = models.ForeignKey(AudioFolder, on_delete=models.SET_NULL, null=True, blank=True, related_name="audios_list")
