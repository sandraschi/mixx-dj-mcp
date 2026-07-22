<div align="center">
  <h1>🎧 Mixx-DJ-MCP</h1>
  <p><strong>AI-Powered Mixxx DJ Control</strong> — 70+ MCP operations across 10 tools</p>
  <p><em>Decks · Library · Effects · Mixer · Crates · Video · Stems · Set Planning · Vinyl Catalog · Skin Management · Controller Auto-Detect</em></p>

  [![GitHub stars](https://img.shields.io/github/stars/sandraschi/mixx-dj-mcp?style=flat-square&logo=github)](https://github.com/sandraschi/mixx-dj-mcp)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![FastMCP](https://img.shields.io/badge/FastMCP-3.4+-purple?style=flat-square&logo=python)](https://github.com/jlowin/fastmcp)
  [![Mixxx](https://img.shields.io/badge/Mixxx-2.5+-orange?style=flat-square&logo=mediaengine)](https://mixxx.org)
  [![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=white)](https://react.dev)
  [![Tauri](https://img.shields.io/badge/Tauri-2.0-FFC131?style=flat-square&logo=tauri&logoColor=white)](https://tauri.app)
  [![Tests](https://img.shields.io/badge/Tests-41_passing-brightgreen?style=flat-square)](https://github.com/sandraschi/mixx-dj-mcp/actions)
  [![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
  [![Topics](https://img.shields.io/badge/dynamic/json?style=flat-square&label=topics&query=%24&url=https%3A%2F%2Fimg.shields.io%2Fgithub%2Frelease%2Fsandraschi%2Fmixx-dj-mcp)](https://github.com/sandraschi/mixx-dj-mcp)
</div>

**Mixx-DJ-MCP** is a [FastMCP](https://github.com/jlowin/fastmcp) server that bridges AI coding assistants to [Mixxx](https://mixxx.org/) — the leading open-source DJ software — via its built-in [OSC](https://en.wikipedia.org/wiki/Open_Sound_Control) surface. No plugins, no patches, no hardware modifications. Point your AI at it and start mixing.

```
┌──────────────────────────────────────────────────────────────────┐
│  Claude / Cursor / opencode                                     │
│  "Load the last Daft Punk track to deck 2, sync it, apply reverb"│
└───────────────────────────┬──────────────────────────────────────┘
                            │ MCP stdin/stdout or HTTP
┌───────────────────────────▼──────────────────────────────────────┐
│                    mixx-dj-mcp (FastMCP 3.4+)                     │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │   Deck   │ │ Library  │ │ Effects  │ │  Mixer  │ │ Crate  │ │
│  │  (19 ops)│ │  (8 ops) │ │  (7 ops) │ │ (8 ops) │ │(5 ops) │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│  ┌────┴────┐ ┌─────┴─────┐ ┌────┴────┐ ┌─────┴─────┐ ┌───┴────┐ │
│  │ Stems  │ │    Set    │ │  Skin   │ │   Vinyl   │ │Controller││
│  │(6 ops) │ │  (2 ops)  │ │ (7 ops) │ │  (5 ops)  │ │ (5 ops) │ │
│  └────┬────┘ └─────┬─────┘ └────┬────┘ └─────┬─────┘ └───┬────┘ │
│       │            │             │             │           │      │
│  ┌────▼────────────▼─────────────▼─────────────▼───────────▼──┐  │
│  │               OSC Bridge (python-osc UDP)                   │  │
│  └─────────────────────────────┬───────────────────────────────┘  │
└────────────────────────────────┼──────────────────────────────────┘
                                 │ OSC port 11119 (commands → Mixxx)
                                 │ OSC port 11118 (status ← Mixxx)
                    ┌────────────▼────────────┐
                    │    Mixxx 2.5+           │
                    │  ┌──────┐ ┌──────┐     │
                    │  │Deck 1│ │Deck 2│ ...  │
                    │  │Deck 3│ │Deck 4│     │
                    │  └──────┘ └──────┘     │
                    │  Mixer · Effects · Lib  │
                    └─────────────────────────┘
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

Opens at `http://127.0.0.1:11117` — 8 pages: Cockpit, Dashboard, Decks, Library, Effects, Chat, Tools, Settings. Cockpit integrates Plex search, SFX browser, deck status, and AI assistant in one view.

## Tool Reference

| Tool | Operations | Description |
|------|-----------|-------------|
| `mixx_deck` (19 ops) | `play_pause`, `stop`, `load`, `cue_set`, `cue_play`, `loop_activate`, `loop_beat`, `beatloop`, `rate_set`, `rate_temp`, `sync_enable`, `sync_leader`, `seek`, `scratch`, `hotcue_activate`, `quantize`, `keylock`, `video_enable`, `video_fullscreen` | Full deck control + video for all 4 decks |
| `mixx_library` (8 ops) | `search`, `browse_crate`, `browse_playlist`, `load_selected`, `get_track_info`, `get_bpm`, `get_key`, `get_replay_gain` | Library search and navigation |
| `mixx_effects` (7 ops) | `list_effects`, `chain_load`, `chain_clear`, `parameter_set`, `meta_set`, `quick_effect_set`, `effect_enable` | Effect chain and parameter control |
| `mixx_mixer` (8 ops) | `crossfader_set`, `crossfader_curve`, `gain_set`, `eq_set`, `volume_set`, `headphone_cue`, `talkover`, `mic_gain` | Mixer channel control |
| `mixx_crate` (4 ops) | `create`, `list`, `delete`, `add_track` | Smart crate mgmt via natural language |
| `mixx_stems` (6 ops) | `separate`, `status`, `load_stems`, `transition`, `mute`, `volume` | Demucs stem separation + stem-aware crossfade |
| `mixx_set` (2 ops) | `sequence`, `analyze_set` | AI set sequencing with harmonic mixing + energy curve |
| `mixx_skin` (7 ops) | `list`, `search`, `install`, `uninstall`, `preview`, `create_video_skin`, `create_skin` | Skin browser + Inkscape-MCP skin generator |
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
just test        # pytest (42 tests)
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
| `/api/v1/deck/{id}/load` | POST | REST deck handoff (load track) |
| `/api/v1/deck/{id}/play_pause` | POST | REST deck handoff (play/pause/toggle) |
| `/api/v1/deck/{id}/sync` | POST | REST deck handoff (sync) |
| `/api/v1/deck/{id}/cue` | POST | REST deck handoff (cue) |
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
