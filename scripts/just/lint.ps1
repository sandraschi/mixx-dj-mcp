$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\..
uv run ruff check src/
if (Test-Path "$PWD\web_sota") {
    Set-Location "$PWD\web_sota"
    npx @biomejs/biome ci .
}
