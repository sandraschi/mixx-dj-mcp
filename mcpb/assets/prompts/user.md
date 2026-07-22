# Mixx-DJ-MCP User Guide

This guide teaches you how to use Mixx-DJ-MCP effectively. Whether you are a beginner learning to mix or an experienced DJ looking to automate Mixxx, this tutorial covers everything you need.

## Table of Contents

1. Getting Started
2. Basic DJ Operations
3. Beatmatching and Tempo Control
4. Mixing Techniques
5. Effects and Processing
6. Library Management
7. Recording Sessions
8. Advanced Techniques
9. Troubleshooting
10. Example Conversations

---

## 1. Getting Started

### Prerequisites
- **Mixxx 2.4+** installed and running on your machine (or a networked machine).
- **OSC enabled** in Mixxx: Go to Preferences > Controllers > Add New > Search for "OSC" and enable the OSC controller with default ports.
- **Python 3.12+** and `uv` installed for the MCP server.
- The Mixx-DJ-MCP server running: `uv run python -m mixx_dj_mcp.server`

### First Launch
When you start the MCP server, it attempts to establish an OSC connection to Mixxx. The server logs its connection status. Look for:

```
[info] Mixxx OSC bridge initialized (host: 127.0.0.1, out: 8000, in: 9000)
```

If you see a connection error, verify that:
1. Mixxx is running.
2. OSC controller is enabled in Mixxx.
3. The ports match your Mixxx configuration.

### Configuration
The server reads from environment variables:
- `MIXX_HOST` - Mixxx machine IP (default: 127.0.0.1).
- `MIXX_OSC_OUT_PORT` - Port Mixxx sends from (default: 8000).
- `MIXX_OSC_IN_PORT` - Port Mixxx receives on (default: 9000).

Set these in a `.env` file at the repo root or in your OS environment.

---

## 2. Basic DJ Operations

### Loading Tracks
To load a track onto a deck, you first need to find it in the library:

1. Search for tracks: `mixx_library(operation="search", query="Daft Punk")]
2. Select a track and note its ID.
3. Load to deck: `mixx_deck(operation="load", deck=1, track_id="<id>")`

### Playing and Pausing
- **Play**: `mixx_deck(operation="play_pause", deck=1)`
- **Stop**: `mixx_deck(operation="stop", deck=1)`
- The play/pause operation toggles: if playing, it pauses; if paused, it plays.

### Seeking
Jump to a specific position in the track:
- By seconds: `mixx_deck(operation="seek", deck=1, position=30)` (30 seconds in)
- By percentage: `mixx_deck(operation="seek", deck=1, position=0.25)` (25% through the track)

### Cue Points
Mixxx supports 8 hot cue points per deck:
- **Jump to cue**: `mixx_deck(operation="cue", deck=1, cue_point=1)`
- **Set cue**: `mixx_deck(operation="hot_cue_set", deck=1, cue_number=1)`
- **Clear cue**: `mixx_deck(operation="hot_cue_clear", deck=1, cue_number=1)`

Pro tip: Set cue points on breakdowns and drop points for quick navigation during your set.

### Volume Control
- **Deck volume**: `mixx_mixer(operation="volume", deck=1, value=0.8)`
- **Master volume**: `mixx_mixer(operation="master_volume", value=0.85)`
- **Headphone cue**: `mixx_mixer(operation="headphone", deck=1, enabled=true)`

Always maintain headroom. Keep master volume around 0.8 (-3dB) and adjust during the set as needed.

---

## 3. Beatmatching and Tempo Control

### Manual Beatmatching
The traditional DJ skill of matching tempos by ear:

1. Check BPM of both tracks:
   `mixx_library(operation="track_info", track_id="<id>")` - note the BPM of both tracks.
2. Listen to deck 2 in headphones (cue enabled).
3. Adjust tempo: `mixx_deck(operation="rate", deck=2, value=2.5)` - increase BPM by 2.5%.
4. Nudge to align beats: use beat jump for fine adjustment.
5. Fine-tune: adjust rate in 0.1% increments until perfectly matched.

### Using Sync
For quicker mixing, use Beat Sync:

1. Enable sync on the incoming deck:
   `mixx_deck(operation="sync", deck=2, enabled=true)`
2. Deck 2 will automatically match deck 1's BPM.
3. Use beat jump to align phase if needed.

Sync is great for quick transitions, but manual beatmatching is a fundamental skill worth learning.

### Key Sync
Match the musical key of both tracks for harmonic mixing:

`mixx_deck(operation="sync_key", deck=2, enabled=true)`

This enables keylock (preserves pitch when changing tempo) and syncs the musical key between decks.

### Tempo Ramping
For gradual tempo changes:

`mixx_deck(operation="rate_ramp", deck=1, target_rate=-5, duration=45)`

This slowly reduces the tempo by 5% over 45 seconds, perfect for end-of-set transitions.

---

## 4. Mixing Techniques

### The Basic Crossfader Transition
The simplest way to move between tracks:

1. Ensure beatmatching is solid.
2. Start deck 2 in headphones, confirm it is beatmatched.
3. Start playback on deck 2 at a phrase boundary.
4. `mixx_mixer(operation="crossfader", value=0.3)` - start moving toward deck 2.
5. `mixx_mixer(operation="crossfader", value=0.5)` - equal mix.
6. `mixx_mixer(operation="crossfader", value=1.0)` - fully on deck 2.

### EQ Sweep Transition
More musical than a raw crossfader:

1. Beatmatch both tracks.
2. On the outgoing deck, cut the lows:
   `mixx_mixer(operation="eq", deck=1, band="low", value=0.0)`
3. Start bringing the incoming track:
   `mixx_mixer(operation="eq", deck=2, band="low", value=1.0)`
   `mixx_mixer(operation="crossfader", value=0.7)`
4. Gradually cut mids/highs on deck 1 and bring them in on deck 2.
5. Complete the crossfader to deck 2.

### Phrase Mixing
The gold standard of DJ transitions - mixing at phrase boundaries:

1. Know that most electronic music phrases are 8, 16, or 32 bars.
2. At the start of a phrase (typically every 32 beats), start the incoming track.
3. Crossfade over 16-32 beats.
4. The outgoing track should reach a breakdown or drop as the incoming track builds.

Phrase mixing creates seamless transitions that musical dancers can follow. To identify phrase boundaries, listen for changes in the arrangement (hi-hat patterns, snare placement, melodic changes).

### Harmonic Mixing
Mixing tracks in compatible musical keys:

- **Camelot Wheel**: Adjacent keys mix well. E.g., 8A (F Minor) mixes with 8B (C Minor) or 9A (C Minor).
- **Energy boost**: Move clockwise on the Camelot wheel.
- **Energy drop**: Move counter-clockwise.

Use the library tool to check track keys:
`mixx_library(operation="track_info", track_id="<id>")` - check the `key` field.

### Loop Mixing
Extend sections by looping:

1. Find the section you want to extend (e.g., the intro of track 2).
2. Set a loop: `mixx_deck(operation="beat_loop", deck=2, beats=16)`
3. Start deck 2 at the right phrase and crossfade.
4. Turn off the loop when track 1 reaches its breakdown.
5. `mixx_deck(operation="reloop_toggle", deck=2)` - exit loop.

### Using Slip Mode
Slip mode allows you to cue, loop, and scratch while the track continues playing underneath. When you exit the slip operation, playback jumps to where the track would have been:

1. Enable slip: `mixx_deck(operation="slip_enable", deck=1)`
2. Drop a hot cue or loop while in slip mode.
3. Release the operation - the track continues seamlessly.
4. `mixx_deck(operation="slip_disable", deck=1)` - exit slip mode.

---

## 5. Effects and Processing

### Effect Chain Setup
Mixxx has a powerful effects engine with up to 4 effect units, each capable of chaining multiple effects:

1. List available effects:
   `mixx_effects(operation="list_effects")`
2. Load a chain unit:
   `mixx_effects(operation="chain_load", unit=1, chain="Reverb")`
3. Insert a specific effect:
   `mixx_effects(operation="chain_insert", unit=1, effect="BitCrusher")`
4. Enable the chain:
   `mixx_effects(operation="chain_enable", unit=1, enabled=true)`

### Parameter Control
Fine-tune effect parameters:

- Set parameter: `mixx_effects(operation="parameter_set", unit=1, index=0, value=0.5)`
- Get parameter: `mixx_effects(operation="parameter_get", unit=1, index=0)`
- Super combo: `mixx_effects(operation="super_combo", unit=1, value=0.7)`

Effect parameters range from 0.0 to 1.0. Parameter mapping depends on the specific effect. Common parameter 0 is the "dry/wet" mix for most effects.

### Popular Effect Combinations

**Build-Up**: Reverb + Delay + High-pass filter sweep
1. Load Reverb on unit 1, set decay to 0.7.
2. Load Delay on unit 2, set feedback to 0.4.
3. Use EQ to gradually kill lows and mids.
4. At the drop, kill all effects and bring back the full track.

**Filter Sweep Transition**: Low-pass + High-pass filter
1. Load "BiquadEqualizer" or similar filter effect.
2. Gradually reduce the filter cutoff on deck 1 (outgoing).
3. Bring in deck 2 with low cutoff, gradually opening.
4. Crossfade during the sweep.

**Beat Slicing / Glitch**
1. Load "BeatRepeat" effect on unit 1.
2. Set quantization to 1/4 or 1/8 notes.
3. Enable at key moments (fills, breakdown exits).

### Effects Best Practice
- Less is more. A subtle reverb or delay is usually better than a heavily processed sound.
- Use effects to emphasize musical moments (buildups, drops, breakdowns).
- Match effect timing to the BPM - use beat-synced effects when available.
- Always preview effects in headphones before sending to the master output.

---

## 6. Library Management

### Searching
Search by any metadata field:
`mixx_library(operation="search", query="artist:Todd Terje genre:House")`

You can filter by:
- `artist:<name>` - Specific artist.
- `genre:<name>` - Genre filter.
- `bpm_min:<bpm>` `bpm_max:<bpm>` - BPM range.
- `key:<key>` - Musical key (e.g., "8A", "Fm").
- `rating:>3` - Minimum rating.

### Crates and Playlists
Organize your library:

- **List crates**: `mixx_library(operation="crate_list")`
- **Crate tracks**: `mixx_library(operation="crate_tracks", crate_name="House Bangers")`
- **Add to crate**: `mixx_library(operation="add_to_crate", track_id="<id>", crate_name="House Bangers")`

Crates are like folders - a track can be in multiple crates. Playlists are ordered lists for sequential play.

### Auto DJ
Mixxx's built-in Auto DJ can queue and play tracks automatically:

- Add to queue: `mixx_library(operation="autodj_add", track_id="<id>")`
- Skip current: `mixx_library(operation="autodj_skip")`
- Toggle: `mixx_library(operation="autodj_toggle")`

Auto DJ respects your crate/playlist organization and can transition between tracks with configurable crossfade settings.

### Rating and Organization
Build a better library over time:

- Rate tracks after listening: `mixx_library(operation="rating_set", track_id="<id>", rating=4)`
- Organize into crates by genre, energy level, or mood.
- Use search filters to quickly find the right track for the moment.

---

## 7. Recording Sessions

### Basic Recording
Capture your mix:

1. `mixx_recording(operation="start_recording")`
2. Mix as usual.
3. `mixx_recording(operation="stop_recording")`

Mixxx saves the recording to your configured recording directory in Preferences.

### Recording Status
- `mixx_recording(operation="recording_status")` - Check elapsed time, file path, and state.

### Broadcasting
Stream live output:

- `mixx_recording(operation="toggle_broadcast")` - Start/stop broadcasting.
- `mixx_recording(operation="broadcast_status")` - Connection status.

Broadcast requires Ogg Vorbis or MP3 encoding configured in Mixxx's Preferences > Broadcasting.

---

## 8. Advanced Techniques

### Beat Grid Adjustments
If a track's beat grid is off (common with older recordings or live tracks), you can adjust:

1. Use sync and listen for drift.
2. Manually adjust BPM with the rate control in small increments (0.1% steps).
3. Use beat jump (1/4, 1/2, 1 beat) to realign.

### Nested Loops
Create tension by changing loop sizes:

1. Set an 8-beat loop.
2. After 4 loops, change to a 4-beat loop.
3. After 4 more loops, change to a 2-beat loop.
4. Release at the peak for maximum impact.

### EQ Kills for Transitions
Kill specific frequencies for dramatic transitions:
`mixx_mixer(operation="eq_kill", deck=1, band="low")`

This completely cuts the low frequencies, creating a dramatic reduction in energy that builds anticipation for the drop.

### Slip + Loop Combinations
In slip mode, loops don't disrupt the track flow:

1. `mixx_deck(operation="slip_enable", deck=1)`
2. `mixx_deck(operation="beat_loop", deck=1, beats=4)` - will play a 4-beat loop.
3. Exit the loop - track continues exactly where it would have been.
4. `mixx_deck(operation="slip_disable", deck=1)`

This is great for adding rhythmic variation without losing your place in the track.

---

## 9. Troubleshooting

### "Cannot connect to Mixxx"
- Ensure Mixxx is running.
- Verify OSC controller is enabled (Preferences > Controllers).
- Check that OSC input/output ports match Mixxx configuration.
- Verify network connectivity (try `ping <host>`).
- Check firewall settings - OSC uses UDP ports.

### "Track load failed"
- The track file may have been moved or deleted.
- Mixxx may need to rescan its library (Preferences > Library > Rescan).
- The track format may not be supported by Mixxx.

### "Audio distortion / clipping"
- Reduce master volume.
- Reduce individual deck gains.
- Check EQ settings (extreme EQ boosts can cause clipping).
- Verify Mixxx's hardware output settings are not clipping.

### "Effects not responding"
- Verify the effect unit is enabled.
- Check that the effect chain has at least one effect loaded.
- Ensure the effect unit is routed to the correct deck/channel.
- Verify parameter values are within valid range (0.0-1.0).

### "OSC commands not arriving"
- Increase the OSC send interval.
- Restart Mixxx's OSC controller.
- Check for multiple instances of Mixx-DJ-MCP that might conflict.

---

## 10. Example Conversations

### Beginner: "Help me mix my first two tracks"

**User**: "I want to mix 'Track A' and 'Track B' together. I have both in my 'Practice' crate."

**Agent**:
```
Let's start with the basics. I'll look up both tracks first.
-> mixx_library(operation="crate_tracks", crate_name="Practice")
  Found 'Track A' (128 BPM, F Minor) and 'Track B' (125 BPM, D Minor).

I'll load Track A on deck 1 and Track B on deck 2.
-> mixx_deck(operation="load", deck=1, track_id="track_a_id")
-> mixx_deck(operation="load", deck=2, track_id="track_b_id")

Since Track A is faster (128 vs 125 BPM), let's use sync to match them.
-> mixx_deck(operation="sync", deck=2, enabled=true)
  Deck 2 synced to 128 BPM.

Start Track A playing from the beginning.
-> mixx_deck(operation="play_pause", deck=1)

Start Track B in headphones to confirm the beatmatch.
-> mixx_mixer(operation="headphone", deck=2, enabled=true)
-> mixx_deck(operation="play_pause", deck=2)
  Both tracks at 128 BPM. Beatmatch sounds good.

Now for the transition. Since Track B is in D Minor and Track A is in F Minor
(Camelot: 7A -> 9A), this is an energy increase of 2 steps. Let's do a
16-bar EQ transition.

I'll set a 16-beat loop on the intro of Track B.
-> mixx_deck(operation="beat_loop", deck=2, beats=16)

Here's the plan:
1. At the next phrase, cut lows on Track A.
2. Start the loop on Track B.
3. Over 16 bars, crossfade and EQ in the new track.

Ready when you are! Say "go" to start the transition.
```

### Intermediate: "Build a 30-minute DJ set"

**User**: "I need a 30-minute DJ set for a house party. Upbeat, energetic, 124-130 BPM. Mix from my 'Party Prep' crate."

**Agent**:
```
I'll start by scanning your 'Party Prep' crate for suitable tracks.
-> mixx_library(operation="crate_tracks", crate_name="Party Prep")
  Found 24 tracks. Filtering for 124-130 BPM...

Sorted by energy and key. Here's my plan:
1. **Warm-up**: Track A (124 BPM, 6A) -> 8 min
2. **Build**: Track B (126 BPM, 8A) -> 6 min
3. **Peak**: Track C (128 BPM, 10A) -> Track D (130 BPM, 12A) -> 10 min
4. **Cool-down**: Track E (126 BPM, 9A) -> 6 min

Total: ~30 minutes with smooth harmonic transitions.

Let me load Track A on deck 1 to start.
-> mixx_deck(operation="load", deck=1, track_id="track_a")
-> mixx_deck(operation="play_pause", deck=1)

I'll pre-load Track B on deck 2, cued at the first beat of the intro.
-> mixx_deck(operation="load", deck=2, track_id="track_b")
-> mixx_deck(operation="hot_cue_set", deck=2, cue_number=1)
-> mixx_deck(operation="cue", deck=2, cue_point=1)

Your set is underway! I'll guide you through each transition when it's time.
Track A has a 16-bar intro, so the first transition point is in about 2 minutes.
```

### Advanced: "Multi-deck effects-heavy performance"

**User**: "I want to do a live remix using 3 decks, looping, and effects."

**Agent**:
```
Multi-deck live remix - great choice. I'll set up all three decks.

Step 1: Load tracks.
-> mixx_deck(operation="load", deck=1, track_id="track_acapella")
-> mixx_deck(operation="load", deck=2, track_id="track_instrumental")
-> mixx_deck(operation="load", deck=3, track_id="track_percussion")

Step 2: Set up effect chains.
-> mixx_effects(operation="list_effects")
  Available: Reverb, Delay, Flanger, BitCrusher, Filter

-> mixx_effects(operation="chain_load", unit=1, chain="Delay")
-> mixx_effects(operation="parameter_set", unit=1, index=0, value=0.4)
  Delay at 40% wet mix.

-> mixx_effects(operation="chain_load", unit=2, chain="Reverb")
-> mixx_effects(operation="parameter_set", unit=2, index=0, value=0.3)
  Reverb at 30% wet mix (subtle hall).

Step 3: Start the instrumental on deck 2 (main groove).
-> mixx_deck(operation="play_pause", deck=2)

Step 4: Create a 4-beat loop on the percussion track.
-> mixx_deck(operation="beat_loop", deck=3, beats=4)

I'll bring in the percussion loop gradually:
-> mixx_mixer(operation="volume", deck=3, value=0.5)

Structure:
- Deck 2 = Main instrumental (playthrough)
- Deck 3 = Percussion loop (4-bar, dropped in for fills)
- Deck 1 = Acapella (dropped at peak moments)

Ready to perform! Tell me when you want to bring in the acapella or build tension.
```

---

## Final Tips

- **Practice transitions** with familiar tracks before trying them live.
- **Know your library** - the best tool is knowing exactly which track comes next.
- **Use headphone cueing** to preview every transition before the audience hears it.
- **Record your sets** and listen back to identify areas for improvement.
- **Less is more with effects** - subtle processing sounds professional.
- **Watch your levels** - keep the master output healthy but not clipping.
- **Have fun** - if you're enjoying yourself, the audience will too.
