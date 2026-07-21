# Rollback Runbook

## Overview
This runbook defines when and how to rollback a deployment for the Zyrp platform.

## Rollback Triggers (MUST meet at least ONE)

| Trigger | Criteria | Example |
|---------|----------|---------|
| **Critical Bug** | Data loss, security breach, payment failure | Duplicate charges, data corruption |
| **Systemic Failure** | >5% error rate for >5 min, or core feature down | Sales API 500s, PDV offline |
| **Fiscal Failure** | NFC-e emission broken for >10 min | All fiscal docs REJECTED |
| **Sync Failure** | Outbox queue growing, data not syncing | Pending messages >10k |
| **Performance** | P95 latency >3x baseline for >10 min | P95 API >2s (baseline 300ms) |

## Rollback Authority
| Environment | Who Can Trigger | Approval |
|-------------|-----------------|----------|
| Staging | Any engineer | Self |
| Production | On-call engineer + TL | Engineering Lead |

## Pre-Rollback Checklist
- [ ] Confirm rollback trigger met
- [ ] Identify affected version/commit
- [ ] Verify previous version is stable (check logs/metrics)
- [ ] Notify on-call + team lead
- [ ] Open incident channel: `#incident-YYYYMMDD-rollback`

## Rollback Procedures

### Backend (Django) - Docker/Kubernetes
```bash
# 1. Check current deployment
kubectl get deployments -n zyrp

# 2. View rollout history
kubectl rollout history deployment/zyrp-backend -n zyrp

# 3. Rollback to previous revision
kubectl rollout undo deployment/zyrp-backend -n zyrp

# 4. Verify rollout
kubectl rollout status deployment/zyrp-backend -n zyrp

# 5. If specific revision needed
kubectl rollout undo deployment/zyrp-backend --to-revision=N -n zyrp
```

### Backend (Django) - Traditional Server
```bash
# 1. Stop current service
sudo systemctl stop zyrp-backend

# 2. Switch to previous release
cd /opt/zyrp/releases
ln -sfn release-YYYYMMDD-HHMMSS current

# 3. Run migrations (if rollback includes DB changes)
cd /opt/zyrp/current/backend
python manage.py migrate --fake-initial

# 4. Restart service
sudo systemctl start zyrp-backend

# 5. Verify health
curl -f http://localhost:8000/api/v1/monitoring/health/
```

### Database Rollback (DANGEROUS - LAST RESORT)
```bash
# ONLY if data corruption confirmed and no other fix
# 1. STOP ALL SERVICES
sudo systemctl stop zyrp-backend zyrp-worker zyrp-scheduler

# 2. Restore from backup
pg_restore -d zyrp -U postgres -h localhost backup_YYYYMMDD_HHMMSS.dump

# 3. Verify data integrity
psql -d zyrp -c "SELECT count(*) FROM sales_sale;"

# 4. Restart services
sudo systemctl start zyrp-backend zyrp-worker zyrp-scheduler
```

### PDV (Electron) Rollback
```bash
# 1. Check current version in auto-updater
# 2. Publish previous version as "latest" in auto-updater channel
# 3. PDVs will auto-update on next restart/check

# Or manual:
# 1. Download previous .exe from artifacts
# 2. Distribute via MDM or manual install
```

### Feature Flag Rollback (Preferred)
If feature flagged:
```bash
# Disable feature flag immediately
kubectl set env deployment/zyrp-backend FEATURE_NEW_CHECKOUT=false -n zyrp
# Or via admin panel
```

## Post-Rollback Verification

| Check | Command | Expected |
|-------|---------|----------|
| Health | `curl /api/v1/monitoring/health/` | `{"status":"healthy"}` |
| Readiness | `curl /api/v1/monitoring/ready/` | `{"status":"ready"}` |
| Sales API | `curl /api/v1/sales/counter/` | 200 OK |
| Fiscal | `curl /api/v1/fiscal/config/` | 200 OK |
| PDV Sync | Check device in admin | Online |
| Error Rate | Grafana / logs | <1% |

## Communication During Rollback

### Immediate (within 5 min)
```
🔄 ROLLBACK INITIATED: [Service] vX.Y.Z → vX.Y.Z-1
Trigger: [SEV-X] <description>
Commander: @username
ETA: <time>
Channel: #incident-YYYYMMDD-rollback
```

### On Completion
```
✅ ROLLBACK COMPLETE: [Service]
Duration: <time>
Previous Version: vX.Y.Z
Current Version: vX.Y.Z-1
Status: Verified healthy
```

### Post-Rollback (within 1 hour)
1. Root cause analysis
2. Create postmortem issue
3. Schedule fix + re-deploy
4. Update deployment checklist

## Rollback Decision Matrix

```
                    ┌─────────────────────────┐
                    │  Incident Detected      │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Is it SEV-1/2?         │
                    └───────────┬─────────────┘
                     YES /      \ NO
                      │          │
          ┌───────────▼─┐  ┌────▼────────────┐
          │  Can fix in │  │ Monitor + Fix   │
          │  <15 min?   │  │ in next deploy  │
          └──────┬──────┘  └─────────────────┘
           YES /  \ NO
              │    │
    ┌─────────▼─┐ ┌─▼─────────────────┐
    │ Hotfix +  │ │  ROLLBACK NOW     │
    │ Deploy    │ │ (Follow procedure)│
    └───────────┘ └───────────────────┘
```

## Database Migration Rollback Rules

| Scenario | Action |
|----------|--------|
| Additive migration (new table/column, no data loss) | Rollback code only, keep migration |
| Data migration (data transform) | Rollback code + create reverse migration |
| Destructive (drop column/table) | **DO NOT ROLLBACK CODE ALONE** - Restore DB from backup |
| Renamed column/table | Create reverse migration, then rollback |

## Testing Rollbacks
- Monthly: Test rollback in staging
- Quarterly: Full DR drill (backup → restore → verify)
- Document results in `/docs/10_Releases/ROLLBACK_TEST_RESULTS.md`

## Contacts

| Role | Name | Phone | Slack |
|------|------|-------|-------|
| On-Call Primary | - | - | @oncall |
| On-Call Secondary | - | - | @oncall-backup |
| Engineering Lead | - | - | @eng-lead |
| Database Admin | - | - | @dba |

## Revision History
| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-07-21 | 1.0 | - | Initial version |