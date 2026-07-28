"""First-run readiness for mixx-dj-mcp + Mixxxxx."""

from __future__ import annotations

from dataclasses import dataclass

from .mixxx_launcher import detect_installations, get_process_info


@dataclass
class SetupStep:
    id: str
    label: str
    done: bool
    hint: str | None = None


def get_first_run_status(*, osc_connected: bool = False) -> dict:
    """
    User-facing checklist: install → launch → OSC.
    Most users fail at step 1 (no Mixxxxx path) without this.
    """
    installations = detect_installations()
    mixxxxx = next((i for i in installations if i.engine == "mixxxxx" and i.exists), None)
    mixxx = next((i for i in installations if i.engine == "mixxx" and i.exists), None)
    proc = get_process_info()
    dj_installed = mixxxxx is not None or mixxx is not None
    preferred = mixxxxx or mixxx

    steps = [
        SetupStep(
            id="install_mixxxxx",
            label="Install Mixxxxx (or set MIXXXXX_EXE in .env)",
            done=dj_installed,
            hint=None if dj_installed else "Build: mixxxxx/docs/INSTALLER.md · Dev: MIXXXXX_EXE= path to mixxx.exe",
        ),
        SetupStep(
            id="launch_dj",
            label="Launch Mixxxxx",
            done=proc.running,
            hint="Dashboard → Launch (OSC fleet shortcut if installed)",
        ),
        SetupStep(
            id="osc_connect",
            label="OSC connected (11119 / 11118)",
            done=osc_connected,
            hint="Launch mixxxxx with OSC flags or use mixxxxx-osc.cmd · then Probe OSC",
        ),
    ]

    ready = all(s.done for s in steps)

    return {
        "ready": ready,
        "mixxxxx_installed": mixxxxx is not None,
        "mixxx_vanilla_installed": mixxx is not None,
        "preferred_engine": preferred.engine if preferred else None,
        "preferred_path": preferred.path if preferred else None,
        "process_running": proc.running,
        "osc_connected": osc_connected,
        "steps": [{"id": s.id, "label": s.label, "done": s.done, "hint": s.hint} for s in steps],
        "user_message": (
            "Ready to DJ — open Library or use MCP tools."
            if ready
            else (steps[0].hint if not steps[0].done else (steps[1].hint if not steps[1].done else steps[2].hint))
        ),
    }
