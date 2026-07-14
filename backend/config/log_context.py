import logging
from contextvars import ContextVar

_request_context = ContextVar('request_log_context', default=None)
request_logger = logging.getLogger('config.request')


def get_request_context():
    return _request_context.get() or {}


def set_request_context(request):
    context = {
        'correlation_id': getattr(request, 'correlation_id', '-'),
        'tenant_id': str(getattr(getattr(request, 'tenant', None), 'id', '-')),
        'user': (
            request.user.email
            if getattr(request, 'user', None) and request.user.is_authenticated
            else 'anonymous'
        ),
    }
    return _request_context.set(context)


def reset_request_context(token):
    _request_context.reset(token)


class RequestContextLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = set_request_context(request)
        try:
            response = self.get_response(request)
            request_logger.info(
                'request_completed method=%s path=%s status=%s',
                request.method,
                request.path,
                response.status_code,
            )
            return response
        finally:
            reset_request_context(token)


class ThreadLocalFilter(logging.Filter):
    def filter(self, record):
        context = get_request_context()
        record.correlation_id = context.get('correlation_id', '-')
        record.tenant_id = context.get('tenant_id', '-')
        record.user = context.get('user', '-')
        return True
