# NDI (planned)

**Status:** Not implemented in mixxxxx yet (TODO 27). This page is a short pointer; the full
primer lives in the fork repo.

## What is NDI?

**NDI** (Network Device Interface) sends live audio/video over your LAN so other apps can use
mixxxxx as a **network video source** — OBS, Resolume, vMix, etc. — without HDMI capture or
window scraping.

It is **not** a file format. It is live plumbing between apps on the same network.

## Where to read more

| Resource | Location |
|---|---|
| Full primer (design, roadmap, glossary) | [mixxxxx `docs/NDI.md`](https://github.com/sandraschi/mixxxxx/blob/video/docs/NDI.md) |
| Feature order vs beat FX / fallback | mixxxxx `docs/IDEAS.md` |
| In-app summary | mixx-dj-mcp webapp → **Help** → **NDI** tab |

## When it ships

Expect optional CMake `NDI=ON`, NDI SDK sender from the same blended frame as fullscreen
video, and ControlObjects for enable/source name. Until OBS or NDI Studio Monitor shows the
feed, STATUS stays **planned**.
