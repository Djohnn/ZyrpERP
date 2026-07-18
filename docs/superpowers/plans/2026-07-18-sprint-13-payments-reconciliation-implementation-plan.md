# Sprint 13 Payments Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add payment provider contracts, fake provider integration, webhook idempotency and reconciliation of gross/net payment amounts.

**Architecture:** Add `payments` as an integration context. Sales owns the sale, financial owns receivables/settlements, and payments owns provider communication, transactions, webhooks and reconciliation batches.

**Tech Stack:** Django, DRF, PostgreSQL, pytest-django, existing `sales`, `financial`, `audit`, `outbox`.

---

### Task 1: Payment models

**Files:**
- Create: `backend/payments/__init__.py`
- Create: `backend/payments/apps.py`
- Create: `backend/payments/models.py`
- Modify: `backend/config/settings/base.py`
- Create: `backend/tests/test_payments_models.py`

- [ ] Write failing tests for provider config, payment intent, transaction and webhook uniqueness.
- [ ] Create `PaymentProviderConfig`, `PaymentIntent`, `PaymentTransaction`, `PaymentWebhookEvent`, `PaymentReconciliationBatch` and `PaymentReconciliationItem`.
- [ ] Add idempotency and provider reference constraints.
- [ ] Generate migrations.

### Task 2: Provider contract and fake adapter

**Files:**
- Create: `backend/payments/providers/base.py`
- Create: `backend/payments/providers/fake.py`
- Create: `backend/tests/test_payment_provider_contract.py`

- [ ] Write failing tests for create intent, capture, cancel and refund methods.
- [ ] Define provider result dataclasses.
- [ ] Implement fake provider with deterministic responses.
- [ ] Ensure provider secrets never appear in string representation or logs.

### Task 3: Payment services

**Files:**
- Create: `backend/payments/services.py`
- Create: `backend/tests/test_payment_services.py`

- [ ] Write failing test for creating a payment intent from sale amount.
- [ ] Write failing test for capture updating transaction state.
- [ ] Write failing test for duplicate webhook replay.
- [ ] Implement service functions with `transaction.atomic`.
- [ ] Emit audit and Outbox events for state changes.

### Task 4: Reconciliation

**Files:**
- Modify: `backend/payments/services.py`
- Modify: `backend/financial/services.py`
- Create: `backend/tests/test_payment_reconciliation.py`

- [ ] Write failing test for reconciling gross amount, fee and net settlement.
- [ ] Write failing test for divergence requiring manual review.
- [ ] Implement reconciliation batch import and confirmation.
- [ ] Create financial adjustment or settlement records through financial service.

### Task 5: API and webhooks

**Files:**
- Create: `backend/payments/serializers.py`
- Create: `backend/payments/views.py`
- Create: `backend/payments/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_payments_api.py`

- [ ] Write failing API tests for intent creation, transaction listing, webhook and reconciliation confirmation.
- [ ] Implement endpoints with tenant filtering and Problem Details.
- [ ] Validate webhook signature for fake provider with deterministic secret.
- [ ] Add cross-tenant negative tests.

### Task 6: Documentation and quality

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/03_Domain/PAYMENT_PROVIDER_CONTRACT.md`
- Create: `docs/10_Releases/SPRINT-013_Payments_Reconciliation_Final_Report.md`

- [ ] Update Sprint 13 checklist in PRD.
- [ ] Document manual/external payment support versus integrated provider support.
- [ ] Run focused tests, full backend suite, Ruff, mypy, check and migration check.
- [ ] Record evidence in final report.
