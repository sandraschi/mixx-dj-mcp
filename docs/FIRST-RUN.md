# First run (most important user path)

**Goal:** Install → Launch → OSC connected → DJ.

## 1. Install Mixxxxx

Windows installer (when built):

```
mixxxxx/build/mixxxxx-*-win64.exe
```

Or dev build: `mixxxxx/docs/INSTALLER.md`

Creates:

- `%ProgramFiles%\Mixxxxx\mixxx.exe`
- `%ProgramFiles%\Mixxxxx\mixxxxx-osc.cmd` (OSC fleet launcher)
- Start Menu **Mixxxxx (OSC fleet)**

## 2. Install mixx-dj-mcp operator

See `docs/INSTALL.md` — Tauri NSIS operator bundles MCP + webapp.

Optional `.env`:

```
MIXXXXX_EXE=C:\Program Files\Mixxxxx\mixxx.exe
PLEX_MCP_URL=http://127.0.0.1:10740
```

## 3. Open webapp → Dashboard

First-time **onboarding wizard** (OSC ports → Launch → Probe).

Checklist API: `GET /api/mixxx/setup`

```json
{
  "ready": false,
  "steps": [
    {"id": "install_mixxxxx", "done": true, ...},
    {"id": "launch_dj", "done": false, ...},
    {"id": "osc_connect", "done": false, ...}
  ],
  "user_message": "Dashboard → Launch ..."
}
```

## 4. Daily use

1. Start **mixx-dj-mcp** operator (or backend only in dev)
2. Dashboard → **Launch** (uses `mixxxxx-osc.cmd` when installed)
3. **Probe OSC** — green = MCP can control decks
4. Library (Plex + Mixxx) or MCP tools in Cursor

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No Mixxxxx in exe dropdown | Install Mixxxxx or set `MIXXXXX_EXE` |
| OSC offline | Launch via OSC shortcut; check ports 11119/11118 |
| Backend offline | Restart operator; port 11116 |
| Plex empty | Start plex-mcp on 10740 |

Serato crates optional — see `mixxxxx/docs/SERATO-IMPORT.md`.
