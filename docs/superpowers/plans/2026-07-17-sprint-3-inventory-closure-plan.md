# Sprint 3 Inventory Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Close Sprint 3 by enforcing lot/expiry, idempotent stock writes, no negative stock under concurrency, RLS, reconciliation, API documentation, and objective validation.

**Architecture:** Keep the existing `inventory` app. Harden domain services first, route API writes through services, add RLS via migration, and prove behavior with pytest before updating PRD/report checkboxes.

**Tech Stack:** Django 5, Django REST Framework, PostgreSQL, pytest-django, Ruff.

---

### Task 1: Domain service hardening

**Files:**
- Modify: `backend/inventory/services.py`
- Test: `backend/tests/test_inventory_closure.py`

- [x] Add failing tests for required lot, required expiry, expired-lot blocking, idempotency conflict, transfer rollback, reversal uniqueness, and reconciliation divergence.
- [x] Implement payload fingerprinting for idempotency.
- [x] Enforce `Idempotency-Key` for service writes except explicit internal non-API usage.
- [x] Lock balances with `select_for_update` and deterministic ordering for transfers.
- [x] Add reconciliation service returning divergences without silent correction.

### Task 2: API write hardening

**Files:**
- Modify: `backend/inventory/serializers.py`
- Modify: `backend/inventory/views.py`
- Test: `backend/tests/test_inventory_api_closure.py`

- [x] Add write serializers/actions for receipt, issue, adjustment, transfer, and reversal.
- [x] Require `Idempotency-Key` header on write actions.
- [x] Return replayed operation for identical replay and `409` for changed payload.
- [x] Return safe stock validation errors using problem-style fields.

### Task 3: RLS and immutability

**Files:**
- Modify: `backend/inventory/models.py`
- Create: `backend/inventory/migrations/0005_inventory_rls_and_constraints.py`
- Test: `backend/tests/test_inventory_security_closure.py`

- [x] Prevent deletion of locations with movement/balance history.
- [x] Prevent editing/deleting confirmed movements through model validation and API read-only shape.
- [x] Enable and force RLS on tenant-scoped inventory tables.
- [x] Add tests for cross-tenant and missing tenant context.

### Task 4: Documentation and acceptance

**Files:**
- Modify: `docs/PRD.md`
- Modify: `docs/10_Releases/SPRINT-003_Inventory_Final_Report.md`
- Create/modify: `docs/05_API/API-Inventory-Sprint-3.md`

- [x] Document endpoints, idempotency, and events.
- [x] Mark only validated Sprint 3 items as `[x]`.
- [x] Record commands, results, residual risks, and final status.
- [x] Commit with `feat: sprint 3 - estoque e movimentacoes`.
