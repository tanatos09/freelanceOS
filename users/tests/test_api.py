"""
Integrační testy pro API endpointy aplikace users.

Pokrývá:
- Registrace
- Přihlášení
- Odhlášení
- Změna hesla
- Refresh tokenů
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestAuthRegisterEndpoint:
    """Testy pro endpoint /api/v1/auth/register/"""

    def test_register_success(self, api_client, db):
        """Test: Úspěšná registrace."""
        data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password2": "securepass123",
        }
        response = api_client.post("/api/v1/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

    def test_register_returns_tokens(self, api_client, db):
        """Test: Registrace vrátí access a refresh tokeny."""
        data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password2": "securepass123",
        }
        response = api_client.post("/api/v1/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["access"]
        assert response.data["refresh"]
        assert len(response.data["access"]) > 0
        assert len(response.data["refresh"]) > 0

    def test_register_creates_user_profile(self, api_client, db):
        """Test: Registrace vytváří UserProfile."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password2": "securepass123",
        }
        api_client.post("/api/v1/auth/register/", data, format="json")
        user = User.objects.get(email="newuser@example.com")
        assert hasattr(user, "profile")

    def test_register_duplicate_email(self, api_client, user):
        """Test: Registrace s duplicitním emailem."""
        data = {"email": user.email, "password": "securepass123", "password2": "securepass123"}
        response = api_client.post("/api/v1/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_password_mismatch(self, api_client, db):
        """Test: Hesla se neshodují."""
        data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password2": "differentpass123",
        }
        response = api_client.post("/api/v1/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_register_weak_password(self, api_client, db):
        """Test: Slabé heslo."""
        data = {"email": "newuser@example.com", "password": "weak", "password2": "weak"}
        response = api_client.post("/api/v1/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_email(self, api_client, db):
        """Test: Chybí email."""
        data = {"password": "securepass123", "password2": "securepass123"}
        response = api_client.post("/api/v1/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_empty_email(self, api_client, db):
        """Test: Prázdný email."""
        data = {"email": "", "password": "securepass123", "password2": "securepass123"}
        response = api_client.post("/api/v1/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAuthLoginEndpoint:
    """Testy pro endpoint /api/v1/auth/login/"""

    def test_login_success(self, api_client, user):
        """Test: Úspěšné přihlášení."""
        data = {"email": "testuser@example.com", "password": "testpass123"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

    def test_login_returns_correct_user_info(self, api_client, user):
        """Test: Login vrátí správné údaje o uživateli."""
        data = {"email": "testuser@example.com", "password": "testpass123"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.data["user"]["email"] == user.email
        assert response.data["user"]["id"] == user.id

    def test_login_invalid_password(self, api_client, user):
        """Test: Špatné heslo."""
        data = {"email": "testuser@example.com", "password": "wrongpassword"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_non_existent_user(self, api_client, db):
        """Test: Přihlášení neexistujícího uživatele."""
        data = {"email": "nonexistent@example.com", "password": "testpass123"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_email(self, api_client, db):
        """Test: Chybí email."""
        data = {"password": "testpass123"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_password(self, api_client, db):
        """Test: Chybí heslo."""
        data = {"email": "test@example.com"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_case_insensitive_email(self, api_client, user):
        """Test: Login je case-insensitive pro email."""
        data = {"email": "TESTUSER@EXAMPLE.COM", "password": "testpass123"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_login_inactive_user(self, api_client, inactive_user):
        """Test: Přihlášení neaktivního uživatele."""
        data = {"email": "inactive@example.com", "password": "testpass123"}
        response = api_client.post("/api/v1/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthLogoutEndpoint:
    """Testy pro endpoint /api/v1/auth/logout/"""

    def test_logout_success(self, auth_client, refresh_token):
        """Test: Úspěšné odhlášení."""
        data = {"refresh": refresh_token}
        response = auth_client.post("/api/v1/auth/logout/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_logout_missing_refresh_token(self, auth_client):
        """Test: Chybí refresh token."""
        data = {}
        response = auth_client.post("/api/v1/auth/logout/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_invalid_token(self, auth_client):
        """Test: Neplatný refresh token."""
        data = {"refresh": "invalid.token.here"}
        response = auth_client.post("/api/v1/auth/logout/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_requires_authentication(self, api_client, refresh_token):
        """Test: Logout vyžaduje autentifikaci."""
        data = {"refresh": refresh_token}
        response = api_client.post("/api/v1/auth/logout/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_blacklists_token(self, auth_client, user, refresh_token):
        """Test: Token je po odhlášení zařazen na blacklist."""
        data = {"refresh": refresh_token}
        response = auth_client.post("/api/v1/auth/logout/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Pokus o refresh s blacklistovaným tokenem
        api_client = APIClient()
        refresh_response = api_client.post(
            "/api/v1/auth/token/refresh/", {"refresh": refresh_token}, format="json"
        )
        # by měl selhat (token je na blacklist)
        assert refresh_response.status_code != status.HTTP_200_OK


class TestAuthMeEndpoint:
    """Testy pro endpoint /api/v1/auth/me/"""

    def test_me_authenticated(self, auth_client, user):
        """Test: Autentifikovaný uživatel vidí své údaje."""
        response = auth_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_me_unauthenticated(self, api_client):
        """Test: Neautentifikovaný uživatel nemůže vidět /me/."""
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_returns_profile_data(self, auth_client, user):
        """Test: /me/ vrací data z profilu."""
        user.profile.timezone = "Europe/Prague"
        user.profile.locale = "en"
        user.profile.save()

        response = auth_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["timezone"] == "Europe/Prague"
        assert response.data["locale"] == "en"


class TestAuthChangePasswordEndpoint:
    """Testy pro endpoint /api/v1/auth/change-password/"""

    def test_change_password_success(self, auth_client, api_client, user):
        """Test: Úspěšná změna hesla."""
        data = {"old_password": "testpass123", "new_password": "newpass456"}
        response = auth_client.post("/api/v1/auth/change-password/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Ověř, že lze přihlásit s novým heslem
        login_response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "testuser@example.com", "password": "newpass456"},
            format="json",
        )
        assert login_response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_old_password(self, auth_client):
        """Test: Špatné staré heslo."""
        data = {"old_password": "wrongoldpass", "new_password": "newpass456"}
        response = auth_client.post("/api/v1/auth/change-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_weak_new_password(self, auth_client):
        """Test: Slabé nové heslo."""
        data = {"old_password": "testpass123", "new_password": "weak"}
        response = auth_client.post("/api/v1/auth/change-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_requires_authentication(self, api_client):
        """Test: Změna hesla vyžaduje autentifikaci."""
        data = {"old_password": "oldpass123", "new_password": "newpass456"}
        response = api_client.post("/api/v1/auth/change-password/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefreshEndpoint:
    """Testy pro endpoint /api/v1/auth/token/refresh/"""

    def test_token_refresh_success(self, api_client, refresh_token):
        """Test: Úspěšný refresh tokenu."""
        data = {"refresh": refresh_token}
        response = api_client.post("/api/v1/auth/token/refresh/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_token_refresh_invalid_token(self, api_client):
        """Test: Neplatný refresh token."""
        data = {"refresh": "invalid.token.here"}
        response = api_client.post("/api/v1/auth/token/refresh/", data, format="json")
        assert response.status_code != status.HTTP_200_OK

    def test_token_refresh_missing_token(self, api_client):
        """Test: Chybí refresh token."""
        data = {}
        response = api_client.post("/api/v1/auth/token/refresh/", data, format="json")
        assert response.status_code != status.HTTP_200_OK


class TestAuthIntegrationFlows:
    """Integrace: Kompletní toky a scénáře."""

    def test_complete_auth_flow(self, api_client, db):
        """Test: Úplný tok - registrace → přihlášení → odhlášení."""
        # 1. Registrace
        register_data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password2": "securepass123",
        }
        response = api_client.post("/api/v1/auth/register/", register_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        refresh_token = response.data["refresh"]
        access_token = response.data["access"]

        # 2. Ověř, že se lze přihlásit
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_response = api_client.get("/api/v1/auth/me/")
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.data["email"] == "newuser@example.com"

        # 3. Odhlášení
        logout_data = {"refresh": refresh_token}
        logout_response = api_client.post("/api/v1/auth/logout/", logout_data, format="json")
        assert logout_response.status_code == status.HTTP_200_OK

    def test_login_change_password_relogin_flow(self, api_client, user):
        """Test: Přihlášení → změna hesla → opět přihlášení."""
        # 1. Přihlaš se
        login_data = {"email": "testuser@example.com", "password": "testpass123"}
        response = api_client.post("/api/v1/auth/login/", login_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        access_token = response.data["access"]

        # 2. Změň heslo
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        change_data = {"old_password": "testpass123", "new_password": "newpass456"}
        response = api_client.post("/api/v1/auth/change-password/", change_data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # 3. Zkus přihlásit s novým heslem
        api_client.credentials()
        login_response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "testuser@example.com", "password": "newpass456"},
            format="json",
        )
        assert login_response.status_code == status.HTTP_200_OK

    def test_token_refresh_flow(self, api_client, user):
        """Test: Použití refresh tokenu k získání nového access tokenu."""
        # 1. Přihlaš se
        login_response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "testuser@example.com", "password": "testpass123"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        # 2. Refresh token
        refresh_response = api_client.post(
            "/api/v1/auth/token/refresh/", {"refresh": refresh_token}, format="json"
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        new_access_token = refresh_response.data["access"]

        # 3. Použij nový access token
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        me_response = api_client.get("/api/v1/auth/me/")
        assert me_response.status_code == status.HTTP_200_OK
