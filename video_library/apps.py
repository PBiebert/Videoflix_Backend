from django.apps import AppConfig


class VideoLibraryConfig(AppConfig):
    name = "video_library"

    def ready(self):
        import video_library.signals
