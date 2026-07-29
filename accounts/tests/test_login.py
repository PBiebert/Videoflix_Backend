from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class LoginViewTests(APITestCase):
    """Tests for POST /api/login/ (accounts.api.views.LoginView)."""

    def setUp(self):
        """Set up the test case with a valid, active user."""

        self.url = reverse("login")
        self.password = "StrongPassword123"
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password=self.password,
        )

    def test_post_login_valid_credentials_return_200(self):
        """Test that a successful login returns a 200 response and sets access/refresh cookies."""

        response = self.client.post(
            self.url, {"email": self.user.email, "password": self.password}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_post_login_valid_credentials_return_detail_message(self):
        """Test that a successful login returns a detail message and no token data in the body."""

        response = self.client.post(
            self.url, {"email": self.user.email, "password": self.password}
        )

        self.assertEqual(response.data, {"detail": "Login successful"})

    def test_post_login_wrong_password_return_401(self):
        """Test that a login with the wrong password returns a 401 response and sets no cookies."""

        response = self.client.post(
            self.url, {"email": self.user.email, "password": "WrongPassword123"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", response.cookies)

    def test_post_login_nonexistent_user_return_401(self):
        """Test that a login with an unknown email returns a 401 response."""

        response = self.client.post(
            self.url,
            {"email": "unknown@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_login_inactive_user_return_401(self):
        """Test that a login with a not-yet-activated user returns a 401 response."""

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

    def test_post_login_missing_fields_return_400(self):
        """Test that a login without a password returns a 400 response."""

        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
