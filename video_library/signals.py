import os
import shutil
from pathlib import Path

import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from video_library.models import Video
from video_library.tasks import convert_video

VIDEO_QUALITYS = ["480", "720", "1080"]


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        for quality in VIDEO_QUALITYS:
            queue = django_rq.get_queue("default")
            queue.enqueue(convert_video, instance.video_file.path, quality)


@receiver(post_delete, sender=Video)
def auto_delete_video_file(sender, instance, **kwargs):
    if instance.video_file and os.path.isfile(instance.video_file.path):
        path = Path(instance.video_file.path)
        os.remove(instance.video_file.path)

        for quality in VIDEO_QUALITYS:
            output_dir = path.parent / f"{path.stem}_{quality}p"
            if output_dir.is_dir():
                shutil.rmtree(output_dir)
