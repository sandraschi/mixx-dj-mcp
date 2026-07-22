"""DAW cross-connection — export stems/sessions to Reaper, Fairlight, Resolume, or disk."""
from typing import Any, Literal
from pathlib import Path
import os
import json
import httpx
from datetime import datetime

from fastmcp import FastMCP
from rich.console import Console

console = Console(file=__import__("sys").stderr)

DAVINCI_RESOLVE_API = os.getenv("DAVINCI_RESOLVE_API", "http://127.0.0.1:10843")
REAPER_API = os.getenv("REAPER_API", "http://127.0.0.1:10797")
RESOLUME_API = os.getenv("RESOLUME_MCP_API", "http://127.0.0.1:0")  # MCP stdio — use OSC directly


def register_daw_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_daw(
        operation: Literal["export_stems", "export_session", "send_to_fairlight", "send_to_reaper", "resolume_sync"],
        source_dir: str = "",
        output_dir: str = "",
        session_name: str = "",
        stems: list[str] | None = None,
        target_bpm: float = 0,
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
                                console.print(f"  [yellow]Fairlight import failed for {wav.name}: {r.status_code}[/yellow]")
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
                                console.print(f"  [yellow]Reaper import failed for {wav.name}: {r.status_code}[/yellow]")
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
                bpm = bridge.get_state("bpm", deck, 128.0)
                playing = bridge.get_state("play", deck, 0.0)
                volume = bridge.get_state("volume", deck, 0.8)

                try:
                    from pythonosc import udp_client
                    client = udp_client.SimpleUDPClient("127.0.0.1", 7000)
                    # Resolume OSC address space
                    client.send_message("/composition/tempo", float(bpm))
                    client.send_message("/composition/bpm", float(bpm))
                    client.send_message(f"/deck/{deck}/playing", 1.0 if playing else 0.0)
                    client.send_message(f"/deck/{deck}/volume", float(volume))
                    return {
                        "success": True,
                        "message": f"Sent BPM {bpm} to Resolume on port 7000",
                        "data": {"bpm": bpm, "playing": bool(playing), "deck": deck},
                    }
                except ImportError:
                    return {"success": False, "message": "python-osc not installed", "data": {}}
                except Exception as e:
                    return {"success": False, "message": f"Resolume OSC error: {e}", "data": {}}

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            console.print(f"[red]Error in mixx_daw: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}
