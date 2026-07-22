import os
import sys
import time
from pathlib import Path

import httpx
import uvicorn
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


from .tools import register_all_tools  # noqa: E402

register_all_tools(mcp)

_registered_tool_count = (
    len(mcp._tool_manager._tools) if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools") else 0
)

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
    get_osc_bridge()
    return {
        "status": "ok",
        "server": config.mcp_name,
        "version": "0.1.0",
        "uptime_seconds": get_uptime(),
        "tool_count": get_tool_count(),
        "tools": [
            {"name": "mixx_deck"},
            {"name": "mixx_library"},
            {"name": "mixx_effects"},
            {"name": "mixx_mixer"},
            {"name": "show_deck_status_card"},
            {"name": "show_mixer_status_card"},
            {"name": "show_library_status_card"},
        ],
        "system": {"windows": True},
        "errors": [],
    }


@fastapi_app.get("/api/deck/status")
async def deck_status():
    bridge = get_osc_bridge()
    decks = []
    for d in range(1, 5):
        decks.append(
            {
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
            }
        )
    return {"decks": decks, "crossfader": bridge.get_global_state("crossfader", 0.0)}


# Music generation — lazy-loaded MusicGen via HuggingFace
_music_model = None

async def _ensure_music_model():
    global _music_model
    if _music_model is not None:
        return _music_model
    try:
        from transformers import AutoProcessor, MusicGenForConditionalGeneration
        import torch
        processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        model = MusicGenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        _music_model = (processor, model, device)
        console.print(f"[green]MusicGen loaded on {device}[/green]")
    except Exception as e:
        console.print(f"[yellow]MusicGen load failed: {e}[/yellow]")
        _music_model = False  # sentinel
    return _music_model


@fastapi_app.post("/api/music/generate")
async def music_generate(body: dict):
    """Generate music using MusicGen (HuggingFace). First call loads model (~2GB)."""
    prompt = body.get("prompt", "")
    duration = int(body.get("duration", 15))
    if not prompt:
        return {"error": "prompt required"}

    result = await _ensure_music_model()
    if not result:
        return {"error": "MusicGen model not available. Install with: uv add transformers torch scipy"}

    processor, model, device = result
    try:
        import torch, scipy.io.wavfile, tempfile, os
        inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
        audio_values = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=int(duration * 50))

        out_dir = tempfile.mkdtemp()
        out_path = os.path.join(out_dir, "generated.wav")
        sampling_rate = model.config.audio_encoder.sampling_rate
        scipy.io.wavfile.write(out_path, rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())

        return {"success": True, "file": out_path, "duration": duration, "prompt": prompt, "model": "musicgen-small", "device": device}
    except Exception as e:
        return {"error": str(e)}


@fastapi_app.get("/api/llm/discover")
async def llm_discover():
    """Detect local LLM provider."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://localhost:11434/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                return {"provider": "ollama", "host": "localhost:11434", "status": "online", "models": [m["name"] for m in models]}
    except Exception:
        pass
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://localhost:1234/api/v1/models")
            if r.status_code == 200:
                return {"provider": "lmstudio", "host": "localhost:1234", "status": "online", "models": []}
    except Exception:
        pass
    return {"provider": "none", "status": "offline", "models": []}


@fastapi_app.get("/api/v1/fork")
async def fork_info():
    """Detect whether connected DJ software is mixxxxx (video fork) or vanilla Mixxx."""
    bridge = get_osc_bridge()
    # Probe for mixxxxx-specific COs
    has_video = bridge.get_state("video_enabled", 1, default=None) is not None
    has_phase = bridge.get_state("phase", 1, default=None) is not None
    has_export = bridge.get_state("export_rekordbox", 1, default=None) is not None
    return {
        "fork": "mixxxxx" if (has_video or has_phase) else "mixxx",
        "connected": bridge.is_connected(),
        "features": {
            "video": has_video,
            "phase_indicator": has_phase,
            "rekordbox_export": has_export,
            "serato_export": True,  # always available in mixxxxx build
            "virtualdj_export": True,
            "stem_separation": False,  # option-gated
        },
        "message": "mixxxxx detected" if has_video else "vanilla Mixxx detected (mixxxxx features unavailable)",
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


async def _try_execute_command(msg: str) -> dict | None:
    """Try to execute a DJ command from natural language. Returns response dict if matched."""
    bridge = get_osc_bridge()
    msg_lower = msg.lower()
    deck_match = re.search(r"deck\s*(\d)", msg_lower)
    deck = int(deck_match.group(1)) if deck_match else 1

    if ("load" in msg_lower and ("track" in msg_lower or "song" in msg_lower)):
        return {"message": "Use the Library page to search and click 'Load to N' to send the track path via the REST API."}

    if "play" in msg_lower and "pause" not in msg_lower:
        bridge.send(f"/deck/{deck}/play", 1.0)
        return {"message": f"Playing deck {deck}.", "executed": True, "deck": deck}
    if "stop" in msg_lower:
        bridge.send(f"/deck/{deck}/play", 0.0)
        return {"message": f"Stopped deck {deck}.", "executed": True, "deck": deck}
    if "sync" in msg_lower:
        bridge.send(f"/deck/{deck}/sync_enabled", 1.0)
        return {"message": f"Sync enabled on deck {deck}.", "executed": True, "deck": deck}

    if "crossfader" in msg_lower or "fade" in msg_lower:
        val = 0.0
        if "left" in msg_lower: val = -1.0
        elif "right" in msg_lower: val = 1.0
        bridge.send("/crossfader", val)
        return {"message": f"Crossfader set to {val}.", "executed": True}

    if "cue" in msg_lower:
        bridge.send(f"/deck/{deck}/cue_play", 1.0)
        return {"message": f"Cue triggered on deck {deck}.", "executed": True, "deck": deck}

    if "bpm" in msg_lower:
        bpm = bridge.get_state("bpm", deck, 128.0)
        return {"message": f"Deck {deck} BPM: {bpm}", "data": {"bpm": bpm, "deck": deck}}

    if "volume" in msg_lower and "deck" in msg_lower:
        val = 0.8
        for word in msg_lower.split():
            w = word.replace("%", "").replace("pct", "")
            try:
                pct = float(w)
                if pct > 1: val = pct / 100
                else: val = pct
            except: pass
        bridge.send(f"/deck/{deck}/volume", min(1.0, max(0.0, val)))
        return {"message": f"Deck {deck} volume set to {val:.0%}.", "executed": True, "deck": deck, "volume": val}

    return None


@fastapi_app.post("/api/llm/chat")
async def llm_chat(body: dict):
    """Chat endpoint — executes commands via OSC, falls back to Ollama."""
    messages = body.get("messages", [])
    model = body.get("model", "llama3.2:3b")
    user_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")

    # Execute commands first, regardless of LLM status
    cmd_result = await _try_execute_command(user_msg)
    if cmd_result:
        return cmd_result

    # Try local Ollama with requested model
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post("http://localhost:11434/api/chat", json={
                "model": model,
                "messages": messages,
                "stream": False,
            })
            if r.status_code == 200:
                reply = r.json().get("message", {}).get("content", "")
                return {"message": reply}
    except Exception:
        pass

    # Ollama failed — not a command, not an LLM request
    return {"message": "Not recognized as a DJ command and no LLM available. Try: 'play deck 1', 'sync deck 2', 'crossfader left', 'load track to deck 1' from Library."}


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
