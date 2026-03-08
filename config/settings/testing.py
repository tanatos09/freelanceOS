"""
Testing settings for freelanceOS.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable throttling in tests
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = ()  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405

# Disable pagination in tests (backward compat)
REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = None  # noqa: F405
