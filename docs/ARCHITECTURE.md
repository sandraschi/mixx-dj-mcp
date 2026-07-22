# Architecture

## Overview

Mixx-DJ-MCP bridges AI coding assistants to Mixxx using the Open Sound Control (OSC) protocol. The architecture has 5 layers:

1. **MCP Tools Layer** — 12 FastMCP portmanteaux exposing 80+ operations
2. **OSC Bridge** — UDP communication with Mixxx via python-osc
3. **REST API** — FastAPI endpoints for health, status, diagnostics, and deck handoff
4. **SOTA Webapp** — React 19 / Vite 6 dashboard
5. **Tauri Shell** — NSIS installer with embedded Python backend

## OSC Bridge

The bridge is the core communication layer. It maintains a persistent UDP socket that sends commands to Mixxx on port 11119 and receives status feedback on port 11118.

```
mixx_dj_mcp/bridge/
├── osc_bridge.py    # UDP client + state tracking (get_state, get_global_state)
├── protocol.py      # OSC address constants and CO mappings
└── __init__.py
```

Mixxx exposes all controls under OSC Control Objects (COs). Example address patterns:
- `/deck/[1-4]/play` — play/pause
- `/deck/[1-4]/rate` — playback rate
- `/EffectRack[1-3]_EffectUnit[1-4]/enabled` — effect unit toggle
- `/crossfader` — master crossfader
- `/microphone/gain` — mic gain

The bridge also tracks state from Mixxx's OSC feedback (best-effort, UDP is fire-and-forget).

## Source Layout

```
src/mixx_dj_mcp/
├── server.py          # FastMCP app, FastAPI app, lifespan, main()
├── http_app.py        # FastAPI factory + CORS + MCP mount
├── config.py          # Env-based configuration
├── transport.py       # MCP transport helpers
├── bridge/
│   ├── osc_bridge.py
│   └── protocol.py
└── tools/
    ├── __init__.py      # Portmanteau imports (register_all_tools)
    ├── deck_control.py  # mixx_deck
    ├── library.py       # mixx_library
    ├── effects.py       # mixx_effects
    ├── mixer.py         # mixx_mixer
    ├── smart_crate.py   # mixx_crate
    ├── stems.py         # mixx_stems
    ├── transitions.py   # mixx_transition
    ├── set_sequencer.py # mixx_set
    ├── skin_manager.py  # mixx_skin
    ├── vinyl.py         # mixx_vinyl
    ├── controller.py    # mixx_controller
    ├── daw.py           # mixx_daw
    └── prefab_cards.py  # show_deck/mixer/library_status_card
```

## REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Server health + Mixxx connection status |
| `/api/deck/status` | GET | Live deck states (play, BPM, volume, etc.) |
| `/api/settings` | GET | Current OSC/host configuration |
| `/api/v1/diagnostics` | GET | Full diagnostics (tool count, OSC, system) |
| `/api/v1/deck/{id}/load` | POST | REST deck handoff (load track) |
| `/api/v1/deck/{id}/play_pause` | POST | REST deck handoff |
| `/api/v1/deck/{id}/sync` | POST | REST deck handoff |
| `/api/v1/deck/{id}/cue` | POST | REST deck handoff |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |

The REST API follows the fleet [Cross-MCP Deck Handoff Convention](https://github.com/sandraschi/mcp-central-docs/operations/WEBAPP_PORTS.md) — stable endpoints for inter-server deck control.

## Webapp (SOTA)

The React dashboard at `web_sota/` provides 7 pages:

- **Cockpit** — Combined view: Plex search, SFX browser, deck status, AI chat
- **Dashboard** — Live stats, health, Mixxx connection status
- **Decks** — Per-deck controls and KPIs
- **Library** — Search and browse Mixxx library
- **Effects** — Effect chain browser and controls
- **Chat** — AI assistant with local LLM integration
- **Settings** — OSC config, ports, provider detection

Tech stack: React 19, Vite 6, Tailwind 4, Zustand 5, Framer Motion, Lucide icons. Dark theme with Amber accents.

## Tauri Shell

The `native/` directory contains a Tauri 2.0 wrapper with embedded Python backend (PyInstaller). Build produces a single NSIS installer.

```
native/
├── Cargo.toml
├── tauri.conf.json     # resources (not externalBin), NSIS hooks
├── build.ps1           # Full pipeline: frontend → PyInstaller → Tauri → NSIS
├── src/backend.rs      # Materialize backend, spawn child, health check
├── src/main.rs         # Tauri app with backend lifecycle
├── windows/hooks.nsh   # NSIS kill hooks for clean uninstall
└── capabilities/default.json
```

## Cross-MCP Connections

### DaVinci Resolve (Fairlight)

`mixx_daw` sends stem WAV files to DaVinci Resolve's Fairlight page via `davinci-resolve-mcp` REST API at `http://127.0.0.1:10843`.

### Reaper

`mixx_daw` sends stem files to Reaper via `reaper-mcp` REST API at `http://127.0.0.1:10797`.

### Plex

`mixx_vinyl` cross-references vinyl records against digital copies in Plex via `plex-mcp` at `http://localhost:10740`.

### Inkscape

`mixx_skin` uses `inkscape-mcp` at `http://127.0.0.1:11028` for SVG recoloring during skin generation.

### Ollama (Local LLM)

Multiple tools use Ollama at `http://localhost:11434` with `llama3.2:3b`:
- `mixx_transition` — suggest transitions based on track metadata
- `mixx_set` — harmonic mixing sequence optimization
- `mixx_crate` — natural language to Mixxx search syntax
- `mixx_vinyl` — AI gig record selection
- `mixx_skin` — color palette extraction from natural language

### SFX / VFX

The Cockpit page integrates SFX browser and deck status alongside Plex search — framework for future cross-connection with `sfx-mcp` and `vfx-mcp` for sound effects and video effects during live sets.

## Data Flow Diagram

```
User: "Load Daft Punk on deck 2, sync it, apply reverb"
  │
  ▼
Claude Desktop / Cursor / opencode
  │ MCP invoke(mixx_deck(load)) + invoke(mixx_deck(sync)) + invoke(mixx_effects(chain_load))
  ▼
mixx-dj-mcp server
  ├── deck_control.py → bridge.send("/deck/2/LoadTrack", ...)
  ├── deck_control.py → bridge.send("/deck/2/sync_enabled", 1.0)
  └── effects.py → bridge.send("/EffectRack1_EffectUnit1/chain_load", "Reverb")
      │
      ▼ OSC UDP (port 11119)
      │
  Mixxx 2.5+
  ├── Deck 2: loads track, syncs to master, enables Reverb
  └── OSC feedback (port 11118) → bridge.get_state("bpm", 2, ...)
```

## Error Handling

All tools return structured responses with recovery suggestions:

```json
{
  "success": false,
  "message": "DaVinci Resolve MCP not reachable at http://127.0.0.1:10843. Is resolve-mcp running?",
  "data": {"api_url": "http://127.0.0.1:10843"}
}
```
