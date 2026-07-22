from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CookieTokenRefreshViewTests(APITestCase):
    """Tests for POST /api/token/refresh/ (accounts.api.views.CookieTokenRefreshView)."""

    def setUp(self):
        self.url = reverse("token_refresh")
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password="StrongPassword123",
        )
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_refresh_success_sets_new_access_cookie(self):
        """Valid refresh cookie returns 200 and sets a new access token cookie."""

        self.client.cookies["refresh_token"] = str(self.refresh_token)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)

    def test_refresh_fails_without_cookie(self):
        """Missing refresh cookie fails with 400."""

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_fails_with_invalid_token(self):
        """Malformed refresh token fails with 401."""

        self.client.cookies["refresh_token"] = "not-a-valid-token"

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
