from .settings import *

SECRET_KEY = 'integration-tests-only-32-characters-minimum'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
