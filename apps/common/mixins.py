"""
Reusable model mixins for freelanceOS.
"""
from django.db import models


class WorkspaceOwnedMixin(models.Model):
    """Mixin for models that belong to a workspace (multi-tenancy)."""
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)ss',
    )

    class Meta:
        abstract = True
