# Sprint 10 Purchasing Receiving Payables Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement purchase orders, partial receiving, inventory entry and generated payables for the MVP replenishment workflow.

**Architecture:** Add `purchasing` as a bounded module that depends on catalog, inventory and financial/payables through service calls and domain events.

**Tech Stack:** Django, DRF, PostgreSQL, pytest-django, existing `catalog`, `inventory`, `audit`, `outbox`.

---

### Task 1: Supplier and purchase order models

**Files:**
- Create: `backend/purchasing/__init__.py`
- Create: `backend/purchasing/apps.py`
- Create: `backend/purchasing/models.py`
- Modify: `backend/config/settings/base.py`
- Create: `backend/tests/test_purchasing_models.py`

- [ ] Write failing tests for supplier tenant isolation and purchase order totals.
- [ ] Create `Supplier`, `PurchaseOrder` and `PurchaseOrderItem`.
- [ ] Add statuses `draft`, `approved`, `partially_received`, `received`, `cancelled`.
- [ ] Add positive quantity/cost constraints.
- [ ] Generate migrations.

### Task 2: Approval and immutability

**Files:**
- Create: `backend/purchasing/services.py`
- Create: `backend/tests/test_purchasing_services.py`

- [ ] Write failing test for approving a draft purchase order.
- [ ] Write failing test blocking item edits after approval.
- [ ] Implement `approve_purchase_order()`.
- [ ] Emit audit and Outbox event `purchasing.order.approved`.

### Task 3: Receiving and inventory entry

**Files:**
- Modify: `backend/purchasing/models.py`
- Modify: `backend/purchasing/services.py`
- Create: `backend/tests/test_purchase_receiving_services.py`

- [ ] Write failing test for partial receipt increasing stock.
- [ ] Write failing test blocking receipt above pending quantity.
- [ ] Add `PurchaseReceipt` and `PurchaseReceiptItem`.
- [ ] Implement `receive_purchase_order()` using `inventory.services.create_receipt`.
- [ ] Ensure idempotent replay does not duplicate stock.

### Task 4: Payables

**Files:**
- Create or Modify: `backend/financial/models.py`
- Create or Modify: `backend/financial/services.py`
- Create: `backend/tests/test_purchase_payables.py`

- [ ] Write failing test proving confirmed receipt creates payable.
- [ ] Add minimal `Payable` model if financial module does not exist.
- [ ] Implement payable generation tied to receipt total.
- [ ] Ensure payable is tenant scoped and immutable after confirmation.

### Task 5: API

**Files:**
- Create: `backend/purchasing/serializers.py`
- Create: `backend/purchasing/views.py`
- Create: `backend/purchasing/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_purchasing_api.py`

- [ ] Write failing tests for supplier CRUD, order create/approve and receipt.
- [ ] Implement DRF endpoints with tenant filtering.
- [ ] Add Problem Details for invalid status, over-receipt and idempotency conflict.
- [ ] Add cross-tenant negative tests.

### Task 6: Documentation and quality

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-010_Purchasing_Receiving_Payables_Final_Report.md`

- [ ] Update Sprint 10 checklist in PRD.
- [ ] Record what is out of scope: RFQ, fiscal entry, bank integration and costing advanced rules.
- [ ] Run focused tests, full backend suite, Ruff, mypy, check and migration check.
