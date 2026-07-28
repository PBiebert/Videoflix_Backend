import subprocess
from pathlib import Path


def convert_video(source, quality):
    path = Path(source)
    output_dir = path.parent / f"{path.stem}_{quality}"
    output_dir.mkdir(parents=True, exist_ok=True)
    playlist_path = output_dir / "index.m3u8"

    height = quality.rstrip("p")
    cmd = [
        "ffmpeg",
        "-i",
        source,
        "-vf",
        f"scale=-2:{height}",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-hls_time",
        "10",
        "-hls_list_size",
        "0",
        "-hls_segment_filename",
        str(output_dir / "segment_%05d.ts"),
        "-f",
        "hls",
        str(playlist_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Fehler bei der Videokonvertierung: {result.stderr}")
