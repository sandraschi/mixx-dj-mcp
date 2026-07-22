"""Tests for the deck control portmanteau tool."""
import pytest
from unittest.mock import AsyncMock, patch


class TestDeckControlTool:
    """Test the mixx_deck portmanteau tool dispatch."""

    @pytest.mark.asyncio
    async def test_play_pause_deck_1(self, mock_osc_bridge):
        """Test play/pause operation on deck 1."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="play_pause", deck=1)
            assert result["success"] is True
            mock_osc_bridge.send_message.assert_called()

    @pytest.mark.asyncio
    async def test_stop_deck(self, mock_osc_bridge):
        """Test stop operation on a deck."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="stop", deck=2)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_sync_enable(self, mock_osc_bridge):
        """Test enabling sync on a deck."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="sync", deck=1, enabled=True)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_rate_set(self, mock_osc_bridge):
        """Test setting the rate on a deck."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="rate", deck=1, value=2.5)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_load_track(self, mock_osc_bridge):
        """Test loading a track onto a deck."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="load", deck=1, track_id="test_track_001")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_seek_position(self, mock_osc_bridge):
        """Test seeking to a position on a deck."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="seek", deck=1, position=60)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_cue_point(self, mock_osc_bridge):
        """Test triggering a cue point."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="cue", deck=1, cue_point=1)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_beat_loop(self, mock_osc_bridge):
        """Test creating a beat loop."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="beat_loop", deck=1, beats=8)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_operation(self, mock_osc_bridge):
        """Test that an invalid operation returns an error."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="nonexistent_op", deck=1)
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_status_check(self, mock_osc_bridge):
        """Test retrieving deck status."""
        from mixx_dj_mcp.tools.deck import mixx_deck
        with patch("mixx_dj_mcp.tools.deck.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_deck(operation="status", deck=1)
            assert "deck" in result["data"]

    def test_portmanteau_operation_literals(self):
        """Verify that the portmanteau operation enum covers all operations."""
        from mixx_dj_mcp.tools.deck import DeckOperation
        expected = {"play_pause", "stop", "cue", "seek", "load", "eject",
                    "sync", "sync_key", "rate", "rate_ramp", "loop_in",
                    "loop_out", "loop_activate", "loop_deactivate",
                    "reloop_toggle", "beat_loop", "beat_jump",
                    "hot_cue_set", "hot_cue_clear", "slip_enable",
                    "slip_disable", "quantize", "status"}
        actual = set(DeckOperation.__args__[0].__args__)
        assert actual == expected, f"Missing operations: {expected - actual}"
