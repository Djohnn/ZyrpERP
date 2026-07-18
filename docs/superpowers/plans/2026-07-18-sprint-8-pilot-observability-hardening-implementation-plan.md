# Sprint 8 Pilot Observability Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare a pilot-ready release candidate with measurable observability, restore evidence, smoke tests, runbooks, security checks and rollback criteria.

**Architecture:** Harden the existing Django backend, PDV Electron and infrastructure scripts without adding new commercial features. Use versioned scripts, docs and tests so every pilot gate can be reproduced.

**Tech Stack:** Django, DRF, PostgreSQL, Redis, Celery/Outbox, Electron/Vitest/Playwright, PowerShell-compatible scripts, Markdown runbooks.

---

### Task 1: Pilot readiness checklist

**Files:**
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-008_Pilot_Observability_Hardening_Final_Report.md`
- Create: `docs/09_Operations/PILOT_READINESS_CHECKLIST.md`

- [ ] Write the Sprint 8 checklist in `docs/PRD.md`.
- [ ] Create a pilot readiness checklist covering tenant setup, users, catalog, inventory, sales, PDV, fiscal, backup, restore, support and rollback.
- [ ] Add explicit sign-off boxes for Product, Engineering and Support.
- [ ] Verify there is no unfinished text in `docs/09_Operations/PILOT_READINESS_CHECKLIST.md` before marking the checklist complete.

### Task 2: Health, readiness and smoke tests

**Files:**
- Modify: `backend/config/views.py`
- Create: `backend/tests/test_readiness.py`
- Create: `infra/scripts/smoke_backend.ps1`
- Create: `infra/scripts/smoke_pdv.ps1`

- [ ] Write failing tests for readiness responses covering database, Redis/cache and Outbox backlog metadata.
- [ ] Extend health/readiness output without exposing secrets.
- [ ] Add backend smoke script for `/health/`, auth page/API readiness and correlation ID.
- [ ] Add PDV smoke script for install/build status and critical renderer route.
- [ ] Run focused tests and scripts.

### Task 3: Operational metrics and dashboards

**Files:**
- Modify: `backend/outbox/services.py`
- Create: `backend/config/observability.py`
- Create: `backend/tests/test_operational_metrics.py`
- Create: `docs/09_Operations/OBSERVABILITY_DASHBOARDS.md`

- [ ] Write failing tests for Outbox age/backlog summary.
- [ ] Implement helper functions that return safe metric dictionaries.
- [ ] Document dashboard panels: API latency/errors, Outbox backlog, fiscal pending/rejected/error, PDV offline queue, DB/Redis health.
- [ ] Document alert thresholds as pilot baselines, not final commercial SLOs.

### Task 4: Backup and restore proof

**Files:**
- Create: `infra/scripts/backup_postgres.ps1`
- Create: `infra/scripts/restore_postgres_verify.ps1`
- Create: `docs/09_Operations/RUNBOOK_BACKUP_RESTORE.md`

- [ ] Create backup script using environment variables and no embedded credentials.
- [ ] Create restore verification script that restores into a disposable database name.
- [ ] Document restore steps, expected output and rollback decision.
- [ ] Run scripts in a safe local/staging environment and record evidence in the final report.

### Task 5: Incident response and rollback

**Files:**
- Create: `docs/09_Operations/RUNBOOK_INCIDENT_RESPONSE.md`
- Create: `docs/09_Operations/RUNBOOK_ROLLBACK.md`
- Modify: `docs/10_Releases/SPRINT-008_Pilot_Observability_Hardening_Final_Report.md`

- [ ] Define SEV-1 to SEV-4 with examples for fiscal, offline sync, data isolation, payment/cash and database incidents.
- [ ] Define rollback triggers and operator communication templates.
- [ ] Include postmortem template without blame.
- [ ] Record commands and evidence in the Sprint 8 final report.

### Task 6: Quality gate

**Files:**
- Modify: `docs/PRD.md`

- [ ] Run backend focused tests for readiness/metrics.
- [ ] Run existing backend full suite.
- [ ] Run PDV/frontend tests available in the current branch.
- [ ] Run Ruff, mypy, Django check and migration check.
- [ ] Run secret grep/detect-secrets baseline review.
- [ ] Mark PRD Sprint 8 boxes only after evidence is captured.
