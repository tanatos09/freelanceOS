"""
Jednotkové testy pro Client model.

Pokrývá:
- Vytváření klientů
- Validace polí
- Vztahy
- Metody modelu
"""

import pytest
from clients.models import Client
from django.db import IntegrityError

pytestmark = pytest.mark.unit


class TestClientModelCreation:
    """Testy vytváření klientů."""

    def test_create_client_success(self, user):
        """Test: Vytvoření validního klienta."""
        client = Client.objects.create(
            user=user,
            name="Test Client",
            email="test@example.com",
            phone="+420123456789",
            company="Test Co.",
            notes="Test notes",
        )
        assert client.name == "Test Client"
        assert client.email == "test@example.com"
        assert client.user == user

    def test_create_client_required_fields(self, user):
        """Test: Vyžadovaná pole jsou: user, name, email."""
        with pytest.raises(IntegrityError):
            Client.objects.create(user=user, email="test@example.com")

    def test_create_client_optional_fields(self, user):
        """Test: Pole phone, company, notes jsou volitelná."""
        client = Client.objects.create(
            user=user, name="Minimal Client", email="minimal@example.com"
        )
        assert client.phone == ""
        assert client.company == ""
        assert client.notes == ""

    def test_unique_email_per_user(self, user, user_alt):
        """Test: Email je unikátní pro uživatele, ale ne globálně."""
        Client.objects.create(user=user, name="Client 1", email="same@example.com")
        # Stejný email pro jiného uživatele musí být OK
        client2 = Client.objects.create(user=user_alt, name="Client 2", email="same@example.com")
        assert client2.id is not None

        # Ale duplikát pro stejného uživatele by měl selhat
        with pytest.raises(IntegrityError):
            Client.objects.create(user=user, name="Client 3", email="same@example.com")


class TestClientModelMethods:
    """Testy metod klienta."""

    def test_str_representation(self, client_obj, user):
        """Test: String reprezentace."""
        expected = f"{client_obj.name} ({user.email})"
        assert str(client_obj) == expected

    def test_total_earnings_no_projects(self, client_obj):
        """Test: total_earnings() vrátí 0 bez projektů."""
        assert client_obj.total_earnings() == 0

    def test_total_earnings_with_projects(self, client_obj):
        """Test: total_earnings() sečte rozpočty projektů."""
        from tests.factories import ProjectFactory

        ProjectFactory(client=client_obj, budget=1000)
        ProjectFactory(client=client_obj, budget=2000)

        assert client_obj.total_earnings() == 3000

    def test_project_count_no_projects(self, client_obj):
        """Test: project_count() vrátí 0 bez projektů."""
        assert client_obj.project_count() == 0

    def test_project_count_with_projects(self, client_obj):
        """Test: project_count() počítá projekty."""
        from tests.factories import ProjectFactory

        ProjectFactory(client=client_obj)
        ProjectFactory(client=client_obj)
        ProjectFactory(client=client_obj)

        assert client_obj.project_count() == 3


class TestClientEdgeCases:
    """Edge case testy."""

    def test_very_long_name(self, user):
        """Test: Dlouhé jméno."""
        long_name = "A" * 255
        client = Client.objects.create(user=user, name=long_name, email="test@example.com")
        assert client.name == long_name

    def test_email_with_special_chars(self, user):
        """Test: Email se speciálními znaky."""
        client = Client.objects.create(user=user, name="Test", email="test+alias@example.co.uk")
        assert client.email == "test+alias@example.co.uk"

    def test_notes_with_newlines_and_unicode(self, user):
        """Test: Poznámky s newlines a Unicode."""
        notes = "Řádek 1\nŘádek 2\n特殊文字"
        client = Client.objects.create(
            user=user, name="Test", email="test@example.com", notes=notes
        )
        assert client.notes == notes

    def test_timestamps_created(self, user):
        """Test: Timestamps se vytváří automaticky."""
        client = Client.objects.create(user=user, name="Test", email="test@example.com")
        assert client.created_at is not None
        assert client.updated_at is not None
