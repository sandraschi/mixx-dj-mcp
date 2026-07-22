$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RepoName = Split-Path -Leaf $Root
$Triple = "x86_64-pc-windows-msvc"
$ResourceDir = "$PSScriptRoot\resources"
$DevDir = "$PSScriptRoot\binaries"
$BackendPort = 11116
New-Item -ItemType Directory -Force -Path $ResourceDir, $DevDir | Out-Null

Write-Host "=== ${RepoName} Tauri Release Build ===" -ForegroundColor Cyan

# Step 0: Verify API_BASE matches backend port
$apiFiles = @("web_sota\src\lib\api.ts", "web_sota\src\api.ts", "webapp\src\lib\api.ts", "webapp\frontend\src\lib\api.ts")
foreach ($f in $apiFiles) {
    $apiPath = Join-Path $Root $f
    if (Test-Path $apiPath) {
        $apiContent = Get-Content $apiPath -Raw
        if ($apiContent -match "127.0.0.1:(\d+)") {
            $apiPort = [int]$Matches[1]
            if ($apiPort -ne $BackendPort) {
                throw "API_BASE in $apiPath points to port $apiPort but backend serves on $BackendPort. In dev Vite proxies work, in prod/NSIS this gives 'Failed to fetch'."
            }
            Write-Host "  API_BASE port: $apiPort (matches backend) V" -ForegroundColor Green
        }
        break
    }
}

# Step 1: TypeScript lint gate + frontend build
$frontendDirs = @("web_sota", "webapp/frontend", "webapp")
foreach ($dir in $frontendDirs) {
    $frontend = Join-Path $Root $dir
    if (Test-Path "$frontend\package.json") {
        Write-Host "-> [1/4] Building frontend ($dir)..." -ForegroundColor Yellow
        Push-Location $frontend

        # Check for bun.lock or package-lock to determine package manager
        if (Test-Path "bun.lock") {
            $pm = "bun"
        } else {
            $pm = "npm"
        }

        if ($pm -eq "bun") {
            bun install 2>$null
        } else {
            npm install --silent 2>$null
        }

        # TypeScript lint gate
        Write-Host "  tsc --noEmit..." -ForegroundColor Gray
        $tscOut = npx tsc --noEmit 2>&1
        $tscExit = $LASTEXITCODE
        if ($tscExit -ne 0) {
            Write-Host "  TypeScript compilation FAILED - fix errors before building NSIS" -ForegroundColor Red
            Write-Host $tscOut
            throw "TypeScript compilation failed - fix all errors before building NSIS installer"
        }

        if ($pm -eq "bun") {
            bun run build
        } else {
            npm run build
        }
        if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
        Pop-Location
        break
    }
}

# Step 2: PyInstaller backend
Write-Host "-> [2/4] PyInstaller backend..." -ForegroundColor Yellow
$specFile = "$Root\${RepoName}-backend.spec"
if (Test-Path $specFile) {
    $entryFile = "$Root\run_server.py"
    if (-not (Test-Path $entryFile)) {
        throw "run_server.py not found at $entryFile - the spec file '$specFile' references this as the entry point. Create run_server.py with dual-transport (MCP_PORT -> HTTP, fallback -> stdio) before building."
    }

    Push-Location $Root
    # Patch fastmcp metadata fallback
    $fm = "$Root\.venv\Lib\site-packages\fastmcp\__init__.py"
    if (Test-Path $fm) {
        $c = Get-Content $fm -Raw
        if ($c -match 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)') {
            $c = $c -replace 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)', 'except PackageNotFoundError:
    try:
        __version__ = _version("fastmcp")
    except PackageNotFoundError:
        __version__ = "0.0.0"'
            Set-Content $fm -Value $c -Encoding utf8
            Write-Host "  Patched fastmcp metadata fallback" -ForegroundColor Yellow
        }
    }
    # Ensure pyinstaller is available
    $pyiExe = "$Root\.venv\Scripts\pyinstaller.exe"
    if (-not (Test-Path $pyiExe)) {
        Write-Host "  Installing pyinstaller in project venv..." -ForegroundColor Yellow
        uv add --dev pyinstaller
    }
    # Pre-clean stale exe
    Remove-Item "$Root\dist\${RepoName}-backend.exe" -Force -ErrorAction SilentlyContinue
    & $pyiExe "$specFile" --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }

    # Smoke-test the frozen binary
    $frozenExe = "$Root\dist\${RepoName}-backend.exe"
    Write-Host "  Smoke-testing frozen binary..." -ForegroundColor Yellow
    $testPort = 11999
    $oldPort = $env:MIXX_MCP_PORT
    $oldHost = $env:MIXX_MCP_HOST
    $env:MIXX_MCP_PORT = "$testPort"
    $env:MIXX_MCP_HOST = "127.0.0.1"
    $testProc = Start-Process -FilePath $frozenExe -NoNewWindow -PassThru -RedirectStandardError "$Root\dist\pyi-crash.log"
    Start-Sleep -Seconds 5
    $env:MIXX_MCP_PORT = $oldPort
    $env:MIXX_MCP_HOST = $oldHost
    if ($testProc.HasExited) {
        $crash = Get-Content "$Root\dist\pyi-crash.log" -Raw
        throw "Frozen binary crashed on launch (exit $($testProc.ExitCode)):`n$crash"
    }
    $testProc.Kill(); $testProc.Dispose()
    Remove-Item "$Root\dist\pyi-crash.log" -Force -ErrorAction SilentlyContinue
    Write-Host "  Frozen binary smoke test PASSED" -ForegroundColor Green
} else {
    throw "Backend spec file not found at $specFile - create ${RepoName}-backend.spec before building NSIS installer."
}

# Step 3: Embed in Tauri resources with size gate
Write-Host "-> [3/4] Embedding backend..." -ForegroundColor Yellow
$src = "$Root\dist\${RepoName}-backend.exe"
if (-not (Test-Path $src)) { throw "Backend exe not found at $src - PyInstaller step failed" }

$sizeMB = (Get-Item $src).Length / 1MB
if ($sizeMB -lt 5) {
    throw "Backend exe is only $([math]::Round($sizeMB, 1)) MB at $src - PyInstaller produced an empty/broken binary. Common causes: (1) run_server.py missing when spec was written, (2) spec 'pathex' doesn't resolve imports, (3) SKIP list in spec is too aggressive and stripped uvicorn/httpx/fastapi."
}
Copy-Item $src "$ResourceDir\${RepoName}-backend.exe" -Force
Copy-Item $src "$DevDir\${RepoName}-backend-$Triple.exe" -Force
Write-Host "  Backend exe: $([math]::Round($sizeMB, 1)) MB" -ForegroundColor Green

# Bundle .env.example
$envExample = "$Root\.env.example"
if (Test-Path $envExample) {
    Copy-Item $envExample "$ResourceDir\.env.example" -Force
    Write-Host "  Bundled .env.example V" -ForegroundColor Green
} else {
    Write-Host "  WARNING: .env.example not found at repo root" -ForegroundColor DarkYellow
}

# Step 4: Tauri NSIS build
Write-Host "-> [4/5] Tauri NSIS bundle..." -ForegroundColor Yellow
Push-Location $PSScriptRoot
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
npx @tauri-apps/cli build --bundles nsis
if ($LASTEXITCODE -ne 0) { throw "Tauri build failed with exit code $LASTEXITCODE" }
Pop-Location

# Step 5: Stage to repo dist/
$distDir = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$nsisDir = "$PSScriptRoot\target\release\bundle\nsis"
if (Test-Path $nsisDir) {
    $setupExe = Get-ChildItem "$nsisDir\*-setup.exe" | Select-Object -First 1
    if ($setupExe) {
        $setupSize = $setupExe.Length / 1MB
        if ($setupSize -lt 1) {
            throw "NSIS setup is only $([math]::Round($setupSize, 1)) MB - likely missing embedded backend or empty dist."
        }
        Copy-Item $setupExe.FullName "$distDir\" -Force
        Write-Host "  NSIS setup: $([math]::Round($setupSize, 1)) MB" -ForegroundColor Green
    }
}

Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "Ship: $nsisDir\*.exe"
