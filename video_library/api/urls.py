from django.urls import path

from video_library.api.views import VideoListView

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video-list"),
]
