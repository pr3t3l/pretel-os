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
from .tools.awareness import regenerate_bucket_readme, regenerate_project_readme
from .tools.catalog import load_skill, register_skill, register_tool, tool_search
from .tools.context import _get_cache, get_context
from .tools.cross_pollination import (
    list_pending_cross_pollination,
    resolve_cross_pollination,
)
from .tools.health import health
from .tools.report_satisfaction import report_satisfaction
from .tools.lessons import (
    approve_lesson,
    list_pending_lessons,
    reject_lesson,
    save_lesson,
    search_lessons,
)
from .tools.preferences import (
    preference_get,
    preference_list,
    preference_set,
    preference_unset,
)
from .tools.projects import create_project, get_project, list_projects
from .tools.best_practices import (
    best_practice_deactivate,
    best_practice_record,
    best_practice_rollback,
    best_practice_search,
)
from .tools.decisions import decision_record, decision_search, decision_supersede
from .tools.router_feedback import router_feedback_record, router_feedback_review
from .tools.tasks import (
    task_close,
    task_create,
    task_list,
    task_reopen,
    task_update,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("mcp_server")


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[None]:
    log.info("starting db health poller")
    await db_mod.start_background_health_check()

    # Wire LayerBundleCache LISTEN/NOTIFY listener (closes task
    # 5db4bc6f-fbea-4eaf-8de0-7a246b25021f from M4 D.3 follow-ups).
    # Without this, the cache works but stales between MCP restarts.
    cfg = config_mod.load_config()
    layer_cache = _get_cache()
    try:
        layer_cache.start_listener(cfg.database_url)
        log.info("LayerBundleCache LISTEN/NOTIFY listener started")
    except Exception as exc:
        log.warning("layer cache listener failed to start: %s", exc)

    try:
        yield
    finally:
        log.info("stopping layer cache listener + db health poller")
        try:
            layer_cache.stop_listener()
        except Exception as exc:
            log.debug("layer cache stop_listener: %s", exc)
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
    app.tool(report_satisfaction)
    app.tool(save_lesson)
    app.tool(search_lessons)
    app.tool(list_pending_lessons)
    app.tool(approve_lesson)
    app.tool(reject_lesson)
    app.tool(list_pending_cross_pollination)
    app.tool(resolve_cross_pollination)
    app.tool(register_skill)
    app.tool(register_tool)
    app.tool(load_skill)
    app.tool(tool_search)

    # Module 0.X — preferences
    app.tool(preference_set)
    app.tool(preference_get)
    app.tool(preference_list)
    app.tool(preference_unset)

    # Module 0.X — tasks
    app.tool(task_create)
    app.tool(task_list)
    app.tool(task_update)
    app.tool(task_close)
    app.tool(task_reopen)

    # Module 0.X — router_feedback
    app.tool(router_feedback_record)
    app.tool(router_feedback_review)

    # Module 0.X — decisions
    app.tool(decision_record)
    app.tool(decision_search)
    app.tool(decision_supersede)

    # Module 0.X — best_practices
    app.tool(best_practice_record)
    app.tool(best_practice_search)
    app.tool(best_practice_deactivate)
    app.tool(best_practice_rollback)

    # Module 7 Phase B — projects
    app.tool(create_project)
    app.tool(get_project)
    app.tool(list_projects)

    # Module 7.5 — awareness layer (README regeneration)
    app.tool(regenerate_bucket_readme)
    app.tool(regenerate_project_readme)

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
