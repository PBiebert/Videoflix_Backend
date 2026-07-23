from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticates requests via the access token in the HttpOnly cookie
    instead of the Authorization header."""

    def authenticate(self, request):
        """Reads and validates the access token from the `access_token` cookie.

        Returns:
            A (user, validated_token) tuple for a valid token, otherwise
            None (no or invalid cookie -> request stays unauthenticated).
        """

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            return None
