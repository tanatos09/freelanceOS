"""
Lokální pytest fixtures pro workspaces testy.
"""

import pytest

from tests.factories import UserFactory, WorkspaceFactory


@pytest.fixture
def workspace(db, user):
    """Vytvoří workspace s uživatelem jako vlastníkem."""
    return WorkspaceFactory(owner=user, name="Test Workspace", slug="test-workspace")


@pytest.fixture
def workspace_alt(db, user_alt):
    """Vytvoří workspace vlastněný alternativním uživatelem."""
    return WorkspaceFactory(owner=user_alt, name="Alt Workspace", slug="alt-workspace")


@pytest.fixture
def workspace_data():
    """Základní data pro vytvoření workspace."""
    return {"name": "My New Workspace", "slug": "my-new-workspace"}


@pytest.fixture
def workspace_with_member(db, user, user_alt):
    """Workspace s vlastníkem + dalším členem."""
    from apps.workspaces.services import WorkspaceService

    workspace = WorkspaceService.create_workspace(owner=user, name="Members WS", slug="members-ws")
    WorkspaceService.add_member(workspace=workspace, user=user_alt, role="member")
    return workspace
