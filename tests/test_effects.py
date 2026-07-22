"""Tests for the effects control tool."""
import pytest
from unittest.mock import patch


class TestEffectsTool:
    """Test the mixx_effects portmanteau tool."""

    @pytest.mark.asyncio
    async def test_list_effects(self, mock_osc_bridge):
        """Test listing available effects."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="list_effects")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_chains(self, mock_osc_bridge):
        """Test listing effect chains."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="list_chains")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_chain_load(self, mock_osc_bridge):
        """Test loading an effect chain."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="chain_load", unit=1, chain="Reverb")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_chain_enable(self, mock_osc_bridge):
        """Test enabling an effect chain unit."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="chain_enable", unit=1, enabled=True)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_chain_disable(self, mock_osc_bridge):
        """Test disabling an effect chain unit."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="chain_enable", unit=1, enabled=False)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_parameter_set(self, mock_osc_bridge):
        """Test setting an effect parameter."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="parameter_set", unit=1, index=0, value=0.5)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_parameter_get(self, mock_osc_bridge):
        """Test getting an effect parameter."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="parameter_get", unit=1, index=0)
            assert "value" in result

    @pytest.mark.asyncio
    async def test_chain_insert(self, mock_osc_bridge):
        """Test inserting an effect into a chain."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="chain_insert", unit=1, effect="Flanger")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_chain_clear(self, mock_osc_bridge):
        """Test clearing an effect chain."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="chain_clear", unit=1)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_super_combo(self, mock_osc_bridge):
        """Test setting super combo on an effect unit."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="super_combo", unit=1, value=0.7)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_operation(self, mock_osc_bridge):
        """Test that an invalid operation returns an error."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="nonexistent_op", unit=1)
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_chain_focus(self, mock_osc_bridge):
        """Test focusing an effect chain unit."""
        from mixx_dj_mcp.tools.effects import mixx_effects
        with patch("mixx_dj_mcp.tools.effects.get_bridge", return_value=mock_osc_bridge):
            result = await mixx_effects(operation="chain_focus", unit=1)
            assert result["success"] is True
