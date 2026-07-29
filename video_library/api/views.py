from django.core.cache import cache
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from video_library.api.serializers import VideoSerializer
from video_library.models import Video
from video_library.storage import get_hls_directory_path


class VideoListView(ListAPIView):
    """Lists all videos in the video library."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cached_data = cache.get("video_list")
        if cached_data is not None:
            return cached_data
        response = super().list(request, *args, **kwargs)
        cache.set("video_list", response, 60 * 15)
        return response


class HLSPlaylistView(APIView):
    """Serves the HLS playlist (index.m3u8) of a video for a resolution."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Returns the index.m3u8 file for the requested video/resolution.

        Args:
            movie_id: Primary key of the Video object (from the URL).
            resolution: Requested resolution, e.g. "480p" (from the URL).

        Raises:
            Http404: If the video does not exist.
            NotFound: If the resolution is invalid or the playlist file
                does not exist.
        """
        video_id = kwargs.get("movie_id")
        resolution = kwargs.get("resolution")
        video = get_object_or_404(Video, id=video_id)
        playlist_path = get_hls_directory_path(video, resolution) / "index.m3u8"

        if not playlist_path.is_file():
            raise NotFound("Playlist not found")

        return FileResponse(
            open(playlist_path, "rb"),
            content_type="application/vnd.apple.mpegurl",
        )


class HLSSegmentView(APIView):
    """Serves a single HLS segment (.ts file) of a video."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Returns a single .ts segment file of the requested video.

        Args:
            movie_id: Primary key of the Video object (from the URL).
            resolution: Requested resolution, e.g. "480p" (from the URL).
            segment: Segment file name, e.g. "segment_00000.ts"
                (from the URL).

        Raises:
            Http404: If the video does not exist.
            NotFound: If the resolution is invalid, the segment name
                contains path traversal, or the file does not exist.
        """
        video_id = kwargs.get("movie_id")
        resolution = kwargs.get("resolution")
        segment = kwargs.get("segment")
        video = get_object_or_404(Video, id=video_id)
        segment_path = get_hls_directory_path(video, resolution) / segment

        if segment_path.name != segment or not segment_path.is_file():
            raise NotFound("Segment not found")

        return FileResponse(open(segment_path, "rb"), content_type="video/MP2T")
