import argparse
import logging
import os
from typing import Literal

import uvicorn

logger = logging.getLogger(__name__)

TransportType = Literal["stdio", "http", "sse"]

ENV_TRANSPORT = "MCP_TRANSPORT"
ENV_HOST = "MCP_HOST"
ENV_PORT = "MCP_PORT"
ENV_PATH = "MCP_PATH"

DEFAULT_PORT = 11116


def get_transport_config() -> dict:
    return {
        "transport": os.getenv(ENV_TRANSPORT, "stdio").lower(),
        "host": os.getenv(ENV_HOST, "127.0.0.1"),
        "port": int(os.getenv(ENV_PORT, str(DEFAULT_PORT))),
        "path": os.getenv(ENV_PATH, "/mcp"),
    }


def create_argument_parser(server_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"{server_name} - FastMCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument("--stdio", action="store_true", help="Run in STDIO mode (default)")
    transport_group.add_argument("--http", action="store_true", help="Run in HTTP Streamable mode")
    transport_group.add_argument("--sse", action="store_true", help="Run in SSE mode (deprecated)")
    parser.add_argument("--host", default=None, help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port to listen on")
    parser.add_argument("--path", default=None, help="HTTP endpoint path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser


def resolve_transport(args: argparse.Namespace) -> TransportType:
    if args.http:
        return "http"
    elif args.sse:
        logger.warning("SSE transport is deprecated. Use --http instead.")
        return "sse"
    elif args.stdio:
        return "stdio"
    else:
        env_transport = os.getenv(ENV_TRANSPORT, "stdio").lower()
        if env_transport not in ("stdio", "http", "sse"):
            return "stdio"
        return env_transport


def resolve_config(args: argparse.Namespace) -> dict:
    env_config = get_transport_config()
    return {
        "transport": resolve_transport(args),
        "host": args.host if args.host is not None else env_config["host"],
        "port": args.port if args.port is not None else env_config["port"],
        "path": args.path if args.path is not None else env_config["path"],
    }


def run_http(mcp_app, host: str = "127.0.0.1", port: int = 11116) -> None:
    logger.info(f"Starting HTTP server on {host}:{port}")
    uvicorn.run(mcp_app, host=host, port=port, log_level="info")


async def run_http_async(mcp_app, host: str = "127.0.0.1", port: int = 11116) -> None:
    config = uvicorn.Config(mcp_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


def run_stdio(mcp) -> None:
    logger.info("Running in STDIO mode")
    mcp.run(transport="stdio")


async def run_stdio_async(mcp) -> None:
    logger.info("Running in STDIO mode")
    await mcp.run_stdio_async()


__all__ = [
    "ENV_HOST",
    "ENV_PATH",
    "ENV_PORT",
    "ENV_TRANSPORT",
    "TransportType",
    "create_argument_parser",
    "get_transport_config",
    "resolve_config",
    "resolve_transport",
    "run_http",
    "run_http_async",
    "run_stdio",
    "run_stdio_async",
]
