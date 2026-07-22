from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Div, Text
from rich.console import Console

from ..bridge.osc_bridge import get_bridge

console = Console(file=__import__("sys").stderr)


def register_prefab_tools(mcp: FastMCP):
    @mcp.tool(app=True)
    async def show_deck_status_card(deck: int = 1) -> ToolResult | dict[str, Any]:
        """
        Show live deck status as a rich Prefab card.

        Displays play state, BPM, key, volume, loop status, and sync state
        for the specified deck with data-testid attributes for CUA/Playwright testing.

        Args:
            deck: Deck number (1-4, default: 1)

        Returns:
            PrefabApp card with deck KPIs
        """
        try:
            bridge = get_bridge()
            is_playing = bridge.get_state("play", deck, 0.0)
            bpm = bridge.get_state("bpm", deck, 0.0)
            key = bridge.get_state("key", deck, "N/A")
            pregain = bridge.get_state("pregain", deck, 0.0)
            volume = bridge.get_state("volume", deck, 0.0)
            sync_enabled = bridge.get_state("sync_enabled", deck, 0.0)
            loop_enabled = bridge.get_state("loop_enabled", deck, 0.0)
            rate = bridge.get_state("rate", deck, 0.0)
            track_artist = bridge.get_state("track_artist", deck, "No Track")
            track_title = bridge.get_state("track_title", deck, "No Track")

            play_str = "Playing" if is_playing else "Paused"
            sync_str = "Synced" if sync_enabled else "Free"
            loop_str = "Loop On" if loop_enabled else "Loop Off"

            with Card(data_testid="deck-status-card", css_class="max-w-lg border border-neutral-700 bg-neutral-900 rounded-lg shadow-lg p-4") as view:
                with CardHeader():
                    CardTitle(f"Deck {deck} Status", data_testid="deck-status-title", css_class="text-lg font-bold text-white")
                with CardContent(css_class="mt-2 space-y-1"):
                    Div(data_testid="kpi-server")
                    Text(f"Track: {track_artist} - {track_title}", css_class="text-sm text-neutral-300")
                    Text(f"State: {play_str} | Sync: {sync_str} | {loop_str}", css_class="text-sm text-neutral-300")
                    Text(f"BPM: {bpm:.1f} | Key: {key} | Rate: {rate:+.2%}", css_class="text-sm text-neutral-300")
                    Text(f"Gain: {pregain:.2f} | Volume: {volume:.2f}", css_class="text-sm text-neutral-300")

            summary = f"Deck {deck}: {play_str} - {track_artist} - {track_title} ({bpm:.1f} BPM, {key})"
            return ToolResult(content=summary, structured_content=PrefabApp(view=view, title=f"Deck {deck} Status"))

        except Exception as e:
            console.print(f"[red]show_deck_status_card error: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(app=True)
    async def show_mixer_status_card() -> ToolResult | dict[str, Any]:
        """
        Show live mixer status as a rich Prefab card.

        Displays crossfader position, master gain, and per-deck levels
        with data-testid attributes for automated testing.

        Returns:
            PrefabApp card with mixer KPIs
        """
        try:
            bridge = get_bridge()
            crossfader = bridge.get_global_state("crossfader", 0.0)

            with Card(data_testid="mixer-status-card", css_class="max-w-lg border border-neutral-700 bg-neutral-900 rounded-lg shadow-lg p-4") as view:
                with CardHeader():
                    CardTitle("Mixer Status", data_testid="mixer-status-title", css_class="text-lg font-bold text-white")
                with CardContent(css_class="mt-2 space-y-1"):
                    Div(data_testid="kpi-tools")
                    Text(f"Crossfader: {crossfader:+.2f}", css_class="text-sm text-neutral-300")
                    for d in range(1, 5):
                        g = bridge.get_state("pregain", d, 0.0)
                        v = bridge.get_state("volume", d, 0.0)
                        p = bridge.get_state("play", d, 0.0)
                        p_str = "Playing" if p else "Stopped"
                        Text(f"Deck {d}: Gain {g:.2f} Vol {v:.2f} ({p_str})", css_class="text-sm text-neutral-300")

            return ToolResult(
                content=f"Mixer: crossfader at {crossfader:+.2f}",
                structured_content=PrefabApp(view=view, title="Mixer Status"),
            )

        except Exception as e:
            console.print(f"[red]show_mixer_status_card error: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(app=True)
    async def show_library_status_card() -> ToolResult | dict[str, Any]:
        """
        Show library connection and search status as a Prefab card.

        Reports whether the OSC bridge is connected to Mixxx and any active
        search or crate context.

        Returns:
            PrefabApp card with library KPIs
        """
        try:
            bridge = get_bridge()
            connected = bridge.is_connected()
            conn_str = "Connected" if connected else "Disconnected"

            with Card(data_testid="library-status-card", css_class="max-w-lg border border-neutral-700 bg-neutral-900 rounded-lg shadow-lg p-4") as view:
                with CardHeader():
                    CardTitle("Library Status", data_testid="library-status-title", css_class="text-lg font-bold text-white")
                with CardContent(css_class="mt-2 space-y-1"):
                    Text(f"Mixxx OSC: {conn_str}", data_testid="backend-dot", css_class="text-sm text-neutral-300")
                    Text("Ports: OSC In 11119 / OSC Out 11118", css_class="text-sm text-neutral-300")
                    Text("Use mixx_library to search, browse, and load tracks.", css_class="text-sm text-neutral-400 italic")

            return ToolResult(
                content=f"Library Status: {conn_str}",
                structured_content=PrefabApp(view=view, title="Library Status"),
            )

        except Exception as e:
            console.print(f"[red]show_library_status_card error: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}
