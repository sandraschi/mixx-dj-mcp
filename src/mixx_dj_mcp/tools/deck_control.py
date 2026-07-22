from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..bridge.osc_bridge import get_bridge

console = Console(file=__import__("sys").stderr)


def register_deck_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_deck(
        operation: Literal[
            "play_pause", "stop", "load", "cue_set", "cue_play",
            "loop_activate", "loop_beat", "beatloop", "rate_set",
            "rate_temp", "sync_enable", "sync_leader", "seek",
            "scratch", "hotcue_activate", "quantize", "keylock",
        ],
        deck: int = 1,
        value: float | None = None,
        track_path: str | None = None,
        beats: int = 4,
        hotcue: int = 1,
        enable: bool | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive deck control for Mixxx.

        PORTMANTEAU PATTERN: Consolidates all deck playback and transport controls.

        SUPPORTED OPERATIONS:
        - play_pause: Toggle play/pause on deck
        - stop: Stop playback completely
        - load: Load a track to deck (requires track_path)
        - cue_set: Set cue point at current position
        - cue_play: Play from cue point
        - loop_activate: Toggle loop on/off (requires enable)
        - loop_beat: Set loop of specified beats (requires beats)
        - beatloop: Same as loop_beat
        - rate_set: Set playback rate/BPM adjustment (requires value, -1.0 to 1.0)
        - rate_temp: Temporary pitch bend (requires value, seconds)
        - sync_enable: Toggle sync lock (requires enable)
        - sync_leader: Set deck as sync leader (requires enable)
        - seek: Seek to position in seconds (requires value)
        - scratch: Enable/disable scratch mode (requires enable)
        - hotcue_activate: Activate hotcue by number (requires hotcue)
        - quantize: Toggle quantize mode (requires enable)
        - keylock: Toggle keylock (requires enable)

        Returns:
            Dict with operation result

        Examples:
            mixx_deck("play_pause", deck=1)
            mixx_deck("load", deck=1, track_path="C:/Music/track.mp3")
            mixx_deck("rate_set", deck=1, value=0.05)
            mixx_deck("loop_beat", deck=1, beats=8)
            mixx_deck("sync_enable", deck=2, enable=True)
            mixx_deck("hotcue_activate", deck=1, hotcue=3)
        """
        try:
            bridge = get_bridge()

            if operation == "play_pause":
                bridge.send(f"/deck/{deck}/play", 1.0)
                return {"success": True, "message": f"Deck {deck}: play/pause toggled", "data": {"deck": deck}}

            elif operation == "stop":
                bridge.send(f"/deck/{deck}/stop", 1.0)
                return {"success": True, "message": f"Deck {deck}: stopped", "data": {"deck": deck}}

            elif operation == "load":
                if not track_path:
                    return {"success": False, "message": "track_path required for load operation", "data": {}}
                bridge.send(f"/deck/{deck}/LoadTrack", track_path)
                return {"success": True, "message": f"Deck {deck}: loading track", "data": {"deck": deck, "track_path": track_path}}

            elif operation == "cue_set":
                bridge.send(f"/deck/{deck}/cue_set", 1.0)
                return {"success": True, "message": f"Deck {deck}: cue point set", "data": {"deck": deck}}

            elif operation == "cue_play":
                bridge.send(f"/deck/{deck}/cue_play", 1.0)
                return {"success": True, "message": f"Deck {deck}: playing from cue", "data": {"deck": deck}}

            elif operation == "loop_activate":
                if enable is None:
                    return {"success": False, "message": "enable required for loop_activate", "data": {}}
                bridge.send(f"/deck/{deck}/loop_enabled", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Deck {deck}: loop {'enabled' if enable else 'disabled'}", "data": {"deck": deck, "enable": enable}}

            elif operation in ("loop_beat", "beatloop"):
                beats_val = max(1, min(64, beats))
                bridge.send(f"/deck/{deck}/beatloop_{beats_val}", 1.0)
                return {"success": True, "message": f"Deck {deck}: {beats_val}-beat loop", "data": {"deck": deck, "beats": beats_val}}

            elif operation == "rate_set":
                if value is None:
                    return {"success": False, "message": "value required for rate_set (-1.0 to 1.0)", "data": {}}
                val = max(-1.0, min(1.0, value))
                bridge.send(f"/deck/{deck}/rate", val)
                return {"success": True, "message": f"Deck {deck}: rate set to {val:+.3f}", "data": {"deck": deck, "rate": val}}

            elif operation == "rate_temp":
                if value is None:
                    return {"success": False, "message": "value required for rate_temp (seconds)", "data": {}}
                bridge.send(f"/deck/{deck}/rate_temp", value)
                return {"success": True, "message": f"Deck {deck}: temporary pitch bend", "data": {"deck": deck, "duration": value}}

            elif operation == "sync_enable":
                if enable is None:
                    return {"success": False, "message": "enable required for sync_enable", "data": {}}
                bridge.send(f"/deck/{deck}/sync_enabled", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Deck {deck}: sync {'enabled' if enable else 'disabled'}", "data": {"deck": deck, "enable": enable}}

            elif operation == "sync_leader":
                if enable is None:
                    return {"success": False, "message": "enable required for sync_leader", "data": {}}
                bridge.send(f"/deck/{deck}/sync_leader", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Deck {deck}: sync leader {'set' if enable else 'unset'}", "data": {"deck": deck, "enable": enable}}

            elif operation == "seek":
                if value is None:
                    return {"success": False, "message": "value required for seek (seconds)", "data": {}}
                bridge.send(f"/deck/{deck}/seek", value)
                return {"success": True, "message": f"Deck {deck}: seeked to {value}s", "data": {"deck": deck, "position": value}}

            elif operation == "scratch":
                if enable is None:
                    return {"success": False, "message": "enable required for scratch", "data": {}}
                bridge.send(f"/deck/{deck}/scratch", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Deck {deck}: scratch {'enabled' if enable else 'disabled'}", "data": {"deck": deck, "enable": enable}}

            elif operation == "hotcue_activate":
                hotcue_num = max(1, min(8, hotcue))
                bridge.send(f"/deck/{deck}/hotcue_{hotcue_num}_activated", 1.0)
                return {"success": True, "message": f"Deck {deck}: hotcue {hotcue_num} activated", "data": {"deck": deck, "hotcue": hotcue_num}}

            elif operation == "quantize":
                if enable is None:
                    return {"success": False, "message": "enable required for quantize", "data": {}}
                bridge.send(f"/deck/{deck}/quantize", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Deck {deck}: quantize {'enabled' if enable else 'disabled'}", "data": {"deck": deck, "enable": enable}}

            elif operation == "keylock":
                if enable is None:
                    return {"success": False, "message": "enable required for keylock", "data": {}}
                bridge.send(f"/deck/{deck}/keylock", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Deck {deck}: keylock {'enabled' if enable else 'disabled'}", "data": {"deck": deck, "enable": enable}}

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            console.print(f"[red]Error in mixx_deck: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}
