"""Load and validate color scheme token files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_HEX = re.compile(r"^#[0-9a-fA-F]{3,8}$")
_RGBA = re.compile(r"^rgba?\([^)]+\)$", re.IGNORECASE)


def load_scheme(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "tokens" not in data:
        raise ValueError(f"Scheme missing 'tokens': {path}")
    for key, value in data["tokens"].items():
        if not (_HEX.match(str(value)) or _RGBA.match(str(value))):
            raise ValueError(f"Invalid color for token '{key}': {value}")
    replacements = data.get("hex_replacements", {})
    for old, new in replacements.items():
        if not _HEX.match(old):
            raise ValueError(f"Replacement key must be hex: {old}")
        if not (_HEX.match(str(new)) or _RGBA.match(str(new))):
            raise ValueError(f"Replacement value invalid for {old}: {new}")
    return data


def format_scheme_summary(scheme: dict[str, Any]) -> str:
    lines = [f"Scheme: {scheme.get('name', '?')}", scheme.get("description", "")]
    lines.append("")
    lines.append("Tokens:")
    for key, value in scheme.get("tokens", {}).items():
        lines.append(f"  {key}: {value}")
    reps = scheme.get("hex_replacements", {})
    if reps:
        lines.append("")
        lines.append(f"Hex replacements: {len(reps)}")
    return "\n".join(lines)
