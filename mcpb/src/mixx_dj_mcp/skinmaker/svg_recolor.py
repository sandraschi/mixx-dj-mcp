"""SVG recolor helpers (hex map + inkscape-mcp validate/optimize)."""

from __future__ import annotations

import logging
from pathlib import Path

from .inkscape_client import optimize_svg, probe_inkscape_mcp, validate_svg
from .qss_patch import apply_hex_replacements

logger = logging.getLogger(__name__)


async def recolor_skin_svgs(
    skin_path: Path,
    replacements: dict[str, str],
    *,
    max_files: int = 20,
) -> dict[str, int | bool | str]:
    style_dir = skin_path / "style"
    if not style_dir.is_dir():
        return {"files_updated": 0, "inkscape_mcp": False, "method": "none"}

    svg_files = list(style_dir.rglob("*.svg"))
    if not svg_files:
        return {"files_updated": 0, "inkscape_mcp": False, "method": "none"}

    inkscape_up = await probe_inkscape_mcp()

    updated = 0
    inkscape_processed = 0
    for svg in svg_files[:max_files]:
        try:
            content = svg.read_text(encoding="utf-8")
            patched, count = apply_hex_replacements(content, replacements)
            if count:
                svg.write_text(patched, encoding="utf-8")
                updated += 1
            elif not inkscape_up:
                continue

            if inkscape_up:
                if await validate_svg(svg):
                    if await optimize_svg(svg):
                        inkscape_processed += 1
        except Exception:
            logger.warning("Failed to recolor SVG: %s", svg.name)

    method = "hex+inkscape" if inkscape_up and inkscape_processed else "hex"
    if inkscape_up and updated and not inkscape_processed:
        method = "hex+inkscape_partial"

    return {
        "files_updated": updated,
        "inkscape_mcp": inkscape_up,
        "inkscape_optimized": inkscape_processed,
        "method": method,
    }
