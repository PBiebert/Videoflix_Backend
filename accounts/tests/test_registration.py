from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterViewTests(APITestCase):
    """Tests for POST /api/register/ (accounts.api.views.RegisterView)."""

    def setUp(self):
        """Set up the test case with valid registration data."""

        self.url = reverse("register")
        self.user_data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123",
            "confirmed_password": "StrongPassword123",
        }

    def test_post_register_valid_data_return_201(self):
        """Test that a successful registration creates an inactive user and returns a 201 response."""

        response = self.client.post(self.url, self.user_data)
        user = User.objects.get(email=self.user_data["email"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(user.is_active)
        self.assertIn("token", response.data)

    def test_post_register_password_mismatch_return_400(self):
        """Test that registering with mismatching passwords returns a 400 response."""

        invalid_user_data = {**self.user_data, "confirmed_password": "SomethingElse123"}
        response = self.client.post(self.url, invalid_user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=invalid_user_data["email"]).exists())

    def test_post_register_duplicate_email_return_400(self):
        """Test that registering with an already existing email returns a 400 response."""

        User.objects.create_user(
            username=self.user_data["email"],
            email=self.user_data["email"],
            password="whatever123",
        )

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_register_missing_fields_return_400(self):
        """Test that registering without the required fields returns a 400 response."""

        response = self.client.post(self.url, {"email": "incomplete@example.com"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
