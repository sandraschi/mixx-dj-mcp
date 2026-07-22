import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_osc_bridge():
    bridge = MagicMock()
    bridge.is_connected.return_value = True
    bridge.send = MagicMock(return_value=None)
    bridge.get_state = MagicMock(return_value=0.0)
    bridge.get_global_state = MagicMock(return_value=0.0)
    return bridge


@pytest.fixture(autouse=True)
def auto_mock_bridge():
    with patch("mixx_dj_mcp.tools.deck_control.get_bridge") as deck_mock, \
         patch("mixx_dj_mcp.tools.library.get_bridge") as lib_mock, \
         patch("mixx_dj_mcp.tools.effects.get_bridge") as eff_mock, \
         patch("mixx_dj_mcp.tools.mixer.get_bridge") as mix_mock, \
         patch("mixx_dj_mcp.tools.prefab_cards.get_bridge") as pre_mock:
        b = MagicMock()
        b.is_connected.return_value = True
        b.send = MagicMock()
        b.get_state = MagicMock(return_value=0.0)
        b.get_global_state = MagicMock(return_value=0.0)
        deck_mock.return_value = b
        lib_mock.return_value = b
        eff_mock.return_value = b
        mix_mock.return_value = b
        pre_mock.return_value = b
        yield b
