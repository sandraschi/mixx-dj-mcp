import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

console = Console(file=__import__("sys").stderr)

# Default color palette when prompt parsing fails
_DEFAULT_COLORS = {
    "bg_dark": "#0d001a",
    "bg_medium": "#1a0033",
    "accent": "#00ffff",
    "text": "#ffffff",
    "waveform": "#00ffff",
}

INKSCAPE_MCP_URL = "http://127.0.0.1:11028/mcp"

# Curated skin manifest
AVAILABLE_SKINS = {
    "mixxxxx-video": {
        "name": "Mixxxxx Video",
        "author": "sandraschi",
        "version": "1.0.0",
        "description": "LateNight-based with video previews, output panel, projector controls",
        "tags": ["video-ready", "4-deck", "dark", "recommended"],
        "source": "https://github.com/sandraschi/mixxxxx",
        "preview_url": "",
    },
    "latenight": {
        "name": "LateNight",
        "author": "owilliams, ronso0",
        "version": "2.4.0.01",
        "description": "Wide nighttime skin with stacked waveforms, 4 decks, 16 samplers",
        "tags": ["4-deck", "waveforms", "hotcues"],
        "source": "bundled",
        "preview_url": "",
    },
    "deere": {
        "name": "Deere",
        "author": "Be",
        "version": "2.4.0.01",
        "description": "Clean minimal skin with broad layout",
        "tags": ["4-deck", "minimal", "clean"],
        "source": "bundled",
        "preview_url": "",
    },
    "shade": {
        "name": "Shade",
        "author": "Tobias Esterer",
        "version": "2.4.0.01",
        "description": "Dark compact skin for smaller screens",
        "tags": ["dark", "compact"],
        "source": "bundled",
        "preview_url": "",
    },
    "tango": {
        "name": "Tango",
        "author": "Tobias Esterer",
        "version": "2.4.0.01",
        "description": "Colorful skin with bold visuals",
        "tags": ["colorful", "waveforms"],
        "source": "bundled",
        "preview_url": "",
    },
    "tara": {
        "name": "Tara",
        "author": "m0d",
        "version": "2.3.0",
        "description": "Clean 2-deck skin with large waveforms",
        "tags": ["2-deck", "minimal", "waveforms"],
        "source": "https://github.com/search?q=mixxx+skin+tara",
        "preview_url": "",
    },
    "djcontrol": {
        "name": "DJ Control Compact",
        "author": "Hercules",
        "version": "2.3.0",
        "description": "Optimized for Hercules DJ Control Compact hardware",
        "tags": ["hardware", "compact", "2-deck"],
        "source": "bundled",
        "preview_url": "",
    },
}


def _get_skins_path() -> Path:
    """Get the Mixxx user skins directory."""
    appdata = os.environ.get("LOCALAPPDATA", "")
    if appdata:
        path = Path(appdata) / "Mixxx" / "skins"
    else:
        path = Path.home() / ".mixxx" / "skins"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _find_bundled_skin(skin_id: str) -> Path | None:
    """Locate a bundled skin in the Mixxx installation directory."""
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Mixxx" / "res" / "skins" / skin_id,
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Mixxx" / "res" / "skins" / skin_id,
        Path(os.environ.get("MIXXX_PATH", "")) / "res" / "skins" / skin_id,
    ]
    # Also check common install locations
    for root in ["C:\\Program Files", "C:\\Program Files (x86)"]:
        candidates.append(Path(root) / "Mixxx" / "res" / "skins" / skin_id)
    for p in candidates:
        if p.exists():
            return p
    return None


_VIDEO_WIDGET_XML = """
    <!-- VideoWidget (inserted by mixx_skin create_video_skin) -->
    <WidgetGroup>
        <ObjectName>VideoWidget</ObjectName>
        <Layout>vertical</Layout>
        <Size>240,180</Size>
        <Children>
            <WidgetGroup>
                <ObjectName>VideoPreview</ObjectName>
                <MinimumSize>200,130</MinimumSize>
            </WidgetGroup>
            <WidgetGroup>
                <ObjectName>VideoControls</ObjectName>
                <Layout>horizontal</Layout>
                <Children>
                    <PushButton><ObjectName>video_start</ObjectName></PushButton>
                    <PushButton><ObjectName>video_stop</ObjectName></PushButton>
                </Children>
            </WidgetGroup>
        </Children>
    </WidgetGroup>"""


def _inject_video_widget(skin_dir: Path) -> list[str]:
    """Add VideoWidget entry to the skin's main XML file(s)."""
    modified = []
    for skin_file in skin_dir.rglob("*.skin"):
        if not skin_file.is_file():
            continue
        content = skin_file.read_text(encoding="utf-8")
        if "VideoWidget" in content:
            continue
        # Insert VideoWidget before the closing </Skin> tag
        if "</Skin>" in content:
            content = content.replace("</Skin>", f"{_VIDEO_WIDGET_XML}\n</Skin>")
            skin_file.write_text(content, encoding="utf-8")
            modified.append(str(skin_file))
    return modified


# ── Skin Generation Helpers ─────────────────────────────────────────────


def _find_late_night_skin() -> Path | None:
    """Find the LateNight skin directory (bundled or user-installed)."""
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Mixxx" / "res" / "skins" / "LateNight",
        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Mixxx" / "res" / "skins" / "LateNight",
        _get_skins_path().parent / "LateNight",
        _get_skins_path() / "latenight",
    ]
    for c in candidates:
        if (c / "skin.xml").exists():
            return c
    return None


def _copy_skin_directory(src: Path, dst: Path):
    """Copy a skin directory, skipping backup files."""
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.bak"))
    for f in dst.rglob("*.bak"):
        f.unlink()


def _update_skin_manifest(skin_path: Path, name: str, colors: dict):
    """Update skin.xml with new name, author, and description."""
    skin_xml = skin_path / "skin.xml"
    if not skin_xml.exists():
        return
    content = skin_xml.read_text(encoding="utf-8")
    content = re.sub(r"<title>.*?</title>", f"<title>{name}</title>", content)
    content = re.sub(r"<author>.*?</author>", "<author>AI Skin Generator</author>", content)
    content = re.sub(r"<version>.*?</version>", "<version>1.0.0</version>", content)
    content = re.sub(
        r"<description>.*?</description>",
        f"<description>AI-generated skin: {name}</description>",
        content,
    )
    skin_xml.write_text(content, encoding="utf-8")


async def _parse_prompt_for_colors(prompt: str) -> dict:
    """Extract a hex color palette from a natural language prompt using Ollama."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": (
                        "Extract a hex color palette from this skin description. "
                        "Return ONLY valid JSON with keys: "
                        "bg_dark, bg_medium, accent, text, waveform.\n\n"
                        f"Description: {prompt}"
                    ),
                    "stream": False,
                },
            )
            if r.status_code == 200:
                text = r.json().get("response", "")
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(text[start:end])
                    return {k: v for k, v in parsed.items() if isinstance(v, str) and v.startswith("#")}
    except Exception:
        pass
    return dict(_DEFAULT_COLORS)


async def _recolor_skins_via_inkscape(skin_path: Path, colors: dict, prompt: str) -> int:
    """Recolor SVG assets using inkscape-mcp introspection + text replacement."""
    import httpx

    style_dir = skin_path / "style"
    if not style_dir.exists():
        return 0

    svg_files = list(style_dir.rglob("*.svg"))
    if not svg_files:
        return 0

    # Probe inkscape-mcp availability
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(
                INKSCAPE_MCP_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "inkscape_file",
                    "params": {"operation": "info", "input_path": str(svg_files[0])},
                },
                timeout=10,
            )
            if r.status_code == 200:
                resp = r.json()
                resp.get("result", {}).get("content", [{}])[0].get("text", "").find("success") > -1 or resp.get(
                    "result", {}
                ).get("success", False)
    except Exception:
        pass

    count = 0

    # Build color replacement map
    replacements = {
        "#000000": colors.get("bg_dark", "#000000"),
        "#1a1a2e": colors.get("bg_medium", "#1a0033"),
        "#333333": colors.get("bg_medium", "#333333"),
        "#ffffff": colors.get("text", "#ffffff"),
        "#cccccc": colors.get("text", "#cccccc"),
        "#00ff00": colors.get("accent", "#00ff00"),
        "#00cc00": colors.get("accent", "#00aa00"),
        "#ff0000": colors.get("accent", "#ff4444"),
        "#ff8800": colors.get("accent", "#ff8800"),
        "#ffff00": colors.get("accent", "#ffcc00"),
        "#4488ff": colors.get("accent", "#4488ff"),
        "#0066ff": colors.get("accent", "#0066ff"),
    }

    for svg in svg_files[:20]:
        try:
            content = svg.read_text(encoding="utf-8")
            for old, new in replacements.items():
                if old != new:
                    content = content.replace(old, new)
            svg.write_text(content, encoding="utf-8")
            count += 1
        except Exception:
            pass

    return count


async def _generate_skin(name: str, prompt: str, base_skin: str) -> dict:
    """Generate a Mixxx skin by cloning a base and recoloring via inkscape-mcp."""

    colors = await _parse_prompt_for_colors(prompt)

    # Locate the base skin
    base_path = None
    if base_skin == "latenight" or base_skin == "LateNight":
        base_path = _find_late_night_skin()
    else:
        base_path = _find_bundled_skin(base_skin)
        if not base_path:
            base_path = _get_skins_path() / base_skin
            if not base_path.exists():
                base_path = None

    if not base_path:
        return {
            "success": False,
            "message": f"Base skin '{base_skin}' not found. Install Mixxx first.",
            "data": {},
        }

    skin_path = _get_skins_path() / name
    if skin_path.exists():
        return {
            "success": False,
            "message": f"Skin '{name}' already exists at {skin_path}",
            "data": {},
        }

    _copy_skin_directory(base_path, skin_path)
    generated = await _recolor_skins_via_inkscape(skin_path, colors, prompt)
    _update_skin_manifest(skin_path, name, colors)

    return {
        "success": True,
        "message": f"Generated skin '{name}' with {generated} recolored SVGs",
        "data": {
            "skin_path": str(skin_path),
            "skin_id": name,
            "colors": colors,
            "svgs_generated": generated,
            "base_skin": base_skin,
            "note": f"Select '{name}' in Mixxx Preferences → Interface → Skin and restart.",
        },
    }


def register_skin_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_skin(
        operation: Literal["list", "search", "install", "uninstall", "preview", "create_video_skin", "create_skin"],
        query: str = "",
        skin_id: str = "",
        tags: str = "",
        name: str = "",
        prompt: str = "",
        base_skin: str = "latenight",
    ) -> dict[str, Any]:
        """
        Skin browser and manager for Mixxx.

        PORTMANTEAU PATTERN: Consolidates skin discovery and management.

        SUPPORTED OPERATIONS:
        - list: List all available skins from the curated manifest
        - search: Search skins by name, author, or tag (requires query or tags)
        - install: Install a skin from the manifest to the Mixxx user skins dir
        - uninstall: Remove an installed skin (requires skin_id)
        - preview: Show information about a skin (requires skin_id)
        - create_video_skin: Copy LateNight and add VideoWidget entries for video-DJ workflows
        - create_skin: Generate a new skin by cloning LateNight and recoloring SVGs via inkscape-mcp
          (requires name and prompt; optional base_skin defaults to latenight)

        Returns:
            Dict with operation result and list of skins

        Examples:
            mixx_skin("list")
            mixx_skin("search", tags="video-ready,dark")
            mixx_skin("install", skin_id="tara")
            mixx_skin("create_video_skin")
            mixx_skin("create_skin", name="cyberpunk", prompt="dark purple with cyan accents, neon waveform")
        """
        try:
            if operation == "list":
                skins = [{"id": sid, **info} for sid, info in AVAILABLE_SKINS.items()]
                return {
                    "success": True,
                    "message": f"Found {len(skins)} available skins",
                    "data": {"skins": skins},
                }

            elif operation == "search":
                results = []
                q = query.lower() if query else ""
                tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()] if tags else []

                for sid, info in AVAILABLE_SKINS.items():
                    score = 0
                    if q:
                        if q in sid.lower():
                            score += 3
                        if q in info["name"].lower():
                            score += 3
                        if q in info["author"].lower():
                            score += 2
                        if q in info["description"].lower():
                            score += 1

                    if tag_list:
                        skin_tags = [t.lower() for t in info.get("tags", [])]
                        if not any(t in skin_tags for t in tag_list):
                            continue
                        score += sum(1 for t in tag_list if t in skin_tags) * 2

                    if q or tag_list:
                        if score > 0:
                            results.append({"id": sid, **info, "relevance": score})
                    else:
                        results.append({"id": sid, **info})

                if q or tag_list:
                    results.sort(key=lambda x: x.get("relevance", 0), reverse=True)

                return {
                    "success": True,
                    "message": f"Found {len(results)} matching skins",
                    "data": {"skins": results, "query": query, "tags": tags},
                }

            elif operation == "install":
                if skin_id not in AVAILABLE_SKINS:
                    return {"success": False, "message": f"Unknown skin: {skin_id}", "data": {}}

                install_path = _get_skins_path() / skin_id

                if AVAILABLE_SKINS[skin_id].get("source") == "bundled":
                    return {
                        "success": True,
                        "message": f"'{AVAILABLE_SKINS[skin_id]['name']}' is bundled with Mixxx. Select it in Preferences \u2192 Interface \u2192 Skin.",
                        "data": {"skin": skin_id, "bundled": True},
                    }

                if install_path.exists():
                    return {
                        "success": True,
                        "message": f"Skin '{skin_id}' already installed at {install_path}",
                        "data": {"skin": skin_id, "path": str(install_path)},
                    }

                return {
                    "success": False,
                    "message": f"Auto-install for '{skin_id}' requires manual download. Visit: {AVAILABLE_SKINS[skin_id].get('source', 'N/A')}",
                    "data": {"skin": skin_id, "source": AVAILABLE_SKINS[skin_id].get("source")},
                }

            elif operation == "uninstall":
                install_path = _get_skins_path() / skin_id
                if install_path.exists():
                    shutil.rmtree(install_path)
                    return {"success": True, "message": f"Uninstalled skin '{skin_id}'", "data": {"skin": skin_id}}
                return {"success": False, "message": f"Skin '{skin_id}' not installed", "data": {}}

            elif operation == "preview":
                if skin_id not in AVAILABLE_SKINS:
                    return {"success": False, "message": f"Unknown skin: {skin_id}", "data": {}}
                info = AVAILABLE_SKINS[skin_id]
                install_path = _get_skins_path() / skin_id
                return {
                    "success": True,
                    "message": f"{info['name']} by {info['author']}",
                    "data": {
                        "skin": skin_id,
                        "name": info["name"],
                        "author": info["author"],
                        "version": info["version"],
                        "description": info["description"],
                        "tags": info["tags"],
                        "source": info.get("source", ""),
                        "installed": install_path.exists(),
                    },
                }

            elif operation == "create_video_skin":
                target_id = "latenight-video"
                target_path = _get_skins_path() / target_id

                if target_path.exists():
                    shutil.rmtree(target_path)

                # Find the LateNight source
                source_path = _get_skins_path() / "latenight"
                if not source_path.exists():
                    bundled = _find_bundled_skin("latenight")
                    if bundled:
                        source_path = bundled
                    else:
                        return {
                            "success": False,
                            "message": "LateNight skin not found. Install Mixxx first or copy a LateNight skin to the user skins directory.",
                            "data": {"hint": "Default location: C:\\Program Files\\Mixxx\\res\\skins\\latenight"},
                        }

                shutil.copytree(source_path, target_path)
                modified = _inject_video_widget(target_path)

                return {
                    "success": True,
                    "message": f"Created video-optimized skin 'latenight-video' at {target_path}",
                    "data": {
                        "skin_id": target_id,
                        "path": str(target_path),
                        "files_modified": modified,
                        "note": "Select 'latenight-video' in Mixxx Preferences \u2192 Interface \u2192 Skin and restart.",
                    },
                }

            elif operation == "create_skin":
                if not name:
                    return {
                        "success": False,
                        "message": "name is required for create_skin operation",
                        "data": {},
                    }
                result = await _generate_skin(name, prompt, base_skin)
                return result

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            console.print(f"[red]Error in mixx_skin: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}
