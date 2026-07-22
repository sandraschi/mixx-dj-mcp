from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..bridge.osc_bridge import get_bridge

console = Console(file=__import__("sys").stderr)


async def mixx_library(
    operation: Literal[
        "search",
        "browse_crate",
        "browse_playlist",
        "load_selected",
        "get_track_info",
        "get_bpm",
        "get_key",
        "get_replay_gain",
    ],
    query: str = "",
    playlist: str | None = None,
    crate: str | None = None,
    deck: int = 1,
    track_index: int = 1,
) -> dict[str, Any]:
    """
    Library management for Mixxx.

    PORTMANTEAU PATTERN: Consolidates all library browsing and track info tools.

    SUPPORTED OPERATIONS:
    - search: Search the library for tracks (requires query)
    - browse_crate: Browse tracks in a crate (requires crate)
    - browse_playlist: Browse tracks in a playlist (requires playlist)
    - load_selected: Load highlighted/selected track to deck
    - get_track_info: Get metadata for current track on deck (requires deck)
    - get_bpm: Get BPM of track on deck (requires deck)
    - get_key: Get musical key of track on deck (requires deck)
    - get_replay_gain: Get replay gain values for track on deck (requires deck)

    Returns:
        Dict with operation result

    Examples:
        mixx_library("search", query="Daft Punk")
        mixx_library("load_selected", deck=1)
        mixx_library("get_track_info", deck=1)
    """
    try:
        bridge = get_bridge()

        if operation == "search":
            if not query:
                return {"success": False, "message": "query required for search", "data": {}}
            bridge.send("/library/search", query)
            return {"success": True, "message": f"Searching library for: {query}", "data": {"query": query}}

        elif operation == "browse_crate":
            if not crate:
                return {"success": False, "message": "crate name required for browse_crate", "data": {}}
            bridge.send(f"/library/crate/{crate}/select", 1.0)
            return {"success": True, "message": f"Browsing crate: {crate}", "data": {"crate": crate}}

        elif operation == "browse_playlist":
            if not playlist:
                return {"success": False, "message": "playlist name required for browse_playlist", "data": {}}
            bridge.send(f"/library/playlist/{playlist}/select", 1.0)
            return {"success": True, "message": f"Browsing playlist: {playlist}", "data": {"playlist": playlist}}

        elif operation == "load_selected":
            bridge.send("/library/load_selected", float(deck))
            return {"success": True, "message": f"Loading selected track to deck {deck}", "data": {"deck": deck}}

        elif operation == "get_track_info":
            info = bridge.get_state("track_info", deck, {})
            return {"success": True, "message": f"Track info for deck {deck}", "data": {"deck": deck, "info": info}}

        elif operation == "get_bpm":
            bpm = bridge.get_state("bpm", deck, 0.0)
            return {"success": True, "message": f"Deck {deck} BPM: {bpm}", "data": {"deck": deck, "bpm": bpm}}

        elif operation == "get_key":
            key = bridge.get_state("key", deck, "Unknown")
            return {"success": True, "message": f"Deck {deck} key: {key}", "data": {"deck": deck, "key": key}}

        elif operation == "get_replay_gain":
            gain = bridge.get_state("replay_gain", deck, {})
            return {"success": True, "message": f"Deck {deck} replay gain", "data": {"deck": deck, "replay_gain": gain}}

        else:
            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

    except Exception as e:
        console.print(f"[red]Error in mixx_library: {e}[/red]")
        return {"success": False, "message": str(e), "data": {}}


def register_library_tools(mcp: FastMCP):
    mcp.tool()(mixx_library)
