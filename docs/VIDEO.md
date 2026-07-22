# Video Features

Video support requires the **mixxxxx** fork of Mixxx — a video-enabled build based on Mixxx 2.5.6 that adds FFmpeg-based video playback alongside the standard audio engine.

## Mixxxxx Repository

https://github.com/sandraschi/mixxxxx

This fork adds:
- FFmpeg-based video decoding for MP4, MOV, AVI, MKV
- Video preview in the GUI (per-deck video widgets)
- Fullscreen projector output to a second monitor
- Video skins with embedded preview panels
- A/V sync engine (keeps video frame-accurate with audio)
- Video transition effects between decks

## MCP Video Operations

Two OSC addresses control video per deck:

```
video_enable       →  /deck/[N]/video_enabled     (bool)
video_fullscreen   →  /deck/[N]/video_fullscreen   (bool)
```

Both are exposed via `mixx_deck`:

```python
mixx_deck(operation="video_enable", deck=1, enable=True)
mixx_deck(operation="video_fullscreen", deck=1, enable=True)
```

## Video Skins

Use `mixx_skin` to create a video-ready skin:

```python
mixx_skin(operation="create_video_skin")
```

This clones the LateNight skin and adds VideoWidget entries for video preview and projector controls. Select the skin in Mixxx Preferences → Interface → Skin → "latenight-video" and restart.

## A/V Sync

The mixxxxx fork uses FFmpeg's frame-accurate decoding to keep video in sync with Mixxx's audio engine. Key points:
- Video follows the deck's play/pause, rate, and seek state
- Scrubbing updates the video frame at the scrub position
- Loops maintain A/V sync on loop boundaries
- Fullscreen output runs on a separate thread from the GUI

## VFX Pipeline (Planned)

Future integration with `vfx-mcp` will add:
- Real-time video effects (glitch, color grading, overlays)
- Visual transitions between deck video outputs
- Text/title overlays for live streaming
- MIDI-controlled video parameters

## Projector Output

The fullscreen video output sends to whatever display Mixxx designates as the fullscreen target. Typical setup:
- Laptop screen: Mixxx GUI with deck controls
- External monitor/projector: Fullscreen video output
- Audio: Main mix to speakers

## Build Instructions

See `projects/mixxxxx/README.md` in `mcp-central-docs` for build instructions. Requires:
- FFmpeg 6.0+ development libraries
- Qt 5.15+ or Qt 6.5+
- CMake 3.20+
- Windows: MSVC 2022 Build Tools
