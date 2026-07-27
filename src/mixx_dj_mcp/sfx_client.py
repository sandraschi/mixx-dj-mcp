"""HTTP client for sfx-mcp REST API (FreeSound search + local cache)."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_SFX_MCP_URL = "http://127.0.0.1:11120"
REQUEST_TIMEOUT = 30.0


def get_sfx_mcp_url() -> str:
    return os.environ.get("SFX_MCP_URL", DEFAULT_SFX_MCP_URL).rstrip("/")


async def sfx_available(base_url: str | None = None) -> bool:
    url = (base_url or get_sfx_mcp_url()).rstrip("/")
    try:
        async with httpx.AsyncClient(base_url=url, timeout=5.0) as client:
            response = await client.get("/api/health")
            return response.status_code == 200
    except Exception:
        return False


async def sfx_status(base_url: str | None = None) -> dict[str, Any]:
    url = (base_url or get_sfx_mcp_url()).rstrip("/")
    try:
        async with httpx.AsyncClient(base_url=url, timeout=5.0) as client:
            response = await client.get("/api/health")
            response.raise_for_status()
            body = response.json()
            return {
                "available": True,
                "has_api_key": bool(body.get("has_api_key")),
                "server": body.get("server", "sfx-mcp"),
            }
    except Exception as exc:
        logger.debug("sfx-mcp health check failed: %s", exc)
        return {"available": False, "has_api_key": False, "server": "sfx-mcp"}


async def search_sounds(
    query: str,
    *,
    duration_max: int = 30,
    page: int = 1,
    tag: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    url = (base_url or get_sfx_mcp_url()).rstrip("/")
    params: dict[str, Any] = {"q": query, "duration_max": duration_max, "page": page}
    if tag:
        params["tag"] = tag
    async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
        response = await client.get("/api/sounds/search", params=params)
        response.raise_for_status()
        return response.json()


async def list_local_sounds(
    *,
    tag: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    url = (base_url or get_sfx_mcp_url()).rstrip("/")
    params = {"tag": tag} if tag else None
    async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
        response = await client.get("/api/sounds/local", params=params)
        response.raise_for_status()
        return response.json()


async def download_sound(
    sound_id: int,
    *,
    destination: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    url = (base_url or get_sfx_mcp_url()).rstrip("/")
    body: dict[str, Any] = {"sound_id": sound_id}
    if destination:
        body["destination"] = destination
    async with httpx.AsyncClient(base_url=url, timeout=120.0) as client:
        response = await client.post("/api/sounds/download", json=body)
        response.raise_for_status()
        return response.json()
