import subprocess
from pathlib import Path


def convert_video(source, quality):
    path = Path(source)
    new_file_name = str(path.with_name(f"{path.stem}_{quality}p.mp4"))
    cmd = [
        "ffmpeg",
        "-i",
        source,
        "-vf",
        f"scale=-2:{quality}",
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
        "-movflags",
        "+faststart",
        new_file_name,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Fehler bei der Videokonvertierung: {result.stderr}")
