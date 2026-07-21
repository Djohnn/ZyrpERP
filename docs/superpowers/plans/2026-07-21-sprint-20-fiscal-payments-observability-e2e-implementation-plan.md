# Sprint 20 Fiscal Payments Observability and E2E Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the administrative web product with fiscal, payments and observability screens plus release-grade cross-browser acceptance tests.

**Architecture:** Add three final feature folders and a release acceptance suite. Secrets are write-only: configuration responses expose `configured: true` but never stored values. Observability endpoints return authorized aggregates only; correlation IDs connect UI failures to runbooks.

**Tech Stack:** Existing frontend/backend stack, Playwright Chromium/Firefox/WebKit, axe-core, JUnit/HTML reports.

---

## Execution protocol

Prerequisite: Sprints 16–19 are merged and green. Execute on `feat/sprint-20-web-release`. Provider fakes, polling, secret redaction, browser matrix and release gates are fixed decisions; no provider selection or architecture clarification is required.

## Locked decisions

- No real fiscal/payment provider is mandatory; existing fake/adapters remain behind contracts.
- Provider secret inputs are blank on edit and never repopulated.
- Metrics UI uses periodic refetch with visibility-aware pause; no WebSocket in this sprint.
- E2E uses deterministic test DB/seed and never production/shared environments.

### Task 1: Harden fiscal/payment/monitoring API contracts

**Files:**
- Modify: `backend/fiscal/serializers.py`, `backend/fiscal/views.py`, `backend/fiscal/urls.py`
- Modify: `backend/payments/serializers.py`, `backend/payments/views.py`
- Modify: `backend/monitoring/views.py`
- Create: `backend/tests/test_web_fiscal_payments_monitoring_api.py`

- [ ] Write BDD tests for fiscal configuration/status/retry/cancel/download authorization, payment config redaction/intents/transactions/batches, metrics authorization, secret absence and cross-tenant 404.
- [ ] Run focused tests; expect RED for missing safe management endpoints.
- [ ] Add explicit write-only secret serializers and `configured` booleans. Add bounded filters/pagination and aggregate metrics; never return raw credentials, webhook bodies, XML content in list endpoints or unrestricted logs.
- [ ] Standardize Problem Details for provider errors, divergence and unavailable dependencies.
- [ ] Regenerate OpenAPI/types and run tests.
- [ ] Commit with `feat(api): harden fiscal payments monitoring web contracts`.

### Task 2: Fiscal management

**Files:**
- Create: `frontend/src/fiscal/FiscalConfigPage.tsx`, `FiscalDocumentsPage.tsx`, `FiscalDocumentDetailPage.tsx`
- Create: `frontend/src/fiscal/PurchaseFiscalReconciliationPage.tsx`
- Create: `frontend/src/fiscal/fiscalApi.ts`, `fiscalPages.test.tsx`

- [ ] Write tests for write-only config, document filters/status, retry, cancel, authorized downloads, rejection detail and purchase reconciliation.
- [ ] Run focused tests; expect RED.
- [ ] Implement fiscal routes; secret/certificate fields clear after submit and are never represented in query cache responses.
- [ ] Require explicit confirmation for retry/cancel and show immutable audit/status timeline.
- [ ] Run tests and axe; expect PASS.
- [ ] Commit with `feat(frontend): add fiscal operations`.

### Task 3: Payment and reconciliation management

**Files:**
- Create: `frontend/src/payments/ProviderConfigPage.tsx`, `TransactionsPage.tsx`
- Create: `frontend/src/payments/ReconciliationBatchesPage.tsx`, `ReconciliationBatchDetailPage.tsx`
- Create: `frontend/src/payments/paymentsApi.ts`, `paymentPages.test.tsx`

- [ ] Write tests for write-only provider secret, transactions, CSV/JSON batch import validation, gross/fee/net display, divergence and confirmation.
- [ ] Run focused tests; expect RED.
- [ ] Implement pages with decimal strings, safe file-size/row limits and no raw webhook payload display.
- [ ] Prevent confirmation while any item is divergent; backend 409 remains authoritative.
- [ ] Run tests and accessibility checks; expect PASS.
- [ ] Commit with `feat(frontend): add payment reconciliation management`.

### Task 4: Operational observability

**Files:**
- Create: `frontend/src/monitoring/OperationsPage.tsx`, `MetricCard.tsx`, `RunbookLink.tsx`
- Create: `frontend/src/monitoring/monitoringApi.ts`, `operationsPage.test.tsx`

- [ ] Write tests for health/readiness, authorized metrics, dependency outage, visibility pause/resume, correlation ID and runbook links.
- [ ] Run focused tests; expect RED.
- [ ] Implement 30-second refetch only while `document.visibilityState === 'visible'`; stop polling on logout/tenant change.
- [ ] Display queues, Outbox, fiscal and webhook aggregates without customer payloads or credentials.
- [ ] Run tests and axe; expect PASS.
- [ ] Commit with `feat(frontend): add operational observability`.

### Task 5: Release-grade end-to-end suite

**Files:**
- Create: `frontend/e2e/release/01-auth-tenancy.spec.ts`
- Create: `frontend/e2e/release/02-catalog-purchasing.spec.ts`
- Create: `frontend/e2e/release/03-pdv-management.spec.ts`
- Create: `frontend/e2e/release/04-financial-fiscal-payments.spec.ts`
- Create: `frontend/e2e/release/05-security-resilience.spec.ts`
- Modify: `frontend/playwright.config.ts`, `.github/workflows/ci.yml`

- [ ] Make each scenario independent through API/DB fixtures and unique IDs; no ordered dependencies or hardcoded waits.
- [ ] Cover login/MFA/tenant, catalog→receipt, seeded PDV sale management, people/financial, fiscal/payment, role denial, cross-tenant, expired session and network recovery.
- [ ] Run Chromium, Firefox and WebKit with retries 0 locally/CI; fix every flaky selector or timing issue rather than enabling retries.
- [ ] Add JUnit and HTML reporters; upload reports/screenshots/traces only on failure.
- [ ] Run axe-core on one representative page per feature and fail on serious/critical violations.
- [ ] Commit with `test(frontend): add release acceptance suite`.

### Task 6: Performance, security and release closure

**Files:**
- Modify: `frontend/vite.config.ts`, `.github/workflows/ci.yml`
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-020_Fiscal_Payments_Observability_E2E_Final_Report.md`
- Create: `docs/10_Releases/WEB_ADMIN_RELEASE_READINESS.md`

- [ ] Enforce route-level lazy loading and a documented initial compressed JS budget of 250 KiB; fail CI when exceeded through a deterministic bundle report script.
- [ ] Run `npm audit --audit-level=high`, backend `pip-audit`, secret scanning, CSP/deploy checks and verify no source maps are publicly exposed in production config.
- [ ] Run backend full suite, frontend lint/typecheck/unit/build, three-browser E2E, accessibility and smoke tests. Record exact counts/durations and any accepted risks.
- [ ] Complete Sprint 20 and web-admin readiness checklists only when every required gate is green.
- [ ] Commit with `feat: sprint 20 - fiscal pagamentos observabilidade e2e web`.
