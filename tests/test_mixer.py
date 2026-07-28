import pytest


@pytest.mark.asyncio
async def test_crossfader_set():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="crossfader_set", value=0.5)
    assert result["success"] is True
    b.send.assert_called_once_with("/crossfader", 0.5)


@pytest.mark.asyncio
async def test_crossfader_curve():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="crossfader_curve", value=0.3)
    assert result["success"] is True
    b.send.assert_called_once_with("/crossfader/curve", 0.3)


@pytest.mark.asyncio
async def test_volume_set():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="volume_set", deck=1, value=0.85)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/volume", 0.85)


@pytest.mark.asyncio
async def test_gain_set():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="gain_set", deck=1, value=2.0)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/pregain", 2.0)


@pytest.mark.asyncio
async def test_volume_clamp():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="volume_set", deck=1, value=5.0)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/volume", 1.0)


@pytest.mark.asyncio
async def test_eq_set():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="eq_set", deck=1, eq_band="low", value=0.8)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/filterLow", 0.8)


@pytest.mark.asyncio
async def test_eq_set_mid():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="eq_set", deck=1, eq_band="mid", value=0.5)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/filterMid", 0.5)


@pytest.mark.asyncio
async def test_eq_set_high():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="eq_set", deck=1, eq_band="high", value=0.6)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/filterHigh", 0.6)


@pytest.mark.asyncio
async def test_headphone_cue():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="headphone_cue", deck=1, enable=True)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/pfl", 1.0)


@pytest.mark.asyncio
async def test_talkover():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="talkover", enable=True)
    assert result["success"] is True
    b.send.assert_called_once_with("/talkover", 1.0)


@pytest.mark.asyncio
async def test_mic_gain():
    from mixx_dj_mcp.tools.mixer import get_bridge, mixx_mixer

    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_mixer(operation="mic_gain", value=0.7)
    assert result["success"] is True
    b.send.assert_called_once_with("/microphone/gain", 0.7)


@pytest.mark.asyncio
async def test_invalid_operation():
    from mixx_dj_mcp.tools.mixer import mixx_mixer

    result = await mixx_mixer(operation="nonexistent_op", deck=1)
    assert result["success"] is False
