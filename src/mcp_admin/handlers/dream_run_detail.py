"""Dream Engine run drill-down — `GET /dream-engine/{run_id}`.

Pretty-prints jobs_run + failures JSONB. No journalctl excerpt in V1
(would require subprocess + careful escaping; defer to fase 2).
"""
from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/dream-engine/run/{run_id}", response_class=HTMLResponse)
async def dream_run_detail(request: Request, run_id: str) -> HTMLResponse:
    pool = db_mod.get_pool()
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, started_at, completed_at, status,
                       jobs_run, failures, worker_pid
                FROM   dream_engine_runs
                WHERE  id = %s
                """,
                (run_id,),
            )
            r = await cur.fetchone()
    if r is None:
        raise HTTPException(status_code=404, detail=f"run {run_id!r} not found")

    duration_ms = (
        int((r[2] - r[1]).total_seconds() * 1000) if r[1] and r[2] else None
    )
    run: dict[str, Any] = {
        "id": str(r[0]),
        "started_at": r[1].isoformat() if r[1] else "",
        "completed_at": r[2].isoformat() if r[2] else "",
        "duration_ms": duration_ms,
        "status": r[3],
        "jobs_run": r[4] or {},
        "failures": r[5] or [],
        "worker_pid": r[6],
        "jobs_run_json": json.dumps(r[4] or {}, indent=2),
        "failures_json": json.dumps(r[5] or [], indent=2),
    }

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="dream_run_detail.html",
        context={
            "active_view": "dream_engine",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "run": run,
        },
    )
