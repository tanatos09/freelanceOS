from django.utils import timezone
from rest_framework import serializers

from .models import WorkCommit


class WorkCommitSerializer(serializers.ModelSerializer):
    is_running = serializers.BooleanField(read_only=True)
    is_paused = serializers.BooleanField(read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    duration_hours = serializers.SerializerMethodField()
    elapsed_seconds = serializers.SerializerMethodField()

    class Meta:
        model = WorkCommit
        fields = [
            "id",
            "project",
            "project_name",
            "start_time",
            "end_time",
            "description",
            "tag",
            "duration_seconds",
            "duration_hours",
            "is_running",
            "is_paused",
            "paused_at",
            "total_paused_seconds",
            "elapsed_seconds",
            "created_at",
        ]
        read_only_fields = ["id", "duration_seconds", "created_at"]

    def get_duration_hours(self, obj):
        return obj.duration_hours()

    def get_elapsed_seconds(self, obj):
        if obj.is_running:
            total = int((timezone.now() - obj.start_time).total_seconds())
            paused = obj.total_paused_seconds
            if obj.paused_at:
                paused += int((timezone.now() - obj.paused_at).total_seconds())
            return max(0, total - paused)
        return obj.duration_seconds

    def validate_tag(self, value):
        """Coerce empty string to None."""
        return value or None
