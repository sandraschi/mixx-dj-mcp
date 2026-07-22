# Mixx-DJ-MCP — Product Requirements Document v0.1

**Status**: Draft
**Author**: Sandra Schipal
**Created**: 2026-07-22

---

## Problem

DJs increasingly use AI coding assistants (Claude Desktop, Cursor, opencode) for production workflows but have no way to control their DJ software through natural language. Commercial DJ software (Serato DJ Pro, VirtualDJ, Traktor) lacks open APIs or requires proprietary SDKs. Mixxx is the leading open-source DJ software with a built-in OSC protocol, but no MCP bridge exists to connect it to AI agents.

The gap: A DJ using Claude to plan a set must manually switch between the AI and Mixxx to load tracks, cue, apply effects, or manage transitions. This breaks flow and prevents scripted/programmatic mixing.

## Solution

**Mixx-DJ-MCP** — a FastMCP 3.4+ server that bridges LLM agents to Mixxx via its built-in OSC (Open Sound Control) protocol. The server exposes intuitive deck control, library search, effect management, and mixer operations as composable MCP tools.

The architecture follows fleet standards: FastMCP portmanteau tools, Prefab UI cards for in-chat visualization, a SOTA React webapp, Tauri NSIS installer for desktop deployment, and MCPB bundle for Claude Desktop.

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

## Key Features

### v0.1 (Core)

- [x] OSC bridge to Mixxx (ports 11118/11119) via python-osc
- [x] Deck control: play, stop, cue, cue_goto, loop, loop_roll, sync, sync_enable
- [x] Hot cues: set, clear, navigate (4 hot cues per deck)
- [x] Library: full-text search, crate/playlist browsing, track info
- [x] Load track to any deck
- [x] Per-deck transport: seek, beatjump, beatloop, rate, rate_reset, nudge
- [x] Per-deck audio: pregain, filter high/mid/low
- [x] Mixer: crossfader, crossfader curve, per-channel volume/gain/balance/headphone/talkover/orientation
- [x] Effects: chain enable/select/focus, per-effect enable/param, quick effect, clear chain
- [x] Prefab UI cards for deck status, mixer state, library search, track info
- [x] Conversational return format (message + data + success keys)
- [x] Error handling with recovery suggestions

### v0.2 (Refinement)

- [ ] Full 4-deck control parity
- [ ] Scratching with position/timing
- [ ] Recording control (start/stop recording)
- [ ] Auto-DJ mode control
- [ ] Waveform position polling via OSC feedback
- [ ] Track metadata enrichment (BPM, key, Rekordbox tag parsing)

### v0.3 (Webapp + Tauri)

- [ ] SOTA webapp: React/Vite/Bun/Tailwind/Zustand
- [ ] Dashboard with live Mixxx connection status
- [ ] Deck status indicators (track, BPM, play state, loop state)
- [ ] Library browser with search
- [ ] Chat page with LLM integration
- [ ] Settings page for OSC port configuration
- [ ] Tauri NSIS build pipeline with embedded backend
- [ ] Zoom support (Ctrl+scroll) in webview
- [ ] Backend health endpoint + dashboard KPIs
- [ ] CORS configuration for Tauri WebView

### v0.5 (Release)

- [ ] MCPB bundle (.mcpb)
- [ ] Playwright E2E tests
- [ ] CUA-NSIS smoke test (7 phases)
- [ ] GitHub Actions CI/CD
- [ ] llms.txt + llms-full.txt documentation
- [ ] Glama registry entry
- [ ] Session context injection (.claude-plugin, .cursorrules)
- [ ] Mixxx 2.5+ compatibility validated

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
2. Optionally receives OSC feedback from Mixxx's output port (11118) for state tracking

```
mixx_dj_mcp/
├── server.py             # FastMCP app, lifecycle, lifespan
├── transport.py          # Dual transport (stdio/HTTP)
├── config.py             # Env-based config with defaults
├── osc/
│   ├── bridge.py         # OSC UDP client + connection management
│   ├── addresses.py      # OSC address constants and mappings
│   └── feedback.py       # OSC feedback receiver (future)
├── tools/
│   ├── deck.py           # mixx_deck portmanteau
│   ├── library.py        # mixx_library portmanteau
│   ├── effects.py        # mixx_effects portmanteau
│   └── mixer.py          # mixx_mixer portmanteau
├── models/
│   └── schemas.py        # Pydantic models for tool I/O
└── skills/
    └── mixx-dj/
        └── SKILL.md      # Skill definition
```

### MCP Tool Layer

All tools use the fleet portmanteau pattern with an `operation` enum discriminator:

- `mixx_deck(deck: int, operation: Literal[...], ...)` — single tool for all deck operations
- `mixx_library(operation: Literal[...], ...)` — library search and browse
- `mixx_effects(chain: int, operation: Literal[...], ...)` — effect chain control
- `mixx_mixer(channel: int, operation: Literal[...], ...)` — mixer operations

### REST API

FastMCP HTTP mode exposes:

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Server health + Mixxx connection status |
| `GET /api/v1/diagnostics` | Full diagnostics (tool count, OSC status) |
| `GET /api/skills` | List available skills |
| `POST /mcp` | MCP streamable HTTP transport |

### Webapp

Standard SOTA stack: React/Vite/Bun/Tailwind CSS dark theme/Zustand/Lucide/Framer Motion.
Pages: Dashboard, Tools, Chat, Skills, Settings.

### Tauri NSIS

Single-installer pattern: PyInstaller-freezed backend embedded in `bundle.resources`, Rust shell spawns child process on launch.

## Milestones

| Version | Scope | Timeline |
|---------|-------|----------|
| v0.1 | OSC core + library search + deck control + effects + mixer | 2026-07-22 |
| v0.2 | Refinement + polling feedback + recording + Auto-DJ | TBD |
| v0.3 | SOTA webapp + Tauri NSIS installer | TBD |
| v0.5 | MCPB + cert + CI/CD + fleet release | TBD |

## Open Questions

1. **OSC message reliability** — UDP is fire-and-forget. How do we detect lost commands? Options: OSC feedback from Mixxx, periodic state polling, or accept best-effort.
2. **Multiple simultaneous connections** — If both Claude Desktop and Cursor connect, do we allow concurrent OSC sessions? Likely yes (stateless OSC).
3. **Security boundaries** — OSC is unauthenticated on localhost. Should we restrict binding to 127.0.0.1 only? Yes — default config enforces this.
4. **Mixxx version compatibility** — OSC address paths may change between Mixxx versions. Document tested version(s) and add version detection.
5. **Deck count** — Mixxx supports up to 4 decks by default, more with custom skins. Default to 4, configurable via env.
6. **Feedback loop** — Without OSC feedback, the server is blind to Mixxx state changes (e.g., user pressing play on the keyboard). Solution: optional OSC feedback listener on port 11118.

## Reference

- [Mixxx OSC Protocol](https://mixxx.org/manual/latest/chapters/osc.html)
- [python-osc](https://pypi.org/project/python-osc/)
- [FastMCP 3.4 Docs](https://github.com/jlowin/fastmcp)
- [Fleet Tauri Standard](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/rules/tauri_nsis_building.md)
- [SOTA Webapp Standard](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/WEBAPP_SOTA_STANDARDS.md)
