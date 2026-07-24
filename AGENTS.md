# mixx-dj-mcp Agent Context

Fleet MCP server for Mixxx DJ control via OSC.
See `justfile` for available recipes.

## Quick Ref

- **Ports**: backend 11116, frontend 11117, OSC Mixxx-out 11118, OSC Mixxx-in 11119
- **Dependencies**: `uv sync`, `bun install` (web_sota/)
- **Serve**: `uv run uvicorn mixx_dj_mcp.server:app --port 11116 --reload`
- **Test**: `uv run pytest tests/ -q`
- **Lint**: `just lint` (ruff check + format)
- **Mixxx OSC config**: Preferences -> MIDI/OSC -> Enable OSC, port 11119 (in), 11118 (out), 127.0.0.1
- **Webapp**: `cd web_sota && bun run dev` -> http://127.0.0.1:11117
- **Build NSIS**: `just build-native`
- **CUA smoke**: `just cua-nsis-test`

## Key Files

| File | Purpose |
|------|---------|
| `src/mixx_dj_mcp/server.py` | FastMCP app + tool registration + REST endpoints |
| `src/mixx_dj_mcp/bridge/osc_bridge.py` | OSC UDP bridge to Mixxx |
| `src/mixx_dj_mcp/bridge/protocol.py` | OSC address constants and CO mappings |
| `src/mixx_dj_mcp/tools/deck_control.py` | `mixx_deck` portmanteau |
| `src/mixx_dj_mcp/tools/library.py` | `mixx_library` portmanteau |
| `src/mixx_dj_mcp/tools/effects.py` | `mixx_effects` portmanteau |
| `src/mixx_dj_mcp/tools/mixer.py` | `mixx_mixer` portmanteau |
| `src/mixx_dj_mcp/tools/controller.py` | `mixx_controller` USB auto-detect |
| `src/mixx_dj_mcp/tools/daw.py` | `mixx_daw` DAW export |
| `src/mixx_dj_mcp/tools/stems.py` | `mixx_stems` stem separation |
| `src/mixx_dj_mcp/tools/transitions.py` | `mixx_transition` AI transitions |
| `src/mixx_dj_mcp/tools/vinyl.py` | `mixx_vinyl` vinyl control |
| `src/mixx_dj_mcp/tools/skin_manager.py` | `mixx_skin` skin management |
| `src/mixx_dj_mcp/tools/smart_crate.py` | `mixx_crate` LLM crate creation |
| `src/mixx_dj_mcp/tools/set_sequencer.py` | `mixx_set` AI set sequencing |
| `src/mixx_dj_mcp/tools/prefab_cards.py` | Prefab UI status cards |
| `src/mixx_dj_mcp/config.py` | Env-based config |
| `bridge/README.md` | Mixxx OSC setup guide |

## Portmanteau Tools

All operations use `Literal` enums. Call pattern:

```python
result = await mixx_deck(deck=1, operation="play_pause")
result = await mixx_library(operation="search", query="tech house", limit=20)
result = await mixx_effects(chain=1, operation="chain_enable", enabled=True)
result = await mixx_mixer(channel=1, operation="crossfader", position=0.5)
result = await mixx_stems(operation="separate", deck=1, output_dir="C:/stems/out")
result = await mixx_transition(operation="suggest", deck_a=1, deck_b=2)
result = await mixx_vinyl(operation="calibrate", deck=1)
result = await mixx_crate(operation="generate", count=15)
result = await mixx_skin(operation="list")
result = await mixx_controller(operation="detect")
result = await mixx_daw(operation="export", deck=1)
result = await mixx_set(operation="plan", duration_minutes=60)
```

## Standards

- FastMCP 3.4+ with portmanteau pattern
- Prefab UI for deck/mixer/library status cards
- Conversational returns (success + message + data)
- Error responses with recovery suggestions
- SOTA webapp (React/Vite/Bun/Tailwind/Zustand)
- Tauri NSIS installer with embedded backend
- CORS configured for Tauri WebView
