"""
Django settings for freelanceOS.

This file now imports from config.settings (split settings).
Kept for backward compatibility with DJANGO_SETTINGS_MODULE='core.settings'.
"""

# Import everything from the new split-settings module
from config.settings import *  # noqa: F401, F403
