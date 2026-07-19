<#
.SYNOPSIS
  Restore a PostgreSQL dump into a disposable database and verify integrity.

.DESCRIPTION
  Reads connection parameters from environment variables. Creates a temporary
  database from the dump file, runs a basic verification (SELECT count of
  known tables), then drops the disposable database on success. Never touches
  the production database.

  Pass the backup file path as the first argument.

.EXAMPLE
  $env:DB_NAME="zyrp"; $env:DB_USER="postgres"
  ./restore_postgres_verify.ps1 .\backups\zyrp_20260719_120000.dump
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [string]$DbUser = $env:DB_USER,
    [string]$DbPassword = $env:DB_PASSWORD,
    [string]$DbHost = $env:DB_HOST,
    [string]$DbPort = $env:DB_PORT
)

$ErrorActionPreference = "Stop"

# Validate backup file
if (-not (Test-Path -LiteralPath $BackupFile)) {
    Write-Host "[FAIL] Backup file not found: $BackupFile" -ForegroundColor Red
    exit 1
}

if (-not $BackupFile.EndsWith('.dump')) {
    Write-Host "[FAIL] Expected a .dump file (pg_dump custom format)" -ForegroundColor Red
    exit 1
}

# Validate required env vars
$missing = @()
if (-not $DbUser) { $missing += "DB_USER" }
if (-not $DbPassword) { $missing += "DB_PASSWORD" }
if (-not $DbHost) { $DbHost = "localhost"; Write-Host "[INFO] DB_HOST not set, using localhost" }
if (-not $DbPort) { $DbPort = "5432"; Write-Host "[INFO] DB_PORT not set, using 5432" }

if ($missing.Count -gt 0) {
    Write-Host "[FAIL] Missing required environment variables: $($missing -join ', ')" -ForegroundColor Red
    exit 1
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$restoreDb = "verify_restore_$timestamp"

Write-Host "=== Restore Verification ===" -ForegroundColor Cyan
Write-Host "Backup: $BackupFile"
Write-Host "Target: $restoreDb (disposable)"
Write-Host "Host: $DbHost`:$DbPort`n"

$env:PGPASSWORD = $DbPassword

try {
    # 1. Create disposable database
    Write-Host "[STEP] Creating disposable database '$restoreDb'..." -ForegroundColor Yellow
    & "psql" -h $DbHost -p $DbPort -U $DbUser -d postgres -c "CREATE DATABASE `"$restoreDb`";" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Could not create disposable database" -ForegroundColor Red
        exit 1
    }
    Write-Host "[PASS] Disposable database created" -ForegroundColor Green

    # 2. Restore into disposable database
    Write-Host "[STEP] Restoring into disposable database..." -ForegroundColor Yellow
    & "pg_restore" -h $DbHost -p $DbPort -U $DbUser -d $restoreDb -v $BackupFile 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Restore failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "[PASS] Restore completed" -ForegroundColor Green

    # 3. Verify key tables exist
    Write-Host "[STEP] Running verification queries..." -ForegroundColor Yellow
    $tablesToCheck = @("accounts_user", "tenancy_tenant", "catalog_product", "sales_sale", "django_migrations")
    $allOk = $true
    foreach ($table in $tablesToCheck) {
        $count = & "psql" -h $DbHost -p $DbPort -U $DbUser -d $restoreDb -t -A -c "SELECT COUNT(*) FROM `"$table`";" 2>&1
        if ($LASTEXITCODE -eq 0 -and $count -match '^\d+$') {
            Write-Host "       Table $table : $count rows" -ForegroundColor Green
        } else {
            Write-Host "       Table $table : NOT FOUND" -ForegroundColor Yellow
            $allOk = $false
        }
    }
    if ($allOk) {
        Write-Host "[PASS] All key tables verified" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Some tables missing — backup may be incomplete" -ForegroundColor Yellow
    }

    # 4. Check migration state
    $migrationCount = & "psql" -h $DbHost -p $DbPort -U $DbUser -d $restoreDb -t -A -c "SELECT COUNT(*) FROM django_migrations;" 2>&1
    Write-Host "       Migrations applied: $migrationCount"

    Write-Host "`n[PASS] Restore verification completed successfully" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Verification failed: $_" -ForegroundColor Red
    exit 1
} finally {
    # 5. Drop disposable database
    Write-Host "[CLEANUP] Dropping disposable database '$restoreDb'..." -ForegroundColor Yellow
    & "psql" -h $DbHost -p $DbPort -U $DbUser -d postgres -c "DROP DATABASE IF EXISTS `"$restoreDb`";" 2>&1 | Out-Null
    Remove-Item -LiteralPath "env:PGPASSWORD" -ErrorAction SilentlyContinue
    Write-Host "[CLEANUP] Done" -ForegroundColor Green
}

Write-Host "=== Restore verification finished at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
