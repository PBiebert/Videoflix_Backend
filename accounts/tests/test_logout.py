from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

User = get_user_model()


class LogoutViewTests(APITestCase):
    """Tests for POST /api/logout/ (accounts.api.views.LogoutView)."""

    def setUp(self):
        """Set up the test case with a valid, active user."""

        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.password = "StrongPassword123"
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password=self.password,
        )

    def test_post_logout_blacklists_refresh_token(self):
        """Test that logout adds the refresh token to the blacklist table."""

        login_response = self.client.post(
            self.login_url, {"email": self.user.email, "password": self.password}
        )
        refresh_token = login_response.cookies["refresh_token"].value

        self.client.post(self.logout_url)

        outstanding = OutstandingToken.objects.get(token=refresh_token)
        self.assertTrue(BlacklistedToken.objects.filter(token=outstanding).exists())

    def test_post_token_refresh_with_blacklisted_token_return_401(self):
        """Test that a blacklisted refresh token can no longer be used to obtain a new access token."""

        login_response = self.client.post(
            self.login_url, {"email": self.user.email, "password": self.password}
        )
        refresh_token = login_response.cookies["refresh_token"].value

        self.client.post(self.logout_url)

        self.client.cookies["refresh_token"] = refresh_token
        response = self.client.post(reverse("token_refresh"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
