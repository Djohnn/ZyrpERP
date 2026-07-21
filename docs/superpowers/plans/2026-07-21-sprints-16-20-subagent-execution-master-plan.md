# Sprints 16–20 Subagent-Driven Execution Master Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development for every implementation task. Option 1 is locked for the entire sequence; do not substitute superpowers:executing-plans.

**Goal:** Execute Sprints 16 through 20 without architecture prompts, using the committed specifications and implementation plans as the complete source of technical decisions.

**Execution order:** Sprint 16 → Sprint 17 → Sprint 18 → Sprint 19 → Sprint 20. Sprints must not run in parallel because each plan depends on the integrated result of the previous sprint.

---

## Locked operating rules

- Use a dedicated git worktree and the branch declared by each sprint plan; never implement directly on `master`.
- Before dispatching work, read the complete sprint plan once, extract every task with its full text and context, and create the execution checklist.
- Dispatch exactly one fresh implementation subagent at a time. Provide the full task text and relevant repository context; do not ask the subagent to discover or reinterpret the plan.
- Every implementation task follows TDD: RED, GREEN, REFACTOR, with deterministic tests at the cheapest sufficient pyramid level.
- After the implementer completes and self-reviews, dispatch a fresh specification-compliance reviewer. Any gap or extra scope returns to the implementer and must be re-reviewed until approved.
- Only after specification approval, dispatch a fresh code-quality reviewer. Any issue returns to the implementer and must be re-reviewed until approved.
- Do not advance while either review has open findings. After all tasks, run the complete sprint verification and dispatch a final reviewer for the whole implementation.
- Use `superpowers:finishing-a-development-branch` only after the final review and all required gates are green.
- Do not ask the user architecture questions. Resolve implementation details from the sprint spec, sprint plan, generated API contract, and existing repository conventions, in that order.
- Stop and request user direction only for missing external authority or credentials, unavailable required runtime, a reproducible failing baseline, or a direct contradiction that cannot be resolved from committed documentation.
- Never hide failures, skip gates, weaken assertions, or mark a checklist item complete without recorded verification evidence.

## Sprint queue

### 1. Sprint 16 — Frontend foundation and API contract

- Plan: `docs/superpowers/plans/2026-07-21-sprint-16-frontend-foundation-api-contract-implementation-plan.md`
- Branch: `feat/sprint-16-frontend-foundation`
- Entry gate: current `master` baseline is green and the Sprint 15 prerequisite is integrated.
- Exit gate: every plan task, test suite, review, documentation update, and final verification is green.

### 2. Sprint 17 — Admin shell, tenancy and access

- Plan: `docs/superpowers/plans/2026-07-21-sprint-17-admin-shell-tenancy-implementation-plan.md`
- Branch: `feat/sprint-17-admin-tenancy`
- Entry gate: Sprint 16 is integrated into `master` and green.
- Exit gate: every plan task, test suite, review, documentation update, and final verification is green.

### 3. Sprint 18 — Catalog, inventory and purchasing web

- Plan: `docs/superpowers/plans/2026-07-21-sprint-18-catalog-inventory-purchasing-web-implementation-plan.md`
- Branch: `feat/sprint-18-operations-web`
- Entry gate: Sprint 17 is integrated into `master` and green.
- Exit gate: every plan task, test suite, review, documentation update, and final verification is green.

### 4. Sprint 19 — PDV management, people and financial web

- Plan: `docs/superpowers/plans/2026-07-21-sprint-19-pdv-management-people-financial-implementation-plan.md`
- Branch: `feat/sprint-19-pdv-management-web`
- Entry gate: Sprint 18 is integrated into `master` and green.
- Exit gate: every plan task, test suite, review, documentation update, and final verification is green.

### 5. Sprint 20 — Fiscal, payments, observability and E2E acceptance

- Plan: `docs/superpowers/plans/2026-07-21-sprint-20-fiscal-payments-observability-e2e-implementation-plan.md`
- Branch: `feat/sprint-20-web-release`
- Entry gate: Sprint 19 is integrated into `master` and green.
- Exit gate: every plan task, full E2E acceptance, accessibility, security, bundle, review, and release-readiness gate is green.

## Per-task dispatch contract

For every task, the controller must provide the subagent with:

- the task's complete steps, acceptance criteria, file paths, commands, and expected outcomes;
- its place in the sprint and dependencies already completed;
- the locked architecture and repository conventions relevant to the task;
- explicit instruction to use `superpowers:test-driven-development`;
- the expected status response: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- a requirement to run the stated verification, self-review the diff, and commit only the task's scoped changes.

## Sequence completion ledger

- [ ] Sprint 16 completed, fully reviewed, green, and integrated.
- [ ] Sprint 17 completed, fully reviewed, green, and integrated.
- [ ] Sprint 18 completed, fully reviewed, green, and integrated.
- [ ] Sprint 19 completed, fully reviewed, green, and integrated.
- [ ] Sprint 20 completed, fully reviewed, green, and integrated.
- [ ] Final cross-sprint regression and release-readiness evidence recorded.

## Resume instruction

When an AI is told to continue this roadmap, it must locate the first unchecked sprint above, confirm its entry gate, open that sprint's implementation plan, and begin the Subagent-Driven workflow. It must not ask the user to choose an execution mode or architecture again.
