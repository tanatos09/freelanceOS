"""
Workspace models for multi-tenancy.

Every tenant-scoped resource in freelanceOS belongs to a Workspace.
Users access workspaces through WorkspaceMembership with role-based access.
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import BaseModel

User = get_user_model()


class Workspace(BaseModel):
    """A workspace / organization — the top-level tenant in the system."""

    PLAN_CHOICES = [
        ("free", "Free"),
        ("starter", "Starter"),
        ("professional", "Professional"),
        ("enterprise", "Enterprise"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owned_workspaces",
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "workspaces_workspace"
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorkspaceMembership(BaseModel):
    """Membership of a user in a workspace, with a role."""

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
        ("viewer", "Viewer"),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "workspaces_membership"
        unique_together = ("workspace", "user")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["workspace", "role"]),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.workspace.name} ({self.role})"
