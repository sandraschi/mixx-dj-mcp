# Skinmaker (inside mixx-dj-mcp)

Skin authoring for the **Mixxxxx fleet** — not a generic Mixxx utility. QSS schemes, SVG recolor (inkscape-mcp), and webapp/MCP install flows live here so users stay in the Mixx-MCP ecosystem.

## Why here, not a separate repo

- Skins page, `mixx_skin`, and Help docs are already in this repo
- Mixxxxx Video + Daylight v2 are fleet-specific (`mixxxxx/res/skins/MixxxxxVideo`)
- Vanilla Mixxx users can still use `mixx_skin` if they run mixx-dj-mcp, but schemes target Mixxxxx Video workflows

## Layout

```
src/mixx_dj_mcp/skinmaker/
  palette.py          # load *.tokens.json schemes
  qss_patch.py        # apply hex_replacements to QSS
  svg_recolor.py      # hex map + inkscape validate/optimize when MCP up
  inkscape_client.py  # POST /v1/tool → inkscape_file, inkscape_vector
  schemes/            # bundled token files
src/mixx_dj_mcp/tools/skin_manager.py   # mixx_skin MCP tool
```

## MCP operations

```python
mixx_skin("list")
mixx_skin("create_video_skin")
mixx_skin("patch_scheme", scheme="daylight-v2", target="installed")  # user skin dir
mixx_skin("patch_scheme", scheme="daylight-v2", target="source")    # mixxxxx repo
mixx_skin("create_skin", name="mytheme", prompt="…")
```

## Schemes

| File | Use |
|------|-----|
| `daylight-v2.tokens.json` | Outdoor Mixxxxx Video Daylight |

Add schemes under `skinmaker/schemes/` and register in Help → Skins.

## inkscape-mcp

Set `INKSCAPE_MCP_URL=http://127.0.0.1:11028` (optional `INKSCAPE_V1_TOOL_URL` for `/v1/tool`).

When inkscape-mcp is running, `create_skin` / `recolor_skin_svgs`:

1. Applies palette via hex replacement in `style/**/*.svg`
2. Calls `inkscape_file` validate + `inkscape_vector` optimize/scour per file

Returns `method`: `hex`, `hex+inkscape`, or `hex+inkscape_partial`. Full palette quantize via Inkscape extensions is still Phase 3.

## Related

- `mixxxxx/docs/SKINS.md` — canonical skin files
- mixx-dj-mcp webapp `/skins` — browse + install
