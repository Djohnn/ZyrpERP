"""Sprint 13 provider contract scenarios (Given/When/Then)."""

from decimal import Decimal


def test_fake_provider_supports_full_payment_lifecycle():
    """Given a fake provider, when lifecycle methods run, then states are deterministic."""
    from payments.providers.fake import FakePaymentProvider

    provider = FakePaymentProvider(secret='top-secret')
    intent = provider.create_intent(amount=Decimal('42.00'), idempotency_key='order-42')
    capture = provider.capture(intent.reference, Decimal('42.00'))
    cancel = provider.cancel(intent.reference)
    refund = provider.refund(capture.reference, Decimal('10.00'))

    assert intent.status == 'authorized'
    assert intent.reference == 'fake-intent-order-42'
    assert capture.status == 'succeeded'
    assert cancel.status == 'succeeded'
    assert refund.status == 'succeeded'
    assert refund.amount == Decimal('10.00')


def test_fake_provider_failure_and_signature_are_deterministic():
    """Given deterministic inputs, when failure/signature run, then results are reproducible."""
    from payments.providers.fake import FakePaymentProvider

    provider = FakePaymentProvider(secret='top-secret')
    failed = provider.create_intent(amount=Decimal('1.00'), idempotency_key='fail-case')
    signature = provider.sign(b'{"id":"evt-1"}')

    assert failed.status == 'failed'
    assert provider.verify_signature(b'{"id":"evt-1"}', signature)
    assert not provider.verify_signature(b'changed', signature)
    assert 'top-secret' not in str(provider)
    assert 'top-secret' not in repr(provider)
