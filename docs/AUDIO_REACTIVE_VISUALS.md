# Audio-Reactive Visuals — Resolume Bridge

**Spec v0.1** — 2026-07-22

## Concept

When a DJ plays a track in mixxxxx, the visuals in Resolume automatically dance to the beat — color pulses with the kick drum, patterns rotate at the BPM, effects trigger on phrase changes. No manual MIDI mapping. No configuration. Plug in and the visuals follow the music.

## Architecture

```
mixxxxx deck → OSC → mixx-dj-mcp → audio feature extraction → Resolume OSC (port 7000)
                                    │
                                    └── /composition/tempo     = BPM
                                        /composition/bpm       = BPM
                                        /layer1/opacity        = volume envelope
                                        /layer1/effect1/param1 = bass energy
                                        /layer1/effect1/param2 = mid energy  
                                        /layer1/effect1/param3 = high energy
                                        /layer2/opacity        = beat phase (pulse)
```

## What We Can Read from Mixxx OSC

| Bridge state | What it tells us | Resolume mapping |
|-------------|------------------|-----------------|
| `bpm` | Tempo | `/composition/tempo` |
| `play` | Playing/paused | Layer visibility toggle |
| `volume` | Overall energy | Layer opacity |
| `pregain` | Amplitude | Effect intensity |
| `track_samples` + `track_samplerate` | Beat phase approximation | `/layer{N}/clip{N}/video/position` |
| `filterHigh/Mid/Low` | EQ state (user's hands) | Effect color/parameter |

## What We Compute

```python
def compute_audio_features(bridge, deck) -> dict:
    bpm = bridge.get_state("bpm", deck, 128.0)
    play = bridge.get_state("play", deck, 0.0)
    volume = bridge.get_state("volume", deck, 0.8)
    pregain = bridge.get_state("pregain", deck, 1.0)
    samples = bridge.get_state("track_samples", deck, 0.0)
    sample_rate = bridge.get_state("track_samplerate", deck, 44100.0)
    
    # Beat phase: where we are in the current beat (0.0 - 1.0)
    beats_per_second = bpm / 60.0
    seconds = samples / sample_rate if sample_rate > 0 else 0
    total_beats = seconds * beats_per_second
    beat_phase = total_beats % 1.0  # 0.0 = downbeat, 0.5 = upbeat
    
    # Energy envelope: smoothed volume proxy
    energy = min(1.0, volume * pregain * 1.5)
    
    # Beat flash: sharp pulse on downbeat for strobe effects
    beat_flash = 1.0 if beat_phase < 0.05 else max(0.0, 1.0 - (beat_phase * 2))
    
    return {
        "bpm": bpm,
        "beat_phase": beat_phase,
        "energy": energy,
        "beat_flash": beat_flash,
        "playing": bool(play),
    }
```

## Resolume Mapping

The Resolume Arena composition template should have:
- **Layer 1**: Background visuals driven by energy + BPM (generative patterns)
- **Layer 2**: Beat-reactive overlays (strobe, flash, geometric shapes)
- **Layer 3**: Camera/clip input from mixxxxx video output
- **Master**: Tempo synced to `/composition/tempo`

## New MCP Tool: `mixx_visuals`

Extend `mixx_daw` with a new operation, or create a dedicated `mixx_visuals` tool:

```python
@mcp.tool()
async def mixx_visuals(
    operation: Literal["connect", "disconnect", "set_auto", "trigger_effect"],
    deck: int = 1,
    mode: str = "auto",     # auto, manual, off
    effect: str = "",       # strobe, pulse, color_cycle, wave, particles
    intensity: float = 0.5,  # 0.0 - 1.0
) -> dict:
```

### Operations

| Operation | What it does |
|-----------|-------------|
| `connect` | Start sending deck state → Resolume OSC at 30fps |
| `disconnect` | Stop sending |
| `set_auto` | Auto-detect best visual mode based on track energy |
| `trigger_effect` | Fire a one-shot visual effect (build drop, transition accent) |

### Visual Effects (trigger_effect)

| Effect | Description | OSC |
|--------|-------------|-----|
| `strobe` | Rapid flash on beat | `/layer2/opacity` oscillate 0↔1 |
| `pulse` | Throb on downbeat | `/layer1/scale` brief 1.0→1.15→1.0 |
| `color_cycle` | Hue shift per bar | `/layer1/effect1/param3` ramp 0→1 over 4 beats |
| `wave` | Ripple from center | `/layer1/effect2/param1` brief pulse |
| `particles` | Particle burst | `/layer3/opacity` brief 1.0 then decay |

## Visual Template

The Resolume `.avc` template file ships in `docs/resolume/MixxVisuals.avc` with:
- Pre-configured composition with 3 layers
- Layer effects mapped to OSC addresses
- BPM sync enabled on master
- Beat-reactive clip envelopes
- Audio FFT analysis as fallback when OSC is delayed

## Implementation Plan

| Step | What | Effort |
|------|------|--------|
| 1 | Extend `mixx_daw` with audio feature computation + continuous OSC loop | ~1 hour |
| 2 | Create Resolume template `.avc` file | ~2 hours (in Resolume) |
| 3 | Test: play a track in mixxxxx, watch Resolume dance | ~30 min |
| 4 | Add visual effects (strobe, pulse, color_cycle, wave, particles) | ~1 hour |
| 5 | Auto-mode: LLM picks visual style based on track genre/energy | ~30 min |

## Demo Prompt

```text
"Start the visuals, set them to auto, and when I drop the bass,
trigger a strobe effect on the downbeat."
```

This becomes:
```
mixx_visuals("connect", deck=1, mode="auto")
# ... crossfader moves ...
mixx_visuals("trigger_effect", effect="strobe", intensity=0.8)
```
