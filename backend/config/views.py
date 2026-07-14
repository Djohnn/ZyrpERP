from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def _check_redis():
    try:
        cache_settings = settings.CACHES.get('default', {})
        location = cache_settings.get('LOCATION', '')
        if not location or 'LocMem' in cache_settings.get('BACKEND', ''):
            return True
        from urllib.parse import urlparse

        from redis import Redis
        parsed = urlparse(location)
        r = Redis(host=parsed.hostname, port=parsed.port, db=0, socket_connect_timeout=2)
        return r.ping()
    except Exception:
        return False


def health(request):
    db_ok = False
    redis_ok = False

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            db_ok = True
    except Exception:
        db_ok = False

    redis_ok = _check_redis()

    status = 200 if (db_ok and redis_ok) else 503
    return JsonResponse(
        {
            'status': 'healthy' if status == 200 else 'degraded',
            'services': {
                'database': 'ok' if db_ok else 'down',
                'cache': 'ok' if redis_ok else 'down',
            },
        },
        status=status,
    )
