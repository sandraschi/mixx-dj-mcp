"""Tests for sfx-mcp proxy routes."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from mixx_dj_mcp import server


@pytest.fixture
def client():
    return TestClient(server.fastapi_app)


def test_sfx_search_proxy(client):
    mock_payload = {
        "success": True,
        "results": [
            {
                "id": 42,
                "name": "Thunder",
                "duration": 2.5,
                "tags": ["nature"],
                "preview_url": "https://example.com/preview.mp3",
                "license": "CC0",
            }
        ],
        "total": 1,
    }
    with (
        patch("mixx_dj_mcp.server.sfx_client.sfx_available", AsyncMock(return_value=True)),
        patch("mixx_dj_mcp.server.sfx_client.search_sounds", AsyncMock(return_value=mock_payload)),
    ):
        response = client.get("/api/sfx/search", params={"q": "thunder"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["sfx_available"] is True
    assert body["results"][0]["name"] == "Thunder"


def test_sfx_search_offline(client):
    with patch("mixx_dj_mcp.server.sfx_client.sfx_available", AsyncMock(return_value=False)):
        response = client.get("/api/sfx/search", params={"q": "thunder"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["sfx_available"] is False


def test_sfx_status(client):
    with patch(
        "mixx_dj_mcp.server.sfx_client.sfx_status",
        AsyncMock(return_value={"available": True, "has_api_key": True, "server": "sfx-mcp"}),
    ):
        response = client.get("/api/sfx/status")
    assert response.status_code == 200
    assert response.json()["available"] is True
