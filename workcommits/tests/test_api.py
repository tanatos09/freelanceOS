"""
Integrační testy pro WorkCommit API endpointy.

Pokrývá:
- GET /api/v1/workcommits/            — seznam
- GET /api/v1/workcommits/running/    — aktuálně běžící
- POST /api/v1/workcommits/start/     — spuštění timeru
- GET/PATCH/DELETE /api/v1/workcommits/{pk}/    — detail/editace/smazání
- POST /api/v1/workcommits/{pk}/commit/         — ukončení + volitelné pokračování
- POST /api/v1/workcommits/{pk}/stop/           — zastavení
"""

import pytest
from django.utils import timezone
from rest_framework import status

from tests.factories import WorkCommitFactory

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestWorkCommitListEndpoint:
    """Testy pro GET /api/v1/workcommits/"""

    def test_list_authenticated(self, auth_client, user, project):
        """Test: Autentifikovaný uživatel vidí své commity."""
        WorkCommitFactory(user=user, project=project)
        WorkCommitFactory(user=user, project=project)
        response = auth_client.get("/api/v1/workcommits/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_unauthenticated(self, api_client):
        """Test: Neautentifikovaný uživatel dostane 401."""
        response = api_client.get("/api/v1/workcommits/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_only_own_commits(self, auth_client, user, user_alt, project):
        """Test: Uživatel vidí pouze vlastní commity."""
        from tests.factories import ClientFactory, ProjectFactory

        WorkCommitFactory(user=user, project=project)
        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)
        WorkCommitFactory(user=user_alt, project=alt_project)

        response = auth_client.get("/api/v1/workcommits/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_filter_by_project(self, auth_client, user, project, client_obj):
        """Test: Filtrování commitů podle projektu."""
        from tests.factories import ProjectFactory

        project2 = ProjectFactory(user=user, client=client_obj)
        WorkCommitFactory(user=user, project=project)
        WorkCommitFactory(user=user, project=project)
        WorkCommitFactory(user=user, project=project2)

        response = auth_client.get(f"/api/v1/workcommits/?project={project.id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_filter_by_date(self, auth_client, user, project):
        """Test: Filtrování commitů podle data."""
        today = timezone.now()
        yesterday = today - timezone.timedelta(days=1)
        WorkCommitFactory(user=user, project=project, start_time=today)
        WorkCommitFactory(user=user, project=project, start_time=yesterday)

        date_str = today.date().isoformat()
        response = auth_client.get(f"/api/v1/workcommits/?date={date_str}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_empty(self, auth_client, user):
        """Test: Prázdný seznam pokud neexistují commity."""
        response = auth_client.get("/api/v1/workcommits/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_returns_correct_fields(self, auth_client, user, project):
        """Test: Vrácená data obsahují očekávaná pole."""
        WorkCommitFactory(user=user, project=project)
        response = auth_client.get("/api/v1/workcommits/")
        assert response.status_code == status.HTTP_200_OK
        item = response.data[0]
        for field in [
            "id",
            "project",
            "project_name",
            "is_running",
            "duration_hours",
            "elapsed_seconds",
        ]:
            assert field in item


class TestWorkCommitRunningEndpoint:
    """Testy pro GET /api/v1/workcommits/running/"""

    def test_running_returns_commit(self, auth_client, user, project):
        """Test: Vrátí aktuálně běžící commit."""
        commit = WorkCommitFactory(user=user, project=project, end_time=None)
        response = auth_client.get("/api/v1/workcommits/running/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == commit.pk
        assert response.data["is_running"] is True

    def test_running_returns_null_when_none(self, auth_client, user):
        """Test: Vrátí null pokud žádný commit neběží."""
        response = auth_client.get("/api/v1/workcommits/running/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data is None

    def test_running_unauthenticated(self, api_client):
        """Test: Neautentifikovaný uživatel dostane 401."""
        response = api_client.get("/api/v1/workcommits/running/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_running_only_own_commit(self, auth_client, user, user_alt, project):
        """Test: Vrátí pouze vlastní běžící commit, ne cizí."""
        from tests.factories import ClientFactory, ProjectFactory

        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)
        WorkCommitFactory(user=user_alt, project=alt_project, end_time=None)

        response = auth_client.get("/api/v1/workcommits/running/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data is None


class TestWorkCommitStartEndpoint:
    """Testy pro POST /api/v1/workcommits/start/"""

    def test_start_success(self, auth_client, user, project):
        """Test: Spuštění timeru vrátí 201."""
        response = auth_client.post(
            "/api/v1/workcommits/start/",
            {"project": project.id},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_running"] is True
        assert response.data["project"] == project.id

    def test_start_unauthenticated(self, api_client, project):
        """Test: Neautentifikovaný uživatel dostane 401."""
        response = api_client.post(
            "/api/v1/workcommits/start/",
            {"project": project.id},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_start_missing_project(self, auth_client):
        """Test: Chybí pole project — vrátí 400."""
        response = auth_client.post("/api/v1/workcommits/start/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_start_already_running(self, auth_client, user, project):
        """Test: Nelze spustit druhý timer pokud jeden již běží."""
        WorkCommitFactory(user=user, project=project, end_time=None)
        response = auth_client.post(
            "/api/v1/workcommits/start/",
            {"project": project.id},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_start_project_not_found(self, auth_client):
        """Test: Neexistující projekt vrátí 404."""
        response = auth_client.post(
            "/api/v1/workcommits/start/",
            {"project": 99999},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_start_other_user_project(self, auth_client, user_alt, project):
        """Test: Nelze spustit timer na cizím projektu."""
        from tests.factories import ClientFactory, ProjectFactory

        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)

        response = auth_client.post(
            "/api/v1/workcommits/start/",
            {"project": alt_project.id},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_start_creates_db_record(self, auth_client, user, project):
        """Test: Spuštění timeru vytvoří záznam v databázi."""
        from workcommits.models import WorkCommit

        count_before = WorkCommit.objects.filter(user=user).count()
        auth_client.post(
            "/api/v1/workcommits/start/",
            {"project": project.id},
            format="json",
        )
        assert WorkCommit.objects.filter(user=user).count() == count_before + 1


class TestWorkCommitDetailEndpoint:
    """Testy pro GET/PATCH/DELETE /api/v1/workcommits/{pk}/"""

    def test_detail_get(self, auth_client, user, project):
        """Test: Detail commitu."""
        commit = WorkCommitFactory(user=user, project=project)
        response = auth_client.get(f"/api/v1/workcommits/{commit.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == commit.pk

    def test_detail_unauthenticated(self, api_client, user, project):
        """Test: Neautentifikovaný uživatel dostane 401."""
        commit = WorkCommitFactory(user=user, project=project)
        response = api_client.get(f"/api/v1/workcommits/{commit.pk}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_not_found(self, auth_client):
        """Test: Neexistující commit vrátí 404."""
        response = auth_client.get("/api/v1/workcommits/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_other_user_commit(self, auth_client, user_alt, project):
        """Test: Nelze vidět cizí commit."""
        from tests.factories import ClientFactory, ProjectFactory

        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)
        commit = WorkCommitFactory(user=user_alt, project=alt_project)
        response = auth_client.get(f"/api/v1/workcommits/{commit.pk}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_patch_description(self, auth_client, user, project):
        """Test: PATCH aktualizuje popis."""
        commit = WorkCommitFactory(user=user, project=project, description="Starý popis")
        response = auth_client.patch(
            f"/api/v1/workcommits/{commit.pk}/",
            {"description": "Nový popis"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == "Nový popis"

    def test_detail_patch_tag(self, auth_client, user, project):
        """Test: PATCH aktualizuje tag."""
        commit = WorkCommitFactory(user=user, project=project)
        response = auth_client.patch(
            f"/api/v1/workcommits/{commit.pk}/",
            {"tag": "backend"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["tag"] == "backend"

    def test_detail_patch_clear_tag(self, auth_client, user, project):
        """Test: PATCH s prázdným tagem nastaví tag na None."""
        commit = WorkCommitFactory(user=user, project=project, tag="frontend")
        response = auth_client.patch(
            f"/api/v1/workcommits/{commit.pk}/",
            {"tag": ""},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["tag"] is None

    def test_detail_delete(self, auth_client, user, project):
        """Test: DELETE smaže commit."""
        from workcommits.models import WorkCommit

        commit = WorkCommitFactory(user=user, project=project)
        response = auth_client.delete(f"/api/v1/workcommits/{commit.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not WorkCommit.objects.filter(pk=commit.pk).exists()

    def test_detail_delete_other_user(self, auth_client, user_alt):
        """Test: Nelze smazat cizí commit."""
        from tests.factories import ClientFactory, ProjectFactory

        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)
        commit = WorkCommitFactory(user=user_alt, project=alt_project)
        response = auth_client.delete(f"/api/v1/workcommits/{commit.pk}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_patch_start_time_recalculates_duration(self, auth_client, stopped_commit):
        """Test: PATCH start_time přepočítá duration_seconds."""
        new_start = stopped_commit.end_time - timezone.timedelta(hours=2)
        response = auth_client.patch(
            f"/api/v1/workcommits/{stopped_commit.pk}/",
            {"start_time": new_start.isoformat()},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["duration_seconds"] == 7200

    def test_detail_patch_end_time_recalculates_duration(self, auth_client, stopped_commit):
        """Test: PATCH end_time přepočítá duration_seconds."""
        new_end = stopped_commit.start_time + timezone.timedelta(minutes=30)
        response = auth_client.patch(
            f"/api/v1/workcommits/{stopped_commit.pk}/",
            {"end_time": new_end.isoformat()},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["duration_seconds"] == 1800

    def test_detail_patch_project(self, auth_client, user, project, client_obj):
        """Test: PATCH projekt změní přiřazení."""
        from tests.factories import ProjectFactory

        new_project = ProjectFactory(user=user, client=client_obj)
        commit = WorkCommitFactory(user=user, project=project)
        response = auth_client.patch(
            f"/api/v1/workcommits/{commit.pk}/",
            {"project": new_project.id},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["project"] == new_project.id

    def test_detail_patch_project_other_user(self, auth_client, user, project, user_alt):
        """Test: Nelze přiřadit cizí projekt."""
        from tests.factories import ClientFactory, ProjectFactory

        commit = WorkCommitFactory(user=user, project=project)
        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)
        response = auth_client.patch(
            f"/api/v1/workcommits/{commit.pk}/",
            {"project": alt_project.id},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_patch_invalid_times(self, auth_client, stopped_commit):
        """Test: end_time před start_time vrátí 400."""
        bad_end = stopped_commit.start_time - timezone.timedelta(minutes=1)
        response = auth_client.patch(
            f"/api/v1/workcommits/{stopped_commit.pk}/",
            {"end_time": bad_end.isoformat()},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_detail_patch_cannot_clear_end_time_on_stopped_commit(self, auth_client, stopped_commit):
        """Test: Nelze nastavit end_time=null na dokončeném záznamu."""
        response = auth_client.patch(
            f"/api/v1/workcommits/{stopped_commit.pk}/",
            {"end_time": None},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_detail_patch_running_commit_times_not_recalculate(self, auth_client, running_commit):
        """Test: Editace start_time běžícího commitu nepřepočítá duration."""
        new_start = timezone.now() - timezone.timedelta(hours=3)
        response = auth_client.patch(
            f"/api/v1/workcommits/{running_commit.pk}/",
            {"start_time": new_start.isoformat()},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_running"] is True
        assert response.data["duration_seconds"] == 0  # not recalculated while running


class TestWorkCommitCommitEndpoint:
    """Testy pro POST /api/v1/workcommits/{pk}/commit/"""

    def test_commit_stop_running(self, auth_client, running_commit):
        """Test: Ukončení běžícího commitu."""
        response = auth_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/commit/",
            {"description": "Dokončeno"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["commit"]["is_running"] is False
        assert response.data["commit"]["description"] == "Dokončeno"
        assert response.data["next_commit"] is None

    def test_commit_with_continue(self, auth_client, running_commit):
        """Test: Ukončení s continue=True spustí nový commit."""
        response = auth_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/commit/",
            {"continue": True},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["commit"]["is_running"] is False
        assert response.data["next_commit"] is not None
        assert response.data["next_commit"]["is_running"] is True

    def test_commit_with_tag(self, auth_client, running_commit):
        """Test: Commit s tagem."""
        response = auth_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/commit/",
            {"tag": "review"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["commit"]["tag"] == "review"

    def test_commit_already_stopped(self, auth_client, stopped_commit):
        """Test: Nelze commitnout již zastavený commit."""
        response = auth_client.post(
            f"/api/v1/workcommits/{stopped_commit.pk}/commit/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_commit_not_found(self, auth_client):
        """Test: Neexistující commit vrátí 404."""
        response = auth_client.post("/api/v1/workcommits/99999/commit/", {}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_commit_other_user(self, auth_client, user_alt):
        """Test: Nelze commitnout cizí commit."""
        from tests.factories import ClientFactory, ProjectFactory

        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)
        commit = WorkCommitFactory(user=user_alt, project=alt_project, end_time=None)
        response = auth_client.post(
            f"/api/v1/workcommits/{commit.pk}/commit/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_commit_unauthenticated(self, api_client, running_commit):
        """Test: Neautentifikovaný uživatel dostane 401."""
        response = api_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/commit/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestWorkCommitStopEndpoint:
    """Testy pro POST /api/v1/workcommits/{pk}/stop/"""

    def test_stop_running_commit(self, auth_client, running_commit):
        """Test: Zastavení běžícího commitu."""
        response = auth_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/stop/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_running"] is False

    def test_stop_with_description(self, auth_client, running_commit):
        """Test: Zastavení s popisem."""
        response = auth_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/stop/",
            {"description": "Konec práce"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == "Konec práce"

    def test_stop_with_tag(self, auth_client, running_commit):
        """Test: Zastavení s tagem."""
        response = auth_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/stop/",
            {"tag": "backend"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["tag"] == "backend"

    def test_stop_already_stopped(self, auth_client, stopped_commit):
        """Test: Nelze zastavit již zastavený commit."""
        response = auth_client.post(
            f"/api/v1/workcommits/{stopped_commit.pk}/stop/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_stop_not_found(self, auth_client):
        """Test: Neexistující commit vrátí 404."""
        response = auth_client.post("/api/v1/workcommits/99999/stop/", {}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_stop_other_user(self, auth_client, user_alt):
        """Test: Nelze zastavit cizí commit."""
        from tests.factories import ClientFactory, ProjectFactory

        alt_client = ClientFactory(user=user_alt)
        alt_project = ProjectFactory(user=user_alt, client=alt_client)
        commit = WorkCommitFactory(user=user_alt, project=alt_project, end_time=None)
        response = auth_client.post(
            f"/api/v1/workcommits/{commit.pk}/stop/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_stop_unauthenticated(self, api_client, running_commit):
        """Test: Neautentifikovaný uživatel dostane 401."""
        response = api_client.post(
            f"/api/v1/workcommits/{running_commit.pk}/stop/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_stop_persists_duration(self, auth_client, user, project):
        """Test: Zastavení uloží duration_seconds do databáze."""
        from workcommits.models import WorkCommit

        start = timezone.now() - timezone.timedelta(minutes=30)
        commit = WorkCommitFactory(user=user, project=project, start_time=start, end_time=None)

        auth_client.post(f"/api/v1/workcommits/{commit.pk}/stop/", {}, format="json")

        refreshed = WorkCommit.objects.get(pk=commit.pk)
        assert refreshed.duration_seconds > 0
        assert refreshed.end_time is not None


class TestWorkCommitIntegrationFlows:
    """Integrační testy celého toku práce."""

    def test_full_work_session(self, auth_client, user, project):
        """Test: Celý pracovní cyklus — start → stop."""
        # Spuštění
        start_response = auth_client.post(
            "/api/v1/workcommits/start/",
            {"project": project.id},
            format="json",
        )
        assert start_response.status_code == status.HTTP_201_CREATED
        commit_id = start_response.data["id"]

        # Kontrola běžícího
        running_response = auth_client.get("/api/v1/workcommits/running/")
        assert running_response.data["id"] == commit_id

        # Zastavení
        stop_response = auth_client.post(
            f"/api/v1/workcommits/{commit_id}/stop/",
            {"description": "Hotová práce"},
            format="json",
        )
        assert stop_response.status_code == status.HTTP_200_OK
        assert stop_response.data["is_running"] is False

        # Žádný commit neběží
        running_after = auth_client.get("/api/v1/workcommits/running/")
        assert running_after.data is None

    def test_commit_continue_creates_chain(self, auth_client, user, project):
        """Test: commit s continue vytvoří nový commit na stejném projektu."""
        start_response = auth_client.post(
            "/api/v1/workcommits/start/",
            {"project": project.id},
            format="json",
        )
        commit_id = start_response.data["id"]

        commit_response = auth_client.post(
            f"/api/v1/workcommits/{commit_id}/commit/",
            {"description": "Část 1", "continue": True},
            format="json",
        )
        next_id = commit_response.data["next_commit"]["id"]

        # Nový commit běží na stejném projektu
        running_response = auth_client.get("/api/v1/workcommits/running/")
        assert running_response.data["id"] == next_id
        assert running_response.data["project"] == project.id
