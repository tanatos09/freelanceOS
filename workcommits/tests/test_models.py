"""
Jednotkové testy pro WorkCommit model.

Pokrývá:
- Vytváření commitů
- Vlastnost is_running
- Metodu stop()
- Metodu duration_hours()
- String reprezentaci
- Edge cases
"""

import pytest
from django.utils import timezone

from workcommits.models import WorkCommit

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestWorkCommitCreation:
    """Testy vytváření WorkCommit objektů."""

    def test_create_workcommit_success(self, user, project):
        """Test: Vytvoření validního commitu."""
        commit = WorkCommit.objects.create(user=user, project=project)
        assert commit.pk is not None
        assert commit.user == user
        assert commit.project == project
        assert commit.end_time is None
        assert commit.duration_seconds == 0
        assert commit.description == ""
        assert commit.tag is None

    def test_create_workcommit_with_all_fields(self, user, project):
        """Test: Vytvoření commitu se všemi poli."""
        start = timezone.now() - timezone.timedelta(hours=2)
        end = timezone.now()
        commit = WorkCommit.objects.create(
            user=user,
            project=project,
            start_time=start,
            end_time=end,
            description="Práce na feature",
            tag="backend",
            duration_seconds=7200,
        )
        assert commit.description == "Práce na feature"
        assert commit.tag == "backend"
        assert commit.duration_seconds == 7200
        assert commit.end_time is not None

    def test_default_ordering_by_start_time(self, user, project):
        """Test: Výchozí řazení od nejnovějšího."""
        from tests.factories import WorkCommitFactory

        t1 = timezone.now() - timezone.timedelta(hours=3)
        t2 = timezone.now() - timezone.timedelta(hours=1)
        c1 = WorkCommitFactory(user=user, project=project, start_time=t1)
        c2 = WorkCommitFactory(user=user, project=project, start_time=t2)

        commits = list(WorkCommit.objects.filter(user=user))
        assert commits[0].pk == c2.pk
        assert commits[1].pk == c1.pk

    def test_str_representation(self, user, project):
        """Test: String reprezentace commitu."""
        import datetime

        start = timezone.datetime(2025, 6, 15, 10, 30, tzinfo=datetime.timezone.utc)
        commit = WorkCommit.objects.create(user=user, project=project, start_time=start)
        assert str(commit) == f"{project.name} – 2025-06-15 10:30"


class TestWorkCommitIsRunning:
    """Testy vlastnosti is_running."""

    def test_is_running_when_end_time_none(self, running_commit):
        """Test: is_running=True pokud end_time je None."""
        assert running_commit.is_running is True

    def test_is_not_running_when_end_time_set(self, stopped_commit):
        """Test: is_running=False pokud end_time je nastaven."""
        assert stopped_commit.is_running is False

    def test_is_running_after_stop(self, running_commit):
        """Test: is_running=False po zavolání stop()."""
        running_commit.stop()
        assert running_commit.is_running is False


class TestWorkCommitStop:
    """Testy metody stop()."""

    def test_stop_sets_end_time(self, running_commit):
        """Test: stop() nastaví end_time."""
        assert running_commit.end_time is None
        running_commit.stop()
        assert running_commit.end_time is not None

    def test_stop_calculates_duration(self, user, project):
        """Test: stop() správně vypočítá dobu trvání."""
        start = timezone.now() - timezone.timedelta(hours=1)
        commit = WorkCommit.objects.create(user=user, project=project, start_time=start)
        commit.stop()
        # Přibližně 3600 sekund (+/- 2s tolerance)
        assert abs(commit.duration_seconds - 3600) < 2

    def test_stop_with_description(self, running_commit):
        """Test: stop() nastaví popis."""
        running_commit.stop(description="Hotová práce")
        assert running_commit.description == "Hotová práce"

    def test_stop_without_description_keeps_empty(self, running_commit):
        """Test: stop() bez popisu zachová prázdný popis."""
        running_commit.stop()
        assert running_commit.description == ""

    def test_stop_persists_to_db(self, user, project):
        """Test: stop() uloží do databáze."""
        from tests.factories import WorkCommitFactory

        start = timezone.now() - timezone.timedelta(seconds=5)
        commit = WorkCommitFactory(user=user, project=project, start_time=start, end_time=None)
        commit.stop()
        refreshed = WorkCommit.objects.get(pk=commit.pk)
        assert refreshed.end_time is not None
        assert refreshed.duration_seconds > 0

    def test_stop_already_stopped_noop(self, stopped_commit):
        """Test: stop() na již zastaveném commitu nedělá nic."""
        original_end = stopped_commit.end_time
        original_duration = stopped_commit.duration_seconds
        stopped_commit.stop()
        assert stopped_commit.end_time == original_end
        assert stopped_commit.duration_seconds == original_duration

    def test_stop_duration_cannot_be_negative(self, user, project):
        """Test: duration_seconds nemůže být negativní."""
        # start_time v budoucnosti (edge case)
        start = timezone.now() + timezone.timedelta(seconds=10)
        commit = WorkCommit.objects.create(user=user, project=project, start_time=start)
        commit.stop()
        assert commit.duration_seconds >= 0


class TestWorkCommitDurationHours:
    """Testy metody duration_hours()."""

    def test_duration_hours_stopped(self, stopped_commit):
        """Test: duration_hours() vrátí správnou hodnotu pro zastavený commit."""
        assert stopped_commit.duration_hours() == 1.0  # 3600s = 1h

    def test_duration_hours_running(self, user, project):
        """Test: duration_hours() pro běžící commit vrátí přibližný čas."""
        start = timezone.now() - timezone.timedelta(hours=2)
        commit = WorkCommit.objects.create(user=user, project=project, start_time=start)
        hours = commit.duration_hours()
        assert abs(hours - 2.0) < 0.01

    def test_duration_hours_zero(self, user, project):
        """Test: Commit s duration_seconds=0 vrátí 0.0."""
        start = timezone.now()
        end = timezone.now()
        commit = WorkCommit.objects.create(
            user=user,
            project=project,
            start_time=start,
            end_time=end,
            duration_seconds=0,
        )
        assert commit.duration_hours() == 0.0

    def test_duration_hours_rounding(self, user, project):
        """Test: duration_hours() zaokrouhluje na 2 desetinná místa."""
        commit = WorkCommit.objects.create(
            user=user,
            project=project,
            start_time=timezone.now(),
            end_time=timezone.now(),
            duration_seconds=5400,  # 1.5h
        )
        assert commit.duration_hours() == 1.5


class TestWorkCommitRelationships:
    """Testy vztahů WorkCommit s dalšími modely."""

    def test_commit_cascade_delete_with_user(self, user, project):
        """Test: Smazání uživatele smaže i jeho commity."""
        from tests.factories import WorkCommitFactory

        WorkCommitFactory(user=user, project=project)
        WorkCommitFactory(user=user, project=project)
        assert WorkCommit.objects.filter(user=user).count() == 2

        user.delete()
        assert WorkCommit.objects.filter().count() == 0

    def test_commit_cascade_delete_with_project(self, user, project):
        """Test: Smazání projektu smaže i jeho commity."""
        from tests.factories import WorkCommitFactory

        WorkCommitFactory(user=user, project=project)
        project.delete()
        assert WorkCommit.objects.filter().count() == 0

    def test_related_name_work_commits(self, user, project):
        """Test: related_name work_commits na User a Project."""
        from tests.factories import WorkCommitFactory

        c = WorkCommitFactory(user=user, project=project)
        assert user.work_commits.filter(pk=c.pk).exists()
        assert project.work_commits.filter(pk=c.pk).exists()
