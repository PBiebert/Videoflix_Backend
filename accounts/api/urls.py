from django.urls import path

from accounts.api.views import (
    ActivateAccountView,
    CookieTokenRefreshView,
    LoginView,
    LogoutView,
    PasswortResetView,
    RegisterView,
    SetNewPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate_account",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_reset/", PasswortResetView.as_view(), name="password_reset"),
    path(
        "password_confirm/<uidb64>/<token>/",
        SetNewPasswordView.as_view(),
        name="set_new_password",
    ),
]
