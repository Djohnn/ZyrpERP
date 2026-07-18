from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from fiscal.adapters.plugnotas import PlugNotasAdapter
from fiscal.models import FiscalDocument, FiscalEmitter, FiscalProductConfig

MAX_AUTO_REATTEMPTS = 2
POLLING_INTERVAL = timedelta(seconds=15)
POLLING_TIMEOUT = timedelta(minutes=30)


def _import_string(path):
    module_path, class_name = path.rsplit('.', 1)
    return getattr(import_module(module_path), class_name)


def _resolve_provider(provider_name: str):
    providers = getattr(settings, 'FISCAL_PROVIDERS', {})
    config = providers.get(provider_name, {})
    klass = config.get('class', PlugNotasAdapter)
    if isinstance(klass, str):
        klass = _import_string(klass)
    return klass(api_key=config.get('api_key', ''))


def resolve_emitter(branch):
    return FiscalEmitter.all_objects.filter(
        branch=branch,
        registered_at_provider=True,
        is_active=True,
    ).first()


def resolve_product_config(product):
    return FiscalProductConfig.all_objects.filter(product=product, is_active=True).first()


def build_item_dict(item):
    product = item.product
    config = resolve_product_config(product)
    return {
        'product': product,
        'quantity': item.quantity,
        'unit_price': item.unit_price,
        'line_total': item.line_total,
        'ncm': product.ncm,
        'unidade': item.unit.symbol if item.unit_id else 'UN',
        'origem': config.origem if config else '0',
        'cst_icms': config.cst_icms if config and config.cst_icms else '00',
        'cst_pis': config.cst_pis if config and config.cst_pis else '99',
        'cst_cofins': config.cst_cofins if config and config.cst_cofins else '07',
        'aliquota_icms': config.aliquota_icms if config and config.aliquota_icms else 0,
    }


def build_payment_dict(payment):
    return {
        'method': payment.method,
        'amount': payment.amount,
    }


@transaction.atomic
def emit_nfce(sale, tenant):
    existing = FiscalDocument.all_objects.filter(sale=sale, is_active=True).first()
    if existing:
        return existing

    doc = FiscalDocument.all_objects.create(
        tenant=tenant,
        sale=sale,
        status=FiscalDocument.STATUS_PENDING,
    )
    return emit_document(doc)


@transaction.atomic
def emit_document(doc):
    emitter = resolve_emitter(doc.sale.branch)
    if emitter is None:
        doc.status = FiscalDocument.STATUS_FAILED
        doc.error_detail = 'Emitente fiscal não configurado para esta filial'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    items = [build_item_dict(item) for item in doc.sale.items.select_related('product', 'unit')]
    missing_ncm = [item['product'].sku for item in items if not item['ncm']]
    if missing_ncm:
        doc.status = FiscalDocument.STATUS_FAILED
        doc.error_detail = f'Produtos sem NCM: {", ".join(missing_ncm)}'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    payments = [build_payment_dict(payment) for payment in doc.sale.payments.all()]
    provider = _resolve_provider(emitter.provider)

    try:
        result = provider.emit(doc.tenant, emitter, doc, items, payments)
    except Exception as exc:
        doc.status = FiscalDocument.STATUS_FAILED
        doc.error_detail = str(exc)[:2000]
        doc.retry_count += 1
        doc.save(update_fields=['status', 'error_detail', 'retry_count', 'updated_at'])
        return doc

    doc.status = FiscalDocument.STATUS_PROCESSING
    doc.provider_document_id = result.provider_document_id
    doc.save(update_fields=['status', 'provider_document_id', 'updated_at'])
    return doc


@transaction.atomic
def poll_fiscal_document(doc):
    doc = FiscalDocument.all_objects.select_for_update().select_related(
        'sale__branch',
        'tenant',
    ).get(pk=doc.pk)
    now = timezone.now()
    if doc.created_at and now - doc.created_at > POLLING_TIMEOUT:
        doc.status = FiscalDocument.STATUS_FAILED
        doc.error_detail = 'Timeout aguardando confirmação do provedor'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    if not doc.provider_document_id:
        doc.status = FiscalDocument.STATUS_FAILED
        doc.error_detail = 'Documento fiscal sem ID do provedor'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    emitter = resolve_emitter(doc.sale.branch)
    if emitter is None:
        doc.status = FiscalDocument.STATUS_FAILED
        doc.error_detail = 'Emitente fiscal não configurado para consulta'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    try:
        result = _resolve_provider(emitter.provider).query(doc.tenant, doc.provider_document_id)
    except Exception as exc:
        doc.retry_count += 1
        doc.error_detail = str(exc)[:2000]
        doc.save(update_fields=['retry_count', 'error_detail', 'updated_at'])
        return doc

    return apply_provider_query_result(doc, result)


def apply_provider_query_result(doc, result):
    if result.status == 'CONCLUIDO':
        doc.status = FiscalDocument.STATUS_CONCLUDED
        doc.protocol = result.protocol or ''
        doc.xml_key = result.xml_url or ''
        doc.pdf_key = result.pdf_url or ''
        doc.last_polled_at = timezone.now()
        doc.save(update_fields=[
            'status', 'protocol', 'xml_key', 'pdf_key', 'last_polled_at', 'updated_at',
        ])
        return doc

    if result.status == 'REJEITADO':
        doc.status = FiscalDocument.STATUS_REJECTED
        doc.is_active = False
        doc.error_detail = result.error_reason or ''
        doc.last_polled_at = timezone.now()
        doc.save(update_fields=[
            'status', 'is_active', 'error_detail', 'last_polled_at', 'updated_at',
        ])
        if doc.attempt_number < MAX_AUTO_REATTEMPTS:
            FiscalDocument.all_objects.create(
                tenant=doc.tenant,
                sale=doc.sale,
                status=FiscalDocument.STATUS_PENDING,
                attempt_number=doc.attempt_number + 1,
            )
        return doc

    if result.status == 'CANCELADO':
        doc.status = FiscalDocument.STATUS_CANCELLED
        doc.is_active = False
        doc.error_detail = result.error_reason or ''
        doc.last_polled_at = timezone.now()
        doc.save(update_fields=[
            'status', 'is_active', 'error_detail', 'last_polled_at', 'updated_at',
        ])
        return doc

    doc.last_polled_at = timezone.now()
    doc.save(update_fields=['last_polled_at', 'updated_at'])
    return doc
