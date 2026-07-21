<#
.SYNOPSIS
    Backend smoke tests for health, readiness, and critical endpoints.
.DESCRIPTION
    Runs smoke tests against backend API endpoints to verify they are operational.
.NOTES
    Requires: BASE_URL, API_KEY, TENANT_ID environment variables or parameters.
#>

param(
    [string]$BaseUrl = $env:BASE_URL ?? "http://localhost:8000",
    [string]$ApiKey = $env:API_KEY ?? "e2e-test-key-2026",
    [string]$TenantId = $env:TENANT_ID ?? ""
)

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [hashtable]$Headers = @{},
        [int[]]$ExpectedStatus = @(200)
    )
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -Headers $Headers -UseBasicParsing -ErrorAction Stop
        $statusCode = 200  # Invoke-RestMethod throws on non-2xx
        if ($ExpectedStatus -contains $statusCode) {
            Write-Host "✅ $Name - OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Name - Unexpected status: $statusCode" -ForegroundColor Red
            return $false
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($ExpectedStatus -contains $statusCode) {
            Write-Host "✅ $Name - Expected status: $statusCode" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Name - Status: $statusCode - $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
}

Write-Host "=== Backend Smoke Tests ===" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host "Tenant ID: $TenantId" -ForegroundColor Gray
Write-Host ""

$headers = @{
    "X-API-Key" = $ApiKey
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}
if ($TenantId) { $headers["X-Tenant-ID"] = $TenantId }

$results = @()

# 1. Health check (no auth)
$results += Test-Endpoint "Health Check" "$BaseUrl/health/"

# 2. Readiness check (no auth)
$results += Test-Endpoint "Readiness Check" "$BaseUrl/api/v1/monitoring/ready/"

# 3. Metrics endpoint
$results += Test-Endpoint "Metrics Endpoint" "$BaseUrl/api/v1/monitoring/metrics/" -Headers $headers

# 4. Auth health
$results += Test-Endpoint "Auth Health" "$BaseUrl/api/v1/accounts/health/" -Headers $headers

# 5. Critical API endpoints (401/403 acceptable if auth differs)
$criticalEndpoints = @(
    @{ Name = "Companies API"; Url = "/api/v1/companies/" },
    @{ Name = "Products API"; Url = "/api/v1/products/" },
    @{ Name = "Inventory Locations"; Url = "/api/v1/inventory/locations/" },
    @{ Name = "Sales Counter"; Url = "/api/v1/sales/counter/" },
    @{ Name = "Fiscal Config"; Url = "/api/v1/fiscal/config/?branch=1" }
)

foreach ($ep in $criticalEndpoints) {
    $results += Test-Endpoint $ep.Name "$BaseUrl$($ep.Url)" -Headers $headers -ExpectedStatus @(200, 401, 403)
}

# Summary
$passed = ($results | Where-Object { $_ }).Count
$failed = ($results | Where-Object { -not $_ }).Count

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

if ($failed -gt 0) {
    exit 1
} else {
    Write-Host "✅ All smoke tests passed!" -ForegroundColor Green
    exit 0
}