import os
import sys
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from pydantic import BaseModel
from rich.console import Console

from .bridge.osc_bridge import OscBridge
from .config import MixxConfig
from .http_app import create_app, mount_mcp

class DeckLoadRequest(BaseModel):
    track_path: str

class PlayPauseRequest(BaseModel):
    action: str = "toggle"

class CueRequest(BaseModel):
    mode: str = "cue"

console = Console(file=sys.stderr)

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

config = MixxConfig.from_env()
mcp = FastMCP(config.mcp_name)

_start_time = time.time()
_osc_bridge: OscBridge | None = None
_registered_tool_count = 0


def get_uptime() -> int:
    return int(time.time() - _start_time)


def get_osc_bridge() -> OscBridge:
    global _osc_bridge
    if _osc_bridge is None:
        _osc_bridge = OscBridge(config)
    return _osc_bridge


def get_tool_count() -> int:
    global _registered_tool_count
    return _registered_tool_count


from .tools import register_all_tools
register_all_tools(mcp)

_registered_tool_count = len(mcp._tool_manager._tools) if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools") else 0

fastapi_app = create_app(config)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:11116",
        "http://127.0.0.1:11116",
        "http://localhost:11117",
        "http://127.0.0.1:11117",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mount_mcp(fastapi_app, mcp, config)


@fastapi_app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "server": config.mcp_name,
        "version": "0.1.0",
        "uptime_seconds": get_uptime(),
        "tool_count": get_tool_count(),
        "providers": {"mixxx": get_osc_bridge().is_connected()},
    }


@fastapi_app.get("/api/v1/diagnostics")
async def diagnostics():
    bridge = get_osc_bridge()
    return {
        "status": "ok",
        "server": config.mcp_name,
        "version": "0.1.0",
        "uptime_seconds": get_uptime(),
        "tool_count": get_tool_count(),
        "tools": [{"name": "mixx_deck"}, {"name": "mixx_library"}, {"name": "mixx_effects"}, {"name": "mixx_mixer"}, {"name": "show_deck_status_card"}, {"name": "show_mixer_status_card"}, {"name": "show_library_status_card"}],
        "system": {"windows": True},
        "errors": [],
    }


@fastapi_app.get("/api/deck/status")
async def deck_status():
    bridge = get_osc_bridge()
    decks = []
    for d in range(1, 5):
        decks.append({
            "id": d,
            "playing": bool(bridge.get_state("play", d, 0.0)),
            "bpm": bridge.get_state("bpm", d, 128.0),
            "key": bridge.get_state("key", d, "Unknown"),
            "track_title": bridge.get_state("track_title", d, "No Track Loaded"),
            "track_artist": bridge.get_state("track_artist", d, ""),
            "volume": bridge.get_state("volume", d, 0.8),
            "gain": bridge.get_state("pregain", d, 1.0),
            "sync_enabled": bool(bridge.get_state("sync_enabled", d, 0.0)),
            "loop_enabled": bool(bridge.get_state("loop_enabled", d, 0.0)),
        })
    return {"decks": decks, "crossfader": bridge.get_global_state("crossfader", 0.0)}


@fastapi_app.get("/api/settings")
async def api_settings():
    return {
        "mixx_host": config.mixx_host,
        "osc_out_port": config.mixx_osc_out_port,
        "osc_in_port": config.mixx_osc_in_port,
        "http_host": config.http_host,
        "http_port": config.http_port,
    }


@fastapi_app.post("/api/v1/deck/{deck_id}/load")
async def deck_load(deck_id: int, req: DeckLoadRequest):
    bridge = get_osc_bridge()
    bridge.send(f"/deck/{deck_id}/LoadTrack", req.track_path)
    return {"success": True, "deck": deck_id, "track": req.track_path}

@fastapi_app.post("/api/v1/deck/{deck_id}/play_pause")
async def deck_play_pause(deck_id: int, req: PlayPauseRequest):
    bridge = get_osc_bridge()
    if req.action == "play":
        bridge.send(f"/deck/{deck_id}/play", 1.0)
    elif req.action == "pause":
        bridge.send(f"/deck/{deck_id}/play", 0.0)
    else:
        bridge.send(f"/deck/{deck_id}/play", 1.0)
    return {"success": True, "deck": deck_id, "action": req.action}

@fastapi_app.post("/api/v1/deck/{deck_id}/sync")
async def deck_sync(deck_id: int):
    bridge = get_osc_bridge()
    bridge.send(f"/deck/{deck_id}/sync_enabled", 1.0)
    return {"success": True, "deck": deck_id}

@fastapi_app.post("/api/v1/deck/{deck_id}/cue")
async def deck_cue(deck_id: int, req: CueRequest):
    bridge = get_osc_bridge()
    bridge.send(f"/deck/{deck_id}/cue_play", 1.0)
    return {"success": True, "deck": deck_id, "mode": req.mode}

app = fastapi_app


def main():
    port = os.environ.get("MCP_PORT") or os.environ.get("PORT") or os.environ.get("HTTP_PORT")

    console.print(f"[green]{config.mcp_name} starting...[/green]")

    bridge = get_osc_bridge()
    try:
        bridge.start()
        console.print(f"[blue]OSC bridge listening on :{config.mixx_osc_out_port}[/blue]")
    except Exception as e:
        console.print(f"[yellow]OSC bridge warning: {e}[/yellow]")

    if port:
        host = os.environ.get("MCP_HOST") or os.environ.get("HOST") or config.http_host
        console.print(f"[green]HTTP mode on {host}:{port}[/green]")
        uvicorn.run(app, host=host, port=int(port), log_level="info")
    else:
        console.print("[green]STDIO mode[/green]")
        try:
            mcp.run(transport="stdio")
        except KeyboardInterrupt:
            console.print("[yellow]Shutdown requested[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise

    try:
        bridge.stop()
    except Exception:
        pass
    console.print(f"[green]{config.mcp_name} stopped[/green]")


__all__ = ["app", "main", "mcp"]
