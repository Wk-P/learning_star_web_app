from django.contrib import admin

from .models import CourseVideo, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')


@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'title', 'level', 'sort_order')
    list_filter = ('subject', 'level')
    search_fields = ('title', 'url')
