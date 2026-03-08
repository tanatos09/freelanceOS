from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum

User = get_user_model()


class Client(models.Model):
    """Reprezentuje klienta (zákazníka) konkrétního freelancera."""

    # Relations
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="clients",
        null=True,
        blank=True,
        help_text="Workspace, do kterého klient patří",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="clients",
        help_text="Freelancer, kterému patří tento klient",
    )

    # Core fields
    name = models.CharField(max_length=255, help_text="Název firmy nebo jméno osoby")
    email = models.EmailField(help_text="Kontaktní email")
    phone = models.CharField(max_length=20, blank=True, help_text="Telefonní číslo")
    company = models.CharField(
        max_length=255, blank=True, help_text="Název společnosti (pokud se liší od name)"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Interní poznámky (není vidět klientovi)")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clients_client"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "name"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["user", "email"], name="unique_user_client_email"),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    def total_earnings(self):
        """Celkové příjmy z projektů tohoto klienta."""
        from projects.models import Project

        return Project.objects.filter(client=self).aggregate(total=Sum("budget"))["total"] or 0

    def project_count(self):
        """Počet projektů tohoto klienta."""
        from projects.models import Project

        return Project.objects.filter(client=self).count()
