from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard statistiky."""
    clients_count = serializers.IntegerField()
    projects_count = serializers.IntegerField()
    active_projects_count = serializers.IntegerField()
    overdue_projects_count = serializers.IntegerField()

