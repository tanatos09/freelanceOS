"""
Helper funkce a utilities pro testování.
"""
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


def create_authenticated_client(user):
    """Vytvoří autentifikovaného APIClient."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


def get_auth_header(user):
    """Vrátí autentifikační header pro daného uživatele."""
    refresh = RefreshToken.for_user(user)
    return f"Bearer {str(refresh.access_token)}"


def assert_error_response(response, expected_status, expected_fields=None):
    """Helper pro ověření chybové odpovědi.

    Args:
        response: Response object
        expected_status: Očekávaný HTTP status
        expected_fields: Set polí, která by měla být v chybě
    """
    assert response.status_code == expected_status
    if expected_fields:
        assert set(response.data.keys()) == expected_fields


def assert_valid_response(response, expected_status, required_fields=None):
    """Helper pro ověření úspěšné odpovědi.

    Args:
        response: Response object
        expected_status: Očekávaný HTTP status
        required_fields: List polí, která by měla být v odpovědi
    """
    assert response.status_code == expected_status
    if required_fields:
        for field in required_fields:
            assert field in response.data
