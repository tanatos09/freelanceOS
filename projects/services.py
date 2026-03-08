from django.db.models import Sum

from .models import Project


class ProjectService:
    """Business layer - obchodní logika pro projekty."""

    @staticmethod
    def get_user_projects(user, filters=None, workspace=None):
        """
        Vrátí všechny projekty uživatele s podporou filtrů.

        If workspace is provided, filters by workspace (multi-tenant).
        Otherwise, falls back to user-based filtering.
        """
        if workspace:
            projects = Project.objects.filter(workspace=workspace)
        else:
            projects = Project.objects.filter(user=user)

        if not filters:
            return projects

        # Filter by status
        if filters.get("status"):
            projects = projects.filter(status=filters["status"])

        # Filter by client
        if filters.get("client_id"):
            projects = projects.filter(client_id=filters["client_id"])

        # Search by name
        if filters.get("search"):
            projects = projects.filter(name__icontains=filters["search"])

        # Filter by overdue
        if filters.get("overdue"):
            from django.utils import timezone

            today = timezone.now().date()
            projects = projects.filter(end_date__lt=today, status__in=["draft", "active"])

        return projects

    @staticmethod
    def create_project(user, workspace=None, **kwargs):
        """Vytvoří projekt (ověří ownership klienta)."""
        client = kwargs.get("client")
        if client.user != user:
            raise ValueError("Nemůžeš vytvářet projekty pro cizího klienta.")

        kwargs["user"] = user
        kwargs["workspace"] = workspace
        return Project.objects.create(**kwargs)

    @staticmethod
    def update_project(project, user, **kwargs):
        """Edituje projekt (ověří ownership)."""
        if project.user != user:
            raise ValueError("Nemůžeš editovat projekt, který ti nepatří.")

        # Zabánit změně uživatele
        if "user" in kwargs:
            del kwargs["user"]

        # Zabánit změně klienta v editaci (pokud to nechceš)
        if "client" in kwargs and kwargs["client"].user != user:
            raise ValueError("Nemůžeš přesunout projekt na cizího klienta.")

        for key, value in kwargs.items():
            setattr(project, key, value)
        project.save()
        return project

    @staticmethod
    def delete_project(project, user):
        """Smaže projekt (ověří ownership)."""
        if project.user != user:
            raise ValueError("Nemůžeš smazat projekt, který ti nepatří.")
        project.delete()

    @staticmethod
    def get_project_detail(user, project_id, workspace=None):
        """Vrátí detail projektu (ověří ownership)."""
        try:
            filters = {"id": project_id}
            if workspace:
                filters["workspace"] = workspace
            else:
                filters["user"] = user
            return Project.objects.get(**filters)
        except Project.DoesNotExist:
            return None

    @staticmethod
    def get_project_stats(user, workspace=None):
        """Vrátí statistiky všech projektů uživatele."""
        if workspace:
            projects = Project.objects.filter(workspace=workspace)
        else:
            projects = Project.objects.filter(user=user)

        return {
            "total_count": projects.count(),
            "active_count": projects.filter(status="active").count(),
            "completed_count": projects.filter(status="completed").count(),
            "overdue_count": sum(1 for p in projects if p.is_overdue()),
            "total_budget": projects.aggregate(Sum("budget"))["budget__sum"] or 0,
            "total_estimated_hours": projects.aggregate(Sum("estimated_hours"))[
                "estimated_hours__sum"
            ]
            or 0,
        }

    @staticmethod
    def get_client_projects(user, client_id):
        """Vrátí všechny projekty klienta (ověří ownership klienta)."""
        try:
            from clients.models import Client

            client = Client.objects.get(id=client_id, user=user)
            return Project.objects.filter(client=client)
        except Exception:
            return []
