# Sprint 9 — Devoluções, Cancelamentos e Estornos — Relatório Final

**Data:** 2026-07-18 a 2026-07-21
**Branch:** `feat/on-demand-fiscal`

---

## Resumo

Sprint concluída com implementação completa do ciclo pós-venda: devolução parcial/total, cancelamento de venda, reentrada de estoque auditável, reflexo em caixa/pagamentos e API REST documentada. Cancelamento fiscal permanece on-demand (nunca automático), conforme decisão de design.

## O que foi entregue

### Modelos de domínio (`sales/models.py`)

| Modelo | Finalidade |
|--------|------------|
| `SaleReturn` | Cabeçalho da devolução (status, reason, idempotency_key) |
| `SaleReturnItem` | Item devolvido vinculado ao `SaleItem` original |
| `SaleRefund` | Reembolso financeiro (método, valor, status) |
| `SaleCancellation` | Cancelamento total da venda |

- Todos com `TenantScopedModel`, `idempotency_key` única por tenant, UUID pk, `AuditableMixin`.
- Migration `0003` gerada e aplicada.

### Serviços (`sales/services.py`)

| Serviço | Comportamento |
|---------|---------------|
| `create_sale_return()` | Devolução parcial/total; valida saldo devolvível; reentra estoque via `create_receipt`; idempotente |
| `create_sale_refund()` | Reembolso: `cash` → `cash_out` no caixa; `pix`/`card_external` → registro sem movimento |
| `cancel_sale()` | Reverte estoque total; reembolso automático para dinheiro; marca `cancelled`; idempotente |

- Idempotência via `idempotency_key` com `DuplicateIdempotencyKey` em conflito.
- Auditoria via `AuditableMixin` e `outbox` events.

### API REST (`sales/views.py`)

| Endpoint | Método | Ação |
|----------|--------|------|
| `POST /api/v1/sales/{id}/returns/` | Cria devolução | `201` ou Problem Details |
| `GET /api/v1/sales/{id}/returns/` | Lista devoluções | `200` |
| `POST /api/v1/sales/{id}/cancel/` | Cancela venda | `200` ou Problem Details |

- `CreateSaleReturnSerializer`, `SaleReturnSerializer`, `CreateSaleCancellationSerializer`, `SaleCancellationSerializer`.
- Problem Details para `InsufficientReturnableQuantity` (409), `SaleAlreadyCancelled` (409), `DuplicateIdempotencyKey` (409).

## Decisões de design

1. **Venda confirmada é imutável** — correções geram fatos compensatórios auditáveis, nunca alteram a venda original.
2. **NFC-e emitida sob demanda** — nunca automática. Cancelamento fiscal será solicitado manualmente pelo operador via interface futura.
3. **Reembolso em dinheiro** move o caixa (`cash_out`); **Pix e cartão externo** registram sem movimentação de caixa (processamento externo).
4. **Cancelamento com pagamento em dinheiro** gera reembolso automático; demais métodos apenas registram o reembolso.
5. **Idempotência** em todos os serviços transacionais — `Idempotency-Key` header obrigatório.

## Resultados dos testes

### Suíte focada (Sprint 9)

| Teste | Arquivo | Resultado |
|-------|---------|-----------|
| 15 testes de modelo | `test_sales_returns_models.py` | ✅ 15 passed |
| 4 testes return service | `test_sales_returns_services.py` | ✅ 4 passed |
| 5 testes refund service | `test_sales_refunds_services.py` | ✅ 5 passed |
| 4 testes cancellation service | `test_sales_cancellations_services.py` | ✅ 4 passed |
| 6 testes de API | `test_sales_returns_api.py` | ✅ 6 passed |
| **Total** | | **34 passed** |

### Suíte completa (269 passed, 2 pre-existing failures)

- Falhas pré-existentes não relacionadas:
  - `test_fiscal_webhook_queries_provider_instead_of_trusting_body` — unique constraint com `--reuse-db`
  - `test_password_recovery_is_generic_and_single_use` — 401 vs 403

## Quality gate

| Ferramenta | Resultado |
|------------|-----------|
| Ruff | ✅ 0 errors no código Sprint 9 (8 pré-existentes) |
| Testes focados | ✅ 34/34 passed |
| Testes completos | ✅ 269 passed (2 pré-existentes) |

## Arquivos alterados/criados

- `backend/sales/models.py` — `SaleReturn`, `SaleReturnItem`, `SaleRefund`, `SaleCancellation`
- `backend/sales/services.py` — `create_sale_return()`, `create_sale_refund()`, `cancel_sale()`
- `backend/sales/serializers.py` — serializers de input/output
- `backend/sales/views.py` — `@action` methods `returns` e `cancel`
- `backend/sales/urls.py` — rotas (via `DefaultRouter`)
- `backend/sales/migrations/0003_add_return_refund_cancellation_models.py`
- `backend/tests/test_sales_returns_models.py` — 15 testes
- `backend/tests/test_sales_returns_services.py` — 4 testes
- `backend/tests/test_sales_refunds_services.py` — 5 testes
- `backend/tests/test_sales_cancellations_services.py` — 4 testes
- `backend/tests/test_sales_returns_api.py` — 6 testes
- `docs/superpowers/specs/2026-07-18-sprint-9-returns-cancellations-refunds-design.md`
- `docs/superpowers/plans/2026-07-18-sprint-9-returns-cancellations-refunds-implementation-plan.md`
- `docs/10_Releases/SPRINT-009_Returns_Cancellations_Refunds_Final_Report.md` (este)

## Pendências

- Interface de usuário para devolução/cancelamento (Sprint futura).
- Cancelamento fiscal on-demand via NFC-e autorizada.
