import pyotp
import pytest
from django.contrib.auth import get_user_model

from accounts.models import MFADevice
from accounts.security import decrypt_secret
from accounts.services.mfa import begin_totp_enrollment, confirm_totp
from tenancy.models import Tenant, TenantMembership

User = get_user_model()


@pytest.mark.django_db
def test_totp_enrollment_encrypts_secret_and_blocks_replay():
    user = User.objects.create_user(email='totp@test.local', password='test-password')
    tenant = Tenant.objects.create(name='TOTP Tenant', slug='totp-tenant')
    TenantMembership.objects.create(user=user, tenant=tenant, role='admin')

    uri, device = begin_totp_enrollment(user=user, tenant=tenant)
    secret = decrypt_secret(device.encrypted_secret)
    code = pyotp.TOTP(secret).now()

    assert uri.startswith('otpauth://totp/')
    assert secret not in device.encrypted_secret
    assert confirm_totp(device=device, code=code)
    assert not confirm_totp(device=device, code=code)
    device.refresh_from_db()
    assert device.verified_at is not None
    assert MFADevice.objects.filter(user=user, tenant=tenant, method='totp').count() == 1
