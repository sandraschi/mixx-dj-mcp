from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..bridge.osc_bridge import get_bridge

console = Console(file=__import__("sys").stderr)


async def mixx_mixer(
        operation: Literal[
            "crossfader_set", "crossfader_curve", "gain_set",
            "eq_set", "volume_set", "headphone_cue",
            "talkover", "mic_gain",
        ],
        deck: int = 1,
        value: float | None = None,
        eq_band: Literal["high", "mid", "low"] | None = None,
        enable: bool | None = None,
    ) -> dict[str, Any]:
        """
        Mixer control for Mixxx.

        PORTMANTEAU PATTERN: Consolidates all mixer and channel strip operations.

        SUPPORTED OPERATIONS:
        - crossfader_set: Set crossfader position (requires value, -1.0 to 1.0)
        - crossfader_curve: Set crossfader curve (requires value, 0.0-1.0)
        - gain_set: Set deck gain/pregain (requires value, 0.0-5.0)
        - eq_set: Set EQ band for deck (requires eq_band, value 0.0-1.0)
        - volume_set: Set channel volume (requires value, 0.0-1.0)
        - headphone_cue: Toggle headphone cue for deck (requires enable)
        - talkover: Toggle talkover / microphone
        - mic_gain: Set microphone gain (requires value, 0.0-1.0)

        Returns:
            Dict with operation result

        Examples:
            mixx_mixer("crossfader_set", value=0.0)
            mixx_mixer("gain_set", deck=1, value=0.85)
            mixx_mixer("eq_set", deck=1, eq_band="low", value=0.5)
            mixx_mixer("headphone_cue", deck=1, enable=True)
        """
        try:
            bridge = get_bridge()

            if operation == "crossfader_set":
                if value is None:
                    return {"success": False, "message": "value required for crossfader (-1.0 to 1.0)", "data": {}}
                val = max(-1.0, min(1.0, value))
                bridge.send("/crossfader", val)
                return {"success": True, "message": f"Crossfader set to {val:+.2f}", "data": {"position": val}}

            elif operation == "crossfader_curve":
                if value is None:
                    return {"success": False, "message": "value required for curve (0.0-1.0)", "data": {}}
                val = max(0.0, min(1.0, value))
                bridge.send("/crossfader/curve", val)
                return {"success": True, "message": f"Crossfader curve set to {val:.2f}", "data": {"curve": val}}

            elif operation == "gain_set":
                if value is None:
                    return {"success": False, "message": "value required for gain (0.0-5.0)", "data": {}}
                val = max(0.0, min(5.0, value))
                bridge.send(f"/deck/{deck}/pregain", val)
                return {"success": True, "message": f"Deck {deck} gain set to {val:.2f}", "data": {"deck": deck, "gain": val}}

            elif operation == "eq_set":
                if eq_band is None or value is None:
                    return {"success": False, "message": "eq_band and value required", "data": {}}
                val = max(0.0, min(1.0, value))
                band_map = {"high": "filterHigh", "mid": "filterMid", "low": "filterLow"}
                cob = band_map[eq_band]
                bridge.send(f"/deck/{deck}/{cob}", val)
                return {"success": True, "message": f"Deck {deck} EQ {eq_band} set to {val:.2f}", "data": {"deck": deck, "band": eq_band, "value": val}}

            elif operation == "volume_set":
                if value is None:
                    return {"success": False, "message": "value required for volume (0.0-1.0)", "data": {}}
                val = max(0.0, min(1.0, value))
                bridge.send(f"/deck/{deck}/volume", val)
                return {"success": True, "message": f"Deck {deck} volume set to {val:.2f}", "data": {"deck": deck, "volume": val}}

            elif operation == "headphone_cue":
                if enable is None:
                    return {"success": False, "message": "enable required for headphone_cue", "data": {}}
                bridge.send(f"/deck/{deck}/pfl", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Deck {deck} headphone cue {'on' if enable else 'off'}", "data": {"deck": deck, "enable": enable}}

            elif operation == "talkover":
                bridge.send("/talkover", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Talkover {'enabled' if enable else 'disabled'}", "data": {"enable": enable}}

            elif operation == "mic_gain":
                if value is None:
                    return {"success": False, "message": "value required for mic gain (0.0-1.0)", "data": {}}
                val = max(0.0, min(1.0, value))
                bridge.send("/microphone/gain", val)
                return {"success": True, "message": f"Mic gain set to {val:.2f}", "data": {"gain": val}}

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            console.print(f"[red]Error in mixx_mixer: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}


def register_mixer_tools(mcp: FastMCP):
    mcp.tool()(mixx_mixer)
