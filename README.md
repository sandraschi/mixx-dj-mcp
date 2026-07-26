<div align="center">
  <br/>
  <h1>Mixx-DJ-MCP</h1>
  <p><strong>AI-native DJ control for Mixxx.</strong> 80+ operations across decks, library, effects, mixer, stems, transitions, video, and more. Talk to your DJ software like a colleague.</p>
  <br/>

[![GitHub stars](https://img.shields.io/github/stars/sandraschi/mixx-dj-mcp?style=flat-square&logo=github)](https://github.com/sandraschi/mixx-dj-mcp)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.4-purple?style=flat-square)](https://github.com/jlowin/fastmcp)
[![Mixxx](https://img.shields.io/badge/Mixxx-2.5-orange?style=flat-square)](https://mixxx.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=white)](https://react.dev)
[![Tauri](https://img.shields.io/badge/Tauri-2.0-FFC131?style=flat-square&logo=tauri&logoColor=white)](https://tauri.app)
[![NSIS](https://img.shields.io/badge/NSIS-installer-0095D9?style=flat-square)](https://nsis.sourceforge.io)

  <br/>
  <b>Say:</b> <i>"Load Daft Punk on deck 2, sync it, cue the drop, then fade in on the next beat."</i>
  <br/>
  <b>It happens.</b>
  <br/><br/>

  <img src="docs/screenshots/cockpit.png" alt="Mixx-DJ-MCP Cockpit" width="800"/>

  <br/>
  <sub>
  <a href="docs/INSTALL.md">Install</a> ·
  <a href="docs/TOOLS.md">Tools</a> ·
  <a href="docs/STATUS.md">Status</a> ·
  <a href="docs/ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/MIXXX_VIDEO.md">Video</a> ·
  <a href="docs/NDI.md">NDI</a> ·
  <a href="docs/NOOB_GUIDE.md">Beginner Guide</a> ·
  <a href="docs/AI_TRANSITIONS.md">AI Transitions</a>
  </sub>
</div>

<br/>

## One command to start

```bash
uv sync && uv run uvicorn mixx_dj_mcp.server:app --port 11116
```

Configure Mixxx OSC once (one minute): **Preferences > MIDI/OSC > Enable OSC**, set out `11118`, in `11119`, send to `127.0.0.1`, restart. Done.

Your AI assistant (Claude, Cursor, opencode) can now control your decks.

## What it does

| You say | The AI does |
|---------|-------------|
| "Play deck 2" | `mixx_deck(operation="play_pause", deck=2)` — OSC to Mixxx |
| "Find some 128 BPM tech house" | `mixx_library(operation="search", query="tech house")` |
| "Add reverb to the outgoing track" | `mixx_effects(operation="chain_load", rack=1, effect="Reverb")` |
| "Plan a 30-min drum & bass set" | `mixx_ai_set(operation="plan", style="drum and bass")` |
| "Record this set" | `mixx_recording(operation="start")` |
| "Analyse this track's key" | `mixx_analyze(operation="track", path="C:/Music/track.mp3")` |
| "Show me my most-played tracks" | `mixx_history(operation="profile")` |
| "Transition with an echo out" | `mixx_transition(operation="apply", effect="echo_out")` |

## Tools at a glance

| Tool | What it controls |
|------|-----------------|
| `mixx_deck` | Play/pause, load, cue, loops, sync, rate, scratch, hotcues, quantize, keylock — plus video |
| `mixx_library` | Search, browse crates/playlists, BPM/key metadata |
| `mixx_effects` | Effect chains, parameters, quick effects, super knob |
| `mixx_mixer` | Crossfader, EQ, gain, headphone cue, talkover, mic |
| `mixx_analyze` | BPM detection, musical key (Krumhansl-Schmuckler), energy, cue suggestions |
| `mixx_stems` | Demucs stem separation, sampler loading, stem-aware mixing |
| `mixx_transition` | AI-suggested transitions, 8 effect types, auto-crossfader |
| `mixx_ai_set` | **Autonomous DJ** — plan sets, perform transitions, review |
| `mixx_recording` | Record, replay, and export DJ sets as OSC streams |
| `mixx_history` | Play history, style profile, track suggestions |
| `mixx_crate` | LLM-generated smart crates by BPM/key/genre |
| `mixx_set` | Harmonic mixing sequences, energy curve planning |
| `mixx_skin` | List, apply, create video skins, AI palette generation |
| `mixx_vinyl` | OCR catalog, AI gig picker, Plex crossref |
| `mixx_controller` | USB auto-detect, install mappings |
| `mixx_daw` | Export stems to DaVinci Resolve, Reaper |
| Prefab cards | `show_deck/mixer/library_status_card` — rich in-chat UI |

## Quick links

| For... | Read |
|--------|------|
| **Installing** the server, webapp, NSIS installer, or MCPB | [`docs/INSTALL.md`](docs/INSTALL.md) |
| **Status & backlog** | [`docs/STATUS.md`](docs/STATUS.md) · [`docs/TODO.md`](docs/TODO.md) |
| **Full tool reference** with parameters, returns, and examples | [`docs/TOOLS.md`](docs/TOOLS.md) |
| **Using video** — requires the mixxxxx fork of Mixxx | [`docs/MIXXX_VIDEO.md`](docs/MIXXX_VIDEO.md) |
| **NDI** (planned network video — primer) | [`docs/NDI.md`](docs/NDI.md) · webapp **Help → NDI** |
| **Project status & backlog** | [`docs/STATUS.md`](docs/STATUS.md) · [`docs/TODO.md`](docs/TODO.md) |
| **AI-powered transitions** between decks | [`docs/AI_TRANSITIONS.md`](docs/AI_TRANSITIONS.md) |
| **Architecture** — how the OSC bridge, REST API, and webapp work | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| **Beginner's guide** to DJing with Mixxx | [`docs/NOOB_GUIDE.md`](docs/NOOB_GUIDE.md) |
| **Comparing** Mixxx to other DJ software | [`docs/DJ_LANDSCAPE.md`](docs/DJ_LANDSCAPE.md) |
| **Algoriddim djay** feature parity | [`docs/ALGORIDDIM_COMPARISON.md`](docs/ALGORIDDIM_COMPARISON.md) |
| **Mixxx OSC setup** and address reference | [`bridge/README.md`](bridge/README.md) |

## Video DJing

Mixx-DJ-MCP supports the **mixxxxx** video fork — a modified Mixxx build that adds FFmpeg video playback, per-deck video widgets, and fullscreen projector output alongside the standard audio engine.

[mixxxxx on GitHub](https://github.com/sandraschi/mixxxxx) &nbsp;·&nbsp; [`docs/MIXXX_VIDEO.md`](docs/MIXXX_VIDEO.md)

## Ports

| Port | What |
|------|------|
| **11116** | Backend REST API + MCP transport |
| **11117** | React webapp (Vite) |
| **11118** | OSC feedback from Mixxx |
| **11119** | OSC commands to Mixxx |

## Fleet integrations

Mixx-DJ-MCP is a **Fleet Audio Hub** — it connects to other MCP servers for a unified DJ ecosystem:

| Server | Integration |
|--------|-------------|
| `plex-mcp` | Cross-reference vinyl with digital library |
| `songgeneration-mcp` | AI music generation loaded direct to decks |
| `sfx-mcp` | Sound effects triggered during live sets |
| `vfx-mcp` | Real-time video effects on video output |
| `stems-mcp` | External stem separation engine |
| `davinci-resolve-mcp` | Export stems to Fairlight for post-production |
| `reaper-mcp` | Export stems to Reaper DAW |
| `inkscape-mcp` | AI skin colour palette generation |
| `speech-mcp` | Voice-controlled DJing ("Hey Mixxx, load deck 2...") |

## License

MIT — Sandra Schipal

_Vinyl not included. Mixxx not included. Bad music taste is your own._