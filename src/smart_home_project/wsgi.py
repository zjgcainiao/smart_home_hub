"""
WSGI config for smart_home_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# to read .env variables
from dotenv import load_dotenv
# load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_home_project.settings')

application = get_wsgi_application()
