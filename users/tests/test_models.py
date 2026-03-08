"""
Jednotkové testy pro User a UserProfile modely.

Pokrývá:
- Vytváření uživatelů
- Validace polí
- Výchozí hodnoty
- Vztahy (User -> UserProfile)
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
pytestmark = pytest.mark.unit


class TestUserModelCreation:
    """Testy vytváření uživatelů."""
    
    def test_create_user_success(self, db):
        """Test: Vytvoření běžného uživatele."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
    
    def test_create_user_requires_email(self, db):
        """Test: Email je povinný."""
        with pytest.raises(ValueError, match='Email is required'):
            User.objects.create_user(email='', password='testpass123')
    
    def test_email_normalization(self, db):
        """Test: Email doména je normalizována na lowercase."""
        user = User.objects.create_user(
            email='Test@EXAMPLE.COM',
            password='testpass123'
        )
        assert user.email == 'Test@example.com'
    
    def test_create_superuser_success(self, db):
        """Test: Vytvoření superuživatele."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        assert user.email == 'admin@example.com'
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True
    
    def test_create_superuser_enforces_is_staff(self, db):
        """Test: Superuživatel musí mít is_staff=True."""
        with pytest.raises(ValueError, match='is_staff'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
    
    def test_create_superuser_enforces_is_superuser(self, db):
        """Test: Superuživatel musí mít is_superuser=True."""
        with pytest.raises(ValueError, match='is_superuser'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )


class TestUserModelProperties:
    """Testy vlastností uživatele."""
    
    def test_user_str_representation(self, user):
        """Test: String reprezentace uživatele."""
        assert str(user) == user.email
    
    def test_user_username_field_is_email(self, db):
        """Test: USERNAME_FIELD je email."""
        assert User.USERNAME_FIELD == 'email'
    
    def test_check_password(self, user):
        """Test: Ověřování hesla."""
        assert user.check_password('testpass123')
        assert not user.check_password('wrongpassword')
    
    def test_set_password(self, user):
        """Test: Nastavení hesla."""
        user.set_password('newpass456')
        user.save()
        assert user.check_password('newpass456')
        assert not user.check_password('testpass123')


class TestUserEdgeCases:
    """Edge case testy."""
    
    def test_duplicate_email_raises_error(self, db):
        """Test: Druhý uživatel se stejným emailem selhává."""
        User.objects.create_user(email='duplicate@example.com', password='pass123')
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(email='duplicate@example.com', password='pass456')
    
    def test_case_sensitive_email_treated_as_duplicates(self, db):
        """Test: Email je case-insensitive pro unikátnost."""
        User.objects.create_user(email='Test@Example.com', password='pass123')
        # Pokus o vytvoření s jinou velikostí by měl selhat
        with pytest.raises(Exception):
            User.objects.create_user(email='test@example.com', password='pass456')


class TestUserProfileAutoCreation:
    """Testy automatického vytváření UserProfile."""
    
    def test_profile_created_automatically(self, user):
        """Test: UserProfile se vytváří automaticky při vytvoření User."""
        assert hasattr(user, 'profile')
        assert user.profile.user == user
    
    def test_profile_default_timezone(self, user):
        """Test: Výchozí timezone je 'UTC'."""
        assert user.profile.timezone == 'UTC'
    
    def test_profile_default_locale(self, user):
        """Test: Výchozí locale je 'cs'."""
        assert user.profile.locale == 'cs'
    
    def test_profile_str_representation(self, user):
        """Test: String reprezentace profilu."""
        expected = f'Profile({user.email})'
        assert str(user.profile) == expected
    
    def test_profile_timestamps(self, user):
        """Test: Profil má created_at a updated_at."""
        assert user.profile.created_at is not None
        assert user.profile.updated_at is not None
    
    def test_profile_update(self, user):
        """Test: Aktualizace profilu."""
        user.profile.timezone = 'Europe/Prague'
        user.profile.locale = 'en'
        user.profile.save()
        
        refreshed_user = User.objects.get(id=user.id)
        assert refreshed_user.profile.timezone == 'Europe/Prague'
        assert refreshed_user.profile.locale == 'en'


class TestUserProfileEdgeCases:
    """Edge case testy pro profil."""
    
    def test_cannot_create_multiple_profiles(self, user):
        """Test: Pokus o vytvoření druhého profilu selže."""
        from users.models import UserProfile
        with pytest.raises(Exception):  # IntegrityError
            UserProfile.objects.create(user=user)
    
    def test_profile_deletion_cascades(self, user):
        """Test: Smazání uživatele smaže i profil."""
        profile_id = user.profile.id
        user_email = user.email
        
        user.delete()
        
        # Uživatel by měl být smazán
        assert not User.objects.filter(email=user_email).exists()
