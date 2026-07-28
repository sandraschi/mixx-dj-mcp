# NDI — network video from mixxxxx

**Status:** Partial MVP in mixxxxx (GPL-clean dynamic load). Verify with NDI Studio Monitor or OBS NDI Source.

## Never heard of NDI?

**NDI®** is a way to send **live video** between apps on the same network. No file export, no
“capture this window”. mixxxxx appears as a **named source** (default `Mixxxxx`); Resolume, OBS,
or vMix **subscribe** to that name.

Think: **OSC for control, NDI for video.**

## Setup (5 steps)

1. Install [NDI redistributable](https://ndi.link/NDIRedistV5) (free).
2. Set env `NDI_RUNTIME_DIR_V5` to the folder with `Processing.NDI.Lib.x64.dll`.
3. Run mixxxxx; enable `[Ndi],enabled` or `--ndi-enable`.
4. Confirm in **NDI Studio Monitor** (free).
5. In Resolume/OBS: add **NDI input** → pick your source name.

## Docs

| Topic | Where |
|-------|--------|
| Full user guide | [mixxxxx `docs/NDI.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/NDI.md) |
| **NDI targets** (OBS, Resolume, vMix, …) | [mixxxxx `docs/NDI-TARGETS.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/NDI-TARGETS.md) |
| Licensing (GPL) | [mixxxxx `docs/NDI-LICENSING.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/NDI-LICENSING.md) |
| Orchestrator context | [`docs/ORCHESTRATOR.md`](ORCHESTRATOR.md) |
| In-app | Webapp **Help → NDI** |

## mixx-dj-mcp role

NDI is **inside mixxxxx**, not in the MCP server. mixx-dj-mcp can toggle deck video and (via OSC COs) enable NDI when exposed; primary control today is mixxxxx COs and CLI.
