import os
from dotenv import load_dotenv
# JWT SETTINGS IS IMPORTED HERE FOR CUSTOMIZATION OF LOCAL/STAGING/PROD
from .jwt_settings import SIMPLE_JWT

load_dotenv(override=True)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sample_db',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'USER': 'test_user',
        'PASSWORD': 'somepass',
        'HOST': '10.0.75.1',
        'PORT': '3306',
    }
}

SMTP_ENABLED = False

# PRINT EMAIL IN CONSOLE - TESTING PURPOSES
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# AWS EMAIL SETTINGS
# EMAIL_BACKEND = 'django_amazon_ses.EmailBackend'
# SES_ID = None
# SES_KEY = None

# SMTP SETTINGS
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = None # Email
# EMAIL_HOST_PASSWORD = None # Password
# EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'Sample <sample@gmail.com>'
PROTOCOL = 'http'

# AXES CONFIG
AXES_COOLDOWN = 60
AXES_LIMIT = 5
