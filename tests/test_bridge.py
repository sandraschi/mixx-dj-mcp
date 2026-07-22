"""Tests for the OSC bridge layer."""
import pytest
from unittest.mock import MagicMock, patch


class TestOSCEncoding:
    def test_deck_play_message(self, mock_osc_bridge):
        """Test OSC message for deck play/pause."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(1, "play", True)
        assert msg.address == "/deck/1/play"
        assert msg.params == [1.0]

    def test_deck_stop_message(self, mock_osc_bridge):
        """Test OSC message for deck stop."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(2, "stop", True)
        assert msg.address == "/deck/2/play"
        assert msg.params == [0.0]

    def test_crossfader_message(self, mock_osc_bridge):
        """Test OSC message for crossfader."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_generic_message
        msg = encode_generic_message("/crossfader", 0.5)
        assert msg.address == "/crossfader"
        assert msg.params == [0.5]

    def test_eq_band_message(self, mock_osc_bridge):
        """Test EQ band OSC message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(1, "filterLow", 0.75)
        assert msg.params == [0.75]

    def test_deck_volume_message(self, mock_osc_bridge):
        """Test deck volume OSC message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(1, "pregain", 0.8)
        assert msg.address == "/deck/1/pregain"

    def test_rate_slider_message(self, mock_osc_bridge):
        """Test rate slider OSC message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(2, "rate", 0.02)
        assert msg.address == "/deck/2/rate"

    def test_headphone_cue_message(self, mock_osc_bridge):
        """Test headphone cue OSC message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(1, "headphone", True)
        assert msg.address == "/deck/1/headphone"

    def test_loop_activate_message(self, mock_osc_bridge):
        """Test loop activate OSC message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(1, "loop_in", True)
        assert msg.address == "/deck/1/loop_in"

    def test_beat_loop_message(self, mock_osc_bridge):
        """Test beat loop size message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(1, "beatloop_8_enabled", True)
        assert msg.address == "/deck/1/beatloop_8_enabled"

    def test_hot_cue_message(self, mock_osc_bridge):
        """Test hot cue OSC message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(1, "hotcue_1_activate", True)
        assert msg.address == "/deck/1/hotcue_1_activate"

    def test_effect_parameter_message(self, mock_osc_bridge):
        """Test effect parameter OSC message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_generic_message
        msg = encode_generic_message("/effect/unit/1/parameter/0", 0.5)
        assert msg.address == "/effect/unit/1/parameter/0"
        assert msg.params == [0.5]

    def test_sync_toggle_message(self, mock_osc_bridge):
        """Test sync toggle message."""
        from mixx_dj_mcp.bridge.osc_bridge import encode_deck_message
        msg = encode_deck_message(2, "sync_enabled", True)
        assert msg.address == "/deck/2/sync_enabled"


class TestOSCBridgeConnection:
    def test_bridge_send_message(self, mock_osc_bridge):
        """Test sending a message through the bridge."""
        msg = mock_osc_bridge.send_message("/deck/1/play", [1.0])
        mock_osc_bridge.send_message.assert_called_once_with("/deck/1/play", [1.0])

    def test_bridge_default_ports(self):
        """Test default OSC bridge port configuration."""
        from mixx_dj_mcp.bridge.osc_bridge import OSCBridge
        bridge = OSCBridge(host="127.0.0.1")
        assert bridge.out_port == 9000
        assert bridge.in_port == 8000

    def test_bridge_custom_ports(self):
        """Test custom port configuration."""
        from mixx_dj_mcp.bridge.osc_bridge import OSCBridge
        bridge = OSCBridge(host="127.0.0.1", out_port=9001, in_port=8001)
        assert bridge.out_port == 9001
        assert bridge.in_port == 8001

    def test_deck_control_mapping_consistency(self, mock_osc_bridge):
        """Verify deck control mapping covers expected controls."""
        from mixx_dj_mcp.bridge.osc_bridge import DECK_CONTROL_MAP
        expected = ["play", "stop", "sync_enabled", "rate", "pregain",
                    "headphone", "loop_in", "loop_out", "beatloop_8_enabled",
                    "hotcue_1_activate"]
        for control in expected:
            assert control in DECK_CONTROL_MAP, f"Missing control: {control}"
