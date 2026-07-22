# Mixx-DJ-MCP — Product Requirements Document

**Status**: v0.1.0 Shipped (2026-07-22)
**Author**: Sandra Schipal
**Created**: 2026-07-22

---

## Problem

DJs increasingly use AI coding assistants (Claude Desktop, Cursor, opencode) for production workflows but have no way to control their DJ software through natural language. Commercial DJ software (Serato DJ Pro, VirtualDJ, Traktor) lacks open APIs or requires proprietary SDKs. Mixxx is the leading open-source DJ software with a built-in OSC protocol, but no MCP bridge exists to connect it to AI agents.

The gap: A DJ using Claude to plan a set must manually switch between the AI and Mixxx to load tracks, cue, apply effects, or manage transitions. This breaks flow and prevents scripted/programmatic mixing.

## Solution

**Mixx-DJ-MCP** — a FastMCP 3.4+ server that bridges LLM agents to Mixxx via its built-in OSC protocol. The server exposes intuitive deck control, library search, effect management, and mixer operations as composable MCP tools using the fleet portmanteau pattern.

## Target Users

| Persona | Need | Use Case |
|---------|------|----------|
| **DJ / Producer** | Voice or text control while hands are on decks | "Load track X on deck 3, cue at 32 bars, apply reverb" |
| **Live streamer** | Automated transitions between songs | "Crossfade to deck 2 over 16 beats" |
| **Mixxx power user** | Scripted complex mix sequences | Batch-load crate, set loops, chain effects |
| **AI developer** | Testing Mixxx integration via tools | Programmatic playlist management, BPM analysis |

## User Stories

- As a DJ, I want to ask my AI to load the next track so I can focus on mixing.
- As a streamer, I want to trigger effects hands-free during a live set.
- As a producer, I want to script complex mix sequences with precise timing.
- As a mobile DJ, I want to search my library by BPM, key, or genre without touching the laptop.
- As a radio host, I want voice-activated talkover and crossfader control.
- As a developer, I want to use Prefab cards in-chat to see deck status at a glance.

## Shipped Features (v0.1.0)

### Core MCP Layer

- [x] OSC bridge to Mixxx via python-osc (UDP ports 11118/11119)
- [x] `mixx_deck` (17 ops): play_pause, stop, load, cue_set, cue_play, loop_activate, loop_beat, beatloop, rate_set, rate_temp, sync_enable, sync_leader, seek, scratch, hotcue_activate, quantize, keylock
- [x] `mixx_library` (8 ops): search, browse_crate, browse_playlist, load_selected, get_track_info, get_bpm, get_key, get_replay_gain
- [x] `mixx_effects` (7 ops): list_effects, chain_load, chain_clear, parameter_set, meta_set, quick_effect_set, effect_enable
- [x] `mixx_mixer` (8 ops): crossfader_set, crossfader_curve, gain_set, eq_set, volume_set, headphone_cue, talkover, mic_gain
- [x] 3 Prefab UI cards: show_deck_status_card, show_mixer_status_card, show_library_status_card
- [x] Conversational return format (success + message + data keys)
- [x] Error handling with recovery suggestions
- [x] FastAPI REST API: /api/health, /api/deck/status, /api/settings, /api/v1/diagnostics
- [x] CORS configured for Tauri WebView + Tailscale + LAN IPs

### Webapp (SOTA)

- [x] React 19 / Vite 6 / Tailwind 4 / Zustand 5 / Framer Motion / Lucide
- [x] 7 pages: Dashboard, Decks, Library, Effects, Chat, Tools, Settings
- [x] Dark theme with Amber accents
- [x] data-testid attributes for CUA/Playwright testing
- [x] Swagger UI + ReDoc at /docs

### Desktop & Distribution

- [x] Tauri 2.0 NSIS build pipeline with embedded backend (native/)
- [x] MCPB packaging (mcpb/)
- [x] Start scripts (start.ps1, start.bat)
- [x] .env.example configuration

### Testing & CI

- [x] 41 pytest tests (bridge mock, deck, effects, mixer)
- [x] Playwright E2E tests
- [x] CUA-NSIS smoke test (7 phases)
- [x] GitHub Actions CI (.github/workflows/ci.yml)
- [x] Ruff lint + format

### Documentation

- [x] llms.txt + llms-full.txt
- [x] README with Quick Start, Mixxx OSC config, port table, tool reference
- [x] CHANGELOG
- [x] PRD
- [x] Session context injection (.claude-plugin, .cursorrules)
- [x] Glama registry entry (glama.json)

## v0.2 Roadmap (Refinement)

| Priority | Item | Rationale |
|----------|------|-----------|
| P0 | **Real Mixxx verification testing** | All current testing is mock-based. Run actual Mixxx integration tests on Windows with Mixxx 2.5.6 |
| P1 | **OSC feedback reliability** | Improve state tracking from OSC feedback (port 11118) — currently best-effort. Add timeout detection for lost commands |
| P1 | **Webapp UI polish** | Prefab card alignment, responsive layout fixes, loading states on deck status pages |
| P2 | **Tauri build verification** | Run just build-native + just cua-nsis-test end-to-end, verify NSIS installer works on clean Windows |
| P2 | **Recording control** | Start/stop recording via OSC |
| P3 | **Auto-DJ mode toggle** | Enable/disable Mixxx Auto-DJ via OSC |
| P3 | **Waveform position polling** | Track position slider feedback in webapp |
| P3 | **Community feedback** | Open issues on GitHub, gather early-adopter use cases |
| P4 | **Track metadata enrichment** | BPM, key, Rekordbox tag parsing beyond what Mixxx provides |

## v0.3 Roadmap (Advanced)

- Cue point management with beat grid analysis
- Smart crate creation from LLM queries
- Mix recording and export workflow
- Session history and playback analytics
- Deck 3-4 control parity with decks 1-2

## Non-Goals

- Real-time audio processing or analysis
- Waveform rendering or visualization
- Replacing Mixxx's native UI or workflow
- Serato/VirtualDJ/Traktor emulation or compatibility
- MIDI controller mapping or translation
- Streaming audio capture or recording to disk
- BPM/key detection (delegated to Mixxx)
- Auto-mixing or AI-generated transitions (future consideration)

## Architecture

### OSC Protocol Bridge

Mixxx exposes a bidirectional OSC surface. The server maintains a persistent UDP socket that:

1. Sends OSC commands to Mixxx's input port (11119) for control operations
2. Receives OSC feedback from Mixxx's output port (11118) for state tracking

```
mixx_dj_mcp/
├── server.py             # FastMCP app, FastAPI, lifespan
├── http_app.py           # FastAPI factory + CORS + MCP mount
├── config.py             # Env-based config with defaults
├── bridge/
│   ├── osc_bridge.py     # OSC UDP client + state tracking
│   └── protocol.py       # OSC address constants and CO mappings
├── tools/
│   ├── deck_control.py   # mixx_deck portmanteau
│   ├── library.py        # mixx_library portmanteau
│   ├── effects.py        # mixx_effects portmanteau
│   ├── mixer.py          # mixx_mixer portmanteau
│   └── prefab_cards.py   # Prefab UI card tools
```

### REST API

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Server health + Mixxx connection status |
| `GET /api/deck/status` | Live deck states (play, BPM, volume, etc.) |
| `GET /api/settings` | Current OSC/host configuration |
| `GET /api/v1/diagnostics` | Full diagnostics (tool count, OSC status) |
| `GET /api/skills` | List available skills |
| `POST /mcp` | MCP streamable HTTP transport |
| `GET /docs` | Swagger UI |

### Ports

| Port | Service |
|------|---------|
| 11116 | Backend HTTP |
| 11117 | Frontend Vite |
| 11118 | OSC listener (Mixxx feedback) |
| 11119 | OSC sender (commands to Mixxx) |

## Milestones

| Version | Scope | Timeline | Status |
|---------|-------|----------|--------|
| v0.1 | OSC core + deck control + library + effects + mixer + webapp + Tauri + MCPB | 2026-07-22 | ✅ Shipped |
| v0.2 | Real Mixxx testing + OSC feedback reliability + UI polish + Tauri verification | TBD | 🔜 Planned |
| v0.3 | Advanced cue + smart crates + recording + session history | TBD | 📋 Future |

## Open Questions

1. **OSC message reliability** — UDP is fire-and-forget. Current approach: best-effort send + optional state polling via OSC feedback on 11118. Consider adding periodic check pings.
2. **Multiple simultaneous connections** — Stateless OSC supports concurrent clients fine. No issue known.
3. **Security boundaries** — OSC bound to 127.0.0.1 by default. Enforced in config.py.
4. **Mixxx version compatibility** — Verified against Mixxx 2.5.6. OSC address paths may change between major versions.
5. **Deck count** — Mixed supports 4 decks by default. Currently all tools work with deck 1-4. Configurable in future.

## Reference

- [Mixxx OSC Protocol](https://mixxx.org/manual/latest/chapters/osc.html)
- [python-osc](https://pypi.org/project/python-osc/)
- [FastMCP 3.4 Docs](https://github.com/jlowin/fastmcp)
- [Fleet Tauri Standard](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/rules/tauri_nsis_building.md)
- [SOTA Webapp Standard](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/WEBAPP_SOTA_STANDARDS.md)
- [Mixxx 2.5.6](https://mixxx.org/download/)
