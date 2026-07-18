import pytest


@pytest.mark.django_db
def test_sale_confirmed_outbox_handler_dispatches_fiscal_task(monkeypatch):
    from fiscal.tasks import handle_sale_confirmed_outbox
    from outbox.handlers import get_handler
    from outbox.models import OutboxMessage

    dispatched = []

    def fake_delay(sale_id):
        dispatched.append(sale_id)

    monkeypatch.setattr('fiscal.tasks.handle_sale_completed.delay', fake_delay)

    message = OutboxMessage.objects.create(
        event_type='sales.sale.confirmed',
        aggregate_type='Sale',
        aggregate_id='sale-123',
        payload={'sale_id': 'sale-123'},
    )

    assert get_handler('sales.sale.confirmed') is handle_sale_confirmed_outbox
    result = handle_sale_confirmed_outbox(message)

    assert dispatched == ['sale-123']
    assert result == {
        'sale_id': 'sale-123',
        'task': 'fiscal.tasks.handle_sale_completed',
    }


@pytest.mark.django_db
def test_handle_sale_completed_is_idempotent(monkeypatch, fiscal_sale_context):
    from fiscal.models import FiscalDocument
    from fiscal.tasks import handle_sale_completed

    ctx = fiscal_sale_context
    FiscalDocument.all_objects.create(
        tenant=ctx['tenant'],
        sale=ctx['sale'],
        status=FiscalDocument.STATUS_PROCESSING,
        provider_document_id='already-created',
    )

    monkeypatch.setattr(
        'fiscal.tasks.emit_nfce',
        lambda sale, tenant: pytest.fail('emit_nfce must not run on redelivery'),
    )

    assert handle_sale_completed(str(ctx['sale'].id)) is None
