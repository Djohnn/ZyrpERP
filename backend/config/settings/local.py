from decouple import config

from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='zyrp'),
        'USER': config('POSTGRES_APP_USER', default='zyrp_app'),
        'PASSWORD': config('POSTGRES_APP_PASSWORD', default='zyrp_app_dev'),
        'HOST': config('POSTGRES_HOST', default='127.0.0.1'),
        'PORT': config('POSTGRES_PORT', default='5433'),
        'OPTIONS': {'connect_timeout': 5},
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6380/0'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    },
}

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6380/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6380/2')
