"""
Globální pytest fixtures pro všechny testy.

Aby se fixtures načetly, musí být tento soubor v root/tests/ složce.
Pytest jej automaticky discover a načte.
"""
import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import UserFactory, ClientFactory, ProjectFactory


# ─────────────────────────────────────────────────────────────────────────────
# MARKER DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    """Zavádí custom markery."""
    config.addinivalue_line(
        "markers", "unit: označuje jednotkové testy (modely, serializers)"
    )
    config.addinivalue_line(
        "markers", "integration: označuje integrační testy (API endpoint)"
    )
    config.addinivalue_line(
        "markers", "edge_cases: označuje testy edge cases"
    )
    config.addinivalue_line(
        "markers", "slow: označuje pomalé testy"
    )


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope='session')
def django_db_setup():
    """Nastaví testovací databázi."""
    pass  # Django testů automaticky vytváří testovací DB


@pytest.fixture
def db():
    """Ensure each test uses the database."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# USER FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def user(db):
    """Vytvoří běžného uživatele."""
    return UserFactory(email='testuser@example.com', password='testpass123')


@pytest.fixture
def user_alt(db):
    """Vytvoří druhého uživatele pro testy interakcí."""
    return UserFactory(email='altuser@example.com', password='testpass123')


@pytest.fixture
def superuser(db):
    """Vytvoří superuživatele."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def client_obj(db, user):
    """Vytvoří klienta přiřazeného k testovacímu uživateli."""
    return ClientFactory(user=user, name='Test Client', email='client@example.com')


@pytest.fixture
def clients_list(db, user):
    """Vytvoří seznam 5 klientů."""
    return [ClientFactory(user=user) for _ in range(5)]


# ─────────────────────────────────────────────────────────────────────────────
# PROJECT FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def project(db, user, client_obj):
    """Vytvoří projekt pro testovacího uživatele."""
    return ProjectFactory(
        user=user,
        client=client_obj,
        name='Test Project',
        status='active'
    )


@pytest.fixture
def projects_list(db, user, client_obj):
    """Vytvoří seznam 5 projektů."""
    return [
        ProjectFactory(user=user, client=client_obj, status='draft'),
        ProjectFactory(user=user, client=client_obj, status='active'),
        ProjectFactory(user=user, client=client_obj, status='active'),
        ProjectFactory(user=user, client=client_obj, status='completed'),
        ProjectFactory(user=user, client=client_obj, status='archived'),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# API CLIENT FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Vytvoří REST API klienta."""
    return APIClient()


@pytest.fixture
def auth_client(db, user):
    """Vytvoří autentifikovaného API klienta."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


@pytest.fixture
def auth_client_alt(db, user_alt):
    """Vytvoří autentifikovaného API klienta s alternativním uživatelem."""
    client = APIClient()
    refresh = RefreshToken.for_user(user_alt)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


# ─────────────────────────────────────────────────────────────────────────────
# TOKEN FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def access_token(db, user):
    """Vrátí access token pro uživatele."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.fixture
def refresh_token(db, user):
    """Vrátí refresh token pro uživatele."""
    refresh = RefreshToken.for_user(user)
    return str(refresh)


@pytest.fixture
def tokens(db, user):
    """Vrátí oba tokeny (access + refresh)."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }
