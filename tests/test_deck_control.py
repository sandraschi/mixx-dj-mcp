import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_play_pause():
    from mixx_dj_mcp.tools.deck_control import mixx_deck
    from mixx_dj_mcp.tools.deck_control import get_bridge
    b = get_bridge()
    result = await mixx_deck(operation="play_pause", deck=1)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/play", 1.0)


@pytest.mark.asyncio
async def test_stop():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="stop", deck=2)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/2/stop", 1.0)


@pytest.mark.asyncio
async def test_sync_enable():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="sync_enable", deck=1, enable=True)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/sync_enabled", 1.0)


@pytest.mark.asyncio
async def test_rate_set():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="rate_set", deck=1, value=0.05)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/rate", 0.05)


@pytest.mark.asyncio
async def test_load_track():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="load", deck=1, track_path="C:/Music/track.mp3")
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/LoadTrack", "C:/Music/track.mp3")


@pytest.mark.asyncio
async def test_seek():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="seek", deck=1, value=60.0)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/seek", 60.0)


@pytest.mark.asyncio
async def test_cue_set():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="cue_set", deck=1)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/cue_set", 1.0)


@pytest.mark.asyncio
async def test_beatloop():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="beatloop", deck=1, beats=8)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/beatloop_8", 1.0)


@pytest.mark.asyncio
async def test_hotcue_activate():
    from mixx_dj_mcp.tools.deck_control import mixx_deck, get_bridge
    b = get_bridge()
    b.send.reset_mock()
    result = await mixx_deck(operation="hotcue_activate", deck=1, hotcue=3)
    assert result["success"] is True
    b.send.assert_called_once_with("/deck/1/hotcue_3_activated", 1.0)


@pytest.mark.asyncio
async def test_invalid_operation():
    from mixx_dj_mcp.tools.deck_control import mixx_deck
    result = await mixx_deck(operation="invalid_op", deck=1)
    assert result["success"] is False


@pytest.mark.asyncio
async def test_missing_value():
    from mixx_dj_mcp.tools.deck_control import mixx_deck
    result = await mixx_deck(operation="rate_set", deck=1)
    assert result["success"] is False
