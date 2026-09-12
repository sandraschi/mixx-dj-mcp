"""Query the local Mixxx / mixxxxx SQLite library for track search."""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

_BPM_RE = re.compile(r"\b(\d{2,3})\s*bpm\b", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def get_mixxx_db_path() -> Path | None:
    """Resolve mixxxdb.sqlite from env or common install locations."""
    explicit = os.environ.get("MIXXX_DB_PATH") or os.environ.get("MIXXX_DATABASE_PATH")
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return path

    settings = os.environ.get("MIXXX_SETTINGS_PATH")
    if settings:
        candidate = Path(settings).expanduser() / "mixxxdb.sqlite"
        if candidate.is_file():
            return candidate

    local_app = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        Path(local_app) / "Mixxx" / "mixxxdb.sqlite",
        Path(local_app) / "mixxxxx" / "mixxxdb.sqlite",
        Path(local_app) / "Mixxxxx" / "mixxxdb.sqlite",
        Path.home() / "AppData" / "Local" / "Mixxx" / "mixxxdb.sqlite",
        Path.home() / "AppData" / "Local" / "mixxxxx" / "mixxxdb.sqlite",
        Path.home() / ".mixxx" / "mixxxdb.sqlite",
        Path.home() / ".mixxxxx" / "mixxxdb.sqlite",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def format_duration(seconds: float | int | None) -> str:
    if seconds is None:
        return "0:00"
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    return f"{minutes}:{secs:02d}"


def _parse_query(query: str) -> tuple[float | None, float | None, list[str]]:
    """Extract optional BPM range and remaining keyword tokens."""
    bpm_min: float | None = None
    bpm_max: float | None = None
    remaining = query

    bpm_match = _BPM_RE.search(query)
    if bpm_match:
        center = float(bpm_match.group(1))
        bpm_min = max(0.0, center - 2.0)
        bpm_max = center + 2.0
        remaining = _BPM_RE.sub(" ", remaining)

    tokens = [t.lower() for t in _TOKEN_RE.findall(remaining) if len(t) >= 2]
    return bpm_min, bpm_max, tokens


def search_library(query: str, *, limit: int = 50, db_path: Path | str | None = None) -> dict:
    """
    Search the Mixxx library database.

    Returns:
        {
            "results": [{"id", "title", "artist", "bpm", "key", "length"}, ...],
            "total": int,
            "database": str | None,
            "message": str,
        }
    """
    query = (query or "").strip()
    if not query:
        return {"results": [], "total": 0, "database": None, "message": "query required"}

    limit = max(1, min(int(limit), 200))
    path = Path(db_path) if db_path else get_mixxx_db_path()
    if path is None or not path.is_file():
        return {
            "results": [],
            "total": 0,
            "database": None,
            "message": ("Mixxx library database not found. Set MIXXX_DB_PATH or scan tracks in Mixxx first."),
        }

    bpm_min, bpm_max, tokens = _parse_query(query)

    sql = """
        SELECT
            track_locations.location AS path,
            library.title,
            library.artist,
            library.bpm,
            library.key,
            library.duration
        FROM library
        INNER JOIN track_locations ON library.location = track_locations.id
        WHERE library.mixxx_deleted = 0
          AND track_locations.fs_deleted = 0
    """
    params: list[object] = []

    if bpm_min is not None and bpm_max is not None:
        sql += " AND library.bpm BETWEEN ? AND ?"
        params.extend([bpm_min, bpm_max])

    for token in tokens:
        like = f"%{token}%"
        sql += (
            " AND (LOWER(library.title) LIKE ?"
            " OR LOWER(library.artist) LIKE ?"
            " OR LOWER(library.album) LIKE ?"
            " OR LOWER(library.genre) LIKE ?)"
        )
        params.extend([like, like, like, like])

    sql += " ORDER BY library.artist COLLATE NOCASE, library.title COLLATE NOCASE LIMIT ?"
    params.append(limit)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.Error as exc:
        return {
            "results": [],
            "total": 0,
            "database": str(path),
            "message": f"Library query failed: {exc}",
        }
    finally:
        conn.close()

    results = []
    for row in rows:
        results.append(
            {
                "id": row["path"] or "",
                "title": row["title"] or "Unknown",
                "artist": row["artist"] or "Unknown",
                "bpm": float(row["bpm"] or 0.0),
                "key": row["key"] or "Unknown",
                "length": format_duration(row["duration"]),
            }
        )

    return {
        "results": results,
        "total": len(results),
        "database": str(path),
        "message": f"Found {len(results)} track(s)",
    }
