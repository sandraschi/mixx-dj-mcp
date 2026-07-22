"""Tests for the mixer control tool."""
import pytest
from unittest.mock import patch


class TestMixerTool:
    """Test the mixx_mixer portmanteau tool."""

    @pytest.mark.asyncio
    async def test_crossfader_center(self, mock_osc_bridge):
        """Test setting crossfader to center."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="crossfader", value=0.5)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_crossfader_left(self, mock_osc_bridge):
        """Test setting crossfader to far left."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="crossfader", value=0.0)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_crossfader_right(self, mock_osc_bridge):
        """Test setting crossfader to far right."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="crossfader", value=1.0)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_crossfader_curve(self, mock_osc_bridge):
        """Test setting crossfader curve."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="crossfader_curve", value=0.3)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_crossfader_assign_left(self, mock_osc_bridge):
        """Test assigning deck to left crossfader."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="crossfader_assign", deck=1, orientation="left")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_volume_set(self, mock_osc_bridge):
        """Test setting deck volume."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="volume", deck=1, value=0.8)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_headphone_enable(self, mock_osc_bridge):
        """Test enabling headphone cue."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="headphone", deck=1, enabled=True)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_headphone_disable(self, mock_osc_bridge):
        """Test disabling headphone cue."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="headphone", deck=1, enabled=False)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_headphone_volume(self, mock_osc_bridge):
        """Test setting headphone volume."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="headphone_volume", value=0.7)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_headphone_mix(self, mock_osc_bridge):
        """Test setting headphone mix."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="headphone_mix", value=0.5)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_eq_low_boost(self, mock_osc_bridge):
        """Test boosting low EQ band."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="eq", deck=1, band="low", value=0.8)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_eq_mid_cut(self, mock_osc_bridge):
        """Test cutting mid EQ band."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="eq", deck=1, band="mid", value=0.0)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_eq_high_set(self, mock_osc_bridge):
        """Test setting high EQ band."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="eq", deck=1, band="high", value=0.6)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_eq_kill_low(self, mock_osc_bridge):
        """Test killing low EQ band."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="eq_kill", deck=1, band="low")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_gain_positive(self, mock_osc_bridge):
        """Test adding gain."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="gain", deck=1, value=3.0)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_gain_negative(self, mock_osc_bridge):
        """Test reducing gain."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="gain", deck=1, value=-2.0)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_master_volume(self, mock_osc_bridge):
        """Test setting master volume."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="master_volume", value=0.85)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_balance(self, mock_osc_bridge):
        """Test setting balance."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="balance", value=0.0)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_operation(self, mock_osc_bridge):
        """Test that an invalid operation returns an error."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="nonexistent_op", deck=1)
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_eq_band(self, mock_osc_bridge):
        """Test that an invalid EQ band returns an error."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="eq", deck=1, band="sub", value=0.5)
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_gain_out_of_range(self, mock_osc_bridge):
        """Test that out-of-range gain returns an error."""
        from mixx_dj_mcp.tools.mixer import mixx_mixer
        with patch("mixx_dj_mcp.tools.mixer.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_mixer(operation="gain", deck=1, value=15.0)
            assert result["success"] is False
