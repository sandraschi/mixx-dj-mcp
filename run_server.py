"""PyInstaller entry point -- dual transport."""
import os
import sys

sys.path.insert(0, "src")

port = os.environ.get("MCP_PORT") or os.environ.get("PORT")
if port:
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    os.environ.setdefault("HTTP_PORT", str(port))
    os.environ.setdefault("HTTP_HOST", host)

from mixx_dj_mcp.server import main
main()
