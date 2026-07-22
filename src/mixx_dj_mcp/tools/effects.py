from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..bridge.osc_bridge import get_bridge

console = Console(file=__import__("sys").stderr)


async def mixx_effects(
        operation: Literal[
            "list_effects", "chain_load", "chain_clear",
            "parameter_set", "meta_set", "quick_effect_set",
            "effect_enable",
        ],
        rack: int = 1,
        unit: int = 1,
        effect: str | None = None,
        parameter: int = 1,
        value: float | None = None,
        deck: int | None = None,
        enable: bool = True,
    ) -> dict[str, Any]:
        """
        Effect chain control for Mixxx.

        PORTMANTEAU PATTERN: Consolidates all effect rack and chain operations.

        SUPPORTED OPERATIONS:
        - list_effects: List available effects for a rack/unit
        - chain_load: Load an effect chain by name (requires effect)
        - chain_clear: Clear the effect chain on a rack/unit
        - parameter_set: Set a specific effect parameter (requires parameter, value)
        - meta_set: Set meta/param knob value (requires value, 0.0-1.0)
        - quick_effect_set: Set quick effect for deck (requires deck, effect)
        - effect_enable: Enable/disable an effect unit (requires enable)

        Returns:
            Dict with operation result

        Examples:
            mixx_effects("chain_load", rack=1, unit=1, effect="Flanger")
            mixx_effects("parameter_set", rack=1, unit=1, parameter=2, value=0.75)
            mixx_effects("effect_enable", rack=1, unit=1, enable=True)
        """
        try:
            bridge = get_bridge()

            if operation == "list_effects":
                return {
                    "success": True,
                    "message": "Available effects (depends on Mixxx build)",
                    "data": {"rack": rack, "unit": unit, "note": "Use mixx_effects chain_load to activate"},
                }

            elif operation == "chain_load":
                if not effect:
                    return {"success": False, "message": "effect name required for chain_load", "data": {}}
                bridge.send(f"/EffectRack{rack}_EffectUnit{unit}/chain_load", effect)
                return {
                    "success": True,
                    "message": f"Loading effect chain: {effect}",
                    "data": {"rack": rack, "unit": unit, "effect": effect},
                }

            elif operation == "chain_clear":
                bridge.send(f"/EffectRack{rack}_EffectUnit{unit}/chain_clear", 1.0)
                return {"success": True, "message": f"Effect chain cleared (rack {rack}, unit {unit})", "data": {"rack": rack, "unit": unit}}

            elif operation == "parameter_set":
                if value is None:
                    return {"success": False, "message": "value required (0.0-1.0)", "data": {}}
                val = max(0.0, min(1.0, value))
                bridge.send(f"/EffectRack{rack}_EffectUnit{unit}/parameter{parameter}", val)
                return {
                    "success": True,
                    "message": f"Parameter {parameter} set to {val:.2f}",
                    "data": {"rack": rack, "unit": unit, "parameter": parameter, "value": val},
                }

            elif operation == "meta_set":
                if value is None:
                    return {"success": False, "message": "value required (0.0-1.0)", "data": {}}
                val = max(0.0, min(1.0, value))
                bridge.send(f"/EffectRack{rack}_EffectUnit{unit}/meta", val)
                return {"success": True, "message": f"Meta knob set to {val:.2f}", "data": {"rack": rack, "unit": unit, "value": val}}

            elif operation == "quick_effect_set":
                if not deck or not effect:
                    return {"success": False, "message": "deck and effect required", "data": {}}
                bridge.send(f"/deck/{deck}/QuickEffect", effect)
                return {"success": True, "message": f"Quick effect set on deck {deck}: {effect}", "data": {"deck": deck, "effect": effect}}

            elif operation == "effect_enable":
                bridge.send(f"/EffectRack{rack}_EffectUnit{unit}/enabled", 1.0 if enable else 0.0)
                return {"success": True, "message": f"Effect unit {'enabled' if enable else 'disabled'}", "data": {"rack": rack, "unit": unit, "enable": enable}}

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            console.print(f"[red]Error in mixx_effects: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}


def register_effects_tools(mcp: FastMCP):
    mcp.tool()(mixx_effects)
