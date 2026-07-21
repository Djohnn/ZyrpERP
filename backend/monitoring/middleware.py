import time

from django.utils.deprecation import MiddlewareMixin

# Simple in-memory metrics storage (for production, use Redis/Prometheus)
_request_counts = {}
_request_latencies = {}
_error_counts = {}


class MetricsMiddleware(MiddlewareMixin):
    """Middleware to collect request metrics."""

    def process_request(self, request):
        request._start_time = time.perf_counter()
        return

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            latency_ms = round((time.perf_counter() - request._start_time) * 1000, 2)
            path = request.path
            method = request.method
            status = response.status_code

            key = f'{method} {path}'
            _request_counts[key] = _request_counts.get(key, 0) + 1

            if key not in _request_latencies:
                _request_latencies[key] = []
            _request_latencies[key].append(latency_ms)
            # Keep only last 100 latencies per endpoint
            if len(_request_latencies[key]) > 100:
                _request_latencies[key] = _request_latencies[key][-100:]

            if status >= 400:
                error_key = f'{method} {path} {status}'
                _error_counts[error_key] = _error_counts.get(error_key, 0) + 1

        return response


def get_request_metrics():
    """Return collected metrics."""
    metrics = {}
    for key, count in _request_counts.items():
        latencies = _request_latencies.get(key, [])
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        metrics[key] = {
            'count': count,
            'avg_latency_ms': round(avg_latency, 2),
            'min_latency_ms': round(min(latencies), 2) if latencies else 0,
            'max_latency_ms': round(max(latencies), 2) if latencies else 0,
        }
    return metrics


def get_error_metrics():
    """Return error metrics."""
    return dict(_error_counts)


def reset_metrics():
    """Reset all metrics (useful for testing)."""
    _request_counts.clear()
    _request_latencies.clear()
    _error_counts.clear()