"""Skills list view — `GET /skills`.

Lists all `tools_catalog` rows with `kind='skill'`. Optional bucket filter
via `?bucket=`. Click on a skill row → existing `/skills/{name}` drill-
down.
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


@router.get("/skills", response_class=HTMLResponse)
async def skills_list(
    request: Request,
    bucket: str | None = Query(None),
    q: str | None = Query(None),
) -> HTMLResponse:
    where: list[str] = ["kind = 'skill'", "archived_at IS NULL", "deprecated = false"]
    params: list[Any] = []
    if bucket:
        where.append("%s = ANY(applicable_buckets)")
        params.append(bucket)
    if q:
        where.append("(name ILIKE %s OR description_short ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])
    w = " AND ".join(where)

    pool = db_mod.get_pool()
    skills: list[dict[str, Any]] = []
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT name, description_short, applicable_buckets,
                       utility_score, usage_count, last_used_at,
                       array_length(trigger_keywords, 1) AS kw_count,
                       embedding IS NOT NULL,
                       skill_file_path, created_at
                FROM   tools_catalog
                WHERE  {w}
                ORDER  BY utility_score DESC NULLS LAST, usage_count DESC, name ASC
                """,
                tuple(params),
            )
            for r in await cur.fetchall():
                skills.append(
                    {
                        "name": r[0],
                        "description_short": r[1],
                        "applicable_buckets": list(r[2] or []),
                        "utility_score": float(r[3] or 0.0),
                        "usage_count": int(r[4] or 0),
                        "last_used_at": r[5].isoformat() if r[5] else None,
                        "kw_count": int(r[6] or 0),
                        "has_embedding": bool(r[7]),
                        "skill_file_path": r[8],
                        "created_at": r[9].isoformat() if r[9] else "",
                    }
                )

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="skills_list.html",
        context={
            "active_view": "skills",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "skills": skills,
            "bucket": bucket or "",
            "q": q or "",
        },
    )
