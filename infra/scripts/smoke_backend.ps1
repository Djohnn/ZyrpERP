param(
    [string]$BaseUrl = "http://localhost:8000",
    [int]$TimeoutSeconds = 10
)

$ErrorActionPreference = "Stop"
$exitCode = 0

Write-Host "=== Smoke Test: Backend ===" -ForegroundColor Cyan
Write-Host "Target: $BaseUrl`n"

# 1. Health endpoint
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health/" -TimeoutSec $TimeoutSeconds
    if ($health.status -eq "healthy") {
        Write-Host "[PASS] Health endpoint: $($health.status)" -ForegroundColor Green
        Write-Host "       DB: $($health.services.database), Cache: $($health.services.cache)"
    } else {
        Write-Host "[FAIL] Health endpoint: $($health.status)" -ForegroundColor Red
        $exitCode = 1
    }
} catch {
    Write-Host "[FAIL] Health endpoint unreachable: $_" -ForegroundColor Red
    $exitCode = 1
}

# 2. Readiness endpoint
try {
    $ready = Invoke-RestMethod -Uri "$BaseUrl/readiness/" -TimeoutSec $TimeoutSeconds
    if ($ready.status -eq "ready") {
        Write-Host "[PASS] Readiness endpoint: $($ready.status)" -ForegroundColor Green
        Write-Host "       Outbox: $($ready.outbox.total_pending) pending, $($ready.outbox.failed_count) failed"
    } else {
        Write-Host "[PASS] Readiness endpoint (degraded): $($ready.status)" -ForegroundColor Yellow
        Write-Host "       Outbox: $($ready.outbox.total_pending) pending"
    }
} catch {
    Write-Host "[FAIL] Readiness endpoint unreachable: $_" -ForegroundColor Red
    $exitCode = 1
}

# 3. Correlation ID header
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/health/" -TimeoutSec $TimeoutSeconds
    if ($response.Headers["X-Correlation-ID"]) {
        Write-Host "[PASS] Correlation-ID header present: $($response.Headers['X-Correlation-ID'])" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Correlation-ID header missing" -ForegroundColor Red
        $exitCode = 1
    }
} catch {
    Write-Host "[FAIL] Correlation-ID check failed: $_" -ForegroundColor Red
    $exitCode = 1
}

# 4. API root reachable
try {
    $apiRoot = Invoke-RestMethod -Uri "$BaseUrl/api/v1/health/" -TimeoutSec $TimeoutSeconds
    Write-Host "[PASS] API v1 health reachable: $($apiRoot.status)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] API v1 health unreachable: $_" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "=== All checks passed ===" -ForegroundColor Green
} else {
    Write-Host "=== Some checks FAILED ===" -ForegroundColor Red
}
exit $exitCode
