"""Skill drill-down — `GET /skills/{name}`.

Calls `mcp_server.tools.catalog.load_skill` to fetch the .md content,
renders it to HTML via the markdown helper, and pulls catalog metadata
(utility, trigger_keywords, applicable_buckets) for the sidebar.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod
from mcp_server.tools.catalog import load_skill

from ..markdown import render as render_markdown

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/skills/{name}", response_class=HTMLResponse)
async def skill_detail(request: Request, name: str) -> HTMLResponse:
    skill_payload = await load_skill(name=name)
    if skill_payload.get("status") != "ok":
        raise HTTPException(
            status_code=404,
            detail=skill_payload.get("error", f"skill {name!r} not found"),
        )

    pool = db_mod.get_pool()
    metadata: dict[str, Any] = {}
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT description_short, description_full, applicable_buckets,
                       trigger_keywords, utility_score, usage_count, last_used_at,
                       created_at, embedding IS NOT NULL AS has_embedding
                FROM   tools_catalog
                WHERE  name = %s AND kind = 'skill'
                """,
                (name,),
            )
            r = await cur.fetchone()
    if r is not None:
        metadata = {
            "description_short": r[0],
            "description_full": r[1],
            "applicable_buckets": list(r[2] or []),
            "trigger_keywords": list(r[3] or []),
            "utility_score": float(r[4] or 0.0),
            "usage_count": int(r[5] or 0),
            "last_used_at": r[6].isoformat() if r[6] else None,
            "created_at": r[7].isoformat() if r[7] else None,
            "has_embedding": bool(r[8]),
        }

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="skill_detail.html",
        context={
            "active_view": "skills",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "name": name,
            "skill_path": skill_payload.get("skill_file_path", ""),
            "rendered_html": render_markdown(skill_payload.get("content", "")),
            "metadata": metadata,
        },
    )
