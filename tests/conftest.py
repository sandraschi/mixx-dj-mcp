from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_osc_bridge():
    bridge = MagicMock()
    bridge.is_connected.return_value = True
    bridge.send = MagicMock(return_value=None)
    bridge.get_state = MagicMock(return_value=0.0)
    bridge.get_global_state = MagicMock(return_value=0.0)
    return bridge


@pytest.fixture(autouse=True)
def auto_mock_bridge(mock_osc_bridge):
    with (
        patch("mixx_dj_mcp.tools.deck_control.get_bridge") as deck_mock,
        patch("mixx_dj_mcp.tools.library.get_bridge") as lib_mock,
        patch("mixx_dj_mcp.tools.effects.get_bridge") as eff_mock,
        patch("mixx_dj_mcp.tools.mixer.get_bridge") as mix_mock,
        patch("mixx_dj_mcp.tools.prefab_cards.get_bridge") as pre_mock,
    ):
        deck_mock.return_value = mock_osc_bridge
        lib_mock.return_value = mock_osc_bridge
        eff_mock.return_value = mock_osc_bridge
        mix_mock.return_value = mock_osc_bridge
        pre_mock.return_value = mock_osc_bridge
        yield mock_osc_bridge
