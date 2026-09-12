"""Unified library search: plex-mcp (primary) with Mixxx SQLite fallback."""

from __future__ import annotations

import re
from typing import Any, Literal

from . import plex_client
from .mixxx_library import search_library as search_mixxx_db

SearchMode = Literal["auto", "plex", "mixxx", "semantic"]
SearchEngine = Literal["plex_keyword", "plex_advanced", "plex_semantic", "mixxx", "mixed"]

_NATURAL_LANGUAGE_RE = re.compile(
    r"\b(tracks?|songs?|music|mix|playlist|like|similar|vibe|mood|for|with)\b",
    re.IGNORECASE,
)


def _has_advanced_filters(filters: dict[str, Any]) -> bool:
    keys = (
        "genre",
        "year",
        "min_year",
        "max_year",
        "collection",
        "actor",
        "director",
        "library_id",
        "media_type",
    )
    return any(filters.get(k) not in (None, "", []) for k in keys)


def _dedupe_results(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        key = str(item.get("rating_key") or item.get("id") or "")
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


async def _enrich_missing_artwork(results: list[dict[str, Any]], plex_url: str, *, max_fetch: int = 10) -> None:
    """Fill cover/poster URLs from Plex media detail when search payloads omit thumbs."""
    fetched = 0
    for row in results:
        if fetched >= max_fetch:
            break
        if row.get("artwork_url") or row.get("source") != "plex":
            continue
        if row.get("thumb") or row.get("art") or row.get("parentThumb") or row.get("grandparentThumb"):
            merged = plex_client.map_plex_item(row)
            for key in ("cover_url", "poster_url", "artwork_url", "thumb", "art"):
                if merged.get(key):
                    row[key] = merged[key]
            continue
        rating_key = row.get("rating_key") or (
            str(row.get("id", "")).removeprefix("plex:") if str(row.get("id", "")).startswith("plex:") else None
        )
        if not rating_key:
            continue
        detail = await plex_client.get_media_detail(str(rating_key), plex_url)
        if not detail:
            continue
        merged = plex_client.map_plex_item({**detail, "rating_key": rating_key})
        for key in ("cover_url", "poster_url", "artwork_url", "thumb", "art"):
            if merged.get(key):
                row[key] = merged[key]
        fetched += 1


async def search_library_smart(
    query: str,
    *,
    limit: int = 50,
    mode: SearchMode = "auto",
    include_mixxx: bool = True,
    **filters: Any,
) -> dict[str, Any]:
    """
    Search Plex via plex-mcp (keyword, advanced filters, or semantic RAG).

    Falls back to local Mixxx SQLite when Plex is offline or returns no hits.
    """
    query = (query or "").strip()
    if not query and not _has_advanced_filters(filters):
        return {
            "results": [],
            "total": 0,
            "message": "query or filters required",
            "engine": None,
            "plex_available": False,
        }

    plex_url = plex_client.get_plex_mcp_url()
    plex_up = await plex_client.plex_available(plex_url)
    results: list[dict[str, Any]] = []
    engine: SearchEngine | None = None
    message = ""

    if mode in ("auto", "plex", "semantic") and plex_up:
        try:
            if mode == "semantic" or (
                mode == "auto" and _NATURAL_LANGUAGE_RE.search(query) and not _has_advanced_filters(filters)
            ):
                payload = await plex_client.semantic_search(query, limit=min(limit, 30), base_url=plex_url)
                results = payload["results"]
                engine = "plex_semantic"
                message = payload["message"]
            elif _has_advanced_filters(filters):
                payload = await plex_client.advanced_search(
                    query=query or None,
                    limit=limit,
                    library_id=filters.get("library_id"),
                    media_type=filters.get("media_type"),
                    genre=filters.get("genre"),
                    year=filters.get("year"),
                    min_year=filters.get("min_year"),
                    max_year=filters.get("max_year"),
                    collection=filters.get("collection"),
                    actor=filters.get("actor"),
                    director=filters.get("director"),
                    base_url=plex_url,
                )
                results = payload["results"]
                engine = "plex_advanced"
                message = payload["message"]
            else:
                payload = await plex_client.keyword_search(
                    query,
                    limit=limit,
                    library_id=filters.get("library_id"),
                    media_type=filters.get("media_type"),
                    base_url=plex_url,
                )
                results = payload["results"]
                engine = "plex_keyword"
                message = payload["message"]
        except Exception as exc:
            message = f"Plex search failed: {exc}"

    if results:
        await _enrich_missing_artwork(results, plex_url)

    mixxx_payload: dict[str, Any] | None = None
    if include_mixxx and (mode in ("auto", "mixxx") or not results):
        mixxx_payload = search_mixxx_db(query, limit=limit)
        mixxx_results = [
            {**row, "source": "mixxx", "tags": [], "genres": [], "loadable": bool(row.get("id"))}
            for row in mixxx_payload.get("results", [])
        ]
        if mixxx_results:
            if results:
                results = _dedupe_results(results + mixxx_results)[:limit]
                engine = "mixed"
                message = f"{message} + {len(mixxx_results)} local Mixxx hit(s)"
            else:
                results = mixxx_results
                engine = "mixxx"
                message = mixxx_payload.get("message") or f"Mixxx library: {len(mixxx_results)} hit(s)"

    if not results and not message:
        message = (
            "No results. Start plex-mcp on port 10740 or scan tracks into Mixxx."
            if not plex_up
            else "No results for this query."
        )

    return {
        "results": results[:limit],
        "total": len(results[:limit]),
        "message": message,
        "engine": engine,
        "plex_available": plex_up,
        "database": mixxx_payload.get("database") if mixxx_payload else None,
    }
