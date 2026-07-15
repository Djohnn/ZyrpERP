from decouple import config

from .base import *

DEBUG = False

SECRET_KEY = config('SECRET_KEY')
MFA_ENCRYPTION_KEY = config('MFA_ENCRYPTION_KEY')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_APP_USER'),
        'PASSWORD': config('POSTGRES_APP_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT', default='5432'),
        'OPTIONS': {'connect_timeout': 10},
        'CONN_MAX_AGE': 60,
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    },
}

CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

STATIC_ROOT = config('STATIC_ROOT', default='/app/staticfiles')
