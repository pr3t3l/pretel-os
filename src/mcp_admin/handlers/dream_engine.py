"""Dream Engine view — last 14 nights of `dream_engine_runs` + manual trigger.

Lists run telemetry rows. Manual trigger spawns the existing systemd
service (`pretel-os-dream-engine.service`) — does not duplicate the
Python entry point. systemctl returns immediately because the unit is
Type=oneshot; the run records its own dream_engine_runs row.
"""
from __future__ import annotations

import logging
import subprocess
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/dream-engine", response_class=HTMLResponse)
async def dream_engine_view(request: Request) -> HTMLResponse:
    pool = db_mod.get_pool()
    runs: list[dict[str, Any]] = []
    summary = {"total": 0, "success": 0, "partial": 0, "failed": 0, "running": 0}
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, started_at, completed_at, status, jobs_run, failures, worker_pid
                FROM   dream_engine_runs
                WHERE  started_at > now() - interval '14 days'
                ORDER  BY started_at DESC
                LIMIT  100
                """
            )
            for r in await cur.fetchall():
                runs.append(
                    {
                        "id": str(r[0]),
                        "started_at": r[1].isoformat() if r[1] else "",
                        "completed_at": r[2].isoformat() if r[2] else "",
                        "duration_ms": (
                            int((r[2] - r[1]).total_seconds() * 1000)
                            if r[1] and r[2]
                            else None
                        ),
                        "status": r[3],
                        "jobs_run": r[4] or {},
                        "failures": r[5] or [],
                        "worker_pid": r[6],
                    }
                )
                summary["total"] += 1
                summary[r[3]] = summary.get(r[3], 0) + 1

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="dream_engine.html",
        context={
            "active_view": "dream_engine",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "runs": runs,
            "summary": summary,
        },
    )


@router.post("/dream-engine/run")
async def dream_engine_trigger(request: Request) -> RedirectResponse:
    """Trigger a manual run via systemd. Service is Type=oneshot, so this
    returns immediately; the run inserts its own dream_engine_runs row."""
    user = getattr(request.state, "user_email", "anonymous")
    log.info("dream-engine manual trigger by %s", user)
    try:
        subprocess.run(
            ["systemctl", "--user", "start", "pretel-os-dream-engine.service"],
            check=True,
            timeout=15,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        log.exception("systemctl invocation failed: %s", exc)
    return RedirectResponse(url="/dream-engine", status_code=303)
