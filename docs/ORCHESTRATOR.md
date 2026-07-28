# AV orchestrator stack

**mixxxxx + mixx-dj-mcp + NDI + Resolume/OBS** — explained for people who never heard of NDI
until five minutes ago.

Full version (with diagram): [mixxxxx `docs/ORCHESTRATOR.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/ORCHESTRATOR.md)

## In plain language

- **mixxxxx** — DJ + per-deck video + crossfader blend. The **hub**.
- **NDI®** — Free runtime you install separately. Puts mixxxxx’s video on the **network** so other apps can pick it up by name — like a virtual camera cable over Wi‑Fi/Ethernet.
- **Resolume** — Visual mixer: layers, effects, projection mapping. **Not** included; you buy Avenue or Arena.
- **OBS** — Streaming/recording with overlays.
- **mixx-dj-mcp** — This repo: webapp + MCP that drives mixxxxx over OSC and connects library/SFX/Resolume bridges.
- **resolume-mcp** — MCP server that talks to Resolume over OSC.

Mixxxxx is the **orchestrator**: it owns the mix and publishes AV; everything else **subscribes** or **automates**.

## Webapp help

Open **Help** in the sidebar:

| Tab | Contents |
|-----|----------|
| **Overview** | Stack summary |
| **AV Rig** | Diagram, OBS vs Resolume, when to use what |
| **NDI** | Beginner primer + setup + **targets table** (OBS, Resolume, …) |
| **Resolume** | Avenue vs demo, integration with mixxxxx |
| **Video / Skins / OSC** | mixxxxx specifics |

## Quick test without buying anything

1. Build mixxxxx with NDI on; install [NDI redistributable](https://ndi.link/NDIRedistV5).
2. Enable NDI; open **NDI Studio Monitor** (free, from NDI Tools).
3. See source **Mixxxxx** (or your `[Ndi],source_name`).

That validates the video pipe before Resolume or OBS.

## NDI targets (full list)

[mixxxxx `docs/NDI-TARGETS.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/NDI-TARGETS.md) — Studio Monitor, OBS/DistroAV, Resolume, vMix, TouchDesigner, bridges, and what mixxxxx does *not* support (HX, receive).
