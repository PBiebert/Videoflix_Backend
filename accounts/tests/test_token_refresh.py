from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CookieTokenRefreshViewTests(APITestCase):
    """Tests for POST /api/token/refresh/ (accounts.api.views.CookieTokenRefreshView)."""

    def setUp(self):
        """Set up the test case with a valid user and a matching refresh token."""

        self.url = reverse("token_refresh")
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password="StrongPassword123",
        )
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_post_token_refresh_valid_cookie_return_200(self):
        """Test that a valid refresh cookie returns a 200 response and sets a new access token cookie."""

        self.client.cookies["refresh_token"] = str(self.refresh_token)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)

    def test_post_token_refresh_missing_cookie_return_400(self):
        """Test that a missing refresh cookie returns a 400 response."""

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_token_refresh_invalid_token_return_401(self):
        """Test that a malformed refresh token returns a 401 response."""

        self.client.cookies["refresh_token"] = "not-a-valid-token"

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
