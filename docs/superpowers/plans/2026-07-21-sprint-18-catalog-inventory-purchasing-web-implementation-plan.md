# Sprint 18 Catalog Inventory and Purchasing Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver complete web journeys for catalog maintenance, inventory visibility/movements and purchasing through receipt.

**Architecture:** Use three isolated frontend feature folders (`catalog`, `inventory`, `purchasing`) connected only through typed IDs and shared primitives. Backend changes are limited to pagination/filter/schema gaps proven by API tests. Monetary and quantity values remain decimal strings end to end.

**Tech Stack:** Sprint 16–17 frontend stack, Django/DRF, PostgreSQL, Vitest, MSW, Playwright, axe-core.

---

## Execution protocol

Prerequisite: Sprints 16–17 are merged and green. Execute on `feat/sprint-18-operations-web`. The module boundaries, filters, decimal policy and idempotency behavior below are final; do not substitute client-side filtering or floating-point business arithmetic.

## Locked decisions

- Routes begin `/catalog`, `/inventory`, `/purchasing`.
- Lists use backend pagination and URL filters; no client-side full-dataset filtering.
- Decimal input uses strings with locale display at the edge; never JavaScript floating-point arithmetic for business totals.
- Mutations requiring `Idempotency-Key` generate UUID v4 once per user submission and preserve it across manual retry.

### Task 1: Verify and complete operational API contracts

**Files:**
- Modify: `backend/catalog/views.py`, `backend/catalog/serializers.py`, `backend/catalog/urls.py`
- Modify: `backend/inventory/views.py`, `backend/inventory/serializers.py`, `backend/inventory/urls.py`
- Modify: `backend/purchasing/views.py`, `backend/purchasing/serializers.py`, `backend/purchasing/urls.py`
- Create: `backend/tests/test_web_operations_api.py`

- [ ] Write BDD tests for pagination, search/filter, role denial, tenant/branch isolation, idempotency conflict shape and optimistic version conflict across catalog, balances, movements, suppliers, purchase orders and receipts.
- [ ] Run focused tests; expect RED only for documented contract gaps.
- [ ] Implement exact missing filters: product `q/category/active`, balance `branch/location/product`, movement `date_from/date_to/type`, purchase order `status/supplier/branch`, receipt `status/order`.
- [ ] Ensure every list schema includes stable IDs and display labels needed by selectors without leaking other tenants.
- [ ] Run focused tests and regenerate OpenAPI/types.
- [ ] Commit with `feat(api): complete catalog inventory purchasing web contracts`.

### Task 2: Catalog screens

**Files:**
- Create: `frontend/src/catalog/CategoriesPage.tsx`, `UnitsPage.tsx`, `ProductsPage.tsx`, `ProductDetailPage.tsx`
- Create: `frontend/src/catalog/ProductForm.tsx`, `PriceForm.tsx`, `catalogApi.ts`, `catalogSchemas.ts`
- Create: `frontend/src/catalog/catalogPages.test.tsx`

- [ ] Write tests for category/unit/product CRUD, search, codes, conversions, price periods, overlap conflict and validation.
- [ ] Run focused tests; expect RED.
- [ ] Implement routes and forms with semantic labels, decimal strings and URL filters.
- [ ] Surface fiscal-registration warnings without blocking non-fiscal edits.
- [ ] Run tests, typecheck and axe; expect PASS.
- [ ] Commit with `feat(frontend): add catalog management`.

### Task 3: Inventory visibility and movements

**Files:**
- Create: `frontend/src/inventory/BalancesPage.tsx`, `MovementsPage.tsx`, `LotsPage.tsx`
- Create: `frontend/src/inventory/ReceiptForm.tsx`, `TransferForm.tsx`, `AdjustmentForm.tsx`, `CountSessionPage.tsx`
- Create: `frontend/src/inventory/inventoryApi.ts`, `inventorySchemas.ts`, `inventoryPages.test.tsx`

- [ ] Write tests for balance filters, lot expiry, receipt, transfer, adjustment, count discrepancy, insufficient stock and duplicate idempotency.
- [ ] Run focused tests; expect RED.
- [ ] Implement read pages and operation forms. Require reason for adjustments and display source/destination for transfers.
- [ ] On success navigate to immutable operation detail and invalidate affected balances/movements only.
- [ ] Run focused tests and accessibility assertions; expect PASS.
- [ ] Commit with `feat(frontend): add inventory operations`.

### Task 4: Suppliers and purchase orders

**Files:**
- Create: `frontend/src/purchasing/SuppliersPage.tsx`, `SupplierForm.tsx`
- Create: `frontend/src/purchasing/PurchaseOrdersPage.tsx`, `PurchaseOrderEditor.tsx`, `PurchaseOrderDetailPage.tsx`
- Create: `frontend/src/purchasing/purchasingApi.ts`, `purchasingSchemas.ts`, `purchaseOrders.test.tsx`

- [ ] Write tests for supplier-person link, draft items, totals, approval, edit lock, recurring template and cancellation.
- [ ] Run focused tests; expect RED.
- [ ] Install `decimal.js@10`, then implement supplier and order workflows. Compute display previews exclusively with `Decimal`; treat backend totals as authoritative.
- [ ] Disable editing after approval and show compensating actions instead.
- [ ] Run tests and typecheck; expect PASS.
- [ ] Commit with `feat(frontend): add supplier and purchase order management`.

### Task 5: Receiving, returns and linked effects

**Files:**
- Create: `frontend/src/purchasing/PurchaseReceiptPage.tsx`, `SupplierReturnPage.tsx`, `RecurringTemplatesPage.tsx`
- Create: `frontend/src/purchasing/receiving.test.tsx`

- [ ] Write tests for partial/full receipt, over-receipt error, receipt cancellation, supplier return, payable link and fiscal reconciliation warnings.
- [ ] Run focused tests; expect RED.
- [ ] Implement receipt quantities against remaining ordered quantity; preserve idempotency key on retry.
- [ ] Display linked stock operation, payable and fiscal document IDs as navigable references.
- [ ] Run tests and axe checks; expect PASS.
- [ ] Commit with `feat(frontend): add purchasing receiving workflows`.

### Task 6: Vertical E2E and closure

**Files:**
- Create: `frontend/e2e/catalog-inventory-purchasing.spec.ts`
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-018_Catalog_Inventory_Purchasing_Web_Final_Report.md`

- [ ] Write independent E2E scenarios for product+price, stock receipt/transfer and purchase order→approval→partial/full receipt.
- [ ] Assert cross-tenant selectors never contain foreign records.
- [ ] Run all backend/frontend gates and three-browser E2E; capture raw output.
- [ ] Update Sprint 18 PRD and final report.
- [ ] Commit with `feat: sprint 18 - catalogo estoque compras web`.
