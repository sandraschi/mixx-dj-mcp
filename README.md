# Mixx-DJ-MCP - AI-Powered Mixxx DJ Control

[![GitHub stars](https://img.shields.io/github/stars/sandraschi/mixx-dj-mcp?style=flat-square)](https://github.com/sandraschi/mixx-dj-mcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)](https://www.python.org/)
[![FastMCP 3.4+](https://img.shields.io/badge/FastMCP-3.4%2B-purple?style=flat-square)](https://github.com/jlowin/fastmcp)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

Control [Mixxx](https://mixxx.org/) open-source DJ software through natural language.
Search your library, cue tracks, set loops, apply effects, and mix — all from your AI assistant.

```
User ──→ AI IDE (Claude/Cursor) ──→ mixx-dj-mcp (FastMCP) ──→ OSC Bridge ──→ Mixxx
                                                                                  │
                                                                             ┌────┴────┐
                                                                             │  4 Decks │
                                                                             │  Mixer   │
                                                                             │  Effects │
                                                                             │  Library │
                                                                             └─────────┘
```

## Features

- **4-Deck Control** — Play, stop, cue, loop, sync, hot cues, scratch, seek, quantize, keylock
- **Library Search** — Full-text search, crate/playlist browsing, track metadata
- **Effect Chains** — Enable/disable effects, adjust parameters, quick-effect presets
- **Mixer** — Crossfader, per-channel EQ (high/mid/low), gain, volume, headphone cue, talkover
- **Sync & Beatmatch** — Sync to master, tap tempo, nudge
- **Prefab UI Cards** — Rich in-chat cards for deck status, mixer state, library results
- **SOTA Webapp** — React/Vite/Bun/Tailwind/Zustand dashboard with live Mixxx status
- **Tauri NSIS Installer** — Single-file desktop installer with embedded backend
- **MCPB Bundle** — Claude Desktop single-click install

## Quick Start

```bash
# Install dependencies
uv sync

# Configure Mixxx (one-time)
# Preferences → MIDI/OSC → Enable OSC → Output port: 11118, Input port: 11119, localhost
# Restart Mixxx

# Start the server
uv run python -m mixx_dj_mcp.server

# Or with HTTP transport
uv run uvicorn mixx_dj_mcp.server:app --port 11116 --reload
```

## Requirements

- **Python 3.12+**
- **Mixxx 2.5+** — with OSC enabled (see [bridge setup](bridge/README.md))
- **bun** — for the webapp (`C:\Users\sandr\.bun\bin\bun.exe`)

## Installation

### uv (recommended)

```bash
uv sync
cp .env.example .env
# Edit .env with your Mixxx OSC ports
```

### Mixxx OSC Configuration

1. Open Mixxx → **Preferences**
2. Go to **MIDI/OSC** section
3. **Enable OSC**: check the box
4. **Output port**: `11118`
5. **Input port**: `11119`
6. **Send to**: `127.0.0.1`
7. Restart Mixxx

See [bridge/README.md](bridge/README.md) for the full OSC address reference.

## Webapp

The SOTA webapp provides a live dashboard for monitoring and controlling Mixxx.

```bash
cd web_sota
bun install
bun run dev
```

Opens at `http://127.0.0.1:11117`

## Tool Reference

| Tool | Operations | Description |
|------|-----------|-------------|
| `mixx_deck` | `play`, `stop`, `cue`, `cue_goto`, `loop`, `loop_roll`, `sync`, `sync_enable`, `hot_cue`, `hot_cue_clear`, `scratch`, `seek`, `quantize`, `keylock`, `load_track`, `eject`, `beatjump`, `beatloop`, `rate`, `rate_reset`, `pregain`, `filter_high`, `filter_mid`, `filter_low` | Full deck control for all 4 decks |
| `mixx_library` | `search`, `browse_crate`, `browse_playlist`, `track_info`, `list_crates`, `list_playlists`, `search_bpm`, `search_genre`, `search_key` | Library search and navigation |
| `mixx_effects` | `chain_enable`, `chain_select`, `chain_focus`, `effect_enable`, `effect_param`, `quick_effect`, `clear_chain`, `list_chains` | Effect chain and parameter control |
| `mixx_mixer` | `crossfader`, `crossfader_curve`, `volume`, `gain`, `balance`, `headphone`, `talkover`, `orientation`, `eq_high`, `eq_mid`, `eq_low`, `eq_reset` | Mixer channel control |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   AI Assistant                       │
│  (Claude Desktop / Cursor / opencode)                │
└──────────────┬──────────────────────────────────────┘
               │ MCP stdio/HTTP
┌──────────────▼──────────────────────────────────────┐
│              mixx-dj-mcp (FastMCP 3.4+)              │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │   Deck   │  │ Library  │  │ Effects  │           │
│  │  Control │  │  Search  │  │   Chain  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │                  │
│  ┌────▼──────────────▼──────────────▼─────┐           │
│  │           OSC Bridge (python-osc)       │           │
│  └────────────────────┬───────────────────┘           │
└───────────────────────┼───────────────────────────────┘
                        │ OSC UDP (port 11118/11119)
┌───────────────────────▼───────────────────────────────┐
│                    Mixxx 2.5+                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Deck 1  │ │  Deck 2  │ │  Deck 3  │ │  Deck 4  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │                   Mixer + Effects                 │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │                   Library                         │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

The OSC bridge uses the [python-osc](https://pypi.org/project/python-osc/) library to send and receive OSC messages to Mixxx. Each tool maps to one or more OSC `/controller` addresses as documented in [bridge/README.md](bridge/README.md).

## Tauri Native Installer

A standalone NSIS installer bundles the React webapp and Python backend into a single `.exe`.

```bash
just build-native
```

Output: `native/target/release/bundle/nsis/Mixx-DJ-MCP_0.1.0_x64-setup.exe`

Pre-release certification:

```bash
just build-native && just cua-nsis-test
```

## MCPB Bundle

For Claude Desktop single-click install:

```bash
mcpb pack . dist/mixx-dj-mcp.mcpb
```

## Development

### just recipes

```bash
just lint        # ruff check + format
just test        # pytest
just serve       # start dev server
just build-native  # Tauri NSIS build
just cua-nsis-test # CUA smoke test
just e2e         # Playwright E2E
```

### Testing

```bash
uv run pytest tests/ -q
uv run pytest tests/ --cov=mixx_dj_mcp
```

### Linting

```bash
uv run ruff check src/
uv run ruff format src/
```

## data-testid Notes (CUA Testing)

The webapp dashboard uses `data-testid` attributes for CUA/Playwright targeting:

| Attribute | Element |
|-----------|---------|
| `dashboard` | Dashboard container |
| `kpi-server` | Server name KPI |
| `kpi-decks` | Active decks count |
| `kpi-mixx-status` | Mixxx connection status |
| `backend-dot` | Backend connection indicator |
| `chat-page` | Chat page container |
| `chat-input` | Chat input field |

## License

[MIT](LICENSE) - Sandra Schipal
