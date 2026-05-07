"""Generic table row drill-down — `GET /db/{table}/{id}`.

Inspects information_schema for the table's columns, fetches the row,
formats every column value as a string. No mutations from this view.

Allowlist of tables we'll show — anything outside the list returns 404
to prevent /db/pg_catalog.pg_user/... shenanigans.
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

# Tables an operator can drill into. Keep this conservative.
ALLOWED_TABLES = frozenset(
    {
        "lessons",
        "decisions",
        "best_practices",
        "tools_catalog",
        "projects",
        "tasks",
        "operator_preferences",
        "dream_engine_runs",
        "cross_pollination_queue",
        "patterns",
        "gotchas",
        "ideas",
        "contacts",
        "conversations_indexed",
        "projects_indexed",
        "routing_logs",
    }
)


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/db/{table}/{row_id}", response_class=HTMLResponse)
async def db_row_view(request: Request, table: str, row_id: str) -> HTMLResponse:
    if table not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail=f"table {table!r} not browsable")

    pool = db_mod.get_pool()
    columns: list[dict[str, str]] = []
    row: dict[str, str] | None = None
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM   information_schema.columns
                WHERE  table_schema='public' AND table_name=%s
                ORDER  BY ordinal_position
                """,
                (table,),
            )
            for r in await cur.fetchall():
                columns.append({"name": r[0], "type": r[1], "nullable": r[2]})

            if not columns:
                raise HTTPException(status_code=404, detail=f"table {table!r} not found")

            col_names = ", ".join(f'"{c["name"]}"' for c in columns)
            try:
                await cur.execute(
                    f'SELECT {col_names} FROM "{table}" WHERE id = %s LIMIT 1',
                    (row_id,),
                )
                fetched = await cur.fetchone()
            except Exception as exc:
                log.warning("row fetch failed for %s/%s: %s", table, row_id, exc)
                fetched = None

    if fetched is not None:
        row = {c["name"]: _format_value(v) for c, v in zip(columns, fetched)}

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="db_row.html",
        context={
            "active_view": "memory",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "table": table,
            "row_id": row_id,
            "columns": columns,
            "row": row,
        },
    )


def _format_value(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, indent=2, ensure_ascii=False, default=str)
    return str(v)
