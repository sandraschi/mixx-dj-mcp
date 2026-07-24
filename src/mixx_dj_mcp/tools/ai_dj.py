"""AI Autonomous Mix Agent — plan, perform, and review DJ sets via ctx.sample()."""

from typing import Any, Literal

from fastmcp import FastMCP, Context
from rich.console import Console

from ..bridge.osc_bridge import get_bridge
from ..db import get_db, log_transition

console = Console(file=__import__("sys").stderr)


async def mixx_ai_set(
    operation: Literal["plan", "suggest_next", "perform_transition", "review_set"],
    ctx: Context = None,
    style: str = "tech house",
    duration_minutes: int = 60,
    start_bpm: float = 126,
    end_bpm: float = 132,
    energy_curve: str = "build_peak_cool",
    deck_a: int = 1,
    deck_b: int = 2,
) -> dict[str, Any]:
    """
    AI Autonomous Mix Agent using MCP sampling.

    Uses ctx.sample() for autonomous reasoning about set structure, track selection,
    and transition timing. Falls back to rule-based execution when sampling is unavailable.

    PORTMANTEAU PATTERN: Consolidates AI set planning and performance.

    SUPPORTED OPERATIONS:
    - plan: Generate a structured DJ set plan (BPM curve, energy arc, genre flow)
    - suggest_next: Given current deck state, suggest the next track and transition
    - perform_transition: Execute an AI-chosen transition between two decks
    - review_set: Analyze a completed or hypothetical set for improvement ideas

    Examples:
        mixx_ai_set("plan", style="drum and bass", duration_minutes=30)
        mixx_ai_set("suggest_next", deck_a=1)
        mixx_ai_set("perform_transition", deck_a=1, deck_b=2)
    """
    try:
        bridge = get_bridge()

        if operation == "plan":
            prompt = (
                f"You are an expert DJ planning a {duration_minutes}-minute set in the '{style}' genre. "
                f"Start BPM: {start_bpm}, end BPM: {end_bpm}, energy curve: {energy_curve}.\n\n"
                f"Create a set plan with:\n"
                f"1. A BPM progression curve (list BPM at 0%, 25%, 50%, 75%, 100%)\n"
                f"2. 5-8 suggested tracks or track characteristics (BPM, key, energy level, role)\n"
                f"3. Transition types between each section (filter_sweep, echo_out, hard_cut, long_blend, etc.)\n"
                f"4. Energy arc description (when to build, peak, cool down)\n"
                f"5. Overall key progression strategy\n\n"
                f"Return as structured JSON with fields: bpm_curve, tracks, transitions, energy_arc, key_strategy"
            )
            result = ""
            if ctx and hasattr(ctx, "sample"):
                try:
                    result = await ctx.sample(prompt)
                except Exception:
                    result = ""
            if not result:
                result = _rule_plan(style, duration_minutes, start_bpm, end_bpm, energy_curve)
            return {
                "success": True,
                "message": f"Set plan for {style}, {duration_minutes}min",
                "data": {"plan": result, "style": style},
            }

        elif operation == "suggest_next":
            info_a = {
                "title": bridge.get_state("track_title", deck_a, "Unknown"),
                "artist": bridge.get_state("track_artist", deck_a, "Unknown"),
                "bpm": bridge.get_state("bpm", deck_a, 128),
                "key": bridge.get_state("key", deck_a, "Unknown"),
            }
            info_b = {
                "title": bridge.get_state("track_title", deck_b, "Unknown"),
                "artist": bridge.get_state("track_artist", deck_b, "Unknown"),
                "bpm": bridge.get_state("bpm", deck_b, 128),
                "key": bridge.get_state("key", deck_b, "Unknown"),
            }
            prompt = (
                f"Deck A is playing: {info_a['artist']} - {info_a['title']} ({info_a['bpm']} BPM, {info_a['key']})\n"
                f"Deck B has: {info_b['artist']} - {info_b['title']} ({info_b['bpm']} BPM, {info_b['key']})\n\n"
                f"What transition should I use between these two tracks? Consider BPM difference, "
                f"key compatibility (Camelot wheel), and energy levels.\n"
                f"Choose from: echo_out, filter_sweep, stem_swap, hard_cut, spin_back, flanger, reverb_kill, long_blend\n"
                f"Respond with: {{'transition': 'name', 'reason': 'explanation', 'bpm_match': true/false, 'key_compatible': true/false}}"
            )
            suggestion = ""
            if ctx and hasattr(ctx, "sample"):
                try:
                    suggestion = await ctx.sample(prompt)
                except Exception:
                    suggestion = ""
            if not suggestion:
                suggestion = '{"transition": "filter_sweep", "reason": "Safe all-purpose transition", "bpm_match": false, "key_compatible": false}'
            return {
                "success": True,
                "message": f"Suggested transition for {info_a['artist']} -> {info_b['artist']}",
                "data": {"deck_a": info_a, "deck_b": info_b, "suggestion": suggestion},
            }

        elif operation == "perform_transition":
            from ..tools.transitions import TRANSITION_EFFECTS

            prompt = (
                f"Deck A ({deck_a}) is playing and needs to transition to Deck B ({deck_b}). "
                f"Available transitions: {', '.join(TRANSITION_EFFECTS.keys())}.\n"
                f"Choose the best one for this situation. Respond with just the transition name."
            )
            choice = "filter_sweep"
            if ctx and hasattr(ctx, "sample"):
                try:
                    result = await ctx.sample(prompt)
                    if result and result.strip() in TRANSITION_EFFECTS:
                        choice = result.strip()
                except Exception:
                    pass

            if choice == "echo_out":
                bridge.send(f"/deck/{deck_a}/filterHigh", 0.0)
                bridge.send(f"/deck/{deck_a}/rate_temp", 0.98)
                bridge.send(f"/deck/{deck_b}/filterHigh", 1.0)
            elif choice == "filter_sweep":
                bridge.send(f"/deck/{deck_a}/filterLow", 0.0)
                bridge.send(f"/deck/{deck_a}/filterHigh", 0.0)
                bridge.send(f"/deck/{deck_b}/filterLow", 1.0)
                bridge.send(f"/deck/{deck_b}/filterHigh", 1.0)
            elif choice == "hard_cut":
                bridge.send(f"/deck/{deck_a}/volume", 0.0)
                bridge.send(f"/deck/{deck_b}/volume", 1.0)
            elif choice == "spin_back":
                bridge.send(f"/deck/{deck_a}/rate_temp", -0.5)
                bridge.send(f"/deck/{deck_b}/play", 1.0)
            elif choice == "flanger":
                bridge.send(f"/deck/{deck_a}/rate_temp", 1.02)
                bridge.send(f"/deck/{deck_b}/rate_temp", 0.98)
            elif choice == "reverb_kill":
                bridge.send(f"/deck/{deck_a}/filterLow", 0.5)
                bridge.send(f"/deck/{deck_a}/volume", 0.0)
                bridge.send(f"/deck/{deck_b}/play", 1.0)
            elif choice == "long_blend":
                bridge.send(f"/deck/{deck_a}/filterHigh", 0.3)
                bridge.send(f"/deck/{deck_b}/filterLow", 0.7)

            bridge.send(f"/deck/{deck_b}/play", 1.0)
            log_transition(None, deck_a, deck_b, choice, 0, 0, "", "")
            return {
                "success": True,
                "message": f"AI performed '{choice}' transition from deck {deck_a} to deck {deck_b}",
                "data": {"transition": choice},
            }

        elif operation == "review_set":
            db = get_db()
            plays = db.execute("SELECT COUNT(*) as cnt FROM play_history").fetchone()[0]
            trans = db.execute("SELECT COUNT(*) as cnt FROM transitions_log").fetchone()[0]
            prompt = (
                f"A DJ set has {plays} tracked plays and {trans} logged transitions. "
                f"Give 3 concise tips for improving DJ sets based on these stats. "
                f"Focus on: transition variety, BPM management, and energy flow."
            )
            review = ""
            if ctx and hasattr(ctx, "sample"):
                try:
                    review = await ctx.sample(prompt)
                except Exception:
                    review = ""
            if not review:
                review = "Play more tracks, try different transition types, and vary your BPM range."
            return {
                "success": True,
                "message": "Set review generated",
                "data": {"plays": plays, "transitions": trans, "review": review},
            }

    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}

    return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}


def _rule_plan(style: str, duration: int, start_bpm: float, end_bpm: float, energy_curve: str) -> str:
    bpm_step = (end_bpm - start_bpm) / 4
    return json.dumps(
        {
            "bpm_curve": [
                start_bpm,
                round(start_bpm + bpm_step, 1),
                round(start_bpm + bpm_step * 2, 1),
                round(start_bpm + bpm_step * 3, 1),
                end_bpm,
            ],
            "tracks": [
                {"position": "0%", "bpm": start_bpm, "role": "opener", "energy": "medium"},
                {"position": "25%", "bpm": round(start_bpm + bpm_step, 1), "role": "build", "energy": "medium-high"},
                {"position": "50%", "bpm": round(start_bpm + bpm_step * 2, 1), "role": "peak", "energy": "high"},
                {"position": "75%", "bpm": round(start_bpm + bpm_step * 3, 1), "role": "maintain", "energy": "high"},
                {"position": "100%", "bpm": end_bpm, "role": "cool-down", "energy": "medium"},
            ],
            "transitions": ["long_blend", "filter_sweep", "hard_cut", "echo_out", "long_blend"],
            "energy_arc": energy_curve,
            "key_strategy": "Move in Camelot wheel steps for harmonic mixing",
        },
        indent=2,
    )


import json  # noqa: E402


def register_ai_tools(mcp: FastMCP):
    mcp.tool()(mixx_ai_set)
