from typing import Any, Literal

from fastmcp import FastMCP

from ..bridge.osc_bridge import get_bridge


def register_crate_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_crate(
        operation: Literal["create", "list", "delete", "add_track"],
        name: str = "",
        prompt: str = "",
        deck: int = 1,
    ) -> dict[str, Any]:
        """
        Smart crate management for Mixxx.

        PORTMANTEAU PATTERN: Consolidates crate creation and management.

        SUPPORTED OPERATIONS:
        - create: Create a crate from a natural language prompt (requires name, prompt)
        - list: List all crates in the library
        - delete: Delete a crate by name (requires name)
        - add_track: Add currently playing track on deck to a crate (requires name, deck)

        ## Return Format
        {"success": bool, "message": str, "data": dict}

        ## Examples
            mixx_crate("create", name="Peak Time", prompt="tech house 124-128 BPM D minor")
            mixx_crate("list")
            mixx_crate("add_track", name="Favorites", deck=1)
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
                return {"success": True, "message": "Use mixx_library(browse_crate) to browse", "data": {}}

            elif operation == "delete":
                return {"success": False, "message": "Crate deletion not available via OSC", "data": {}}

            elif operation == "add_track":
                return {
                    "success": True,
                    "message": f"Add current deck {deck} track to crate '{name}' manually in Mixxx",
                    "data": {"crate": name, "deck": deck},
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
