set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# Dashboard

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# Quality

# Execute Ruff linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check src/
    if (Test-Path '{{justfile_directory()}}\web_sota') {
        Set-Location '{{justfile_directory()}}\web_sota'
        npx @biomejs/biome ci .
    }

# Execute Ruff fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check src/ --fix --unsafe-fixes
    uv run ruff format src/
    if (Test-Path '{{justfile_directory()}}\web_sota') {
        Set-Location '{{justfile_directory()}}\web_sota'
        npx @biomejs/biome check --write .
    }

# Serve

# Start the backend server
serve:
    Set-Location '{{justfile_directory()}}'
    uv run uvicorn mixx_dj_mcp.server:app --host 127.0.0.1 --port 11116 --reload

# Start the frontend dev server
dev:
    if (Test-Path '{{justfile_directory()}}\web_sota') {
        Set-Location '{{justfile_directory()}}\web_sota'
        npm run dev
    }

# Test

# Run tests
test:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ -q

# Tauri Native

# Build Tauri native desktop app (full pipeline: frontend + PyInstaller + NSIS)
build-native:
    Set-Location '{{justfile_directory()}}\native'
    pwsh -NoLogo -File .\build.ps1

# Run the CUA smoke test against the installed NSIS app
cua-nsis-test:
    uv run python scripts/cua-smoke.py
