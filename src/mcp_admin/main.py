"""FastAPI app factory for the pretel-os admin console.

Listens on 127.0.0.1 only — the only path to it is via Cloudflare Tunnel,
which puts Cloudflare Access in front. The lifespan reuses the
mcp_server.db pool so we don't create a parallel pool against the same
Postgres.

Run for development:
    PYTHONPATH=/home/pretel/dev/pretel-os/src \\
      DEV_FAKE_USER_EMAIL=you@example.com \\
      /home/pretel/.venvs/pretel-os/bin/python -m mcp_admin.main

Run via systemd:
    systemctl --user start pretel-os-admin.service
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

from .handlers.costs import attach_templates as costs_attach
from .handlers.costs import router as costs_router
from .handlers.db_browser import attach_templates as db_browser_attach
from .handlers.db_browser import router as db_browser_router
from .handlers.dream_engine import attach_templates as dream_engine_attach
from .handlers.dream_engine import router as dream_engine_router
from .handlers.dream_run_detail import attach_templates as dream_run_detail_attach
from .handlers.dream_run_detail import router as dream_run_detail_router
from .handlers.lesson_detail import attach_templates as lesson_detail_attach
from .handlers.lesson_detail import router as lesson_detail_router
from .handlers.memory import attach_templates as memory_attach
from .handlers.memory import router as memory_router
from .handlers.pending import attach_templates as pending_attach
from .handlers.pending import router as pending_router
from .handlers.preferences import attach_templates as preferences_attach
from .handlers.preferences import router as preferences_router
from .handlers.projects_detail import attach_templates as projects_detail_attach
from .handlers.projects_detail import router as projects_detail_router
from .handlers.skills_detail import attach_templates as skills_detail_attach
from .handlers.skills_detail import router as skills_detail_router
# Phase E expansion — list / overview views
from .handlers.buckets import attach_templates as buckets_attach
from .handlers.buckets import router as buckets_router
from .handlers.skills_list import attach_templates as skills_list_attach
from .handlers.skills_list import router as skills_list_router
from .handlers.tools_list import attach_templates as tools_list_attach
from .handlers.tools_list import router as tools_list_router
from .handlers.workers import attach_templates as workers_attach
from .handlers.workers import router as workers_router
from .middleware import AccessIdentityMiddleware

log = logging.getLogger(__name__)

PACKAGE_ROOT = Path(__file__).parent
STATIC_DIR = PACKAGE_ROOT / "static"
TEMPLATES_DIR = PACKAGE_ROOT / "templates"

DEFAULT_PORT = 8088


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open the shared DB pool + health-check poller on startup."""
    pool = db_mod.get_pool()
    await pool.open(wait=True)
    await db_mod.start_background_health_check()
    log.info("mcp_admin: DB pool opened + health-check poller started")
    try:
        yield
    finally:
        await db_mod.stop_background_health_check()
        await pool.close()
        log.info("mcp_admin: DB pool closed")


def build_app() -> FastAPI:
    """Application factory. Tests import this and patch as needed."""
    app = FastAPI(
        title="pretel-os admin",
        description="Single-operator admin console for pretel-os.",
        lifespan=_lifespan,
    )

    app.add_middleware(AccessIdentityMiddleware)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    for attach in (
        preferences_attach,
        memory_attach,
        dream_engine_attach,
        costs_attach,
        pending_attach,
        # Phase C drill-downs
        db_browser_attach,
        skills_detail_attach,
        projects_detail_attach,
        dream_run_detail_attach,
        lesson_detail_attach,
        # Phase E expansion — list / overview views
        skills_list_attach,
        tools_list_attach,
        buckets_attach,
        workers_attach,
    ):
        attach(templates)
    for r in (
        preferences_router,
        memory_router,
        dream_engine_router,
        costs_router,
        pending_router,
        # Phase C drill-downs
        db_browser_router,
        skills_detail_router,
        projects_detail_router,
        dream_run_detail_router,
        lesson_detail_router,
        # Phase E expansion
        skills_list_router,
        tools_list_router,
        buckets_router,
        workers_router,
    ):
        app.include_router(r)

    @app.get("/")
    async def root_redirect() -> dict[str, str]:
        return {"status": "ok", "redirect": "/preferences"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = build_app()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s mcp_admin [%(levelname)s] %(message)s",
    )
    port = int(os.environ.get("PRETEL_ADMIN_PORT", str(DEFAULT_PORT)))
    host = os.environ.get("PRETEL_ADMIN_HOST", "127.0.0.1")
    uvicorn.run(
        "mcp_admin.main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
