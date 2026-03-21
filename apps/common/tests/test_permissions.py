"""
Jednotkové testy pro apps/common permissions.

Pokrývá:
- IsWorkspaceMember
- IsWorkspaceAdmin
- IsWorkspaceOwner
"""

from unittest.mock import MagicMock

import pytest

from apps.common.permissions import (
    IsWorkspaceAdmin,
    IsWorkspaceMember,
    IsWorkspaceOwner,
)

pytestmark = pytest.mark.unit


def _make_request(user, workspace=None):
    """Pomocná funkce — vytvoří mock request."""
    request = MagicMock()
    request.user = user
    request.workspace = workspace
    return request


class TestIsWorkspaceMember:
    """Testy pro IsWorkspaceMember permission."""

    def test_no_workspace_denies(self, user):
        """Test: Bez workspace → odepřít."""
        request = _make_request(user, workspace=None)
        assert IsWorkspaceMember().has_permission(request, None) is False

    @pytest.mark.django_db
    def test_active_member_allowed(self, user, user_alt):
        """Test: Aktivní člen má přístup."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Perm WS", slug="perm-ws-1")
        WorkspaceService.add_member(ws, user_alt, role="member")

        request = _make_request(user_alt, workspace=ws)
        assert IsWorkspaceMember().has_permission(request, None) is True

    @pytest.mark.django_db
    def test_inactive_member_denied(self, user, user_alt):
        """Test: Neaktivní člen nemá přístup."""
        from apps.workspaces.models import WorkspaceMembership
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Perm WS2", slug="perm-ws-2")
        WorkspaceService.add_member(ws, user_alt, role="member")
        WorkspaceMembership.objects.filter(workspace=ws, user=user_alt).update(is_active=False)

        request = _make_request(user_alt, workspace=ws)
        assert IsWorkspaceMember().has_permission(request, None) is False

    @pytest.mark.django_db
    def test_owner_is_member(self, user):
        """Test: Vlastník workspace je také člen."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Owner WS", slug="owner-ws-1")
        request = _make_request(user, workspace=ws)
        assert IsWorkspaceMember().has_permission(request, None) is True

    @pytest.mark.django_db
    def test_non_member_denied(self, user, user_alt):
        """Test: Uživatel bez membership nemá přístup."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="No Mem WS", slug="nomem-ws-1")
        request = _make_request(user_alt, workspace=ws)
        assert IsWorkspaceMember().has_permission(request, None) is False


class TestIsWorkspaceAdmin:
    """Testy pro IsWorkspaceAdmin permission."""

    def test_no_workspace_denies(self, user):
        """Test: Bez workspace → odepřít."""
        request = _make_request(user, workspace=None)
        assert IsWorkspaceAdmin().has_permission(request, None) is False

    @pytest.mark.django_db
    def test_owner_is_admin(self, user):
        """Test: Vlastník má admin práva."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Admin WS", slug="admin-ws-1")
        request = _make_request(user, workspace=ws)
        assert IsWorkspaceAdmin().has_permission(request, None) is True

    @pytest.mark.django_db
    def test_admin_role_allowed(self, user, user_alt):
        """Test: Uživatel s rolí admin má přístup."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Admin WS2", slug="admin-ws-2")
        WorkspaceService.add_member(ws, user_alt, role="admin")
        request = _make_request(user_alt, workspace=ws)
        assert IsWorkspaceAdmin().has_permission(request, None) is True

    @pytest.mark.django_db
    def test_member_not_admin(self, user, user_alt):
        """Test: Člen s rolí member nemá admin práva."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Admin WS3", slug="admin-ws-3")
        WorkspaceService.add_member(ws, user_alt, role="member")
        request = _make_request(user_alt, workspace=ws)
        assert IsWorkspaceAdmin().has_permission(request, None) is False

    @pytest.mark.django_db
    def test_viewer_not_admin(self, user, user_alt):
        """Test: Člen s rolí viewer nemá admin práva."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Admin WS4", slug="admin-ws-4")
        WorkspaceService.add_member(ws, user_alt, role="viewer")
        request = _make_request(user_alt, workspace=ws)
        assert IsWorkspaceAdmin().has_permission(request, None) is False


class TestIsWorkspaceOwner:
    """Testy pro IsWorkspaceOwner permission."""

    def test_no_workspace_denies(self, user):
        """Test: Bez workspace → odepřít (falsy)."""
        request = _make_request(user, workspace=None)
        assert not IsWorkspaceOwner().has_permission(request, None)

    @pytest.mark.django_db
    def test_owner_allowed(self, user):
        """Test: Vlastník má přístup."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Owner WS", slug="owner-ws-2")
        request = _make_request(user, workspace=ws)
        assert IsWorkspaceOwner().has_permission(request, None) is True

    @pytest.mark.django_db
    def test_non_owner_denied(self, user, user_alt):
        """Test: Non-owner nemá přístup i s admin rolí."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Owner WS2", slug="owner-ws-3")
        WorkspaceService.add_member(ws, user_alt, role="admin")
        request = _make_request(user_alt, workspace=ws)
        assert IsWorkspaceOwner().has_permission(request, None) is False
