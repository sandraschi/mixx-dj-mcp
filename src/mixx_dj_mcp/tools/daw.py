"""DAW cross-connection — export stems/sessions to Reaper, Fairlight, Resolume, or disk."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import httpx
from fastmcp import FastMCP
from rich.console import Console

from ..bridge.osc_bridge import get_bridge

console = Console(file=__import__("sys").stderr)

DAVINCI_RESOLVE_API = os.getenv("DAVINCI_RESOLVE_API", "http://127.0.0.1:10843")
REAPER_API = os.getenv("REAPER_API", "http://127.0.0.1:10797")
RESOLUME_API = os.getenv("RESOLUME_MCP_API", "http://127.0.0.1:0")  # MCP stdio — use OSC directly


def register_daw_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_daw(
        operation: Literal[
            "export_stems",
            "export_session",
            "send_to_fairlight",
            "send_to_reaper",
            "resolume_sync",
            "visuals_connect",
            "visuals_trigger",
        ],
        source_dir: str = "",
        output_dir: str = "",
        session_name: str = "",
        stems: list[str] | None = None,
        target_bpm: float = 0,
        mode: str = "auto",
        effect: str = "",
        intensity: float = 0.5,
        deck_a: int = 1,
        deck_b: int = 2,
    ) -> dict[str, Any]:
        """
        Cross-connection between Mixx-DJ-MCP and DAWs (Fairlight, Reaper).

        PORTMANTEAU PATTERN: Consolidates DAW export operations.

        SUPPORTED OPERATIONS:
        - export_stems: Copy stem WAVs to a DAW project directory
        - export_session: Write a session metadata JSON for DAW import
        - send_to_fairlight: Send stems to DaVinci Resolve's Fairlight page via REST API
        - send_to_reaper: Send stems to Reaper via reaper-mcp REST API (POST /api/v1/project/import_media)
        - resolume_sync: Send deck BPM and play state to Resolume via OSC (port 7000)
        - visuals_connect: Start continuous audio-reactive visual sync to Resolume
        - visuals_trigger: Fire a one-shot visual effect (strobe, pulse, color_cycle, wave, particles)

        Returns:
            Dict with export result and file paths

        Examples:
            mixx_daw("export_stems", output_dir="D:/Projects/Gig/Stems")
            mixx_daw("export_session", session_name="Friday Gig", source_dir="D:/Stems")
            mixx_daw("send_to_fairlight", source_dir="D:/Stems", session_name="Friday Gig")
        """
        try:
            if operation == "export_stems":
                out = Path(output_dir or os.path.expanduser("~/Mixxx/Exports"))
                out.mkdir(parents=True, exist_ok=True)

                if source_dir and os.path.isdir(source_dir):
                    src = Path(source_dir)
                    copied = 0
                    for wav in src.rglob("*.wav"):
                        dest = out / wav.name
                        import shutil

                        shutil.copy2(str(wav), str(dest))
                        copied += 1
                    return {
                        "success": True,
                        "message": f"Exported {copied} stem files to {out}",
                        "data": {"output_dir": str(out), "files_copied": copied},
                    }

                return {"success": False, "message": "source_dir required", "data": {}}

            elif operation == "export_session":
                out = Path(output_dir or os.path.expanduser("~/Mixxx/Exports"))
                out.mkdir(parents=True, exist_ok=True)

                name = session_name or f"mixx-session-{datetime.now():%Y%m%d-%H%M%S}"
                metadata = {
                    "session": name,
                    "exported_at": datetime.now().isoformat(),
                    "bpm": target_bpm or 128,
                    "stems": stems or [],
                    "source": source_dir or "",
                }
                meta_file = out / f"{name}.mixx-session.json"
                meta_file.write_text(json.dumps(metadata, indent=2))

                return {
                    "success": True,
                    "message": f"Session '{name}' exported to {meta_file}",
                    "data": {"session_file": str(meta_file), "metadata": metadata},
                }

            elif operation == "send_to_fairlight":
                if not source_dir or not os.path.isdir(source_dir):
                    return {"success": False, "message": "source_dir required", "data": {}}

                src = Path(source_dir)
                wav_files = list(src.rglob("*.wav"))
                if not wav_files:
                    return {"success": False, "message": "No WAV files found in source_dir", "data": {}}

                api = DAVINCI_RESOLVE_API
                imported = []
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        for wav in wav_files:
                            r = await client.post(
                                f"{api}/api/v1/media/import",
                                json={"file_path": str(wav)},
                                timeout=30,
                            )
                            if r.status_code == 200:
                                imported.append(str(wav.name))
                            else:
                                console.print(
                                    f"  [yellow]Fairlight import failed for {wav.name}: {r.status_code}[/yellow]"
                                )
                except httpx.ConnectError:
                    return {
                        "success": False,
                        "message": f"DaVinci Resolve MCP not reachable at {api}. Is resolve-mcp running?",
                        "data": {"api_url": api, "files_found": len(wav_files)},
                    }

                return {
                    "success": True,
                    "message": f"Sent {len(imported)}/{len(wav_files)} stems to Fairlight",
                    "data": {"imported": imported, "total": len(wav_files), "api": api},
                }

            elif operation == "send_to_reaper":
                if not source_dir or not os.path.isdir(source_dir):
                    return {"success": False, "message": "source_dir required", "data": {}}

                src = Path(source_dir)
                wav_files = list(src.rglob("*.wav"))
                if not wav_files:
                    return {"success": False, "message": "No WAV files found in source_dir", "data": {}}

                api = REAPER_API
                imported = []
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        for wav in wav_files:
                            r = await client.post(
                                f"{api}/api/v1/project/import_media",
                                params={"file_path": str(wav)},
                                timeout=30,
                            )
                            if r.status_code == 200:
                                imported.append(str(wav.name))
                            else:
                                console.print(
                                    f"  [yellow]Reaper import failed for {wav.name}: {r.status_code}[/yellow]"
                                )
                except httpx.ConnectError:
                    return {
                        "success": False,
                        "message": f"Reaper MCP not reachable at {api}. Is reaper-mcp running?",
                        "data": {"api_url": api, "files_found": len(wav_files)},
                    }

                return {
                    "success": True,
                    "message": f"Sent {len(imported)}/{len(wav_files)} stems to Reaper",
                    "data": {"imported": imported, "total": len(wav_files), "api": api},
                }

            elif operation == "resolume_sync":
                """Send deck BPM and beat state to Resolume via OSC."""
                br = get_bridge()
                d = deck_a
                bpm = br.get_state("bpm", d, 128.0)
                playing = br.get_state("play", d, 0.0)
                volume = br.get_state("volume", d, 0.8)

                try:
                    from pythonosc import udp_client

                    client = udp_client.SimpleUDPClient("127.0.0.1", 7000)
                    client.send_message("/composition/tempo", float(bpm))
                    client.send_message("/composition/bpm", float(bpm))
                    client.send_message(f"/deck/{d}/playing", 1.0 if playing else 0.0)
                    client.send_message(f"/deck/{d}/volume", float(volume))
                    return {
                        "success": True,
                        "message": f"Sent BPM {bpm} to Resolume on port 7000",
                        "data": {"bpm": bpm, "playing": bool(playing), "deck": d},
                    }
                except ImportError:
                    return {"success": False, "message": "python-osc not installed", "data": {}}
                except Exception as e:
                    return {"success": False, "message": f"Resolume OSC error: {e}", "data": {}}

            elif operation == "visuals_connect":
                """Start continuous audio-reactive visual sync to Resolume."""
                try:
                    from pythonosc import udp_client

                    client = udp_client.SimpleUDPClient("127.0.0.1", 7000)

                    bridge = get_bridge()

                    bpm = bridge.get_state("bpm", deck_a, 128.0)
                    samples = bridge.get_state("track_samples", deck_a, 0.0)
                    sample_rate = bridge.get_state("track_samplerate", deck_a, 44100.0)
                    volume = bridge.get_state("volume", deck_a, 0.8)
                    pregain = bridge.get_state("pregain", deck_a, 1.0)

                    # Beat phase computation
                    beats_per_second = bpm / 60.0
                    seconds = samples / sample_rate if sample_rate > 0 else 0
                    total_beats = seconds * beats_per_second
                    beat_phase = total_beats % 1.0
                    energy = min(1.0, volume * pregain * 1.5)
                    beat_flash = 1.0 if beat_phase < 0.05 else max(0.0, 1.0 - (beat_phase * 2))

                    # Send to Resolume
                    client.send_message("/composition/tempo", float(bpm))
                    client.send_message("/composition/bpm", float(bpm))
                    client.send_message("/layer1/opacity", float(energy))
                    client.send_message("/layer1/effect1/param1", float(bpm / 200.0))
                    client.send_message("/layer1/effect1/param2", float(beat_phase))
                    client.send_message("/layer1/effect1/param3", float(energy))
                    client.send_message("/layer2/opacity", float(beat_flash))
                    client.send_message("/layer2/effect1/param1", float(beat_phase))

                    return {
                        "success": True,
                        "message": f"Audio-reactive visuals connected (BPM: {bpm}, energy: {energy:.2f}, mode: {mode})",
                        "data": {
                            "bpm": bpm,
                            "beat_phase": beat_phase,
                            "energy": energy,
                            "beat_flash": beat_flash,
                            "mode": mode,
                        },
                    }
                except ImportError:
                    return {"success": False, "message": "python-osc not installed", "data": {}}
                except Exception as e:
                    return {"success": False, "message": f"Visuals error: {e}", "data": {}}

            elif operation == "visuals_trigger":
                """Fire a one-shot visual effect."""
                effects = {"strobe", "pulse", "color_cycle", "wave", "particles"}
                if effect not in effects:
                    return {"success": False, "message": f"Unknown effect: {effect}. Options: {effects}", "data": {}}

                try:
                    from pythonosc import udp_client

                    client = udp_client.SimpleUDPClient("127.0.0.1", 7000)

                    intensity = max(0.0, min(1.0, intensity))

                    if effect == "strobe":
                        client.send_message("/layer2/opacity", intensity)
                        client.send_message("/layer2/effect1/param1", 0.0)
                    elif effect == "pulse":
                        client.send_message("/layer1/scale", 1.0 + intensity * 0.15)
                        client.send_message("/layer1/opacity", 1.0)
                    elif effect == "color_cycle":
                        client.send_message("/layer1/effect1/param3", 1.0)
                    elif effect == "wave":
                        client.send_message("/layer1/effect2/param1", intensity)
                    elif effect == "particles":
                        client.send_message("/layer3/opacity", 1.0)

                    return {
                        "success": True,
                        "message": f"Triggered visual effect: {effect} at {intensity:.2f}",
                        "data": {"effect": effect, "intensity": intensity},
                    }
                except ImportError:
                    return {"success": False, "message": "python-osc not installed", "data": {}}
                except Exception as e:
                    return {"success": False, "message": f"Visual trigger error: {e}", "data": {}}

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            console.print(f"[red]Error in mixx_daw: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}
