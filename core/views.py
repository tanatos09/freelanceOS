import logging

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    GET /api/dashboard/stats/
    Vrátí základní statistiky pro dashboard.

    Supports workspace-scoped filtering via X-Workspace-Id header.
    """
    from clients.models import Client
    from projects.models import Project

    user = request.user
    workspace = getattr(request, "workspace", None)

    try:
        # Always filter by user; additionally by workspace if present
        clients_qs = Client.objects.filter(user=user)
        projects_qs = Project.objects.filter(user=user)

        if workspace:
            clients_qs = clients_qs.filter(workspace=workspace)
            projects_qs = projects_qs.filter(workspace=workspace)

        today = timezone.now().date()
        overdue_count = projects_qs.filter(
            end_date__lt=today,
            status__in=["draft", "active"],
        ).count()

        data = {
            "clients_count": clients_qs.count(),
            "projects_count": projects_qs.count(),
            "active_projects_count": projects_qs.filter(status="active").count(),
            "overdue_projects_count": overdue_count,
        }
    except Exception as e:
        logger.exception("Dashboard stats error for user %s: %s", user.pk, e)
        data = {
            "clients_count": 0,
            "projects_count": 0,
            "active_projects_count": 0,
            "overdue_projects_count": 0,
        }

    return Response(data)
