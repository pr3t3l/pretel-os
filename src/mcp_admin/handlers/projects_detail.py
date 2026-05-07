"""Project drill-down — `GET /projects/{bucket}/{slug}`.

Calls `mcp_server.tools.projects.get_project` for the registry row + state.
Reads README from disk if present. Lists recent decisions + tasks scoped
to the project.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod
from mcp_server.tools.projects import get_project

from ..markdown import render as render_markdown

log = logging.getLogger(__name__)

router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[3]


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/projects/{bucket}/{slug}", response_class=HTMLResponse)
async def project_detail(
    request: Request, bucket: str, slug: str
) -> HTMLResponse:
    payload = await get_project(bucket=bucket, slug=slug)
    # get_project returns {status:'ok', found:bool, ...}; not_found = found=False.
    if payload.get("status") != "ok" or not payload.get("found"):
        raise HTTPException(
            status_code=404,
            detail=payload.get("error", f"project {bucket}:{slug} not found"),
        )

    project: dict[str, Any] = payload.get("project", {}) or {}
    state: list[dict[str, Any]] = list(payload.get("state", []) or [])

    readme_html = ""
    readme_path = project.get("readme_path")
    if readme_path:
        full = REPO_ROOT / readme_path
        try:
            readme_html = render_markdown(full.read_text())
        except OSError:
            log.warning("README not readable at %s", full)

    project_id = project.get("id")
    decisions: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    if project_id:
        pool = db_mod.get_pool()
        async with pool.connection(timeout=5.0) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, title, severity, scope, status, adr_number, created_at
                    FROM   decisions
                    WHERE  project_id = %s
                    ORDER  BY created_at DESC LIMIT 25
                    """,
                    (project_id,),
                )
                for r in await cur.fetchall():
                    decisions.append(
                        {
                            "id": str(r[0]),
                            "title": r[1],
                            "severity": r[2],
                            "scope": r[3],
                            "status": r[4],
                            "adr_number": r[5],
                            "created_at": r[6].isoformat() if r[6] else "",
                        }
                    )
                await cur.execute(
                    """
                    SELECT id, title, status, priority, created_at
                    FROM   tasks
                    WHERE  project_id = %s
                    ORDER  BY created_at DESC LIMIT 25
                    """,
                    (project_id,),
                )
                for r in await cur.fetchall():
                    tasks.append(
                        {
                            "id": str(r[0]),
                            "title": r[1],
                            "status": r[2],
                            "priority": r[3],
                            "created_at": r[4].isoformat() if r[4] else "",
                        }
                    )

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "active_view": "projects",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "bucket": bucket,
            "slug": slug,
            "project": project,
            "state": state,
            "readme_html": readme_html,
            "decisions": decisions,
            "tasks": tasks,
        },
    )
