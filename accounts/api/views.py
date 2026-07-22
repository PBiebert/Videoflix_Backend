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
)
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.api.serializers import RegistrationSerializer
from accounts.api.services import send_activation_email
from accounts.api.token_helpers import set_tokens_as_cookies

from .serializers import CookieTokenObtainPairSerializer

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
        activation_url = request.build_absolute_uri(f"/api/activate/{uidb64}/{token}/")
        django_rq.enqueue(send_activation_email, user, activation_url)

        return Response(
            {"user": {"id": user.id, "email": user.email}, "token": token},
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
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {
                    "message": "Activation failed, please try again later or contact support."
                },
                status=HTTP_400_BAD_REQUEST,
            )

        token = kwargs.get("token")
        is_valid = default_token_generator.check_token(user, token)

        if user.is_active:
            return Response(
                {"message": "Account is already activated."},
                status=HTTP_400_BAD_REQUEST,
            )

        if is_valid:
            user.is_active = True
            user.save()
        else:
            return Response(
                {
                    "message": "Activation failed, please try again later or contact support."
                },
                status=HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Account successfully activated."}, status=HTTP_200_OK
        )


class LoginView(TokenObtainPairView):
    """Login view that returns access/refresh tokens as HttpOnly cookies
    instead of in the response body."""

    serializer_class = CookieTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Validates the credentials and sets the generated tokens as
        HttpOnly cookies instead of exposing them in the response body."""

        # Credentials validieren, Tokens + Userdaten erzeugen lassen
        response = super().post(request, *args, **kwargs)

        # Tokens und Userdaten aus der Standard-Response herausholen
        access = response.data.get("access")
        refresh = response.data.get("refresh")
        user = response.data.get("user")

        # Tokens als HttpOnly-Cookies setzen statt sie im Body preiszugeben
        set_tokens_as_cookies(response, {"access": access, "refresh": refresh})

        # Body auf eine saubere Erfolgsmeldung + Userdaten reduzieren
        response.data = {"detail": "Login successful", "user": user}
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
