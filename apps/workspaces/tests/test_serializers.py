"""
Jednotkové testy pro Workspace serializers.

Pokrývá:
- WorkspaceSerializer
- WorkspaceCreateSerializer
- WorkspaceMembershipSerializer
"""

import pytest

from apps.workspaces.serializers import (
    WorkspaceCreateSerializer,
    WorkspaceMembershipSerializer,
    WorkspaceSerializer,
)

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestWorkspaceSerializer:
    """Testy pro WorkspaceSerializer."""

    def test_contains_expected_fields(self, workspace):
        """Test: Serializer vrátí očekávaná pole."""
        data = WorkspaceSerializer(workspace).data
        for field in ["id", "name", "slug", "plan", "is_active", "member_count", "created_at"]:
            assert field in data

    def test_member_count_no_members(self, workspace):
        """Test: member_count je 0 bez aktivních členů."""
        # workspace fixture nemá automaticky memberships (pouze přes WorkspaceFactory)
        data = WorkspaceSerializer(workspace).data
        assert data["member_count"] == 0

    def test_member_count_with_members(self, workspace_with_member, user, user_alt):
        """Test: member_count počítá pouze aktivní členy."""
        data = WorkspaceSerializer(workspace_with_member).data
        assert data["member_count"] == 2  # owner + member

    def test_member_count_excludes_inactive(self, workspace, user_alt):
        """Test: member_count nezahrnuje neaktivní členy."""
        from apps.workspaces.models import WorkspaceMembership

        WorkspaceMembership.objects.create(
            workspace=workspace, user=user_alt, role="member", is_active=False
        )
        data = WorkspaceSerializer(workspace).data
        assert data["member_count"] == 0

    def test_id_is_uuid_string(self, workspace):
        """Test: id je serializováno jako UUID řetězec."""
        data = WorkspaceSerializer(workspace).data
        import uuid

        uuid.UUID(str(data["id"]))  # Musí být validní UUID

    def test_plan_default_free(self, workspace):
        """Test: Výchozí plán je 'free'."""
        data = WorkspaceSerializer(workspace).data
        assert data["plan"] == "free"


class TestWorkspaceCreateSerializer:
    """Testy pro WorkspaceCreateSerializer."""

    def test_valid_data(self):
        """Test: Validní data projdou validací."""
        serializer = WorkspaceCreateSerializer(data={"name": "New WS", "slug": "new-ws"})
        assert serializer.is_valid()

    def test_missing_name(self):
        """Test: Chybí jméno — validace selže."""
        serializer = WorkspaceCreateSerializer(data={"slug": "test-slug"})
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_missing_slug(self):
        """Test: Chybí slug — validace selže."""
        serializer = WorkspaceCreateSerializer(data={"name": "Test WS"})
        assert not serializer.is_valid()
        assert "slug" in serializer.errors

    def test_empty_name(self):
        """Test: Prázdné jméno selže."""
        serializer = WorkspaceCreateSerializer(data={"name": "", "slug": "test"})
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_slug_too_long(self):
        """Test: Příliš dlouhý slug selže."""
        serializer = WorkspaceCreateSerializer(data={"name": "WS", "slug": "a" * 101})
        assert not serializer.is_valid()
        assert "slug" in serializer.errors


class TestWorkspaceMembershipSerializer:
    """Testy pro WorkspaceMembershipSerializer."""

    def test_contains_expected_fields(self, workspace_with_member, user):
        """Test: Serializer vrátí očekávaná pole."""
        from apps.workspaces.models import WorkspaceMembership

        membership = WorkspaceMembership.objects.filter(
            workspace=workspace_with_member, user=user
        ).first()
        data = WorkspaceMembershipSerializer(membership).data
        for field in ["id", "user", "user_email", "role", "is_active", "created_at"]:
            assert field in data

    def test_user_email_from_source(self, workspace_with_member, user):
        """Test: user_email čte z user.email."""
        from apps.workspaces.models import WorkspaceMembership

        membership = WorkspaceMembership.objects.filter(
            workspace=workspace_with_member, user=user
        ).first()
        data = WorkspaceMembershipSerializer(membership).data
        assert data["user_email"] == user.email

    def test_valid_membership_data(self, user):
        """Test: POST data pro přidání člena."""
        serializer = WorkspaceMembershipSerializer(data={"user": user.pk, "role": "member"})
        assert serializer.is_valid(), serializer.errors

    def test_invalid_role(self, user):
        """Test: Neplatná role selže validaci."""
        serializer = WorkspaceMembershipSerializer(data={"user": user.pk, "role": "superuser"})
        assert not serializer.is_valid()
        assert "role" in serializer.errors
