<#
.SYNOPSIS
    PDV Electron app smoke tests.
.DESCRIPTION
    Verifies PDV build artifacts and critical renderer routes.
.NOTES
    Requires: PDV_DIST_PATH environment variable or parameter.
#>

param(
    [string]$DistPath = $env:PDV_DIST_PATH ?? "C:\ERP\pdv\dist"
)

Write-Host "=== PDV Smoke Tests ===" -ForegroundColor Cyan
Write-Host "Dist Path: $DistPath" -ForegroundColor Gray
Write-Host ""

$results = @()

function Test-File {
    param([string]$Name, [string]$Path)
    if (Test-Path $Path) {
        Write-Host "✅ $Name - Found" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $Name - Missing: $Path" -ForegroundColor Red
        return $false
    }
}

function Test-Dir {
    param([string]$Name, [string]$Path)
    if (Test-Path $Path -PathType Container) {
        Write-Host "✅ $Name - Directory exists" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $Name - Missing directory: $Path" -ForegroundColor Red
        return $false
    }
}

# 1. Build artifacts
$results += Test-Dir "Renderer Dist" "$DistPath\renderer"
$results += Test-Dir "Main Process" "$DistPath\main"
$results += Test-Dir "Preload Scripts" "$DistPath\preload"

$results += Test-File "Renderer index.html" "$DistPath\renderer\index.html"
$results += Test-File "Main entry" "$DistPath\main\index.js"
$results += Test-File "Preload entry" "$DistPath\preload\index.js"

# 2. Critical assets
$assetsDir = "$DistPath\renderer\assets"
if (Test-Path $assetsDir) {
    $jsFiles = Get-ChildItem $assetsDir -Filter "*.js"
    $cssFiles = Get-ChildItem $assetsDir -Filter "*.css"
    
    $results += Test-File "JS Bundle" ($jsFiles | Select-Object -First 1).FullName
    $results += Test-File "CSS Bundle" ($cssFiles | Select-Object -First 1).FullName
    
    Write-Host "  JS files: $($jsFiles.Count)" -ForegroundColor Gray
    Write-Host "  CSS files: $($cssFiles.Count)" -ForegroundColor Gray
}

# 3. Verify index.html has critical routes
$indexHtml = "$DistPath\renderer\index.html"
if (Test-Path $indexHtml) {
    $content = Get-Content $indexHtml -Raw
    
    $criticalRoutes = @(
        "sale",           # PDV sale screen
        "dashboard",      # Dashboard
        "login",          # Login
        "cash-session"    # Cash session
    )
    
    foreach ($route in $criticalRoutes) {
        if ($content -match $route) {
            Write-Host "✅ Route reference: $route" -ForegroundColor Green
            $results += $true
        } else {
            Write-Host "❌ Route reference missing: $route" -ForegroundColor Red
            $results += $false
        }
    }
}

# 4. Check for source maps (optional, dev builds)
$mapFiles = Get-ChildItem $assetsDir -Filter "*.map" -ErrorAction SilentlyContinue
if ($mapFiles.Count -gt 0) {
    Write-Host "  Source maps: $($mapFiles.Count) found" -ForegroundColor Gray
}

# 5. Package.json verification
$packageJson = "$DistPath\..\package.json"
if (Test-Path $packageJson) {
    $pkg = Get-Content $packageJson -Raw | ConvertFrom-Json
    Write-Host "  PDV Version: $($pkg.version)" -ForegroundColor Gray
    Write-Host "  Electron: $($pkg.devDependencies.electron)" -ForegroundColor Gray
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
    Write-Host "✅ All PDV smoke tests passed!" -ForegroundColor Green
    exit 0
}