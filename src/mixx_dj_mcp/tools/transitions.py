from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..bridge.osc_bridge import get_bridge

console = Console(file=__import__("sys").stderr)

TRANSITION_EFFECTS: dict[str, str] = {
    "echo_out": "Progressive echo/delay on outgoing track",
    "filter_sweep": "Low-pass filter on outgoing, high-pass on incoming",
    "stem_swap": "Drop vocals from A, bring instrumental of B (needs stems)",
    "hard_cut": "Instant switch, club style",
    "spin_back": "Outgoing spins down like vinyl brake",
    "flanger": "Flanger sweep across both decks",
    "reverb_kill": "Reverb + delay on outgoing, then kill",
    "long_blend": "Slow EQ fade over 16-32 bars",
}


async def _llm_pick_transition(deck_a_info: dict, deck_b_info: dict, style: str) -> str:
    """Ask Ollama which transition fits the two tracks."""
    da, db = deck_a_info, deck_b_info
    da_genre = da.get("genre", "unknown")
    db_genre = db.get("genre", "unknown")
    prompt = (
        "You are an expert DJ choosing a transition between two tracks.\n\n"
        f"Deck A: {da['artist']} - {da['title']} "
        f"({da['bpm']} BPM, {da['key']}, genre: {da_genre})\n"
        f"Deck B: {db['artist']} - {db['title']} "
        f"({db['bpm']} BPM, {db['key']}, genre: {db_genre})\n\n"
        f"Style requested: {style}\n\nAvailable transitions:\n"
        "- echo_out: Progressive echo/delay on outgoing track only\n"
        "- filter_sweep: Low-pass filter on outgoing, high-pass on incoming\n"
        "- stem_swap: Drop vocals from A, bring instrumental of B\n"
        "- hard_cut: Instant switch, club style\n"
        "- spin_back: Outgoing spins down like vinyl brake\n"
        "- flanger: Flanger sweep across both decks\n"
        "- reverb_kill: Reverb + delay on outgoing, then kill\n"
        "- long_blend: Slow EQ fade over 16-32 bars\n\n"
        "Respond with ONLY the transition name, nothing else."
    )
    try:
        import httpx

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                },
            )
            if r.status_code == 200:
                choice = r.json().get("response", "").strip()
                if choice in TRANSITION_EFFECTS:
                    return choice
    except Exception:
        console.print("[yellow]Ollama transition suggestion failed[/yellow]")
    return "filter_sweep"


async def mixx_transition(
    operation: Literal["suggest", "apply", "auto_crossfader"],
    deck_a: int = 1,
    deck_b: int = 2,
    style: str = "any",
    effect: str = "",
    duration_beats: int = 8,
    enable: bool | None = None,
) -> dict[str, Any]:
    """
    AI-powered transitions between decks.

    PORTMANTEAU PATTERN: Consolidates creative transition effects.

    SUPPORTED OPERATIONS:
    - suggest: Ask LLM to suggest best transition for the two loaded tracks
    - apply: Apply a specific transition effect between decks
    - auto_crossfader: Enable/disable AI-assisted crossfader (auto-picks transitions)

    Available effects:
        echo_out, filter_sweep, stem_swap, hard_cut, spin_back, flanger, reverb_kill, long_blend

    Returns:
        Dict with transition result

    Examples:
        mixx_transition("suggest", deck_a=1, deck_b=2)
        mixx_transition("apply", deck_a=1, deck_b=2, effect="filter_sweep")
        mixx_transition("auto_crossfader", enable=True)
    """
    try:
        bridge = get_bridge()

        if operation == "suggest":
            info_a = {
                "artist": bridge.get_state("track_artist", deck_a, "Unknown"),
                "title": bridge.get_state("track_title", deck_a, "Unknown"),
                "bpm": bridge.get_state("bpm", deck_a, 128),
                "key": bridge.get_state("key", deck_a, "Unknown"),
            }
            info_b = {
                "artist": bridge.get_state("track_artist", deck_b, "Unknown"),
                "title": bridge.get_state("track_title", deck_b, "Unknown"),
                "bpm": bridge.get_state("bpm", deck_b, 128),
                "key": bridge.get_state("key", deck_b, "Unknown"),
            }

            choice = await _llm_pick_transition(info_a, info_b, style)
            reason = TRANSITION_EFFECTS.get(choice, "")
            return {
                "success": True,
                "message": f"Suggested transition: {choice} — {reason}",
                "data": {
                    "deck_a": info_a,
                    "deck_b": info_b,
                    "suggested_effect": choice,
                    "reason": reason,
                    "effects": {k: v for k, v in TRANSITION_EFFECTS.items()},
                },
            }

        elif operation == "apply":
            eff = effect or "filter_sweep"

            if eff == "echo_out":
                bridge.send(f"/deck/{deck_a}/filterHigh", 0.0)
                bridge.send(f"/deck/{deck_a}/rate_temp", 0.98)
                bridge.send(f"/deck/{deck_b}/filterHigh", 1.0)

            elif eff == "filter_sweep":
                for _ in range(4):
                    bridge.send(f"/deck/{deck_a}/filterLow", 0.0)
                    bridge.send(f"/deck/{deck_a}/filterHigh", 0.0)
                bridge.send(f"/deck/{deck_b}/filterLow", 1.0)
                bridge.send(f"/deck/{deck_b}/filterHigh", 1.0)

            elif eff == "hard_cut":
                bridge.send(f"/deck/{deck_a}/volume", 0.0)
                bridge.send(f"/deck/{deck_b}/volume", 1.0)

            elif eff == "spin_back":
                bridge.send(f"/deck/{deck_a}/rate_temp", -0.5)
                bridge.send(f"/deck/{deck_b}/play", 1.0)

            elif eff == "flanger":
                bridge.send(f"/deck/{deck_a}/rate_temp", 1.02)
                bridge.send(f"/deck/{deck_b}/rate_temp", 0.98)

            elif eff == "reverb_kill":
                bridge.send(f"/deck/{deck_a}/filterLow", 0.5)
                bridge.send(f"/deck/{deck_a}/volume", 0.0)
                bridge.send(f"/deck/{deck_b}/play", 1.0)

            elif eff == "long_blend":
                bridge.send(f"/deck/{deck_a}/filterHigh", 0.3)
                bridge.send(f"/deck/{deck_b}/filterLow", 0.7)

            else:
                return {"success": False, "message": f"Unknown effect: {eff}", "data": {}}

            return {
                "success": True,
                "message": f"Applied {eff} transition from deck {deck_a} to deck {deck_b}",
                "data": {"effect": eff, "deck_a": deck_a, "deck_b": deck_b},
            }

        elif operation == "auto_crossfader":
            if enable is None:
                return {"success": False, "message": "enable required", "data": {}}
            bridge.send("/mixer/auto_transition", 1.0 if enable else 0.0)
            return {
                "success": True,
                "message": f"AI crossfader {'enabled' if enable else 'disabled'}",
                "data": {"auto_transition": enable},
            }

        else:
            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

    except Exception as e:
        console.print(f"[red]Error in mixx_transition: {e}[/red]")
        return {"success": False, "message": str(e), "data": {}}


def register_transition_tools(mcp: FastMCP):
    mcp.tool()(mixx_transition)
