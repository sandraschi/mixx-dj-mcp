"""UDP port availability checks for OSC onboarding."""

from __future__ import annotations

import socket


def udp_port_available(host: str, port: int) -> bool:
    """True if we can bind UDP port (nothing else listening)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
        return True
    except OSError:
        return False


def osc_port_status(
    *,
    listen_host: str,
    listen_port: int,
    send_port: int,
) -> dict:
    """
    Check fleet OSC pair.

    mixx-dj-mcp listens on listen_port (Mixxx feedback).
    mixxxxx listens on send_port (commands in).
    """
    listen_free = udp_port_available(listen_host, listen_port)
    send_free = udp_port_available(listen_host, send_port)
    return {
        "listen_port": listen_port,
        "send_port": send_port,
        "host": listen_host,
        "listen_port_free": listen_free,
        "send_port_free": send_free,
        "ready": listen_free and send_free,
        "clash_hint": (
            None
            if listen_free and send_free
            else (
                f"Port clash on {listen_host}: "
                + (f"listen {listen_port} busy" if not listen_free else "")
                + (" · " if not listen_free and not send_free else "")
                + (f"send {send_port} busy" if not send_free else "")
                + ". Stop other Mixxx/MCP instances or pick alternate ports in onboarding."
            )
        ),
    }
