import json
from datetime import datetime
from typing import Any, Literal

from fastmcp import FastMCP

from ..bridge.osc_bridge import get_bridge


def register_crate_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_crate(
        operation: Literal["create", "list", "delete", "add_track", "create_agentic"],
        name: str = "",
        prompt: str = "",
        deck: int = 1,
        rule: str = "",
        max_tracks: int = 50,
        update: str = "manual",
    ) -> dict[str, Any]:
        """
        Smart crate management for Mixxx.

        PORTMANTEAU PATTERN: Consolidates crate creation and management.

        SUPPORTED OPERATIONS:
        - create: Create a crate from a natural language prompt (requires name, prompt)
        - list: List all crates in the library
        - delete: Delete a crate by name (requires name)
        - add_track: Add currently playing track on deck to a crate (requires name, deck)
        - create_agentic: Create a self-curating crate with an LLM rule (requires name, rule)
          Rules: "126-132 BPM, Dm or Em, 4+ stars, genre:tech house"
          The crate auto-updates based on the rule when the server starts.

        ## Return Format
        {"success": bool, "message": str, "data": dict}

        ## Examples
            mixx_crate("create", name="Peak Time", prompt="tech house 124-128 BPM D minor")
            mixx_crate("list")
            mixx_crate("add_track", name="Favorites", deck=1)
            mixx_crate("create_agentic", name="Morning Warmup", rule="126-132 BPM, Dm or Em, 4+ stars, genre:tech house")
        """
        try:
            bridge = get_bridge()

            if operation == "create":
                if not name or not prompt:
                    return {"success": False, "message": "name and prompt required", "data": {}}
                search_query = await _prompt_to_search(prompt)
                bridge.send("/library/search", search_query)
                return {
                    "success": True,
                    "message": f"Searching: '{search_query}'. In Mixxx, save search as crate '{name}'",
                    "data": {"crate": name, "search_query": search_query, "prompt": prompt}
                }

            elif operation == "list":
                data: dict[str, Any] = {"hint": "Use mixx_library(browse_crate) to browse"}
                agentic = _list_agentic_crates()
                if agentic:
                    data["agentic_crates"] = [{"name": k, **v} for k, v in agentic.items()]
                return {"success": True, "message": "Use mixx_library(browse_crate) to browse", "data": data}

            elif operation == "delete":
                return {"success": False, "message": "Crate deletion not available via OSC", "data": {}}

            elif operation == "add_track":
                return {
                    "success": True,
                    "message": f"Add current deck {deck} track to crate '{name}' manually in Mixxx",
                    "data": {"crate": name, "deck": deck},
                }

            elif operation == "create_agentic":
                if not name:
                    return {"success": False, "message": "name required", "data": {}}
                if not rule:
                    return {"success": False, "message": "rule required (e.g. '126-132 BPM, Dm or Em, 4+ stars')", "data": {}}

                rules_file = _get_rules_path()
                rules = {}
                if rules_file.exists():
                    rules = json.loads(rules_file.read_text())

                rules[name] = {
                    "rule": rule,
                    "max_tracks": max_tracks,
                    "update": update,
                    "created": str(datetime.now()),
                }
                rules_file.write_text(json.dumps(rules, indent=2))

                search_query = await _prompt_to_search(rule)

                return {
                    "success": True,
                    "message": f"Created agentic crate '{name}'. Rule: '{rule}'. Update: {update}",
                    "data": {
                        "crate": name,
                        "rule": rule,
                        "search_query": search_query,
                        "update_frequency": update,
                    }
                }

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}


async def _prompt_to_search(prompt: str) -> str:
    """Translate a natural language prompt to Mixxx search syntax."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post("http://localhost:11434/api/generate", json={
                "model": "llama3.2:3b",
                "prompt": (
                    "Convert this DJ crate description into Mixxx library search syntax. "
                    "Rules: use bpm:, key:, genre: prefixes, AND/OR operators, - for negation. "
                    "Only output the search query, nothing else.\n\n"
                    f"Description: {prompt}\n\nSearch:"
                ),
                "stream": False,
            })
            if r.status_code == 200:
                result = r.json().get("response", "").strip().strip('"').strip("'")
                if result:
                    return result
    except httpx.TransportError:
        pass

    parts = prompt.lower().split()
    search_parts = []
    for i, word in enumerate(parts):
        if word == "bpm" and i + 1 < len(parts):
            search_parts.append(f"bpm:{parts[i+1]}")
        elif word.isdigit() and i > 0 and parts[i-1] == "bpm":
            continue
        elif word in (
            "tech", "house", "deep", "progressive", "minimal",
            "techno", "trance", "dubstep", "drum", "bass",
            "garage", "disco", "funk", "soul", "rnb", "hip",
            "hop", "edm", "pop", "rock", "metal", "jazz", "blues",
        ):
            search_parts.append(f'genre:"{word}"')
        elif not any(c.isdigit() for c in word):
            search_parts.append(word)

    return " ".join(search_parts) if search_parts else prompt


def _get_rules_path():
    import os
    from pathlib import Path
    data_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "mixx-dj-mcp"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "agentic_crates.json"


def _list_agentic_crates() -> dict:
    rules_file = _get_rules_path()
    if rules_file.exists():
        return json.loads(rules_file.read_text())
    return {}


def _delete_agentic_crate(name: str) -> bool:
    rules = _list_agentic_crates()
    if name in rules:
        del rules[name]
        _get_rules_path().write_text(json.dumps(rules, indent=2))
        return True
    return False
