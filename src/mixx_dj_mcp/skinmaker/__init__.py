"""Mixxxxx skin authoring — QSS schemes, SVG recolor via inkscape-mcp."""

from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path

__all__ = ["scheme_path"]


def scheme_path(name: str) -> Path:
    """Return path to a bundled *.tokens.json scheme (e.g. daylight-v2)."""
    ref = files("mixx_dj_mcp.skinmaker").joinpath(f"schemes/{name}.tokens.json")
    with as_file(ref) as resolved:
        path = Path(resolved)
        if not path.is_file():
            raise FileNotFoundError(f"Scheme not found: {name}")
        return path
