# Sprint 14 AI Readiness Readonly Copilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare a safe read-only AI/copilot foundation with approved sources, redaction, authorization, audit and no transactional actions.

**Architecture:** Add an `ai_core` or `copilot` module that exposes query orchestration over approved documents/read models. Provider adapters stay swappable and no raw unrestricted database access is allowed.

**Tech Stack:** Django, DRF, PostgreSQL, pytest-django, optional future LangChain/LangGraph/RAG provider interfaces, existing audit/security docs.

---

### Task 1: AI governance and source registry

**Files:**
- Create: `docs/03_Domain/AI_GOVERNANCE.md`
- Create: `docs/03_Domain/AI_SOURCE_REGISTRY.md`
- Modify: `docs/08_Security/DATA_CLASSIFICATION.md`

- [ ] Document allowed source classes: docs, runbooks, approved read models and aggregate metrics.
- [ ] Document forbidden source classes: secrets, certificates, tokens, raw fiscal payloads and unrestricted SQL.
- [ ] Define read-only policy and human approval requirement for future actions.
- [ ] Record data classification and retention rules for AI interactions.

### Task 2: Copilot app and models

**Files:**
- Create: `backend/copilot/__init__.py`
- Create: `backend/copilot/apps.py`
- Create: `backend/copilot/models.py`
- Modify: `backend/config/settings/base.py`
- Create: `backend/tests/test_copilot_models.py`

- [ ] Write failing tests for source registry, query audit and feedback records.
- [ ] Create `CopilotSource`, `CopilotQuery`, `CopilotCitation` and `CopilotFeedback`.
- [ ] Add tenant scope where a source or query is tenant-specific.
- [ ] Generate migrations.

### Task 3: Redaction and authorization

**Files:**
- Create: `backend/copilot/redaction.py`
- Create: `backend/copilot/permissions.py`
- Create: `backend/tests/test_copilot_redaction.py`

- [ ] Write failing tests proving tokens, certificate-like values and sensitive fields are redacted.
- [ ] Implement deterministic redaction helpers.
- [ ] Add permission checks for tenant-scoped read models.
- [ ] Ensure audit records do not store raw restricted data.

### Task 4: Query orchestration

**Files:**
- Create: `backend/copilot/services.py`
- Create: `backend/copilot/providers/base.py`
- Create: `backend/copilot/providers/fake.py`
- Create: `backend/tests/test_copilot_services.py`

- [ ] Write failing test for documentation query returning answer with citation.
- [ ] Write failing test blocking cross-tenant operational query.
- [ ] Implement fake provider for deterministic tests.
- [ ] Implement source retrieval from approved documents/read models only.
- [ ] Persist query audit and citations.

### Task 5: API

**Files:**
- Create: `backend/copilot/serializers.py`
- Create: `backend/copilot/views.py`
- Create: `backend/copilot/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_copilot_api.py`

- [ ] Write failing API tests for query, source list, audit list and feedback.
- [ ] Implement endpoints with tenant and role checks.
- [ ] Return Problem Details for forbidden source or missing permission.
- [ ] Add rate limit or throttle class if existing project pattern supports it.

### Task 6: Documentation and quality

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-014_AI_Readiness_Readonly_Copilot_Final_Report.md`

- [ ] Update Sprint 14 checklist in PRD.
- [ ] Document explicitly that no AI action writes to sales, fiscal, stock or finance.
- [ ] Run focused tests, full backend suite, Ruff, mypy, check and migration check.
- [ ] Record evidence in final report.
