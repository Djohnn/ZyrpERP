# Sprint 12 People Customers Partners Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement tenant-scoped people, customers, partners, addresses, contacts and consent records for sales, fiscal, purchasing and finance.

**Architecture:** Add a focused `people` bounded module. Other modules reference `Person` through foreign keys or service lookups, while sensitive personal data remains tenant-scoped, audited and redacted from logs/events.

**Tech Stack:** Django, DRF, PostgreSQL, pytest-django, existing `tenancy`, `sales`, `purchasing`, `fiscal`, `audit`, `outbox`.

---

### Task 1: People app and core models

**Files:**
- Create: `backend/people/__init__.py`
- Create: `backend/people/apps.py`
- Create: `backend/people/models.py`
- Modify: `backend/config/settings/base.py`
- Create: `backend/tests/test_people_models.py`

- [ ] Write failing tests for PF/PJ person creation and tenant-scoped document uniqueness.
- [ ] Create `Person`, `PersonRole`, `PersonDocument`, `PersonAddress`, `PersonContact` and `ConsentRecord`.
- [ ] Add constraints for active document uniqueness per tenant.
- [ ] Normalize document, e-mail and phone values in model/service layer.
- [ ] Generate migrations.

### Task 2: Services and audit

**Files:**
- Create: `backend/people/services.py`
- Create: `backend/tests/test_people_services.py`

- [ ] Write failing test for creating a customer with fiscal address.
- [ ] Write failing test for deactivating a person without deleting history.
- [ ] Implement `create_person()` and `deactivate_person()`.
- [ ] Emit audit and Outbox events for creation, update and deactivation.
- [ ] Ensure sensitive values are not emitted raw in event payloads.

### Task 3: API

**Files:**
- Create: `backend/people/serializers.py`
- Create: `backend/people/views.py`
- Create: `backend/people/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_people_api.py`

- [ ] Write failing API tests for CRUD, deactivate, addresses, contacts and consents.
- [ ] Implement DRF viewsets and nested endpoints.
- [ ] Add filtering by role, document and active status.
- [ ] Add cross-tenant negative tests.

### Task 4: Sales, purchasing and fiscal references

**Files:**
- Modify: `backend/sales/models.py`
- Modify: `backend/sales/serializers.py`
- Modify: `backend/purchasing/models.py`
- Modify: `backend/fiscal/services.py`
- Create: `backend/tests/test_people_integrations.py`

- [ ] Write failing test for sale with identified customer.
- [ ] Write failing test for supplier linked to `Person`.
- [ ] Write failing test for fiscal recipient data loaded from `Person`.
- [ ] Implement optional references without breaking anonymous counter sales.

### Task 5: Documentation and quality

**Files:**
- Modify: `docs/PRD.md`
- Modify: `docs/08_Security/DATA_CLASSIFICATION.md`
- Create: `docs/10_Releases/SPRINT-012_People_Customers_Partners_Final_Report.md`

- [ ] Update Sprint 12 checklist in PRD.
- [ ] Document personal-data classification and redaction rules.
- [ ] Run focused tests, full backend suite, Ruff, mypy, check and migration check.
- [ ] Record evidence in the final report.
