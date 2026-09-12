"""UDP heartbeat against a minimal fake Mixxx OSC peer (no GUI required)."""

import socket
import struct
import threading
import time

import pytest

from mixx_dj_mcp.bridge.osc_bridge import OscBridge
from mixx_dj_mcp.config import MixxConfig


def _pad_osc_string(text: str) -> bytes:
    raw = text.encode("utf-8") + b"\x00"
    while len(raw) % 4 != 0:
        raw += b"\x00"
    return raw


def _encode_float_message(address: str, value: float) -> bytes:
    blob = _pad_osc_string(address) + _pad_osc_string(",f")
    packed = struct.pack(">f", value)
    return blob + packed


def _read_padded_string(data: bytes, offset: int) -> tuple[str, int]:
    end = data.index(b"\x00", offset)
    text = data[offset:end].decode("utf-8")
    offset = end + 1
    while offset % 4 != 0:
        offset += 1
    return text, offset


def _decode_address(data: bytes) -> str:
    addr, _ = _read_padded_string(data, 0)
    return addr


@pytest.mark.integration
def test_probe_mixxx_against_fake_peer():
    host = "127.0.0.1"
    in_port = 31119
    out_port = 31118
    stop = threading.Event()

    def fake_mixxx() -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, in_port))
        sock.settimeout(0.2)
        reply = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not stop.is_set():
            try:
                data, _addr = sock.recvfrom(4096)
            except TimeoutError:
                continue
            except OSError:
                break
            if _decode_address(data) == "/mixxxxx/ping":
                reply.sendto(
                    _encode_float_message("/mixxxxx/pong", 1.0),
                    (host, out_port),
                )
        sock.close()
        reply.close()

    thread = threading.Thread(target=fake_mixxx, daemon=True)
    thread.start()
    time.sleep(0.05)

    cfg = MixxConfig(
        mixx_host=host,
        mixx_osc_in_port=in_port,
        mixx_osc_out_port=out_port,
    )
    bridge = OscBridge(cfg)
    try:
        bridge.start()
        time.sleep(0.1)
        assert bridge.probe_mixxx(timeout_s=1.5) is True
    finally:
        bridge.stop()
        stop.set()
        thread.join(timeout=2)
