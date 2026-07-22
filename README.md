<div align="center">
  <h1>Mixx-DJ-MCP</h1>
  <p><strong>AI-Powered Mixxx DJ Control</strong> — 80+ MCP operations across 12 portmanteaux + 3 Prefab cards</p>
  <p><em>Decks · Library · Effects · Mixer · Crates · Stems · Transitions · Video · Set Sequencing · Vinyl Catalog · Skin Management · Controller Auto-Detect · DAW Export</em></p>

  [![GitHub stars](https://img.shields.io/github/stars/sandraschi/mixx-dj-mcp?style=flat-square&logo=github)](https://github.com/sandraschi/mixx-dj-mcp)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![FastMCP](https://img.shields.io/badge/FastMCP-3.4+-purple?style=flat-square)](https://github.com/jlowin/fastmcp)
  [![Mixxx](https://img.shields.io/badge/Mixxx-2.5+-orange?style=flat-square)](https://mixxx.org)
  [![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=white)](https://react.dev)
  [![Tauri](https://img.shields.io/badge/Tauri-2.0-FFC131?style=flat-square&logo=tauri&logoColor=white)](https://tauri.app)
  [![Tests](https://img.shields.io/badge/Tests-41_passing-brightgreen?style=flat-square)](https://github.com/sandraschi/mixx-dj-mcp/actions)
  [![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
</div>

**Mixx-DJ-MCP** is a [FastMCP](https://github.com/jlowin/fastmcp) 3.4+ server that bridges AI coding assistants to [Mixxx](https://mixxx.org/) — the leading open-source DJ software — via its built-in [OSC](https://en.wikipedia.org/wiki/Open_Sound_Control) protocol. No plugins, no patches, no hardware modifications. Point your AI at it and start mixing.

## Quick Start

```bash
uv sync                                    # install deps
uv run uvicorn mixx_dj_mcp.server:app --port 11116 --reload   # start server
```

Then configure Mixxx: **Preferences → MIDI/OSC → Enable OSC**, set output port `11118`, input port `11119`, send to `127.0.0.1`. Restart Mixxx.

## Tool Overview

| Tool | Ops | Description |
|------|-----|-------------|
| `mixx_deck` | 19 | Play/pause, stop, load, cue, loops, sync, rate, scratch, hotcues, quantize, keylock, video |
| `mixx_library` | 8 | Search, browse crates/playlists, load selected, track metadata (BPM, key, replay gain) |
| `mixx_effects` | 7 | Effect chain load/clear, parameter set, meta knob, quick effect, enable/disable |
| `mixx_mixer` | 8 | Crossfader, EQ, gain, volume, headphone cue, talkover, mic gain |
| `mixx_crate` | 5 | Create from natural language, list, delete, add track, LLM-curated agentic crates |
| `mixx_stems` | 6 | Demucs stem separation, load to samplers, mute, volume, stem-aware transition |
| `mixx_transition` | 3 | AI-suggested transitions, apply effects (8 types), auto-crossfader |
| `mixx_set` | 3 | AI set sequencing with harmonic mixing + energy curve, record, analyze |
| `mixx_skin` | 7 | List, search, install, uninstall, preview, video skin, AI skin generation via inkscape-mcp |
| `mixx_vinyl` | 5 | OCR catalog, search, AI gig picker, Plex crossref, collection stats |
| `mixx_controller` | 5 | USB auto-detect, install mapping, list, status, download |
| `mixx_daw` | 4 | Export stems/sessions, send to DaVinci Resolve Fairlight, send to Reaper |
| Prefab cards | 3 | `show_deck_status_card`, `show_mixer_status_card`, `show_library_status_card` |

## Architecture

```
AI Assistant (Claude/Cursor/opencode)
       │ MCP stdio/HTTP
       ▼
mixx-dj-mcp (FastMCP 3.4+)
  ┌─────────┬──────────┬──────────┬──────────┐
  │  Deck   │ Library  │ Effects  │  Mixer   │
  └────┬────┴────┬─────┴────┬─────┴────┬─────┘
  ┌────┴────┐ ┌──┴───┐ ┌───┴───┐ ┌───┴────┐
  │ Stems  │ │ Set  │ │ Skin  │ │ Vinyl  │
  │Transit.│ │ DAW  │ │Control│ │        │
  └────┬────┘ └──┬───┘ └───┬───┘ └───┬────┘
       └─────────┴─────────┴─────────┘
               OSC Bridge (UDP)
          ports 11118 (status) / 11119 (commands)
                    │
                 Mixxx 2.5+
           4 decks · Mixer · Effects · Library
```

## Ports

| Port | Service |
|------|---------|
| 11116 | Backend HTTP (health + REST API) |
| 11117 | Frontend (Vite dev server) |
| 11118 | OSC listener (receives Mixxx status) |
| 11119 | OSC sender (commands to Mixxx) |

## Sub-docs

| Doc | Contents |
|-----|----------|
| [docs/INSTALL.md](docs/INSTALL.md) | Detailed install guide, OSC config, Tauri build, MCPB, troubleshooting |
| [docs/TOOLS.md](docs/TOOLS.md) | Full tool reference — operations, parameters, returns, examples |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | OSC bridge, REST API, webapp, Tauri shell, cross-MCP connections |
  - **Algoriddim comparison** — Feature comparison vs djay iOS
| [docs/VIDEO.md](docs/VIDEO.md) | Video features (requires mixxxxx fork) |
| [docs/AI_TRANSITIONS.md](docs/AI_TRANSITIONS.md) | AI transition effects, prompts, examples |
| [docs/DJ_LANDSCAPE.md](docs/DJ_LANDSCAPE.md) | DJ software comparison — why Mixxx + open source won |
| [docs/NOOB_GUIDE.md](docs/NOOB_GUIDE.md) | Absolute beginner's guide to DJing with Mixxx |

## License

MIT — Sandra Schipal
