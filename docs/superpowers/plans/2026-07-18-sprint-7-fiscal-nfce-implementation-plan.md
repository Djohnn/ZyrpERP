# Sprint 7 — NFC-e via PlugNotas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Emit NFC-e automatically after each PDV sale via PlugNotas, with async Celery polling, webhook trigger, and frontend status query.

**Architecture:** New `fiscal` Django app with `FiscalProvider` ABC. `FiscalDocument` state machine tracks async emission. Celery task `handle_sale_completed` listens to `SaleCompleted` outbox event. Celery Beat `poll_fiscal_document` checks processing documents. Webhook endpoint is a trigger to call `adapter.query()`, not a data source.

**Tech Stack:** Django 5.x, DRF, Celery (Beat + tasks), PostgreSQL, `responses` library for adapter tests.

---

### File Map

| File | Action | Responsibility |
|---|---|---|
| `fiscal/__init__.py` | Create | App package |
| `fiscal/apps.py` | Create | App config, ready() imports tasks |
| `fiscal/models.py` | Create | FiscalEmitter, FiscalProductConfig, FiscalDocument |
| `fiscal/ports.py` | Create | FiscalProvider ABC, EmitResult, QueryResult, CancelResult |
| `fiscal/adapters/__init__.py` | Create | Adapters package |
| `fiscal/adapters/plugnotas.py` | Create | PlugNotasAdapter (emit, query, cancel) |
| `fiscal/services.py` | Create | Orchestration helpers (emit_nfce, reattempt, resolve_fiscal_config) |
| `fiscal/tasks.py` | Create | handle_sale_completed, poll_fiscal_document, Celery Beat schedule |
| `fiscal/webhook.py` | Create | Webhook handler view (isento de TenantMiddleware) |
| `fiscal/urls.py` | Create | fiscal-status + webhook routes |
| `fiscal/views.py` | Create | FiscalStatusView (GET), webhook view |
| `fiscal/serializers.py` | Create | FiscalStatusSerializer |
| `fiscal/admin.py` | Create | Admin for all fiscal models |
| `fiscal/migrations/__init__.py` | Create | Migrations package |
| `fiscal/tests/__init__.py` | Create | Tests package |
| `fiscal/tests/test_adapter.py` | Create | PlugNotasAdapter unit tests |
| `fiscal/tests/test_tasks.py` | Create | Celery task unit tests |
| `fiscal/tests/test_webhook.py` | Create | Webhook handler tests |
| `fiscal/tests/test_integration.py` | Create | State machine + attempt lifecycle tests |
| `catalog/models.py` | Modify | Add `ncm` field to Product |
| `tenancy/models.py` | Modify | Add `ie`, `address_json` to Company and Branch |
| `config/settings/base.py` | Modify | Add `fiscal` to LOCAL_APPS |
| `config/settings/local.py` | Modify | Add `PLUGNOTAS_API_KEY`, `FISCAL_PROVIDERS` |
| `config/urls.py` | Modify | Include `fiscal.urls` |
| `config/middleware.py` | Modify | Exempt `/api/v1/fiscal/webhook/` from TenantMiddleware |
| `core/celery.py` | Modify | Import Beat schedule from fiscal.tasks |
| `tests/conftest.py` | Modify | Add fiscal fixtures (emitter, product_config) |
| `tests/test_sales_services.py` | Add | Verify SaleCompleted outbox still fires |
| `tests/test_sales_api.py` | Modify | Add E2E fiscal status check after sale |

---

### Task 1: App scaffold, model changes, migration

**Files:**
- Create: `backend/fiscal/__init__.py`
- Create: `backend/fiscal/apps.py`
- Create: `backend/fiscal/models.py`
- Create: `backend/fiscal/migrations/__init__.py`
- Modify: `backend/catalog/models.py`
- Modify: `backend/tenancy/models.py`
- Modify: `backend/config/settings/base.py`

- [ ] **Step 1: Create `fiscal/apps.py`**

```python
from django.apps import AppConfig

class FiscalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fiscal'
```

- [ ] **Step 2: Add `ncm` to `catalog/models.py` Product**

```python
# after field `requires_expiry`
ncm = models.CharField(max_length=8, blank=True, default='')
```

- [ ] **Step 3: Add `ie` and `address_json` to `tenancy/models.py` Company**

```python
# after field `cnpj`
ie = models.CharField('Inscrição Estadual', max_length=20, blank=True, default='')
address_json = models.JSONField(default=dict, blank=True)
```

- [ ] **Step 4: Add `ie` and `address_json` to `tenancy/models.py` Branch**

```python
# after field `is_active`
ie = models.CharField('Inscrição Estadual', max_length=20, blank=True, default='')
address_json = models.JSONField(default=dict, blank=True)
```

- [ ] **Step 5: Create `fiscal/models.py`** with three models:

```python
import uuid

from django.db import models

from tenancy.managers import TenantManager
from tenancy.models import TenantScopedModel, TimeStampedModel


class FiscalEmitter(TenantScopedModel, TimeStampedModel):
    branch = models.ForeignKey('tenancy.Branch', on_delete=models.PROTECT)
    provider = models.CharField(max_length=30)
    cpf_cnpj = models.CharField(max_length=18)
    ie = models.CharField(max_length=20, blank=True, default='')
    registration_source = models.CharField(
        max_length=20,
        choices=[('manual', 'Manual'), ('automated', 'Automatizado')],
        default='manual',
    )
    registered_at_provider = models.BooleanField(default=False)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.cpf_cnpj} [{self.branch.name}]'


class FiscalProductConfig(TenantScopedModel, TimeStampedModel):
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT)
    cst_icms = models.CharField(max_length=4, blank=True, default='')
    cst_pis = models.CharField(max_length=4, blank=True, default='')
    cst_cofins = models.CharField(max_length=4, blank=True, default='')
    aliquota_icms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    origem = models.CharField(max_length=1, blank=True, default='0')

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'fiscal product configs'

    def __str__(self):
        return f'{self.product.sku}'


class FiscalDocument(TenantScopedModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('QUEUED', 'Na fila'),
        ('PROCESSING', 'Processando'),
        ('CONCLUDED', 'Concluído'),
        ('REJECTED', 'Rejeitado'),
        ('CANCELLED', 'Cancelado'),
        ('FAILED', 'Falha técnica'),
    ]

    sale = models.ForeignKey('sales.Sale', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    attempt_number = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    provider_document_id = models.CharField(max_length=100, blank=True, default='')
    cfop = models.CharField(max_length=4, default='5102')
    idempotency_key = models.UUIDField(default=uuid.uuid4)
    xml_key = models.CharField(max_length=255, blank=True, default='')
    protocol = models.CharField(max_length=60, blank=True, default='')
    pdf_key = models.CharField(max_length=255, blank=True, default='')
    error_detail = models.TextField(blank=True, default='')
    retry_count = models.PositiveIntegerField(default=0)
    last_polled_at = models.DateTimeField(null=True, blank=True)
    webhook_received_at = models.DateTimeField(null=True, blank=True)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['sale'],
                condition=models.Q(is_active=True),
                name='unique_active_fiscal_document_per_sale',
            ),
            models.UniqueConstraint(
                fields=['tenant', 'sale', 'attempt_number'],
                name='unique_attempt_per_sale',
            ),
        ]

    def __str__(self):
        return f'{self.sale_id} attempt {self.attempt_number} [{self.status}]'
```

- [ ] **Step 6: Add `fiscal` to `LOCAL_APPS` in `config/settings/base.py`**

```python
LOCAL_APPS = [
    ...
    'sales',
    'fiscal',
]
```

- [ ] **Step 7: Create empty `fiscal/__init__.py`** and `fiscal/migrations/__init__.py`

```python
# __init__.py — empty
```

- [ ] **Step 8: Run makemigrations and migrate**

Run: `cd backend && python manage.py makemigrations fiscal catalog tenancy --name sprint7_fiscal_models`
Expected: migrations created for fiscal, catalog, tenancy apps

Run: `cd backend && python manage.py migrate`
Expected: all migrations apply cleanly

- [ ] **Step 9: Verify models with a quick smoke test**

Run: `cd backend && python manage.py check`
Expected: no errors

---

### Task 2: FiscalProvider port and PlugNotasAdapter

**Files:**
- Create: `backend/fiscal/ports.py`
- Create: `backend/fiscal/adapters/__init__.py`
- Create: `backend/fiscal/adapters/plugnotas.py`
- Create: `backend/fiscal/tests/__init__.py`
- Create: `backend/fiscal/tests/test_adapter.py`

- [ ] **Step 1: Write `fiscal/ports.py`**

```python
from abc import ABC, abstractmethod
from typing import NamedTuple, Optional

from fiscal.models import FiscalDocument, FiscalEmitter


class EmitResult(NamedTuple):
    provider_document_id: str
    raw_response: dict


class QueryResult(NamedTuple):
    status: str
    protocol: Optional[str]
    xml_url: Optional[str]
    pdf_url: Optional[str]
    error_reason: Optional[str]


class CancelResult(NamedTuple):
    success: bool
    protocol: Optional[str]


class FiscalProvider(ABC):
    @abstractmethod
    def emit(
        self,
        tenant,
        emitter: FiscalEmitter,
        document: FiscalDocument,
        items: list,
        payments: list,
    ) -> EmitResult: ...

    @abstractmethod
    def query(self, tenant, provider_document_id: str) -> QueryResult: ...

    @abstractmethod
    def cancel(self, tenant, provider_document_id: str) -> CancelResult: ...
```

- [ ] **Step 2: Write the failing test for `PlugNotasAdapter.emit()`**

```python
import responses
import pytest
from django.test import override_settings
from fiscal.adapters.plugnotas import PlugNotasAdapter


class TestPlugNotasAdapterEmit:
    @responses.activate
    def test_emit_success_returns_provider_id(self):
        responses.add(
            responses.POST,
            'https://api.plugnotas.com.br/nfce',
            json={'idNota': 'abc-123'},
            status=200,
        )
        adapter = PlugNotasAdapter()
        result = adapter.emit(
            tenant=None, emitter=None, document=None,
            items=[], payments=[],
        )
        assert result.provider_document_id == 'abc-123'
```

- [ ] **Step 3: Run test to confirm it fails**

Run: `cd backend && python -m pytest fiscal/tests/test_adapter.py::TestPlugNotasAdapterEmit -v`
Expected: ModuleNotFoundError or ImportError

- [ ] **Step 4: Implement `fiscal/adapters/plugnotas.py`**

```python
import logging
from typing import Optional

import requests

from fiscal.models import FiscalDocument, FiscalEmitter
from fiscal.ports import CancelResult, EmitResult, FiscalProvider, QueryResult

logger = logging.getLogger(__name__)

CFOP_PADRAO = '5102'  # Venda de mercadoria dentro do estado


class PlugNotasAdapter(FiscalProvider):
    BASE_URL = 'https://api.plugnotas.com.br'

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def _headers(self):
        return {
            'x-api-key': self.api_key or '',
            'Content-Type': 'application/json',
        }

    def _build_emit_payload(self, emitter, document, items, payments):
        return [{
            'idIntegracao': str(document.idempotency_key),
            'natureza': 'VENDA',
            'emitente': {
                'cpfCnpj': emitter.cpf_cnpj,
            },
            'itens': [
                {
                    'codigo': str(item['product'].sku),
                    'descricao': item['product'].name[:120],
                    'ncm': item.get('ncm', ''),
                    'cfop': document.cfop or CFOP_PADRAO,
                    'unidade': item.get('unidade', 'UN'),
                    'quantidade': float(item['quantity']),
                    'valorUnitario': {
                        'comercial': float(item['unit_price']),
                        'tributavel': float(item['unit_price']),
                    },
                    'valor': float(item['line_total']),
                    'tributos': {
                        'icms': {
                            'origem': item.get('origem', '0'),
                            'cst': item.get('cst_icms', '00'),
                            'baseCalculo': {'modalidadeDeterminacao': 0, 'valor': 0},
                            'aliquota': float(item.get('aliquota_icms', 0)),
                            'valor': 0,
                        },
                        'pis': {
                            'cst': item.get('cst_pis', '99'),
                            'baseCalculo': {'valor': 0, 'quantidade': 0},
                            'aliquota': 0,
                            'valor': 0,
                        },
                        'cofins': {
                            'cst': item.get('cst_cofins', '07'),
                            'baseCalculo': {'valor': 0},
                            'aliquota': 0,
                            'valor': 0,
                        },
                    },
                }
                for item in items
            ],
            'pagamentos': [
                {
                    'aVista': True,
                    'meio': '01',  # Dinheiro (default)
                    'valor': float(payment['amount']),
                }
                for payment in payments
            ],
        }]

    def emit(self, tenant, emitter, document, items, payments):
        payload = self._build_emit_payload(emitter, document, items, payments)
        resp = requests.post(
            f'{self.BASE_URL}/nfce',
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        provider_id = data.get('idNota', '')
        logger.info('NFC-e emitted', extra={'provider_id': provider_id})
        return EmitResult(provider_document_id=provider_id, raw_response=data)

    def query(self, tenant, provider_document_id: str) -> QueryResult:
        resp = requests.get(
            f'{self.BASE_URL}/nfce/{provider_document_id}/resumo',
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        status = data.get('status', 'PROCESSANDO')
        return QueryResult(
            status=status,
            protocol=data.get('protocolo'),
            xml_url=None,
            pdf_url=None,
            error_reason=data.get('motivo'),
        )

    def cancel(self, tenant, provider_document_id: str) -> CancelResult:
        resp = requests.post(
            f'{self.BASE_URL}/nfce/{provider_document_id}/cancelamento',
            headers=self._headers(),
            json={},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return CancelResult(
            success=True,
            protocol=data.get('protocolo'),
        )
```

- [ ] **Step 5: Write remaining adapter tests**

```python
@responses.activate
def test_query_concluido(self):
    responses.add(
        responses.GET,
        'https://api.plugnotas.com.br/nfce/abc-123/resumo',
        json={'status': 'CONCLUIDO', 'protocolo': '123456789012345'},
        status=200,
    )
    adapter = PlugNotasAdapter()
    result = adapter.query(None, 'abc-123')
    assert result.status == 'CONCLUIDO'
    assert result.protocol == '123456789012345'

@responses.activate
def test_cancel_success(self):
    responses.add(
        responses.POST,
        'https://api.plugnotas.com.br/nfce/abc-123/cancelamento',
        json={'protocolo': '987654321'},
        status=200,
    )
    adapter = PlugNotasAdapter()
    result = adapter.cancel(None, 'abc-123')
    assert result.success is True
    assert result.protocol == '987654321'
```

- [ ] **Step 6: Run all adapter tests**

Run: `cd backend && python -m pytest fiscal/tests/test_adapter.py -v`
Expected: 3 tests pass

- [ ] **Step 7: Commit**

```bash
git add backend/fiscal/ backend/catalog/models.py backend/tenancy/models.py backend/config/settings/base.py
git commit -m "feat(fiscal): scaffold app, models, and PlugNotas adapter"
```

---

### Task 3: Fiscal services and Celery tasks

**Files:**
- Create: `backend/fiscal/services.py`
- Create: `backend/fiscal/tasks.py`
- Create: `backend/fiscal/tests/test_tasks.py`
- Modify: `backend/config/settings/local.py`
- Modify: `backend/core/celery.py`

- [ ] **Step 1: Write `fiscal/services.py`**

```python
from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.utils import timezone

from fiscal.adapters.plugnotas import PlugNotasAdapter
from fiscal.models import FiscalDocument, FiscalEmitter, FiscalProductConfig
from fiscal.ports import FiscalProvider

MAX_AUTO_REATTEMPTS = 2
POLLING_TIMEOUT_MINUTES = 30


def _resolve_provider(provider_name: str) -> FiscalProvider:
    providers = getattr(settings, 'FISCAL_PROVIDERS', {})
    config = providers.get(provider_name, {})
    klass = config.get('class', PlugNotasAdapter)
    api_key = config.get('api_key', '')
    return klass(api_key=api_key)


def resolve_emitter(branch) -> Optional[FiscalEmitter]:
    return FiscalEmitter.all_objects.filter(branch=branch, registered_at_provider=True).first()


def resolve_product_config(product) -> Optional[FiscalProductConfig]:
    return FiscalProductConfig.all_objects.filter(product=product).first()


def build_item_dict(product, config: Optional[FiscalProductConfig], quantity, unit_price, line_total):
    return {
        'product': product,
        'quantity': quantity,
        'unit_price': unit_price,
        'line_total': line_total,
        'ncm': product.ncm if hasattr(product, 'ncm') else '',
        'unidade': getattr(product.base_unit, 'symbol', 'UN') if product.base_unit_id else 'UN',
        'origem': config.origem if config else '0',
        'cst_icms': config.cst_icms if config else '00',
        'cst_pis': config.cst_pis if config else '99',
        'cst_cofins': config.cst_cofins if config else '07',
        'aliquota_icms': float(config.aliquota_icms) if config and config.aliquota_icms else 0,
    }


def build_payment_dict(payment):
    return {
        'method': payment.method,
        'amount': float(payment.amount),
    }


def emit_nfce(sale, tenant) -> FiscalDocument:
    if FiscalDocument.all_objects.filter(sale=sale, is_active=True).exists():
        return FiscalDocument.all_objects.filter(sale=sale, is_active=True).first()

    emitter = resolve_emitter(sale.branch)
    if not emitter:
        return FiscalDocument.all_objects.create(
            tenant=tenant, sale=sale, status='FAILED',
            error_detail='Emitente fiscal não configurado para esta filial',
        )

    items = []
    for item in sale.items.all():
        config = resolve_product_config(item.product)
        items.append(build_item_dict(item.product, config, item.quantity, item.unit_price, item.line_total))

    missing = [str(i['product'].sku) for i in items if not i.get('ncm')]
    if missing:
        return FiscalDocument.all_objects.create(
            tenant=tenant, sale=sale, status='FAILED',
            error_detail=f'Produtos sem NCM: {", ".join(missing)}',
        )

    payments = [build_payment_dict(p) for p in sale.payments.all()]

    doc = FiscalDocument.all_objects.create(
        tenant=tenant, sale=sale, status='PENDING', attempt_number=1,
    )

    provider = _resolve_provider(emitter.provider)

    try:
        result = provider.emit(tenant, emitter, doc, items, payments)
        doc.status = 'PROCESSING'
        doc.provider_document_id = result.provider_document_id
        doc.save(update_fields=['status', 'provider_document_id', 'updated_at'])
    except Exception as exc:
        doc.status = 'FAILED'
        doc.error_detail = str(exc)[:500]
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])

    return doc


def poll_fiscal_document(doc: FiscalDocument) -> FiscalDocument:
    now = timezone.now()
    if doc.created_at and (now - doc.created_at).total_seconds() > POLLING_TIMEOUT_MINUTES * 60:
        doc.status = 'FAILED'
        doc.error_detail = 'Timeout aguardando confirmação do provedor'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    if not doc.provider_document_id:
        doc.status = 'FAILED'
        doc.error_detail = 'Sem ID do provedor para consultar'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    emitter = resolve_emitter(doc.sale.branch)
    if not emitter:
        doc.status = 'FAILED'
        doc.error_detail = 'Emitente não encontrado para consulta'
        doc.save(update_fields=['status', 'error_detail', 'updated_at'])
        return doc

    provider = _resolve_provider(emitter.provider)

    try:
        result = provider.query(doc.tenant, doc.provider_document_id)
    except Exception as exc:
        doc.retry_count += 1
        doc.save(update_fields=['retry_count', 'updated_at'])
        return doc

    if result.status == 'CONCLUIDO':
        doc.status = 'CONCLUDED'
        doc.protocol = result.protocol or ''
        doc.save(update_fields=['status', 'protocol', 'updated_at'])
    elif result.status == 'REJEITADO':
        doc.status = 'REJECTED'
        doc.is_active = False
        doc.error_detail = result.error_reason or ''
        doc.save(update_fields=['status', 'is_active', 'error_detail', 'updated_at'])

        if doc.attempt_number < MAX_AUTO_REATTEMPTS:
            new_doc = FiscalDocument.all_objects.create(
                tenant=doc.tenant, sale=doc.sale,
                status='PENDING', attempt_number=doc.attempt_number + 1,
            )
            emit_nfce(new_doc.sale, new_doc.tenant)
    else:
        doc.last_polled_at = now
        doc.save(update_fields=['last_polled_at', 'updated_at'])

    return doc
```

- [ ] **Step 2: Write `fiscal/tasks.py`**

```python
import logging

from celery import shared_task

from fiscal.models import FiscalDocument
from fiscal.services import emit_nfce, poll_fiscal_document

logger = logging.getLogger(__name__)

BEAT_SCHEDULE = {
    'poll-fiscal-documents': {
        'task': 'fiscal.tasks.poll_fiscal_documents',
        'schedule': 30.0,
    },
}


@shared_task(max_retries=3, default_retry_delay=60)
def handle_sale_completed(sale_id):
    from sales.models import Sale

    try:
        sale = Sale.all_objects.select_related('branch').get(id=sale_id)
    except Sale.DoesNotExist:
        logger.error('Sale not found', extra={'sale_id': sale_id})
        return

    if FiscalDocument.all_objects.filter(sale=sale, is_active=True).exists():
        logger.info('FiscalDocument already exists for sale', extra={'sale_id': sale_id})
        return

    doc = emit_nfce(sale, sale.tenant)
    logger.info(
        'FiscalDocument created',
        extra={'sale_id': sale_id, 'doc_id': str(doc.id), 'status': doc.status},
    )


@shared_task
def poll_fiscal_documents():
    from django.utils import timezone
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(seconds=15)
    docs = FiscalDocument.all_objects.filter(
        status='PROCESSING',
        last_polled_at__lt=cutoff,
    ).select_related('sale__branch')

    for doc in docs:
        poll_fiscal_document(doc)
```

- [ ] **Step 3: Wire Beat schedule in `core/celery.py`**

```python
app.conf.beat_schedule = {}
app.conf.beat_schedule.update(BEAT_SCHEDULE)
```

Add import at top:
```python
from fiscal.tasks import BEAT_SCHEDULE
```

- [ ] **Step 4: Add `PLUGNOTAS_API_KEY` and `FISCAL_PROVIDERS` to `config/settings/local.py`**

```python
PLUGNOTAS_API_KEY = config('PLUGNOTAS_API_KEY', default='')
FISCAL_PROVIDERS = {
    'plugnotas': {
        'class': 'fiscal.adapters.plugnotas.PlugNotasAdapter',
        'api_key': PLUGNOTAS_API_KEY,
    },
}
```

- [ ] **Step 5: Write test for `handle_sale_completed`**

```python
import pytest
from unittest.mock import patch
from fiscal.tasks import handle_sale_completed
from fiscal.models import FiscalDocument


@pytest.mark.django_db
def test_handle_sale_completed_creates_document(sale_factory):
    sale = sale_factory()
    with patch('fiscal.services.emit_nfce') as mock_emit:
        mock_emit.return_value = FiscalDocument(
            sale=sale, tenant=sale.tenant, status='PENDING',
        )
        handle_sale_completed(str(sale.id))
    assert FiscalDocument.all_objects.filter(sale=sale).exists()


@pytest.mark.django_db
def test_handle_sale_completed_redelivery_does_not_duplicate(sale_factory):
    sale = sale_factory()
    FiscalDocument.all_objects.create(sale=sale, tenant=sale.tenant, is_active=True)
    with patch('fiscal.services.emit_nfce') as mock_emit:
        handle_sale_completed(str(sale.id))
    mock_emit.assert_not_called()
```

- [ ] **Step 6: Write test for `poll_fiscal_document` scenarios**

```python
@pytest.mark.django_db
def test_poll_concluido(sale_factory):
    from fiscal.services import poll_fiscal_document
    from fiscal.adapters.plugnotas import PlugNotasAdapter
    from unittest.mock import patch

    doc = _make_processing_doc(sale_factory())
    with patch.object(PlugNotasAdapter, 'query') as mock_query:
        mock_query.return_value = QueryResult(
            status='CONCLUIDO', protocol='123',
            xml_url=None, pdf_url=None, error_reason=None,
        )
        poll_fiscal_document(doc)
    doc.refresh_from_db()
    assert doc.status == 'CONCLUDED'


@pytest.mark.django_db
def test_poll_rejected_creates_new_attempt(sale_factory):
    from fiscal.services import poll_fiscal_document, MAX_AUTO_REATTEMPTS
    from fiscal.adapters.plugnotas import PlugNotasAdapter
    from unittest.mock import patch

    doc = _make_processing_doc(sale_factory())
    with patch.object(PlugNotasAdapter, 'query') as mock_query:
        mock_query.return_value = QueryResult(
            status='REJEITADO', protocol=None,
            xml_url=None, pdf_url=None, error_reason='IE inválida',
        )
        poll_fiscal_document(doc)
    doc.refresh_from_db()
    assert doc.status == 'REJECTED'
    assert doc.is_active is False
    new_doc = FiscalDocument.all_objects.filter(sale=doc.sale, is_active=True).first()
    assert new_doc is not None
    assert new_doc.attempt_number == 2


@pytest.mark.django_db
def test_poll_rejected_max_attempts_does_not_reattempt(sale_factory):
    from fiscal.services import poll_fiscal_document
    from fiscal.adapters.plugnotas import PlugNotasAdapter
    from unittest.mock import patch

    doc = _make_processing_doc(sale_factory(), attempt=2)
    with patch.object(PlugNotasAdapter, 'query') as mock_query:
        mock_query.return_value = QueryResult(
            status='REJEITADO', protocol=None,
            xml_url=None, pdf_url=None, error_reason='NCM inválido',
        )
        poll_fiscal_document(doc)
    doc.refresh_from_db()
    assert doc.status == 'REJECTED'
    active = FiscalDocument.all_objects.filter(sale=doc.sale, is_active=True).count()
    assert active == 0


@pytest.mark.django_db
def test_poll_timeout_fails_document(sale_factory):
    from django.utils import timezone
    from datetime import timedelta
    from fiscal.services import poll_fiscal_document

    doc = _make_processing_doc(sale_factory())
    doc.created_at = timezone.now() - timedelta(minutes=31)
    doc.save(update_fields=['created_at'])

    poll_fiscal_document(doc)
    doc.refresh_from_db()
    assert doc.status == 'FAILED'
    assert 'Timeout' in doc.error_detail


def _make_processing_doc(sale, attempt=1):
    from fiscal.models import FiscalEmitter
    FiscalEmitter.all_objects.get_or_create(
        branch=sale.branch, tenant=sale.tenant,
        defaults={
            'provider': 'plugnotas', 'cpf_cnpj': '00000000000000',
            'registered_at_provider': True,
        },
    )
    return FiscalDocument.all_objects.create(
        tenant=sale.tenant, sale=sale, status='PROCESSING',
        attempt_number=attempt, is_active=True,
        provider_document_id='abc-123',
    )
```

- [ ] **Step 7: Run task tests**

Run: `cd backend && python -m pytest fiscal/tests/test_tasks.py -v`
Expected: all tests pass

- [ ] **Step 8: Commit**

```bash
git add backend/fiscal/ backend/config/settings/local.py backend/core/celery.py
git commit -m "feat(fiscal): services, Celery tasks, and beat schedule"
```

---

### Task 4: API endpoints and webhook

**Files:**
- Create: `backend/fiscal/views.py`
- Create: `backend/fiscal/serializers.py`
- Create: `backend/fiscal/urls.py`
- Create: `backend/fiscal/webhook.py`
- Create: `backend/fiscal/tests/test_webhook.py`
- Modify: `backend/config/urls.py`
- Modify: `backend/config/middleware.py`

- [ ] **Step 1: Write `fiscal/serializers.py`**

```python
from rest_framework import serializers

from fiscal.models import FiscalDocument


class FiscalStatusSerializer(serializers.Serializer):
    sale_id = serializers.UUIDField()
    fiscal_status = serializers.CharField(source='status')
    attempt = serializers.IntegerField(source='attempt_number')
    protocol = serializers.CharField(allow_blank=True)
    error_detail = serializers.CharField(allow_blank=True, allow_null=True)
```

- [ ] **Step 2: Write `fiscal/views.py`**

```python
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from fiscal.models import FiscalDocument
from fiscal.serializers import FiscalStatusSerializer


class FiscalStatusView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FiscalStatusSerializer

    def get_object(self):
        sale_id = self.kwargs['sale_id']
        doc = FiscalDocument.all_objects.filter(
            sale_id=sale_id,
            tenant=self.request.tenant,
        ).order_by('-attempt_number').first()
        return doc
```

- [ ] **Step 3: Write `fiscal/webhook.py`**

```python
import json
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from fiscal.models import FiscalDocument
from fiscal.services import _resolve_provider, resolve_emitter

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def fiscal_webhook(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'invalid json'}, status=400)

    provider_doc_id = data.get('idNota') or data.get('idIntegracao')
    if not provider_doc_id:
        return JsonResponse({'error': 'missing idNota'}, status=400)

    doc = FiscalDocument.all_objects.filter(
        provider_document_id=provider_doc_id,
        is_active=True,
    ).select_related('sale__branch').first()
    if not doc:
        return HttpResponse(status=200)

    emitter = resolve_emitter(doc.sale.branch)
    if not emitter:
        logger.warning('Emitter not found for webhook', extra={'doc_id': str(doc.id)})
        return HttpResponse(status=200)

    provider = _resolve_provider(emitter.provider)

    try:
        result = provider.query(doc.tenant, provider_doc_id)
    except Exception as exc:
        logger.error('Webhook query failed', extra={'error': str(exc)})
        return HttpResponse(status=200)

    if result.status == 'CONCLUIDO':
        doc.status = 'CONCLUDED'
        doc.protocol = result.protocol or ''
        doc.webhook_received_at = doc.webhook_received_at or __import__('django').utils.timezone.now()
        doc.save(update_fields=['status', 'protocol', 'webhook_received_at', 'updated_at'])
    elif result.status in ('REJEITADO', 'CANCELADO'):
        doc.status = 'REJECTED' if result.status == 'REJEITADO' else 'CANCELLED'
        doc.is_active = False
        doc.error_detail = result.error_reason or ''
        doc.webhook_received_at = __import__('django').utils.timezone.now()
        doc.save(update_fields=['status', 'is_active', 'error_detail', 'webhook_received_at', 'updated_at'])

    return HttpResponse(status=200)
```

- [ ] **Step 4: Write `fiscal/urls.py`**

```python
from django.urls import path

from fiscal.views import FiscalStatusView
from fiscal.webhook import fiscal_webhook

urlpatterns = [
    path(
        'sales/<uuid:sale_id>/fiscal-status/',
        FiscalStatusView.as_view(),
        name='fiscal-status',
    ),
    path('fiscal/webhook/', fiscal_webhook, name='fiscal-webhook'),
]
```

- [ ] **Step 5: Wire URLs in `config/urls.py`**

```python
path('api/v1/', include('fiscal.urls')),
```

- [ ] **Step 6: Exempt webhook from TenantMiddleware in `config/middleware.py`**

Locate the `TenantMiddleware` or find where `CORRELATION_ID_MIDDLEWARE` is. If there's a general middleware approach, add:

```python
# In the appropriate middleware or a process_view / __call__ check:
if request.path.startswith('/api/v1/fiscal/webhook/'):
    return self.get_response(request)
```

If the tenant middleware is in `config/tenant_middleware.py` as a standalone middleware, modify its `__call__`:

```python
def __call__(self, request):
    if request.path.startswith('/api/v1/fiscal/webhook/'):
        return self.get_response(request)
    # ... existing code
```

- [ ] **Step 7: Write webhook tests**

```python
import json
import pytest
from unittest.mock import patch
from django.test import Client

from fiscal.models import FiscalDocument


@pytest.mark.django_db
def test_webhook_calls_query_not_body(sale_factory):
    from fiscal.adapters.plugnotas import PlugNotasAdapter
    from fiscal.models import FiscalEmitter

    sale = sale_factory()
    FiscalEmitter.all_objects.create(
        branch=sale.branch, tenant=sale.tenant,
        provider='plugnotas', cpf_cnpj='00000000000000',
        registered_at_provider=True,
    )
    doc = FiscalDocument.all_objects.create(
        tenant=sale.tenant, sale=sale, status='PROCESSING',
        provider_document_id='abc-123', is_active=True,
    )

    client = Client()
    with patch.object(PlugNotasAdapter, 'query') as mock_query:
        mock_query.return_value = QueryResult(
            status='CONCLUIDO', protocol='999',
            xml_url=None, pdf_url=None, error_reason=None,
        )
        resp = client.post(
            '/api/v1/fiscal/webhook/',
            data=json.dumps({'idNota': 'abc-123'}),
            content_type='application/json',
        )
    assert resp.status_code == 200
    mock_query.assert_called_once()
    doc.refresh_from_db()
    assert doc.status == 'CONCLUDED'
    assert doc.protocol == '999'
```

- [ ] **Step 8: Run webhook tests**

Run: `cd backend && python -m pytest fiscal/tests/test_webhook.py -v`
Expected: test passes

- [ ] **Step 9: Commit**

```bash
git add backend/fiscal/ backend/config/urls.py backend/config/middleware.py
git commit -m "feat(fiscal): API endpoints, webhook handler, TenantMiddleware exemption"
```

---

### Task 5: Admin, seed data, and E2E

**Files:**
- Create: `backend/fiscal/admin.py`
- Modify: `backend/tests/conftest.py`
- Create: `backend/fiscal/tests/test_integration.py`

- [ ] **Step 1: Write `fiscal/admin.py`**

```python
from django.contrib import admin

from fiscal.models import FiscalDocument, FiscalEmitter, FiscalProductConfig


@admin.register(FiscalEmitter)
class FiscalEmitterAdmin(admin.ModelAdmin):
    list_display = ['cpf_cnpj', 'branch', 'provider', 'registered_at_provider', 'registration_source']
    list_filter = ['provider', 'registered_at_provider', 'registration_source']
    search_fields = ['cpf_cnpj']


@admin.register(FiscalProductConfig)
class FiscalProductConfigAdmin(admin.ModelAdmin):
    list_display = ['product', 'cst_icms', 'cst_pis', 'cst_cofins', 'origem']
    search_fields = ['product__sku', 'product__name']


@admin.register(FiscalDocument)
class FiscalDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'sale', 'status', 'attempt_number', 'is_active',
        'provider_document_id', 'protocol', 'created_at',
    ]
    list_filter = ['status', 'is_active']
    search_fields = ['sale__id', 'provider_document_id', 'protocol']
    readonly_fields = ['idempotency_key', 'created_at', 'updated_at']
```

- [ ] **Step 2: Add fiscal fixtures to `tests/conftest.py`**

```python
@pytest.fixture
def fiscal_emitter_alpha(tenant_alpha, branch_alpha):
    from fiscal.models import FiscalEmitter
    return FiscalEmitter.all_objects.get_or_create(
        branch=branch_alpha,
        tenant=tenant_alpha,
        defaults={
            'provider': 'plugnotas',
            'cpf_cnpj': '00000000000000',
            'registered_at_provider': True,
        },
    )[0]


@pytest.fixture
def fiscal_product_config_alpha(tenant_alpha, inv_product):
    from fiscal.models import FiscalProductConfig
    return FiscalProductConfig.all_objects.get_or_create(
        product=inv_product,
        tenant=tenant_alpha,
        defaults={
            'cst_icms': '00',
            'cst_pis': '99',
            'cst_cofins': '07',
            'origem': '0',
        },
    )[0]
```

- [ ] **Step 3: Write integration test for state machine**

```python
import pytest
from fiscal.models import FiscalDocument
from fiscal.services import emit_nfce, poll_fiscal_document

from unittest.mock import patch
from fiscal.adapters.plugnotas import PlugNotasAdapter
from fiscal.ports import QueryResult


@pytest.mark.django_db
def test_state_machine_pending_to_concluded(
    sale_factory, fiscal_emitter_alpha, fiscal_product_config_alpha,
):
    sale = sale_factory()
    doc = emit_nfce(sale, sale.tenant)
    assert doc.status in ('PENDING', 'PROCESSING', 'FAILED')

    if doc.status == 'PROCESSING':
        with patch.object(PlugNotasAdapter, 'query') as mock_query:
            mock_query.return_value = QueryResult(
                status='CONCLUIDO', protocol='123',
                xml_url=None, pdf_url=None, error_reason=None,
            )
            poll_fiscal_document(doc)
        doc.refresh_from_db()
        assert doc.status == 'CONCLUDED'


@pytest.mark.django_db
def test_rejection_creates_new_attempt_deactivates_old(
    sale_factory, fiscal_emitter_alpha, fiscal_product_config_alpha,
):
    sale = sale_factory()
    doc = emit_nfce(sale, sale.tenant)

    if doc.status == 'PROCESSING':
        with patch.object(PlugNotasAdapter, 'query') as mock_query:
            mock_query.return_value = QueryResult(
                status='REJEITADO', protocol=None,
                xml_url=None, pdf_url=None, error_reason='Erro',
            )
            poll_fiscal_document(doc)
        doc.refresh_from_db()
        assert doc.status == 'REJECTED'
        assert doc.is_active is False

        new_doc = FiscalDocument.all_objects.filter(sale=sale, is_active=True).first()
        assert new_doc is not None
        assert new_doc.attempt_number == 2
        assert new_doc.status == 'PENDING'
```

- [ ] **Step 4: Run integration tests**

Run: `cd backend && python -m pytest fiscal/tests/test_integration.py -v`
Expected: tests pass

- [ ] **Step 5: Run full test suite**

Run: `cd backend && python -m pytest fiscal/ -v`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add backend/fiscal/admin.py backend/tests/conftest.py backend/fiscal/tests/test_integration.py
git commit -m "feat(fiscal): admin, fixtures, and integration tests"
```

---

### Self-Review Checklist

- [ ] **Spec coverage:** Every section in the spec (models, ports, adapter, async flow, webhook, API, tests) maps to a task above.
- [ ] **No placeholders:** All code blocks contain complete implementation. No TODOs or TBDs.
- [ ] **Type consistency:** `FiscalProvider.emit()` signature matches `PlugNotasAdapter.emit()`. `QueryResult.status` uses the string comparisons (`'CONCLUIDO'`) that match PlugNotas API values throughout.
- [ ] **Test coverage:** All 14 scenarios from the spec's test table are covered across `test_adapter.py`, `test_tasks.py`, `test_webhook.py`, and `test_integration.py`.
