# Sprint 4 Sales Cash Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build online counter sale with registered payment, immediate stock deduction, cash movement, audit and Outbox.

**Architecture:** Add a focused Django app `sales` with models, serializers, services and DRF viewsets. Business writes go through transactional services and all write endpoints require tenant, MFA and idempotency.

**Tech Stack:** Django 5, Django REST Framework, PostgreSQL, pytest-django, existing `inventory`, `catalog`, `audit`, `outbox` and `tenancy` apps.

---

### Task 1: App foundation and models

**Files:**
- Create: `backend/sales/__init__.py`
- Create: `backend/sales/apps.py`
- Create: `backend/sales/models.py`
- Modify: `backend/config/settings/base.py`

- [ ] Create the `sales` app files.
- [ ] Add `sales` to `LOCAL_APPS`.
- [ ] Define `CashSession`, `CashMovement`, `Sale`, `SaleItem` and `SalePayment`.
- [ ] Add constraints for one open cash session per tenant/branch/operator and unique sale idempotency key.
- [ ] Run `makemigrations sales`.

### Task 2: Service layer with TDD

**Files:**
- Create: `backend/sales/services.py`
- Create: `backend/tests/test_sales_services.py`

- [ ] Write failing tests for opening cash sessions.
- [ ] Implement idempotent `open_cash_session`.
- [ ] Write failing tests for counter sale confirmation.
- [ ] Implement `create_counter_sale` with transaction, stock issue, cash movement, audit and Outbox.
- [ ] Write failing tests for validation failures and idempotency conflicts.
- [ ] Make the service tests pass.

### Task 3: API layer with TDD

**Files:**
- Create: `backend/sales/serializers.py`
- Create: `backend/sales/views.py`
- Create: `backend/sales/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_sales_api.py`

- [ ] Write failing API tests for opening/current/closing cash session.
- [ ] Implement serializers and viewsets.
- [ ] Write failing API tests for `POST /api/v1/sales/counter/`.
- [ ] Implement sale endpoint and problem responses.
- [ ] Make API tests pass.

### Task 4: Documentation and quality gates

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-004_Sales_Cash_Web_Final_Report.md`

- [ ] Update Sprint 4 checklist in PRD as tasks are completed.
- [ ] Record evidence in final report.
- [ ] Run Ruff, mypy, Django check, makemigrations check and focused tests.
- [ ] Run full suite when focused tests are green.
- [ ] Commit as `feat: sprint 4 - vendas caixa web`.
