"""
Production settings for freelanceOS.
"""

import dj_database_url

from .base import *  # noqa: F401, F403

DEBUG = False

# Security
# Render terminates SSL at the load balancer — use proxy header instead of redirect
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Static files — WhiteNoise compressed + cached storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Database — parse DATABASE_URL from Render's PostgreSQL addon
import os  # noqa: E402

_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}
