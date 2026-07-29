import os
import shutil
from pathlib import Path

import django_rq
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from video_library.models import Video
from video_library.tasks import convert_video

VIDEO_RESOLUTIONS = ["480p", "720p", "1080p"]


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        for quality in VIDEO_RESOLUTIONS:
            queue = django_rq.get_queue("default")
            queue.enqueue(convert_video, instance.video_file.path, quality)


@receiver(post_delete, sender=Video)
def auto_delete_video_file(sender, instance, **kwargs):
    if instance.video_file and os.path.isfile(instance.video_file.path):
        path = Path(instance.video_file.path)
        os.remove(instance.video_file.path)

        for quality in VIDEO_RESOLUTIONS:
            output_dir = path.parent / f"{path.stem}_{quality}"
            if output_dir.is_dir():
                shutil.rmtree(output_dir)


@receiver(post_delete, sender=Video)
def auto_delete_thumbnail_file(sender, instance, **kwargs):
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)


@receiver(post_save, sender=Video)
@receiver(post_delete, sender=Video)
def invalidate_video_list_cache(sender, instance, **kwargs):
    cache.delete("video_list")
