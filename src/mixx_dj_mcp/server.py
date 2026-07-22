import os
import sys
import time
from pathlib import Path

import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from rich.console import Console

from .bridge.osc_bridge import OscBridge
from .config import MixxConfig
from .http_app import create_app

console = Console(file=sys.stderr)

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

config = MixxConfig.from_env()
mcp = FastMCP(config.mcp_name)

_start_time = time.time()
_osc_bridge: OscBridge | None = None


def get_uptime() -> int:
    return int(time.time() - _start_time)


def get_osc_bridge() -> OscBridge:
    global _osc_bridge
    if _osc_bridge is None:
        _osc_bridge = OscBridge(config)
    return _osc_bridge


from .tools import register_all_tools
register_all_tools(mcp)

fastapi_app = create_app(config)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:11116",
        "http://127.0.0.1:11116",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.get("/api/health")
async def health_check():
    tool_count = len(mcp._tool_manager.tools) if hasattr(mcp, "_tool_manager") else 0
    return {
        "status": "ok",
        "server": config.mcp_name,
        "version": "0.1.0",
        "uptime_seconds": get_uptime(),
        "tool_count": tool_count,
        "providers": {"mixxx": get_osc_bridge().is_connected()},
    }


@fastapi_app.get("/api/v1/diagnostics")
async def diagnostics():
    tool_count = len(mcp._tool_manager.tools) if hasattr(mcp, "_tool_manager") else 0
    bridge = get_osc_bridge()
    tool_names = []
    if hasattr(mcp, "_tool_manager"):
        tool_names = [{"name": name} for name in mcp._tool_manager.tools.keys()]
    return {
        "status": "ok",
        "server": config.mcp_name,
        "version": "0.1.0",
        "uptime_seconds": get_uptime(),
        "tool_count": tool_count,
        "tools": tool_names,
        "system": {"windows": True},
        "errors": [],
    }


@fastapi_app.get("/api/settings")
async def api_settings():
    return {
        "mixx_host": config.mixx_host,
        "osc_out_port": config.mixx_osc_out_port,
        "osc_in_port": config.mixx_osc_in_port,
        "http_host": config.http_host,
        "http_port": config.http_port,
    }


app = fastapi_app


def main():
    console.print(f"[green]{config.mcp_name} MCP Server starting...[/green]")
    bridge = get_osc_bridge()
    try:
        bridge.start()
        console.print(f"[blue]OSC bridge listening on :{config.mixx_osc_out_port}[/blue]")
    except Exception as e:
        console.print(f"[yellow]OSC bridge warning: {e}[/yellow]")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        console.print("[yellow]MCP Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]MCP Server error: {e}[/red]")
        raise
    finally:
        try:
            bridge.stop()
        except Exception:
            pass
        console.print(f"[green]{config.mcp_name} MCP Server stopped[/green]")


__all__ = ["app", "main", "mcp"]
