from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:11116",
            "http://127.0.0.1:11116",
            "http://localhost:11117",
            "http://127.0.0.1:11117",
            "http://tauri.localhost",
            "https://tauri.localhost",
            "tauri://localhost",
        ],
        allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def mount_mcp(app: FastAPI, mcp: FastMCP, config: MixxConfig) -> None:
    try:
        mcp_app = mcp.sse_app()
        app.mount("/mcp", mcp_app)
    except (AttributeError, TypeError, Exception) as e:
        import sys
        print(f"MCP SSE mount skipped: {e}", file=sys.stderr)
