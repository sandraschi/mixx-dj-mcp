import pytest


@pytest.mark.asyncio
async def test_list_effects():
    from mixx_dj_mcp.tools.effects import mixx_effects

    result = await mixx_effects(operation="list_effects", rack=1, unit=1)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_chain_load():
    from mixx_dj_mcp.tools.effects import get_bridge, mixx_effects

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_effects(operation="chain_load", rack=1, unit=1, effect="Flanger")
    assert result["success"] is True
    b.send.assert_called_once_with("/EffectRack1_EffectUnit1/chain_load", "Flanger")


@pytest.mark.asyncio
async def test_chain_clear():
    from mixx_dj_mcp.tools.effects import get_bridge, mixx_effects

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_effects(operation="chain_clear", rack=1, unit=1)
    assert result["success"] is True
    b.send.assert_called_once_with("/EffectRack1_EffectUnit1/chain_clear", 1.0)


@pytest.mark.asyncio
async def test_effect_enable():
    from mixx_dj_mcp.tools.effects import get_bridge, mixx_effects

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_effects(operation="effect_enable", rack=1, unit=1, enable=True)
    assert result["success"] is True
    b.send.assert_called_once_with("/EffectRack1_EffectUnit1/enabled", 1.0)


@pytest.mark.asyncio
async def test_effect_disable():
    from mixx_dj_mcp.tools.effects import get_bridge, mixx_effects

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_effects(operation="effect_enable", rack=1, unit=1, enable=False)
    assert result["success"] is True
    b.send.assert_called_once_with("/EffectRack1_EffectUnit1/enabled", 0.0)


@pytest.mark.asyncio
async def test_parameter_set():
    from mixx_dj_mcp.tools.effects import get_bridge, mixx_effects

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_effects(operation="parameter_set", rack=1, unit=1, parameter=2, value=0.75)
    assert result["success"] is True
    b.send.assert_called_once_with("/EffectRack1_EffectUnit1/parameter2", 0.75)


@pytest.mark.asyncio
async def test_meta_set():
    from mixx_dj_mcp.tools.effects import get_bridge, mixx_effects

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_effects(operation="meta_set", rack=1, unit=1, value=0.5)
    assert result["success"] is True
    b.send.assert_called_once_with("/EffectRack1_EffectUnit1/meta", 0.5)


@pytest.mark.asyncio
async def test_invalid_operation():
    from mixx_dj_mcp.tools.effects import mixx_effects

    result = await mixx_effects(operation="nonexistent_op", rack=1, unit=1)
    assert result["success"] is False


@pytest.mark.asyncio
async def test_missing_effect_name():
    from mixx_dj_mcp.tools.effects import mixx_effects

    result = await mixx_effects(operation="chain_load", rack=1, unit=1)
    assert result["success"] is False
