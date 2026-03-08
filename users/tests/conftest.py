"""
Lokální pytest fixtures pro aplikaci users.

Tyto fixtures jsou specifické pro users app a doplňují
globální fixtures z root/tests/conftest.py
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user_data():
    """Vrátí validní data pro vytvoření uživatele."""
    return {
        "email": "newuser@example.com",
        "password": "securepass123",
        "password2": "securepass123",
    }


@pytest.fixture
def registration_data(user_data):
    """Alias pro user_data."""
    return user_data


@pytest.fixture
def inactive_user(db):
    """Vytvoří neaktivního uživatele."""
    user = User.objects.create_user(email="inactive@example.com", password="testpass123")
    user.is_active = False
    user.save()
    return user
