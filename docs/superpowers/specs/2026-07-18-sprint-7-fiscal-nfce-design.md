# Sprint 7 — NFC-e via PlugNotas

| Campo | Valor |
|---|---|
| Status | Draft |
| Data | 2026-07-18 |
| Sprint | 7 |
| Provedor | PlugNotas (TecnoSpeed) |
| Documento | NFC-e (modelo 65) |

## 1. Objetivo

Emitir NFC-e automaticamente após cada venda confirmada no PDV, usando PlugNotas como provedor fiscal externo. Cliente cadastra empresa emitente no portal PlugNotas (manual); nosso sistema consome a API REST.

## 2. Decisões de design

### 2.1 Provedor fiscal

- **PlugNotas** via API REST (`x-api-key` header, sem SigV4).
- Documento: **NFC-e** (modelo 65) — venda direta ao consumidor no PDV.
- Cadastro do emitente é **manual no portal PlugNotas**. O modelo prevê `registration_source` e `registered_at_provider` para automação futura, sem implementar certificado ou upload agora.

### 2.2 Modelagem de dados

| Dado | Onde fica | Motivo |
|---|---|---|
| NCM | `Product` (novo campo) | Identidade estável do produto |
| CFOP | App fiscal, **regra/constante** (5102 no MVP) | Depende do contexto da venda, não do produto |
| Endereço, IE, código município | `Company`/`Branch` | Dado cadastral, não fiscal |
| CST ICMS/PIS/COFINS, alíquotas, origem | `FiscalProductConfig` (app fiscal) | Varia por regime tributário |
| Emitente fiscal | `FiscalEmitter` referenciando `Branch` | IE é por estabelecimento, não por empresa |

### 2.3 Fluxo de emissão

```
Venda confirmada → Outbox (SaleCompleted) → Celery task → PlugNotas API → polling → conclusão
```

- A view de venda **não** bloqueia para emitir NFC-e.
- `handle_sale_completed` (Celery) cria `FiscalDocument`, chama `PlugNotasAdapter.emit()`, e agenda polling.
- `poll_fiscal_document` (Celery Beat) varre documentos em PROCESSING, consulta PlugNotas, atualiza status.
- Frontend consulta `GET /sales/{id}/fiscal-status/` — lê do nosso banco, nunca do PlugNotas.
- Webhook é opcional (otimizador). Se receber, atualiza mais rápido; polling é a segurança.

### 2.4 Segurança webhook

- Rota `POST /api/v1/fiscal/webhook/` isenta de `TenantMiddleware` (path exemption).
- O payload do webhook **não é confiável como fonte de dado** — serve apenas de índice (`provider_document_id`) para disparar `adapter.query()`. Status e protocolo gravados vêm sempre da API do PlugNotas, nunca do corpo do POST recebido.

## 3. Models

### Product (catalog)

```python
# existing Product + novo campo
ncm = models.CharField(max_length=8, blank=True, default='')
```

### Company (tenancy)

```python
# novos campos
ie = models.CharField('Inscrição Estadual', max_length=20, blank=True, default='')
address_json = models.JSONField(default=dict, blank=True)
# { "logradouro", "numero", "complemento", "bairro", "codigoCidade", "descricaoCidade", "estado", "cep" }
```

### Branch (tenancy)

```python
# novo campo
ie = models.CharField('Inscrição Estadual', max_length=20, blank=True, default='')
address_json = models.JSONField(default=dict, blank=True)
```

### FiscalEmitter (fiscal)

```python
class FiscalEmitter(TenantScopedModel, TimeStampedModel):
    branch = models.ForeignKey('tenancy.Branch', on_delete=models.PROTECT)
    provider = models.CharField(max_length=30)  # 'plugnotas'
    cpf_cnpj = models.CharField(max_length=18)
    ie = models.CharField(max_length=20, blank=True, default='')
    registration_source = models.CharField(
        max_length=20,
        choices=[('manual', 'Manual'), ('automated', 'Automatizado')],
        default='manual',
    )
    registered_at_provider = models.BooleanField(default=False)
```

### FiscalProductConfig (fiscal)

```python
class FiscalProductConfig(TenantScopedModel, TimeStampedModel):
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT)
    cst_icms = models.CharField(max_length=4, blank=True, default='')
    cst_pis = models.CharField(max_length=4, blank=True, default='')
    cst_cofins = models.CharField(max_length=4, blank=True, default='')
    aliquota_icms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    origem = models.CharField(max_length=1, blank=True, default='0')
```

### FiscalDocument (fiscal)

```python
STATUS_CHOICES = [
    ('PENDING', 'Pendente'),
    ('QUEUED', 'Na fila'),
    ('PROCESSING', 'Processando'),
    ('CONCLUDED', 'Concluído'),
    ('REJECTED', 'Rejeitado'),
    ('CANCELLED', 'Cancelado'),
    ('FAILED', 'Falha técnica'),
]

class FiscalDocument(TenantScopedModel, TimeStampedModel):
    sale = models.ForeignKey('sales.Sale', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    attempt_number = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    provider_document_id = models.CharField(max_length=100, blank=True, default='')
    cfop = models.CharField(max_length=4, default='5102')
    idempotency_key = models.UUIDField(default=uuid.uuid4)  # nova a cada attempt
    # Artefatos
    xml_key = models.CharField(max_length=255, blank=True, default='')  # S3 key
    protocol = models.CharField(max_length=60, blank=True, default='')
    pdf_key = models.CharField(max_length=255, blank=True, default='')
    # Controle
    error_detail = models.TextField(blank=True, default='')
    retry_count = models.PositiveIntegerField(default=0)
    last_polled_at = models.DateTimeField(null=True, blank=True)
    webhook_received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
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
```

## 4. Ports/Adapters

### FiscalProvider (ports.py)

```python
class EmitResult(NamedTuple):
    provider_document_id: str
    raw_response: dict

class QueryResult(NamedTuple):
    status: str  # CONCLUIDO | REJEITADO | PROCESSANDO | CANCELADO
    protocol: str | None
    xml_url: str | None
    pdf_url: str | None
    error_reason: str | None

class CancelResult(NamedTuple):
    success: bool
    protocol: str | None

class FiscalProvider(ABC):
    @abstractmethod
    def emit(self, tenant, emitter: FiscalEmitter, document: FiscalDocument,
             items: list, payments: list) -> EmitResult: ...
    @abstractmethod
    def query(self, tenant, provider_document_id: str) -> QueryResult: ...
    @abstractmethod
    def cancel(self, tenant, provider_document_id: str) -> CancelResult: ...
```

### PlugNotasAdapter (adapters/plugnotas.py)

- `BASE_URL = "https://api.plugnotas.com.br"`
- Auth: `{"x-api-key": settings.PLUGNOTAS_API_KEY}`
- `emit()` → `POST /nfce` com JSON NFC-e montado (emitente, itens, pagamentos, CFOP 5102)
- `query()` → `GET /nfce/{idNota}/resumo`
- `cancel()` → `POST /nfce/{idNota}/cancelamento`

Provider resolution: `FiscalEmitter.provider` → lookup em `settings.FISCAL_PROVIDERS` dict.

## 5. Fluxo assíncrono

Constantes:
- `MAX_AUTO_REATTEMPTS = 2` — após 2 tentativas rejeitadas, aguarda ação manual.
- `POLLING_TIMEOUT = timedelta(minutes=30)` — SLA máximo em PROCESSING.
- `POLLING_INTERVAL = timedelta(seconds=15)` — intervalo mínimo entre polls do mesmo documento.

### 5.1 handle_sale_completed (Celery task)

```
1. Se já existe FiscalDocument is_active para sale_id → return (idempotência)
2. Cria FiscalDocument(sale, status=PENDING, attempt=1)
3. Resolve FiscalEmitter via branch da sale
   └─ Se não existe → status=FAILED, error="Emitente não configurado para esta filial"
4. Resolve FiscalProductConfig para cada item vendido
   └─ Se algum item não tem config → status=FAILED, error="Produto X sem config fiscal (NCM/CST)"
5. Chama adapter.emit()
   ├─ Sucesso → status=PROCESSING, salva provider_document_id
   └─ Falha técnica → status=FAILED, agenda retry (exponential backoff, max_retries)
```

### 5.2 poll_fiscal_document (Celery Beat, ex: a cada 30s)

```
1. Busca documentos status=PROCESSING, last_polled_at < now - 15s
2. Para cada:
   ├─ Se created_at + POLLING_TIMEOUT < now → status=FAILED, error=timeout
   ├─ Chama adapter.query()
   │    ├─ CONCLUIDO → status=CONCLUDED, baixa XML/PDF → S3
   │    ├─ REJEITADO → status=REJECTED, is_active=False
   │    │              Se attempt < MAX_AUTO_REATTEMPTS (2):
   │    │                novo FiscalDocument(attempt+1) → enfileira reemissão
   │    │              Senão: aguarda correção manual via admin
   │    └─ PROCESSANDO → atualiza last_polled_at
```

### 5.3 Webhook handler

Webhook é **gatilho, não fonte de dados**. O payload só informa QUAL documento consultar; o status real vem da API do PlugNotas.

```
POST /api/v1/fiscal/webhook/
→ lê idNota do payload (índice, não dado confiável)
→ lookup FiscalDocument por provider_document_id
→ chama adapter.query(idNota) — fonte da verdade
→ atualiza status, protocolo, XML/PDF com resultado de query()
→ marca webhook_received_at
→ return 200
```

## 6. API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/sales/{sale_id}/fiscal-status/` | Status + protocolo + URLs (se autorizado) |
| `POST` | `/api/v1/fiscal/webhook/` | Callback PlugNotas (isento de TenantMiddleware) |

Resposta `fiscal-status`:
```json
{
  "sale_id": "uuid",
  "fiscal_status": "CONCLUDED",
  "attempt": 1,
  "protocol": "123456789012345",
  "pdf_url": "/api/v1/sales/{id}/fiscal-danfe/",
  "xml_url": "/api/v1/sales/{id}/fiscal-xml/",
  "error_detail": null
}
```

## 7. Testes

| Tipo | Cenário |
|---|---|
| Unit (adapter) | `emit()` mocka POST /nfce → sucesso |
| Unit (adapter) | `query()` mocka GET → CONCLUIDO/REJEITADO/PROCESSANDO |
| Unit (adapter) | `cancel()` mocka POST → cancelamento |
| Unit (task) | `handle_sale_completed` cria FiscalDocument PENDING |
| Unit (task) | `handle_sale_completed` **redelivery** → não duplica documento |
| Unit (task) | `poll_fiscal_document` → PROCESSING → CONCLUDED |
| Unit (task) | `poll_fiscal_document` → PROCESSING → REJECTED → novo attempt (se < 2) |
| Unit (task) | `poll_fiscal_document` → REJECTED no **attempt máximo** → não reenfileira |
| Unit (task) | `poll_fiscal_document` → **timeout** (30min) → FAILED |
| Unit (webhook) | Payload recebido → chama `adapter.query()` (não usa body como fonte) |
| Integration | State machine: PENDING → QUEUED → PROCESSING → CONCLUDED |
| Integration | Rejeição → novo attempt com is_active anterior=False |
| Integration | Cancelamento via adapter |
| E2E | Venda completa → aguarda polling → FiscalDocument CONCLUDED |

## 8. Fora do escopo da Sprint 7

- **Cancelamento orquestrado:** `cancel()` é implementado e testado no adapter, mas a orquestração (quando/quem dispara o cancelamento de uma NFC-e autorizada) depende do fluxo de cancelamento/devolução de venda, ainda não definido.
- NF-e (modelo 55) — B2B com transporte
- NFS-e (serviço)
- Cadastro automático de emitente via API
- Upload/gestão de certificado A1
- Tabela de regras de CFOP (hardcoded 5102 no MVP)
- Devolução fiscal
- Carta de Correção (CC-e)
- Inutilização de numeração
