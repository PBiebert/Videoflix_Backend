from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class LoginViewTests(APITestCase):
    """Tests for POST /api/login/ (accounts.api.views.LoginView)."""

    def setUp(self):
        self.url = reverse("token_obtain_pair")
        self.password = "StrongPassword123"
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password=self.password,
        )

    def test_login_success_sets_cookies_and_hides_tokens_from_body(self):
        """Successful login returns 200 and sets access/refresh cookies."""

        response = self.client.post(
            self.url, {"email": self.user.email, "password": self.password}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_success_returns_user_data_in_body(self):
        """Successful login includes the user data in the response body."""

        response = self.client.post(
            self.url, {"email": self.user.email, "password": self.password}
        )

        self.assertEqual(response.data["user"]["id"], self.user.id)

    def test_login_fails_with_wrong_password(self):
        """Wrong password fails with 401, no cookies are set."""

        response = self.client.post(
            self.url, {"email": self.user.email, "password": "WrongPassword123"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", response.cookies)

    def test_login_fails_for_nonexistent_user(self):
        """Login with an unknown email fails with 401."""

        response = self.client.post(
            self.url,
            {"email": "unknown@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_fails_for_inactive_user(self):
        """Login with a not-yet-activated user fails with 401."""

        User.objects.create_user(
            username="inactive@example.com",
            email="inactive@example.com",
            password=self.password,
            is_active=False,
        )

        response = self.client.post(
            self.url,
            {"email": "inactive@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_fails_on_missing_fields(self):
        """Login without a password fails with 400."""

        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
