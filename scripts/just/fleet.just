# Fleet Standard Recipes
# Import this file in any repo's justfile:
#     import 'scripts/just/fleet.just'

REPO_DIR := justfile_directory()

# Build .mcpb bundle for Claude Desktop
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{REPO_DIR}}/scripts/mcpb-pack.ps1" -RepoRoot "{{REPO_DIR}}"

# Run CUA-NSIS smoke test (install -> launch -> verify -> uninstall)
cua-nsis-test:
    C:\Windows\py.exe scripts/cua-smoke.py

# Scan repository for Unicode issues in logger/print calls
emojibuster:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{REPO_DIR}}/scripts/just/emojibuster.ps1" -Path "{{REPO_DIR}}"
