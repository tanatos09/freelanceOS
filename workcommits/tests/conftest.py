"""
Lokální pytest fixtures pro workcommits testy.
"""

import pytest
from django.utils import timezone

from tests.factories import UserFactory, WorkCommitFactory


@pytest.fixture
def running_commit(db, user, project):
    """Vytvoří právě běžící WorkCommit (end_time=None)."""
    return WorkCommitFactory(user=user, project=project, end_time=None)


@pytest.fixture
def stopped_commit(db, user, project):
    """Vytvoří dokončený WorkCommit (end_time nastaven, 3600s = 1h)."""
    start = timezone.now() - timezone.timedelta(hours=1)
    return WorkCommitFactory(
        user=user,
        project=project,
        start_time=start,
        end_time=timezone.now(),
        duration_seconds=3600,
        description="Hotovo",
    )


@pytest.fixture
def commit_data(project):
    """Základní data pro start commitu."""
    return {"project": project.id}
