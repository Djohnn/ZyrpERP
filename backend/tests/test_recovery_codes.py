import pytest
from django.contrib.auth import get_user_model

from accounts.models import MFADevice, RecoveryCode
from accounts.services.mfa import consume_recovery_code, regenerate_recovery_codes
from tenancy.models import Tenant

User = get_user_model()


@pytest.mark.django_db
def test_recovery_codes_are_hashed_and_single_use():
    user = User.objects.create_user(email='recovery@test.local', password='test-password')
    tenant = Tenant.objects.create(name='Recovery', slug='recovery')
    device = MFADevice.objects.create(user=user, tenant=tenant, method='email')

    codes = regenerate_recovery_codes(device=device, count=3)

    assert len(codes) == 3
    assert not RecoveryCode.objects.filter(digest__in=codes).exists()
    assert consume_recovery_code(device=device, code=codes[0])
    assert not consume_recovery_code(device=device, code=codes[0])
