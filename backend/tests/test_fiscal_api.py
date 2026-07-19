import json

import pytest

from tests.test_fiscal_services import _run_in_tenant


@pytest.mark.django_db
def test_fiscal_status_returns_latest_attempt(client, fiscal_sale_context):
    from fiscal.models import FiscalDocument

    ctx = fiscal_sale_context
    client.force_login(ctx['user'])
    session = client.session
    session['mfa_tenant_id'] = str(ctx['tenant'].id)
    session['mfa_method'] = 'totp'
    session.save()

    def _create_docs():
        FiscalDocument.all_objects.create(
            tenant=ctx['tenant'],
            sale=ctx['sale'],
            status='REJECTED',
            attempt_number=1,
            is_active=False,
            error_detail='Erro anterior',
        )
        FiscalDocument.all_objects.create(
            tenant=ctx['tenant'],
            sale=ctx['sale'],
            status='CONCLUDED',
            attempt_number=2,
            protocol='12345',
        )

    _run_in_tenant(ctx['tenant'], _create_docs)

    response = client.get(
        f'/api/v1/sales/{ctx["sale"].id}/fiscal-status/',
        HTTP_X_TENANT_ID=str(ctx['tenant'].id),
    )

    assert response.status_code == 200
    assert response.json()['fiscal_status'] == 'CONCLUDED'
    assert response.json()['attempt'] == 2
    assert response.json()['protocol'] == '12345'


@pytest.mark.django_db
def test_fiscal_status_returns_404_when_document_does_not_exist(client, fiscal_sale_context):
    ctx = fiscal_sale_context
    client.force_login(ctx['user'])
    session = client.session
    session['mfa_tenant_id'] = str(ctx['tenant'].id)
    session['mfa_method'] = 'totp'
    session.save()

    response = client.get(
        f'/api/v1/sales/{ctx["sale"].id}/fiscal-status/',
        HTTP_X_TENANT_ID=str(ctx['tenant'].id),
    )

    assert response.status_code == 404


def test_fiscal_webhook_rejects_invalid_json(client):
    response = client.post(
        '/api/v1/fiscal/webhook/',
        data='{',
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'invalid json'


def test_fiscal_webhook_rejects_missing_provider_id(client):
    response = client.post(
        '/api/v1/fiscal/webhook/',
        data=json.dumps({'status': 'CONCLUIDO'}),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'missing idNota'


@pytest.mark.django_db
def test_fiscal_webhook_ignores_unknown_provider_document(client):
    response = client.post(
        '/api/v1/fiscal/webhook/',
        data=json.dumps({'idNota': 'unknown'}),
        content_type='application/json',
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_fiscal_webhook_queries_provider_instead_of_trusting_body(
    monkeypatch,
    client,
    fiscal_sale_context,
):
    from fiscal.models import FiscalDocument, FiscalEmitter
    from fiscal.ports import QueryResult

    ctx = fiscal_sale_context

    def fake_query(self, tenant, provider_document_id):
        assert provider_document_id == 'nfce-123'
        return QueryResult(
            status='CONCLUIDO',
            protocol='real-protocol',
            xml_url=None,
            pdf_url=None,
            error_reason=None,
        )

    monkeypatch.setattr('fiscal.adapters.plugnotas.PlugNotasAdapter.query', fake_query)

    def _create_doc():
        FiscalEmitter.all_objects.create(
            tenant=ctx['tenant'],
            branch=ctx['branch'],
            provider='plugnotas',
            cpf_cnpj='12345678000199',
            registered_at_provider=True,
        )
        return FiscalDocument.all_objects.create(
            tenant=ctx['tenant'],
            sale=ctx['sale'],
            status='PROCESSING',
            provider_document_id='nfce-123',
        )

    doc = _run_in_tenant(ctx['tenant'], _create_doc)

    response = client.post(
        '/api/v1/fiscal/webhook/',
        data=json.dumps({'idNota': 'nfce-123', 'status': 'REJEITADO'}),
        content_type='application/json',
    )

    assert response.status_code == 200
    doc.refresh_from_db()
    assert doc.status == 'CONCLUDED'
    assert doc.protocol == 'real-protocol'
    assert doc.webhook_received_at is not None
