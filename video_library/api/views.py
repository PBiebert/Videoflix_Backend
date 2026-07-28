from pathlib import Path

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from video_library.api.serializers import VideoSerializer
from video_library.models import Video

ALLOWED_RESOLUTIONS = ["480p", "720p", "1080p"]


def get_hls_directory_path(video, resolution):
    if resolution not in ALLOWED_RESOLUTIONS:
        raise NotFound("Unknown resolution")

    source_path = Path(video.video_file.path)
    hls_dir = source_path.parent / f"{source_path.stem}_{resolution}"
    return hls_dir


class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]


class HLSPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        video_id = kwargs.get("movie_id")
        resolution = kwargs.get("resolution")
        video = get_object_or_404(Video, id=video_id)
        playlist_path = get_hls_directory_path(video, resolution) / "index.m3u8"

        if not playlist_path.is_file():
            raise NotFound("Playlist not found")

        return FileResponse(open(playlist_path, "rb"))
