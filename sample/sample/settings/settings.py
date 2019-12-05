import os
import importlib
from .site_logger import *
from ._aws import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e0c#s)#c(+-iki+4v7@lhkI93j9g6b=#vjco5*%i1n#$@j8!uj'
SECRET_SALT = 'no!ip-e*idukUnlbr*clMn4jds05ibaPRijuW=7EgiD+u&R'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_ID = 1

# Server settings is in here, just change the boolean values
STAGING = False
PRODUCTION = False

if PRODUCTION:
    MODULE = importlib.import_module('sample.settings.production')
    STAGING = False
    DEBUG = False

if STAGING:
    MODULE = importlib.import_module('sample.settings.staging')
    DEBUG = False

if DEBUG:
    MODULE = importlib.import_module('sample.settings.local')

# LOADING SETTINGS
ALLOWED_HOSTS = MODULE.ALLOWED_HOSTS
SIMPLE_JWT = MODULE.SIMPLE_JWT
SIMPLE_JWT['SIGNING_KEY'] = SECRET_SALT

# EMAIL SETTINGS
EMAIL_BACKEND = MODULE.EMAIL_BACKEND
EMAIL_HOST = MODULE.EMAIL_HOST
EMAIL_PORT = MODULE.EMAIL_PORT
if MODULE.SMTP_ENABLED:
    EMAIL_HOST_USER = MODULE.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = MODULE.EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS = MODULE.EMAIL_USE_TLS
DEFAULT_FROM_EMAIL = MODULE.DEFAULT_FROM_EMAIL
PROTOCOL = MODULE.PROTOCOL

DATABASES = MODULE.DATABASES
 
# AUTH MODEL
AUTH_USER_MODEL = 'authentication.User'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'authentication',
]

# DRF SETTINGS
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'utils.exception_handler.custom_exception_handler',
}

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesModelBackend',
    'django.contrib.auth.backends.ModelBackend'
]

CACHES = {
    # 'default': {
    #     'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    #     'LOCATION': '0.0.0.0:11211',
    # },
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    },
    'axes_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
    # "redis": {
    #     "BACKEND": "django_redis.cache.RedisCache",
    #     "LOCATION": "redis://127.0.0.1:6379/1",
    #     "OPTIONS": {
    #         "CLIENT_CLASS": "django_redis.client.DefaultClient",
    #     }
    # }
}

AXES_CACHE = 'axes_cache'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sample.urls'

TEMPLATE_DIRS = [os.path.join(os.path.abspath('.'), 'authentications/templates'),]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sample.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kuala_Lumpur'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
