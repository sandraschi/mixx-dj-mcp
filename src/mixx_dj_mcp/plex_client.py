"""HTTP client for plex-mcp REST API (intelligent library search)."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from .mixxx_library import format_duration

logger = logging.getLogger(__name__)

DEFAULT_PLEX_MCP_URL = "http://127.0.0.1:10740"
REQUEST_TIMEOUT = 20.0


def get_plex_mcp_url() -> str:
    return os.environ.get("PLEX_MCP_URL", DEFAULT_PLEX_MCP_URL).rstrip("/")


async def _get(client: httpx.AsyncClient, path: str, **params: Any) -> dict[str, Any]:
    response = await client.get(path, params=params)
    response.raise_for_status()
    return response.json()


async def _post(client: httpx.AsyncClient, path: str, body: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(path, json=body)
    response.raise_for_status()
    return response.json()


async def plex_available(base_url: str | None = None) -> bool:
    url = (base_url or get_plex_mcp_url()).rstrip("/")
    try:
        async with httpx.AsyncClient(base_url=url, timeout=5.0) as client:
            response = await client.get("/health")
            return response.status_code == 200
    except Exception:
        return False


async def list_libraries(base_url: str | None = None) -> list[dict[str, Any]]:
    url = (base_url or get_plex_mcp_url()).rstrip("/")
    async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
        payload = await _get(client, "/api/libraries/")
        if isinstance(payload, dict):
            return payload.get("data") or payload.get("libraries") or []
        return payload if isinstance(payload, list) else []


def _artist_from_item(item: dict[str, Any]) -> str:
    for key in ("grandparentTitle", "parentTitle", "artist", "albumArtist"):
        value = item.get(key)
        if value:
            return str(value)
    if item.get("type") == "track" and item.get("title"):
        return str(item.get("library_section_title") or "Unknown")
    return str(item.get("studio") or item.get("library_section_title") or "Unknown")


def _tags_from_item(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for key in ("genres", "collections", "mood", "style"):
        raw = item.get(key)
        if isinstance(raw, list):
            tags.extend(str(x) for x in raw if x)
        elif raw:
            tags.append(str(raw))
    if item.get("content_rating"):
        tags.append(str(item["content_rating"]))
    return tags


def map_plex_item(item: dict[str, Any], *, score: float | None = None) -> dict[str, Any]:
    rating_key = str(item.get("rating_key") or item.get("id") or "")
    duration_min = item.get("duration")
    length = "0:00"
    if isinstance(duration_min, int | float) and duration_min > 0:
        # Plex search items may use minutes; analysis uses ms in some paths
        seconds = int(duration_min * 60) if duration_min < 1000 else int(duration_min / 1000)
        length = format_duration(seconds)
    elif item.get("media_info"):
        first = item["media_info"][0] if item["media_info"] else {}
        dur_ms = first.get("duration")
        if dur_ms:
            length = format_duration(int(dur_ms) / 1000)

    file_path = item.get("file") or item.get("path")
    track_id = str(file_path) if file_path else f"plex:{rating_key}"

    return {
        "id": track_id,
        "title": str(item.get("title") or "Unknown"),
        "artist": _artist_from_item(item),
        "bpm": float(item.get("bpm") or 0.0),
        "key": str(item.get("key") or item.get("original_key") or "Unknown"),
        "length": length,
        "source": "plex",
        "rating_key": rating_key,
        "year": item.get("year"),
        "type": item.get("type"),
        "genres": item.get("genres") or [],
        "collections": item.get("collections") or [],
        "tags": _tags_from_item(item),
        "summary": item.get("summary") or "",
        "score": score,
        "loadable": bool(file_path) or bool(rating_key),
    }


async def keyword_search(
    query: str,
    *,
    library_id: str | None = None,
    media_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    base_url: str | None = None,
) -> dict[str, Any]:
    url = (base_url or get_plex_mcp_url()).rstrip("/")
    params: dict[str, Any] = {"query": query, "limit": limit, "offset": offset}
    if library_id:
        params["library_id"] = library_id
    if media_type:
        params["media_type"] = media_type

    async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
        payload = await _get(client, "/api/search/", **params)

    items = payload.get("data") or []
    return {
        "results": [map_plex_item(item) for item in items],
        "total": payload.get("count") or len(items),
        "message": f"Plex keyword search: {len(items)} result(s)",
        "engine": "plex_keyword",
    }


async def advanced_search(
    *,
    query: str | None = None,
    library_id: str | None = None,
    media_type: str | None = None,
    genre: str | None = None,
    year: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    collection: str | None = None,
    actor: str | None = None,
    director: str | None = None,
    limit: int = 50,
    offset: int = 0,
    base_url: str | None = None,
) -> dict[str, Any]:
    url = (base_url or get_plex_mcp_url()).rstrip("/")
    body: dict[str, Any] = {"limit": limit, "offset": offset}
    for key, value in {
        "query": query,
        "library_id": library_id,
        "media_type": media_type,
        "genre": genre,
        "year": year,
        "min_year": min_year,
        "max_year": max_year,
        "collection": collection,
        "actor": actor,
        "director": director,
    }.items():
        if value is not None and value != "":
            body[key] = value

    async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
        payload = await _post(client, "/api/search/advanced", body)

    items = payload.get("data") or []
    return {
        "results": [map_plex_item(item) for item in items],
        "total": payload.get("count") or len(items),
        "message": f"Plex advanced search: {len(items)} result(s)",
        "engine": "plex_advanced",
    }


async def semantic_search(
    query: str,
    *,
    limit: int = 20,
    base_url: str | None = None,
) -> dict[str, Any]:
    url = (base_url or get_plex_mcp_url()).rstrip("/")
    async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
        payload = await _post(client, "/api/v1/search", {"query": query, "limit": limit})

    if not payload.get("success", True):
        return {
            "results": [],
            "total": 0,
            "message": payload.get("error") or "Plex semantic search unavailable",
            "engine": "plex_semantic",
        }

    results: list[dict[str, Any]] = []
    for hit in payload.get("results") or []:
        meta = hit.get("metadata") if isinstance(hit, dict) else {}
        if not isinstance(meta, dict):
            meta = {}
        item = {
            "id": str(meta.get("rating_key") or meta.get("id") or ""),
            "title": meta.get("title") or meta.get("name") or "Unknown",
            "type": meta.get("type"),
            "year": meta.get("year"),
            "summary": hit.get("content") or meta.get("summary") or "",
            "genres": meta.get("genres") or [],
            "collections": meta.get("collections") or [],
        }
        mapped = map_plex_item(item, score=float(hit.get("score") or 0.0))
        results.append(mapped)

    return {
        "results": results,
        "total": len(results),
        "message": f"Plex semantic search: {len(results)} result(s)",
        "engine": "plex_semantic",
    }


async def get_media_detail(rating_key: str, base_url: str | None = None) -> dict[str, Any] | None:
    url = (base_url or get_plex_mcp_url()).rstrip("/")
    async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
        payload = await _get(client, f"/api/media/{rating_key}")
    data = payload.get("data")
    return data if isinstance(data, dict) else None


async def resolve_file_path(track_ref: str, base_url: str | None = None) -> str | None:
    """Resolve deck load path from filesystem path or plex:rating_key."""
    if not track_ref.startswith("plex:"):
        return track_ref

    rating_key = track_ref.removeprefix("plex:")
    url = (base_url or get_plex_mcp_url()).rstrip("/")
    try:
        async with httpx.AsyncClient(base_url=url, timeout=REQUEST_TIMEOUT) as client:
            payload = await _get(client, f"/api/media/{rating_key}/file")
        file_path = payload.get("file")
        return str(file_path) if file_path else None
    except Exception as exc:
        logger.warning("Plex file resolve failed for %s: %s", rating_key, exc)
        return None
