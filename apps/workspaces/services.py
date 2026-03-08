"""
Workspace business logic.
"""
from django.utils.text import slugify
from apps.common.exceptions import NotFoundError, BusinessError
from .models import Workspace, WorkspaceMembership


class WorkspaceService:
    @staticmethod
    def create_workspace(owner, name, slug=None):
        """Create a new workspace and add owner as member."""
        if not slug:
            slug = slugify(name)

        # Ensure slug uniqueness
        base_slug = slug
        counter = 1
        while Workspace.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        workspace = Workspace.objects.create(
            name=name,
            slug=slug,
            owner=owner,
        )
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=owner,
            role="owner",
        )
        return workspace

    @staticmethod
    def get_user_workspaces(user):
        """Get all active workspaces for a user."""
        return Workspace.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
            is_active=True,
        ).distinct()

    @staticmethod
    def get_workspace(workspace_id):
        try:
            return Workspace.objects.get(id=workspace_id, is_active=True)
        except Workspace.DoesNotExist:
            raise NotFoundError("Workspace nenalezen.")

    @staticmethod
    def add_member(workspace, user, role="member"):
        """Add a user to a workspace."""
        membership, created = WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=user,
            defaults={"role": role},
        )
        if not created:
            if membership.is_active:
                raise BusinessError("Uživatel je již členem tohoto workspace.")
            membership.is_active = True
            membership.role = role
            membership.save()
        return membership

    @staticmethod
    def remove_member(workspace, user):
        """Remove a user from a workspace (soft)."""
        try:
            membership = WorkspaceMembership.objects.get(
                workspace=workspace,
                user=user,
            )
        except WorkspaceMembership.DoesNotExist:
            raise NotFoundError("Členství nenalezeno.")

        if membership.role == "owner":
            raise BusinessError("Nelze odebrat vlastníka workspace.")

        membership.is_active = False
        membership.save()

    @staticmethod
    def change_role(workspace, user, new_role):
        """Change a user's role in a workspace."""
        try:
            membership = WorkspaceMembership.objects.get(
                workspace=workspace,
                user=user,
            )
        except WorkspaceMembership.DoesNotExist:
            raise NotFoundError("Členství nenalezeno.")

        if membership.role == "owner" and new_role != "owner":
            raise BusinessError("Nelze změnit roli vlastníka workspace.")

        membership.role = new_role
        membership.save()
        return membership
