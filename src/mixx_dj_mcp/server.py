import logging
import os
import re
import sys
import time
from pathlib import Path

import httpx
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastmcp import FastMCP
from pydantic import BaseModel
from rich.console import Console

from .bridge.osc_bridge import OscBridge
from .config import MixxConfig
from .http_app import create_app, mount_mcp

logger = logging.getLogger(__name__)


class DeckLoadRequest(BaseModel):
    track_path: str


class PlayPauseRequest(BaseModel):
    action: str = "toggle"


class CueRequest(BaseModel):
    mode: str = "cue"


class LibrarySearchRequest(BaseModel):
    query: str = ""
    limit: int = 50
    mode: str = "auto"  # auto | plex | mixxx | semantic
    include_mixxx: bool = True
    library_id: str | None = None
    media_type: str | None = None
    genre: str | None = None
    year: int | None = None
    min_year: int | None = None
    max_year: int | None = None
    collection: str | None = None
    actor: str | None = None
    director: str | None = None


class LibraryResolveRequest(BaseModel):
    track_ref: str


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict = {}


class EffectsRequest(BaseModel):
    operation: str
    rack: int = 1
    unit: int = 1
    effect: str | None = None
    parameter: int = 1
    value: float | None = None
    deck: int | None = None
    enable: bool = True


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


from . import (  # noqa: E402
    plex_client,
    sfx_client,
)
from .library_search import search_library_smart  # noqa: E402
from .tool_dispatch import build_tool_dispatch, dispatch_tool  # noqa: E402
from .tools import register_all_tools  # noqa: E402

register_all_tools(mcp)

_registered_tool_count = (
    len(mcp._tool_manager._tools) if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools") else 0
)
_tool_dispatch = build_tool_dispatch(mcp)

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
    try:
        tool_names = (
            sorted(mcp._tool_manager._tools.keys())
            if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools")
            else []
        )
    except Exception:
        tool_names = []
    return {
        "status": "ok",
        "server": config.mcp_name,
        "version": "0.1.0",
        "uptime_seconds": get_uptime(),
        "tool_count": len(tool_names),
        "tools": [{"name": t} for t in tool_names],
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


@fastapi_app.get("/api/library/plex/libraries")
async def library_plex_libraries():
    """List Plex libraries from plex-mcp (for filter dropdowns)."""
    if not await plex_client.plex_available(config.plex_mcp_url):
        return {"libraries": [], "plex_available": False}
    libraries = await plex_client.list_libraries(config.plex_mcp_url)
    return {"libraries": libraries, "plex_available": True}


@fastapi_app.post("/api/library/search")
async def library_search(req: LibrarySearchRequest):
    """Search via plex-mcp (filters, metadata, semantic) with Mixxx SQLite fallback."""
    query = req.query.strip()
    if not query and not any(
        [
            req.genre,
            req.year,
            req.library_id,
            req.collection,
            req.actor,
            req.director,
        ]
    ):
        return {"results": [], "total": 0, "message": "query or filters required"}

    result = await search_library_smart(
        query,
        limit=req.limit,
        mode=req.mode if req.mode in ("auto", "plex", "mixxx", "semantic") else "auto",
        include_mixxx=req.include_mixxx,
        library_id=req.library_id,
        media_type=req.media_type,
        genre=req.genre,
        year=req.year,
        min_year=req.min_year,
        max_year=req.max_year,
        collection=req.collection,
        actor=req.actor,
        director=req.director,
    )

    if query:
        bridge = get_osc_bridge()
        bridge.send("/library/search", query)

    return result


@fastapi_app.post("/api/library/resolve")
async def library_resolve(req: LibraryResolveRequest):
    """Resolve plex:rating_key to a local file path for deck load."""
    path = await plex_client.resolve_file_path(req.track_ref, config.plex_mcp_url)
    if not path:
        return {"success": False, "message": "Could not resolve track path", "path": None}
    return {"success": True, "path": path, "track_ref": req.track_ref}


@fastapi_app.get("/api/library/artwork/plex")
async def library_artwork_plex(path: str, width: int = 128, height: int = 128):
    """Proxy Plex thumb/poster art through mixx-dj-mcp (same-origin for the webapp)."""
    clean = path.lstrip("/")
    upstream = f"{config.plex_mcp_url.rstrip('/')}/api/image/{clean}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(upstream, params={"width": width, "height": height})
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg"),
            )
    except Exception as exc:
        logger.warning("Plex artwork proxy failed for %s: %s", clean, exc)
        return Response(status_code=404)


@fastapi_app.get("/api/library/artwork/calibre/{book_id}")
async def library_artwork_calibre(book_id: int):
    """Proxy Calibre book cover through mixx-dj-mcp."""
    calibre_url = os.getenv("CALIBRE_MCP_URL", "http://127.0.0.1:10720").rstrip("/")
    upstream = f"{calibre_url}/api/books/{book_id}/cover"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(upstream)
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg"),
            )
    except Exception as exc:
        logger.warning("Calibre cover proxy failed for book %s: %s", book_id, exc)
        return Response(status_code=404)


def _register_sfx_fleet_source() -> None:
    if sfx_client.get_sfx_mcp_url():
        _audio_sources["sfx"] = {
            "name": "sfx",
            "base_url": config.sfx_mcp_url,
            "capabilities": ["search", "download", "preview", "list_local"],
            "registered_at": time.time(),
            "status": "online",
        }


@fastapi_app.get("/api/sfx/status")
async def sfx_status():
    """sfx-mcp connectivity and FreeSound API key status."""
    status = await sfx_client.sfx_status(config.sfx_mcp_url)
    if status.get("available"):
        _register_sfx_fleet_source()
    return status


@fastapi_app.get("/api/sfx/search")
async def sfx_search_route(
    q: str,
    duration_max: int = 30,
    page: int = 1,
    tag: str | None = None,
):
    """Search FreeSound via sfx-mcp."""
    if not await sfx_client.sfx_available(config.sfx_mcp_url):
        return {
            "results": [],
            "total": 0,
            "message": "sfx-mcp offline — start on port 11120",
            "sfx_available": False,
        }
    try:
        payload = await sfx_client.search_sounds(
            q,
            duration_max=duration_max,
            page=page,
            tag=tag,
            base_url=config.sfx_mcp_url,
        )
        _register_sfx_fleet_source()
        return {
            **payload,
            "sfx_available": True,
        }
    except Exception as exc:
        logger.warning("SFX search failed: %s", exc)
        return {
            "results": [],
            "total": 0,
            "message": str(exc),
            "sfx_available": True,
        }


@fastapi_app.post("/api/sfx/download")
async def sfx_download_route(body: dict):
    """Download a sound through sfx-mcp to local cache."""
    sound_id = body.get("sound_id")
    if not sound_id:
        return {"success": False, "message": "sound_id required"}
    try:
        result = await sfx_client.download_sound(
            int(sound_id),
            destination=body.get("destination"),
            base_url=config.sfx_mcp_url,
        )
        _register_sfx_fleet_source()
        return result
    except Exception as exc:
        return {"success": False, "message": str(exc)}


@fastapi_app.get("/api/sfx/local")
async def sfx_local_route(tag: str | None = None):
    """List locally cached sfx-mcp sounds."""
    if not await sfx_client.sfx_available(config.sfx_mcp_url):
        return {"results": [], "total": 0, "sfx_available": False}
    try:
        payload = await sfx_client.list_local_sounds(tag=tag, base_url=config.sfx_mcp_url)
        return {**payload, "sfx_available": True}
    except Exception as exc:
        return {"results": [], "total": 0, "message": str(exc), "sfx_available": True}


@fastapi_app.post("/api/v1/tools/call")
async def tools_call(req: ToolCallRequest):
    """Invoke a registered MCP tool from the webapp or scripts."""
    result = await dispatch_tool(_tool_dispatch, req.name, req.arguments)
    return {"success": True, "tool": req.name, "result": result}


@fastapi_app.post("/api/v1/effects")
async def effects_action(req: EffectsRequest):
    """Apply an effect rack operation via mixx_effects."""
    payload = req.model_dump(exclude_none=True)
    result = await dispatch_tool(_tool_dispatch, "mixx_effects", payload)
    if isinstance(result, dict) and result.get("success") is False:
        return {"success": False, "message": result.get("message", "effect failed"), "data": result.get("data", {})}
    return result


# Music generation — lazy-loaded MusicGen via HuggingFace
_music_model = None


async def _ensure_music_model():
    global _music_model
    if _music_model is not None:
        return _music_model
    try:
        import torch
        from transformers import AutoProcessor, MusicGenForConditionalGeneration

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
    """Generate music — tries: Lyria (Vertex AI) → MusicGen (local) → songgeneration-mcp."""
    prompt = body.get("prompt", "")
    duration = int(body.get("duration", 15))
    if not prompt:
        return {"error": "prompt required"}

    # Backend 1: Lyria (Google Vertex AI, requires GOOGLE_CLOUD_PROJECT)
    try:
        from google import genai
        from google.genai import types

        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if project:
            client = genai.Client(vertexai=True, project=project, location="global")
            import os as _os
            import tempfile

            out_dir = tempfile.mkdtemp()
            out_path = _os.path.join(out_dir, "lyria.wav")
            response = client.models.generate_content(
                model="lyria-3-pro-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    audio_timestamp=True,
                    output_audio_format="wav",
                ),
            )
            if response.candidates and response.candidates[0].audio:
                with open(out_path, "wb") as f:
                    f.write(response.candidates[0].audio.data)
                return {
                    "success": True,
                    "file": out_path,
                    "duration": duration,
                    "prompt": prompt,
                    "model": "lyria-3-pro-preview",
                    "backend": "lyria",
                }
    except Exception as e:
        console.print(f"[yellow]Lyria failed: {e}[/yellow]")

    # Backend 2: MusicGen (local HuggingFace, first load downloads ~2GB)
    result = await _ensure_music_model()
    if result:
        try:
            processor, model, device = result
            import os as _os
            import tempfile

            import scipy.io.wavfile

            inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
            audio_values = model.generate(
                **inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=int(duration * 50)
            )
            out_dir = tempfile.mkdtemp()
            out_path = _os.path.join(out_dir, "generated.wav")
            sampling_rate = model.config.audio_encoder.sampling_rate
            scipy.io.wavfile.write(out_path, rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())
            return {
                "success": True,
                "file": out_path,
                "duration": duration,
                "prompt": prompt,
                "model": "musicgen-small",
                "backend": "musicgen",
            }
        except Exception as e:
            console.print(f"[yellow]MusicGen failed: {e}[/yellow]")

    # Backend 3: songgeneration-mcp (cloud Studio API)
    try:
        import httpx

        r = await httpx.AsyncClient(timeout=120).post(
            "http://127.0.0.1:10885/api/v1/generate", json={"prompt": prompt, "duration": duration}
        )
        if r.status_code == 200:
            data = r.json()
            data["backend"] = "songgen-studio"
            return data
    except Exception as e:
        console.print(f"[yellow]songgeneration-mcp failed: {e}[/yellow]")

    return {
        "error": (
            "All music generation backends failed. "
            "Try: uv add transformers torch scipy (MusicGen) "
            "or set GOOGLE_CLOUD_PROJECT (Lyria)"
        ),
    }


@fastapi_app.get("/api/llm/discover")
async def llm_discover():
    """Detect local LLM provider(s)."""
    providers = []

    async def _probe(name: str, port: int, probe_path: str, model_path: str | None = None):
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                r = await client.get(f"http://localhost:{port}{probe_path}")
                if r.status_code == 200:
                    models = []
                    if model_path:
                        raw = r.json()
                        for key in model_path.split("."):
                            raw = raw.get(key, []) if isinstance(raw, dict) else []
                        models = [m.get("name") or m.get("id") or "" for m in raw if isinstance(m, dict)]
                    providers.append({"name": name, "port": port, "status": "detected", "models": models})
                    return
        except Exception:
            logger.debug("%s probe failed on port %d", name, port)
        providers.append({"name": name, "port": port, "status": "not_found", "models": []})

    await _probe("ollama", 11434, "/api/tags", "models")
    await _probe("lmstudio", 1234, "/v1/models", "data")
    await _probe("vllm", 8000, "/v1/models", "data")

    return {"providers": providers}


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
    track_path = await plex_client.resolve_file_path(req.track_path, config.plex_mcp_url)
    if not track_path:
        return {"success": False, "deck": deck_id, "message": "Could not resolve track path", "track": req.track_path}
    bridge.send(f"/deck/{deck_id}/LoadTrack", track_path)
    return {"success": True, "deck": deck_id, "track": track_path}


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

    if "load" in msg_lower and ("track" in msg_lower or "song" in msg_lower):
        return {
            "message": "Use the Library page to search and click 'Load to N' to send the track path via the REST API."
        }

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
        val = -1.0 if "left" in msg_lower else (1.0 if "right" in msg_lower else 0.0)
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
                val = pct / 100 if pct > 1 else pct
            except Exception:
                logger.debug("Failed to parse volume value from: %s", word)
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
            r = await client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                },
            )
            if r.status_code == 200:
                reply = r.json().get("message", {}).get("content", "")
                return {"message": reply}
    except Exception:
        logger.debug("Ollama chat failed")

    # Ollama failed — not a command, not an LLM request
    return {
        "message": (
            "Not recognized as a DJ command and no LLM available. "
            "Try: 'play deck 1', 'sync deck 2', 'crossfader left', "
            "'load track to deck 1' from Library."
        ),
    }


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
    except Exception as e:
        console.print(f"[yellow]OSC bridge stop warning: {e}[/yellow]")
    console.print(f"[green]{config.mcp_name} stopped[/green]")


# --- Fleet Audio Hub: Cross-MCP Deck Handoff ---
_audio_sources: dict[str, dict] = {}


@fastapi_app.get("/api/v1/fleet/sources")
async def fleet_sources():
    """List registered external audio sources (songgen, sfx, stems, plex, etc.)."""
    return {"sources": _audio_sources}


@fastapi_app.post("/api/v1/fleet/register")
async def fleet_register(body: dict):
    """Register an external audio source for deck handoff."""
    name = body.get("name", "unknown")
    _audio_sources[name] = {
        "name": name,
        "base_url": body.get("base_url", ""),
        "capabilities": body.get("capabilities", []),
        "registered_at": __import__("time").time(),
        "status": "online",
    }
    return {"success": True, "source": name}


@fastapi_app.get("/api/v1/cockpit/now_playing")
async def cockpit_now_playing():
    """Aggregated 'what's happening' across all decks and connected sources."""
    bridge = get_osc_bridge()
    decks = []
    for d in range(1, 5):
        decks.append(
            {
                "id": d,
                "playing": bool(bridge.get_state("play", d, 0.0)),
                "bpm": bridge.get_state("bpm", d, 0.0),
                "key": bridge.get_state("key", d, ""),
                "track_title": bridge.get_state("track_title", d, "No Track"),
                "track_artist": bridge.get_state("track_artist", d, ""),
                "volume": bridge.get_state("volume", d, 0.8),
                "sync_enabled": bool(bridge.get_state("sync_enabled", d, 0.0)),
            }
        )
    recording = None
    try:
        from .tools.recording import _active_recording

        if _active_recording:
            recording = {"name": _active_recording["name"], "events": _active_recording["events"]}
    except Exception:
        logger.debug("Failed to read active recording state")
    return {
        "decks": decks,
        "crossfader": bridge.get_global_state("crossfader", 0.0),
        "recording": recording,
        "external_sources": list(_audio_sources.keys()),
    }


# --- Voice Control Webhook ---
@fastapi_app.post("/api/voice/command")
async def voice_command(body: dict):
    """Webhook for speech-mcp voice commands."""
    text = body.get("text", "")
    if not text:
        return {"success": False, "error": "No text provided"}
    result = await _try_execute_command(text)
    if result:
        result["source"] = "voice"
        return result
    return {"success": False, "message": f"Voice command not recognized: {text}", "source": "voice"}


__all__ = ["app", "main", "mcp"]
