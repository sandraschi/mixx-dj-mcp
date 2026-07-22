# OSC Bridge — Mixxx Configuration Guide

Mixx-DJ-MCP communicates with Mixxx via the **Open Sound Control (OSC)** protocol over UDP. Mixxx has a built-in OSC server that accepts commands on one port and sends feedback on another.

## Configuring Mixxx

1. Open Mixxx
2. Go to **Preferences** → **MIDI/OSC**
3. Check **Enable OSC**
4. Set the following:

| Setting | Value |
|---------|-------|
| **Output port** | `11118` |
| **Input port** | `11119` |
| **Send to** | `127.0.0.1` |

5. Click **Apply**
6. **Restart Mixxx** for changes to take effect

## Verifying the Connection

Start the MCP server and check the health endpoint:

```bash
uv run uvicorn mixx_dj_mcp.server:app --port 11116 --reload
curl http://127.0.0.1:11116/api/health
```

Expected response:
```json
{"status": "ok", "server": "mixx-dj-mcp", "version": "0.1.0", "mixx_connected": true}
```

If `mixx_connected` is `false`, Mixxx is not running or OSC is misconfigured.

## OSC Address Reference

Mixxx exposes all controls under the `/controller` OSC namespace. The bridge sends messages to `127.0.0.1:11119` and optionally listens for feedback on port `11118`.

### Deck Transport

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/deck/[1-4]/play` | bool | 0/1 | Play/pause toggle |
| `/deck/[1-4]/play_indicator` | float | 0/1 | Play state (read) |
| `/deck/[1-4]/stop` | bool | 0/1 | Stop |
| `/deck/[1-4]/cue_default` | bool | 0/1 | Set/jump to cue point |
| `/deck/[1-4]/cue_goto` | bool | 0/1 | Jump to cue point |
| `/deck/[1-4]/cue_set` | bool | 0/1 | Set cue at current position |
| `/deck/[1-4]/quantize` | bool | 0/1 | Toggle beat quantization |
| `/deck/[1-4]/keylock` | bool | 0/1 | Toggle keylock |

### Loops & Beatjumps

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/deck/[1-4]/loop_enabled` | bool | 0/1 | Loop on/off |
| `/deck/[1-4]/loop_in` | bool | 0/1 | Set loop start |
| `/deck/[1-4]/loop_out` | bool | 0/1 | Set loop end |
| `/deck/[1-4]/beatloop_[4,8,16,32,64]` | bool | 0/1 | Toggle beat loop |
| `/deck/[1-4]/beatloop_roll_[4,8,16,32,64]` | bool | 0/1 | Roll loop |
| `/deck/[1-4]/beatjump_[1,2,4,8,16,32,64]_forward` | bool | 0/1 | Jump forward N beats |
| `/deck/[1-4]/beatjump_[1,2,4,8,16,32,64]_backward` | bool | 0/1 | Jump backward N beats |
| `/deck/[1-4]/reloop_toggle` | bool | 0/1 | Toggle loop (re-activate last) |
| `/deck/[1-4]/reloop_exit` | bool | 0/1 | Exit loop |

### Sync

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/deck/[1-4]/sync_enabled` | bool | 0/1 | Sync lock toggle |
| `/deck/[1-4]/sync_mode` | float | 0-4 | Sync mode (0=off, 1=master, 2=follower, 3=leader, 4=none) |
| `/deck/[1-4]/beatsync` | bool | 0/1 | One-shot beat sync |
| `/deck/[1-4]/beatsync_tempo` | bool | 0/1 | Sync tempo only |
| `/deck/[1-4]/beatsync_phase` | bool | 0/1 | Sync phase only |

### Hot Cues

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/deck/[1-4]/hotcue_[1-4]_activated` | bool | 0/1 | Activate hot cue |
| `/deck/[1-4]/hotcue_[1-4]_set` | bool | 0/1 | Set hot cue at current pos |
| `/deck/[1-4]/hotcue_[1-4]_clear` | bool | 0/1 | Clear hot cue |

### Rate & Tempo

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/deck/[1-4]/rate` | float | -1.0 to 1.0 | Playback rate adjustment |
| `/deck/[1-4]/rate_perm_up` | bool | 0/1 | Increase rate (temporary) |
| `/deck/[1-4]/rate_perm_down` | bool | 0/1 | Decrease rate (temporary) |
| `/deck/[1-4]/rate_temp_up` | bool | 0/1 | Nudge faster |
| `/deck/[1-4]/rate_temp_down` | bool | 0/1 | Nudge slower |
| `/deck/[1-4]/pregain` | float | 0.0-4.0 | Pregain (linear scale) |

### Filters & EQ

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/deck/[1-4]/filterHigh` | float | 0.0-1.0 | High shelf filter |
| `/deck/[1-4]/filterMid` | float | 0.0-1.0 | Mid peak filter |
| `/deck/[1-4]/filterLow` | float | 0.0-1.0 | Low shelf filter |
| `/deck/[1-4]/filterHighKill` | bool | 0/1 | Kill high filter |
| `/deck/[1-4]/filterMidKill` | bool | 0/1 | Kill mid filter |
| `/deck/[1-4]/filterLowKill` | bool | 0/1 | Kill low filter |

### Track Loading

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/deck/[1-4]/LoadTrack` | string | Path | Load track by file path |
| `/deck/[1-4]/LoadSelectedTrack` | bool | 0/1 | Load currently selected track |
| `/deck/[1-4]/eject` | bool | 0/1 | Unload track |

### Mixer

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/mixer/crossfader` | float | -1.0 to 1.0 | Crossfader position |
| `/mixer/crossfader_curve` | float | 0.0 to 1.0 | Crossfader curve shape |
| `/mixer/volume/[1-4]` | float | 0.0 to 1.0 | Channel volume |
| `/mixer/pregain/[1-4]` | float | 0.0 to 4.0 | Channel pregain |
| `/mixer/balance/[1-4]` | float | -1.0 to 1.0 | Channel balance |
| `/mixer/headVolume/[1-4]` | float | 0.0 to 1.0 | Headphone volume |
| `/mixer/pfl/[1-4]` | bool | 0/1 | Headphone cue (Pre-Fader Listen) |
| `/mixer/talkover/[1-4]` | bool | 0/1 | Talkover (duck music) |
| `/mixer/orientation/[1-4]` | int | 0/1/2 | Orientation (0=left, 1=center, 2=right) |
| `/mixer/equalizer/[1-4]/0` | float | 0.0 to 1.0 | EQ low band |
| `/mixer/equalizer/[1-4]/1` | float | 0.0 to 1.0 | EQ mid band |
| `/mixer/equalizer/[1-4]/2` | float | 0.0 to 1.0 | EQ high band |

### Effects

| OSC Address | Type | Values | Description |
|-------------|------|--------|-------------|
| `/effects/chain/[1-4]/enabled` | bool | 0/1 | Enable effect chain |
| `/effects/chain/[1-4]/mix` | float | 0.0 to 1.0 | Chain wet/dry mix |
| `/effects/chain/[1-4]/super` | float | 0.0 to 1.0 | Super knob (all params) |
| `/effects/chain/[1-4]/effect/[1-4]/enabled` | bool | 0/1 | Enable individual effect |
| `/effects/chain/[1-4]/effect/[1-4]/param/[1-4]` | float | 0.0 to 1.0 | Effect parameter value |
| `/effects/chain/[1-4]/effect/[1-4]/param/[1-4]/meta` | float | 0.0 to 1.0 | Parameter minimum, maximum, default (read-only) |

## OSC Protocol Notes

- Mixxx uses the standard OSC bundle format
- Commands are sent as UDP packets to `127.0.0.1:11119`
- Mixxx responds on port `11118` if feedback is enabled
- OSC addresses are case-sensitive — use exact casing from the reference above
- Boolean values: send `1.0` for true, `0.0` for false
- String values (LoadTrack): send as OSC string with full file path
- Mixxx may not send ACK for every command — this is normal UDP behavior

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No response from Mixxx | OSC not enabled | Check Preferences → MIDI/OSC |
| "Connection refused" on 11119 | Wrong port in .env | Verify `.env` matches Mixxx settings |
| Commands work intermittently | Port conflict | Check no other app uses 11118/11119 |
| LoadTrack does nothing | Invalid file path | Mixxx must be able to resolve the path |
| Crossfader not moving | Mixxx orientation setting | Ensure channel orientation is set correctly |
