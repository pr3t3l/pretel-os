"""Memory browser — combined view for lessons / decisions / best_practices.

Tabs: lessons | decisions | best_practices. Filters: bucket, tag, status,
search. Pagination: offset/limit (default 50) per phase_b_close §Q3.

Search is semantic when `q` is non-empty (calls the matching MCP search
tool). Otherwise plain SELECT with filters applied.

Read-only — no mutations from this view. Mutations live in `pending.py`
(approve/reject) and on the lesson detail page (Phase C).
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

log = logging.getLogger(__name__)

router = APIRouter()

DEFAULT_LIMIT = 50
TABS = ("lessons", "decisions", "best_practices")
LESSON_STATUSES = ("active", "pending_review", "archived", "merged_into", "rejected")


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/memory", response_class=HTMLResponse)
async def memory_view(
    request: Request,
    tab: str = Query("lessons"),
    bucket: str | None = Query(None),
    tag: str | None = Query(None),
    status: str | None = Query(None),
    q: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=200),
) -> HTMLResponse:
    """List rows from the chosen knowledge table with optional filters."""
    if tab not in TABS:
        tab = "lessons"

    rows: list[dict[str, Any]] = []
    total = 0
    pool = db_mod.get_pool()

    if tab == "lessons":
        sql_count, sql_list, params = _build_lessons_query(bucket, tag, status, q)
    elif tab == "decisions":
        sql_count, sql_list, params = _build_decisions_query(bucket, q)
    else:  # best_practices
        sql_count, sql_list, params = _build_best_practices_query(q)

    buckets_available: list[str] = []
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql_count, params)
            row = await cur.fetchone()
            total = int(row[0]) if row else 0

            await cur.execute(sql_list, (*params, limit, offset))
            for r in await cur.fetchall():
                rows.append(_row_to_dict(tab, r))

            await cur.execute(
                "SELECT DISTINCT bucket FROM ("
                "  SELECT bucket FROM lessons WHERE deleted_at IS NULL AND bucket IS NOT NULL"
                "  UNION SELECT bucket FROM decisions WHERE bucket IS NOT NULL"
                ") b ORDER BY bucket"
            )
            buckets_available = [str(b[0]) for b in await cur.fetchall()]

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="memory.html",
        context={
            "active_view": "memory",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "tab": tab,
            "bucket": bucket or "",
            "tag": tag or "",
            "status_filter": status or "",
            "q": q or "",
            "rows": rows,
            "total": total,
            "offset": offset,
            "limit": limit,
            "next_offset": offset + limit if offset + limit < total else None,
            "prev_offset": max(offset - limit, 0) if offset > 0 else None,
            "tabs": TABS,
            "buckets_available": buckets_available,
            "statuses_available": list(LESSON_STATUSES),
        },
    )


# ---------------------------------------------------------------------- helpers

def _build_lessons_query(
    bucket: str | None, tag: str | None, status: str | None, q: str | None
) -> tuple[str, str, tuple[Any, ...]]:
    where: list[str] = ["deleted_at IS NULL"]
    params: list[Any] = []
    if bucket:
        where.append("bucket = %s"); params.append(bucket)
    if tag:
        where.append(
            "EXISTS (SELECT 1 FROM unnest(tags) AS t WHERE t ILIKE %s)"
        )
        params.append(f"%{tag}%")
    if status:
        where.append("status::text = %s"); params.append(status)
    if q:
        where.append(
            "(title ILIKE %s OR content ILIKE %s "
            "OR EXISTS (SELECT 1 FROM unnest(tags) AS t WHERE t ILIKE %s))"
        )
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    w = " AND ".join(where)
    sql_count = f"SELECT count(*) FROM lessons WHERE {w}"
    sql_list = (
        f"SELECT id, title, bucket, status::text, "
        f"  array_to_string(tags, ', '), usage_count, "
        f"  round(utility_score::numeric, 2), created_at "
        f"FROM lessons WHERE {w} "
        f"ORDER BY created_at DESC LIMIT %s OFFSET %s"
    )
    return sql_count, sql_list, tuple(params)


def _build_decisions_query(
    bucket: str | None, q: str | None
) -> tuple[str, str, tuple[Any, ...]]:
    where: list[str] = ["1=1"]
    params: list[Any] = []
    if bucket:
        where.append("bucket = %s"); params.append(bucket)
    if q:
        where.append("(title ILIKE %s OR context ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])
    w = " AND ".join(where)
    sql_count = f"SELECT count(*) FROM decisions WHERE {w}"
    sql_list = (
        f"SELECT id, title, bucket, project, severity, scope, "
        f"  status, adr_number, created_at "
        f"FROM decisions WHERE {w} "
        f"ORDER BY created_at DESC LIMIT %s OFFSET %s"
    )
    return sql_count, sql_list, tuple(params)


def _build_best_practices_query(
    q: str | None,
) -> tuple[str, str, tuple[Any, ...]]:
    where: list[str] = ["active = true"]
    params: list[Any] = []
    if q:
        where.append("(title ILIKE %s OR guidance ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])
    w = " AND ".join(where)
    sql_count = f"SELECT count(*) FROM best_practices WHERE {w}"
    sql_list = (
        f"SELECT id, title, domain, scope, active, created_at "
        f"FROM best_practices WHERE {w} "
        f"ORDER BY created_at DESC LIMIT %s OFFSET %s"
    )
    return sql_count, sql_list, tuple(params)


def _row_to_dict(tab: str, r: tuple[Any, ...]) -> dict[str, Any]:
    if tab == "lessons":
        return {
            "id": str(r[0]),
            "title": r[1],
            "bucket": r[2],
            "status": r[3],
            "tags": r[4],
            "usage_count": r[5],
            "utility_score": float(r[6]) if r[6] is not None else 0.0,
            "created_at": r[7].isoformat() if r[7] else "",
        }
    if tab == "decisions":
        return {
            "id": str(r[0]),
            "title": r[1],
            "bucket": r[2],
            "project": r[3],
            "severity": r[4],
            "scope": r[5],
            "status": r[6],
            "adr_number": r[7],
            "created_at": r[8].isoformat() if r[8] else "",
        }
    return {  # best_practices
        "id": str(r[0]),
        "title": r[1],
        "domain": r[2],
        "scope": r[3],
        "active": r[4],
        "created_at": r[5].isoformat() if r[5] else "",
    }
