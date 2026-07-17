import logging

import pytest
from django.test import RequestFactory
from django.views import View

from config import views as config_views
from config.log_filters import RequestContextFilter
from config.mixins import TenantRequiredMixin
from config.views import csrf_failure


def test_request_context_filter_adds_default_fields():
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='message',
        args=(),
        exc_info=None,
    )

    assert RequestContextFilter().filter(record) is True
    assert record.correlation_id == '-'
    assert record.tenant_id == '-'
    assert record.user == '-'


def test_request_context_filter_preserves_existing_fields():
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='message',
        args=(),
        exc_info=None,
    )
    record.correlation_id = 'cid'
    record.tenant_id = 'tenant'
    record.user = 'user'

    RequestContextFilter().filter(record)

    assert record.correlation_id == 'cid'
    assert record.tenant_id == 'tenant'
    assert record.user == 'user'


class TenantProtectedView(TenantRequiredMixin, View):
    def get(self, request):
        from django.http import JsonResponse

        return JsonResponse({'detail': 'ok'})


@pytest.mark.django_db
def test_tenant_required_mixin_rejects_missing_tenant():
    request = RequestFactory().get('/protected/')
    request.tenant = None

    response = TenantProtectedView.as_view()(request)

    assert response.status_code == 403


@pytest.mark.django_db
def test_tenant_required_mixin_allows_request_with_tenant(tenant_alpha):
    request = RequestFactory().get('/protected/')
    request.tenant = tenant_alpha

    response = TenantProtectedView.as_view()(request)

    assert response.status_code == 200


def test_csrf_failure_returns_problem_json():
    response = csrf_failure(RequestFactory().post('/unsafe/'), reason='missing')

    assert response.status_code == 403
    assert response['Content-Type'] == 'application/problem+json'


def test_check_redis_returns_true_for_locmem(settings):
    settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

    assert config_views._check_redis() is True


def test_check_redis_pings_configured_redis(settings, monkeypatch):
    class FakeRedis:
        def __init__(self, host, port, db, socket_connect_timeout):
            self.host = host
            self.port = port
            self.db = db
            self.socket_connect_timeout = socket_connect_timeout

        def ping(self):
            return True

    settings.CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://localhost:6380/0',
        },
    }
    monkeypatch.setattr('redis.Redis', FakeRedis)

    assert config_views._check_redis() is True


def test_check_redis_returns_false_on_exception(settings, monkeypatch):
    class BrokenRedis:
        def __init__(self, *args, **kwargs):
            pass

        def ping(self):
            raise ConnectionError('down')

    settings.CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://localhost:6380/0',
        },
    }
    monkeypatch.setattr('redis.Redis', BrokenRedis)

    assert config_views._check_redis() is False
