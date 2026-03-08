from rest_framework import serializers
from .models import Project


class ProjectListSerializer(serializers.ModelSerializer):
    """Seznam projektů (optimalizováno pro výkon)."""
    client_name = serializers.CharField(source='client.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'client', 'client_name', 'status', 'status_display',
            'budget', 'estimated_hours', 'end_date', 'is_overdue', 'progress', 'created_at'
        )
        read_only_fields = ('client_name', 'is_overdue', 'progress', 'created_at')
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_progress(self, obj):
        return obj.progress_percent()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Podrobný detail projektu."""
    client_name = serializers.CharField(source='client.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    actual_hours = serializers.SerializerMethodField()
    hourly_rate = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'client', 'client_name',
            'status', 'status_display', 'budget', 'estimated_hours',
            'start_date', 'end_date', 'is_overdue', 'days_until_deadline',
            'progress', 'actual_hours', 'hourly_rate',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'client_name', 'is_overdue', 'days_until_deadline', 'progress',
            'actual_hours', 'hourly_rate', 'created_at', 'updated_at'
        )
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_days_until_deadline(self, obj):
        return obj.days_until_deadline()
    
    def get_progress(self, obj):
        return obj.progress_percent()
    
    def get_actual_hours(self, obj):
        return obj.actual_hours()
    
    def get_hourly_rate(self, obj):
        return obj.hourly_rate()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Pro vytváření a editaci projektů."""
    
    class Meta:
        model = Project
        fields = (
            'name', 'description', 'client', 'status', 'budget',
            'estimated_hours', 'start_date', 'end_date'
        )
    
    def validate_client(self, value):
        """Zkontroluj ownership klienta."""
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Tento klient ti nepatří.")
        return value
    
    def validate_budget(self, value):
        """Budget musí být >= 0."""
        if value < 0:
            raise serializers.ValidationError("Rozpočet nemůže být záporný.")
        return value
    
    def validate_estimated_hours(self, value):
        """Odhadnuté hodiny musí být >= 0."""
        if value < 0:
            raise serializers.ValidationError("Hodiny nemohou být záporné.")
        return value
    
    def validate(self, data):
        """Prověř logiku datumů."""
        start_date = data.get('start_date') or self.instance.start_date if self.instance else None
        end_date = data.get('end_date') or self.instance.end_date if self.instance else None
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Datum začátku musí být před deadline."
            )
        return data
