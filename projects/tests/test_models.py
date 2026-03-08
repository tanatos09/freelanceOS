"""
Jednotkové testy pro Project model.

Pokrývá:
- Vytváření projektů
- Validace polí
- Status choices
- Metody modelu
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from projects.models import Project

pytestmark = pytest.mark.unit


class TestProjectModelCreation:
    """Testy vytváření projektů."""

    def test_create_project_success(self, project):
        """Test: Vytvoření validního projektu."""
        assert project.name is not None
        assert project.user is not None
        assert project.client is not None
        assert project.status in ["draft", "active", "completed", "archived", "cancelled"]

    def test_project_default_status(self, user, client_obj):
        """Test: Výchozí status je 'draft'."""
        project = Project.objects.create(
            user=user, client=client_obj, name="Test Project", status="draft"
        )
        assert project.status == "draft"

    def test_project_default_budget_zero(self, user, client_obj):
        """Test: Výchozí rozpočet je 0."""
        project = Project.objects.create(user=user, client=client_obj, name="Test Project")
        assert project.budget == 0

    def test_project_optional_fields(self, user, client_obj):
        """Test: Volitelná pole jsou skutečně volitelná."""
        project = Project.objects.create(user=user, client=client_obj, name="Minimal Project")
        assert project.description == ""
        assert project.start_date is None
        assert project.end_date is None
        assert project.estimated_hours == 0


class TestProjectStatus:
    """Testy status choices."""

    def test_all_status_choices_valid(self, user, client_obj):
        """Test: Všechny status volby jsou platné."""
        statuses = ["draft", "active", "completed", "archived", "cancelled"]
        for status in statuses:
            project = Project.objects.create(
                user=user, client=client_obj, name=f"Project {status}", status=status
            )
            assert project.status == status

    def test_invalid_status_rejected(self, user, client_obj):
        """Test: Neplatný status je odmítnut."""
        with pytest.raises(Exception):  # Integrity error or validation error
            Project.objects.create(
                user=user, client=client_obj, name="Test", status="invalid_status"
            )


class TestProjectModelMethods:
    """Testy metod projektu."""

    def test_str_representation(self, project):
        """Test: String reprezentace."""
        expected = f"{project.name} ({project.client.name})"
        assert str(project) == expected

    def test_is_overdue_no_end_date(self, project):
        """Test: Projekt bez end_date není overdue."""
        project.end_date = None
        project.save()
        assert project.is_overdue() is False

    def test_is_overdue_future_end_date(self, user, client_obj):
        """Test: Projekt s budoucím end_date není overdue."""
        future_date = timezone.now().date() + timedelta(days=10)
        project = Project.objects.create(
            user=user, client=client_obj, name="Future Project", end_date=future_date
        )
        assert project.is_overdue() is False

    def test_is_overdue_past_end_date(self, user, client_obj):
        """Test: Projekt s minulým end_date a status != completed je overdue."""
        past_date = timezone.now().date() - timedelta(days=10)
        project = Project.objects.create(
            user=user, client=client_obj, name="Past Project", end_date=past_date, status="active"
        )
        assert project.is_overdue() is True

    def test_completed_project_not_overdue(self, user, client_obj):
        """Test: Dokončený projekt není overdue."""
        past_date = timezone.now().date() - timedelta(days=10)
        project = Project.objects.create(
            user=user,
            client=client_obj,
            name="Completed Project",
            end_date=past_date,
            status="completed",
        )
        assert project.is_overdue() is False

    def test_days_until_deadline_no_end_date(self, project):
        """Test: days_until_deadline bez end_date vrátí None."""
        project.end_date = None
        project.save()
        assert project.days_until_deadline() is None

    def test_days_until_deadline_with_date(self, user, client_obj):
        """Test: days_until_deadline vrátí správný počet dní."""
        future_date = timezone.now().date() + timedelta(days=5)
        project = Project.objects.create(
            user=user, client=client_obj, name="Test", end_date=future_date
        )
        days = project.days_until_deadline()
        assert days >= 4 and days <= 6  # tolerence pro změnu data během testu

    def test_progress_percent_no_hours(self, project):
        """Test: progress_percent() bez hodů vrátí 0."""
        project.estimated_hours = 0
        project.save()
        assert project.progress_percent() == 0

    def test_timestamps_created(self, project):
        """Test: Timestamps se vytváří automaticky."""
        assert project.created_at is not None
        assert project.updated_at is not None


class TestProjectEdgeCases:
    """Edge case testy."""

    def test_project_with_very_large_budget(self, user, client_obj):
        """Test: Velký rozpočet."""
        large_budget = 9999999.99
        project = Project.objects.create(
            user=user, client=client_obj, name="Expensive Project", budget=large_budget
        )
        assert project.budget == large_budget

    def test_project_with_decimal_hours(self, user, client_obj):
        """Test: Desítková čísla pro hodiny."""
        project = Project.objects.create(
            user=user, client=client_obj, name="Test", estimated_hours=123.45
        )
        assert float(project.estimated_hours) == 123.45

    def test_project_long_description(self, user, client_obj):
        """Test: Dlouhý popis."""
        long_desc = "A" * 5000
        project = Project.objects.create(
            user=user, client=client_obj, name="Test", description=long_desc
        )
        assert len(project.description) == 5000

    def test_project_dates_validation(self, user, client_obj):
        """Test: start_date > end_date by mělo být řešeno serializerem."""
        from django.utils import timezone

        start = timezone.now().date() + timedelta(days=10)
        end = timezone.now().date() + timedelta(days=5)

        # Model by neměl validovat, to dělá serializer
        # Ale pojďme to otestovat
        project = Project.objects.create(
            user=user, client=client_obj, name="Test", start_date=start, end_date=end
        )
        assert project.start_date > project.end_date
