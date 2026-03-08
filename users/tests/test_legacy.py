"""
Komplexní testy pro aplikaci `users`.

Pokrývá:
- Model User a UserProfile
- Validaci dat v serializerech
- Registraci, přihlášení, odhlášení
- Autentifikaci a oprávnění
- Výjimečné případy (neaktivní uživatel, špatná data, apod.)
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from users.serializers import (
    RegisterSerializer, 
    UserSerializer, 
    ChangePasswordSerializer
)

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# MODEL TESTS
# ─────────────────────────────────────────────────────────────────────────────

class UserModelTests(TestCase):
    """Testy pro User model."""
    
    def test_create_user_success(self):
        """Test: Vytvoření běžného uživatele."""
        user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_user_requires_email(self):
        """Test: Email je povinný."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email='', password='testpass123')
        self.assertIn('Email is required', str(context.exception))
    
    def test_create_user_email_normalized(self):
        """Test: Email doména je normalizována na lowercase (Django standard)."""
        user = User.objects.create_user(email='Test@EXAMPLE.COM', password='testpass123')
        # Django normalize_email normalizuje jen doménu, ne lokální část
        self.assertEqual(user.email, 'Test@example.com')
    
    def test_create_superuser_success(self):
        """Test: Vytvoření superuživatele."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_create_superuser_enforces_flags(self):
        """Test: Superuživatel musí mít is_staff=True a is_superuser=True."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
        self.assertIn('is_staff', str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )
        self.assertIn('is_superuser', str(context.exception))
    
    def test_user_str_representation(self):
        """Test: String reprezentace uživatele."""
        user = User.objects.create_user(email='test@example.com', password='pass')
        self.assertEqual(str(user), 'test@example.com')


class UserProfileModelTests(TestCase):
    """Testy pro UserProfile model."""
    
    def test_profile_created_automatically(self):
        """Test: UserProfile se vytváří automaticky při vytvoření User."""
        user = User.objects.create_user(email='test@example.com', password='pass')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user, user)
    
    def test_profile_default_values(self):
        """Test: Výchozí hodnoty UserProfile."""
        user = User.objects.create_user(email='test@example.com', password='pass')
        profile = user.profile
        self.assertEqual(profile.timezone, 'UTC')
        self.assertEqual(profile.locale, 'cs')
    
    def test_profile_str_representation(self):
        """Test: String reprezentace profilu."""
        user = User.objects.create_user(email='test@example.com', password='pass')
        expected = f'Profile({user.email})'
        self.assertEqual(str(user.profile), expected)


# ─────────────────────────────────────────────────────────────────────────────
# SERIALIZER TESTS
# ─────────────────────────────────────────────────────────────────────────────

class RegisterSerializerTests(TestCase):
    """Testy pro RegisterSerializer."""
    
    def test_valid_registration_data(self):
        """Test: Validní data pro registraci."""
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('securepass123'))
    
    def test_password_mismatch(self):
        """Test: Hesla se neshodují."""
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'differentpass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_missing_email(self):
        """Test: Chybí email."""
        data = {
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_missing_password(self):
        """Test: Chybí heslo."""
        data = {
            'email': 'newuser@example.com',
            'password2': 'securepass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_weak_password(self):
        """Test: Slabé heslo (Django standart, minimálně 8 znaků)."""
        data = {
            'email': 'newuser@example.com',
            'password': 'pass',
            'password2': 'pass'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_duplicate_email(self):
        """Test: Duplikátní email."""
        User.objects.create_user(email='test@example.com', password='pass123')
        data = {
            'email': 'test@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class UserSerializerTests(TestCase):
    """Testy pro UserSerializer."""
    
    def test_serialize_user(self):
        """Test: Serializace User objektu."""
        user = User.objects.create_user(email='test@example.com', password='pass')
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['id'], user.id)
        self.assertIn('created_at', data)
    
    def test_includes_profile_data(self):
        """Test: Serializer obsahuje data z profilu."""
        user = User.objects.create_user(email='test@example.com', password='pass')
        user.profile.timezone = 'Europe/Prague'
        user.profile.locale = 'en'
        user.profile.save()
        
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertEqual(data['timezone'], 'Europe/Prague')
        self.assertEqual(data['locale'], 'en')


class ChangePasswordSerializerTests(TestCase):
    """Testy pro ChangePasswordSerializer."""
    
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='oldpass123')
        self.request = type('Request', (), {'user': self.user})()
    
    def test_valid_password_change(self):
        """Test: Validní změna hesla."""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass456'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
    
    def test_wrong_old_password(self):
        """Test: Špatné staré heslo."""
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass456'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
    
    def test_weak_new_password(self):
        """Test: Slabé nové heslo."""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'weak'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)


# ─────────────────────────────────────────────────────────────────────────────
# API ENDPOINT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class AuthRegisterAPITests(APITestCase):
    """Testy pro endpoint /api/auth/register/"""
    
    def test_register_success(self):
        """Test: Úspěšná registrace."""
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
    
    def test_register_duplicate_email(self):
        """Test: Registrace s duplicitním emailem."""
        User.objects.create_user(email='existing@example.com', password='pass123')
        data = {
            'email': 'existing@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_password_mismatch(self):
        """Test: Hesla se neshodují."""
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'differentpass123'
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_register_weak_password(self):
        """Test: Slabé heslo."""
        data = {
            'email': 'newuser@example.com',
            'password': 'weak',
            'password2': 'weak'
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_missing_email(self):
        """Test: Chybí email."""
        data = {
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_creates_profile(self):
        """Test: Registrace vytváří UserProfile."""
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        self.client.post('/api/v1/auth/register/', data, format='json')
        user = User.objects.get(email='newuser@example.com')
        self.assertTrue(hasattr(user, 'profile'))


class AuthLoginAPITests(APITestCase):
    """Testy pro endpoint /api/auth/login/"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_success(self):
        """Test: Úspěšné přihlášení."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test: Špatná přihlašovací data."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_non_existent_user(self):
        """Test: Přihlášení neexistujícího uživatele."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_email(self):
        """Test: Chybí email."""
        data = {
            'password': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_missing_password(self):
        """Test: Chybí heslo."""
        data = {
            'email': 'test@example.com'
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_empty_fields(self):
        """Test: Prázdné pole."""
        data = {
            'email': '',
            'password': ''
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_case_insensitive(self):
        """Test: Login je case-insensitive pro email."""
        data = {
            'email': 'TEST@EXAMPLE.COM',
            'password': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_inactive_user(self):
        """Test: Přihlášení neaktivního uživatele."""
        self.user.is_active = False
        self.user.save()
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthLogoutAPITests(APITestCase):
    """Testy pro endpoint /api/auth/logout/"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
    
    def test_logout_success(self):
        """Test: Úspěšné odhlášení."""
        data = {'refresh': self.refresh_token}
        response = self.client.post('/api/v1/auth/logout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_missing_refresh_token(self):
        """Test: Chybí refresh token."""
        data = {}
        response = self.client.post('/api/v1/auth/logout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_invalid_token(self):
        """Test: Neplatný token."""
        data = {'refresh': 'invalid.token.here'}
        response = self.client.post('/api/v1/auth/logout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_requires_authentication(self):
        """Test: Logout vyžaduje autentifikaci."""
        self.client.force_authenticate(user=None)
        data = {'refresh': self.refresh_token}
        response = self.client.post('/api/v1/auth/logout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_blacklists_token(self):
        """Test: Token je po odhlášení zařazen na blacklist."""
        data = {'refresh': self.refresh_token}
        response = self.client.post('/api/v1/auth/logout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Pokus o refresh s blacklistovaným tokenem by měl selhat
        refresh_response = self.client.post(
            '/api/v1/auth/token/refresh/',
            {'refresh': self.refresh_token},
            format='json'
        )
        self.assertNotEqual(refresh_response.status_code, status.HTTP_200_OK)


class AuthMeAPITests(APITestCase):
    """Testy pro endpoint /api/auth/me/"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_me_authenticated(self):
        """Test: Autentifikovaný uživatel vidí své údaje."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_me_unauthenticated(self):
        """Test: Neautentifikovaný uživatel nemůže vidět /me/."""
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_me_returns_profile_data(self):
        """Test: /me/ vrací data z profilu."""
        self.user.profile.timezone = 'Europe/Prague'
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.data['timezone'], 'Europe/Prague')


class AuthChangePasswordAPITests(APITestCase):
    """Testy pro endpoint /api/auth/change-password/"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_change_password_success(self):
        """Test: Úspěšná změna hesla."""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass456'
        }
        response = self.client.post('/api/v1/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ověř, že lze přihlásit s novým heslem
        self.client.force_authenticate(user=None)
        login_response = self.client.post(
            '/api/v1/auth/login/',
            {'email': 'test@example.com', 'password': 'newpass456'},
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
    def test_change_password_wrong_old_password(self):
        """Test: Špatné staré heslo."""
        data = {
            'old_password': 'wrongoldpass',
            'new_password': 'newpass456'
        }
        response = self.client.post('/api/v1/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_weak_new_password(self):
        """Test: Slabé nové heslo."""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'weak'
        }
        response = self.client.post('/api/v1/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_requires_authentication(self):
        """Test: Změna hesla vyžaduje autentifikaci."""
        self.client.force_authenticate(user=None)
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass456'
        }
        response = self.client.post('/api/v1/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshAPITests(APITestCase):
    """Testy pro endpoint /api/auth/token/refresh/"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
    
    def test_token_refresh_success(self):
        """Test: Úspěšný refresh tokenu."""
        data = {'refresh': self.refresh_token}
        response = self.client.post('/api/v1/auth/token/refresh/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_token_refresh_invalid_token(self):
        """Test: Neplatný refresh token."""
        data = {'refresh': 'invalid.token.here'}
        response = self.client.post('/api/v1/auth/token/refresh/', data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
    
    def test_token_refresh_missing_token(self):
        """Test: Chybí refresh token."""
        data = {}
        response = self.client.post('/api/v1/auth/token/refresh/', data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class FullAuthFlowTests(APITestCase):
    """Integrace: Kompletní tok registrace, přihlášení, odhlášení."""
    
    def test_complete_auth_flow(self):
        """Test: Úplný tok - registrace → přihlášení → odhlášení."""
        # 1. Registrace
        register_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post('/api/v1/auth/register/', register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        refresh_token = response.data['refresh']
        access_token = response.data['access']
        
        # 2. Ověř, že se lze přihlásit
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        me_response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['email'], 'newuser@example.com')
        
        # 3. Odhlášení
        logout_data = {'refresh': refresh_token}
        logout_response = self.client.post('/api/v1/auth/logout/', logout_data, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # 4. Pokus o refresh - mělo by selhat
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post('/api/v1/auth/token/refresh/', refresh_data, format='json')
        self.assertNotEqual(refresh_response.status_code, status.HTTP_200_OK)
    
    def test_login_then_change_password_flow(self):
        """Test: Přihlášení → změna hesla → opět přihlášení."""
        # 1. Vytvoř uživatele
        user = User.objects.create_user(
            email='test@example.com',
            password='oldpass123'
        )
        
        # 2. Přihlaš se
        login_data = {
            'email': 'test@example.com',
            'password': 'oldpass123'
        }
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        
        # 3. Změň heslo
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        change_data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass456'
        }
        response = self.client.post('/api/v1/auth/change-password/', change_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Zkus přihlásit s novým heslem
        self.client.credentials()
        login_data = {
            'email': 'test@example.com',
            'password': 'newpass456'
        }
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
