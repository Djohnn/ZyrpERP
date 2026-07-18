# Sprint 15 SaaS Commercial Admin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add SaaS commercial administration for plans, subscriptions, entitlements, tenant lifecycle, support access and feature flags.

**Architecture:** Extend platform/tenancy concerns without coupling commercial ERP modules to billing details. ERP modules consume entitlements and tenant status through a small service boundary.

**Tech Stack:** Django, DRF, PostgreSQL, pytest-django, existing `tenancy`, `accounts`, `audit`, `outbox`.

---

### Task 1: Platform commercial models

**Files:**
- Create or Modify: `backend/platform/__init__.py`
- Create or Modify: `backend/platform/apps.py`
- Create or Modify: `backend/platform/models.py`
- Modify: `backend/config/settings/base.py`
- Create: `backend/tests/test_platform_commercial_models.py`

- [ ] Write failing tests for plan, subscription, entitlement and feature flag models.
- [ ] Create `Plan`, `Subscription`, `TenantEntitlement`, `FeatureFlag`, `PlatformAdminAudit` and `SupportAccessRequest`.
- [ ] Add unique constraints for plan code and tenant active subscription.
- [ ] Generate migrations.

### Task 2: Entitlement service

**Files:**
- Create or Modify: `backend/platform/services.py`
- Create: `backend/tests/test_platform_entitlements.py`

- [ ] Write failing tests for checking enabled capability and usage limit.
- [ ] Implement `tenant_has_capability()` and `tenant_limit_for()`.
- [ ] Add tenant suspension policy helpers.
- [ ] Ensure suspended tenant behavior is explicit and testable.

### Task 3: Feature flags and rollout

**Files:**
- Modify: `backend/platform/services.py`
- Create: `backend/tests/test_feature_flags.py`

- [ ] Write failing test for tenant-scoped feature flag override.
- [ ] Write failing test for global default fallback.
- [ ] Implement feature flag read/write service with audit.
- [ ] Emit Outbox event on flag changes.

### Task 4: Support access

**Files:**
- Modify: `backend/platform/models.py`
- Modify: `backend/platform/services.py`
- Create: `backend/tests/test_support_access.py`

- [ ] Write failing test for time-limited support access request.
- [ ] Write failing test blocking expired support access.
- [ ] Implement approval, expiration and revocation services.
- [ ] Audit support reason, approver, target tenant and expiration.

### Task 5: Admin API

**Files:**
- Create: `backend/platform/serializers.py`
- Create: `backend/platform/views.py`
- Create: `backend/platform/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_platform_admin_api.py`

- [ ] Write failing tests for plans, subscriptions, entitlements, feature flags and support access endpoints.
- [ ] Implement admin-only DRF endpoints.
- [ ] Return Problem Details for permission, suspension and idempotency conflicts.
- [ ] Add cross-tenant and non-admin negative tests.

### Task 6: Documentation and quality

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/00_Governance/SAAS_OPERATING_MODEL.md`
- Create: `docs/10_Releases/SPRINT-015_SaaS_Commercial_Admin_Final_Report.md`

- [ ] Update Sprint 15 checklist in PRD.
- [ ] Document plan, suspension, support access and feature flag governance.
- [ ] Run focused tests, full backend suite, Ruff, mypy, check and migration check.
- [ ] Record evidence in final report.
