"""Tools list view — `GET /tools`.

Lists all `tools_catalog` rows with `kind='tool'`. Click → existing
`/db/tools_catalog/{id}` drill-down.
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


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/tools", response_class=HTMLResponse)
async def tools_list(
    request: Request,
    bucket: str | None = Query(None),
    q: str | None = Query(None),
) -> HTMLResponse:
    where: list[str] = ["kind = 'tool'", "archived_at IS NULL", "deprecated = false"]
    params: list[Any] = []
    if bucket:
        where.append("%s = ANY(applicable_buckets)")
        params.append(bucket)
    if q:
        where.append("(name ILIKE %s OR description_short ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])
    w = " AND ".join(where)

    pool = db_mod.get_pool()
    tools: list[dict[str, Any]] = []
    buckets_available: list[str] = []
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT id, name, description_short, applicable_buckets,
                       utility_score, usage_count, last_used_at, mcp_tool_name,
                       embedding IS NOT NULL, created_at
                FROM   tools_catalog
                WHERE  {w}
                ORDER  BY utility_score DESC NULLS LAST, usage_count DESC, name ASC
                """,
                tuple(params),
            )
            for r in await cur.fetchall():
                tools.append(
                    {
                        "id": str(r[0]),
                        "name": r[1],
                        "description_short": r[2],
                        "applicable_buckets": list(r[3] or []),
                        "utility_score": float(r[4] or 0.0),
                        "usage_count": int(r[5] or 0),
                        "last_used_at": r[6].isoformat() if r[6] else None,
                        "mcp_tool_name": r[7],
                        "has_embedding": bool(r[8]),
                        "created_at": r[9].isoformat() if r[9] else "",
                    }
                )

            await cur.execute(
                "SELECT DISTINCT unnest(applicable_buckets) AS b "
                "FROM tools_catalog "
                "WHERE kind = 'tool' AND archived_at IS NULL AND deprecated = false "
                "ORDER BY b"
            )
            buckets_available = [str(b[0]) for b in await cur.fetchall()]

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="tools_list.html",
        context={
            "active_view": "tools",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "tools": tools,
            "bucket": bucket or "",
            "q": q or "",
            "total": len(tools),
            "buckets_available": buckets_available,
        },
    )
