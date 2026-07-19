# Incident Response Runbook

## Severity Matrix

| SEV | Criteria | Response Time | Communication |
|-----|----------|---------------|---------------|
| **SEV-1** | Data leak (cross-tenant), data loss, complete system unavailability, fiscal systemic failure | Immediate (24/7) | Executive + all-hands |
| **SEV-2** | Critical feature degraded (PDV offline > 1h, NFCe not issuing, sync broken), no acceptable workaround | < 30 min | Ops chat + Support lead |
| **SEV-3** | Limited impact with workaround (slow sync, single store issue, UI glitch) | Next business day | Support ticket |
| **SEV-4** | Minor defect, cosmetic issue, enhancement request | Backlog | Normal tracking |

## Incident Lifecycle

```text
DETECT → CLASSIFY → CONTAIN → COMMUNICATE → RECOVER → VALIDATE → POSTMORTEM
```

### 1. Detect

Sources:
- Health check alerts (monitoring)
- User/support report
- Automated smoke test failure
- Log spike / error rate increase

### 2. Classify

Answer:
- Which tenant/store is affected?
- Is data at risk (leak, loss, corruption)?
- Is fiscal issuance affected?
- Is PDV offline sync stuck?

→ Assign SEV level based on the matrix.

### 3. Contain

| Scenario | Containment Action |
|----------|-------------------|
| Data leak risk | Isolate tenant, disable API keys, revoke tokens |
| Fiscal failure | Switch store to manual receipt |  
| PDV sync issue | Enable full-online mode, disable offline queue |
| DB corruption | Failover to replica, block writes, backup current state |

### 4. Communicate

- SEV-1: Notify Product + Engineering + Support within 5 min
- SEV-2: Notify Ops chat + Support lead
- All: Update status page if external impact
- Template:

```text
[SEV-1] Subject: <brief description>
Tenant(s): <affected>
Impact: <what's broken / data at risk>
Action: <contained / investigating / resolved>
ETA: <or "TBD">
Commander: <name>
```

### 5. Recover

Follow the specific recovery procedure:
- **DB issue:** See [BACKUP_RESTORE](./RUNBOOK_BACKUP_RESTORE.md)
- **Fiscal:** Reattempt from admin panel or trigger `retry_fiscal_document` task
- **Sync:** Reset sync engine state from PDV admin panel
- **App bug:** Roll back deployment (see [ROLLBACK](./RUNBOOK_ROLLBACK.md))

### 6. Validate

Verify:
- `GET /health/` → 200
- `GET /readiness/` → outbox/fiscal within thresholds
- PDV login + sale flow completes
- Fiscal document issuable (mock or real)

### 7. Postmortem

Within 48h for SEV-1/SEV-2, next sprint for SEV-3/SEV-4.

Template:

```markdown
## Postmortem: <title>

Date: YYYY-MM-DD
Severity: SEV-<N>
Commander: <name>

### Summary
<2-3 sentence description>

### Timeline
- HH:MM — Detected via <source>
- HH:MM — Classified as SEV-<N>
- HH:MM — Containment action taken
- HH:MM — Recovery completed
- HH:MM — Validation passed
- HH:MM — Communicated resolution

### Root Cause
<what caused the incident>

### Impact
- Duration: <N> minutes
- Tenants affected: <N>
- Data loss: Yes/No (details)

### Action Items
- [ ] <owner>: <preventive action> (priority)
- [ ] <owner>: <detection improvement> (priority)

### Blame-free statement
The system failed, not the people. This postmortem exists to improve the system.
```

## Communication Templates

### Incident Open

> **SEV-<N>** — We are investigating an issue affecting <scope>. Impact: <summary>. Updates will be posted here. Commander: <name>.

### Incident Resolved

> **SEV-<N>** — The issue has been resolved. <cause and fix summary>. A postmortem will follow within 48h. If you experience any lingering effects, contact Support.
