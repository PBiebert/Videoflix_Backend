from django.conf import settings


def set_tokens_as_cookies(response, tokens):
    """Setzt die Access- und Refresh-Token als HttpOnly-Cookies im Response-Objekt.

    Args:
        response: DRF-Response-Objekt, auf dem die Cookies gesetzt werden.
        tokens: Dictionary mit den Schlüsseln "access" und "refresh".
    """

    # Access-Token als HttpOnly-Cookie setzen
    response.set_cookie(
        key="access_token",
        value=tokens["access"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )

    # Refresh-Token als HttpOnly-Cookie setzen
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )
