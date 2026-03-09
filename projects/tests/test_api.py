"""
Integrační testy pro API endpointy aplikaci projects.

Pokrývá:
- List projektů
- Vytvoření projektu
- Detail projektu
- Editace projektu
- Smazání projektu
- Filtrování podle statusu
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestProjectsListEndpoint:
    """Testy pro endpoint GET /api/projects/"""

    def test_list_projects_authenticated(self, auth_client, user, projects_list):
        """Test: Autentifikovaný uživatel vidí své projekty."""
        response = auth_client.get("/api/v1/projects/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_list_projects_unauthenticated(self, api_client):
        """Test: Neautentifikovaný uživatel nemůže vidět projekty."""
        response = api_client.get("/api/v1/projects/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_projects_returns_correct_fields(self, auth_client, project):
        """Test: Seznam vrátí správná pole."""
        response = auth_client.get("/api/v1/projects/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

        project_data = response.data[0]
        assert "id" in project_data
        assert "name" in project_data
        assert "client_name" in project_data
        assert "status_display" in project_data

    def test_list_only_own_projects(self, auth_client, auth_client_alt, user, user_alt, project):
        """Test: Uživatel vidí pouze své projekty."""
        from tests.factories import ClientFactory, ProjectFactory

        other_client = ClientFactory(user=user_alt)
        ProjectFactory(user=user_alt, client=other_client)

        response = auth_client.get("/api/v1/projects/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == project.id

    def test_filter_projects_by_status(self, auth_client, user, projects_list):
        """Test: Filtrování podle statusu."""
        response = auth_client.get("/api/v1/projects/?status=active")
        assert response.status_code == status.HTTP_200_OK
        # projects_list má 2 active projekty
        assert len(response.data) >= 1
        for proj in response.data:
            assert proj["status"] == "active"

    def test_filter_projects_by_client(self, auth_client, user, client_obj):
        """Test: Filtrování podle klienta."""
        from tests.factories import ProjectFactory

        ProjectFactory(user=user, client=client_obj)

        response = auth_client.get(f"/api/v1/projects/?client={client_obj.id}")
        assert response.status_code == status.HTTP_200_OK
        # Všechny projekty by měly být od tohoto klienta
        for proj in response.data:
            assert proj["client"] == client_obj.id

    def test_search_projects_by_name(self, auth_client, user):
        """Test: Hledání podle názvu."""
        from tests.factories import ProjectFactory

        ProjectFactory(user=user, name="Specific Project Name")
        ProjectFactory(user=user, name="Other Project")

        response = auth_client.get("/api/v1/projects/?search=Specific")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert "Specific" in response.data[0]["name"]


class TestProjectsCreateEndpoint:
    """Testy pro endpoint POST /api/projects/"""

    def test_create_project_success(self, auth_client, project_data):
        """Test: Vytvoření nového projektu."""
        response = auth_client.post("/api/v1/projects/", project_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == project_data["name"]
        assert response.data["status"] == "draft"

    def test_create_project_unauthenticated(self, api_client, project_data):
        """Test: Neautentifikovaný uživatel nemůže vytvořit projekt."""
        response = api_client.post("/api/v1/projects/", project_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_project_missing_name(self, auth_client, client_obj):
        """Test: Chybí jméno."""
        data = {"client": client_obj.id, "status": "draft"}
        response = auth_client.post("/api/v1/projects/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_project_missing_client(self, auth_client):
        """Test: Chybí klient."""
        data = {"name": "Test Project", "status": "draft"}
        response = auth_client.post("/api/v1/projects/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "client" in response.data

    def test_create_project_with_other_users_client(self, auth_client, user_alt):
        """Test: Nelze vytvořit projekt s cizím klientem."""
        from tests.factories import ClientFactory

        other_client = ClientFactory(user=user_alt)

        data = {"name": "Hacked Project", "client": other_client.id, "status": "draft"}
        response = auth_client.post("/api/v1/projects/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "client" in response.data

    def test_create_project_with_negative_budget(self, auth_client, client_obj):
        """Test: Rozpočet nesmí být negativní."""
        data = {"name": "Test Project", "client": client_obj.id, "budget": -1000}
        response = auth_client.post("/api/v1/projects/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_project_minimal_data(self, auth_client, client_obj):
        """Test: Vytvoření s minimálními daty."""
        data = {"name": "Minimal Project", "client": client_obj.id}
        response = auth_client.post("/api/v1/projects/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["budget"] == "0.00"
        assert response.data["description"] == ""


class TestProjectDetailEndpoint:
    """Testy pro endpoint GET /api/projects/{id}/"""

    def test_get_project_detail_success(self, auth_client, project):
        """Test: Získat detail projektu."""
        response = auth_client.get(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == project.id
        assert response.data["name"] == project.name

    def test_get_project_detail_unauthenticated(self, api_client, project):
        """Test: Neautentifikovaný uživatel nemůže vidět detail."""
        response = api_client.get(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_project_detail_not_found(self, auth_client):
        """Test: Neexistující projekt."""
        response = auth_client.get("/api/v1/projects/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_project_detail_not_own(self, auth_client, user_alt):
        """Test: Uživatel nemůže vidět projekt jiného uživatele."""
        from tests.factories import ClientFactory, ProjectFactory

        other_client = ClientFactory(user=user_alt)
        other_project = ProjectFactory(user=user_alt, client=other_client)

        response = auth_client.get(f"/api/v1/projects/{other_project.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_includes_all_fields(self, auth_client, project):
        """Test: Detail obsahuje všechna pole."""
        response = auth_client.get(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_200_OK

        data = response.data
        assert "description" in data
        assert "is_overdue" in data
        assert "days_until_deadline" in data


class TestProjectUpdateEndpoint:
    """Testy pro endpoint PUT /api/projects/{id}/"""

    def test_update_project_success(self, auth_client, project):
        """Test: Editace projektu."""
        data = {"name": "Updated Project Name", "status": "active", "budget": 10000.00}
        response = auth_client.put(f"/api/v1/projects/{project.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Project Name"
        assert response.data["status"] == "active"

    def test_update_project_unauthenticated(self, api_client, project):
        """Test: Neautentifikovaný uživatel nemůže editovat."""
        data = {"name": "Updated"}
        response = api_client.put(f"/api/v1/projects/{project.id}/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_project_not_own(self, auth_client, user_alt):
        """Test: Uživatel nemůže editovat projekt jiného uživatele."""
        from tests.factories import ClientFactory, ProjectFactory

        other_client = ClientFactory(user=user_alt)
        other_project = ProjectFactory(user=user_alt, client=other_client)

        data = {"name": "Hacked"}
        response = auth_client.put(f"/api/v1/projects/{other_project.id}/", data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_project_change_status(self, auth_client, project):
        """Test: Změna statusu."""
        statuses = ["draft", "active", "completed", "archived", "cancelled"]
        for new_status in statuses:
            data = {"status": new_status}
            response = auth_client.put(f"/api/v1/projects/{project.id}/", data, format="json")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["status"] == new_status


class TestProjectDeleteEndpoint:
    """Testy pro endpoint DELETE /api/projects/{id}/"""

    def test_delete_project_success(self, auth_client, project):
        """Test: Smazání projektu."""
        project_id = project.id
        response = auth_client.delete(f"/api/v1/projects/{project_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Ověř, že je smazán
        from projects.models import Project

        assert not Project.objects.filter(id=project_id).exists()

    def test_delete_project_unauthenticated(self, api_client, project):
        """Test: Neautentifikovaný uživatel nemůže smazat."""
        response = api_client.delete(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_project_not_own(self, auth_client, user_alt):
        """Test: Uživatel nemůže smazat projekt jiného uživatele."""
        from tests.factories import ClientFactory, ProjectFactory

        other_client = ClientFactory(user=user_alt)
        other_project = ProjectFactory(user=user_alt, client=other_client)

        response = auth_client.delete(f"/api/v1/projects/{other_project.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProjectEdgeCasesIntegration:
    """Edge case testy v integraci."""

    def test_project_with_large_budget(self, auth_client, client_obj):
        """Test: Projekt s obrovským rozpočtem."""
        data = {"name": "Expensive Project", "client": client_obj.id, "budget": 9999999.99}
        response = auth_client.post("/api/v1/projects/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["budget"] == "9999999.99"

    def test_project_with_long_description(self, auth_client, client_obj):
        """Test: Dlouhý popis."""
        long_desc = "A" * 5000
        data = {"name": "Test Project", "client": client_obj.id, "description": long_desc}
        response = auth_client.post("/api/v1/projects/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["description"]) == 5000

    def test_project_dates_ordering(self, auth_client, client_obj):
        """Test: start_date musí být před end_date."""
        start_date = timezone.now().date() + timedelta(days=10)
        end_date = timezone.now().date() + timedelta(days=5)

        data = {
            "name": "Test Project",
            "client": client_obj.id,
            "start_date": start_date,
            "end_date": end_date,
        }
        response = auth_client.post("/api/v1/projects/", data, format="json")
        # by mělo selhati
        assert response.status_code == status.HTTP_400_BAD_REQUEST
