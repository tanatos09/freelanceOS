from rest_framework import serializers

from .models import Workspace, WorkspaceMembership


class WorkspaceSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ("id", "name", "slug", "plan", "is_active", "member_count", "created_at")
        read_only_fields = ("id", "member_count", "created_at")

    def get_member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("name", "slug")


class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = WorkspaceMembership
        fields = ("id", "user", "user_email", "role", "is_active", "created_at")
        read_only_fields = ("id", "created_at")
