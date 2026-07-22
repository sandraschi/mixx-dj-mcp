# Installation Guide

## Prerequisites

- **Python 3.12+**
- **Mixxx 2.5+** — [Download Mixxx](https://mixxx.org/download/)
- **bun** — for the webapp (`C:\Users\sandr\.bun\bin\bun.exe` or `winget install oven-sh.bun`)
- **Rust toolchain** (optional, for Tauri NSIS build): `rustup.rs`

## Quick Install (Dev)

```bash
uv sync
uv run uvicorn mixx_dj_mcp.server:app --port 11116 --reload
```

## Mixxx OSC Configuration (One-Time)

1. Open Mixxx → **Preferences** → **MIDI/OSC**
2. Check **Enable OSC**
3. Set the following:

| Setting | Value |
|---------|-------|
| Output port | `11118` |
| Input port | `11119` |
| Send to | `127.0.0.1` |

4. Click **Apply**, then **restart Mixxx**

## Verify the Connection

```bash
curl http://127.0.0.1:11116/api/health
```

Expected: `{"status": "ok", "server": "mixx-dj-mcp", "version": "0.1.0", "mixx_connected": true}`

## Ports Table

| Port | Protocol | Direction | Service |
|------|----------|-----------|---------|
| 11116 | HTTP | Inbound | Backend REST API + MCP |
| 11117 | HTTP | Inbound | Frontend Vite dev server |
| 11118 | OSC (UDP) | Inbound | Mixxx status feedback → us |
| 11119 | OSC (UDP) | Outbound | Our commands → Mixxx |

## Webapp

```bash
cd web_sota
bun install
bun run dev
```

Opens at `http://127.0.0.1:11117`.

## Tauri NSIS Build

Build the single-file desktop installer with embedded Python backend:

```bash
just build-native
```

Output: `native/target/release/bundle/nsis/Mixx-DJ-MCP_0.1.0_x64-setup.exe`

Pre-release certification:

```bash
just build-native && just cua-nsis-test
```

## MCPB Bundle (Claude Desktop)

```bash
mcpb pack . dist/mixx-dj-mcp.mcpb
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_PORT` / `PORT` | — | Enables HTTP mode if set |
| `MCP_HOST` / `HOST` | `127.0.0.1` | HTTP bind address |
| `MIXXX_HOST` | `127.0.0.1` | Mixxx OSC host |
| `MIXXX_OSC_OUT_PORT` | `11118` | OSC feedback port |
| `MIXXX_OSC_IN_PORT` | `11119` | OSC command port |
| `HTTP_PORT` | `11116` | Backend HTTP port |
| `DAVINCI_RESOLVE_API` | `http://127.0.0.1:10843` | DaVinci Resolve MCP URL |
| `REAPER_API` | `http://127.0.0.1:10797` | Reaper MCP URL |
| `PLEX_MCP_URL` | `http://localhost:10740` | Plex MCP URL |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No response from Mixxx | OSC not enabled | Check Preferences → MIDI/OSC |
| "Connection refused" on 11119 | Wrong port in config | Verify env matches Mixxx OSC settings |
| Commands work intermittently | Port conflict | Check no other app uses 11118/11119 |
| LoadTrack does nothing | Invalid file path | Mixxx must be able to resolve the path |
| Crossfader not moving | Mixxx orientation setting | Ensure channel orientation is set correctly |
| Webapp shows "Failed to fetch" | Backend not running | Start the backend server first |

## Development

```bash
just lint        # ruff check + format
just test        # pytest (41 tests)
just serve       # uvicorn dev server on :11116
just build-native  # Tauri NSIS build
just cua-nsis-test # CUA smoke test
just e2e         # Playwright E2E
```
