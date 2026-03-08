from rest_framework import serializers
from .models import Client


class ClientListSerializer(serializers.ModelSerializer):
    """Legit seznam klientů (bez detailů pro výkon)."""

    total_earnings = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ("id", "name", "email", "company", "total_earnings", "project_count", "created_at")
        read_only_fields = ("total_earnings", "project_count", "created_at")

    def get_total_earnings(self, obj):
        """Cached total earnings."""
        return obj.total_earnings()

    def get_project_count(self, obj):
        """Cached project count."""
        return obj.project_count()


class ClientDetailSerializer(serializers.ModelSerializer):
    """Podrobný detail klienta s úplnými informacemi."""

    total_earnings = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "company",
            "notes",
            "total_earnings",
            "project_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("total_earnings", "project_count", "created_at", "updated_at")

    def get_total_earnings(self, obj):
        return obj.total_earnings()

    def get_project_count(self, obj):
        return obj.project_count()


class ClientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pro vytvoření a editaci klienta."""

    class Meta:
        model = Client
        fields = ("name", "email", "phone", "company", "notes")

    def validate_email(self, value):
        """Zkontroluj, že email je unikátní pro daného uživatele."""
        user = self.context["request"].user
        email_exists = Client.objects.filter(user=user, email=value).exists()

        # Pokud editujeme existující klienta, ignoruj jeho vlastní email
        if self.instance:
            email_exists = (
                Client.objects.filter(user=user, email=value).exclude(id=self.instance.id).exists()
            )

        if email_exists:
            raise serializers.ValidationError("Tento email již máš v klientech.")
        return value
