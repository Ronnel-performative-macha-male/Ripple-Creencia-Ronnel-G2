from django.contrib import admin

from .models import Rant


@admin.register(Rant)
class RantAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "mood", "is_anonymous", "created_at")
    list_filter = ("is_anonymous", "mood")
    search_fields = ("content", "author__username")
