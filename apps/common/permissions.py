"""
Custom permissions for freelanceOS.
"""

from rest_framework.permissions import BasePermission


class IsWorkspaceMember(BasePermission):
    """User must be an active member of the current workspace."""

    message = "Musíte být členem tohoto workspace."

    def has_permission(self, request, view):
        workspace = getattr(request, "workspace", None)
        if not workspace:
            return False
        return workspace.memberships.filter(
            user=request.user,
            is_active=True,
        ).exists()


class IsWorkspaceAdmin(BasePermission):
    """User must have admin or owner role in the current workspace."""

    message = "Vyžadováno oprávnění admin."

    def has_permission(self, request, view):
        workspace = getattr(request, "workspace", None)
        if not workspace:
            return False
        return workspace.memberships.filter(
            user=request.user,
            role__in=["admin", "owner"],
            is_active=True,
        ).exists()


class IsWorkspaceOwner(BasePermission):
    """User must be the owner of the current workspace."""

    message = "Vyžadováno oprávnění vlastníka workspace."

    def has_permission(self, request, view):
        workspace = getattr(request, "workspace", None)
        return workspace and workspace.owner == request.user
