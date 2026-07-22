# Algoriddim djay — Feature Comparison

**Updated**: 2026-07-22
**Source**: https://www.algoriddim.com/djay-ios

## Overview

Algoriddim (Munich-based) makes djay, the #1 iOS DJ app. Winner of multiple Apple Design Awards. Also has macOS, Windows, Android, Vision Pro, and Meta Quest versions. Subscription-based ($6.99/mo or $49.99/yr).

## Feature Comparison

| Feature | djay (iOS) | mixx-dj-mcp + mixxxxx | Gap |
|---------|-----------|----------------------|-----|
| **Neural Mix™** — real-time AI stem separation | ✅ Real-time | ⏳ Pre-process (Demucs) | Real-time stems is the next big C++ piece |
| **Streaming** — Spotify, Apple Music, TIDAL, SoundCloud, Beatport | ✅ Built-in | ❌ None | Requires API licensing deals |
| **Crossfader Fusion™** — intelligent EQ/filter morphing | ✅ Proprietary | ✅ AI Transitions (LLM chooses) | Different approach; ours is more creative |
| **Fluid Beatgrid™** | ✅ | ✅ (Mixxx engine) | Parity |
| **Video mixing** | ✅ Video + audio-reactive visuals | ✅ Video playback + VFX | Audio-reactive VJ is missing |
| **Looper** — 48-slot grid sequencer | ✅ | ❌ No grid looper | Buildable via OSC + sampler decks |
| **MIDI controllers** | ~50 plug-and-play | ~40 via auto-detect | Near parity |
| **Content packs** — 1000+ loops/samples | ✅ Subscription | ✅ sfx-mcp (FreeSound, free) | Different model |
| **Hardware certification** | Pioneer, Reloop, Numark, Denon | Community mappings | Gap |
| **Cross-platform** | iOS, macOS, Windows, Android, Vision Pro, Quest | Windows only (mixxxxx) | Gap |
| **Price** | $6.99/mo sub + in-app purchases | Free (FOSS) | ✅ Win |
| **Open source** | ❌ | ✅ MIT | ✅ Win |
| **Video export / clip extraction** | ❌ | ✅ Via plex-mcp + vfx-mcp | ✅ Win |
| **Vinyl catalog** | ❌ | ✅ Via mixx_vinyl | ✅ Win |
| **Skin generator** | ❌ | ✅ Via inkscape-mcp | ✅ Win |
| **Controller auto-detect** | ✅ | ✅ Via mixx_controller | ✅ Win |
| **AI transition suggestions** | ❌ | ✅ Via mixx_transition | ✅ Win |
| **DAW export** | ❌ | ✅ Fairlight, Reaper, Resolume | ✅ Win |

## What to Filch (in priority order)

| Priority | Feature | Effort | Notes |
|----------|---------|--------|-------|
| P1 | **Grid looper** | 1 afternoon | Map 48 slots to sampler decks via OSC, build JS in mixx-dj-mcp |
| P2 | **Audio-reactive visuals** | 2-3 days | Connect BPM/beat to Resolume or write a simple GL visualizer in mixxxxx |
| P3 | **Real-time Neural Mix** | ~1 week | ONNX Runtime integration in mixxxxx (already spec'd) |
| P4 | **Streaming integration** | Unknown | Spotify/TIDAL require commercial API deals — probably not feasible for FOSS |
| P5 | **Android port** | Months | Mixxx already has an Android port in progress (#15679) |

## Verdict

For a 1-day project, mixxxxx + mixx-dj-mcp matches or beats djay on most DJ features. djay wins on **streaming** (Spotify deal) and **polish** (Apple Design Awards for a reason). mixxxxx wins on **openness**, **price** (free), **extensibility** (MCP), and **unique features** (AI transitions, vinyl catalog, controller auto-detect, DAW export).

The biggest gap: **real-time stems**. Algoriddim's Neural Mix is genuinely impressive — they run a lightweight model on-device (Apple Neural Engine) with sub-100ms latency. Our Demucs pipeline works but takes 30s. Closing that gap is the single highest-ROI C++ project for mixxxxx.
