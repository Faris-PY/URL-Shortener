import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'URL_Shortener.settings')

application = get_wsgi_application()
