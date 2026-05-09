from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("CodeArena profile", {"fields": ("display_name", "bio", "preferred_language")}),
    )
    list_display = ("username", "email", "display_name", "preferred_language", "is_staff")
