"""Workers + services view — `GET /workers`.

Shows the 4 chartered workers per CONSTITUTION §2.6 (post-amendment v5.2)
plus the 3 sibling services (MCP server, Telegram bot, admin console).
Per row: systemd is-active status (via subprocess) + last-activity hint
when a relevant DB signal exists.
"""
from __future__ import annotations

import logging
import subprocess
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


# Chartered workers per CONSTITUTION §2.6 v5.2 (post-M6 amendment).
WORKERS: list[dict[str, Any]] = [
    {
        "name": "Dream Engine",
        "kind": "worker",
        "trigger": "Cron 02:00 America/New_York",
        "home": "systemd timer + service",
        "service": "pretel-os-dream-engine.service",
        "timer": "pretel-os-dream-engine.timer",
        "details_url": "/dream-engine",
        "constitution_ref": "§2.6 row 1",
        "deferred": False,
    },
    {
        "name": "Morning intelligence",
        "kind": "worker",
        "trigger": "Cron 06:00 America/New_York",
        "home": "n8n workflow",
        "service": None,
        "timer": None,
        "details_url": None,
        "constitution_ref": "§2.6 row 2",
        "deferred": True,
        "deferred_reason": "n8n not yet operational",
    },
    {
        "name": "Auto-index on save",
        "kind": "worker",
        "trigger": "Postgres LISTEN on `embedding_queue` channel + 60s safety scan",
        "home": "systemd user unit (drains `pending_embeddings` via OpenAI text-embedding-3-large)",
        "service": "pretel-os-autoindex.service",
        "timer": None,
        "details_url": None,
        "constitution_ref": "§2.6 row 3",
        "deferred": False,
    },
    {
        "name": "README consumer (M7.5)",
        "kind": "worker",
        "trigger": "Postgres LISTEN on `readme_dirty` channel",
        "home": "systemd user unit",
        "service": "pretel-os-readme.service",
        "timer": None,
        "details_url": None,
        "constitution_ref": "§2.6 row 4",
        "deferred": False,
    },
]

SIBLING_SERVICES: list[dict[str, Any]] = [
    {
        "name": "MCP server",
        "kind": "service",
        "purpose": "Single gateway for all clients (Claude.ai, Claude Code, Telegram, admin)",
        "service": "pretel-os-mcp.service",
        "details_url": None,
    },
    {
        "name": "Telegram bot",
        "kind": "service",
        "purpose": "Operator interface for /save, /idea, /review_pending, /cross_poll_review",
        "service": "pretel-os-bot.service",
        "details_url": None,
    },
    {
        "name": "Admin console (this)",
        "kind": "service",
        "purpose": "Operator dashboard at mcp-admin.alfredopretelvargas.com",
        "service": "pretel-os-admin.service",
        "details_url": "/preferences",
    },
]


def _systemd_is_active(unit: str | None) -> str:
    if not unit:
        return "n/a"
    try:
        r = subprocess.run(
            ["systemctl", "--user", "is-active", unit],
            capture_output=True, text=True, timeout=3,
        )
        return r.stdout.strip() or "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


@router.get("/workers", response_class=HTMLResponse)
async def workers_view(request: Request) -> HTMLResponse:
    workers = []
    for w in WORKERS:
        item = dict(w)
        item["service_status"] = _systemd_is_active(w.get("service"))
        item["timer_status"] = _systemd_is_active(w.get("timer"))
        workers.append(item)

    services = []
    for s in SIBLING_SERVICES:
        item = dict(s)
        item["service_status"] = _systemd_is_active(s.get("service"))
        services.append(item)

    last_activity = await _last_activity_signals()

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="workers.html",
        context={
            "active_view": "workers",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "workers": workers,
            "services": services,
            "last_activity": last_activity,
        },
    )


async def _last_activity_signals() -> dict[str, Any]:
    """Best-effort 'last activity' hints from the DB for each worker."""
    out: dict[str, Any] = {}
    pool = db_mod.get_pool()
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(
                    "SELECT max(started_at), count(*) FROM dream_engine_runs"
                )
                r = await cur.fetchone()
                out["dream_engine_last_run"] = r[0].isoformat() if r and r[0] else None
                out["dream_engine_run_count"] = int(r[1]) if r else 0
            except Exception as exc:
                log.warning("dream_engine signals failed: %s", exc)

            try:
                await cur.execute(
                    "SELECT count(*), min(created_at) FROM pending_embeddings"
                )
                r = await cur.fetchone()
                out["pending_embeddings_count"] = int(r[0]) if r else 0
                out["pending_embeddings_oldest"] = (
                    r[1].isoformat() if r and r[1] else None
                )
            except Exception as exc:
                log.warning("pending_embeddings signals failed: %s", exc)

    return out
