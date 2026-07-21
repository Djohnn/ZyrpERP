# Sprint 17 Admin Shell and Tenancy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Option 1 is locked; do not switch to superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a production-ready administrative shell for companies, branches, memberships, invitations, MFA policies and PDV devices.

**Architecture:** Extend the Sprint 16 SPA with feature folders and route-level code splitting. Every list is server-paginated, filters are URL state, and every mutation uses the generated API client. Backend authorization remains authoritative; frontend capabilities only control affordances.

**Tech Stack:** Existing Sprint 16 stack, DRF, Vitest, Testing Library, MSW, Playwright, axe-core.

---

## Execution protocol

Prerequisite: Sprint 16 is merged and green. Execute on `feat/sprint-17-admin-tenancy`; follow the fixed routes, pagination contract and permission model below without requesting architectural choices. Match generated API names to the committed OpenAPI schema and regenerate types after backend changes.

## Locked decisions

- Routes: `/dashboard`, `/organization/companies`, `/organization/branches`, `/access/members`, `/access/invitations`, `/security/mfa`, `/devices`.
- Pagination contract: `count`, `next`, `previous`, `results`; default 25, max 100.
- Filters live in `URLSearchParams`; secrets and PII never do.
- Destructive/sensitive operations use accessible confirmation dialogs and require a fresh backend response.

### Task 1: Close tenancy API gaps

**Files:**
- Modify: `backend/config/settings/base.py`
- Modify: `backend/tenancy/serializers.py`, `backend/tenancy/serializers_access.py`
- Modify: `backend/tenancy/views.py`, `backend/tenancy/views_access.py`, `backend/tenancy/urls.py`
- Create: `backend/tests/test_web_admin_api.py`

- [ ] Write BDD API tests for paginated companies/branches/members/devices, branch CRUD, invitation status/filter, device revoke, role denial and cross-tenant 404.
- [ ] Run `python -m pytest tests/test_web_admin_api.py -q --no-cov`; expect RED for missing pagination/branch/device endpoints.
- [ ] Configure DRF `PageNumberPagination`, page size 25, max 100. Add branch list/create/detail and device list/revoke without changing registration/validation endpoints.
- [ ] Return Problem Details for conflicts and permissions; never serialize key hashes, MFA secrets or invitation digests.
- [ ] Run focused tests; expect PASS.
- [ ] Commit with `feat(tenancy): complete web administration API`.

### Task 2: Organization context and dashboard

**Files:**
- Create: `frontend/src/organization/OrganizationProvider.tsx`, `frontend/src/organization/organizationApi.ts`
- Create: `frontend/src/dashboard/DashboardPage.tsx`, `frontend/src/dashboard/DashboardPage.test.tsx`
- Modify: `frontend/src/layout/Navigation.tsx`, `frontend/src/app/App.tsx`

- [ ] Write tests for company/branch selection, invalid saved branch reset, tenant-switch reset and capability-aware dashboard cards.
- [ ] Run focused tests; expect RED.
- [ ] Implement organization context; persist branch UUID only after verifying it belongs to the active tenant/company.
- [ ] Add dashboard cards for authorized modules and backend readiness status; do not query operational totals yet.
- [ ] Run tests and typecheck; expect PASS.
- [ ] Commit with `feat(frontend): add organization context and dashboard`.

### Task 3: Companies and branches screens

**Files:**
- Create: `frontend/src/organization/CompaniesPage.tsx`, `CompanyForm.tsx`, `BranchesPage.tsx`, `BranchForm.tsx`
- Create: `frontend/src/organization/organizationSchemas.ts`, `organizationPages.test.tsx`

- [ ] Write MSW-backed tests for list/loading/empty, create, edit, validation, pagination, 409 conflict and cross-tenant 404.
- [ ] Run focused tests; expect RED.
- [ ] Implement typed queries/mutations and accessible forms. CNPJ/IE remain strings and are never converted to numbers.
- [ ] Invalidate only organization query keys after mutation; preserve current URL filters.
- [ ] Run tests and axe checks; expect PASS and no serious/critical violations.
- [ ] Commit with `feat(frontend): manage companies and branches`.

### Task 4: Memberships and invitations

**Files:**
- Create: `frontend/src/access/MembersPage.tsx`, `MemberRoleDialog.tsx`
- Create: `frontend/src/access/InvitationsPage.tsx`, `InvitationForm.tsx`
- Create: `frontend/src/access/accessSchemas.ts`, `accessPages.test.tsx`

- [ ] Write tests for filters, invite, resend, role update, deactivate, forbidden actions and validation mapping.
- [ ] Run focused tests; expect RED.
- [ ] Implement pages using role labels `admin`, `manager`, `operator`; require explicit branch scope and confirmation for access removal.
- [ ] Never show invitation token/digest. Show expiration and accepted state only.
- [ ] Run focused tests and typecheck; expect PASS.
- [ ] Commit with `feat(frontend): manage memberships and invitations`.

### Task 5: MFA policy and PDV devices

**Files:**
- Create: `frontend/src/security/MfaPolicyPage.tsx`
- Create: `frontend/src/devices/DevicesPage.tsx`, `DeviceRevokeDialog.tsx`
- Create: `frontend/src/security/securityPages.test.tsx`, `frontend/src/devices/devicesPage.test.tsx`

- [ ] Write tests for policy loading/update, prevention of disabling every MFA method, device filters/details/revoke and secret-field absence.
- [ ] Run focused tests; expect RED.
- [ ] Implement policy and device screens. Device key hashes and refresh secrets must be absent from TypeScript view models.
- [ ] Invalidate device queries after revoke and display audit correlation ID on conflict/error.
- [ ] Run tests and accessibility assertions; expect PASS.
- [ ] Commit with `feat(frontend): add security and device administration`.

### Task 6: Cross-browser acceptance and closure

**Files:**
- Create: `frontend/e2e/admin-tenancy.spec.ts`
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-017_Admin_Shell_Tenancy_Final_Report.md`

- [ ] Write independent Playwright scenarios for company, branch, invitation, role denial, MFA policy and device revoke.
- [ ] Run E2E in Chromium, Firefox and WebKit; expect all PASS without retries masking failures.
- [ ] Run backend full suite and all frontend gates; capture raw counts/durations.
- [ ] Mark Sprint 17 boxes complete and record evidence in the report.
- [ ] Commit with `feat: sprint 17 - painel administrativo tenancy`.
