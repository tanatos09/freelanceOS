import logging
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    GET /api/dashboard/stats/?range=today|week|month
    Vrátí základní statistiky pro dashboard.

    Supports workspace-scoped filtering via X-Workspace-Id header.
    """
    from django.db.models import Sum

    from clients.models import Client
    from projects.models import Project
    from workcommits.models import WorkCommit

    user = request.user
    workspace = getattr(request, "workspace", None)
    range_param = request.query_params.get("range", "today")

    try:
        # Always filter by user; additionally by workspace if present
        clients_qs = Client.objects.filter(user=user)
        projects_qs = Project.objects.filter(user=user)

        if workspace:
            clients_qs = clients_qs.filter(workspace=workspace)
            projects_qs = projects_qs.filter(workspace=workspace)

        today = timezone.localdate()
        overdue_count = projects_qs.filter(
            end_date__lt=today,
            status__in=["draft", "active"],
        ).count()

        # Determine date range start
        if range_param == "week":
            range_start = today - timedelta(days=today.weekday())  # Monday
        elif range_param == "month":
            range_start = today.replace(day=1)
        else:  # today
            range_start = today

        # WorkCommits in range (finished only)
        commits_qs = WorkCommit.objects.filter(
            user=user,
            start_time__date__gte=range_start,
            end_time__isnull=False,
        )
        if workspace:
            commits_qs = commits_qs.filter(project__workspace=workspace)

        # Hours worked in range
        total_seconds = commits_qs.aggregate(total=Sum("duration_seconds"))["total"] or 0
        hours_worked = round(total_seconds / 3600, 1)

        # Earnings in range: sum(duration × effective_hourly_rate) per project
        earnings_in_range = Decimal("0")
        project_seconds: dict = {}
        for commit in commits_qs.select_related("project__client"):
            pid = commit.project_id
            if pid not in project_seconds:
                project_seconds[pid] = {"secs": 0, "project": commit.project}
            project_seconds[pid]["secs"] += commit.duration_seconds
        for pid, entry in project_seconds.items():
            rate = Decimal(str(entry["project"].effective_hourly_rate()))
            hours = Decimal(str(entry["secs"])) / Decimal("3600")
            earnings_in_range += hours * rate

        data = {
            "clients_count": clients_qs.count(),
            "projects_count": projects_qs.count(),
            "active_projects_count": projects_qs.filter(status="active").count(),
            "overdue_projects_count": overdue_count,
            "range": range_param,
            "hours_worked": hours_worked,
            "earnings": float(round(earnings_in_range, 2)),
        }
    except Exception as e:
        logger.exception("Dashboard stats error for user %s: %s", user.pk, e)
        data = {
            "clients_count": 0,
            "projects_count": 0,
            "active_projects_count": 0,
            "overdue_projects_count": 0,
            "range": range_param,
            "hours_worked": 0,
            "earnings": 0,
        }

    return Response(data)
