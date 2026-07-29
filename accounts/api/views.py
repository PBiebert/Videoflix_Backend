import django_rq
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.api.serializers import RegistrationSerializer
from accounts.api.services import send_activation_email, send_password_reset_email
from accounts.api.token_helpers import set_tokens_as_cookies

from .serializers import CheckPasswordSerializer

User = get_user_model()


class RegisterView(APIView):
    """Registers a new, initially inactive user and triggers the activation email."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validates the registration data, creates the user, builds a signed
        activation link, and sends it asynchronously via email.
        """

        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={token}"
        django_rq.enqueue(send_activation_email, user, activation_url)

        return Response(
            {"user": {"id": user.id, "email": user.email}},
            status=HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    """Activates a user based on the uidb64/token pair from the activation link."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Decodes the user ID from uidb64, checks the token against the current
        user state, and sets is_active=True on success.
        """

        try:
            uid = force_str(urlsafe_base64_decode(kwargs.get("uidb64")))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {
                    "message": "Activation failed, please try again later or contact support."
                },
                status=HTTP_400_BAD_REQUEST,
            )

        token = kwargs.get("token")
        is_valid = default_token_generator.check_token(user, token)

        if not is_valid:
            return Response(
                {
                    "message": "Activation failed, please try again later or contact support."
                },
                status=HTTP_400_BAD_REQUEST,
            )

        if user.is_active:
            return Response(
                {"message": "Account is already activated."},
                status=HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        return Response(
            {"message": "Account successfully activated."}, status=HTTP_200_OK
        )


class LoginView(TokenObtainPairView):
    """Login view that returns access/refresh tokens as HttpOnly cookies
    instead of in the response body."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Validates the credentials and sets the generated tokens as
        HttpOnly cookies instead of exposing them in the response body."""

        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")

        set_tokens_as_cookies(response, {"access": access, "refresh": refresh})

        response.data = {"detail": "Login successful"}
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh view that reads the refresh token from the HttpOnly cookie
    instead of the request body and returns the new access token as a
    cookie again."""

    def post(self, request, *args, **kwargs):
        """Validates the refresh token from the cookie and sets the new
        access token as an HttpOnly cookie."""

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, ValidationError):
            return Response(
                {"detail": "Refresh token is invalid!"},
                status=HTTP_401_UNAUTHORIZED,
            )
        access_token = serializer.validated_data.get("access")

        response = Response({"detail": "Access-Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )
        return response


class LogoutView(APIView):
    """Logs the user out by blacklisting the refresh token and deleting both token cookies."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Blacklists the refresh token from the cookie and deletes both auth cookies."""

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Refresh token is invalid!"},
                status=HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {
                "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
            }
        )

        response.delete_cookie("access_token", samesite="Lax")
        response.delete_cookie("refresh_token", samesite="Lax")

        return response


class PasswortResetView(APIView):
    """Sends a password-reset email to the user matching the given email."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Looks up the user by email and sends a password-reset email if one exists;
        returns 404 if the user is unknown.
        """

        email = request.data.get("email")

        try:
            user = User.objects.get(email=email, is_active=True)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
        django_rq.enqueue(send_password_reset_email, user, reset_url)

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=HTTP_200_OK,
        )


class SetNewPasswordView(APIView):
    """Sets a new password for the user identified by uidb64, after validating the reset token."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Decodes the user ID from uidb64, checks the token and active state,
        and sets the new password from the request body on success.
        """

        try:
            uid = force_str(urlsafe_base64_decode(kwargs.get("uidb64")))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)

        token = kwargs.get("token")
        token_is_valid = default_token_generator.check_token(user, token)

        if token_is_valid and user.is_active:
            serializer = CheckPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response(
                {"detail": "Your Password has been successfully reset."},
                status=HTTP_200_OK,
            )

        return Response(
            {"detail": "The link is invalid"},
            status=HTTP_400_BAD_REQUEST,
        )
