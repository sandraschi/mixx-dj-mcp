"""Apply token-based hex replacements to QSS and SVG text."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .palette import load_scheme


def apply_hex_replacements(content: str, replacements: dict[str, str]) -> tuple[str, int]:
    count = 0
    for old, new in sorted(replacements.items(), key=lambda kv: len(kv[0]), reverse=True):
        if old == new:
            continue
        occurrences = content.count(old)
        if occurrences:
            content = content.replace(old, new)
            count += occurrences
    return content, count


def patch_qss_file(qss_path: Path, scheme_path: Path, *, dry_run: bool = False) -> dict[str, Any]:
    scheme = load_scheme(scheme_path)
    original = qss_path.read_text(encoding="utf-8")
    patched, count = apply_hex_replacements(original, scheme.get("hex_replacements", {}))

    if not dry_run and patched != original:
        qss_path.write_text(patched, encoding="utf-8")

    return {
        "path": str(qss_path),
        "scheme": scheme.get("name", scheme_path.stem),
        "replacements_applied": count,
        "changed": patched != original,
    }
