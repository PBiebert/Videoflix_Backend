import os

import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from video_library.models import Video
from video_library.tasks import convert_video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        QUALITYS = ["480", "720", "1080"]
        for quality in QUALITYS:
            queue = django_rq.get_queue("default")
            queue.enqueue(convert_video, instance.video_file.path, quality)


@receiver(post_delete, sender=Video)
def auto_delete_video_file(sender, instance, **kwargs):
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            print(f"Video-Datei gelöscht: {instance.video_file.path}")
