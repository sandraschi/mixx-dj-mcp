# Tool Reference

80+ MCP operations across 12 portmanteaux + 3 Prefab UI card tools.

All tools return:
```json
{"success": bool, "message": "Human-readable summary", "data": {...}}
```

---

## 1. mixx_deck (19 ops)

Full deck control for all 4 decks. Requires `deck` (1-4).

```
play_pause       Toggle play/pause
stop             Stop playback
load             Load track to deck (requires track_path)
cue_set          Set cue point at current position
cue_play         Play from cue point
loop_activate    Toggle loop on/off (requires enable)
loop_beat        Set beat loop of N beats (requires beats)
beatloop         Alias for loop_beat
rate_set         Set playback rate, -1.0 to 1.0 (requires value)
rate_temp        Temporary pitch bend in seconds (requires value)
sync_enable      Toggle sync lock (requires enable)
sync_leader      Set deck as sync leader (requires enable)
seek             Seek to position in seconds (requires value)
scratch          Enable/disable scratch mode (requires enable)
hotcue_activate  Activate hotcue by number 1-8 (requires hotcue)
quantize         Toggle quantize mode (requires enable)
keylock          Toggle keylock (requires enable)
video_enable     Toggle video playback (requires enable, needs mixxxxx)
video_fullscreen Toggle video fullscreen (requires enable, needs mixxxxx)
```

### Parameters

| Param | Type | Required For |
|-------|------|-------------|
| `deck` | int (1-4) | All |
| `value` | float | rate_set, rate_temp, seek |
| `track_path` | str | load |
| `beats` | int | loop_beat, beatloop |
| `hotcue` | int (1-8) | hotcue_activate |
| `enable` | bool | loop_activate, sync_enable, sync_leader, scratch, quantize, keylock, video_enable, video_fullscreen |

### Examples

```python
mixx_deck(operation="play_pause", deck=1)
mixx_deck(operation="load", deck=2, track_path="C:/Music/track.mp3")
mixx_deck(operation="rate_set", deck=1, value=0.05)
mixx_deck(operation="loop_beat", deck=1, beats=8)
mixx_deck(operation="sync_enable", deck=2, enable=True)
mixx_deck(operation="hotcue_activate", deck=1, hotcue=3)
mixx_deck(operation="video_enable", deck=1, enable=True)
```

---

## 2. mixx_library (8 ops)

Library search and track metadata.

```
search           Search library by query string
browse_crate     Browse tracks in a crate (requires crate)
browse_playlist  Browse tracks in a playlist (requires playlist)
load_selected    Load currently selected track to deck
get_track_info   Get metadata for track on deck
get_bpm          Get BPM of track on deck
get_key          Get musical key of track on deck
get_replay_gain  Get replay gain values for track on deck
```

### Parameters

| Param | Type | Required For |
|-------|------|-------------|
| `query` | str | search |
| `crate` | str | browse_crate |
| `playlist` | str | browse_playlist |
| `deck` | int | load_selected, get_track_info, get_bpm, get_key, get_replay_gain |
| `track_index` | int | — |

### Examples

```python
mixx_library(operation="search", query="Daft Punk")
mixx_library(operation="browse_crate", crate="Peak Time")
mixx_library(operation="load_selected", deck=1)
mixx_library(operation="get_bpm", deck=1)
```

---

## 3. mixx_effects (7 ops)

Effect chain and parameter control.

```
list_effects    List available effects for rack/unit
chain_load      Load an effect chain by name (requires effect)
chain_clear     Clear the effect chain
parameter_set   Set effect parameter (requires parameter, value)
meta_set        Set meta/param knob (requires value, 0.0-1.0)
quick_effect_set Set quick effect for deck (requires deck, effect)
effect_enable   Enable/disable effect unit (requires enable)
```

### Parameters

| Param | Type | Default | Required For |
|-------|------|---------|-------------|
| `rack` | int | 1 | All |
| `unit` | int | 1 | All |
| `effect` | str | — | chain_load, quick_effect_set |
| `parameter` | int | 1 | parameter_set |
| `value` | float | — | parameter_set, meta_set |
| `deck` | int | — | quick_effect_set |
| `enable` | bool | true | effect_enable |

### Examples

```python
mixx_effects(operation="chain_load", rack=1, unit=1, effect="Flanger")
mixx_effects(operation="parameter_set", rack=1, unit=1, parameter=2, value=0.75)
mixx_effects(operation="effect_enable", rack=1, unit=1, enable=True)
mixx_effects(operation="quick_effect_set", deck=1, effect="Reverb")
```

---

## 4. mixx_mixer (8 ops)

Mixer channel and crossfader control.

```
crossfader_set    Set crossfader position (requires value, -1.0 to 1.0)
crossfader_curve  Set crossfader curve (requires value, 0.0-1.0)
gain_set          Set deck pregain (requires value, 0.0-5.0)
eq_set            Set EQ band: high/mid/low (requires eq_band, value)
volume_set        Set channel volume (requires value, 0.0-1.0)
headphone_cue     Toggle headphone cue (requires enable)
talkover          Toggle talkover
mic_gain          Set microphone gain (requires value, 0.0-1.0)
```

### Parameters

| Param | Type | Required For |
|-------|------|-------------|
| `deck` | int | gain_set, eq_set, volume_set, headphone_cue |
| `value` | float | crossfader_set, crossfader_curve, gain_set, eq_set, volume_set, mic_gain |
| `eq_band` | "high"\|"mid"\|"low" | eq_set |
| `enable` | bool | headphone_cue, talkover |

### Examples

```python
mixx_mixer(operation="crossfader_set", value=0.0)
mixx_mixer(operation="gain_set", deck=1, value=0.85)
mixx_mixer(operation="eq_set", deck=1, eq_band="low", value=0.5)
mixx_mixer(operation="headphone_cue", deck=1, enable=True)
mixx_mixer(operation="talkover", enable=True)
```

---

## 5. mixx_crate (5 ops)

Smart crate management via natural language.

```
create          Create crate from natural language prompt (requires name, prompt)
list            List all crates
delete          Delete a crate (not available via OSC)
add_track       Add current deck track to crate (requires name, deck)
create_agentic  Create LLM-curated crate with rule (requires name, rule)
```

### Parameters

| Param | Type | Default | Required For |
|-------|------|---------|-------------|
| `name` | str | — | create, delete, add_track, create_agentic |
| `prompt` | str | — | create |
| `rule` | str | — | create_agentic (e.g. "126-132 BPM, Dm or Em, 4+ stars") |
| `deck` | int | 1 | add_track |
| `max_tracks` | int | 50 | create_agentic |
| `update` | "manual"\|"auto" | "manual" | create_agentic |

### Examples

```python
mixx_crate(operation="create", name="Peak Time", prompt="tech house 124-128 BPM D minor")
mixx_crate(operation="list")
mixx_crate(operation="add_track", name="Favorites", deck=1)
mixx_crate(operation="create_agentic", name="Morning Warmup", rule="126-132 BPM, Dm or Em, genre:tech house")
```

---

## 6. mixx_stems (6 ops)

Demucs stem separation and sampler control.

```
separate    Run Demucs stem separation (requires output_dir)
status      Check Demucs availability + sampler slot assignments
load_stems  Load separated stems to Mixxx sampler decks
transition  Stem-aware crossfade — drops vocals from deck A
mute        Mute/unmute a sampler (requires enable)
volume      Set sampler volume (requires value, 0.0-1.0)
```

### Parameters

| Param | Type | Default | Required For |
|-------|------|---------|-------------|
| `deck` | int | 1 | separate, load_stems |
| `sampler` | int | 1 | mute, volume |
| `stem` | str | "vocals" | mute |
| `output_dir` | str | — | separate |
| `enable` | bool | — | mute |
| `value` | float | — | volume |

### Examples

```python
mixx_stems(operation="separate", deck=1, output_dir="C:/stems/out")
mixx_stems(operation="status")
mixx_stems(operation="mute", sampler=1, enable=True)
mixx_stems(operation="volume", sampler=2, value=0.5)
mixx_stems(operation="transition", deck_a=1, deck_b=2)
```

**Note:** Demucs is optional (`uv add demucs`). Without it, only status, mute, and volume work.

---

## 7. mixx_transition (3 ops)

AI-powered transitions between decks.

```
suggest          Ask LLM to suggest best transition for loaded tracks
apply            Apply a specific transition effect
auto_crossfader  Enable/disable AI-assisted crossfader
```

### Parameters

| Param | Type | Default | Required For |
|-------|------|---------|-------------|
| `deck_a` | int | 1 | suggest, apply |
| `deck_b` | int | 2 | suggest, apply |
| `style` | str | "any" | suggest |
| `effect` | str | — | apply |
| `duration_beats` | int | 8 | apply |
| `enable` | bool | — | auto_crossfader |

### Available Effects

| Effect | Description |
|--------|-------------|
| `echo_out` | Progressive echo/delay on outgoing track |
| `filter_sweep` | Low-pass on outgoing, high-pass on incoming |
| `stem_swap` | Drop vocals from A, bring instrumental of B |
| `hard_cut` | Instant switch, club style |
| `spin_back` | Outgoing spins down like vinyl brake |
| `flanger` | Flanger sweep across both decks |
| `reverb_kill` | Reverb + delay on outgoing, then kill |
| `long_blend` | Slow EQ fade over 16-32 bars |

### Examples

```python
mixx_transition(operation="suggest", deck_a=1, deck_b=2)
mixx_transition(operation="apply", deck_a=1, deck_b=2, effect="filter_sweep")
mixx_transition(operation="auto_crossfader", enable=True)
```

---

## 8. mixx_set (3 ops)

AI-assisted set planning and recording.

```
sequence     Generate optimized track order from crate via Ollama
record       Start/stop session recording via OSC
analyze_set  Analyze recorded session for BPM transitions, energy
```

### Parameters

| Param | Type | Default | Required For |
|-------|------|---------|-------------|
| `crate` | str | — | sequence |
| `name` | str | — | sequence (playlist name) |
| `energy_curve` | str | "build_peak_cooldown" | sequence |
| `analyze_type` | str | "recording" | analyze_set |

### Examples

```python
mixx_set(operation="sequence", crate="Peak Time", name="Friday Gig")
mixx_set(operation="record")
mixx_set(operation="analyze_set", name="Last Saturday")
```

**Note:** `sequence` requires Ollama (`http://localhost:11434`) with `llama3.2:3b`. Falls back to BPM-sorted order.

---

## 9. mixx_skin (7 ops)

Skin browser, installer, and AI skin generator.

```
list               List all available skins from curated manifest
search             Search skins by name, author, or tag
install            Install a skin (bundled or from source)
uninstall          Remove an installed skin (requires skin_id)
preview            Show skin details (requires skin_id)
create_video_skin  Clone LateNight + add VideoWidget for video DJing
create_skin        Generate new skin via inkscape-mcp recolor (requires name, prompt)
```

### Parameters

| Param | Type | Default | Required For |
|-------|------|---------|-------------|
| `skin_id` | str | — | install, uninstall, preview |
| `query` | str | — | search |
| `tags` | str | — | search (comma-separated) |
| `name` | str | — | create_skin |
| `prompt` | str | — | create_skin |
| `base_skin` | str | "latenight" | create_skin |

### Examples

```python
mixx_skin(operation="list")
mixx_skin(operation="search", tags="video-ready,dark")
mixx_skin(operation="install", skin_id="tara")
mixx_skin(operation="create_video_skin")
mixx_skin(operation="create_skin", name="cyberpunk", prompt="dark purple with cyan accents, neon waveform")
```

---

## 10. mixx_vinyl (5 ops)

Vinyl record catalog, search, and Plex cross-reference.

```
catalog    Run OCR pipeline on vinyl photos (requires directory)
search     Search vinyl DB by query, genre, era
gig_pick   AI-powered record selection for a gig (requires query)
crossref   Find digital copy in Plex (requires vinyl_id)
stats      Collection summary with genre/era/mood distribution
```

### Parameters

| Param | Type | Default | Required For |
|-------|------|---------|-------------|
| `directory` | str | — | catalog |
| `query` | str | "" | search, gig_pick |
| `genre` | str | — | search |
| `era` | str | — | search |
| `limit` | int | 20 | search |
| `vinyl_id` | int | — | crossref |
| `count` | int | 5 | gig_pick |

### Examples

```python
mixx_vinyl(operation="catalog", directory="D:/Vinyl/inbox")
mixx_vinyl(operation="search", query="techno")
mixx_vinyl(operation="gig_pick", query="dark warehouse techno set", count=5)
mixx_vinyl(operation="crossref", vinyl_id=1)
mixx_vinyl(operation="stats")
```

---

## 11. mixx_controller (5 ops)

DJ controller auto-detection and mapping management.

```
detect   Scan USB for connected DJ controllers (100+ in DB)
install  Install a Mixxx mapping for a detected controller
list     List installed Mixxx controller mappings
status   Show current controller configuration
download Download community mappings from GitHub
```

### Parameters

| Param | Type | Required For |
|-------|------|-------------|
| `mapping_name` | str | install |
| `vid` | int | — |
| `pid` | int | — |

### Supported Controller Brands

Pioneer, Denon, Numark, Hercules, Reloop, Behringer, Allen & Heath, Native Instruments (Traktor) — 40+ models built into the detection database.

### Examples

```python
mixx_controller(operation="detect")
mixx_controller(operation="list")
mixx_controller(operation="install", mapping_name="Pioneer-DDJ-400")
mixx_controller(operation="status")
```

---

## 12. mixx_daw (4 ops)

DAW cross-connection — export stems/sessions to Fairlight and Reaper.

```
export_stems        Copy stem WAVs to a DAW project directory
export_session      Write session metadata JSON for DAW import
send_to_fairlight   Send stems to DaVinci Resolve Fairlight via REST
send_to_reaper      Send stems to Reaper via reaper-mcp REST API
```

### Parameters

| Param | Type | Required For |
|-------|------|-------------|
| `source_dir` | str | export_stems, send_to_fairlight, send_to_reaper |
| `output_dir` | str | export_stems, export_session |
| `session_name` | str | export_session, send_to_fairlight |
| `target_bpm` | float | export_session |

### Examples

```python
mixx_daw(operation="export_stems", output_dir="D:/Projects/Gig/Stems")
mixx_daw(operation="export_session", session_name="Friday Gig")
mixx_daw(operation="send_to_fairlight", source_dir="D:/Stems", session_name="Friday Gig")
mixx_daw(operation="send_to_reaper", source_dir="D:/Stems")
```

---

## Prefab UI Cards (3 tools)

Rich in-chat cards for deck, mixer, and library status.

```python
show_deck_status_card(deck=1)      # Play state, BPM, key, volume, loop, sync
show_mixer_status_card()           # Crossfader, per-deck gain/volume/play state
show_library_status_card()         # Osc connection status, ports
```

All three return `ToolResult` with `content` (plain text) and `structured_content` (PrefabApp). Use via FastMCP 3.4+ clients that support MCP Apps.
