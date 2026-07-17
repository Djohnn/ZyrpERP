import pytest
from django.db import connection

from inventory.models import StockLocation
from tenancy.context import reset_current_tenant_id, set_current_tenant_id
from tenancy.models import Branch, Company, Tenant


def _set_pg_tenant(tenant_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('app.current_tenant_id', %s, false)",
            [str(tenant_id) if tenant_id else ''],
        )


def _run_in_tenant(tenant, callback):
    token = set_current_tenant_id(tenant.id)
    try:
        _set_pg_tenant(tenant.id)
        return callback()
    finally:
        reset_current_tenant_id(token)


def _create_location(tenant, code):
    def _create():
        company = Company.all_objects.create(tenant=tenant, name=f'Company {code}')
        branch = Branch.all_objects.create(
            tenant=tenant,
            company=company,
            name=f'Branch {code}',
        )
        return StockLocation.all_objects.create(
            tenant=tenant,
            branch=branch,
            code=code,
            name=f'Location {code}',
        )

    return _run_in_tenant(tenant, _create)


@pytest.mark.django_db
def test_inventory_rls_blocks_cross_tenant_rows():
    tenant_a = Tenant.objects.create(name='Inventory RLS A', slug='inventory-rls-a')
    tenant_b = Tenant.objects.create(name='Inventory RLS B', slug='inventory-rls-b')
    location_a = _create_location(tenant_a, 'A')
    location_b = _create_location(tenant_b, 'B')

    _set_pg_tenant(tenant_a.id)
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) FROM inventory_stocklocation WHERE id = %s',
            [str(location_a.id)],
        )
        assert cursor.fetchone()[0] == 1
        cursor.execute(
            'SELECT COUNT(*) FROM inventory_stocklocation WHERE id = %s',
            [str(location_b.id)],
        )
        assert cursor.fetchone()[0] == 0


@pytest.mark.django_db
def test_inventory_rls_denies_rows_without_tenant_context():
    tenant = Tenant.objects.create(name='Inventory RLS None', slug='inventory-rls-none')
    location = _create_location(tenant, 'NONE')

    _set_pg_tenant(None)
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) FROM inventory_stocklocation WHERE id = %s',
            [str(location.id)],
        )
        assert cursor.fetchone()[0] == 0
