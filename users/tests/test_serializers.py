"""
Testy pro Django REST Framework serializery.

Pokrývá:
- Validaci vstupních dat
- Transformaci dat
- Chybové zprávy
"""

import pytest
from django.contrib.auth import get_user_model

from users.serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()
pytestmark = pytest.mark.unit


class TestRegisterSerializer:
    """Testy pro RegisterSerializer."""

    def test_valid_registration_data(self, db, user_data):
        """Test: Validní data pro registraci."""
        serializer = RegisterSerializer(data=user_data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == "newuser@example.com"
        assert user.check_password("securepass123")

    def test_password_validation_mismatch(self, db):
        """Test: Hesla se neshodují."""
        data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password2": "differentpass123",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_missing_email(self, db):
        """Test: Chybí email."""
        data = {"password": "securepass123", "password2": "securepass123"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_missing_password(self, db):
        """Test: Chybí heslo."""
        data = {"email": "newuser@example.com", "password2": "securepass123"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_missing_password_confirm(self, db):
        """Test: Chybí potvrzení hesla."""
        data = {"email": "newuser@example.com", "password": "securepass123"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password2" in serializer.errors

    def test_weak_password(self, db):
        """Test: Slabé heslo (Django standart, minimálně 8 znaků)."""
        data = {"email": "newuser@example.com", "password": "pass", "password2": "pass"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_duplicate_email(self, user):
        """Test: Duplikátní email."""
        data = {"email": user.email, "password": "securepass123", "password2": "securepass123"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_empty_email(self, db):
        """Test: Prázdný email."""
        data = {"email": "", "password": "securepass123", "password2": "securepass123"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors


class TestUserSerializer:
    """Testy pro UserSerializer."""

    def test_serialize_user(self, user):
        """Test: Serializace User objektu."""
        serializer = UserSerializer(user)
        data = serializer.data
        assert data["email"] == user.email
        assert data["id"] == user.id
        assert "created_at" in data

    def test_includes_timezone_from_profile(self, user):
        """Test: Serializer obsahuje timezone z profilu."""
        user.profile.timezone = "Europe/Prague"
        user.profile.save()

        serializer = UserSerializer(user)
        assert serializer.data["timezone"] == "Europe/Prague"

    def test_includes_locale_from_profile(self, user):
        """Test: Serializer obsahuje locale z profilu."""
        user.profile.locale = "en"
        user.profile.save()

        serializer = UserSerializer(user)
        assert serializer.data["locale"] == "en"

    def test_all_required_fields_present(self, user):
        """Test: Všechna požadovaná pole jsou přítomna."""
        serializer = UserSerializer(user)
        data = serializer.data
        required_fields = ["id", "email", "timezone", "locale", "created_at"]
        for field in required_fields:
            assert field in data

    def test_no_sensitive_data_exposed(self, user):
        """Test: Heslo a ostatní citlivá data nejsou v serializaci."""
        serializer = UserSerializer(user)
        data = serializer.data
        assert "password" not in data
        assert "is_staff" not in data
        assert "is_superuser" not in data


class TestChangePasswordSerializer:
    """Testy pro ChangePasswordSerializer."""

    def test_valid_password_change(self, db, user, rf):
        """Test: Validní změna hesla."""
        request = rf.post("/")
        request.user = user

        data = {"old_password": "testpass123", "new_password": "newpass456"}
        serializer = ChangePasswordSerializer(data=data, context={"request": request})
        assert serializer.is_valid()

    def test_wrong_old_password(self, db, user, rf):
        """Test: Špatné staré heslo."""
        request = rf.post("/")
        request.user = user

        data = {"old_password": "wrongpass", "new_password": "newpass456"}
        serializer = ChangePasswordSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "old_password" in serializer.errors

    def test_weak_new_password(self, db, user, rf):
        """Test: Slabé nové heslo."""
        request = rf.post("/")
        request.user = user

        data = {"old_password": "testpass123", "new_password": "weak"}
        serializer = ChangePasswordSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "new_password" in serializer.errors

    def test_missing_old_password(self, db, user, rf):
        """Test: Chybí staré heslo."""
        request = rf.post("/")
        request.user = user

        data = {"new_password": "newpass456"}
        serializer = ChangePasswordSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "old_password" in serializer.errors

    def test_missing_new_password(self, db, user, rf):
        """Test: Chybí nové heslo."""
        request = rf.post("/")
        request.user = user

        data = {"old_password": "testpass123"}
        serializer = ChangePasswordSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "new_password" in serializer.errors


class TestSerializerEdgeCases:
    """Edge case testy."""

    def test_register_with_special_characters_in_password(self, db):
        """Test: Heslo se speciálními znaky."""
        data = {
            "email": "test@example.com",
            "password": "P@ssw0rd!#$%",
            "password2": "P@ssw0rd!#$%",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()

    def test_register_email_with_plus_addressing(self, db):
        """Test: Email s plus addressing."""
        data = {
            "email": "test+alias@example.com",
            "password": "securepass123",
            "password2": "securepass123",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == "test+alias@example.com"
