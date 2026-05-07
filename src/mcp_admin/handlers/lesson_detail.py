"""Lesson drill-down — `GET /memory/lessons/{id}`.

Full card with title / content / next_time / tags / metadata. Approve
and reject actions wire to MCP tools. Archive deferred per phase_c_close
(no `archive_lesson` MCP tool exists in fase 1; tracked as M10.fu5+).
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod
from mcp_server.tools.lessons import approve_lesson, reject_lesson

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/memory/lessons/{lesson_id}", response_class=HTMLResponse)
async def lesson_detail(request: Request, lesson_id: str) -> HTMLResponse:
    pool = db_mod.get_pool()
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, title, content, next_time,
                       bucket, project, category, tags::text[], applicable_buckets::text[],
                       status::text, source, created_at, reviewed_at, updated_at,
                       usage_count, round(utility_score::numeric, 4), last_used_at,
                       embedding IS NOT NULL AS has_embedding
                FROM   lessons
                WHERE  id = %s AND deleted_at IS NULL
                """,
                (lesson_id,),
            )
            r = await cur.fetchone()
    if r is None:
        raise HTTPException(status_code=404, detail=f"lesson {lesson_id} not found")

    lesson: dict[str, Any] = {
        "id": str(r[0]),
        "title": r[1],
        "content": r[2],
        "next_time": r[3],
        "bucket": r[4],
        "project": r[5],
        "category": r[6],
        "tags": list(r[7] or []),
        "applicable_buckets": list(r[8] or []),
        "status": r[9],
        "source": r[10],
        "created_at": r[11].isoformat() if r[11] else "",
        "reviewed_at": r[12].isoformat() if r[12] else None,
        "updated_at": r[13].isoformat() if r[13] else "",
        "usage_count": int(r[14] or 0),
        "utility_score": float(r[15] or 0.0),
        "last_used_at": r[16].isoformat() if r[16] else None,
        "has_embedding": bool(r[17]),
    }

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="lesson_detail.html",
        context={
            "active_view": "memory",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "lesson": lesson,
        },
    )


@router.post("/memory/lessons/{lesson_id}/approve")
async def lesson_approve(
    request: Request, lesson_id: str
) -> RedirectResponse:
    user = getattr(request.state, "user_email", "anonymous")
    log.info("lesson %s approve by %s", lesson_id, user)
    await approve_lesson(id=lesson_id)
    return RedirectResponse(url=f"/memory/lessons/{lesson_id}", status_code=303)


@router.post("/memory/lessons/{lesson_id}/reject")
async def lesson_reject(
    request: Request, lesson_id: str, reason: str = Form("")
) -> RedirectResponse:
    user = getattr(request.state, "user_email", "anonymous")
    log.info("lesson %s reject by %s", lesson_id, user)
    await reject_lesson(
        id=lesson_id, reason=reason or "rejected via admin console"
    )
    return RedirectResponse(url=f"/memory/lessons/{lesson_id}", status_code=303)
