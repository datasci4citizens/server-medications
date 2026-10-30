import os
from django.core.exceptions import ImproperlyConfigured
from .settings import *

DEBUG = False

def env_list(name):
    return [value.strip().rstrip('/') for value in os.getenv(name, '').split(',') if value.strip()]

if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('Configure DJANGO_SECRET_KEY com pelo menos 50 caracteres.')
if not os.getenv('DATABASE_URL'):
    raise ImproperlyConfigured('Configure DATABASE_URL com a referência do PostgreSQL no Railway.')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS')
if os.getenv('RAILWAY_PUBLIC_DOMAIN'):
    ALLOWED_HOSTS.append(os.environ['RAILWAY_PUBLIC_DOMAIN'])
ALLOWED_HOSTS.append('healthcheck.railway.app')
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
CORS_ALLOW_CREDENTIALS = False
# Railway terminates TLS and forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r'^health/$']
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SIMPLE_JWT = {**SIMPLE_JWT, 'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30)}
