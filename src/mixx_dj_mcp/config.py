import os
from dataclasses import dataclass


@dataclass
class MixxConfig:
    mixx_host: str = "127.0.0.1"
    mixx_osc_out_port: int = 11118
    mixx_osc_in_port: int = 11119
    http_host: str = "127.0.0.1"
    http_port: int = 11116
    mcp_name: str = "Mixx-DJ-MCP"
    telemetry_enabled: bool = True
    plex_mcp_url: str = "http://127.0.0.1:10740"

    @classmethod
    def from_env(cls) -> "MixxConfig":
        return cls(
            mixx_host=os.getenv("MIXX_HOST", "127.0.0.1"),
            mixx_osc_out_port=int(os.getenv("MIXX_OSC_OUT_PORT", "11118")),
            mixx_osc_in_port=int(os.getenv("MIXX_OSC_IN_PORT", "11119")),
            http_host=os.getenv("HTTP_HOST", "127.0.0.1"),
            http_port=int(os.getenv("HTTP_PORT", "11116")),
            mcp_name=os.getenv("MCP_NAME", "Mixx-DJ-MCP"),
            telemetry_enabled=os.getenv("TELEMETRY_ENABLED", "true").lower() in ("1", "true", "yes"),
            plex_mcp_url=os.getenv("PLEX_MCP_URL", "http://127.0.0.1:10740"),
        )
