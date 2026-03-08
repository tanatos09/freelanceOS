"""
Testy pro serializery aplikace projects.
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from projects.serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
)

pytestmark = pytest.mark.unit


class TestProjectListSerializer:
    """Testy pro ProjectListSerializer."""

    def test_serialize_project(self, project):
        """Test: Serializace projektu."""
        serializer = ProjectListSerializer(project)
        data = serializer.data
        assert data["id"] == project.id
        assert data["name"] == project.name
        assert "client_name" in data

    def test_includes_computed_fields(self, project):
        """Test: Obsahuje počítané pole (is_overdue, progress)."""
        serializer = ProjectListSerializer(project)
        data = serializer.data
        assert "is_overdue" in data
        assert "progress" in data

    def test_includes_status_display(self, project):
        """Test: Obsahuje čitelný status."""
        serializer = ProjectListSerializer(project)
        data = serializer.data
        assert "status_display" in data

    def test_list_serialization(self, projects_list):
        """Test: Serializace seznamu projektů."""
        serializer = ProjectListSerializer(projects_list, many=True)
        assert len(serializer.data) == 5


class TestProjectDetailSerializer:
    """Testy pro ProjectDetailSerializer."""

    def test_serialize_project_with_all_fields(self, project):
        """Test: Detail obsahuje všechna pole."""
        serializer = ProjectDetailSerializer(project)
        data = serializer.data
        required_fields = [
            "id",
            "name",
            "description",
            "client",
            "status",
            "budget",
            "estimated_hours",
            "start_date",
            "end_date",
            "is_overdue",
            "days_until_deadline",
            "progress",
        ]
        for field in required_fields:
            assert field in data

    def test_includes_advanced_computed_fields(self, project):
        """Test: Detail má rozšířená computed fields."""
        serializer = ProjectDetailSerializer(project)
        data = serializer.data
        assert "days_until_deadline" in data
        assert "actual_hours" in data
        assert "hourly_rate" in data


class TestProjectCreateUpdateSerializer:
    """Testy pro ProjectCreateUpdateSerializer."""

    def test_valid_creation_data(self, db, user, rf, client_obj, project_data):
        """Test: Vytvoření s validním data."""
        request = rf.post("/")
        request.user = user

        serializer = ProjectCreateUpdateSerializer(data=project_data, context={"request": request})
        assert serializer.is_valid()

    def test_missing_required_name(self, db, user, rf, client_obj):
        """Test: Chybí jméno."""
        request = rf.post("/")
        request.user = user

        data = {"client": client_obj.id, "status": "draft"}
        serializer = ProjectCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_missing_required_client(self, db, user, rf):
        """Test: Chybí klient."""
        request = rf.post("/")
        request.user = user

        data = {"name": "Test Project", "status": "draft"}
        serializer = ProjectCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "client" in serializer.errors

    def test_client_ownership_validation(self, db, user, user_alt, rf):
        """Test: Klient musí patřit uživateli."""
        from tests.factories import ClientFactory

        other_user_client = ClientFactory(user=user_alt)

        request = rf.post("/")
        request.user = user

        data = {"name": "Test Project", "client": other_user_client.id, "status": "draft"}
        serializer = ProjectCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "client" in serializer.errors

    def test_negative_budget_validation(self, db, user, rf, client_obj):
        """Test: Rozpočet nesmí být negativní."""
        request = rf.post("/")
        request.user = user

        data = {"name": "Test Project", "client": client_obj.id, "budget": -100}
        serializer = ProjectCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "budget" in serializer.errors

    def test_negative_hours_validation(self, db, user, rf, client_obj):
        """Test: Hodiny nesmí být negativní."""
        request = rf.post("/")
        request.user = user

        data = {"name": "Test Project", "client": client_obj.id, "estimated_hours": -10}
        serializer = ProjectCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "estimated_hours" in serializer.errors

    def test_date_validation_start_after_end(self, db, user, rf, client_obj):
        """Test: start_date nemůže být po end_date."""
        request = rf.post("/")
        request.user = user

        start_date = timezone.now().date() + timedelta(days=10)
        end_date = timezone.now().date() + timedelta(days=5)

        data = {
            "name": "Test Project",
            "client": client_obj.id,
            "start_date": start_date,
            "end_date": end_date,
        }
        serializer = ProjectCreateUpdateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors or "start_date" in serializer.errors
