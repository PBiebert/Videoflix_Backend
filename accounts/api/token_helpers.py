from django.conf import settings


def set_tokens_as_cookies(response, tokens):
    """Sets the access and refresh tokens as HttpOnly cookies on the response.

    Args:
        response: DRF response object the cookies are set on.
        tokens: Dictionary with the keys "access" and "refresh".
    """

    response.set_cookie(
        key="access_token",
        value=tokens["access"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )
