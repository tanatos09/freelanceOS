from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Project(models.Model):
    """Reprezentuje projekt, který má freelancer u klienta."""

    # Status choices
    STATUS_CHOICES = [
        ("draft", "Návrh"),
        ("active", "Aktivní"),
        ("paused", "Pozastaveno"),
        ("pending_payment", "Čeká na platbu"),
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
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Hodinová sazba (0 = fallback na klienta)",
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
        """Procentuální postup projektu."""
        if not self.estimated_hours:
            return 0

        actual_hours = self.actual_hours()
        estimated_hours = float(self.estimated_hours)  # Ensure consistent types

        progress = (actual_hours / estimated_hours) * 100
        return min(progress, 100)  # Cap at 100%

    def actual_hours(self):
        """Součet odpracovaných hodin na projektu z WorkCommit záznamů."""
        from django.db.models import Sum
        from workcommits.models import WorkCommit

        total = WorkCommit.objects.filter(
            project=self, end_time__isnull=False
        ).aggregate(total=Sum("duration_seconds"))["total"]
        return round((total or 0) / 3600, 2)

    def effective_hourly_rate(self):
        """Efektivní hodinová sazba – projektová, nebo fallback na klienta."""
        if self.hourly_rate and self.hourly_rate > 0:
            return float(self.hourly_rate)
        try:
            client_rate = float(self.client.hourly_rate)
            if client_rate > 0:
                return client_rate
        except Exception:
            pass
        return 0

    def earnings(self):
        """Výdělek = odpracované hodiny × efektivní sazba."""
        return round(self.actual_hours() * self.effective_hourly_rate(), 2)
