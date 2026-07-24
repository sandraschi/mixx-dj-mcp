"""Live set recording, replay, and export."""

import json
import time
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..db import get_db

console = Console(file=__import__("sys").stderr)

_active_recording: dict | None = None
_recording_thread: Thread | None = None


def _get_sets_dir() -> Path:
    p = Path(__file__).parent.parent.parent.parent / "data" / "sets"
    p.mkdir(parents=True, exist_ok=True)
    return p


async def mixx_recording(
    operation: Literal["start", "stop", "list", "replay", "export", "status"],
    name: str = "",
    set_id: str = "",
    replay_speed: float = 1.0,
    loop: bool = False,
) -> dict[str, Any]:
    """
    Record, replay, and export DJ sets.

    PORTMANTEAU PATTERN: Consolidates set recording and replay.

    SUPPORTED OPERATIONS:
    - start: Begin recording OSC commands (name: set name)
    - stop: Stop recording and save
    - list: List recorded sets
    - replay: Replay a recorded set's OSC commands
    - export: Export set as JSON for external tools
    - status: Show current recording state

    Examples:
        mixx_recording("start", name="Club Night 2026-07-24")
        mixx_recording("stop")
        mixx_recording("list")
        mixx_recording("replay", set_id="...", replay_speed=0.5)
    """
    global _active_recording

    if operation == "start":
        if _active_recording:
            return {"success": False, "message": "Recording already in progress. Stop first.", "data": {}}
        set_id_val = datetime.utcnow().strftime("set_%Y%m%d_%H%M%S")
        path = _get_sets_dir() / f"{set_id_val}.jsonl"
        _active_recording = {
            "set_id": set_id_val,
            "name": name or f"Set {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "path": str(path),
            "started_at": datetime.utcnow().isoformat(),
            "events": 0,
            "file": open(path, "w", encoding="utf-8"),
        }
        db = get_db()
        db.execute(
            "INSERT INTO set_recordings (id, name, started_at, file_path) VALUES (?,?,?,?)",
            (set_id_val, _active_recording["name"], _active_recording["started_at"], str(path)),
        )
        db.commit()
        return {
            "success": True,
            "message": f"Recording '{_active_recording['name']}' — writing to {path.name}",
            "data": {"set_id": set_id_val, "path": str(path)},
        }

    elif operation == "stop":
        if not _active_recording:
            return {"success": False, "message": "No active recording", "data": {}}
        _active_recording["file"].close()
        ended = datetime.utcnow().isoformat()
        db = get_db()
        db.execute(
            "UPDATE set_recordings SET ended_at=?, osc_events=? WHERE id=?",
            (ended, _active_recording["events"], _active_recording["set_id"]),
        )
        db.commit()
        info = dict(_active_recording)
        _active_recording = None
        return {
            "success": True,
            "message": f"Recording stopped — {info['events']} OSC events captured",
            "data": {"set_id": info["set_id"], "events": info["events"], "path": info["path"]},
        }

    elif operation == "status":
        return {
            "success": True,
            "message": "Recording" if _active_recording else "Idle",
            "data": {
                "recording": _active_recording is not None,
                "set_id": _active_recording["set_id"] if _active_recording else None,
                "name": _active_recording["name"] if _active_recording else None,
                "events": _active_recording["events"] if _active_recording else 0,
            },
        }

    elif operation == "list":
        db = get_db()
        cur = db.execute(
            "SELECT id, name, started_at, ended_at, duration_seconds, track_count, transition_count, osc_events FROM set_recordings ORDER BY started_at DESC LIMIT 50"
        )
        sets = [dict(r) for r in cur.fetchall()]
        return {
            "success": True,
            "message": f"{len(sets)} recorded sets",
            "data": {"sets": sets},
        }

    elif operation == "replay":
        path = _get_sets_dir() / f"{set_id}.jsonl"
        if not path.exists():
            return {"success": False, "message": f"Set not found: {set_id}", "data": {}}
        try:
            from ..bridge.osc_bridge import get_bridge

            bridge = get_bridge()
            events = []
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
            for evt in events:
                addr = evt.get("address", "")
                val = evt.get("value", 0.0)
                bridge.send(addr, val)
                time.sleep((evt.get("beat_offset", 0) or 0) / replay_speed)
            return {
                "success": True,
                "message": f"Replayed {len(events)} events from {set_id}",
                "data": {"set_id": set_id, "events_replayed": len(events)},
            }
        except Exception as e:
            return {"success": False, "message": f"Replay failed: {e}", "data": {}}

    elif operation == "export":
        path = _get_sets_dir() / f"{set_id}.jsonl"
        if not path.exists():
            return {"success": False, "message": f"Set not found: {set_id}", "data": {}}
        events = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return {
            "success": True,
            "message": f"Exported {len(events)} events from {set_id}",
            "data": {"set_id": set_id, "events": events},
        }

    return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}


def record_osc_event(address: str, value: Any):
    """Called by the OSC bridge to record events during an active recording."""
    global _active_recording
    if not _active_recording:
        return
    try:
        evt = {
            "ts": time.time(),
            "address": address,
            "value": value,
        }
        _active_recording["file"].write(json.dumps(evt) + "\n")
        _active_recording["file"].flush()
        _active_recording["events"] += 1
    except Exception:
        pass


def register_recording_tools(mcp: FastMCP):
    mcp.tool()(mixx_recording)
