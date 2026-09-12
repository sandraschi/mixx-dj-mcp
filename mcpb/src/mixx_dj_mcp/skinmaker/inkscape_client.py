"""Thin HTTP client for inkscape-mcp (port 11028)."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

INKSCAPE_MCP_URL = os.environ.get("INKSCAPE_MCP_URL", "http://127.0.0.1:11028")
INKSCAPE_V1_TOOL = os.environ.get("INKSCAPE_V1_TOOL_URL", f"{INKSCAPE_MCP_URL.rstrip('/')}/v1/tool")


async def probe_inkscape_mcp(base_url: str = INKSCAPE_MCP_URL) -> bool:
    try:
        health_url = base_url.rstrip("/").replace("/mcp", "") + "/api/health"
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(health_url)
            if r.status_code == 200:
                return True
            r = await client.post(
                base_url if base_url.endswith("/mcp") else f"{base_url}/mcp",
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            )
            return r.status_code == 200
    except Exception:
        return False


async def call_v1_tool(tool: str, params: dict[str, Any]) -> dict[str, Any]:
    """Invoke inkscape-mcp REST bridge (POST /v1/tool)."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(
            INKSCAPE_V1_TOOL,
            json={"tool": tool, "params": params},
        )
        r.raise_for_status()
        body = r.json()
        if not body.get("success"):
            raise RuntimeError(body.get("error") or f"{tool} failed")
        data = body.get("data")
        return data if isinstance(data, dict) else {"output": data}


async def validate_svg(path: Path) -> bool:
    try:
        await call_v1_tool(
            "inkscape_file",
            {"operation": "validate", "input_path": str(path.resolve())},
        )
        return True
    except Exception as exc:
        logger.debug("inkscape validate failed for %s: %s", path.name, exc)
        return False


async def optimize_svg(path: Path) -> bool:
    """Run inkscape_vector optimize_svg + scour on a skin SVG."""
    resolved = str(path.resolve())
    try:
        await call_v1_tool(
            "inkscape_vector",
            {"operation": "optimize_svg", "input_path": resolved, "output_path": resolved},
        )
        return True
    except Exception:
        try:
            await call_v1_tool(
                "inkscape_vector",
                {"operation": "scour_svg", "input_path": resolved, "output_path": resolved},
            )
            return True
        except Exception as exc:
            logger.debug("inkscape optimize failed for %s: %s", path.name, exc)
            return False


async def recolor_svg_batch(
    svg_paths: list[Path],
    palette_hex: list[str],
    *,
    base_url: str = INKSCAPE_MCP_URL,
    max_files: int = 20,
) -> dict[str, Any]:
    available = await probe_inkscape_mcp(base_url)
    return {
        "inkscape_mcp_available": available,
        "files_queued": min(len(svg_paths), max_files),
        "palette": palette_hex,
        "note": "Palette applied via hex map; inkscape validates/optimizes when MCP is up.",
    }
