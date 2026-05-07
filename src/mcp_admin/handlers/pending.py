"""Pending review queue — `lessons WHERE status='pending_review'` and
`cross_pollination_queue WHERE status='pending'`. Approve / reject route
through the corresponding MCP tools per CONSTITUTION §2.1.

approve_lesson + reject_lesson live in mcp_server.tools.lessons.
resolve_cross_pollination lives in mcp_server.tools.cross_pollination.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod
from mcp_server.tools.cross_pollination import resolve_cross_pollination
from mcp_server.tools.lessons import approve_lesson, reject_lesson

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/pending", response_class=HTMLResponse)
async def pending_view(request: Request) -> HTMLResponse:
    pool = db_mod.get_pool()
    pending_lessons: list[dict[str, Any]] = []
    pending_xpoll: list[dict[str, Any]] = []

    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, title, bucket, content, next_time, tags, created_at
                FROM   lessons
                WHERE  status = 'pending_review' AND deleted_at IS NULL
                ORDER  BY created_at DESC
                LIMIT  100
                """
            )
            for r in await cur.fetchall():
                pending_lessons.append(
                    {
                        "id": str(r[0]),
                        "title": r[1],
                        "bucket": r[2],
                        "content": r[3],
                        "next_time": r[4],
                        "tags": list(r[5] or []),
                        "created_at": r[6].isoformat() if r[6] else "",
                    }
                )

            await cur.execute(
                """
                SELECT id, origin_bucket, target_bucket, idea, reasoning,
                       confidence_score, proposed_by, created_at
                FROM   cross_pollination_queue
                WHERE  status = 'pending'
                ORDER  BY COALESCE(priority, 99) ASC, created_at ASC
                LIMIT  100
                """
            )
            for r in await cur.fetchall():
                pending_xpoll.append(
                    {
                        "id": str(r[0]),
                        "origin_bucket": r[1],
                        "target_bucket": r[2],
                        "idea": r[3],
                        "reasoning": r[4],
                        "confidence_score": float(r[5]) if r[5] is not None else None,
                        "proposed_by": r[6],
                        "created_at": r[7].isoformat() if r[7] else "",
                    }
                )

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="pending.html",
        context={
            "active_view": "pending",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "pending_lessons": pending_lessons,
            "pending_xpoll": pending_xpoll,
            "lesson_count": len(pending_lessons),
            "xpoll_count": len(pending_xpoll),
        },
    )


@router.post("/pending/lessons/{lesson_id}/{action}")
async def lesson_review(
    request: Request,
    lesson_id: str,
    action: str,
    reason: str = Form(""),
) -> RedirectResponse:
    """approve / reject a pending lesson via MCP tools (NEVER direct SQL)."""
    user = getattr(request.state, "user_email", "anonymous")
    log.info("lesson %s %s by %s", lesson_id, action, user)
    if action == "approve":
        await approve_lesson(id=lesson_id)
    elif action == "reject":
        await reject_lesson(id=lesson_id, reason=reason or "rejected via admin console")
    else:
        log.warning("unknown action %r", action)
    return RedirectResponse(url="/pending", status_code=303)


@router.post("/pending/cross-poll/{xp_id}/{action}")
async def cross_poll_review(
    request: Request,
    xp_id: str,
    action: str,
    note: str = Form(""),
) -> RedirectResponse:
    """approve / reject a pending cross-pollination row."""
    user = getattr(request.state, "user_email", "anonymous")
    log.info("cross-poll %s %s by %s", xp_id, action, user)
    if action in ("approve", "reject"):
        await resolve_cross_pollination(id=xp_id, action=action, note=note or None)
    else:
        log.warning("unknown action %r", action)
    return RedirectResponse(url="/pending", status_code=303)
