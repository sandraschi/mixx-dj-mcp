param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath
$BackendPort = 11116
$FrontendPort = 11117
$BackendProc = $null
$FrontendProc = $null

Write-Host "=== Mixx-DJ-MCP Startup ===" -ForegroundColor Cyan

# Kill zombies on our ports
Write-Host "-> Clearing port zombies..." -ForegroundColor Yellow
foreach ($port in @($BackendPort, $FrontendPort)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "  Killing PID $($_.OwningProcess) on port $port" -ForegroundColor DarkYellow
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
}
Start-Sleep -Seconds 1

# Start backend
if (-not $BackendOnly) {
    Write-Host "-> Starting backend on port $BackendPort..." -ForegroundColor Yellow
    $BackendProc = Start-Process -NoNewWindow -PassThru -FilePath "uv" -ArgumentList @(
        "run", "uvicorn", "mixx_dj_mcp.server:app",
        "--port", "$BackendPort",
        "--host", "127.0.0.1",
        "--log-level", "info"
    ) -WorkingDirectory $ScriptRoot

    # Health poll
    Write-Host "  Waiting for backend..." -ForegroundColor Gray
    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($r.StatusCode -eq 200) {
                $ready = $true
                Write-Host "  Backend ready!" -ForegroundColor Green
                break
            }
        } catch {}
        Start-Sleep -Seconds 1
    }
    if (-not $ready) {
        Write-Host "  WARNING: Backend health check did not respond within 60s" -ForegroundColor DarkYellow
    }
}

# Start frontend
if (-not $Headless -and -not $BackendOnly) {
    $webRoot = Join-Path $ScriptRoot "web_sota"
    if (Test-Path "$webRoot\package.json") {
        Write-Host "-> Starting frontend on port $FrontendPort..." -ForegroundColor Yellow
        $FrontendProc = Start-Process -NoNewWindow -PassThru -FilePath "bun" -ArgumentList @(
            "run", "dev",
            "--port", "$FrontendPort",
            "--host"
        ) -WorkingDirectory $webRoot

        Start-Sleep -Seconds 3

        # Open browser
        if (-not $NoBrowser) {
            Start-Process "http://127.0.0.1:$FrontendPort"
        }
        Write-Host "  Frontend: http://127.0.0.1:$FrontendPort" -ForegroundColor Green
    } else {
        Write-Host "  No webapp found at $webRoot, skipping frontend" -ForegroundColor DarkYellow
    }
}

Write-Host "=== Mixx-DJ-MCP running ===" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:$BackendPort" -ForegroundColor Green
Write-Host "  Health:   http://127.0.0.1:$BackendPort/api/health" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Gray

# Keep-alive
try {
    while ($true) {
        if ($BackendProc -and $BackendProc.HasExited) {
            Write-Host "Backend process exited ($($BackendProc.ExitCode))" -ForegroundColor Red
            break
        }
        if ($FrontendProc -and $FrontendProc.HasExited) {
            Write-Host "Frontend process exited ($($FrontendProc.ExitCode))" -ForegroundColor Yellow
        }
        Start-Sleep -Seconds 2
    }
} finally {
    # Cleanup on Ctrl+C
    if ($BackendProc -and -not $BackendProc.HasExited) {
        $BackendProc.Kill()
    }
    if ($FrontendProc -and -not $FrontendProc.HasExited) {
        $FrontendProc.Kill()
    }
}
