import pytest


def test_sale_confirmed_outbox_does_not_trigger_automatic_fiscal_emission():
    from outbox.handlers import get_handler

    assert get_handler('sales.sale.confirmed') is None


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
