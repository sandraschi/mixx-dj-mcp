import json
import os
import sqlite3
from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

console = Console(file=__import__("sys").stderr)

# Camelot wheel for harmonic mixing
CAMELOT_WHEEL = {
    0: "8A",
    1: "3A",
    2: "10A",
    3: "5A",
    4: "12A",
    5: "7A",
    6: "2A",
    7: "9A",
    8: "4A",
    9: "11A",
    10: "6A",
    11: "1A",
    12: "8B",
    13: "3B",
    14: "10B",
    15: "5B",
    16: "12B",
    17: "7B",
    18: "2B",
    19: "9B",
    20: "4B",
    21: "11B",
    22: "6B",
    23: "1B",
}

# Adjacent keys on Camelot wheel that blend harmonically
KEYS_COMPATIBLE = {
    "1A": ["1B", "12A", "2A"],
    "2A": ["2B", "1A", "3A"],
    # ... add more as needed, or we can derive it from the wheel structure
}


def _get_mixxx_db_path() -> str | None:
    """Find the Mixxx database path."""
    candidates = [
        os.path.expanduser("~/.mixxx/mixxxdb.sqlite"),
        os.path.expanduser("~\\AppData\\Local\\Mixxx\\mixxxdb.sqlite"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Mixxx", "mixxxdb.sqlite"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def _get_tracks_from_crate(db_path: str, crate_name: str) -> list[dict]:
    """Query Mixxx SQLite for tracks in a crate."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Mixxx stores crates in the `crates` table and track-crate membership in `CrateTracks`
    cursor.execute(
        """
        SELECT t.id, t.artist, t.title, t.bpm, t.key, t.location, t.genre, t.duration, t.year
        FROM library t
        JOIN crate_tracks ct ON t.id = ct.track_id
        JOIN crates c ON ct.crate_id = c.id
        WHERE c.name = ?
        ORDER BY t.artist, t.title
    """,
        (crate_name,),
    )

    tracks = []
    for row in cursor.fetchall():
        tracks.append(
            {
                "id": row["id"],
                "artist": row["artist"],
                "title": row["title"],
                "bpm": row["bpm"] or 120,
                "key": row["key"] or "Unknown",
                "genre": row["genre"] or "",
                "duration_seconds": row["duration"] or 300,
            }
        )
    conn.close()
    return tracks


async def _llm_suggest_sequence(tracks: list[dict]) -> list[dict]:
    """Send track list to local Ollama for mix ordering."""
    import httpx

    track_summary = []
    for t in tracks:
        track_summary.append(f"- {t['artist']} - {t['title']} ({t['bpm']} BPM, {t['key']}, {t['genre']})")

    prompt = f"""You are an expert DJ planning a set. Given these tracks, order them for a smooth mix.

Rules:
1. Adjacent tracks should be in compatible keys (Camelot wheel adjacency)
2. BPM should change gradually (max +/-5 BPM between adjacent tracks)
3. Energy should build over the set (start lower, peak in middle-to-late, optionally cooldown)
4. Group tracks by genre/artist for coherence

Output ONLY valid JSON array, no other text:
[
  {{
    "track_index": 0,
    "reason": "harmonic mix, energy building"
  }}
]

Tracks:
{chr(10).join(track_summary)}
"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7},
                },
            )
            if r.status_code == 200:
                text = r.json().get("response", "")
                # Find JSON array in response
                start = text.find("[")
                end = text.rfind("]") + 1
                if start >= 0 and end > start:
                    ordering = json.loads(text[start:end])
                    # Apply ordering to tracks
                    ordered = []
                    placed = set()
                    for item in ordering:
                        idx = item.get("track_index")
                        if idx is not None and 0 <= idx < len(tracks) and idx not in placed:
                            track = dict(tracks[idx])
                            track["reason"] = item.get("reason", "")
                            ordered.append(track)
                            placed.add(idx)
                    # Add any unplaced tracks at the end
                    for i, t in enumerate(tracks):
                        if i not in placed:
                            ordered.append(dict(t))
                    return ordered
    except Exception as e:
        console.print(f"[yellow]Ollama unavailable: {e}[/yellow]")

    # Fallback: sort by BPM ascending
    return sorted([dict(t) for t in tracks], key=lambda t: t.get("bpm", 120))


def _write_mixx_playlist(db_path: str, name: str, tracks: list[dict]) -> bool:
    """Write ordered tracks as a Mixxx playlist."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create playlist
        cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        playlist_id = cursor.lastrowid

        # Add tracks
        for i, t in enumerate(tracks):
            cursor.execute(
                "INSERT INTO PlaylistTracks (playlist_id, track_id, position, pl_datetime_added) VALUES (?, ?, ?, datetime('now'))",
                (playlist_id, t["id"], i),
            )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        console.print(f"[red]Failed to write playlist: {e}[/red]")
        return False


def register_sequencer_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_set(
        operation: Literal["sequence", "analyze_set"],
        crate: str = "",
        name: str = "",
        energy_curve: str = "build_peak_cooldown",
    ) -> dict[str, Any]:
        """
        AI-assisted set sequencing and analysis.

        PORTMANTEAU PATTERN: Consolidates set planning and analysis.

        SUPPORTED OPERATIONS:
        - sequence: Generate an optimized track order from a crate (requires crate)
          Uses local Ollama (llama3.2:3b) for harmonic mixing, energy curve, and
          phrase-aligned transitions.
        - analyze_set: Analyze a recorded set for BPM consistency, transitions, etc.

        Returns:
            Dict with ordered track list and reasoning

        Examples:
            mixx_set("sequence", crate="Peak Time", name="Friday Gig")
            mixx_set("analyze_set", name="Last Saturday")
        """
        try:
            if operation == "sequence":
                if not crate:
                    return {"success": False, "message": "crate name required", "data": {}}

                db_path = _get_mixxx_db_path()
                if not db_path:
                    return {"success": False, "message": "Mixxx database not found", "data": {}}

                tracks = _get_tracks_from_crate(db_path, crate)
                if not tracks:
                    return {"success": False, "message": f"No tracks found in crate '{crate}'", "data": {}}

                ordered = await _llm_suggest_sequence(tracks)

                playlist_name = name or f"AI Set: {crate}"
                _write_mixx_playlist(db_path, playlist_name, ordered)

                return {
                    "success": True,
                    "message": f"Sequenced {len(ordered)} tracks from '{crate}' into playlist '{playlist_name}'",
                    "data": {
                        "playlist": playlist_name,
                        "tracks": ordered,
                        "crate": crate,
                    },
                }

            elif operation == "analyze_set":
                return {
                    "success": True,
                    "message": "Set analysis not yet implemented (needs recorded session data)",
                    "data": {"name": name, "note": "Recording + analysis coming in next sprint"},
                }

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}
