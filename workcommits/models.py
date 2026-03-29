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
    paused_at = models.DateTimeField(null=True, blank=True)
    total_paused_seconds = models.IntegerField(default=0)
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

    @property
    def is_paused(self):
        return self.is_running and self.paused_at is not None

    def pause(self):
        """Pause the running timer."""
        if self.is_running and not self.is_paused:
            self.paused_at = timezone.now()
            self.save(update_fields=["paused_at"])

    def resume(self):
        """Resume a paused timer, accumulating the pause duration."""
        if self.is_paused:
            paused_duration = int((timezone.now() - self.paused_at).total_seconds())
            self.total_paused_seconds += paused_duration
            self.paused_at = None
            self.save(update_fields=["paused_at", "total_paused_seconds"])

    def stop(self, description=""):
        """Stop the timer and compute actual work duration (excluding paused time)."""
        if self.is_running:
            if self.is_paused:
                paused_duration = int((timezone.now() - self.paused_at).total_seconds())
                self.total_paused_seconds += paused_duration
                self.paused_at = None
            self.end_time = timezone.now()
            if description:
                self.description = description
            total_elapsed = int((self.end_time - self.start_time).total_seconds())
            self.duration_seconds = max(0, total_elapsed - self.total_paused_seconds)
            self.save()

    def duration_hours(self):
        if self.is_running:
            return round((timezone.now() - self.start_time).total_seconds() / 3600, 2)
        return round(self.duration_seconds / 3600, 2)
