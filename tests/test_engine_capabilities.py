"""Tests for engine_capabilities.py - the Mixxx-vs-mixxxxx feature matrix.

No coverage existed for this module before this file. Written after a
rename (rekordbox_export -> engine_export, matching mixxxxx's own
RekordboxExporter -> EngineExporter rename, see mixxxxx docs/TODO.md item
13) that had to be applied by hand with a grep sweep because nothing here
would have caught a stale key name. The regression tests below exist so
that never has to happen silently again.
"""

from unittest.mock import MagicMock

from mixx_dj_mcp.engine_capabilities import (
    MIXXXXX_ONLY,
    build_capabilities,
    get_engine_capabilities,
    infer_fork_from_process,
    resolve_fork,
)
from mixx_dj_mcp.mixxx_launcher import MixxxProcessInfo


def test_engine_export_key_present_not_rekordbox():
    """Regression test for the rename itself: the feature key is
    engine_export, and the old rekordbox_export name must not silently
    reappear (e.g. from a stale merge or a partially-reverted edit)."""
    caps = build_capabilities(fork="mixxxxx", process_running=True, osc_connected=True)
    assert "engine_export" in caps["features"]
    assert "rekordbox_export" not in caps["features"]
    assert "engine_export" in MIXXXXX_ONLY
    assert "rekordbox_export" not in MIXXXXX_ONLY


def test_engine_export_available_on_mixxxxx():
    caps = build_capabilities(fork="mixxxxx", process_running=True, osc_connected=True)
    assert caps["features"]["engine_export"]["available"] is True
    assert caps["features"]["engine_export"]["enabled"] is True


def test_engine_export_unavailable_on_vanilla_mixxx():
    """mixxxxx-only features must be gated off on vanilla Mixxx, which has
    no export/video/stem stack at all."""
    caps = build_capabilities(fork="mixxx", process_running=True, osc_connected=True)
    assert caps["features"]["engine_export"]["available"] is False
    assert caps["features"]["engine_export"]["enabled"] is False
    assert "mixxxxx" in caps["features"]["engine_export"]["reason"].lower()


def test_engine_export_unavailable_when_fork_unknown_and_not_running():
    caps = build_capabilities(fork="unknown", process_running=False, osc_connected=False)
    assert caps["features"]["engine_export"]["available"] is False
    assert caps["features"]["engine_export"]["enabled"] is False


def test_osc_gated_feature_available_but_disabled_without_osc():
    """crossfader needs live OSC but isn't mixxxxx-only - should be
    reported available (the deck exists) but not enabled until OSC
    connects, distinct from a mixxxxx-only feature on vanilla Mixxx."""
    caps = build_capabilities(fork="mixxxxx", process_running=True, osc_connected=False)
    assert caps["features"]["crossfader"]["available"] is True
    assert caps["features"]["crossfader"]["enabled"] is False


def test_summary_reflects_fork_and_osc_state():
    connected = build_capabilities(fork="mixxxxx", process_running=True, osc_connected=True)
    assert "full av feature set" in connected["summary"].lower()

    vanilla = build_capabilities(fork="mixxx", process_running=True, osc_connected=True)
    assert "audio/osc only" in vanilla["summary"].lower()

    unknown = build_capabilities(fork="unknown", process_running=False, osc_connected=False)
    assert "unknown" in unknown["summary"].lower()


def test_infer_fork_from_process_detects_mixxxxx_by_path():
    proc = MixxxProcessInfo(running=True, pid=123, exe="D:\\Dev\\repos\\mixxxxx\\build\\mixxx.exe")
    assert infer_fork_from_process(proc) == "mixxxxx"


def test_infer_fork_from_process_detects_vanilla_in_program_files():
    proc = MixxxProcessInfo(running=True, pid=123, exe="C:\\Program Files\\Mixxx\\mixxx.exe")
    assert infer_fork_from_process(proc) == "mixxx"


def test_infer_fork_from_process_not_running_is_unknown():
    proc = MixxxProcessInfo(running=False, pid=None, exe=None)
    assert infer_fork_from_process(proc) == "unknown"


def test_resolve_fork_prefers_osc_video_co_over_process_path():
    """A live video/phase CO over OSC is stronger evidence than the exe
    path - e.g. a dev build of mixxxxx that still produces mixxx.exe
    outside the mixxxxx tree should still resolve correctly once OSC
    confirms it via a fork-specific CO."""
    proc = MixxxProcessInfo(running=True, pid=1, exe="C:\\Program Files\\Mixxx\\mixxx.exe")
    fork = resolve_fork(proc=proc, osc_connected=True, osc_has_video_co=True, osc_has_phase_co=False)
    assert fork == "mixxxxx"


def test_get_engine_capabilities_reports_engine_export_when_connected():
    """End-to-end through get_engine_capabilities(bridge) - the actual
    entry point server.py calls - not just the pure build_capabilities()
    helper, so a mismatch between this module's expected bridge interface
    (probe_mixxx/has_received_co) and whatever bridge is actually passed
    would show up here too."""
    bridge = MagicMock()
    bridge._running = True
    bridge.probe_mixxx.return_value = True
    bridge.has_received_co.side_effect = lambda name, _default: name == "video_enabled"

    caps = get_engine_capabilities(bridge)

    assert caps["osc_connected"] is True
    assert caps["fork"] == "mixxxxx"
    assert caps["features"]["engine_export"]["available"] is True
