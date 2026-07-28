from django.urls import path

from video_library.api.views import HLSPlaylistView, VideoListView

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video-list"),
    path(
        "video/<int:movie_id>/<str:resolution>/index.m3u8",
        HLSPlaylistView.as_view(),
        name="video-stream",
    ),
]
