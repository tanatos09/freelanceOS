from django.conf import settings
from django.db import models
from django.utils import timezone


class WorkCommit(models.Model):
    """
    Represents a timed work segment on a project.
    end_time=None means the timer is currently running.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_commits",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="work_commits",
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, default="")
    tag = models.CharField(max_length=50, null=True, blank=True, default=None)
    duration_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workcommits_workcommit"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["user", "-start_time"]),
            models.Index(fields=["user", "end_time"]),
            models.Index(fields=["project", "-start_time"]),
        ]

    def __str__(self):
        return f"{self.project.name} – {self.start_time:%Y-%m-%d %H:%M}"

    @property
    def is_running(self):
        return self.end_time is None

    def stop(self, description=""):
        """Stop the timer and compute duration."""
        if self.is_running:
            self.end_time = timezone.now()
            if description:
                self.description = description
            delta = self.end_time - self.start_time
            self.duration_seconds = max(0, int(delta.total_seconds()))
            self.save()

    def duration_hours(self):
        if self.is_running:
            return round((timezone.now() - self.start_time).total_seconds() / 3600, 2)
        return round(self.duration_seconds / 3600, 2)
