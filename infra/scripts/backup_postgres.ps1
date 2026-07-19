<#
.SYNOPSIS
  Backup PostgreSQL database to a compressed dump file.

.DESCRIPTION
  Reads connection parameters from environment variables (DB_NAME, DB_USER,
  DB_PASSWORD, DB_HOST, DB_PORT). Writes a timestamped .dump file to
  BACKUP_DIR (default: ./backups). No secrets are embedded in this script.

.EXAMPLE
  $env:DB_NAME="zyrp"; $env:DB_USER="postgres"
  ./backup_postgres.ps1
#>

param(
    [string]$BackupDir = (Join-Path -Path (Get-Location) -ChildPath "backups"),
    [string]$DbName = $env:DB_NAME,
    [string]$DbUser = $env:DB_USER,
    [string]$DbPassword = $env:DB_PASSWORD,
    [string]$DbHost = $env:DB_HOST,
    [string]$DbPort = $env:DB_PORT,
    [int]$RetentionDays = 30
)

$ErrorActionPreference = "Stop"

# Validate required env vars
$missing = @()
if (-not $DbName) { $missing += "DB_NAME" }
if (-not $DbUser) { $missing += "DB_USER" }
if (-not $DbPassword) { $missing += "DB_PASSWORD" }
if (-not $DbHost) { $DbHost = "localhost"; Write-Host "[INFO] DB_HOST not set, using localhost" }
if (-not $DbPort) { $DbPort = "5432"; Write-Host "[INFO] DB_PORT not set, using 5432" }

if ($missing.Count -gt 0) {
    Write-Host "[FAIL] Missing required environment variables: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "       Set them before running: `$env:DB_NAME='...'"
    exit 1
}

# Ensure backup directory exists
if (-not (Test-Path -LiteralPath $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "[INFO] Created backup directory: $BackupDir"
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path -Path $BackupDir -ChildPath "${DbName}_${timestamp}.dump"
$logFile = Join-Path -Path $BackupDir -ChildPath "${DbName}_${timestamp}.log"

Write-Host "=== PostgreSQL Backup ===" -ForegroundColor Cyan
Write-Host "Database: $DbName"
Write-Host "Host: $DbHost`:$DbPort"
Write-Host "Output: $backupFile"

# Set PGPASSWORD for pg_dump
$env:PGPASSWORD = $DbPassword

try {
    & "pg_dump" `
        -h $DbHost `
        -p $DbPort `
        -U $DbUser `
        -F c `
        -Z 9 `
        -v `
        -f $backupFile `
        $DbName 2>&1 | Tee-Object -FilePath $logFile

    if ($LASTEXITCODE -eq 0) {
        $fileInfo = Get-Item -LiteralPath $backupFile
        Write-Host "[PASS] Backup completed: $backupFile" -ForegroundColor Green
        Write-Host "       Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
    } else {
        Write-Host "[FAIL] pg_dump failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "[FAIL] Backup failed: $_" -ForegroundColor Red
    exit 1
} finally {
    Remove-Item -LiteralPath "env:PGPASSWORD" -ErrorAction SilentlyContinue
}

# Cleanup old backups
$cutoff = (Get-Date).AddDays(-$RetentionDays)
$oldBackups = Get-ChildItem -LiteralPath $BackupDir -Filter "*.dump" | Where-Object { $_.LastWriteTime -lt $cutoff }
foreach ($old in $oldBackups) {
    Remove-Item -LiteralPath $old.FullName -Force
    Write-Host "[INFO] Removed old backup: $($old.Name)"
}

Write-Host "=== Backup finished at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
