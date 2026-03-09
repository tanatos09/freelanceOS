"""
Integrační testy pro API endpointy aplikaci clients.

Pokrývá:
- List klientů
- Vytvoření klienta
- Detail klienta
- Editace klienta
- Smazání klienta
- Filtrování a vyhledávání
"""

import pytest
from rest_framework import status

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestClientsListEndpoint:
    """Testy pro endpoint GET /api/clients/"""

    def test_list_clients_authenticated(self, auth_client, user, clients_list):
        """Test: Autentifikovaný uživatel vidí své klienty."""
        response = auth_client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_list_clients_unauthenticated(self, api_client):
        """Test: Neautentifikovaný uživatel nemůže vidět klienty."""
        response = api_client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_clients_returns_correct_fields(self, auth_client, user, client_obj):
        """Test: Seznam vrátí správná pole."""
        response = auth_client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

        client_data = response.data[0]
        assert "id" in client_data
        assert "name" in client_data
        assert "email" in client_data
        assert "total_earnings" in client_data
        assert "project_count" in client_data

    def test_list_only_own_clients(self, auth_client, auth_client_alt, user, user_alt, client_obj):
        """Test: Uživatel vidí pouze své klienty."""
        from tests.factories import ClientFactory

        ClientFactory(user=user_alt, name="Alt Client", email="alt@example.com")

        response = auth_client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == client_obj.name

    def test_list_clients_search_by_name(self, auth_client, user, clients_list):
        """Test: Hledání podle jména."""
        clients_list[0].name = "Specific Name"
        clients_list[0].save()

        response = auth_client.get("/api/v1/clients/?search=Specific")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Specific Name"

    def test_list_clients_search_by_email(self, auth_client, user):
        """Test: Hledání podle emailu."""
        from tests.factories import ClientFactory

        ClientFactory(user=user, name="Test", email="unique@example.com")
        ClientFactory(user=user, name="Other", email="other@example.com")

        response = auth_client.get("/api/v1/clients/?search=unique")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert "unique" in response.data[0]["email"]

    def test_list_clients_search_by_company(self, auth_client, user):
        """Test: Hledání podle společnosti."""
        from tests.factories import ClientFactory

        ClientFactory(user=user, name="Test", email="test1@example.com", company="Unique Corp")
        ClientFactory(user=user, name="Other", email="test2@example.com", company="Other Inc")

        response = auth_client.get("/api/v1/clients/?search=Unique")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["company"] == "Unique Corp"


class TestClientsCreateEndpoint:
    """Testy pro endpoint POST /api/clients/"""

    def test_create_client_success(self, auth_client, user, client_data):
        """Test: Vytvoření nového klienta."""
        response = auth_client.post("/api/v1/clients/", client_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == client_data["name"]
        assert response.data["email"] == client_data["email"]

    def test_create_client_unauthenticated(self, api_client, client_data):
        """Test: Neautentifikovaný uživatel nemůže vytvořit klienta."""
        response = api_client.post("/api/v1/clients/", client_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_client_missing_name(self, auth_client):
        """Test: Chybí jméno."""
        data = {"email": "test@example.com"}
        response = auth_client.post("/api/v1/clients/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_client_missing_email(self, auth_client):
        """Test: Chybí email."""
        data = {"name": "Test Client"}
        response = auth_client.post("/api/v1/clients/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_create_client_duplicate_email(self, auth_client, user, client_obj):
        """Test: Email který již existuje pro daného uživatele."""
        data = {"name": "Different Name", "email": client_obj.email}
        response = auth_client.post("/api/v1/clients/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_create_client_without_optional_fields(self, auth_client):
        """Test: Vytvoření bez volitelných polí."""
        data = {"name": "Minimal Client", "email": "minimal@example.com"}
        response = auth_client.post("/api/v1/clients/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["phone"] == ""
        assert response.data["company"] == ""

    def test_create_client_with_all_fields(self, auth_client, client_data):
        """Test: Vytvoření se všemi poli."""
        response = auth_client.post("/api/v1/clients/", client_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["phone"] == client_data["phone"]
        assert response.data["company"] == client_data["company"]
        assert response.data["notes"] == client_data["notes"]


class TestClientDetailEndpoint:
    """Testy pro endpoint GET /api/clients/{id}/"""

    def test_get_client_detail_success(self, auth_client, client_obj):
        """Test: Získat detail klienta."""
        response = auth_client.get(f"/api/v1/clients/{client_obj.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == client_obj.id
        assert response.data["name"] == client_obj.name

    def test_get_client_detail_unauthenticated(self, api_client, client_obj):
        """Test: Neautentifikovaný uživatel nemůže vidět detail."""
        response = api_client.get(f"/api/v1/clients/{client_obj.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_client_detail_not_found(self, auth_client):
        """Test: Neexistující klient."""
        response = auth_client.get("/api/v1/clients/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_client_detail_not_own(self, auth_client, user_alt):
        """Test: Uživatel nemůže vidět klienta jiného uživatele."""
        from tests.factories import ClientFactory

        other_client = ClientFactory(user=user_alt)

        response = auth_client.get(f"/api/v1/clients/{other_client.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_includes_all_fields(self, auth_client, client_obj):
        """Test: Detail obsahuje všechna pole včetně notes."""
        response = auth_client.get(f"/api/v1/clients/{client_obj.id}/")
        assert response.status_code == status.HTTP_200_OK

        data = response.data
        assert "notes" in data
        assert "phone" in data
        assert "company" in data


class TestClientUpdateEndpoint:
    """Testy pro endpoint PUT /api/clients/{id}/"""

    def test_update_client_success(self, auth_client, client_obj):
        """Test: Editace klienta."""
        data = {"name": "Updated Name", "email": "updated@example.com", "phone": "+420987654321"}
        response = auth_client.put(f"/api/v1/clients/{client_obj.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"
        assert response.data["email"] == "updated@example.com"

    def test_update_client_partial(self, auth_client, client_obj):
        """Test: Částečná editace (PATCH)."""
        data = {"name": "Only Name Changed"}
        response = auth_client.put(f"/api/v1/clients/{client_obj.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Only Name Changed"

    def test_update_client_unauthenticated(self, api_client, client_obj):
        """Test: Neautentifikovaný uživatel nemůže editovat."""
        data = {"name": "Updated"}
        response = api_client.put(f"/api/v1/clients/{client_obj.id}/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_client_not_own(self, auth_client, user_alt):
        """Test: Uživatel nemůže editovat cizího klienta."""
        from tests.factories import ClientFactory

        other_client = ClientFactory(user=user_alt)

        data = {"name": "Hacked"}
        response = auth_client.put(f"/api/v1/clients/{other_client.id}/", data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_duplicate_email_error(self, auth_client, user, client_obj):
        """Test: Editace na existující email jiného klienta."""
        from tests.factories import ClientFactory

        other_client = ClientFactory(user=user, name="Other", email="other@example.com")

        data = {"email": other_client.email}
        response = auth_client.put(f"/api/v1/clients/{client_obj.id}/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


class TestClientDeleteEndpoint:
    """Testy pro endpoint DELETE /api/clients/{id}/"""

    def test_delete_client_success(self, auth_client, client_obj):
        """Test: Smazání klienta."""
        client_id = client_obj.id
        response = auth_client.delete(f"/api/v1/clients/{client_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Ověř, že je smazán
        from clients.models import Client

        assert not Client.objects.filter(id=client_id).exists()

    def test_delete_client_unauthenticated(self, api_client, client_obj):
        """Test: Neautentifikovaný uživatel nemůže smazat."""
        response = api_client.delete(f"/api/v1/clients/{client_obj.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_client_not_own(self, auth_client, user_alt):
        """Test: Uživatel nemůže smazat cizího klienta."""
        from tests.factories import ClientFactory

        other_client = ClientFactory(user=user_alt)

        response = auth_client.delete(f"/api/v1/clients/{other_client.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_client_not_found(self, auth_client):
        """Test: Smazání neexistujícího klienta."""
        response = auth_client.delete("/api/v1/clients/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestClientStatsEndpoint:
    """Testy pro endpoint GET /api/clients/{id}/stats/"""

    def test_client_stats_success(self, auth_client, client_obj):
        """Test: Získat statistiky klienta."""
        response = auth_client.get(f"/api/v1/clients/{client_obj.id}/stats/")
        assert response.status_code == status.HTTP_200_OK
        assert "total_earnings" in response.data
        assert "project_count" in response.data

    def test_client_stats_with_projects(self, auth_client, client_obj):
        """Test: Statistiky obsahují správné hodnoty."""
        from tests.factories import ProjectFactory

        ProjectFactory(client=client_obj, budget=1000)
        ProjectFactory(client=client_obj, budget=2000)

        response = auth_client.get(f"/api/v1/clients/{client_obj.id}/stats/")
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data["total_earnings"]) == 3000
        assert response.data["project_count"] == 2
