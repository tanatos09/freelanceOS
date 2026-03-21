from django.utils import timezone
from rest_framework import serializers

from .models import WorkCommit


class WorkCommitSerializer(serializers.ModelSerializer):
    is_running = serializers.BooleanField(read_only=True)
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
            "elapsed_seconds",
            "created_at",
        ]
        read_only_fields = ["id", "duration_seconds", "created_at"]

    def get_duration_hours(self, obj):
        return obj.duration_hours()

    def get_elapsed_seconds(self, obj):
        if obj.is_running:
            return int((timezone.now() - obj.start_time).total_seconds())
        return obj.duration_seconds

    def validate_tag(self, value):
        """Coerce empty string to None."""
        return value or None
