param(
    [string]$PdvDir = "..\pdv",
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$exitCode = 0

Write-Host "=== Smoke Test: PDV Electron ===" -ForegroundColor Cyan
Write-Host "PDV directory: $PdvDir`n"

# 1. Check package.json exists
$pkgJson = Join-Path -Path $PdvDir -ChildPath "package.json"
if (Test-Path -LiteralPath $pkgJson) {
    Write-Host "[PASS] package.json found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] package.json not found at $pkgJson" -ForegroundColor Red
    exit 1
}

# 2. Check node_modules exists
$nodeModules = Join-Path -Path $PdvDir -ChildPath "node_modules"
if (Test-Path -LiteralPath $nodeModules) {
    Write-Host "[PASS] node_modules found" -ForegroundColor Green
} else {
    Write-Host "[WARN] node_modules not found — run 'npm install' first" -ForegroundColor Yellow
}

# 3. Check TypeScript compiles
try {
    $tsc = & "npx.cmd" --prefix "$PdvDir" tsc --noEmit 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[PASS] TypeScript compilation: no errors" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] TypeScript compilation errors:" -ForegroundColor Red
        Write-Host "$tsc"
        $exitCode = 1
    }
} catch {
    Write-Host "[WARN] TypeScript check skipped (tsc not available): $_" -ForegroundColor Yellow
}

# 4. Run unit tests
try {
    $testOutput = & "npx.cmd" --prefix "$PdvDir" vitest run --reporter=verbose 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[PASS] Unit tests: all passed" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Unit tests failed" -ForegroundColor Red
        $exitCode = 1
    }
} catch {
    Write-Host "[WARN] Unit tests skipped (vitest not available): $_" -ForegroundColor Yellow
}

# 5. Check critical renderer routes exist
$criticalPaths = @(
    "src/renderer/pages",
    "src/renderer/contexts"
)
foreach ($p in $criticalPaths) {
    $fullPath = Join-Path -Path $PdvDir -ChildPath $p
    if (Test-Path -LiteralPath $fullPath) {
        Write-Host "[PASS] $p exists" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $p not found" -ForegroundColor Red
        $exitCode = 1
    }
}

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "=== All PDV checks passed ===" -ForegroundColor Green
} else {
    Write-Host "=== Some PDV checks FAILED ===" -ForegroundColor Red
}
exit $exitCode
