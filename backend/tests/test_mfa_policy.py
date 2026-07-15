import pytest
from django.core.exceptions import ValidationError

from tenancy.models import Tenant, TenantMFAPolicy


@pytest.mark.django_db
def test_mfa_policy_requires_at_least_one_method():
    tenant = Tenant.objects.create(name='Policy Tenant', slug='policy-tenant')
    policy = TenantMFAPolicy(tenant=tenant, allow_totp=False, allow_email=False)
    with pytest.raises(ValidationError):
        policy.save()
