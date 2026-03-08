"""
Testy pro serializery aplikace clients.
"""

import pytest
from clients.serializers import (
    ClientListSerializer,
    ClientDetailSerializer,
    ClientCreateUpdateSerializer,
)

pytestmark = pytest.mark.unit


class TestClientListSerializer:
    """Testy pro ClientListSerializer."""

    def test_serialize_client(self, client_obj):
        """Test: Serializace klienta."""
        serializer = ClientListSerializer(client_obj)
        data = serializer.data
        assert data["id"] == client_obj.id
        assert data["name"] == client_obj.name
        assert data["email"] == client_obj.email

    def test_includes_computed_fields(self, client_obj):
        """Test: Obsahuje počítané pole (total_earnings, project_count)."""
        serializer = ClientListSerializer(client_obj)
        data = serializer.data
        assert "total_earnings" in data
        assert "project_count" in data

    def test_list_serialization(self, clients_list):
        """Test: Serializace seznamu klientů."""
        serializer = ClientListSerializer(clients_list, many=True)
        assert len(serializer.data) == 5

    def test_read_only_fields(self, client_obj):
        """Test: Stanovená pole jsou read-only."""
        serializer = ClientListSerializer(client_obj)
        assert "total_earnings" in serializer.fields
        assert serializer.fields["total_earnings"].read_only is True


class TestClientDetailSerializer:
    """Testy pro ClientDetailSerializer."""

    def test_serialize_client_with_all_fields(self, client_obj):
        """Test: Serializace obsahuje všechna pole."""
        serializer = ClientDetailSerializer(client_obj)
        data = serializer.data
        required_fields = [
            "id",
            "name",
            "email",
            "phone",
            "company",
            "notes",
            "total_earnings",
            "project_count",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert field in data

    def test_includes_notes_field(self, client_obj):
        """Test: Detail se liší tím, že obsahuje notes."""
        list_ser = ClientListSerializer(client_obj)
        detail_ser = ClientDetailSerializer(client_obj)
        assert "notes" not in list_ser.data
        assert "notes" in detail_ser.data


class TestClientCreateUpdateSerializer:
    """Testy pro ClientCreateUpdateSerializer."""

    def test_valid_creation_data(self, db, user, rf):
        """Test: Vytvoření s validním data."""
        request = rf.post("/")
        request.user = user

        data = {
            "name": "New Client",
            "email": "new@example.com",
            "phone": "+420123456789",
            "company": "New Co.",
            "notes": "Test",
        }
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert serializer.is_valid()

    def test_missing_required_name(self, db, user, rf):
        """Test: Chybí jméno."""
        request = rf.post("/")
        request.user = user

        data = {"email": "test@example.com"}
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_missing_required_email(self, db, user, rf):
        """Test: Chybí email."""
        request = rf.post("/")
        request.user = user

        data = {"name": "Test Client"}
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_duplicate_email_validation(self, db, user, rf, client_obj):
        """Test: Duplikátní email pro stejného uživatele."""
        request = rf.post("/")
        request.user = user

        data = {
            "name": "Different Name",
            "email": client_obj.email,  # Tento email už patří user
            "phone": "+420123456789",
        }
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_duplicate_email_allowed_for_other_user(self, db, user, user_alt, rf):
        """Test: Stejný email pro jiného uživatele je OK."""
        from tests.factories import ClientFactory

        ClientFactory(user=user, name="Client 1", email="same@example.com")

        request = rf.post("/")
        request.user = user_alt

        data = {"name": "Client 2", "email": "same@example.com"}
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert serializer.is_valid()

    def test_update_allows_own_email(self, db, user, rf, client_obj):
        """Test: Update vlastního emailu nepovažuje za duplikát."""
        request = rf.post("/")
        request.user = user

        data = {
            "name": "Updated Name",
            "email": client_obj.email,  # Stejný email jako existující instance
        }
        serializer = ClientCreateUpdateSerializer(
            client_obj, data=data, partial=True, context={"request": request}
        )
        assert serializer.is_valid()

    def test_optional_fields_validation(self, db, user, rf):
        """Test: Volitelná pole jsou bez validace."""
        request = rf.post("/")
        request.user = user

        data = {
            "name": "Minimal Client",
            "email": "minimal@example.com",
            # phone a company nejsou vyplneny
        }
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert serializer.is_valid()


class TestSerializerEdgeCases:
    """Edge case testy."""

    def test_invalid_email_format(self, db, user, rf):
        """Test: Neplatný formát emailu."""
        request = rf.post("/")
        request.user = user

        data = {"name": "Test", "email": "not-an-email"}
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_empty_optional_fields(self, db, user, rf):
        """Test: Prázdná volitelná pole."""
        request = rf.post("/")
        request.user = user

        data = {
            "name": "Test",
            "email": "test@example.com",
            "phone": "",
            "company": "",
            "notes": "",
        }
        serializer = ClientCreateUpdateSerializer(data=data, context={"request": request})
        assert serializer.is_valid()
