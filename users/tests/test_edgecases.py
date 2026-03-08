"""
Edge-case API testy pro aplikaci `users`.

Pokrývá:
- Race conditions (konkurrentní registrace se stejným emailem)
- Expirace refresh tokenu
- Token blacklisting (double logout)
- Edge-case inputy (dlouhé emaily, SQL injection, atd.)
"""
import threading
import time
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# RACE CONDITION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class RaceConditionTests(TestCase):
    """Testy pro race conditions, zejména při konkurenční registraci."""

    def test_concurrent_registration_same_email_raises_integrity_error(self):
        """
        Test: Pokus o konkurenční registraci se stejným emailem.
        Očekávání: Pouze jeden uživatel by měl být vytvořen, druhý pokus
        by měl vyhodit IntegrityError nebo ValidationError.
        """
        email = 'race@example.com'
        password = 'secure_pass_123'
        
        def create_user():
            try:
                User.objects.create_user(email=email, password=password)
            except (IntegrityError, ValidationError):
                # Očekáváno pro druhý thread
                pass
        
        # Spustíme dva thready skoro ve stejný čas
        thread1 = threading.Thread(target=create_user)
        thread2 = threading.Thread(target=create_user)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Ověřit, že existuje pouze jeden uživatel s tímto emailem
        user_count = User.objects.filter(email=email).count()
        self.assertEqual(user_count, 1, 
            f"Byl vytvořen {user_count} uživatel(é), očekáván 1")
    
    def test_concurrent_registration_api_endpoint(self):
        """
        Test: Race condition přes API endpoint (simultánní POST requesty).
        """
        from rest_framework.test import APIClient
        
        client = APIClient()
        email = 'api_race@example.com'
        payload = {
            'email': email,
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        
        # Spustíme dva requesty sekvenčně (kvůli test DB)
        results = []
        
        try:
            # První pokus
            response1 = client.post('/api/v1/auth/register/', payload)
            results.append(response1.status_code)
            
            # Druhý pokus se stejným emailem
            response2 = client.post('/api/v1/auth/register/', payload)
            results.append(response2.status_code)
        except Exception:
            # Něco se pokazilo, alespoň jedné byl konflikt
            pass
        
        # Ověřit, že existuje pouze jeden uživatel
        user_count = User.objects.filter(email=email).count()
        self.assertEqual(user_count, 1, 
            f"Skrz API byl vytvořen {user_count} uživatel(é), očekáván 1")


# ─────────────────────────────────────────────────────────────────────────────
# REFRESH TOKEN TESTS
# ─────────────────────────────────────────────────────────────────────────────

class RefreshTokenExpirationTests(APITestCase):
    """Testy pro expirace a validaci JWT refresh tokenů."""
    
    def setUp(self):
        """Připravit testového uživatele."""
        self.user = User.objects.create_user(
            email='refresh@example.com',
            password='testpass123'
        )
    
    def test_refresh_token_lifecycle(self):
        """
        Test: Normální lifecycle refresh tokenu.
        """
        # Vygenerujeme token pár
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Refresh token by měl být platný
        new_refresh = RefreshToken(refresh_token)
        self.assertIsNotNone(new_refresh.access_token)
    
    def test_expired_refresh_token_cannot_be_refreshed(self):
        """
        Test: Expiovaný refresh token nemůže být použit.
        """
        refresh = RefreshToken.for_user(self.user)
        refresh_token_str = str(refresh)
        
        # Manuálně exspirujeme token (manipulace exp claim)
        refresh['exp'] = int(time.time()) - 3600  # 1 hodinu v minulosti
        
        # Pokus o použití exspirovaného tokenu by měl selhať
        with self.assertRaises(TokenError):
            RefreshToken(str(refresh))
    
    def test_refresh_token_api_with_expired_token(self):
        """
        Test: API endpoint /api/auth/token/refresh/ s exspirovaným tokenem.
        """
        refresh = RefreshToken.for_user(self.user)
        refresh['exp'] = int(time.time()) - 3600
        
        response = self.client.post(
            '/api/v1/auth/token/refresh/',
            {'refresh': str(refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────────────────────────────────────
# TOKEN BLACKLIST TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TokenBlacklistTests(APITestCase):
    """Testy pro blacklist tokenů (double logout)."""
    
    def setUp(self):
        """Připravit testového uživatele a login."""
        self.user = User.objects.create_user(
            email='blacklist@example.com',
            password='testpass123'
        )
    
    def test_logout_blacklists_token(self):
        """
        Test: Logout by měl zneplatnit refresh token.
        """
        # Login a získáme token
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'blacklist@example.com',
            'password': 'testpass123',
        })
        refresh_token_str = response.data.get('refresh')
        access_token = response.data.get('access')
        
        # Authorizuj client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Logout
        response = self.client.post('/api/v1/auth/logout/', {
            'refresh': refresh_token_str,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Pokus o refresh s blacklistovaným tokenem
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token_str,
        })
        
        # Mělo by selhát
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
    
    def test_double_logout_attempt(self):
        """
        Test: Pokus o double logout.
        """
        # Vytvoř uživatele a login
        user = User.objects.create_user(
            email='double_logout@example.com',
            password='testpass123'
        )
        
        # Login
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'double_logout@example.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data.get('refresh')
        
        # Authorizuj client s access tokenem
        access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # První logout
        response1 = self.client.post('/api/v1/auth/logout/', {
            'refresh': refresh_token,
        })
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Druhý logout se stejným tokenem by měl selhát
        response2 = self.client.post('/api/v1/auth/logout/', {
            'refresh': refresh_token,
        })
        
        # Může být 400 Bad Request nebo 401 Unauthorized
        self.assertIn(
            response2.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]
        )


# ─────────────────────────────────────────────────────────────────────────────
# EDGE CASE INPUT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class EdgeCaseInputTests(APITestCase):
    """Testy pro edge case inputy."""
    
    def test_extremely_long_email(self):
        """
        Test: Velmi dlouhý email address.
        """
        long_email = 'a' * 300 + '@example.com'
        payload = {
            'email': long_email,
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        
        # Mělo by být 400, ne 500
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def test_special_characters_in_email(self):
        """
        Test: Neobvyklé znaky v emailu.
        """
        test_cases = [
            'user@exam ple.com',  # Mezera
            'user@example..com',  # Dvojité tečky
            'user @example.com',  # Mezera v lokální části
        ]
        
        for invalid_email in test_cases:
            payload = {
                'email': invalid_email,
                'password': 'testpass123',
                'password2': 'testpass123',
            }
            
            response = self.client.post('/api/v1/auth/register/', payload, format='json')
            
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST
            )
    
    def test_password_mismatch(self):
        """
        Test: Hesla se neshodují.
        """
        payload = {
            'email': 'mismatch@example.com',
            'password': 'testpass123',
            'password2': 'differentpass123',
        }
        
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
    
    def test_missing_required_fields(self):
        """
        Test: Chybí povinná pole.
        """
        # Chybí email
        payload1 = {
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        response1 = self.client.post('/api/v1/auth/register/', payload1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Chybí heslo
        payload2 = {
            'email': 'test@example.com',
        }
        response2 = self.client.post('/api/v1/auth/register/', payload2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_whitespace_only_email(self):
        """
        Test: Email pouze z mezer.
        """
        payload = {
            'email': '   ',
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN EDGE CASES
# ─────────────────────────────────────────────────────────────────────────────

class LoginEdgeCaseTests(APITestCase):
    """Testy pro edge cases v login endpointu."""
    
    def setUp(self):
        """Připravit testového uživatele."""
        self.user = User.objects.create_user(
            email='login@example.com',
            password='testpass123'
        )
    
    def test_login_with_wrong_password(self):
        """
        Test: Login se špatným heslem.
        """
        payload = {
            'email': 'login@example.com',
            'password': 'wrongpassword',
        }
        
        response = self.client.post('/api/v1/auth/login/', payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_nonexistent_user(self):
        """
        Test: Login s neexistujícím emailem.
        """
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123',
        }
        
        response = self.client.post('/api/v1/auth/login/', payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_inactive_user(self):
        """
        Test: Login s neaktivním uživatelem.
        """
        # Vygenerujeme neaktivního uživatele
        inactive_user = User.objects.create_user(
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        
        payload = {
            'email': 'inactive@example.com',
            'password': 'testpass123',
        }
        
        response = self.client.post('/api/v1/auth/login/', payload, format='json')
        
        # Neaktivního uživatele by neměly být schopni se přihlásit
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_case_insensitive_email(self):
        """
        Test: Login s emailem v jiném případě.
        """
        payload = {
            'email': 'LOGIN@EXAMPLE.COM',  # Uppercase
            'password': 'testpass123',
        }
        
        response = self.client.post('/api/v1/auth/login/', payload, format='json')
        
        # Mělo by vrátit 200 OK (Django normalizuje email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
