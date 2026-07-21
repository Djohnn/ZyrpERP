# Sprint 19 PDV Management People and Financial Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Option 1 is locked; do not switch to superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let managers supervise Electron PDV sales and cash sessions, manage people, and trace financial effects without implementing a second point of sale.

**Architecture:** The web application is read/management oriented for PDV-originated operations. Confirmed sales remain immutable; returns, cancellations and refunds call compensating backend actions. Feature folders are `salesManagement`, `people` and `financial`.

**Tech Stack:** Existing frontend stack, Django/DRF, Vitest, MSW, Playwright, axe-core.

---

## Execution protocol

Prerequisite: Sprints 16–18 are merged and green. Execute on `feat/sprint-19-pdv-management-web`. The management-only boundary is final; never ask whether to add a web checkout or reuse Electron runtime code.

## Non-negotiable boundary

Do not add product scanning, cart, checkout, payment capture, receipt printing or offline sale routes to `frontend/`. Those remain in `pdv/`. A test must assert the web navigation exposes no “new sale” action.

### Task 1: Management API gaps and exports

**Files:**
- Modify: `backend/sales/views.py`, `backend/sales/serializers.py`
- Modify: `backend/financial/views.py`, `backend/financial/urls.py`
- Create: `backend/tests/test_web_sales_financial_api.py`

- [ ] Write BDD tests for paginated sale/cash lists, filters (`date`, `branch`, `operator`, `device`, `customer`, `status`), detailed linked effects, bounded CSV export, people/financial filters, role denial and cross-tenant 404.
- [ ] Run focused tests; expect RED for contract gaps.
- [ ] Add only missing read endpoints/fields and bounded export with maximum 1000 rows. Never expose secret, full restricted PII without permission, or mutable sale fields.
- [ ] Regenerate OpenAPI/types and run focused tests.
- [ ] Commit with `feat(api): add PDV management and financial web contracts`.

### Task 2: Sales and cash management

**Files:**
- Create: `frontend/src/salesManagement/SalesPage.tsx`, `SaleDetailPage.tsx`
- Create: `frontend/src/salesManagement/CashSessionsPage.tsx`, `CashSessionDetailPage.tsx`
- Create: `frontend/src/salesManagement/salesManagementApi.ts`, `salesManagement.test.tsx`

- [ ] Write tests for filters, pagination, sale item/payment/operator/device detail, cash movements, closing difference and absence of create-sale affordance.
- [ ] Run focused tests; expect RED.
- [ ] Implement management-only routes `/sales` and `/cash-sessions` with immutable detail views.
- [ ] Link sale to stock, fiscal and financial IDs; show correlation ID on failures.
- [ ] Run tests and axe; expect PASS.
- [ ] Commit with `feat(frontend): add PDV sales and cash supervision`.

### Task 3: Compensating actions

**Files:**
- Create: `frontend/src/salesManagement/ReturnDialog.tsx`, `CancellationDialog.tsx`, `RefundDialog.tsx`
- Create: `frontend/src/salesManagement/compensations.test.tsx`

- [ ] Write tests for quantity limits, mandatory reason, MFA/permission denial, idempotency replay, already-cancelled conflict and immutable original sale.
- [ ] Run focused tests; expect RED.
- [ ] Implement dialogs with explicit consequence summaries and UUID idempotency key preserved across retry.
- [ ] Refresh sale, stock, fiscal and financial queries after success; never optimistically mutate confirmed sale data.
- [ ] Run tests; expect PASS.
- [ ] Commit with `feat(frontend): manage sale compensations`.

### Task 4: People management with PII controls

**Files:**
- Create: `frontend/src/people/PeoplePage.tsx`, `PersonDetailPage.tsx`, `PersonForm.tsx`
- Create: `frontend/src/people/AddressesSection.tsx`, `ContactsSection.tsx`, `ConsentsSection.tsx`
- Create: `frontend/src/people/peopleApi.ts`, `peopleSchemas.ts`, `peoplePages.test.tsx`

- [ ] Write tests for PF/PJ, roles, normalized documents, addresses, contacts, consents, deactivation, masking and cross-tenant 404.
- [ ] Run focused tests; expect RED.
- [ ] Implement forms without placing document/contact/address values in URL or telemetry. Mask Restricted fields for roles lacking permission.
- [ ] Require confirmation for deactivation and consent revocation; retain history views.
- [ ] Run tests and axe; expect PASS.
- [ ] Commit with `feat(frontend): add secure people management`.

### Task 5: Financial operations and reports

**Files:**
- Create: `frontend/src/financial/ReceivablesPage.tsx`, `PayablesPage.tsx`, `CashflowPage.tsx`
- Create: `frontend/src/financial/SettlementDialog.tsx`, `ReportsPage.tsx`
- Create: `frontend/src/financial/financialApi.ts`, `financialPages.test.tsx`

- [ ] Write tests for status/period/account/branch filters, partial/full settlement, over-settlement conflict, immutable settlement, projection and bounded export.
- [ ] Run focused tests; expect RED.
- [ ] Implement pages using decimal strings and backend-calculated totals. Link every obligation/entry to its source operation when present.
- [ ] Require MFA/confirmation according to backend permission responses; do not duplicate permission rules client-side.
- [ ] Run tests and accessibility assertions; expect PASS.
- [ ] Commit with `feat(frontend): add financial management and reports`.

### Task 6: PDV-to-web E2E and closure

**Files:**
- Create: `frontend/e2e/pdv-management-financial.spec.ts`
- Modify: `backend/tenancy/management/commands/seed_e2e.py`
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-019_PDV_Management_People_Financial_Final_Report.md`

- [ ] Extend deterministic seed with a PDV device, closed/open cash sessions, identified/anonymous sales and linked effects.
- [ ] Write E2E scenarios to find seeded PDV sale, inspect links, execute authorized return, inspect cash difference, manage person and settle obligation.
- [ ] Add an assertion that no web route/menu/button starts a sale.
- [ ] Run full backend/frontend/E2E gates; capture output.
- [ ] Update PRD/report and commit with `feat: sprint 19 - gestao pdv pessoas financeiro web`.
