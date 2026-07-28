"""Tests for first-run setup and launcher path priority."""

from pathlib import Path
from unittest.mock import patch

from mixx_dj_mcp.first_run import get_first_run_status
from mixx_dj_mcp.mixxx_launcher import (
    _mixxxxx_candidates,
    _osc_launcher_cmd,
)


def test_mixxxxx_candidates_prefers_program_files():
    paths = [str(p) for p in _mixxxxx_candidates()]
    assert any("Mixxxxx" in p and "Program Files" in p for p in paths)
    assert paths.index(next(p for p in paths if "Program Files" in p and "Mixxxxx" in p)) < paths.index(
        next(p for p in paths if "Dev" in p and "repos" in p)
    )


def test_osc_launcher_cmd_detects_script(tmp_path: Path):
    exe = tmp_path / "mixxx.exe"
    exe.write_text("", encoding="utf-8")
    (tmp_path / "mixxxxx-osc.cmd").write_text("@echo off\n", encoding="utf-8")
    assert _osc_launcher_cmd(str(exe)) == tmp_path / "mixxxxx-osc.cmd"


def test_first_run_not_ready_without_install():
    with patch("mixx_dj_mcp.first_run.detect_installations", return_value=[]):
        with patch("mixx_dj_mcp.first_run.get_process_info") as proc:
            proc.return_value = type("P", (), {"running": False})()
            st = get_first_run_status(osc_connected=False)
    assert st["ready"] is False
    assert st["steps"][0]["id"] == "install_mixxxxx"
    assert st["steps"][0]["done"] is False


def test_api_mixxx_setup():
    from fastapi.testclient import TestClient

    from mixx_dj_mcp.server import fastapi_app

    client = TestClient(fastapi_app)
    r = client.get("/api/mixxx/setup")
    assert r.status_code == 200
    body = r.json()
    assert "ready" in body
    assert len(body["steps"]) == 3
