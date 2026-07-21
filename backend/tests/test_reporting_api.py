from decimal import Decimal

import pytest

from financial.models import Payable
from tenancy.models import Tenant


def _authenticate(client, ctx):
    client.force_login(ctx['user'])
    session = client.session
    session['mfa_tenant_id'] = str(ctx['tenant'].id)
    session['mfa_method'] = 'totp'
    session.save()
    return client


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'expected_key'),
    [
        ('/api/v1/reports/sales/', 'net_total'),
        ('/api/v1/reports/cash-closing/', 'sessions'),
        ('/api/v1/reports/inventory/', 'items'),
        ('/api/v1/reports/financial/', 'payables'),
        ('/api/v1/reports/cashflow/', 'realized_balance'),
        ('/api/v1/reports/pending-operations/', 'fiscal'),
    ],
)
def test_operational_reports_are_available(path, expected_key, client, sale_context):
    """When a manager requests an operational report, a tenant-scoped read model is returned."""
    ctx = sale_context
    client = _authenticate(client, ctx)

    response = client.get(
        path,
        {'date_from': '2026-07-01', 'date_to': '2026-07-31'},
        HTTP_X_TENANT_ID=str(ctx['tenant'].id),
    )

    assert response.status_code == 200
    assert expected_key in response.json()


@pytest.mark.django_db
def test_financial_report_does_not_expose_another_tenant(client, sale_context):
    """Given another tenant's payable, the active tenant report shall not expose it."""
    ctx = sale_context
    client = _authenticate(client, ctx)
    other_tenant = Tenant.objects.create(name='Other Financial', slug='other-financial')
    foreign = Payable.all_objects.create(
        tenant=other_tenant,
        supplier_name='Segredo Cross Tenant',
        amount=Decimal('999.00'),
    )

    response = client.get(
        '/api/v1/reports/financial/',
        HTTP_X_TENANT_ID=str(ctx['tenant'].id),
    )

    assert response.status_code == 200
    ids = {item['id'] for item in response.json()['payables']}
    assert str(foreign.id) not in ids


@pytest.mark.django_db
def test_report_export_rejects_rows_above_limit(client, sale_context):
    """When an export exceeds 1000 rows, the API shall reject it before querying data."""
    ctx = sale_context
    client = _authenticate(client, ctx)

    response = client.get(
        '/api/v1/reports/financial/',
        {'export': 'csv', 'limit': '1001'},
        HTTP_X_TENANT_ID=str(ctx['tenant'].id),
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'export_limit_exceeded'
