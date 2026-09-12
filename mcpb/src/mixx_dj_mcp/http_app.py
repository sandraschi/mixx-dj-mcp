from fastapi import FastAPI
from fastmcp import FastMCP

from .config import MixxConfig


def create_app(config: MixxConfig) -> FastAPI:
    app = FastAPI(
        title=config.mcp_name,
        description="REST API for Mixxx DJ software control via OSC",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    return app


def mount_mcp(app: FastAPI, mcp: FastMCP, config: MixxConfig) -> None:
    try:
        mcp_app = mcp.http_app()
        app.mount("/mcp", mcp_app)
    except Exception as e:
        import sys

        print(f"MCP mount skipped: {e}", file=sys.stderr)
