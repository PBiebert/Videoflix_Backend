from pathlib import Path

from rest_framework.exceptions import NotFound

from video_library.signals import VIDEO_RESOLUTIONS


def get_hls_directory_path(video, resolution):
    """
    Computes the HLS output directory of a video for a given resolution.

    Args:
        video: The Video object whose video_file is used as the base.
        resolution: Resolution, e.g. "480p" (must be in VIDEO_RESOLUTIONS).

    Returns:
        Path to the directory containing index.m3u8 and the .ts segments.

    Raises:
        NotFound: If resolution is not in VIDEO_RESOLUTIONS.
    """
    if resolution not in VIDEO_RESOLUTIONS:
        raise NotFound("Unknown resolution")

    source_path = Path(video.video_file.path)
    hls_dir = source_path.parent / f"{source_path.stem}_{resolution}"
    return hls_dir
