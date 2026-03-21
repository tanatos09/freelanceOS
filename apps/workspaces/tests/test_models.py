"""
Jednotkové testy pro Workspace a WorkspaceMembership modely.

Pokrývá:
- Vytváření workspace
- Unikátnost slugu
- WorkspaceMembership
- WorkspaceService (create, add_member, remove_member, change_role)
- String reprezentace
- Edge cases
"""

import pytest

from apps.common.exceptions import BusinessError, NotFoundError
from apps.workspaces.models import Workspace, WorkspaceMembership
from apps.workspaces.services import WorkspaceService

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestWorkspaceModelCreation:
    """Testy vytváření workspace."""

    def test_create_workspace_success(self, user):
        """Test: Vytvoření validního workspace."""
        ws = Workspace.objects.create(name="My Workspace", slug="my-workspace", owner=user)
        assert ws.name == "My Workspace"
        assert ws.slug == "my-workspace"
        assert ws.owner == user
        assert ws.plan == "free"
        assert ws.is_active is True

    def test_workspace_has_uuid_pk(self, workspace):
        """Test: Workspace má UUID jako primární klíč."""
        import uuid

        assert isinstance(workspace.id, uuid.UUID)

    def test_workspace_slug_unique(self, user):
        """Test: Unikátní omezení na slug."""
        from django.db import IntegrityError

        Workspace.objects.create(name="WS1", slug="unique-slug", owner=user)
        with pytest.raises(IntegrityError):
            Workspace.objects.create(name="WS2", slug="unique-slug", owner=user)

    def test_workspace_str_representation(self, workspace):
        """Test: String reprezentace workspace."""
        assert str(workspace) == workspace.name

    def test_workspace_plan_choices(self, user):
        """Test: Validní hodnoty plánu."""
        for plan in ["free", "starter", "professional", "enterprise"]:
            ws = Workspace.objects.create(
                name=f"WS-{plan}", slug=f"ws-{plan}", owner=user, plan=plan
            )
            assert ws.plan == plan

    def test_workspace_settings_default_empty_dict(self, workspace):
        """Test: Výchozí settings je prázdný dict."""
        assert workspace.settings == {}

    def test_workspace_has_timestamps(self, workspace):
        """Test: Workspace má created_at a updated_at."""
        assert workspace.created_at is not None
        assert workspace.updated_at is not None


class TestWorkspaceMembershipModel:
    """Testy WorkspaceMembership modelu."""

    def test_create_membership(self, workspace, user):
        """Test: Vytvoření membership."""
        membership = WorkspaceMembership.objects.create(
            workspace=workspace, user=user, role="owner"
        )
        assert membership.workspace == workspace
        assert membership.user == user
        assert membership.role == "owner"
        assert membership.is_active is True

    def test_membership_unique_together(self, workspace, user):
        """Test: Unikátní kombinace workspace+user."""
        from django.db import IntegrityError

        WorkspaceMembership.objects.create(workspace=workspace, user=user, role="member")
        with pytest.raises(IntegrityError):
            WorkspaceMembership.objects.create(workspace=workspace, user=user, role="admin")

    def test_membership_str_representation(self, workspace, user):
        """Test: String reprezentace membership."""
        m = WorkspaceMembership.objects.create(workspace=workspace, user=user, role="admin")
        assert user.email in str(m)
        assert workspace.name in str(m)
        assert "admin" in str(m)

    def test_membership_role_choices(self, workspace, user, user_alt):
        """Test: Validní role."""
        from tests.factories import UserFactory

        for i, role in enumerate(["owner", "admin", "member", "viewer"]):
            u = UserFactory()
            m = WorkspaceMembership.objects.create(workspace=workspace, user=u, role=role)
            assert m.role == role

    def test_membership_has_uuid_pk(self, workspace, user):
        """Test: Membership má UUID PK."""
        import uuid

        m = WorkspaceMembership.objects.create(workspace=workspace, user=user, role="member")
        assert isinstance(m.id, uuid.UUID)


class TestWorkspaceService:
    """Testy WorkspaceService."""

    def test_create_workspace_creates_owner_membership(self, user):
        """Test: create_workspace automaticky vytvoří owner membership."""
        ws = WorkspaceService.create_workspace(owner=user, name="WS", slug="ws-test-1")
        assert WorkspaceMembership.objects.filter(
            workspace=ws, user=user, role="owner", is_active=True
        ).exists()

    def test_create_workspace_auto_slug(self, user):
        """Test: Automatické generování slugu z názvu."""
        ws = WorkspaceService.create_workspace(owner=user, name="My Cool Workspace")
        assert ws.slug == "my-cool-workspace"

    def test_create_workspace_slug_uniqueness(self, user):
        """Test: Duplikátní slug se automaticky inkrementuje."""
        WorkspaceService.create_workspace(owner=user, name="WS", slug="existing-slug")
        ws2 = WorkspaceService.create_workspace(owner=user, name="WS2", slug="existing-slug")
        assert ws2.slug == "existing-slug-1"

    def test_create_workspace_slug_uniqueness_multiple(self, user):
        """Test: Více duplikátů slugu se inkrementují."""
        WorkspaceService.create_workspace(owner=user, name="WS", slug="dup-slug")
        WorkspaceService.create_workspace(owner=user, name="WS2", slug="dup-slug")
        ws3 = WorkspaceService.create_workspace(owner=user, name="WS3", slug="dup-slug")
        assert ws3.slug == "dup-slug-2"

    def test_get_user_workspaces_returns_own(self, user):
        """Test: get_user_workspaces vrátí workspace uživatele."""
        ws = WorkspaceService.create_workspace(owner=user, name="User WS", slug="user-ws-1")
        workspaces = WorkspaceService.get_user_workspaces(user)
        pks = [w.pk for w in workspaces]
        assert ws.pk in pks

    def test_get_user_workspaces_excludes_others(self, user, user_alt):
        """Test: get_user_workspaces nevrátí cizí workspace."""
        WorkspaceService.create_workspace(owner=user_alt, name="Alt WS", slug="alt-ws-1")
        workspaces = list(WorkspaceService.get_user_workspaces(user))
        assert len(workspaces) == 0

    def test_get_workspace_existing(self, workspace):
        """Test: get_workspace vrátí existující workspace."""
        result = WorkspaceService.get_workspace(workspace.id)
        assert result.pk == workspace.pk

    def test_get_workspace_not_found(self):
        """Test: get_workspace pro neexistující ID vyhodí NotFoundError."""
        import uuid

        with pytest.raises(NotFoundError):
            WorkspaceService.get_workspace(uuid.uuid4())

    def test_add_member_success(self, workspace, user_alt):
        """Test: add_member přidá nového člena."""
        membership = WorkspaceService.add_member(workspace, user_alt, role="member")
        assert membership.user == user_alt
        assert membership.role == "member"
        assert membership.is_active is True

    def test_add_member_already_active(self, workspace_with_member, user_alt):
        """Test: add_member vyhodí BusinessError pro existujícího aktivního člena."""
        with pytest.raises(BusinessError):
            WorkspaceService.add_member(workspace_with_member, user_alt, role="admin")

    def test_add_member_reactivate_inactive(self, workspace, user_alt):
        """Test: add_member reaktivuje neaktivní membership."""
        m = WorkspaceMembership.objects.create(
            workspace=workspace, user=user_alt, role="member", is_active=False
        )
        WorkspaceService.add_member(workspace, user_alt, role="admin")
        m.refresh_from_db()
        assert m.is_active is True
        assert m.role == "admin"

    def test_remove_member_success(self, workspace_with_member, user_alt):
        """Test: remove_member deaktivuje membership."""
        WorkspaceService.remove_member(workspace_with_member, user_alt)
        m = WorkspaceMembership.objects.get(workspace=workspace_with_member, user=user_alt)
        assert m.is_active is False

    def test_remove_owner_raises(self, user):
        """Test: Nelze odebrat vlastníka workspace."""
        ws = WorkspaceService.create_workspace(owner=user, name="Del WS", slug="del-ws-1")
        with pytest.raises(BusinessError):
            WorkspaceService.remove_member(ws, user)

    def test_remove_nonexistent_member_raises(self, workspace, user_alt):
        """Test: Odebrat neexistujícího člena vyhodí NotFoundError."""
        with pytest.raises(NotFoundError):
            WorkspaceService.remove_member(workspace, user_alt)

    def test_change_role_success(self, workspace_with_member, user_alt):
        """Test: change_role změní roli člena."""
        WorkspaceService.change_role(workspace_with_member, user_alt, "admin")
        m = WorkspaceMembership.objects.get(workspace=workspace_with_member, user=user_alt)
        assert m.role == "admin"

    def test_change_role_owner_raises(self, user):
        """Test: Nelze změnit roli vlastníka (owner → non-owner)."""
        ws = WorkspaceService.create_workspace(owner=user, name="Role WS", slug="role-ws-1")
        with pytest.raises(BusinessError):
            WorkspaceService.change_role(ws, user, "admin")

    def test_change_role_nonexistent_member_raises(self, workspace, user_alt):
        """Test: change_role pro neexistujícího člena vyhodí NotFoundError."""
        with pytest.raises(NotFoundError):
            WorkspaceService.change_role(workspace, user_alt, "admin")
