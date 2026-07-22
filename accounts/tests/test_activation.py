from django.contrib.auth import get_user_model
from django.contrib.auth.forms import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ActivateAccountViewTests(APITestCase):
    """Tests for GET /api/activate/<uidb64>/<token>/ (accounts.api.views.ActivateAccountView)."""

    def setUp(self):
        """Set up the test case with an inactive user and a valid activation token."""

        self.user = User.objects.create_user(
            username="inactive@example.com",
            email="inactive@example.com",
            password="StrongPassword123",
            is_active=False,
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def _activation_url(self, uidb64, token):
        return reverse("activate_account", kwargs={"uidb64": uidb64, "token": token})

    def test_get_activate_valid_token_return_200(self):
        """Test that activating with a valid uidb64/token pair returns a 200 response and activates the user."""

        response = self.client.get(self._activation_url(self.uidb64, self.token))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)

    def test_get_activate_invalid_token_return_400(self):
        """Test that activating with an invalid token returns a 400 response and leaves the user inactive."""

        response = self.client.get(self._activation_url(self.uidb64, "invalid-token"))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)

    def test_get_activate_malformed_uidb64_return_400(self):
        """Test that activating with a malformed uidb64 returns a 400 response instead of a 500 error."""

        response = self.client.get(self._activation_url("not-valid-base64", self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_activate_nonexistent_user_return_400(self):
        """Test that activating a syntactically valid uidb64 with no matching user returns a 400 response."""

        nonexistent_uidb64 = urlsafe_base64_encode(force_bytes(99))

        response = self.client.get(self._activation_url(nonexistent_uidb64, self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_activate_reused_token_return_400(self):
        """
        Test that reusing the same token after a successful activation returns a 400 response,
        because the changed user state (is_active) is part of the token hash.
        """

        self.client.get(self._activation_url(self.uidb64, self.token))

        response = self.client.get(self._activation_url(self.uidb64, self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
