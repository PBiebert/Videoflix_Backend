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
    """
    Computes the HLS output directory of a video for a given resolution.

    Args:
        video: The Video object whose video_file is used as the base.
        resolution: Resolution, e.g. "480p" (must be in ALLOWED_RESOLUTIONS).

    Returns:
        Path to the directory containing index.m3u8 and the .ts segments.

    Raises:
        NotFound: If resolution is not in ALLOWED_RESOLUTIONS.
    """
    if resolution not in ALLOWED_RESOLUTIONS:
        raise NotFound("Unknown resolution")

    source_path = Path(video.video_file.path)
    hls_dir = source_path.parent / f"{source_path.stem}_{resolution}"
    return hls_dir


class VideoListView(ListAPIView):
    """Lists all videos in the video library."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]


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
            open(playlist_path, "rb"), "Content-Type: application/vnd.apple.mpegurl"
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

        return FileResponse(open(segment_path, "rb"), "Content-Type: video/MP2T")
