# mixx-dj-mcp — fleet recipes (just 1.50+ safe: one-liners or -File scripts)

set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

import 'scripts/just/fleet.just'

# Show available recipes (default when you run `just` with no args)
default:
    @just --list

# Alias for recipe list
help:
    @just --list

# Execute Ruff linting (+ biome if web_sota)
lint:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}/scripts/just/lint.ps1"

# Execute Ruff fix and formatting
fix:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}/scripts/just/fix.ps1"

# Start backend + frontend (same as start.ps1 / fleet start.bat)
start:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}/start.ps1"

# Start the backend server only
serve:
    @powershell.exe -NoProfile -Command "Set-Location '{{justfile_directory()}}'; uv run uvicorn mixx_dj_mcp.server:app --host 127.0.0.1 --port 11116 --reload"

# Start the frontend dev server
dev:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}/scripts/just/dev.ps1"

# Run tests
test:
    @powershell.exe -NoProfile -Command "Set-Location '{{justfile_directory()}}'; uv run pytest tests/ -q"

# Apply daylight-v2 hex scheme to mixxxxx source QSS (dev)
patch-daylight-source mixxxxx_root="D:\\Dev\\repos\\mixxxxx":
    @powershell.exe -NoProfile -Command "Set-Location '{{justfile_directory()}}'; uv run python -c \"from pathlib import Path; from mixx_dj_mcp.skinmaker import scheme_path; from mixx_dj_mcp.skinmaker.qss_patch import patch_qss_file; qss=Path(r'{{mixxxxx_root}}')/'res'/'skins'/'MixxxxxVideo'/'style_daylight.qss'; print(patch_qss_file(qss, scheme_path('daylight-v2')))\""

# Build Tauri native desktop app (frontend + PyInstaller + NSIS)
build-native:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}/native/build.ps1"
