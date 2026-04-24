"""FastMCP server entry point.

Boot sequence:
  1. Load config (crashes early with a clear message if env vars missing).
  2. Construct the FastMCP app with a lifespan that starts / stops the
     background DB health poller.
  3. Register the 7 Phase-1 tools with their async signatures.
  4. Expose /health as an unauthenticated HTTP route.
  5. Wrap the app in PretelAuthMiddleware (ASGI), which short-circuits 401
     for every non-/health request missing the shared secret.
  6. Run Streamable HTTP on MCP_SERVER_HOST:MCP_SERVER_PORT.

Invoked as: python -m mcp_server.main
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import FastMCP
from starlette.middleware import Middleware

from . import config as config_mod
from . import db as db_mod
from .auth import PretelAuthMiddleware
from .tools.catalog import load_skill, register_skill, register_tool, tool_search
from .tools.context import get_context
from .tools.health import health
from .tools.lessons import save_lesson, search_lessons

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("mcp_server")


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[None]:
    log.info("starting db health poller")
    await db_mod.start_background_health_check()
    try:
        yield
    finally:
        log.info("stopping db health poller")
        await db_mod.stop_background_health_check()


def build_app() -> FastMCP:
    cfg = config_mod.load_config()

    app = FastMCP(
        name="pretel-os",
        instructions=(
            "pretel-os MCP server (Part 1). Tools: get_context, save_lesson, "
            "search_lessons, register_skill, register_tool, load_skill, tool_search. "
            "All mutations obey degraded mode per CONSTITUTION §8.43."
        ),
        lifespan=_lifespan,
    )

    app.tool(get_context)
    app.tool(save_lesson)
    app.tool(search_lessons)
    app.tool(register_skill)
    app.tool(register_tool)
    app.tool(load_skill)
    app.tool(tool_search)

    app.custom_route("/health", methods=["GET"])(health)

    log.info(
        "configured: host=%s port=%s embedding_model=%s identity=%s",
        cfg.mcp_server_host,
        cfg.mcp_server_port,
        cfg.openai_embedding_model,
        cfg.identity_path,
    )
    return app


def main() -> None:
    cfg = config_mod.load_config()
    app = build_app()
    middleware = [Middleware(PretelAuthMiddleware, shared_secret=cfg.mcp_shared_secret)]
    try:
        app.run(
            transport="http",
            host=cfg.mcp_server_host,
            port=cfg.mcp_server_port,
            middleware=middleware,
            show_banner=False,
        )
    except KeyboardInterrupt:
        log.info("shutting down on SIGINT")


if __name__ == "__main__":
    main()
