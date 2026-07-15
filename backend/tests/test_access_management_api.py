import pytest
from django.contrib.auth import get_user_model

from tenancy.models import Tenant, TenantMembership

User = get_user_model()


@pytest.mark.django_db
def test_admin_updates_membership_and_policy(client):
    admin = User.objects.create_user(email='access-admin@test.local', password='test-password')
    member = User.objects.create_user(email='access-member@test.local', password='test-password')
    tenant = Tenant.objects.create(name='Access Tenant', slug='access-tenant')
    TenantMembership.objects.create(user=admin, tenant=tenant, role='admin')
    membership = TenantMembership.objects.create(user=member, tenant=tenant, role='operator')
    client.force_login(admin)

    changed = client.patch(
        f'/api/v1/memberships/{membership.id}/', {'role': 'manager'},
        content_type='application/json', HTTP_X_TENANT_ID=str(tenant.id),
    )
    policy = client.patch(
        '/api/v1/security/mfa-policy/', {'allow_totp': True, 'allow_email': False},
        content_type='application/json', HTTP_X_TENANT_ID=str(tenant.id),
    )

    assert changed.status_code == 200
    assert changed.json()['role'] == 'manager'
    assert policy.status_code == 200
    assert policy.json() == {'allow_totp': True, 'allow_email': False}


@pytest.mark.django_db
def test_other_tenant_membership_returns_404(client):
    admin = User.objects.create_user(email='idor-admin@test.local', password='test-password')
    other = User.objects.create_user(email='idor-other@test.local', password='test-password')
    tenant_a = Tenant.objects.create(name='Tenant A access', slug='tenant-a-access')
    tenant_b = Tenant.objects.create(name='Tenant B access', slug='tenant-b-access')
    TenantMembership.objects.create(user=admin, tenant=tenant_a, role='admin')
    target = TenantMembership.objects.create(user=other, tenant=tenant_b, role='operator')
    client.force_login(admin)
    response = client.patch(
        f'/api/v1/memberships/{target.id}/', {'role': 'manager'},
        content_type='application/json', HTTP_X_TENANT_ID=str(tenant_a.id),
    )
    assert response.status_code == 404
