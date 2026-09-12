"""DJ analytics, play history, and personal style profiling."""

from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..bridge.osc_bridge import get_bridge
from ..db import get_db, log_play, log_transition, style_profile, suggest_tracks

console = Console(file=__import__("sys").stderr)


async def mixx_history(
    operation: Literal["plays", "transitions", "profile", "suggest", "log_play", "log_transition"],
    deck: int = 1,
    track_path: str = "",
    track_title: str = "",
    track_artist: str = "",
    transition_type: str = "filter_sweep",
    from_deck: int = 1,
    to_deck: int = 2,
    limit: int = 20,
) -> dict[str, Any]:
    """
    DJ play history, analytics, and personal style profiling.

    PORTMANTEAU PATTERN: Consolidates analytics and history.

    SUPPORTED OPERATIONS:
    - plays: Recent play history
    - transitions: Recent transition log
    - profile: Personal DJ style profile (BPM range, key preferences, transition style)
    - suggest: Tracks you haven't played recently
    - log_play: Manually log a track play (auto-called by deck ops)
    - log_transition: Manually log a transition

    Examples:
        mixx_history("profile")
        mixx_history("suggest", limit=10)
        mixx_history("plays", limit=20)
    """
    try:
        db = get_db()

        if operation == "plays":
            cur = db.execute("SELECT * FROM play_history ORDER BY started_at DESC LIMIT ?", (limit,))
            plays = [dict(r) for r in cur.fetchall()]
            return {"success": True, "message": f"{len(plays)} recent plays", "data": {"plays": plays}}

        elif operation == "transitions":
            cur = db.execute("SELECT * FROM transitions_log ORDER BY timestamp DESC LIMIT ?", (limit,))
            trans = [dict(r) for r in cur.fetchall()]
            return {"success": True, "message": f"{len(trans)} recent transitions", "data": {"transitions": trans}}

        elif operation == "profile":
            profile = style_profile()
            return {"success": True, "message": "Style profile generated", "data": profile}

        elif operation == "suggest":
            suggestions = suggest_tracks(limit)
            return {
                "success": True,
                "message": f"{len(suggestions)} tracks to revisit",
                "data": {"tracks": suggestions},
            }

        elif operation == "log_play":
            bridge = get_bridge()
            bpm = bridge.get_state("bpm", deck, 0.0)
            key = bridge.get_state("key", deck, "")
            title = track_title or bridge.get_state("track_title", deck, "Unknown")
            artist = track_artist or bridge.get_state("track_artist", deck, "")
            log_play(deck, track_path, title, artist, float(bpm), str(key), 0.0)
            return {"success": True, "message": f"Logged play: {artist} - {title}"}

        elif operation == "log_transition":
            bridge = get_bridge()
            bpm_a = bridge.get_state("bpm", from_deck, 0.0)
            bpm_b = bridge.get_state("bpm", to_deck, 0.0)
            key_a = bridge.get_state("key", from_deck, "")
            key_b = bridge.get_state("key", to_deck, "")
            log_transition(
                None, from_deck, to_deck, transition_type, float(bpm_a), float(bpm_b), str(key_a), str(key_b)
            )
            return {"success": True, "message": f"Logged {transition_type} transition {from_deck} -> {to_deck}"}

    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}

    return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}


def register_history_tools(mcp: FastMCP):
    mcp.tool()(mixx_history)
