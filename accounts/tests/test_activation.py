from django.contrib.auth import get_user_model
from django.contrib.auth.forms import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ActivateAccountViewTests(APITestCase):
    """Tests für GET /api/activate/<uidb64>/<token>/ (accounts.api.views.ActivateAccountView)."""

    def setUp(self):
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

    def test_activation_success_activates_user(self):
        """Gültiges uidb64/token-Paar aktiviert den User und liefert 200."""

        response = self.client.get(self._activation_url(self.uidb64, self.token))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)

    def test_activation_fails_with_invalid_token(self):
        """Falscher Token schlägt mit 400 fehl, User bleibt inaktiv."""

        response = self.client.get(self._activation_url(self.uidb64, "invalid-token"))

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)

    def test_activation_fails_with_malformed_uidb64(self):
        """Kein gültiger Base64-String führt zu 400 statt zu einem 500er."""

        response = self.client.get(self._activation_url("not-valid-base64", self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activation_fails_for_nonexistent_user(self):
        """Syntaktisch gültiges uidb64 ohne passenden User führt zu 400."""

        nonexistent_uidb64 = urlsafe_base64_encode(force_bytes(99))

        response = self.client.get(self._activation_url(nonexistent_uidb64, self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activation_token_cannot_be_reused(self):
        """
        Nach erfolgreicher Aktivierung ist derselbe Token ungültig, weil sich
        der User-Zustand (is_active) geändert hat und in den Hash einfließt.
        """

        self.client.get(self._activation_url(self.uidb64, self.token))

        response = self.client.get(self._activation_url(self.uidb64, self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
