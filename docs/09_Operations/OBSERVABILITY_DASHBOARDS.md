# Operational Dashboards

## API Health Dashboard

| Panel | Metric | Source | Threshold (pilot) |
|-------|--------|--------|-------------------|
| API uptime | /health/ → 200 | `config.views.health` | 0 | 99.5% (24h) |
| DB connectivity | services.database = ok | `config.views.health` | down → SEV-2 |
| Cache connectivity | services.cache = ok | `config.views.health` | down → SEV-3 |
| Response time p95 | middleware log | structured log | < 500ms |
| Correlation ID coverage | header present | all responses | 100% |

## Outbox Backlog Dashboard

| Panel | Metric | Source | Threshold (pilot) |
|-------|--------|--------|-------------------|
| Total pending | outbox_metrics().pending | `config.observability.outbox_metrics` | < 100 |
| Oldest pending age | now - oldest_pending_at | `config.observability.outbox_metrics` | < 5 min |
| Failed count | outbox_metrics().failed | `config.observability.outbox_metrics` | < 10 |
| Dead letter count | outbox_metrics().dead_letter | `config.observability.outbox_metrics` | 0 |
| Publish rate | total published / hour | log-based counter | N/A (baseline) |

## Fiscal Dashboard

| Panel | Metric | Source | Threshold (pilot) |
|-------|--------|--------|-------------------|
| Total documents today | fiscal_metrics().total | `config.observability.fiscal_metrics` | N/A |
| Pending issuance | fiscal_metrics().pending | `config.observability.fiscal_metrics` | < 5 |
| Rejection rate | rejected / total (24h) | `config.observability.fiscal_metrics` | < 10% |
| Technical errors | fiscal_metrics().failed | `config.observability.fiscal_metrics` | < 3 |
| Reattempts in flight | status=PROCESSING | `config.observability.fiscal_metrics` | < 5 |

## PDV Offline Queue Dashboard

| Panel | Metric | Source | Threshold (pilot) |
|-------|--------|--------|-------------------|
| Queued operations | SyncEngine queue size | `pdv/src/main/services/syncEngine.ts` | < 50 |
| Last sync timestamp | last successful sync | `pdv/src/main/services/connectivityMonitor.ts` | < 5 min |
| Pending conflict count | unresolved conflicts | `pdv/src/main/services/conflictResolver.ts` | 0 |
| Failed operations | retry_count > max | `pdv/src/main/services/operationJournal.ts` | < 5 |

## Alert Thresholds (Pilot Baselines)

These are **not** commercial SLOs. They will be adjusted after the pilot.

| Alert | Condition | Severity |
|-------|-----------|----------|
| DB down | health check fails 3 consecutive retries | SEV-1 |
| Outbox backlog > 100 | pending count > 100 for > 5 min | SEV-2 |
| Fiscal rejection spike | > 10% rejection rate in 1h | SEV-2 |
| PDV offline > 30 min | last sync > 30 min ago | SEV-3 |
| Fiscal technical error | failed count > 3 in 1h | SEV-3 |
| Correlation ID missing | any response without header | SEV-4 |

## How to View

- **Backend health:** `GET /health/` or `GET /api/v1/readiness/`
- **Outbox metrics:** via `system_metrics()` helper or readiness endpoint
- **Fiscal metrics:** via `system_metrics()` helper
- **PDV status:** Electron main process → `connectivityMonitor` → log/UI
- **Logs:** structured JSON logs in `./logs/` or journald
