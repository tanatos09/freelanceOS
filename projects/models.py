from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Project(models.Model):
    """Reprezentuje projekt, který má freelancer u klienta."""

    # Status choices
    STATUS_CHOICES = [
        ("draft", "Návrh"),
        ("active", "Aktivní"),
        ("completed", "Hotovo"),
        ("archived", "Archivováno"),
        ("cancelled", "Zrušeno"),
    ]

    # Relations
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
        help_text="Workspace, do kterého projekt patří",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        help_text="Freelancer, který má projekt",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="projects",
        help_text="Klient, pro kterého je projekt",
    )

    # Core fields
    name = models.CharField(max_length=255, help_text="Název projektu")
    description = models.TextField(blank=True, help_text="Podrobný popis projektu")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", help_text="Status projektu"
    )

    # Budget & Hours
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Celkový rozpočet projektu"
    )
    estimated_hours = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, help_text="Odhadnuté hodiny"
    )

    # Dates
    start_date = models.DateField(null=True, blank=True, help_text="Datum začátku projektu")
    end_date = models.DateField(null=True, blank=True, help_text="Deadline projektu")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects_project"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["client", "-created_at"]),
            models.Index(fields=["user", "status", "-end_date"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.client.name})"

    def is_overdue(self):
        """Je projekt po deadlinu?"""
        if not self.end_date or self.status in ["completed", "cancelled"]:
            return False
        return self.end_date < timezone.now().date()

    def days_until_deadline(self):
        """Počet dní do deadlinu (negativní = po deadline)."""
        if not self.end_date:
            return None
        delta = self.end_date - timezone.now().date()
        return delta.days

    def progress_percent(self):
        """Procenta hotovosti (dle hodin nebo na základě estimace)."""
        if not self.estimated_hours or self.estimated_hours == 0:
            return 0

        actual_hours = self.actual_hours()
        if actual_hours == 0:
            return 0

        progress = (actual_hours / self.estimated_hours) * 100
        return min(100, round(progress, 1))  # Max 100%

    def actual_hours(self):
        """Součet všech hodin na tomto projektu."""
        # TODO: Integrace s timetracking app
        # Zatím vrátíme 0 - later bude načítcat z TimeEntry
        try:
            from timetracking.models import TimeEntry

            total = TimeEntry.objects.filter(project=self).aggregate(
                total=models.Sum("duration_hours")
            )["total"]
            return total or 0
        except (ImportError, ModuleNotFoundError):
            # Timetracking aplikace ainda není k dispozici
            return 0

    def hourly_rate(self):
        """Vypočtená hodinová sazba (rozpočet / odhad hodin)."""
        if not self.estimated_hours or self.estimated_hours == 0:
            return 0
        return round(float(self.budget) / float(self.estimated_hours), 2)
