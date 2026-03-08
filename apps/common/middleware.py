"""
Workspace middleware for multi-tenancy.

Sets request.workspace based on:
1. X-Workspace-Id header
2. ?workspace= query parameter
3. User's default workspace from profile
"""
import logging

logger = logging.getLogger(__name__)


class WorkspaceMiddleware:
    """Resolves the current workspace for authenticated requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.workspace = None

        if hasattr(request, "user") and request.user.is_authenticated:
            workspace_id = request.headers.get("X-Workspace-Id") or request.GET.get("workspace")

            if workspace_id:
                from apps.workspaces.models import Workspace

                try:
                    request.workspace = Workspace.objects.get(
                        id=workspace_id,
                        memberships__user=request.user,
                        memberships__is_active=True,
                        is_active=True,
                    )
                except (Workspace.DoesNotExist, ValueError):
                    logger.warning(
                        "Invalid workspace %s for user %s",
                        workspace_id,
                        request.user.id,
                    )
            else:
                # Fall back to user's default workspace
                profile = getattr(request.user, "profile", None)
                if profile and getattr(profile, "default_workspace", None):
                    request.workspace = profile.default_workspace

        return self.get_response(request)
