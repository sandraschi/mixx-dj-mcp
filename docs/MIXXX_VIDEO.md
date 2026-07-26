# Video DJing with mixxxxx

> **mixxxxx** is Sandra's video-enabled fork of Mixxx 2.5.6. It adds FFmpeg-based video playback, per-deck video widgets, and fullscreen projector output alongside the standard audio engine. No second app, no external video mixer — everything runs inside Mixxx.

**Repository**: [github.com/sandraschi/mixxxxx](https://github.com/sandraschi/mixxxxx)

---

## What mixxxxx adds

| Feature | What it does |
|---------|-------------|
| **Per-deck video** | Each deck gets a video widget showing the current track's video file |
| **FFmpeg decoding** | MP4, MOV, AVI, MKV — any format FFmpeg supports |
| **Fullscreen projector** | Second monitor output for club/stream use |
| **A/V sync** | Frame-accurate sync via FFmpeg timestamps tied to Mixxx's audio engine |
| **Video skins** | Built-in LateNight variant with VideoWidget panels |
| **Video transitions** | Crossfader blends video between decks |
| **Seek sync** | Scrubbing updates the video frame at the exact position |
| **Loop sync** | A/V stays in sync across loop boundaries |
| **Rate sync** | Pitch-shifted video follows tempo changes |

### What it does not do (yet)

- No real-time video effects (glitch, chroma key, overlays) — planned via `vfx-mcp`
- No separate video mixer — video follows audio crossfader
- No recording/mixing of video output to file
- **No NDI network output** — planned ([`docs/NDI.md`](NDI.md) · mixxxxx [`docs/NDI.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/NDI.md))

---

## Quick start

### 1. Get mixxxxx

```bash
git clone https://github.com/sandraschi/mixxxxx.git
cd mixxxxx
```

### 2. Build (Windows)

```powershell
# Prerequisites: MSVC 2022 Build Tools, CMake 3.20+, Qt 6.5+, FFmpeg 6.0+
cmake -S . -B build -G "Visual Studio 17 2022" -DCMAKE_PREFIX_PATH="C:\Qt\6.5.0\msvc2022_64"
cmake --build build --config Release
```

Or grab a prebuilt release from the [Releases page](https://github.com/sandraschi/mixxxxx/releases).

### 3. Configure OSC

Same as regular Mixxx: **Preferences > MIDI/OSC > Enable OSC**, out `11118`, in `11119`.

### 4. Load video tracks

mixxxxx treats video files as first-class media. Load an MP4/MOV/MKV the same way you'd load an audio file. The video widget shows the picture; audio plays through Mixxx's engine.

---

## MCP video controls

Two OSC addresses control video per deck, both exposed via `mixx_deck`:

```python
# Enable video on deck 1 (shows video widget)
mixx_deck(operation="video_enable", deck=1, enable=True)

# Toggle fullscreen projector on deck 2
mixx_deck(operation="video_fullscreen", deck=2, enable=True)
```

The [Cockpit webapp](../web_sota/src/pages/Cockpit.tsx) detects whether mixxxxx is running by probing `/api/v1/fork`:

```json
{
  "fork": "mixxxxx",
  "features": {
    "video": true,
    "phase_indicator": true,
    "rekordbox_export": true,
    "serato_export": true,
    "virtualdj_export": true
  }
}
```

Vanilla Mixxx returns `"fork": "mixxx"` — video controls are still available but will have no effect.

---

## Video skins

mixxxxx ships **`MixxxxxVideo`** in the repo (`res/skins/MixxxxxVideo/`) — a LateNight
derivative with video preview/output default on and a **Daylight** colour scheme.
Community skins: mixxxxx [`docs/SKINS.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/SKINS.md).

Use `mixx_skin` to install into your user folder:

```python
mixx_skin(operation="create_video_skin")
```

This copies the shipped bundle, patches `skin.xml` (video on, spinnies/cover off,
4 decks), and ensures the video output panel is wired. Select **Mixxxxx Video** in
**Preferences → Interface → Skin** (`Ctrl+P` — not the top-right gear, which is skin
layout only).

### What the video skin includes

- **Deck video preview** — per-deck widget when companion file exists
- **Master video output panel** — crossfader-blended output (hidden on stock LateNight)
- **Projector / fullscreen** — `video_fullscreen` CO or MCP
- **Daylight scheme** — light QSS variant for bright rooms

---

## NDI (planned)

**NDI** sends live video over your LAN so OBS, Resolume, or vMix can subscribe without
HDMI capture. Not in the build yet.

| Where to read | Link |
|---|---|
| Full primer | mixxxxx [`docs/NDI.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/NDI.md) |
| Short pointer | [`docs/NDI.md`](NDI.md) |
| In-app | Webapp **Help → NDI** tab |

Recommended build order before NDI: beat-locked video FX → video fallback chain → NDI
(mixxxxx `docs/IDEAS.md`).

Older docs referred to `latenight-video` from a clone-only workflow — prefer
**MixxxxxVideo** + `create_video_skin` above.

---

## Projector setup

Typical dual-display configuration:

```
Laptop screen              Projector / external monitor
┌─────────────────┐        ┌──────────────────────────┐
│ Mixxx GUI       │        │ Fullscreen video output  │
│ Deck controls   │        │                          │
│ Video preview   │        │ No UI overlays           │
│ Library browser │        │ Pure video               │
│ Oscilloscope    │        │                          │
└─────────────────┘        └──────────────────────────┘
```

1. Connect external monitor/projector
2. In Mixxx Preferences, set fullscreen target to the external display
3. Click the fullscreen button on any deck (or send via MCP)
4. Video plays fullscreen on the projector; GUI stays on your laptop

---

## VFX pipeline (planned)

Future integration with `vfx-mcp` (fleet video effects server, port 11122) will add:

| Effect | What it does |
|--------|-------------|
| **Glitch** | Bit-crush, datamosh, frame-repeat |
| **Colour grade** | LUTs, HSL curves, colour space transforms |
| **Overlays** | Text, logo, camera inset for streaming |
| **Transitions** | Wipe, cross-zoom, page-peel between deck videos |
| **Audio-reactive** | Bass-drop flash, beat-sync stutter, energy-based saturation |

The VFX pipeline will sit between mixxxxx's video output and the projector:

```
Mixx-DJ-MCP (deck control)
  │
  ├── OSC → mixxxxx (video playback + sync)
  │
  └── REST → vfx-mcp (effects processing)
                │
                └── FFmpeg filter graph → projector output
```

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Video widget shows black | Video file not found or codec unsupported | Check file path, try H.264 MP4 |
| A/V out of sync | CPU overload or FFmpeg thread contention | Lower video decode thread count, close other GPU apps |
| Fullscreen shows desktop | Wrong display target | Check Preferences > Fullscreen output |
| MCP says "mixxx" not "mixxxxx" | Running vanilla Mixxx | Build and launch mixxxxx instead |
| `video_enable` has no effect | Mixxx skin has no VideoWidget | Use `mixx_skin(create_video_skin)` or switch to latenight-video |
| Video stutters on loop | Loop boundary + keyframe misalignment | Use shorter loops or higher keyframe-rate videos |

---

## Build requirements

| Dependency | Version | Notes |
|-----------|---------|-------|
| FFmpeg | 6.0+ | Shared libraries with `avformat`, `avcodec`, `avutil`, `swscale` |
| Qt | 5.15+ or 6.5+ | Qt Multimedia recommended for audio backend |
| CMake | 3.20+ | Generator: Visual Studio 17 2022 |
| MSVC | 2022 | Build Tools or full Visual Studio |
| Python | 3.12+ | For the MCP server, not mixxxxx itself |

Full build guide: [`projects/mixxxxx/README.md`](https://github.com/sandraschi/mixxxxx/blob/main/README.md)

---

## See also

- [`docs/STATUS.md`](STATUS.md) — mixx-dj-mcp + mixxxxx integration status
- [`docs/TODO.md`](TODO.md) — backlog
- [`docs/NDI.md`](NDI.md) — NDI pointer (planned)
- [`docs/VIDEO.md`](../docs/VIDEO.md) — original video notes (legacy)
- [`docs/AI_TRANSITIONS.md`](../docs/AI_TRANSITIONS.md) — audio transitions that work with video
- [`docs/INSTALL.md`](../docs/INSTALL.md) — full server installation
- Webapp **Help** (`/help`) — Overview, NDI, Video, Skins, OSC
- [`mcp-central-docs/projects/mixxxxx/`](https://github.com/sandraschi/mcp-central-docs/projects/mixxxxx/) — fleet project page
