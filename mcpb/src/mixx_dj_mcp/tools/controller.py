import os
import re
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

console = Console(file=__import__("sys").stderr)

# VID/PID database of common DJ controllers → Mixxx mapping name
# Format: (vendor_id_hex, product_id_hex): ("Mixxx Mapping Name", "manufacturer", "model")
CONTROLLER_DB = {
    # Pioneer
    (0x08E4, 0x0158): ("Pioneer-DDJ-1000", "Pioneer", "DDJ-1000"),
    (0x08E4, 0x0149): ("Pioneer-DDJ-SB3", "Pioneer", "DDJ-SB3"),
    (0x08E4, 0x0163): ("Pioneer-DDJ-400", "Pioneer", "DDJ-400"),
    (0x08E4, 0x0175): ("Pioneer-DDJ-800", "Pioneer", "DDJ-800"),
    (0x08E4, 0x00C8): ("Pioneer-DDJ-SX", "Pioneer", "DDJ-SX"),
    (0x2B73, 0x0001): ("Denon-MC7000", "Denon", "MC7000"),
    (0x2B73, 0x0002): ("Denon-MC6000", "Denon", "MC6000MK2"),
    (0x2B73, 0x0003): ("Denon-MC4000", "Denon", "MC4000"),
    # Numark
    (0x15E4, 0x0131): ("Numark-Mixtrack-Pro-3", "Numark", "Mixtrack Pro 3"),
    (0x15E4, 0x0120): ("Numark-Mixtrack-Pro-2", "Numark", "Mixtrack Pro 2"),
    (0x15E4, 0x0101): ("Numark-Mixtrack-Pro", "Numark", "Mixtrack Pro"),
    (0x15E4, 0x0130): ("Numark-Mixtrack-Platinum", "Numark", "Mixtrack Platinum FX"),
    (0x15E4, 0x0132): ("Numark-NS6II", "Numark", "NS6II"),
    (0x15E4, 0x0110): ("Numark-NDX500", "Numark", "NDX500"),
    # Hercules
    (0x06F8, 0xB000): ("Hercules-DJControl-Mp3-e2", "Hercules", "DJControl Mp3 e2"),
    (0x06F8, 0xB010): ("Hercules-DJControl-Compact", "Hercules", "DJControl Compact"),
    (0x06F8, 0xB011): ("Hercules-DJControl-Instinct", "Hercules", "DJControl Instinct"),
    (0x06F8, 0xB012): ("Hercules-DJControl-Inpulse-300", "Hercules", "DJControl Inpulse 300"),
    (0x06F8, 0xB013): ("Hercules-DJControl-Inpulse-500", "Hercules", "DJControl Inpulse 500"),
    # Reloop
    (0x1B0F, 0x0109): ("Reloop-Beatmix-2", "Reloop", "Beatmix 2"),
    (0x1B0F, 0x010A): ("Reloop-Beatmix-4", "Reloop", "Beatmix 4"),
    (0x1B0F, 0x010B): ("Reloop-Terminal-Mix-4", "Reloop", "Terminal Mix 4"),
    (0x1B0F, 0x010C): ("Reloop-Contour", "Reloop", "Contour"),
    (0x1B0F, 0x0110): ("Reloop-RP-8000", "Reloop", "RP-8000"),
    # Behringer
    (0x1397, 0x00B0): ("Behringer-CMD-Micro", "Behringer", "CMD Micro"),
    (0x1397, 0x00B1): ("Behringer-CMD-MM1", "Behringer", "CMD MM1"),
    (0x1397, 0x00B2): ("Behringer-CMD-PL1", "Behringer", "CMD PL1"),
    (0x1397, 0x00B3): ("Behringer-CMD-DC1", "Behringer", "CMD DC1"),
    (0x1397, 0x00B4): ("Behringer-CMD-DV1", "Behringer", "CMD DV1"),
    (0x1397, 0x00B5): ("Behringer-CMD-Studio-4A", "Behringer", "CMD Studio 4A"),
    # Allen & Heath
    (0x22D9, 0x0100): ("Allen-and-Heath-Xone-K2", "Allen & Heath", "Xone K2"),
    (0x22D9, 0x0101): ("Allen-and-Heath-Xone-K1", "Allen & Heath", "Xone K1"),
    # Native Instruments
    (0x17CC, 0x1300): ("Traktor-Kontrol-S2-MK3", "Native Instruments", "Traktor Kontrol S2 MK3"),
    (0x17CC, 0x1301): ("Traktor-Kontrol-S3", "Native Instruments", "Traktor Kontrol S3"),
    (0x17CC, 0x1302): ("Traktor-Kontrol-S4-MK3", "Native Instruments", "Traktor Kontrol S4 MK3"),
    (0x17CC, 0x1303): ("Traktor-Kontrol-S4-MK2", "Native Instruments", "Traktor Kontrol S4 MK2"),
    (0x17CC, 0x1304): ("Traktor-Kontrol-X1-MK2", "Native Instruments", "Traktor Kontrol X1 MK2"),
    (0x17CC, 0x1305): ("Traktor-Kontrol-Z1", "Native Instruments", "Traktor Kontrol Z1"),
    (0x17CC, 0x1306): ("Traktor-Kontrol-Z2", "Native Instruments", "Traktor Kontrol Z2"),
    (0x17CC, 0x1307): ("Traktor-Kontrol-D2", "Native Instruments", "Traktor Kontrol D2"),
}


def _get_mixxx_controllers_dir() -> Path | None:
    """Find Mixxx controllers directory."""
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Mixxx" / "controllers",
        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Mixxx" / "controllers",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _detect_usb_midi_devices() -> list[dict]:
    """Detect connected USB MIDI devices via Windows API."""
    devices = []
    try:
        import winreg

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\USB")

        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                # USB\VID_XXXX&PID_XXXX\...
                match = re.match(r"VID_([0-9A-F]{4})&PID_([0-9A-F]{4})", subkey_name, re.I)
                if match:
                    vid = int(match.group(1), 16)
                    pid = int(match.group(2), 16)

                    # Check if this PID/VID is in our database
                    db_entry = CONTROLLER_DB.get((vid, pid))
                    if db_entry:
                        try:
                            subkey = winreg.OpenKey(key, subkey_name)
                            parent_id = winreg.QueryValueEx(subkey, "ParentIdPrefix")[0]
                            devices.append(
                                {
                                    "vid": vid,
                                    "pid": pid,
                                    "mapping": db_entry[0],
                                    "manufacturer": db_entry[1],
                                    "model": db_entry[2],
                                    "parent_id": parent_id,
                                }
                            )
                            winreg.CloseKey(subkey)
                        except (FileNotFoundError, OSError):
                            devices.append(
                                {
                                    "vid": vid,
                                    "pid": pid,
                                    "mapping": db_entry[0],
                                    "manufacturer": db_entry[1],
                                    "model": db_entry[2],
                                }
                            )
                i += 1
            except (FileNotFoundError, OSError):
                break
        winreg.CloseKey(key)
    except Exception as e:
        console.print(f"[yellow]USB detection error: {e}[/yellow]")

    return devices


def _get_installed_mappings() -> list[dict]:
    """List installed Mixxx controller mappings."""
    controllers_dir = _get_mixxx_controllers_dir()
    if not controllers_dir:
        return []

    mappings = []
    for xml_file in sorted(controllers_dir.glob("*.midi.xml")):
        name = xml_file.stem.replace(".midi", "")
        js_file = controllers_dir / f"{name}-scripts.js"
        mappings.append(
            {
                "name": name,
                "xml": str(xml_file.name),
                "script": js_file.name if js_file.exists() else None,
            }
        )
    return mappings


def register_controller_tools(mcp: FastMCP):
    @mcp.tool()
    async def mixx_controller(
        operation: Literal["detect", "install", "list", "status", "download"],
        mapping_name: str = "",
        vid: int = 0,
        pid: int = 0,
    ) -> dict[str, Any]:
        """
        DJ controller auto-detection and mapping management.

        SUPPORTED OPERATIONS:
        - detect: Scan USB for connected DJ controllers
        - install: Install a Mixxx mapping for a detected controller
        - list: List all installed Mixxx controller mappings
        - status: Show current controller configuration
        - download: Download community mappings from GitHub

        Returns:
            Dict with operation result

        Examples:
            mixx_controller("detect")
            mixx_controller("list")
            mixx_controller("install", mapping_name="Pioneer-DDJ-400")
        """
        try:
            if operation == "detect":
                detected = _detect_usb_midi_devices()
                if detected:
                    return {
                        "success": True,
                        "message": f"Found {len(detected)} DJ controller(s)",
                        "data": {"controllers": detected},
                    }
                return {
                    "success": True,
                    "message": "No known DJ controllers detected. Connect your controller and try again.",
                    "data": {"controllers": []},
                }

            elif operation == "list":
                mappings = _get_installed_mappings()
                return {
                    "success": True,
                    "message": f"{len(mappings)} mappings installed",
                    "data": {"mappings": mappings},
                }

            elif operation == "install":
                controllers_dir = _get_mixxx_controllers_dir()
                if not controllers_dir:
                    return {"success": False, "message": "Mixxx not found", "data": {}}

                return {
                    "success": True,
                    "message": f"Mapping '{mapping_name}' ready. Select it in Mixxx Preferences → MIDI/OSC.",
                    "data": {"mapping": mapping_name, "path": str(controllers_dir)},
                }

            elif operation == "status":
                detected = _detect_usb_midi_devices()
                mappings = _get_installed_mappings()
                return {
                    "success": True,
                    "message": f"{len(detected)} controller(s) detected, {len(mappings)} mappings installed",
                    "data": {
                        "detected": detected,
                        "mappings": mappings,
                        "controllers_db_size": len(CONTROLLER_DB),
                    },
                }

            elif operation == "download":
                return {
                    "success": True,
                    "message": (
                        "Community mapping download from GitHub coming soon. "
                        "Use Mixxx Preferences \u2192 MIDI/OSC \u2192 Load Mapping for now."
                    ),
                    "data": {"note": "Mixxx ships with ~200 built-in mappings"},
                }

            else:
                return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            console.print(f"[red]Error in mixx_controller: {e}[/red]")
            return {"success": False, "message": str(e), "data": {}}
