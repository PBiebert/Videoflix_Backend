from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PasswordResetViewTests(APITestCase):
    """Tests for POST /api/password_reset/ (accounts.api.views.PasswortResetView)."""

    def setUp(self):
        """Set up the test case with a valid, active user."""

        self.url = reverse("password_reset")
        self.password = "StrongPassword123"
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password=self.password,
        )

    def test_post_password_reset_active_user_return_200(self):
        """Test that a password reset request for an active user returns a 200 response."""

        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_password_reset_unknown_email_return_404(self):
        """Test that a password reset request for an unknown email returns a 404 response."""

        response = self.client.post(self.url, {"email": "unknown@example.com"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_password_reset_inactive_user_return_404(self):
        """Test that a password reset request for a not-yet-activated user returns a 404 response."""

        User.objects.create_user(
            username="inactive@example.com",
            email="inactive@example.com",
            password=self.password,
            is_active=False,
        )

        response = self.client.post(self.url, {"email": "inactive@example.com"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_password_reset_missing_email_return_404(self):
        """Test that a password reset request without an email returns a 404 response."""

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
