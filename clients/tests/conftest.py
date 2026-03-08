"""
Lokální fixtures pro aplikaci clients.
"""

import pytest
from tests.factories import ClientFactory


@pytest.fixture
def client_data(user):
    """Validní data pro vytvoření klienta."""
    return {
        "name": "Test Co.",
        "email": "contact@testco.com",
        "phone": "+420777123456",
        "company": "Test Company Ltd.",
        "notes": "VIP client",
    }


@pytest.fixture
def multiple_clients(user):
    """Vytvoří více klientů."""
    return [
        ClientFactory(user=user, name=f"Client {i}", email=f"client{i}@example.com")
        for i in range(5)
    ]
