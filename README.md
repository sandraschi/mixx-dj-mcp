# Mixx-DJ-MCP — AI-Powered Mixxx DJ Control

[![GitHub stars](https://img.shields.io/github/stars/sandraschi/mixx-dj-mcp?style=flat-square)](https://github.com/sandraschi/mixx-dj-mcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)](https://www.python.org/)
[![FastMCP 3.4+](https://img.shields.io/badge/FastMCP-3.4%2B-purple?style=flat-square)](https://github.com/jlowin/fastmcp)
[![Mixxx 2.5+](https://img.shields.io/badge/Mixxx-2.5%2B-orange?style=flat-square)](https://mixxx.org/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

Control [Mixxx](https://mixxx.org/) open-source DJ software through natural language.
Search your library, cue tracks, set loops, manage effects, and mix — all from your AI assistant.

```
User ──→ AI IDE (Claude/Cursor/opencode) ──→ mixx-dj-mcp (FastMCP) ──→ OSC Bridge ──→ Mixxx
                                                                                           │
                                                                                     ┌─────┴─────┐
                                                                                     │  4 Decks   │
                                                                                     │  Mixer     │
                                                                                     │  Effects   │
                                                                                     │  Library   │
                                                                                     └────────────┘
```

## Features

- **4-Deck Control** — Play/pause, stop, load tracks, cue points, loops, beatloops, sync, rate, scratch, hot cues, quantize, keylock
- **Library Search** — Full-text search, crate/playlist browsing, track metadata (BPM, key, replay gain), load selected to deck
- **Effect Chains** — Load/clear chains, enable/disable units, set parameters, quick effects per deck
- **Mixer** — Crossfader, curve, per-channel gain/EQ/volume/headphone cue/talkover/mic gain
- **Prefab UI Cards** — Rich in-chat cards for deck, mixer, and library status via `prefab-ui`
- **SOTA Webapp** — React 19 / Vite 6 / Tailwind 4 / Zustand 5 / Framer Motion / Lucide dashboard
- **Tauri NSIS Installer** — Single-file desktop installer with embedded Python backend
- **MCPB Bundle** — Claude Desktop single-click install
- **FastAPI REST API** — `/api/health`, `/api/deck/status`, `/api/settings`, `/api/v1/diagnostics`

## Quick Start

```bash
# Install dependencies
uv sync

# Start the server (stdio mode for Claude Desktop)
uv run python -m mixx_dj_mcp.server

# Or with HTTP transport (for webapp + multi-client)
uv run uvicorn mixx_dj_mcp.server:app --port 11116 --reload
```

### Mixxx OSC Configuration (one-time)

1. Open Mixxx → **Preferences** → **MIDI/OSC**
2. **Enable OSC**: check the box
3. **Output port**: `11118` (Mixxx sends status here)
4. **Input port**: `11119` (we send commands here)
5. **Send to**: `127.0.0.1`
6. Restart Mixxx

> Mixxx must be running with OSC enabled for commands to work. Verify with `curl http://127.0.0.1:11116/api/health`.

## Requirements

- **Python 3.12+**
- **Mixxx 2.5+** — with OSC enabled (see OSC config above)
- **bun** — for the webapp (`C:\Users\sandr\.bun\bin\bun.exe`)

## Ports

| Port | Service |
|------|---------|
| 11116 | Backend HTTP (health + REST API) |
| 11117 | Frontend (Vite dev server) |
| 11118 | OSC listener (receives Mixxx status feedback) |
| 11119 | OSC sender (sends commands to Mixxx) |

## Webapp

```bash
cd web_sota
bun install
bun run dev
```

Opens at `http://127.0.0.1:11117` — 7 pages: Dashboard, Decks, Library, Effects, Chat, Tools, Settings.

## Tool Reference

| Tool | Operations | Description |
|------|-----------|-------------|
| `mixx_deck` (19 ops) | `play_pause`, `stop`, `load`, `cue_set`, `cue_play`, `loop_activate`, `loop_beat`, `beatloop`, `rate_set`, `rate_temp`, `sync_enable`, `sync_leader`, `seek`, `scratch`, `hotcue_activate`, `quantize`, `keylock`, `video_enable`, `video_fullscreen` | Full deck control for all 4 decks |
| `mixx_library` (8 ops) | `search`, `browse_crate`, `browse_playlist`, `load_selected`, `get_track_info`, `get_bpm`, `get_key`, `get_replay_gain` | Library search and navigation |
| `mixx_effects` (7 ops) | `list_effects`, `chain_load`, `chain_clear`, `parameter_set`, `meta_set`, `quick_effect_set`, `effect_enable` | Effect chain and parameter control |
| `mixx_mixer` (8 ops) | `crossfader_set`, `crossfader_curve`, `gain_set`, `eq_set`, `volume_set`, `headphone_cue`, `talkover`, `mic_gain` | Mixer channel control |
| `show_deck_status_card` | — | Prefab UI card for deck KPIs |
| `show_mixer_status_card` | — | Prefab UI card for mixer state |
| `show_library_status_card` | — | Prefab UI card for library status |

### Example calls

```python
await mixx_deck(deck=1, operation="play_pause")
await mixx_deck(deck=2, operation="load", track_path="C:/Music/track.mp3")
await mixx_deck(deck=1, operation="sync_enable", enable=True)
await mixx_deck(deck=1, operation="rate_set", value=0.05)
await mixx_library(operation="search", query="tech house")
await mixx_library(operation="load_selected", deck=3)
await mixx_mixer(channel=1, operation="crossfader_set", value=0.0)
await mixx_mixer(deck=1, operation="eq_set", eq_band="low", value=0.5)
await mixx_effects(rack=1, unit=1, operation="chain_load", effect="Flanger")
await mixx_effects(rack=1, unit=1, operation="effect_enable", enable=True)
```

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     AI Assistant                          │
│     (Claude Desktop / Cursor / opencode)                  │
└──────────────┬───────────────────────────────────────────┘
               │ MCP stdio/HTTP
┌──────────────▼───────────────────────────────────────────┐
│               mixx-dj-mcp (FastMCP 3.4+)                  │
│                                                           │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Deck   │  │ Library  │  │ Effects  │  │  Mixer   │  │
│  │ Control │  │  Search  │  │   Chain  │  │          │  │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │              │        │
│  ┌────▼─────────────▼─────────────▼──────────────▼─────┐  │
│  │            OSC Bridge (python-osc UDP)               │  │
│  └─────────────────────┬───────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────┘
                         │ OSC (11118/11119)
┌────────────────────────▼──────────────────────────────────┐
│                      Mixxx 2.5+                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │  Deck 1 │ │  Deck 2 │ │  Deck 3 │ │  Deck 4 │        │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Mixer + Effects + Library               │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

The OSC bridge uses [python-osc](https://pypi.org/project/python-osc/) to send commands to Mixxx on port 11119 and receive status feedback on port 11118. Each tool maps to Mixxx Control Object (CO) addresses as documented in `src/mixx_dj_mcp/bridge/protocol.py`.

## Mixxxxx Integration

This server is companion to [Mixxxxx](https://github.com/sandraschi/mixxxxx) — a video-enabled fork of Mixxx 2.5.6 that adds FFmpeg-based video playback. Control video via:

- `video_enable` — toggle video playback per deck (`enable=True/False`)
- `video_fullscreen` — toggle fullscreen video output (`enable=True/False`)

OSC addresses: `/deck/[N]/video_enabled` and `/deck/[N]/video_fullscreen`. See `projects/mixxxxx/README.md` in `mcp-central-docs` for build instructions.

## Tauri Native Installer

```bash
just build-native
```

Output: `native/target/release/bundle/nsis/Mixx-DJ-MCP_0.1.0_x64-setup.exe`

Pre-release certification:

```bash
just build-native && just cua-nsis-test
```

## MCPB Bundle

```bash
mcpb pack . dist/mixx-dj-mcp.mcpb
```

## Development

### just recipes

```bash
just lint        # ruff check + format
just test        # pytest (41 tests)
just serve       # uvicorn dev server on :11116
just build-native  # Tauri NSIS build
just cua-nsis-test # CUA smoke test
just e2e         # Playwright E2E
```

### Testing

```bash
uv run pytest tests/ -q
uv run pytest tests/ -v --tb=short
```

### Linting

```bash
uv run ruff check src/
uv run ruff format src/ --check
```

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Server health + Mixxx connection status |
| `/api/deck/status` | GET | Live deck states (play, BPM, volume, etc.) |
| `/api/settings` | GET | Current OSC/host configuration |
| `/api/v1/diagnostics` | GET | Full diagnostics (tool count, OSC, system) |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |

## data-testid Notes (CUA Testing)

| Attribute | Element |
|-----------|---------|
| `dashboard` | Dashboard container |
| `kpi-server` | Server name KPI |
| `kpi-decks` | Active decks count |
| `kpi-mixx-status` | Mixxx connection status |
| `backend-dot` | Backend connection indicator |
| `deck-status-card` | Deck status Prefab card |
| `mixer-status-card` | Mixer status Prefab card |

## License

[MIT](LICENSE) — Sandra Schipal
