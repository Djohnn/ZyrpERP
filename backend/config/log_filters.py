import logging


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = getattr(record, 'correlation_id', '-')
        record.tenant_id = getattr(record, 'tenant_id', '-')
        record.user = getattr(record, 'user', '-')
        return True
