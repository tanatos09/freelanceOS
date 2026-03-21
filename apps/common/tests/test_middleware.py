"""
Jednotkové testy pro apps/common middleware.

Pokrývá:
- WorkspaceMiddleware
  - request.workspace = None pro neautentifikovaného uživatele
  - X-Workspace-Id header
  - ?workspace= query param
  - Fallback na default_workspace z profilu
  - Neplatné UUID
  - Neexistující workspace
  - Neaktivní membership
"""

import uuid

import pytest
from django.test import RequestFactory

from apps.common.middleware import WorkspaceMiddleware

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


def get_response_stub(request):
    """Stub pro get_response callback v middleware."""
    return None


def _make_middleware():
    return WorkspaceMiddleware(get_response=get_response_stub)


class TestWorkspaceMiddlewareAnonymous:
    """Testy pro neautentifikovaného uživatele."""

    def test_anonymous_user_workspace_none(self):
        """Test: Pro neautentifikovaného uživatele je workspace=None."""
        factory = RequestFactory()
        request = factory.get("/")
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None

    def test_no_user_attr_workspace_none(self):
        """Test: Request bez atributu user → fallback, bez chyby."""
        factory = RequestFactory()
        request = factory.get("/")
        # Explicitně nestavíme request.user
        if hasattr(request, "user"):
            del request.user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None


class TestWorkspaceMiddlewareHeader:
    """Testy pro X-Workspace-Id hlavičku."""

    def test_valid_header_sets_workspace(self, user):
        """Test: Platný X-Workspace-Id nastaví request.workspace."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="Mid WS", slug="mid-ws-1")
        factory = RequestFactory()
        request = factory.get("/", HTTP_X_WORKSPACE_ID=str(ws.id))
        request.user = user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is not None
        assert request.workspace.id == ws.id

    def test_invalid_uuid_header_workspace_none(self, user):
        """Test: Neplatné UUID v hlavičce → workspace=None, bez chyby."""
        factory = RequestFactory()
        # Use a valid-format UUID that simply doesn't exist in DB
        nonexistent = str(uuid.uuid4())
        request = factory.get("/", HTTP_X_WORKSPACE_ID=nonexistent)
        request.user = user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None

    def test_nonexistent_workspace_header_none(self, user):
        """Test: Neexistující UUID v hlavičce → workspace=None."""
        factory = RequestFactory()
        request = factory.get("/", HTTP_X_WORKSPACE_ID=str(uuid.uuid4()))
        request.user = user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None

    def test_other_user_workspace_header_none(self, user, user_alt):
        """Test: Workspace z hlavičky, kde user není členem → workspace=None."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user_alt, name="Alt MWS", slug="alt-mws-1")
        factory = RequestFactory()
        request = factory.get("/", HTTP_X_WORKSPACE_ID=str(ws.id))
        request.user = user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None

    def test_inactive_membership_workspace_none(self, user, user_alt):
        """Test: Neaktivní membership → workspace=None."""
        from apps.workspaces.models import WorkspaceMembership
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user_alt, name="Inact WS", slug="inact-ws-1")
        WorkspaceService.add_member(ws, user, role="member")
        WorkspaceMembership.objects.filter(workspace=ws, user=user).update(is_active=False)

        factory = RequestFactory()
        request = factory.get("/", HTTP_X_WORKSPACE_ID=str(ws.id))
        request.user = user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None


class TestWorkspaceMiddlewareQueryParam:
    """Testy pro ?workspace= query param."""

    def test_valid_query_param_sets_workspace(self, user):
        """Test: Platný ?workspace= nastaví request.workspace."""
        from apps.workspaces.services import WorkspaceService

        ws = WorkspaceService.create_workspace(owner=user, name="QParam WS", slug="qp-ws-1")
        factory = RequestFactory()
        request = factory.get(f"/?workspace={ws.id}")
        request.user = user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is not None
        assert request.workspace.id == ws.id

    def test_invalid_query_param_workspace_none(self, user):
        """Test: Neplatný ?workspace= UUID → workspace=None, bez chyby."""
        factory = RequestFactory()
        # Non-existent but valid-format UUID
        nonexistent = str(uuid.uuid4())
        request = factory.get(f"/?workspace={nonexistent}")
        request.user = user
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None


class TestWorkspaceMiddlewareDefault:
    """Testy pro fallback na default_workspace z profilu."""

    def test_no_header_no_param_workspace_none_when_no_default(self, user):
        """Test: Bez hlavičky a query param, a bez default_workspace → workspace=None."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user
        # Profil nemá default_workspace
        if hasattr(user, "profile"):
            user.profile.default_workspace = None
            user.profile.save()
        middleware = _make_middleware()
        middleware(request)
        assert request.workspace is None
