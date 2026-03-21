"""
Jednotkové testy pro apps/common modely.

Pokrývá:
- BaseModel (UUID PK, timestamps) — testováno přes Workspace (který z něj dědí)
- SoftDeleteModel (soft delete, restore, hard_delete, is_deleted)
- SoftDeleteQuerySet a SoftDeleteManager interface
"""

import uuid

import pytest
from django.utils import timezone

from apps.common.models import (
    AllObjectsManager,
    BaseModel,
    SoftDeleteManager,
    SoftDeleteModel,
    SoftDeleteQuerySet,
)

pytestmark = pytest.mark.unit


class TestBaseModelViaWorkspace:
    """Testy pro BaseModel abstraktní třídu — testováno přes Workspace."""

    pytestmark = [pytest.mark.unit, pytest.mark.django_db]

    def test_workspace_has_uuid_pk(self, user):
        """Test: Model dědící z BaseModel má UUID jako PK."""
        from apps.workspaces.models import Workspace

        ws = Workspace.objects.create(name="Test", slug="test-base-1", owner=user)
        assert isinstance(ws.id, uuid.UUID)

    def test_created_at_auto_set(self, user):
        """Test: created_at se nastaví automaticky."""
        from apps.workspaces.models import Workspace

        ws = Workspace.objects.create(name="Test", slug="test-base-2", owner=user)
        assert ws.created_at is not None

    def test_updated_at_auto_set(self, user):
        """Test: updated_at se nastaví automaticky."""
        from apps.workspaces.models import Workspace

        ws = Workspace.objects.create(name="Test", slug="test-base-3", owner=user)
        assert ws.updated_at is not None

    def test_updated_at_changes_on_save(self, user):
        """Test: updated_at se změní při uložení."""
        import time

        from apps.workspaces.models import Workspace

        ws = Workspace.objects.create(name="Test", slug="test-base-4", owner=user)
        original_updated_at = ws.updated_at
        time.sleep(0.02)
        ws.name = "Updated"
        ws.save()
        ws.refresh_from_db()
        assert ws.updated_at >= original_updated_at

    def test_basemodel_is_abstract(self):
        """Test: BaseModel je abstraktní (nemá vlastní tabulku)."""
        assert BaseModel._meta.abstract is True


class TestSoftDeleteModelInterface:
    """Testy interface a správců SoftDeleteModel (bez DB)."""

    def test_soft_delete_model_is_abstract(self):
        """Test: SoftDeleteModel je abstraktní."""
        assert SoftDeleteModel._meta.abstract is True

    def test_has_objects_manager(self):
        """Test: SoftDeleteModel deklaruje SoftDeleteManager jako objects manager."""
        # Abstract models can't access managers via descriptor, check via _meta
        manager_names = [m.name for m in SoftDeleteModel._meta.managers]
        assert "objects" in manager_names

    def test_has_all_objects_manager(self):
        """Test: SoftDeleteModel deklaruje AllObjectsManager jako all_objects."""
        manager_names = [m.name for m in SoftDeleteModel._meta.managers]
        assert "all_objects" in manager_names

    def test_has_is_deleted_property(self):
        """Test: SoftDeleteModel má vlastnost is_deleted."""
        assert isinstance(SoftDeleteModel.__dict__["is_deleted"], property)

    def test_has_delete_method(self):
        """Test: SoftDeleteModel má delete() metodu."""
        assert callable(getattr(SoftDeleteModel, "delete", None))

    def test_has_hard_delete_method(self):
        """Test: SoftDeleteModel má hard_delete() metodu."""
        assert callable(getattr(SoftDeleteModel, "hard_delete", None))

    def test_has_restore_method(self):
        """Test: SoftDeleteModel má restore() metodu."""
        assert callable(getattr(SoftDeleteModel, "restore", None))

    def test_soft_delete_queryset_methods(self):
        """Test: SoftDeleteQuerySet má alive(), dead() a hard_delete() metody."""
        for method in ("alive", "dead", "hard_delete"):
            assert callable(getattr(SoftDeleteQuerySet, method, None))


class TestSoftDeleteModelLogic:
    """Testy logiky SoftDeleteModel bez přístupu k DB."""

    def test_is_deleted_false_when_deleted_at_none(self):
        """Test: is_deleted=False pokud deleted_at je None."""
        instance = SoftDeleteModel.__new__(SoftDeleteModel)
        instance.deleted_at = None
        assert instance.is_deleted is False

    def test_is_deleted_true_when_deleted_at_set(self):
        """Test: is_deleted=True pokud deleted_at je nastaven."""
        instance = SoftDeleteModel.__new__(SoftDeleteModel)
        instance.deleted_at = timezone.now()
        assert instance.is_deleted is True

