from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from video_library.models import Video

User = get_user_model()


def create_video(**kwargs):
    """Helper to create a Video instance with placeholder thumbnail/video_file content."""

    defaults = {
        "title": "Test Video",
        "description": "Test Description",
        "category": "Drama",
        "thumbnail": "thumbnails/placeholder.png",
        "video_file": "videos/placeholder.mp4",
    }
    defaults.update(kwargs)
    return Video.objects.create(**defaults)


class VideoListViewTests(APITestCase):
    """Tests for GET /api/video/ (video_library.api.views.VideoListView)."""

    def setUp(self):
        """Set up the test case with a valid, active user."""

        self.url = reverse("video-list")
        self.login_url = reverse("login")
        self.password = "StrongPassword123"
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password=self.password,
        )

    def login(self):
        """Log in via the login endpoint so auth cookies are set on self.client."""

        self.client.post(
            self.login_url, {"email": self.user.email, "password": self.password}
        )

    def test_get_video_list_unauthenticated_return_401(self):
        """Test that an unauthenticated request is rejected with 401."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_video_list_authenticated_return_200(self):
        """Test that an authenticated request returns 200."""

        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video_list_authenticated_with_videos_return_200(self):
        """Test that an authenticated request returns 200 and all created videos."""

        self.login()
        create_video()
        create_video(title="Second Video")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
