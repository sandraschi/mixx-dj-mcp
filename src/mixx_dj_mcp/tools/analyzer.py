"""Real-time audio analysis using librosa — BPM, key, energy, cue points."""

import os
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..db import get_db, store_analysis

console = Console(file=__import__("sys").stderr)

_LIBROSA_OK = None


def _check_librosa() -> bool:
    global _LIBROSA_OK
    if _LIBROSA_OK is not None:
        return _LIBROSA_OK
    try:
        import librosa  # noqa: F401

        _LIBROSA_OK = True
    except ImportError:
        _LIBROSA_OK = False
    return _LIBROSA_OK


_KAM_KEY_PROFILES = {
    "C": [0.15, 0.01, 0.06, 0.05, 0.07, 0.06, 0.03, 0.11, 0.06, 0.02, 0.10, 0.08],
    "C#": [0.09, 0.14, 0.02, 0.08, 0.06, 0.09, 0.07, 0.03, 0.12, 0.06, 0.03, 0.10],
    "D": [0.11, 0.08, 0.15, 0.02, 0.07, 0.06, 0.08, 0.07, 0.03, 0.11, 0.06, 0.04],
    "D#": [0.06, 0.12, 0.08, 0.16, 0.02, 0.08, 0.05, 0.10, 0.07, 0.03, 0.11, 0.06],
    "E": [0.07, 0.06, 0.10, 0.08, 0.15, 0.02, 0.07, 0.07, 0.10, 0.06, 0.03, 0.10],
    "F": [0.10, 0.07, 0.07, 0.10, 0.08, 0.15, 0.02, 0.07, 0.08, 0.09, 0.06, 0.03],
    "F#": [0.04, 0.10, 0.07, 0.07, 0.10, 0.08, 0.15, 0.02, 0.07, 0.08, 0.10, 0.06],
    "G": [0.07, 0.03, 0.10, 0.06, 0.07, 0.10, 0.08, 0.15, 0.02, 0.07, 0.08, 0.09],
    "G#": [0.10, 0.08, 0.04, 0.11, 0.06, 0.07, 0.10, 0.08, 0.14, 0.02, 0.07, 0.09],
    "A": [0.10, 0.08, 0.07, 0.04, 0.10, 0.06, 0.07, 0.10, 0.08, 0.14, 0.02, 0.07],
    "A#": [0.09, 0.07, 0.09, 0.07, 0.04, 0.10, 0.06, 0.07, 0.10, 0.09, 0.14, 0.02],
    "B": [0.03, 0.10, 0.07, 0.10, 0.07, 0.04, 0.09, 0.06, 0.07, 0.10, 0.09, 0.14],
}
_CAMELOT = {
    "C": "8B",
    "C#": "3B",
    "D": "10B",
    "D#": "5B",
    "E": "12B",
    "F": "7B",
    "F#": "2B",
    "G": "9B",
    "G#": "4B",
    "A": "11B",
    "A#": "6B",
    "B": "1B",
    "Cm": "5A",
    "C#m": "12A",
    "Dm": "7A",
    "D#m": "2A",
    "Em": "9A",
    "Fm": "4A",
    "F#m": "11A",
    "Gm": "6A",
    "G#m": "1A",
    "Am": "8A",
    "A#m": "3A",
    "Bm": "10A",
}
_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _detect_key(chromagram) -> tuple[str, str]:
    correlations = {}
    for key_name, profile in _KAM_KEY_PROFILES.items():
        corr = sum(chromagram[i] * profile[i] for i in range(12))
        correlations[key_name] = corr
    best = max(correlations, key=correlations.get)
    alt_idx = (_NOTES.index(best) + 7) % 12
    alt = _NOTES[alt_idx]
    return best, alt


async def mixx_analyze(
    operation: Literal["track", "batch_status", "suggest_cues"],
    path: str = "",
    limit: int = 10,
) -> dict[str, Any]:
    """
    Audio analysis engine using librosa.

    PORTMANTEAU PATTERN: Consolidates audio analysis operations.

    SUPPORTED OPERATIONS:
    - track: Analyze a single audio file. Returns BPM, key, Camelot, energy, structure.
    - batch_status: Show how many tracks are analyzed vs pending.
    - suggest_cues: Suggest hotcue positions based on track structure.

    Returns:
        Dict with analysis results

    Examples:
        mixx_analyze("track", path="C:/Music/track.mp3")
        mixx_analyze("batch_status")
    """
    if not _check_librosa():
        return {"success": False, "message": "librosa not installed. Install with: uv add librosa", "data": {}}

    import librosa  # type: ignore

    if operation == "track":
        if not path or not os.path.exists(path):
            return {"success": False, "message": f"File not found: {path}", "data": {}}
        try:
            y, sr = librosa.load(path, sr=22050, mono=True, duration=300)
            duration = float(librosa.get_duration(y=y, sr=sr))

            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = round(float(tempo), 1)

            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_mean = chroma.mean(axis=1).tolist()
            key, key_alt = _detect_key(chroma_mean)

            spectral = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            energy = float(min(1.0, max(0.0, (spectral.mean() - 500) / 8000)))

            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=3, delta=0.4, wait=10)
            onset_times = librosa.times_like(onset_env)[peaks]
            section_count = min(len(onset_times) // 8, 10)

            camelot = _CAMELOT.get(key, "")
            camelot_alt = _CAMELOT.get(key_alt, "")

            store_analysis(path, bpm, key, key_alt, energy, duration)

            return {
                "success": True,
                "message": f"Analyzed: {Path(path).name} — {bpm} BPM, {key} ({camelot})",
                "data": {
                    "file": path,
                    "bpm": bpm,
                    "key": key,
                    "key_alternative": key_alt,
                    "camelot": camelot,
                    "camelot_alternative": camelot_alt,
                    "energy": round(energy, 3),
                    "duration_seconds": round(duration, 1),
                    "estimated_sections": section_count,
                },
            }
        except Exception as e:
            console.print(f"[red]Analyze error: {e}[/red]")
            return {"success": False, "message": f"Analysis failed: {e}", "data": {}}

    elif operation == "batch_status":
        db = get_db()
        analyzed = db.execute("SELECT COUNT(*) FROM track_analysis").fetchone()[0]
        return {
            "success": True,
            "message": f"{analyzed} tracks analyzed in database",
            "data": {"analyzed_tracks": analyzed},
        }

    elif operation == "suggest_cues":
        if not path or not os.path.exists(path):
            return {"success": False, "message": f"File not found: {path}", "data": {}}
        try:
            y, sr = librosa.load(path, sr=22050, mono=True, duration=300)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            peaks = librosa.util.peak_pick(onset_env, pre_max=5, post_max=5, pre_avg=5, post_avg=5, delta=0.5, wait=20)
            times = librosa.times_like(onset_env)[peaks]

            cues = []
            for t in times[1:6]:
                m, s = divmod(int(t), 60)
                cues.append({"position_seconds": round(t, 1), "label": f"{m:02d}:{s:02d}"})

            return {
                "success": True,
                "message": f"Suggested {len(cues)} cue points",
                "data": {"cues": cues, "total_candidates": len(times)},
            }
        except Exception as e:
            return {"success": False, "message": f"Cue detection failed: {e}", "data": {}}

    return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}


def register_analyzer_tools(mcp: FastMCP):
    mcp.tool()(mixx_analyze)
