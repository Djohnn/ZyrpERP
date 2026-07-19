# Sprint 11 Financial Cashflow Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate operational finance and reports for payables, receivables, settlements, cashflow and management views.

**Architecture:** Add or consolidate `financial` with immutable ledger-like records and read models. Reports query tenant-scoped projections and expose bounded exports.

**Tech Stack:** Django, DRF, PostgreSQL, pytest-django, existing `sales`, `purchasing`, `inventory`, `fiscal`, `audit`, `outbox`.

---

### Task 1: Financial core models

**Files:**
- Create or Modify: `backend/financial/__init__.py`
- Create or Modify: `backend/financial/apps.py`
- Create or Modify: `backend/financial/models.py`
- Modify: `backend/config/settings/base.py`
- Create: `backend/tests/test_financial_models.py`

- [ ] Write failing tests for `FinancialAccount`, `Receivable`, `Payable`, `Settlement` and `CashflowEntry`.
- [ ] Create models with tenant scope, status fields, due dates and immutable confirmed states.
- [ ] Add constraints for positive amounts and unique idempotency.
- [ ] Generate migrations.

### Task 2: Receivables and settlements from sales

**Files:**
- Create or Modify: `backend/financial/services.py`
- Modify: `backend/sales/services.py`
- Create: `backend/tests/test_financial_sales_integration.py`

- [ ] Write failing test proving sale payment creates realized or expected receivable according to method.
- [ ] Implement `record_sale_financial_effects()`.
- [ ] Separate cash immediate, Pix immediate/near-immediate and card external expected settlement.
- [ ] Emit audit and Outbox events.

### Task 3: Payables and settlement workflow

**Files:**
- Modify: `backend/financial/services.py`
- Create: `backend/tests/test_financial_payables_services.py`

- [ ] Write failing test for settling payable partially.
- [ ] Write failing test blocking over-settlement.
- [ ] Implement `settle_payable()` and `settle_receivable()`.
- [ ] Create compensating adjustment instead of editing confirmed settlement.

### Task 4: Cashflow projections

**Files:**
- Modify: `backend/financial/services.py`
- Create: `backend/tests/test_cashflow_projection.py`

- [ ] Write failing test for realized and forecast cashflow by period.
- [ ] Implement query/service for tenant, branch and date range.
- [ ] Include sales, purchase payables and settlements.
- [ ] Ensure timezone and Decimal behavior are explicit.

### Task 5: Reporting API

**Files:**
- Create: `backend/financial/serializers.py`
- Create: `backend/financial/views.py`
- Create: `backend/financial/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_reporting_api.py`

- [ ] Write failing tests for sales, cash closing, inventory, payables/receivables and cashflow reports.
- [ ] Implement read-only endpoints with pagination/filters.
- [ ] Add bounded export option with row limits.
- [ ] Add cross-tenant negative tests for every report.

### Task 6: AI-readiness without AI execution

**Files:**
- Create: `docs/03_Domain/AI_READINESS_READ_MODELS.md`
- Modify: `docs/08_Security/DATA_CLASSIFICATION.md`

- [ ] Document approved read models for future RAG/copilot.
- [ ] Mark financial and fiscal fields that must not be sent to AI.
- [ ] Define that future AI is read-only until explicit approval workflow exists.

### Task 7: Documentation and quality

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-011_Financial_Cashflow_Reporting_Final_Report.md`

- [ ] Update Sprint 11 checklist in PRD.
- [ ] Record report definitions and calculation rules.
- [ ] Run focused tests, full backend suite, Ruff, mypy, check and migration check.
