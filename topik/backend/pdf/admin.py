from django.contrib import admin
from .models import Pdf, PdfFolder

admin.site.register(PdfFolder)
admin.site.register(Pdf)
