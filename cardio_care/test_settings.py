# cardio_care/test_settings.py
from .settings import *

# Use a fixed SECRET_KEY for testing
SECRET_KEY = 'django-insecure-test-key-for-testing-only'

# Use an in-memory SQLite database for faster testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'