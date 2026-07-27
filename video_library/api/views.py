from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from video_library.api.serializers import VideoSerializer
from video_library.models import Video


class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
