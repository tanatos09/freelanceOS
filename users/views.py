from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _token_pair(user) -> dict:
    """Vygeneruje access + refresh token pro daného uživatele."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# ─── Auth endpoints ───────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    POST /api/auth/register/
    Body: { email, password, password2 }
    Vrátí tokeny + info o uživateli.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        {
            "user": UserSerializer(user).data,
            **_token_pair(user),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/auth/login/
    Body: { email, password }
    Vrátí tokeny + info o uživateli.
    """
    from django.contrib.auth import authenticate

    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response(
            {"detail": "Email a heslo jsou povinné."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response(
            {"detail": "Neplatné přihlašovací údaje."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return Response(
        {
            "user": UserSerializer(user).data,
            **_token_pair(user),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    POST /api/auth/logout/
    Body: { refresh }
    Zneplatní refresh token (blacklist).
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response(
            {"detail": "Refresh token je povinný."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response(
            {"detail": "Neplatný nebo expirovaný token."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({"detail": "Odhlášení proběhlo úspěšně."}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """
    GET /api/auth/me/
    Vrátí info o přihlášeném uživateli.
    """
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    POST /api/auth/change-password/
    Body: { old_password, new_password }
    """
    serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    request.user.set_password(serializer.validated_data["new_password"])
    request.user.save()
    return Response({"detail": "Heslo bylo úspěšně změněno."})
