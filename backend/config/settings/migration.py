from decouple import config

from .local import *

DATABASES['default']['USER'] = config('POSTGRES_USER', default='zyrp')
DATABASES['default']['PASSWORD'] = config('POSTGRES_PASSWORD', default='zyrp')
