# Sprint 9 Returns Cancellations Refunds Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement auditable returns, sale cancellations and refund records without mutating confirmed sales.

**Architecture:** Extend the `sales` context with compensating aggregates and transactional services that call inventory, cash and fiscal ports only through explicit application services.

**Tech Stack:** Django, DRF, PostgreSQL, pytest-django, existing `sales`, `inventory`, `fiscal`, `audit`, `outbox`.

---

### Task 1: Domain model

**Files:**
- Modify: `backend/sales/models.py`
- Create: `backend/sales/migrations/`
- Create: `backend/tests/test_sales_returns_models.py`

- [ ] Write failing model tests for `SaleReturn`, `SaleReturnItem`, `SaleRefund` and `SaleCancellation`.
- [ ] Add models with tenant scope, immutable references and status fields.
- [ ] Add constraints preventing duplicate idempotency keys and negative quantities/amounts.
- [ ] Generate migrations.
- [ ] Run model tests and migration check.

### Task 2: Return service

**Files:**
- Modify: `backend/sales/services.py`
- Create: `backend/tests/test_sales_returns_services.py`

- [ ] Write failing test for partial return reentering stock.
- [ ] Write failing test blocking return above sold quantity.
- [ ] Write failing test for idempotent replay.
- [ ] Implement `create_sale_return()` using `transaction.atomic`.
- [ ] Use inventory reversal/receipt semantics without creating negative stock.
- [ ] Emit audit and Outbox event `sales.return.created`.

### Task 3: Refund and cash effects

**Files:**
- Modify: `backend/sales/services.py`
- Create: `backend/tests/test_sales_refunds_services.py`

- [ ] Write failing test for cash refund creating cash-out movement.
- [ ] Write failing test for Pix/card refund creating tracked refund without cash drawer impact.
- [ ] Implement refund method rules.
- [ ] Verify closed cash session rejects new cash movement.
- [ ] Emit audit and Outbox event `sales.refund.created`.

### Task 4: Cancellation service and fiscal hook

**Files:**
- Modify: `backend/sales/services.py`
- Modify: `backend/fiscal/services.py`
- Create: `backend/tests/test_sales_cancellations_services.py`

- [ ] Write failing test for full sale cancellation creating compensating stock movement.
- [ ] Write failing test for cancellation blocked after return already exists unless policy allows it.
- [ ] Write failing test for fiscal cancellation request when fiscal document is authorized and inside allowed policy.
- [ ] Implement `cancel_sale()` with idempotency.
- [ ] Emit `sales.sale.cancelled` and fiscal command/outbox when applicable.

### Task 5: API endpoints

**Files:**
- Modify: `backend/sales/serializers.py`
- Modify: `backend/sales/views.py`
- Modify: `backend/sales/urls.py`
- Create: `backend/tests/test_sales_returns_api.py`

- [ ] Write failing API tests for return, refund and cancellation endpoints.
- [ ] Implement DRF serializers and actions.
- [ ] Return Problem Details for insufficient returnable quantity, missing cash session, fiscal blocked and idempotency conflict.
- [ ] Add cross-tenant negative tests.

### Task 6: Documentation and quality

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-009_Returns_Cancellations_Refunds_Final_Report.md`

- [ ] Update Sprint 9 checklist in PRD.
- [ ] Record fiscal limitations and operational decisions.
- [ ] Run focused tests, full backend suite, Ruff, mypy, check and migration check.
- [ ] Mark tasks only with evidence.
