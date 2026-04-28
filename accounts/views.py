from django.contrib.auth import authenticate
from rest_framework import exceptions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from common.responses import success_response

from .serializers import LoginSerializer, MeSerializer, RegisterSerializer


def _tokens_for(user) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {"access_token": str(refresh.access_token), "refresh_token": str(refresh)}


class RegisterView(APIView):
    """POST /api/accounts/register/ → returns tokens only."""

    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(
            data=_tokens_for(user),
            message="Account registered successfully",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/accounts/login/ → returns tokens only."""

    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if not user:
            raise exceptions.AuthenticationFailed("Invalid email or password")

        return success_response(data=_tokens_for(user), message="Logged in successfully")


class MeView(APIView):
    """POST /api/accounts/me/ → returns the current user's profile."""

    http_method_names = ["post"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MeSerializer(request.user)
        return success_response(data=serializer.data, message="Profile fetched successfully")
