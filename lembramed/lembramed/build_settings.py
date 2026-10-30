# Used only for collectstatic while building the container, without database credentials.
from .settings import *
SECRET_KEY = 'static-build-only-key-not-used-by-the-running-application'
DEBUG = False
