"""Invoke registered MCP tool functions from the REST API."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp import FastMCP

ToolFn = Callable[..., Awaitable[Any]]


def build_tool_dispatch(mcp: FastMCP) -> dict[str, ToolFn]:
    """Map MCP tool names to their async callables."""
    dispatch: dict[str, ToolFn] = {}
    manager = getattr(mcp, "_tool_manager", None)
    tools = getattr(manager, "_tools", None) if manager else None
    if not tools:
        return dispatch

    for name, tool in tools.items():
        fn = getattr(tool, "fn", None)
        if fn is None:
            fn = getattr(tool, "function", None)
        if callable(fn):
            dispatch[name] = fn
    return dispatch


async def dispatch_tool(
    dispatch: dict[str, ToolFn],
    name: str,
    arguments: dict[str, Any] | None = None,
) -> Any:
    fn = dispatch.get(name)
    if fn is None:
        return {"success": False, "message": f"Unknown tool: {name}", "data": {}}
    try:
        return await fn(**(arguments or {}))
    except TypeError as exc:
        return {"success": False, "message": f"Invalid arguments for {name}: {exc}", "data": {}}
