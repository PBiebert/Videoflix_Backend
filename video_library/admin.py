from django.contrib import admin

from video_library.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "category"]
