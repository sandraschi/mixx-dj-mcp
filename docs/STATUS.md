# mixx-dj-mcp — Status

Last updated: 2026-07-27. Companion to [mixxxxx](https://github.com/sandraschi/mixxxxx)
(`video` branch).

## Integration with mixxxxx

| Capability | Status | Note |
|---|---|---|
| OSC bridge (11118/11119) | Works | When Mixxx/mixxxxx running with OSC enabled |
| Heartbeat `/mixxxxx/ping` | Works | `is_connected()` uses pong timeout |
| `mixx_deck` video ops | Works | Requires mixxxxx + video skin |
| Fork detection `/api/v1/fork` | Works | Cockpit shows mixxxxx vs vanilla |
| `mixx_skin(create_video_skin)` | Works | Copies MixxxxxVideo bundle, patches `skin.xml` |

## Webapp

| Page | Status | Note |
|---|---|---|
| Cockpit, Decks, Chat, Tools, Settings | Works | SOTA React 19 stack |
| **Library** | Works | Plex via `plex-mcp` (keyword, advanced filters, semantic) + Mixxx SQLite fallback |
| `/api/library/plex/libraries` | Works | Plex library picker for filters |
| `/api/library/resolve` | Works | Resolves `plex:rating_key` → local file for deck load |
| **Effects** | Works | `POST /api/v1/effects` → `mixx_effects` OSC |
| **Help** (`/help`) | Works (source) | Overview, **NDI**, Video, Skins, OSC tabs |
| `/api/v1/tools/call` | Works | Generic MCP tool bridge (Skins install, DAW sync, …) |
| Help in frozen NSIS build | Rebuild needed | `web_sota/dist/` gitignored — run `npm run build` |

## Documentation

| Doc | Purpose |
|---|---|
| [`docs/NDI.md`](NDI.md) | Short NDI pointer → mixxxxx primer |
| [`docs/MIXXX_VIDEO.md`](MIXXX_VIDEO.md) | Video DJ workflow |
| [`docs/TOOLS.md`](TOOLS.md) | MCP tool reference |
| [`docs/TODO.md`](TODO.md) | Backlog |
| mixxxxx [`docs/STATUS.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/STATUS.md) | What actually works in the fork |

## Not implemented (fork-side)

- NDI output (mixxxxx TODO 27) — documented in Help tab only
- Beat-locked video FX, fallback chain — mixxxxx IDEAS.md order before NDI
