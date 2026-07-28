"""Serato DJ library path helpers (no Serato install required for listing)."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_SERATO_ROOT = Path.home() / "Music" / "_Serato_"
DEFAULT_SUBCRATES = DEFAULT_SERATO_ROOT / "Subcrates"


def serato_subcrates_dir() -> Path:
    """Override with SERATO_SUBCRATES_DIR env."""
    raw = os.getenv("SERATO_SUBCRATES_DIR", "").strip()
    if raw:
        return Path(raw)
    return DEFAULT_SUBCRATES


def serato_installed() -> bool:
    """True if default Serato metadata tree exists."""
    root = serato_subcrates_dir().parent
    db = root / "database V2"
    return root.is_dir() and (db.is_file() or serato_subcrates_dir().is_dir())


def list_serato_crates(directory: Path | None = None) -> list[Path]:
    root = directory or serato_subcrates_dir()
    if not root.is_dir():
        return []
    return sorted(root.glob("*.crate"))


def serato_status() -> dict:
    sub = serato_subcrates_dir()
    crates = list_serato_crates(sub)
    return {
        "serato_installed": serato_installed(),
        "subcrates_dir": str(sub),
        "subcrates_exists": sub.is_dir(),
        "crate_count": len(crates),
        "crates": [
            {
                "name": p.stem,
                "path": str(p.resolve()),
                "size_bytes": p.stat().st_size if p.is_file() else 0,
            }
            for p in crates
        ],
        "import_cli_hint": (
            f'mixxx.exe --import-crate "{crates[0]}" --into-crate "{crates[0].stem}"'
            if crates
            else f'mixxx.exe --import-crate "{sub / "MyCrate.crate"}" --into-crate "MyCrate"'
        ),
        "note": (
            "Serato library found on this machine."
            if serato_installed()
            else "Serato not installed or no _Serato_ folder — use synthetic tests / import when Dani exports crates."
        ),
    }


def mixxx_import_crate_cli(crate_path: Path, into_crate: str) -> str:
    return f'mixxx.exe --import-crate "{crate_path}" --into-crate "{into_crate}"'
