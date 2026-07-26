import asyncio
import logging
import threading
import time
from typing import Any

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from rich.console import Console

from ..config import MixxConfig
from .protocol import DECK_OBSERVED_COS, OSC_IN_PORT

logger = logging.getLogger(__name__)
console = Console(file=__import__("sys").stderr)

_bridge_instance: "OscBridge | None" = None


def get_bridge() -> "OscBridge":
    global _bridge_instance
    if _bridge_instance is None:
        raise RuntimeError("OscBridge not initialized. Call OscBridge.start() first.")
    return _bridge_instance


class OscBridge:
    def __init__(self, config: MixxConfig):
        self.config = config
        self._send_client = udp_client.SimpleUDPClient(config.mixx_host, OSC_IN_PORT)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._server_task: asyncio.Task | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()
        self._mixxx_responded = False
        self._deck_state: dict[int, dict[str, Any]] = {}
        self._global_state: dict[str, Any] = {"crossfader": 0.0}
        for d in range(1, 5):
            self._deck_state[d] = {}
            for co in DECK_OBSERVED_COS:
                self._deck_state[d][co] = 0.0

    def is_connected(self) -> bool:
        if not self._running:
            return False
        with self._lock:
            return self._mixxx_responded

    def probe_mixxx(self, timeout_s: float = 1.0) -> bool:
        """Send heartbeat ping and wait for Mixxx OSC pong."""
        if not self._running:
            return False
        with self._lock:
            self._mixxx_responded = False
        self.send("/mixxxxx/ping", 1.0)
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            with self._lock:
                if self._mixxx_responded:
                    return True
            time.sleep(0.05)
        return False

    def get_state(self, co: str, deck: int, default: Any = None) -> Any:
        with self._lock:
            return self._deck_state.get(deck, {}).get(co, default)

    def get_global_state(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._global_state.get(key, default)

    def _update_state(self, address: str, value: Any) -> None:
        parts = address.strip("/").split("/")
        with self._lock:
            if len(parts) >= 2 and parts[0] == "deck":
                try:
                    deck = int(parts[1])
                except ValueError:
                    deck = None
                if deck and deck in self._deck_state:
                    co = parts[2] if len(parts) > 2 else "unknown"
                    if co in self._deck_state[deck]:
                        self._deck_state[deck][co] = float(value) if isinstance(value, int | float) else value
                    else:
                        self._deck_state[deck][co] = float(value) if isinstance(value, int | float) else value
            elif len(parts) >= 1 and parts[0] == "crossfader":
                self._global_state["crossfader"] = float(value) if isinstance(value, int | float) else value
            elif len(parts) >= 2 and parts[0] == "microphone" and parts[1] == "gain":
                self._global_state["mic_gain"] = float(value) if isinstance(value, int | float) else value
            elif len(parts) >= 2 and parts[0] == "talkover":
                self._global_state["talkover"] = float(value) if isinstance(value, int | float) else value

    def _osc_handler(self, address: str, *args: Any) -> None:
        try:
            if address == "/mixxxxx/pong":
                with self._lock:
                    self._mixxx_responded = True
            if args:
                self._update_state(address, args[0])
                logger.debug("OSC <- %s = %s", address, args[0])
        except Exception as e:
            logger.warning("OSC handler error for %s: %s", address, e)

    def send(self, address: str, value: Any) -> None:
        try:
            if isinstance(value, str):
                self._send_client.send_message(address, value)
            else:
                self._send_client.send_message(address, float(value))
            logger.debug("OSC -> %s = %s", address, value)
        except Exception as e:
            logger.error("OSC send error to %s: %s", address, e)

    def _run_server(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_async_server())

    async def _start_async_server(self) -> None:
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._osc_handler)

        server = AsyncIOOSCUDPServer(
            (self.config.mixx_host, self.config.mixx_osc_out_port),
            dispatcher,
            self._loop,
        )
        transport, protocol = await server.create_serve_endpoint()
        logger.info(
            "OSC bridge listening on %s:%d",
            self.config.mixx_host,
            self.config.mixx_osc_out_port,
        )
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
        finally:
            transport.close()

    def start(self) -> None:
        global _bridge_instance
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        _bridge_instance = self
        if self.probe_mixxx(timeout_s=0.5):
            logger.info("OSC bridge connected to Mixxx on port %d", self.config.mixx_osc_out_port)
        else:
            logger.warning(
                "OSC bridge started but Mixxx did not respond to /mixxxxx/ping on port %d",
                self.config.mixx_osc_out_port,
            )
        logger.info("OSC bridge started on port %d", self.config.mixx_osc_out_port)

    def stop(self) -> None:
        self._running = False
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        global _bridge_instance
        _bridge_instance = None
        logger.info("OSC bridge stopped")
