"""Serato crate path helpers (no Serato app required)."""

from pathlib import Path

from mixx_dj_mcp.serato_paths import (
    list_serato_crates,
    mixxx_import_crate_cli,
    serato_subcrates_dir,
)


def test_serato_subcrates_dir_layout():
    p = serato_subcrates_dir()
    assert p.name == "Subcrates"
    assert p.parent.name == "_Serato_"


def test_list_serato_crates_empty_when_missing(tmp_path: Path):
    assert list_serato_crates(tmp_path / "nope") == []


def test_list_serato_crates_finds_crate_files(tmp_path: Path):
    sub = tmp_path / "_Serato_" / "Subcrates"
    sub.mkdir(parents=True)
    (sub / "Warmup.crate").write_bytes(b"\x00")
    (sub / "readme.txt").write_text("x", encoding="utf-8")
    found = list_serato_crates(sub)
    assert len(found) == 1
    assert found[0].name == "Warmup.crate"


def test_serato_status_structure(monkeypatch, tmp_path):
    monkeypatch.setenv("SERATO_SUBCRATES_DIR", str(tmp_path / "empty"))
    from mixx_dj_mcp.serato_paths import serato_status

    st = serato_status()
    assert "serato_installed" in st
    assert st["crate_count"] == 0


def test_mixxx_import_cli_command():
    cmd = mixxx_import_crate_cli(Path(r"C:\Music\_Serato_\Subcrates\Warmup.crate"), "Warmup")
    assert "--import-crate" in cmd
    assert "Warmup.crate" in cmd
    assert '--into-crate "Warmup"' in cmd
