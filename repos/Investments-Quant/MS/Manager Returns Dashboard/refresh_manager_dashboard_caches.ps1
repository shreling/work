param(
    [string]$PythonExe = "python",
    [string]$PostMapPath = "",
    [string]$PreMapPath = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$msDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dashboardDir = Join-Path $msDir "Manager Returns Dashboard"
$fetchScript = Join-Path $msDir "fetch_manager_returns_data.py"
$buildScript = Join-Path $dashboardDir "build_full_manager_history_data.py"
$fetchMsciScript = Join-Path $dashboardDir "fetch_msci_index_data.py"

$postCacheMs = Join-Path $msDir "manager_returns_data.js"
$preCacheMs = Join-Path $msDir "pre_appointment_data.js"
$postCacheDashboard = Join-Path $dashboardDir "manager_returns_data.js"
$preCacheDashboard = Join-Path $dashboardDir "pre_appointment_data.js"
$fullCacheDashboard = Join-Path $dashboardDir "full_manager_history_data.js"
$msciCacheDashboard = Join-Path $dashboardDir "msci_index_data.js"

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    & $Action
    Write-Host "OK: $Name" -ForegroundColor Green
}

function Invoke-Python {
    param(
        [string[]]$PyArgs
    )

    $cmdPreview = "$PythonExe " + ($PyArgs -join " ")
    if ($DryRun) {
        Write-Host "[DryRun] $cmdPreview"
        return
    }

    & $PythonExe @PyArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $cmdPreview"
    }
}

if (-not (Test-Path $fetchScript)) {
    throw "Missing fetch script: $fetchScript"
}
if (-not (Test-Path $buildScript)) {
    throw "Missing build script: $buildScript"
}
if (-not (Test-Path $fetchMsciScript)) {
    throw "Missing MSCI fetch script: $fetchMsciScript"
}

Write-Host "Starting Manager Dashboard cache refresh..." -ForegroundColor Yellow
Write-Host "MS folder: $msDir"
Write-Host "Dashboard folder: $dashboardDir"
Write-Host "Python executable: $PythonExe"

Invoke-Step "Fetch Post-Appointment cache" {
    $pyArgs = @($fetchScript)
    if ($PostMapPath) {
        $pyArgs += $PostMapPath
    }
    Invoke-Python -PyArgs $pyArgs
}

Invoke-Step "Fetch Pre-Appointment cache" {
    $pyArgs = @($fetchScript, "pre-appointment")
    if ($PreMapPath) {
        $pyArgs += $PreMapPath
    }
    Invoke-Python -PyArgs $pyArgs
}

Invoke-Step "Copy fresh caches into dashboard folder" {
    if ($DryRun) {
        Write-Host "[DryRun] Copy-Item '$postCacheMs' '$postCacheDashboard' -Force"
        Write-Host "[DryRun] Copy-Item '$preCacheMs' '$preCacheDashboard' -Force"
        return
    }

    if (-not (Test-Path $postCacheMs)) {
        throw "Expected file not found after fetch: $postCacheMs"
    }
    if (-not (Test-Path $preCacheMs)) {
        throw "Expected file not found after fetch: $preCacheMs"
    }

    Copy-Item $postCacheMs $postCacheDashboard -Force
    Copy-Item $preCacheMs $preCacheDashboard -Force
}

Invoke-Step "Build Full Manager History cache" {
    Invoke-Python -PyArgs @($buildScript)
}

Invoke-Step "Fetch MSCI Index cache" {
    Invoke-Python -PyArgs @($fetchMsciScript)
}

if (-not $DryRun) {
    if (-not (Test-Path $fullCacheDashboard)) {
        throw "Expected full-history cache was not created: $fullCacheDashboard"
    }
    if (-not (Test-Path $msciCacheDashboard)) {
        throw "Expected MSCI cache was not created: $msciCacheDashboard"
    }

    $fullInfo = Get-Item $fullCacheDashboard
    $msciInfo = Get-Item $msciCacheDashboard
    Write-Host "`nDone. Full cache refreshed:" -ForegroundColor Green
    Write-Host "  $($fullInfo.FullName)"
    Write-Host "  LastWriteTime: $($fullInfo.LastWriteTime)"
    Write-Host "Done. MSCI cache refreshed:" -ForegroundColor Green
    Write-Host "  $($msciInfo.FullName)"
    Write-Host "  LastWriteTime: $($msciInfo.LastWriteTime)"
}
else {
    Write-Host "`nDry run complete. No files changed." -ForegroundColor Yellow
}
