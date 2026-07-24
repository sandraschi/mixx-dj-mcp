"""PyInstaller entry point -- dual transport."""
import os
import sys

sys.path.insert(0, "src")

port = os.environ.get("MIXX_MCP_PORT") or os.environ.get("MCP_PORT") or os.environ.get("PORT")
if port:
    host = os.environ.get("MIXX_MCP_HOST") or os.environ.get("MCP_HOST", "127.0.0.1")
    os.environ.setdefault("HTTP_PORT", str(port))
    os.environ.setdefault("HTTP_HOST", host)

import _strptime  # noqa: F401
import _datetime  # noqa: F401
import mcp.types  # noqa: F401

from mixx_dj_mcp.server import main
main()
