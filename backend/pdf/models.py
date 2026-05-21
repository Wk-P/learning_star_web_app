from django.db import models


class PdfFolder(models.Model):
    # path = ['root', 'level2', 'level3', ...]
    id = models.AutoField(primary_key=True, unique=True)
    path = models.JSONField(default=list, null=True, blank=True)


class Pdf(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=1024, default='#', blank=True, null=True)
    url = models.CharField(max_length=2048, blank=True, null=True)
    path = models.ForeignKey(PdfFolder, on_delete=models.SET_NULL, null=True, blank=True, related_name='pdfs_list')
