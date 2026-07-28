"""Tests for OSC port checks and inkscape client."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mixx_dj_mcp.osc_ports import osc_port_status, udp_port_available


def test_udp_port_available_loopback():
    assert udp_port_available("127.0.0.1", 0) is True


def test_osc_port_status_shape():
    st = osc_port_status(listen_host="127.0.0.1", listen_port=49152, send_port=49153)
    assert st["listen_port"] == 49152
    assert st["send_port"] == 49153
    assert "ready" in st
    assert "clash_hint" in st


@pytest.mark.asyncio
async def test_call_v1_tool_success():
    from mixx_dj_mcp.skinmaker.inkscape_client import call_v1_tool

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"success": True, "data": {"ok": True}}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("mixx_dj_mcp.skinmaker.inkscape_client.httpx.AsyncClient", return_value=mock_client):
        out = await call_v1_tool("inkscape_file", {"operation": "validate", "input_path": "x.svg"})
    assert out == {"ok": True}
    mock_client.post.assert_awaited_once()
