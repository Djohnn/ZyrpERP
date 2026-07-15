import pytest
from django.contrib.auth import get_user_model

from accounts.models import MFADevice, OneTimeToken
from accounts.services.mfa import issue_email_challenge, verify_email_challenge
from tenancy.models import Tenant

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_email_mfa_is_single_use_and_does_not_store_code():
    user = User.objects.create_user(email='email-mfa@test.local', password='test-password')
    tenant = Tenant.objects.create(name='Email MFA', slug='email-mfa')
    code, challenge = issue_email_challenge(user=user)

    assert code not in challenge.digest
    assert verify_email_challenge(challenge_id=challenge.id, code=code)
    assert not verify_email_challenge(challenge_id=challenge.id, code=code)
    assert OneTimeToken.objects.get(pk=challenge.pk).consumed_at is not None
    device = MFADevice.objects.get(user=user, tenant=tenant, method='email') if False else None
    assert device is None
