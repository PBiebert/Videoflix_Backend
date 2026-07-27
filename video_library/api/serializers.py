from rest_framework import serializers

from video_library.models import Video


class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.ImageField(source="thumbnail", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "description",
            "thumbnail_url",
            "created_at",
            "category",
        ]
