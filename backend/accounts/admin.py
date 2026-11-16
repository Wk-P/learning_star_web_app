from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AppUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('其他', {'fields': ('display_name',)}),)
    list_display = ('id', 'username', 'display_name', 'email', 'is_staff', 'is_active')
