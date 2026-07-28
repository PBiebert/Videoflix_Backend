from django.urls import path

from video_library.api.views import HLSPlaylistView, HLSSegmentView, VideoListView

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video-list"),
    path(
        "video/<int:movie_id>/<str:resolution>/index.m3u8",
        HLSPlaylistView.as_view(),
        name="video-stream",
    ),
    path(
        "video/<int:movie_id>/<str:resolution>/<str:segment>/",
        HLSSegmentView.as_view(),
        name="video-stream-segment",
    ),
]
