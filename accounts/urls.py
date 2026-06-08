from django.urls import path

from .views import LoginView, MeView, RefreshTokenView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="accounts-register"),
    path("login/", LoginView.as_view(), name="accounts-login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="accounts-token-refresh"),
    path("me/", MeView.as_view(), name="accounts-me"),
]
