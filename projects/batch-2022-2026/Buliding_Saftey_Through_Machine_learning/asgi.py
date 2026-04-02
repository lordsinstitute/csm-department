"""
ASGI config for Buliding_Saftey_Through_Machine_learning project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Buliding_Saftey_Through_Machine_learning.settings')

application = get_asgi_application()
