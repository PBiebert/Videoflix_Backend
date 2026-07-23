from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "confirmed_password"]

    def validate_email(self, value):
        """Validate that the email is unique and not already in use."""

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address already exists.")
        return value

    def validate(self, data):
        """Validate that the password and repeated password match."""

        if data["password"] != data.pop("confirmed_password"):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        """Create a new user instance."""

        user = User.objects.create_user(
            **validated_data, username=validated_data["email"], is_active=False
        )
        return user


class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login serializer that generates access/refresh tokens as usual, but
    also includes the authenticated user's data in the validated result."""

    def validate(self, data):
        """Validates the credentials and enriches the result with user data."""

        data = super().validate(data)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.email,
        }
        return data


class CheckPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate that the password and repeated password match."""

        if data["new_password"] != data.pop("confirm_password"):
            raise serializers.ValidationError("Passwords do not match")
        return data
