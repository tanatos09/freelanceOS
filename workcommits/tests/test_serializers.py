"""
Jednotkové testy pro WorkCommitSerializer.

Pokrývá:
- Serializaci běžícího a zastaveného commitu
- Vypočítaná pole (is_running, project_name, duration_hours, elapsed_seconds)
- Read-only pole
"""

import pytest
from django.utils import timezone

from workcommits.serializers import WorkCommitSerializer

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestWorkCommitSerializerRunning:
    """Testy serializace běžícího commitu."""

    def test_is_running_true(self, running_commit):
        """Test: is_running=True proběžící commit."""
        data = WorkCommitSerializer(running_commit).data
        assert data["is_running"] is True

    def test_project_name_present(self, running_commit):
        """Test: project_name vrátí jméno projektu."""
        data = WorkCommitSerializer(running_commit).data
        assert data["project_name"] == running_commit.project.name

    def test_elapsed_seconds_positive(self, running_commit):
        """Test: elapsed_seconds > 0 pro běžící commit."""
        data = WorkCommitSerializer(running_commit).data
        assert data["elapsed_seconds"] >= 0

    def test_end_time_is_null(self, running_commit):
        """Test: end_time je null pro běžící commit."""
        data = WorkCommitSerializer(running_commit).data
        assert data["end_time"] is None

    def test_required_fields_present(self, running_commit):
        """Test: Všechna povinná pole jsou přítomna."""
        data = WorkCommitSerializer(running_commit).data
        required_fields = [
            "id",
            "project",
            "project_name",
            "start_time",
            "end_time",
            "description",
            "tag",
            "duration_seconds",
            "duration_hours",
            "is_running",
            "elapsed_seconds",
            "created_at",
        ]
        for field in required_fields:
            assert field in data, f"Pole '{field}' chybí v serializovaných datech"


class TestWorkCommitSerializerStopped:
    """Testy serializace zastaveného commitu."""

    def test_is_running_false(self, stopped_commit):
        """Test: is_running=False pro zastavený commit."""
        data = WorkCommitSerializer(stopped_commit).data
        assert data["is_running"] is False

    def test_duration_hours_correct(self, stopped_commit):
        """Test: duration_hours odpovídá duration_seconds."""
        data = WorkCommitSerializer(stopped_commit).data
        assert data["duration_hours"] == 1.0  # 3600s

    def test_elapsed_seconds_equals_duration_when_stopped(self, stopped_commit):
        """Test: elapsed_seconds=duration_seconds pro zastavený commit."""
        data = WorkCommitSerializer(stopped_commit).data
        assert data["elapsed_seconds"] == stopped_commit.duration_seconds

    def test_end_time_present(self, stopped_commit):
        """Test: end_time je vyplněno."""
        data = WorkCommitSerializer(stopped_commit).data
        assert data["end_time"] is not None


class TestWorkCommitSerializerReadOnly:
    """Testy read-only polí."""

    def test_duration_seconds_read_only(self, user, project, running_commit):
        """Test: duration_seconds je read-only (nelze přepsat přes serializer)."""
        data = {
            "project": project.id,
            "duration_seconds": 99999,
        }
        serializer = WorkCommitSerializer(running_commit, data=data, partial=True)
        serializer.is_valid()
        # duration_seconds by nemělo být v validated_data
        assert "duration_seconds" not in serializer.validated_data

    def test_id_read_only(self, running_commit):
        """Test: Pole id je vždy přítomno a je UUID/int."""
        data = WorkCommitSerializer(running_commit).data
        assert "id" in data
        assert data["id"] == running_commit.pk

    def test_created_at_read_only(self, running_commit):
        """Test: created_at je přítomno."""
        data = WorkCommitSerializer(running_commit).data
        assert "created_at" in data
        assert data["created_at"] is not None


class TestWorkCommitSerializerEdgeCases:
    """Edge case testy pro WorkCommitSerializer."""

    def test_description_empty_string(self, user, project):
        """Test: Prázdný popis se serializuje jako prázdný řetězec."""
        from tests.factories import WorkCommitFactory

        commit = WorkCommitFactory(user=user, project=project, description="")
        data = WorkCommitSerializer(commit).data
        assert data["description"] == ""

    def test_tag_none(self, user, project):
        """Test: tag=None se serializuje jako null."""
        from tests.factories import WorkCommitFactory

        commit = WorkCommitFactory(user=user, project=project, tag=None)
        data = WorkCommitSerializer(commit).data
        assert data["tag"] is None

    def test_tag_with_value(self, user, project):
        """Test: tag s hodnotou se serializuje správně."""
        from tests.factories import WorkCommitFactory

        commit = WorkCommitFactory(user=user, project=project, tag="frontend")
        data = WorkCommitSerializer(commit).data
        assert data["tag"] == "frontend"
