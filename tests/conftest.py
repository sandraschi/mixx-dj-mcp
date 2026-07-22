import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_osc_bridge():
    """Fixture providing a mock OSC bridge."""
    bridge = MagicMock()
    bridge.send_message = AsyncMock(return_value=True)
    bridge.receive_message = AsyncMock(return_value=None)
    bridge.host = "127.0.0.1"
    bridge.out_port = 9000
    bridge.in_port = 8000
    bridge.connected = True
    return bridge


@pytest.fixture
async def async_client():
    """Fixture providing a test HTTP client for the FastAPI app."""
    try:
        from httpx import AsyncClient, ASGITransport
        from mixx_dj_mcp.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    except ImportError:
        pytest.skip("httpx not installed")


@pytest.fixture
def test_config():
    """Fixture providing standard test configuration."""
    return {
        "host": "127.0.0.1",
        "osc_out_port": 8000,
        "osc_in_port": 9000,
        "max_decks": 4,
        "mixx_version": "2.4.0",
    }


@pytest.fixture(autouse=True)
def auto_mock_osc():
    """Auto-mock the OSC bridge for all tests to prevent real network calls."""
    with patch("mixx_dj_mcp.bridge.osc_bridge.OSCBridge") as mock:
        bridge_instance = MagicMock()
        bridge_instance.send_message = MagicMock(return_value=True)
        bridge_instance.host = "127.0.0.1"
        bridge_instance.out_port = 9000
        bridge_instance.in_port = 8000
        bridge_instance.connected = True
        mock.return_value = bridge_instance
        yield mock
