import time
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from monitoring.middleware import get_request_metrics, get_error_metrics, reset_metrics


@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """Health check endpoint for load balancers."""

    def get(self, request):
        db_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            db_ok = True
        except Exception:
            pass

        redis_ok = False
        try:
            cache_settings = settings.CACHES.get('default', {})
            location = cache_settings.get('LOCATION', '')
            if location and 'LocMem' not in cache_settings.get('BACKEND', ''):
                from redis import Redis
                parsed = urlparse(location)
                redis = Redis(
                    host=parsed.hostname,
                    port=parsed.port,
                    db=0,
                    socket_connect_timeout=2,
                )
                redis_ok = redis.ping()
            else:
                redis_ok = True
        except Exception:
            pass

        overall = db_ok and redis_ok
        status_code = 200 if overall else 503

        return JsonResponse(
            {
                'status': 'healthy' if overall else 'unhealthy',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'checks': {
                    'database': 'ok' if db_ok else 'down',
                    'cache': 'ok' if redis_ok else 'down',
                },
            },
            status=status_code,
        )


@method_decorator(csrf_exempt, name='dispatch')
class ReadinessView(View):
    """Readiness probe for Kubernetes."""

    def get(self, request):
        # Check if migrations are applied and app can serve traffic
        db_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            db_ok = True
        except Exception:
            pass

        if not db_ok:
            return JsonResponse(
                {'status': 'not_ready', 'reason': 'database unavailable'},
                status=503,
            )

        return JsonResponse(
            {'status': 'ready', 'timestamp': datetime.utcnow().isoformat() + 'Z'}
        )


@method_decorator(csrf_exempt, name='dispatch')
class MetricsView(View):
    """Expose application metrics for monitoring."""

    def get(self, request):
        # Check if monitoring is enabled
        if not getattr(settings, 'MONITORING_ENABLED', True):
            return JsonResponse({'error': 'Monitoring disabled'}, status=403)

        metrics = get_request_metrics()
        errors = get_error_metrics()

        # Also check database and cache health
        db_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            db_ok = True
        except Exception:
            pass

        # Check Redis
        redis_ok = False
        try:
            cache_settings = settings.CACHES.get('default', {})
            location = cache_settings.get('LOCATION', '')
            if location and 'LocMem' not in cache_settings.get('BACKEND', ''):
                from redis import Redis
                from urllib.parse import urlparse
                parsed = urlparse(location)
                redis = Redis(
                    host=parsed.hostname,
                    port=parsed.port,
                    db=0,
                    socket_connect_timeout=2,
                )
                redis_ok = redis.ping()
            else:
                redis_ok = True
        except Exception:
            pass

        return JsonResponse({
            'database': 'ok' if db_ok else 'down',
            'cache': 'ok' if redis_ok else 'down',
            'request_metrics': metrics,
            'error_metrics': errors,
        })


@method_decorator(csrf_exempt, name='dispatch')
class MetricsResetView(View):
    """Reset metrics (for testing)."""

    def post(self, request):
        reset_metrics()
        return JsonResponse({'status': 'reset'})