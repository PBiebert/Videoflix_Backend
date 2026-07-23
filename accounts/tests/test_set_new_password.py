from django.contrib.auth import get_user_model
from django.contrib.auth.forms import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class SetNewPasswordViewTests(APITestCase):
    """Tests for POST /api/password_confirm/<uidb64>/<token>/ (accounts.api.views.SetNewPasswordView)."""

    def setUp(self):
        """Set up the test case with a valid, active user and a matching uidb64/token pair."""

        self.password = "StrongPassword123"
        self.user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password=self.password,
            is_active=True,
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def _confirm_url(self, uidb64, token):
        return reverse("set_new_password", kwargs={"uidb64": uidb64, "token": token})

    def test_post_set_new_password_valid_token_return_200(self):
        """Test that a valid uidb64/token pair with matching passwords returns a 200 response and sets the new password."""

        response = self.client.post(
            self._confirm_url(self.uidb64, self.token),
            {
                "new_password": "NewStrongPassword456",
                "confirm_password": "NewStrongPassword456",
            },
        )

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password("NewStrongPassword456"))

    def test_post_set_new_password_invalid_token_return_400(self):
        """Test that an invalid token returns a 400 response and leaves the password unchanged."""

        response = self.client.post(
            self._confirm_url(self.uidb64, "invalid-token"),
            {
                "new_password": "NewStrongPassword456",
                "confirm_password": "NewStrongPassword456",
            },
        )

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.user.check_password(self.password))

    def test_post_set_new_password_malformed_uidb64_return_404(self):
        """Test that a malformed uidb64 returns a 404 response instead of a 500 error."""

        response = self.client.post(
            self._confirm_url("not-valid-base64", self.token),
            {
                "new_password": "NewStrongPassword456",
                "confirm_password": "NewStrongPassword456",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_set_new_password_nonexistent_user_return_404(self):
        """Test that a syntactically valid uidb64 with no matching user returns a 404 response."""

        nonexistent_uidb64 = urlsafe_base64_encode(force_bytes(99))

        response = self.client.post(
            self._confirm_url(nonexistent_uidb64, self.token),
            {
                "new_password": "NewStrongPassword456",
                "confirm_password": "NewStrongPassword456",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_set_new_password_inactive_user_return_400(self):
        """Test that a valid token for an inactive user returns a 400 response."""

        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self._confirm_url(self.uidb64, self.token),
            {
                "new_password": "NewStrongPassword456",
                "confirm_password": "NewStrongPassword456",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_set_new_password_mismatch_return_400(self):
        """Test that mismatching new_password/confirm_password values return a 400 response."""

        response = self.client.post(
            self._confirm_url(self.uidb64, self.token),
            {
                "new_password": "NewStrongPassword456",
                "confirm_password": "SomethingElse789",
            },
        )

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.user.check_password(self.password))
