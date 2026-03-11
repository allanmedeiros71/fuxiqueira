"""
ASGI config for bioimpedancia project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bioimpedancia.settings')

application = get_asgi_application()
