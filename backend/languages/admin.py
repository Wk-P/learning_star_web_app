from django.contrib import admin

from .models import Language, LanguageCategory, MediaPermission


@admin.register(LanguageCategory)
class LanguageCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sort_order')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'category', 'sort_order', 'is_active')
    list_filter = ('category', 'is_active')


@admin.register(MediaPermission)
class MediaPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'media_type', 'root_dir')
    list_filter = ('language', 'media_type')
