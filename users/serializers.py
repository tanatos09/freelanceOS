from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Registrace nového uživatele."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Potvrdit heslo")

    class Meta:
        model = User
        fields = ("email", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Hesla se neshodují."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Veřejné info o přihlášeném uživateli."""

    timezone = serializers.CharField(source="profile.timezone", read_only=True)
    locale = serializers.CharField(source="profile.locale", read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "timezone", "locale", "created_at")
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    """Změna hesla přihlášeného uživatele."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Staré heslo je nesprávné.")
        return value
