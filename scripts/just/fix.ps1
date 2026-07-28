$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\..
uv run ruff check src/ --fix --unsafe-fixes
uv run ruff format src/
if (Test-Path "$PWD\web_sota") {
    Set-Location "$PWD\web_sota"
    npx @biomejs/biome check --write .
}
