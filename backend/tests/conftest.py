import pytest
from django.contrib.auth import get_user_model
from django.db import connection

from tenancy.context import reset_current_tenant_id, set_current_tenant_id
from tenancy.models import Branch, Company, Tenant, TenantMembership

User = get_user_model()


def _run_in_tenant(tenant, callback):
    token = set_current_tenant_id(tenant.id)
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET app.current_tenant_id = %s', [str(tenant.id)])
        return callback()
    finally:
        reset_current_tenant_id(token)


@pytest.fixture
def tenant_alpha():
    t, _ = Tenant.objects.get_or_create(
        slug='test-alpha', defaults={'name': 'Test Alpha'},
    )
    return t


@pytest.fixture
def tenant_beta():
    t, _ = Tenant.objects.get_or_create(
        slug='test-beta', defaults={'name': 'Test Beta'},
    )
    return t


@pytest.fixture
def user_alpha(tenant_alpha):
    u, _ = User.objects.get_or_create(email='user-alpha@test.local')
    u.set_password('pass123')
    u.save()
    TenantMembership.objects.get_or_create(
        user=u, tenant=tenant_alpha, defaults={'role': 'admin'},
    )
    return u


@pytest.fixture
def user_beta(tenant_beta):
    u, _ = User.objects.get_or_create(email='user-beta@test.local')
    u.set_password('pass123')
    u.save()
    TenantMembership.objects.get_or_create(
        user=u, tenant=tenant_beta, defaults={'role': 'admin'},
    )
    return u


@pytest.fixture
def company_alpha(tenant_alpha):
    return _run_in_tenant(
        tenant_alpha,
        lambda: Company.objects.get_or_create(
            tenant=tenant_alpha, name='Alpha Company',
        )[0],
    )


@pytest.fixture
def company_beta(tenant_beta):
    return _run_in_tenant(
        tenant_beta,
        lambda: Company.objects.get_or_create(
            tenant=tenant_beta, name='Beta Company',
        )[0],
    )


@pytest.fixture
def branch_alpha(company_alpha, tenant_alpha):
    return _run_in_tenant(
        tenant_alpha,
        lambda: Branch.objects.get_or_create(
            company=company_alpha, tenant=tenant_alpha, name='Alpha Branch',
        )[0],
    )


@pytest.fixture
def branch_beta(company_beta, tenant_beta):
    return _run_in_tenant(
        tenant_beta,
        lambda: Branch.objects.get_or_create(
            company=company_beta, tenant=tenant_beta, name='Beta Branch',
        )[0],
    )
