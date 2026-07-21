from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterViewTests(APITestCase):
    """Tests für POST /api/register/ (accounts.api.views.RegisterView)."""

    def setUp(self):
        self.url = reverse("register")
        self.user_data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123",
            "confirmed_password": "StrongPassword123",
        }

    def test_register_success_creates_inactive_user(self):
        """Erfolgreiche Registrierung erzeugt einen inaktiven User und gibt 201 zurück."""

        response = self.client.post(self.url, self.user_data)
        user = User.objects.get(email=self.user_data["email"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(user.is_active)
        self.assertIn("token", response.data)

    def test_register_fails_on_password_mismatch(self):
        """Registrierung schlägt fehl, wenn Passwörter nicht übereinstimmen."""

        invalid_user_data = {**self.user_data, "confirmed_password": "SomethingElse123"}
        response = self.client.post(self.url, invalid_user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=invalid_user_data["email"]).exists())

    def test_register_fails_on_duplicate_email(self):
        """Registrierung schlägt fehl, wenn die E-Mail bereits existiert."""

        User.objects.create_user(
            username=self.user_data["email"],
            email=self.user_data["email"],
            password="whatever123",
        )

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_fails_on_missing_fields(self):
        """Registrierung schlägt fehl, wenn erforderliche Felder fehlen."""

        response = self.client.post(self.url, {"email": "incomplete@example.com"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
