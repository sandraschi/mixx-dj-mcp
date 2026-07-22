import pytest
from unittest.mock import MagicMock, patch


class TestOscBridge:
    def test_bridge_send(self, mock_osc_bridge):
        mock_osc_bridge.send("/deck/1/play", 1.0)
        mock_osc_bridge.send.assert_called_once_with("/deck/1/play", 1.0)

    def test_bridge_is_connected(self, mock_osc_bridge):
        assert mock_osc_bridge.is_connected() is True

    def test_bridge_get_state(self, mock_osc_bridge):
        mock_osc_bridge.get_state.return_value = 128.0
        val = mock_osc_bridge.get_state("bpm", 1)
        assert val == 128.0

    def test_bridge_get_global_state(self, mock_osc_bridge):
        mock_osc_bridge.get_global_state.return_value = 0.5
        val = mock_osc_bridge.get_global_state("crossfader")
        assert val == 0.5


class TestProtocolAddresses:
    def test_deck_address_pattern(self):
        from mixx_dj_mcp.bridge.protocol import CO_ADDRESS_PATTERNS
        addr = CO_ADDRESS_PATTERNS["play"].format(deck=1)
        assert addr == "/deck/1/play"

    def test_crossfader_address(self):
        from mixx_dj_mcp.bridge.protocol import CO_ADDRESS_PATTERNS
        assert CO_ADDRESS_PATTERNS["crossfader"] == "/crossfader"

    def test_effect_address_pattern(self):
        from mixx_dj_mcp.bridge.protocol import CO_ADDRESS_PATTERNS
        addr = CO_ADDRESS_PATTERNS["effect_enabled"].format(rack=1, unit=1)
        assert addr == "/EffectRack1_EffectUnit1/enabled"

    def test_library_search_address(self):
        from mixx_dj_mcp.bridge.protocol import CO_ADDRESS_PATTERNS
        assert CO_ADDRESS_PATTERNS["library_search"] == "/library/search"

    def test_deck_observed_cos(self):
        from mixx_dj_mcp.bridge.protocol import DECK_OBSERVED_COS
        assert "play" in DECK_OBSERVED_COS
        assert "bpm" in DECK_OBSERVED_COS
        assert "rate" in DECK_OBSERVED_COS
