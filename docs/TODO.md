# mixx-dj-mcp — TODO

Ordered by value. Fork backlog lives in
[mixxxxx `docs/TODO.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/TODO.md).

---

## Done (2026-07-26)

| Item | Note |
|---|---|
| OSC bridge heartbeat | `/mixxxxx/ping` probe in `osc_bridge.py` |
| Help page | `/help` — Overview, NDI, Video, Skins, OSC |
| `docs/NDI.md` | Pointer to mixxxxx primer |
| `create_video_skin` | Patch `skin.xml` from shipped MixxxxxVideo |
| README links | NDI + Help in quick links |

---

## P1 — docs & UX

### 1. Rebuild NSIS with Help page
Run `web_sota` production build before next `build-native` release so installer
includes `/help`.

### 2. Expand Help tab content from mixxxxx STATUS
When STATUS changes, sync Help.tsx NDI/Video sections (or link out).

### 3. TOOLS.md — document Help route
One line under webapp section pointing to `/help`.

---

## P2 — tests

### 4. Bridge integration test (mixxxxx TODO 19)
Opt-in fixture; real UDP on 11119 — partially unblocked by fork OSC server.

---

## P3 — features (blocked on mixxxxx)

| Item | mixxxxx TODO |
|---|---|
| NDI sender | 27 |
| Beat-locked video FX | 25 |
| Video fallback chain | 26 |

Implement in mixxxxx first; expose via existing `mixx_deck` / new COs as needed.
