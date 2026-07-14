import uuid


class CorrelationIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        supplied = request.headers.get('X-Correlation-ID', '')
        try:
            parsed = uuid.UUID(supplied)
            correlation_id = str(parsed) if str(parsed) == supplied.lower() else str(uuid.uuid4())
        except (ValueError, TypeError, AttributeError):
            correlation_id = str(uuid.uuid4())
        request.correlation_id = correlation_id
        response = self.get_response(request)
        response.headers['X-Correlation-ID'] = correlation_id
        return response
