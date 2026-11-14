from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Tag, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role", "is_staff")
    filter_horizontal = UserAdmin.filter_horizontal + ("tags",)
    fieldsets = UserAdmin.fieldsets + (
        ("Ripple", {"fields": ("role", "bio", "tags")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Ripple", {"fields": ("email", "role")}),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "kind")
    list_filter = ("kind",)