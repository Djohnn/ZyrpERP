# Rollback Runbook

## When to Roll Back

Trigger automated or manual rollback when any of the following occurs:

| Trigger | Condition | Action |
|---------|-----------|--------|
| **Critical error** | 500 errors > 5% of requests in 5 min | Roll back backend deployment |
| **Data integrity** | Corruption detected or data loss confirmed | Restore from backup |
| **Fiscal systemic** | NFCe rejection rate > 50% in 10 min or all issuances failing | Disable fiscal integration, switch to manual |
| **PDV sync** | Offline queue not draining for > 2h after connectivity restored | Roll back PDV version |
| **Security** | Data leak suspected or confirmed (cross-tenant) | Isolate tenant, roll back deployment |
| **Business decision** | PO/Squad Lead decides after evaluating severity | Per decision |

## Pre-rollback Checklist

- [ ] Current state backed up (DB dump + config)
- [ ] Rollback target identified (last good deploy commit)
- [ ] Communication sent (see incident runbook)
- [ ] Maintenance window confirmed with stakeholders
- [ ] Database restore verified (if applicable)

## Backend Rollback

### Code Rollback

```powershell
# 1. Identify the last good commit
git log --oneline -20

# 2. Roll back to that commit
git checkout <last-good-commit> -- backend/
git commit -m "chore: rollback backend to <commit-hash>"

# 3. Revert database migrations (if schema change was part of the release)
#    Identify the last migration from the bad release
python manage.py migrate <app_name> <previous_migration>

# 4. Deploy the rolled-back version
```

### Database Rollback (if schema migration caused the issue)

```powershell
# 1. List migrations
python manage.py showmigrations

# 2. Roll back to a specific migration
python manage.py migrate <app_name> <migration_name>

# 3. Verify: python manage.py showmigrations
#    Target migration should be marked [X], later ones unmarked
```

### Full Database Restore (if data corruption)

```powershell
# Follow RUNBOOK_BACKUP_RESTORE.md
# 1. Backup current state
# 2. Drop and recreate database
# 3. Restore from last known good backup
# 4. Verify with restore_postgres_verify.ps1
```

## PDV Electron Rollback

```powershell
# 1. Identify the last good PDV build
git log --oneline -20 pdv/

# 2. Check out the previous version
git checkout <last-good-commit> -- pdv/

# 3. Rebuild
cd pdv
npm ci
npm run build

# 4. Deploy to store machines
#    (copy the build artifacts or installer)
```

## Post-rollback Verification

- [ ] `GET /health/` → 200
- [ ] `GET /readiness/` → ready
- [ ] Smoke test backend: `./infra/scripts/smoke_backend.ps1`
- [ ] Smoke test PDV: `./infra/scripts/smoke_pdv.ps1`
- [ ] Functional test: login → open cash → sale → close cash
- [ ] Fiscal: issue a test NFCe (mock or real)
- [ ] Support notified: rollback complete
- [ ] Postmortem ticket created (SEV-1/SEV-2)

## Lessons Learned

After each rollback:
1. What was the root cause?
2. Why wasn't it caught before deploy?
3. What test/gate can prevent recurrence?
4. How fast was the rollback? (target: < 30 min)
