from django.db import models


class Video(models.Model):
    """
    Model für Videos in der Video-Bibliothek.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    category = models.CharField(max_length=100)
    video_file = models.FileField(upload_to="videos/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
