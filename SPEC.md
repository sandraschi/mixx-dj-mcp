# mixx-dj-mcp v0.2 — Fleet Audio Hub

## Phases

### Phase 1: Audio Analysis Engine
- `mixx_analyze(operation="track")` — librosa BPM, key (Krumhansl-Schmuckler), energy curve, cue point detection
- `mixx_analyze(operation="library")` — batch-analyze unanalyzed tracks in Mixxx library
- Stores results in SQLite for later use by analytics/AI

### Phase 2: Fleet Audio Hub — Cross-MCP Deck Handoff
- `/api/v1/deck/handoff` — register external audio sources (songgen, sfx, stems, plex)
- `/api/v1/deck/{id}/cue` — cue a track in headphones without playing
- `/api/v1/cockpit/now_playing` — aggregated "what's happening" across all sources
- Wire PlexPanel ↔ SongGenPanel ↔ SFXPanel in Cockpit page with real cross-server triggers

### Phase 3: Live Set Recording & Replay
- `mixx_recording(operation="start"|"stop"|"list"|"replay"|"export")`
- JSONL recording of every OSC command with beat-aligned timestamps
- Replay engine for practicing transitions
- Export to Ableton-style session view

### Phase 4: DJ Analytics & History
- `mixx_history(operation="plays"|"transitions"|"profile"|"suggest")`
- SQLite: every play, cue, transition, EQ move logged
- Personal style profile: preferred BPM range, key, transition type, energy arc
- "What haven't I played in 30 days"

### Phase 5: AI Autonomous Mix Agent
- `mixx_ai_set(operation="plan"|"perform"|"review")`
- Uses ctx.sample() to autonomously plan and execute a set
- Monitors and adapts

### Phase 6: Voice Control
- `POST /api/voice/command` — webhook for speech-mcp
- Natural language → OSC via existing `_try_execute_command`
- Wake word integration via fleet-agent-mcp
