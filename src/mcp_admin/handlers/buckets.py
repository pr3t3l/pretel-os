"""Buckets overview — `GET /buckets`.

Shows the 3 fixed buckets (`personal`, `business`, `scout`) plus any
`freelance:<client>` discovered in the projects registry. Per bucket:
counts of active projects / active lessons / decisions / best_practices
+ link to bucket README + list of active projects.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

log = logging.getLogger(__name__)

router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXED_BUCKETS = ("personal", "business", "scout")


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/buckets", response_class=HTMLResponse)
async def buckets_view(request: Request) -> HTMLResponse:
    pool = db_mod.get_pool()
    bucket_names: list[str] = list(FIXED_BUCKETS)
    bucket_data: list[dict[str, Any]] = []

    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT DISTINCT bucket FROM projects
                WHERE  bucket LIKE 'freelance:%'
                  AND  archived_at IS NULL
                ORDER  BY bucket
                """
            )
            for r in await cur.fetchall():
                if r[0] not in bucket_names:
                    bucket_names.append(r[0])

            for b in bucket_names:
                stats = await _bucket_stats(cur, b)
                projects = await _bucket_projects(cur, b)
                readme_path = f"buckets/{b}/README.md"
                readme_exists = (REPO_ROOT / readme_path).exists()
                bucket_data.append(
                    {
                        "name": b,
                        "stats": stats,
                        "projects": projects,
                        "readme_path": readme_path if readme_exists else None,
                        "is_freelance": b.startswith("freelance:"),
                    }
                )

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="buckets.html",
        context={
            "active_view": "buckets",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "buckets": bucket_data,
        },
    )


async def _bucket_stats(cur: Any, bucket: str) -> dict[str, int]:
    out: dict[str, int] = {}
    queries = (
        ("active_projects", "SELECT count(*) FROM projects WHERE bucket=%s AND status='active' AND archived_at IS NULL"),
        ("active_lessons", "SELECT count(*) FROM lessons WHERE bucket=%s AND status='active' AND deleted_at IS NULL"),
        ("pending_lessons", "SELECT count(*) FROM lessons WHERE bucket=%s AND status='pending_review' AND deleted_at IS NULL"),
        ("decisions", "SELECT count(*) FROM decisions WHERE bucket=%s"),
        ("active_best_practices", "SELECT count(*) FROM best_practices WHERE active = true"),
        ("active_skills", "SELECT count(*) FROM tools_catalog WHERE kind='skill' AND %s = ANY(applicable_buckets) AND archived_at IS NULL AND deprecated=false"),
        ("active_tools", "SELECT count(*) FROM tools_catalog WHERE kind='tool' AND %s = ANY(applicable_buckets) AND archived_at IS NULL AND deprecated=false"),
    )
    for key, sql in queries:
        if key == "active_best_practices":
            await cur.execute(sql)  # bucket-agnostic — best_practices has no bucket column today
        else:
            await cur.execute(sql, (bucket,))
        row = await cur.fetchone()
        out[key] = int(row[0]) if row else 0
    return out


async def _bucket_projects(cur: Any, bucket: str) -> list[dict[str, Any]]:
    await cur.execute(
        """
        SELECT slug, name, status, description, created_at
        FROM   projects
        WHERE  bucket = %s AND archived_at IS NULL
        ORDER  BY status DESC, created_at DESC
        LIMIT  50
        """,
        (bucket,),
    )
    out: list[dict[str, Any]] = []
    for r in await cur.fetchall():
        out.append(
            {
                "slug": r[0],
                "name": r[1],
                "status": r[2],
                "description": r[3] or "",
                "created_at": r[4].isoformat() if r[4] else "",
            }
        )
    return out
