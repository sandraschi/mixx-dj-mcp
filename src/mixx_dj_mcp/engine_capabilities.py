"""Feature matrix for Mixxx (vanilla) vs mixxxxx (video fork)."""

from __future__ import annotations

from typing import Any, Literal

from .mixxx_launcher import ENGINE_MIXXX, ENGINE_MIXXXXX, MixxxProcessInfo, get_process_info

ForkId = Literal["mixxxxx", "mixxx", "unknown"]

# Features only available in mixxxxx (video fork build)
MIXXXXX_ONLY: frozenset[str] = frozenset(
    {
        "video_deck",
        "video_fullscreen",
        "ndi_output",
        "video_skins",
        "stem_separation",
        "stem_swap_transitions",
        "rekordbox_export",
        "phase_indicator",
        "help_video",
        "help_ndi",
        "help_av_rig",
    }
)

# Requires live OSC (both forks when configured)
OSC_FEATURES: frozenset[str] = frozenset(
    {
        "osc_deck_control",
        "deck_load",
        "effects_racks",
        "hotcues",
        "crossfader",
        "video_deck",
        "video_fullscreen",
        "library_load",
    }
)

_last_launch_engine: str | None = None


def set_last_launch_engine(engine: str) -> None:
    global _last_launch_engine
    if engine in (ENGINE_MIXXX, ENGINE_MIXXXXX):
        _last_launch_engine = engine


def infer_fork_from_process(proc: MixxxProcessInfo) -> ForkId:
    if not proc.running or not proc.exe:
        return "unknown"
    exe_lower = proc.exe.lower().replace("/", "\\")
    if "mixxxxx" in exe_lower or "\\repos\\mixxxxx\\" in exe_lower:
        return "mixxxxx"
    if "\\program files" in exe_lower and "mixxx" in exe_lower:
        return "mixxx"
    # Dev build under mixxxxx tree but binary still named mixxx.exe
    if "\\mixxxxx\\" in exe_lower:
        return "mixxxxx"
    return "mixxx"


def resolve_fork(
    *,
    proc: MixxxProcessInfo,
    osc_connected: bool,
    osc_has_video_co: bool,
    osc_has_phase_co: bool,
) -> ForkId:
    if osc_connected and (osc_has_video_co or osc_has_phase_co):
        return "mixxxxx"
    inferred = infer_fork_from_process(proc)
    if inferred != "unknown":
        return inferred
    if _last_launch_engine in (ENGINE_MIXXX, ENGINE_MIXXXXX):
        return _last_launch_engine  # type: ignore[return-value]
    return "unknown"


def _feature_entry(
    available: bool,
    enabled: bool,
    reason: str | None = None,
) -> dict[str, Any]:
    return {"available": available, "enabled": enabled, "reason": reason}


def build_capabilities(
    *,
    fork: ForkId,
    process_running: bool,
    osc_connected: bool,
    osc_detected: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Return UI-ready capability map for the webapp."""
    osc_detected = osc_detected or {}
    is_mixxxxx = fork == "mixxxxx"
    is_vanilla = fork == "mixxx"
    fork_unknown = fork == "unknown"

    def gate(feature_id: str) -> dict[str, Any]:
        needs_osc = feature_id in OSC_FEATURES
        mixxxxx_only = feature_id in MIXXXXX_ONLY

        if fork_unknown and not process_running:
            return _feature_entry(
                available=False,
                enabled=False,
                reason="Launch Mixxx or mixxxxx and connect OSC",
            )

        if is_vanilla and mixxxxx_only:
            return _feature_entry(
                available=False,
                enabled=False,
                reason="Requires mixxxxx (video fork) — vanilla Mixxx has no video/stem/NDI stack",
            )

        if needs_osc and not osc_connected:
            return _feature_entry(
                available=True,
                enabled=False,
                reason="Enable OSC in Mixxx Preferences (in 11119, out 11118) and probe connection",
            )

        if mixxxxx_only and not is_mixxxxx and not fork_unknown:
            return _feature_entry(
                available=False,
                enabled=False,
                reason="Requires mixxxxx (video fork)",
            )

        return _feature_entry(available=True, enabled=True, reason=None)

    features = {
        "osc_deck_control": gate("osc_deck_control"),
        "deck_load": gate("deck_load"),
        "effects_racks": gate("effects_racks"),
        "hotcues": gate("hotcues"),
        "crossfader": gate("crossfader"),
        "library_load": gate("library_load"),
        "video_deck": gate("video_deck"),
        "video_fullscreen": gate("video_fullscreen"),
        "ndi_output": gate("ndi_output"),
        "video_skins": gate("video_skins"),
        "stem_separation": gate("stem_separation"),
        "stem_swap_transitions": gate("stem_swap_transitions"),
        "rekordbox_export": gate("rekordbox_export"),
        "phase_indicator": gate("phase_indicator"),
        "help_video": gate("help_video"),
        "help_ndi": gate("help_ndi"),
        "help_av_rig": gate("help_av_rig"),
    }

    # Refine from OSC-detected COs when connected
    if osc_connected and osc_detected.get("video"):
        features["video_deck"]["available"] = True
        features["video_deck"]["enabled"] = is_mixxxxx or fork_unknown

    summary = (
        "mixxxxx connected — full AV feature set"
        if is_mixxxxx and osc_connected
        else "Vanilla Mixxx — audio/OSC only; video/stems/NDI disabled"
        if is_vanilla
        else "Engine unknown — launch and probe OSC"
        if fork_unknown
        else "mixxxxx running — enable OSC to control decks"
        if is_mixxxxx and not osc_connected
        else "Mixxx running — connect OSC"
    )

    return {
        "fork": fork,
        "process_running": process_running,
        "osc_connected": osc_connected,
        "is_mixxxxx": is_mixxxxx,
        "is_vanilla": is_vanilla,
        "summary": summary,
        "features": features,
    }


def get_engine_capabilities(bridge) -> dict[str, Any]:
    proc = get_process_info()
    osc_connected = bridge.is_connected()
    has_video = bridge.get_state("video_enabled", 1, default=None) is not None if osc_connected else False
    has_phase = bridge.get_state("phase", 1, default=None) is not None if osc_connected else False
    fork = resolve_fork(
        proc=proc,
        osc_connected=osc_connected,
        osc_has_video_co=has_video,
        osc_has_phase_co=has_phase,
    )
    return build_capabilities(
        fork=fork,
        process_running=proc.running,
        osc_connected=osc_connected,
        osc_detected={"video": has_video, "phase": has_phase},
    )
