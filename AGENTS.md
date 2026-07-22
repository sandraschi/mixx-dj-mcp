# mixx-dj-mcp Agent Context

Fleet MCP server for Mixxx DJ control via OSC.
See `justfile` for available recipes.

## Quick Ref

- **Ports**: backend 11116, frontend 11117, OSC Mixxx-out 11118, OSC Mixxx-in 11119
- **Dependencies**: `uv sync`, `bun install` (web_sota/)
- **Serve**: `uv run uvicorn mixx_dj_mcp.server:app --port 11116 --reload`
- **Test**: `uv run pytest tests/ -q`
- **Lint**: `just lint` (ruff check + format)
- **Mixxx OSC config**: Preferences → MIDI/OSC → Enable OSC, port 11119 (in), 11118 (out), 127.0.0.1
- **Webapp**: `cd web_sota && bun run dev` → http://127.0.0.1:11117
- **Build NSIS**: `just build-native`
- **CUA smoke**: `just cua-nsis-test`

## Key Files

| File | Purpose |
|------|---------|
| `src/mixx_dj_mcp/server.py` | FastMCP app + tool registration |
| `src/mixx_dj_mcp/osc/bridge.py` | OSC UDP bridge to Mixxx |
| `src/mixx_dj_mcp/osc/addresses.py` | OSC address constants |
| `src/mixx_dj_mcp/tools/deck.py` | `mixx_deck` portmanteau |
| `src/mixx_dj_mcp/tools/library.py` | `mixx_library` portmanteau |
| `src/mixx_dj_mcp/tools/effects.py` | `mixx_effects` portmanteau |
| `src/mixx_dj_mcp/tools/mixer.py` | `mixx_mixer` portmanteau |
| `src/mixx_dj_mcp/config.py` | Env-based config |
| `bridge/README.md` | Mixxx OSC setup guide |

## Portmanteau Tools

All operations use `Literal` enums. Call pattern:

```python
result = await mixx_deck(deck=1, operation="play")
result = await mixx_library(operation="search", query="tech house", limit=20)
result = await mixx_effects(chain=1, operation="chain_enable", enabled=True)
result = await mixx_mixer(channel=1, operation="crossfader", position=0.5)
```

## Standards

- FastMCP 3.4+ with portmanteau pattern
- Prefab UI for deck/mixer/library status cards
- Conversational returns (success + message + data)
- Error responses with recovery suggestions
- SOTA webapp (React/Vite/Bun/Tailwind/Zustand)
- Tauri NSIS installer with embedded backend
- CORS configured for Tauri WebView
