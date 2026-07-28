"""API tests for Serato path discovery (no Serato install required)."""

from fastapi.testclient import TestClient

from mixx_dj_mcp.server import fastapi_app


def test_api_library_serato_status():
    client = TestClient(fastapi_app)
    response = client.get("/api/library/serato/status")
    assert response.status_code == 200
    body = response.json()
    assert "serato_installed" in body
    assert "crates" in body
    assert "import_cli_hint" in body
