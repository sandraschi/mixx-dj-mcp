$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
if (-not (Test-Path (Join-Path $root "web_sota\package.json"))) {
    Write-Host "No web_sota/package.json" -ForegroundColor Yellow
    exit 0
}
Set-Location (Join-Path $root "web_sota")
npm run dev
