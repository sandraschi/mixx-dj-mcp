"""Detect, launch, and monitor Mixxx / mixxxxx on Windows."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import psutil

logger = logging.getLogger(__name__)

ENGINE_MIXXX = "mixxx"
ENGINE_MIXXXXX = "mixxxxx"


# Installed paths first; dev tree last (user machines should not depend on D:\Dev\repos).
def _program_files() -> Path:
    return Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))


def _mixxxxx_candidates() -> list[Path]:
    pf = _program_files()
    return [
        pf / "Mixxxxx" / "mixxx.exe",
        Path(os.path.expandvars(r"%LOCALAPPDATA%\Mixxxxx\mixxx.exe")),
        Path(os.path.expandvars(r"%LOCALAPPDATA%\mixxxxx\mixxx.exe")),
        Path(r"D:\Dev\repos\mixxxxx\build\mixxx.exe"),
        Path(r"D:\Dev\repos\mixxxxx\build\Release\mixxx.exe"),
    ]


def _mixxx_candidates() -> list[Path]:
    pf = _program_files()
    pfx86 = Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))
    return [
        Path(pf / "Mixxx" / "mixxx.exe"),
        Path(pfx86 / "Mixxx" / "mixxx.exe"),
    ]


DEFAULT_CANDIDATES: dict[str, list[Path]] = {
    ENGINE_MIXXXXX: _mixxxxx_candidates(),
    ENGINE_MIXXX: _mixxx_candidates(),
}


def _osc_launcher_cmd(exe: str) -> Path | None:
    """Installer shortcut script (mixxxxx-osc.cmd) beside mixxx.exe."""
    cmd = Path(exe).parent / "mixxxxx-osc.cmd"
    return cmd if cmd.is_file() else None


@dataclass
class MixxxInstallation:
    engine: str
    path: str
    exists: bool
    source: str  # env | default | custom


@dataclass
class MixxxProcessInfo:
    running: bool
    pid: int | None
    exe: str | None


def _env_path(engine: str) -> Path | None:
    key = "MIXXXXX_EXE" if engine == ENGINE_MIXXXXX else "MIXXX_EXE"
    raw = os.getenv(key, "").strip()
    if raw:
        return Path(raw)
    return None


def detect_installations() -> list[MixxxInstallation]:
    """Return known Mixxx/mixxxxx executables (env overrides first)."""
    found: list[MixxxInstallation] = []
    seen: set[str] = set()

    for engine in (ENGINE_MIXXXXX, ENGINE_MIXXX):
        env_p = _env_path(engine)
        if env_p:
            resolved = str(env_p.resolve()) if env_p.exists() else str(env_p)
            if resolved not in seen:
                seen.add(resolved)
                found.append(
                    MixxxInstallation(
                        engine=engine,
                        path=resolved,
                        exists=env_p.is_file(),
                        source="env",
                    )
                )

        for candidate in DEFAULT_CANDIDATES.get(engine, []):
            if not candidate.is_file():
                continue
            resolved = str(candidate.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            found.append(
                MixxxInstallation(
                    engine=engine,
                    path=resolved,
                    exists=True,
                    source="default",
                )
            )

    return found


def get_process_info() -> MixxxProcessInfo:
    """True if mixxx.exe is running (vanilla or mixxxxx build)."""
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            name = (proc.info.get("name") or "").lower()
            if name != "mixxx.exe":
                continue
            exe = proc.info.get("exe") or ""
            return MixxxProcessInfo(running=True, pid=proc.info["pid"], exe=exe)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return MixxxProcessInfo(running=False, pid=None, exe=None)


def resolve_executable(engine: str, path: str | None = None) -> str | None:
    if path:
        p = Path(path)
        return str(p.resolve()) if p.is_file() else None
    env_p = _env_path(engine)
    if env_p and env_p.is_file():
        return str(env_p.resolve())
    for inst in detect_installations():
        if inst.engine == engine and inst.exists:
            return inst.path
    # mixxxxx fallback: any mixxxxx install when engine is mixxx
    if engine == ENGINE_MIXXX:
        for inst in detect_installations():
            if inst.engine == ENGINE_MIXXXXX and inst.exists:
                return inst.path
    return None


def launch_mixxx(
    engine: str = ENGINE_MIXXXXX,
    path: str | None = None,
    extra_args: list[str] | None = None,
    *,
    osc_port_in: int | None = None,
    osc_port_out: int | None = None,
    osc_host_out: str | None = None,
) -> dict:
    """
    Start Mixxx/mixxxxx detached. mixxxxx builds get OSC CLI flags when ports set.
    """
    if sys.platform != "win32":
        return {"success": False, "message": "Launch is only supported on Windows"}

    proc_info = get_process_info()
    if proc_info.running:
        return {
            "success": True,
            "already_running": True,
            "message": f"Mixxx already running (PID {proc_info.pid})",
            "pid": proc_info.pid,
            "exe": proc_info.exe,
        }

    exe = resolve_executable(engine, path)
    if not exe:
        return {
            "success": False,
            "message": (
                f"No {engine} executable found. Set MIXXXXX_EXE or MIXXX_EXE in .env, "
                "or pass path in the launch request."
            ),
        }

    pin = osc_port_in if osc_port_in is not None else 11119
    pout = osc_port_out if osc_port_out is not None else 11118
    host = (osc_host_out or "127.0.0.1").strip()

    osc_script = _osc_launcher_cmd(exe) if engine == ENGINE_MIXXXXX else None
    if osc_script is not None and not extra_args:
        # Installed Mixxxxx: mixxxxx-osc.cmd already sets fleet OSC defaults.
        args = ["cmd.exe", "/c", str(osc_script)]
    else:
        args = [exe]
        cli_extras: list[str] = list(extra_args or [])
        if engine == ENGINE_MIXXXXX:
            cli_extras.extend(
                [
                    f"--osc-port-in={pin}",
                    f"--osc-port-out={pout}",
                    f"--osc-host-out={host}",
                ]
            )
            if os.getenv("MIXXXXX_NDI_ENABLE", "").lower() in ("1", "true", "yes"):
                cli_extras.append("--ndi-enable")
        if cli_extras:
            args.extend(cli_extras)

    try:
        popen = subprocess.Popen(
            args,
            cwd=str(Path(exe).parent),
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
        logger.info("Launched Mixxx: %s (PID %s)", exe, popen.pid)
        from .engine_capabilities import set_last_launch_engine

        set_last_launch_engine(engine)
        if osc_script is not None:
            msg = f"Started Mixxxxx via mixxxxx-osc.cmd (OSC {pin}/{pout} → {host})"
        elif engine == ENGINE_MIXXXXX:
            msg = f"Started {Path(exe).name} — OSC in {pin}, out {pout} → {host} (mixxxxx CLI)"
        else:
            msg = f"Started {Path(exe).name} — enable OSC in Preferences (in {pin}, out {pout}, host {host})"
        return {
            "success": True,
            "message": msg,
            "pid": popen.pid,
            "path": exe,
            "engine": engine,
            "osc_port_in": pin,
            "osc_port_out": pout,
            "osc_host_out": host,
            "launcher": str(osc_script) if osc_script else exe,
        }
    except OSError as exc:
        logger.error("Failed to launch Mixxx: %s", exc)
        return {"success": False, "message": str(exc), "path": exe}


def installation_to_dict(inst: MixxxInstallation) -> dict:
    return {
        "engine": inst.engine,
        "path": inst.path,
        "exists": inst.exists,
        "source": inst.source,
    }
