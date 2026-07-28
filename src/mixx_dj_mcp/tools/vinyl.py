"""Vinyl record catalog tool -- OCR, AI categorization, search, and Plex crossref."""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

import httpx
from fastmcp import FastMCP

DB_PATH = os.environ.get("VINYL_DB", str(Path.home() / "Vinyl" / "vinyl.db"))
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
PLEX_MCP_BASE = os.environ.get("PLEX_MCP_URL", "http://localhost:10740")


def _get_conn() -> sqlite3.Connection | None:
    if not os.path.isfile(DB_PATH):
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        return None


def _mock_records() -> list[dict]:
    """Return mock data when no DB exists."""
    return [
        {
            "id": 1,
            "sequential": 1,
            "artist": "Daft Punk",
            "album_title": "Discovery",
            "catalog_number": "724384960609",
            "year": 2001,
            "side": "A",
            "speed": 33,
            "genre": "electronic",
            "era": "2000s",
            "mood": "uplifting",
            "energy": 8,
        },
        {
            "id": 2,
            "sequential": 2,
            "artist": "Jeff Mills",
            "album_title": "Waveform Transmission Vol. 1",
            "catalog_number": "TRAX001",
            "year": 1992,
            "side": "A",
            "speed": 33,
            "genre": "techno",
            "era": "1990s",
            "mood": "energetic",
            "energy": 9,
        },
        {
            "id": 3,
            "sequential": 3,
            "artist": "Nina Kraviz",
            "album_title": "Ghetto Kraviz",
            "catalog_number": "RBLP07",
            "year": 2013,
            "side": "A",
            "speed": 33,
            "genre": "tech_house",
            "era": "2010s",
            "mood": "deep",
            "energy": 6,
        },
        {
            "id": 4,
            "sequential": 4,
            "artist": "Aphex Twin",
            "album_title": "Selected Ambient Works 85-92",
            "catalog_number": "APOLLO 101",
            "year": 1992,
            "side": "B",
            "speed": 33,
            "genre": "ambient",
            "era": "1990s",
            "mood": "chill",
            "energy": 3,
        },
        {
            "id": 5,
            "sequential": 5,
            "artist": "Miles Davis",
            "album_title": "Kind of Blue",
            "catalog_number": "CL1355",
            "year": 1959,
            "side": "A",
            "speed": 33,
            "genre": "jazz",
            "era": "1950s",
            "mood": "chill",
            "energy": 4,
        },
        {
            "id": 6,
            "sequential": 6,
            "artist": "Kraftwerk",
            "album_title": "Computer World",
            "catalog_number": "1C 064-46 423",
            "year": 1981,
            "side": "A",
            "speed": 33,
            "genre": "electronic",
            "era": "1980s",
            "mood": "groovy",
            "energy": 7,
        },
        {
            "id": 7,
            "sequential": 7,
            "artist": "Moodymann",
            "album_title": "Silent Introduction",
            "catalog_number": "KDJ 02",
            "year": 1997,
            "side": "A",
            "speed": 33,
            "genre": "deep_house",
            "era": "1990s",
            "mood": "deep",
            "energy": 5,
        },
        {
            "id": 8,
            "sequential": 8,
            "artist": "Charlotte de Witte",
            "album_title": "Return to Nowhere",
            "catalog_number": "KNTXT009",
            "year": 2019,
            "side": "A",
            "speed": 33,
            "genre": "techno",
            "era": "2010s",
            "mood": "dark",
            "energy": 9,
        },
    ]


def _mock_filter(records: list[dict], query: str) -> list[dict]:
    q = query.lower()
    return [r for r in records if q in r["artist"].lower() or q in r["album_title"].lower() or q in r["genre"].lower()]


async def _query_db(query: str, params: tuple = ()) -> list[dict]:
    """Query the vinyl DB or return mock data."""
    conn = _get_conn()
    if conn is None:
        records = _mock_records()
        if query:
            records = _mock_filter(records, query)
        return records
    try:
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        conn.close()
        return []


async def _ollama_chat(prompt: str) -> str:
    """Send a prompt to Ollama and return the response text."""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                },
            )
            if r.status_code == 200:
                return r.json().get("response", "")
    except Exception as e:
        return f"[Ollama error: {e}]"
    return ""


async def mixx_vinyl(
    operation: Literal["catalog", "search", "gig_pick", "crossref", "stats"],
    directory: str | None = None,
    query: str = "",
    genre: str | None = None,
    era: str | None = None,
    limit: int = 20,
    vinyl_id: int | None = None,
    count: int = 5,
) -> dict[str, Any]:
    """Vinyl record catalog and search tool.

    PORTMANTEAU PATTERN: Consolidates all vinyl collection management.

    SUPPORTED OPERATIONS:
    - catalog: Run OCR pipeline on a directory of vinyl photos (requires directory)
    - search: Search the vinyl database by query, genre, and era
    - gig_pick: Natural language query to pick records for a gig (requires query)
    - crossref: Find matching digital copy in Plex (requires vinyl_id)
    - stats: Summary of the vinyl collection

    ## Return Format
    {"success": bool, "message": str, "data": dict}

    ## Examples
    mixx_vinyl("catalog", directory="D:/Vinyl/inbox")
    mixx_vinyl("search", query="techno", genre="techno", limit=10)
    mixx_vinyl("gig_pick", query="dark warehouse techno set", count=5)
    mixx_vinyl("crossref", vinyl_id=1)
    mixx_vinyl("stats")
    """
    try:
        if operation == "catalog":
            if not directory:
                return {
                    "success": False,
                    "message": "directory required for catalog operation",
                    "data": {},
                }
            script_path = str(Path(__file__).parent.parent.parent.parent / "scripts" / "vinyl_catalog.py")
            if not os.path.isfile(script_path):
                return {
                    "success": False,
                    "message": f"Catalog script not found at {script_path}",
                    "data": {},
                }
            result = subprocess.run(
                [sys.executable, script_path, directory],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Catalog script failed: {result.stderr[:500]}",
                    "data": {
                        "stdout": result.stdout[:2000],
                        "stderr": result.stderr[:500],
                    },
                }
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = {"raw": result.stdout[:2000]}
            return {
                "success": True,
                "message": f"Cataloged vinyl records from {directory}",
                "data": output,
            }

        elif operation == "search":
            where = []
            params = []
            if query:
                where.append("(artist LIKE ? OR album_title LIKE ? OR genre LIKE ? OR era LIKE ?)")
                q = f"%{query}%"
                params.extend([q, q, q, q])
            if genre:
                where.append("genre = ?")
                params.append(genre)
            if era:
                where.append("era = ?")
                params.append(era)
            sql = "SELECT * FROM vinyl"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            records = await _query_db(sql, tuple(params))
            return {
                "success": True,
                "message": f"Found {len(records)} vinyl records",
                "data": {"records": records, "total": len(records)},
            }

        elif operation == "gig_pick":
            if not query:
                return {
                    "success": False,
                    "message": "query required for gig_pick",
                    "data": {},
                }
            records = await _query_db("SELECT * FROM vinyl ORDER BY RANDOM() LIMIT 100")
            if not records:
                return {
                    "success": False,
                    "message": "No records in database to pick from",
                    "data": {},
                }
            records_json = json.dumps(
                [
                    {
                        "id": r["id"],
                        "artist": r.get("artist", "Unknown"),
                        "album_title": r.get("album_title", "Unknown"),
                        "genre": r.get("genre", "Unknown"),
                        "era": r.get("era", "Unknown"),
                        "mood": r.get("mood", "Unknown"),
                        "energy": r.get("energy", 5),
                    }
                    for r in records
                ],
                indent=2,
            )
            prompt = (
                f"You are a DJ's vinyl selector. Given a collection and a gig "
                f"description, pick the {count} most suitable records.\n\n"
                f"Gig description: {query}\n\n"
                f"Collection:\n{records_json}\n\n"
                f"Return ONLY a JSON array of objects with keys: "
                f'"id", "reason" (why it fits, 1 sentence).\n'
                f"Pick exactly {count} records. Order by best fit first."
            )
            response = await _ollama_chat(prompt)
            picks = []
            try:
                start = response.find("[")
                end = response.rfind("]") + 1
                if start >= 0 and end > start:
                    picks = json.loads(response[start:end])
            except (json.JSONDecodeError, ValueError):
                picks = [{"id": r["id"], "reason": "Suggested based on collection"} for r in records[:count]]
            selected = []
            for pick in picks:
                rid = pick.get("id")
                for r in records:
                    if r["id"] == rid:
                        selected.append(
                            {
                                **r,
                                "match_reason": pick.get("reason", ""),
                            }
                        )
                        break
            if not selected:
                selected = records[:count]
            return {
                "success": True,
                "message": f"Selected {len(selected)} records for gig",
                "data": {"query": query, "records": selected},
            }

        elif operation == "crossref":
            if vinyl_id is None:
                return {
                    "success": False,
                    "message": "vinyl_id required for crossref",
                    "data": {},
                }
            records = await _query_db("SELECT * FROM vinyl WHERE id = ?", (vinyl_id,))
            if not records:
                return {
                    "success": False,
                    "message": f"No record with id {vinyl_id}",
                    "data": {},
                }
            record = records[0]
            search_term = (f"{record.get('artist', '')} {record.get('album_title', '')}").strip()
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    r = await client.get(
                        f"{PLEX_MCP_BASE}/api/v1/search",
                        params={"query": search_term, "limit": 5},
                    )
                    plex_results = r.json().get("results", []) if r.status_code == 200 else []
            except Exception:
                plex_results = [
                    {
                        "title": f"Mock: {search_term}",
                        "type": "track",
                        "library": "Music",
                        "match": "simulated",
                    }
                ]
            return {
                "success": True,
                "message": f"Crossref results for {search_term}",
                "data": {"vinyl": record, "plex_matches": plex_results},
            }

        elif operation == "stats":
            records = await _query_db("SELECT * FROM vinyl ORDER BY sequential")
            total = len(records)
            genres: dict[str, int] = {}
            eras: dict[str, int] = {}
            moods: dict[str, int] = {}
            for r in records:
                g = r.get("genre", "unknown") or "unknown"
                genres[g] = genres.get(g, 0) + 1
                e = r.get("era", "unknown") or "unknown"
                eras[e] = eras.get(e, 0) + 1
                m = r.get("mood", "unknown") or "unknown"
                moods[m] = moods.get(m, 0) + 1
            genre_dist = sorted(genres.items(), key=lambda x: -x[1])
            era_dist = sorted(eras.items(), key=lambda x: -x[1])
            mood_dist = sorted(moods.items(), key=lambda x: -x[1])
            return {
                "success": True,
                "message": f"Collection has {total} records",
                "data": {
                    "total": total,
                    "genre_distribution": [
                        {
                            "genre": k,
                            "count": v,
                            "percentage": (round(v / total * 100, 1) if total else 0),
                        }
                        for k, v in genre_dist
                    ],
                    "era_breakdown": [{"era": k, "count": v} for k, v in era_dist],
                    "mood_breakdown": [{"mood": k, "count": v} for k, v in mood_dist],
                },
            }

        else:
            return {
                "success": False,
                "message": f"Unknown operation: {operation}",
                "data": {},
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Catalog script timed out", "data": {}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


def register_vinyl_tools(mcp: FastMCP):
    mcp.tool()(mixx_vinyl)
