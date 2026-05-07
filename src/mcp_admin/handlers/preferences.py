"""Operator preferences view — first MVP view.

GET /preferences renders all rows of `operator_preferences` grouped by
category, with an inline form per row.

POST /preferences/{category}/{key} routes through the existing MCP tool
`mcp_server.tools.preferences.preference_set` — never writes SQL DML
directly. This preserves the CONSTITUTION §2.1 invariant that the MCP
server is the only write surface.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod
from mcp_server.tools.preferences import preference_set

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    """Late-bind templates from main.py app factory."""
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/preferences", response_class=HTMLResponse)
async def preferences_view(request: Request) -> HTMLResponse:
    """List all operator_preferences rows grouped by category."""
    pool = db_mod.get_pool()
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT category, key, value, scope, source,
                       active, updated_at, metadata->>'purpose' AS purpose
                FROM   operator_preferences
                ORDER  BY category, key
                """
            )
            rows = await cur.fetchall()

    grouped: dict[str, list[dict[str, Any]]] = {}
    for category, key, value, scope, source, active, updated_at, purpose in rows:
        grouped.setdefault(category, []).append(
            {
                "category": category,
                "key": key,
                "value": value,
                "scope": scope,
                "source": source,
                "active": active,
                "updated_at": updated_at,
                "purpose": purpose,
            }
        )

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="preferences.html",
        context={
            "active_view": "preferences",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "grouped": grouped,
            "total_count": sum(len(v) for v in grouped.values()),
        },
    )


@router.post("/preferences/{category}/{key}")
async def preference_set_view(
    request: Request,
    category: str,
    key: str,
    value: str = Form(...),
) -> RedirectResponse:
    """Update one preference via the MCP tool (NEVER direct SQL).

    Per CONSTITUTION §2.1, all mutations route through the MCP tool
    surface. This endpoint just unwraps the form and delegates.
    """
    user_email = getattr(request.state, "user_email", "anonymous")
    log.info(
        "preference_set request: user=%s category=%s key=%s value=%s",
        user_email, category, key, value,
    )
    result = await preference_set(
        category=category,
        key=key,
        value=value,
        scope="global",
        source="operator_explicit",
    )
    if result.get("status") != "ok":
        log.error("preference_set failed: %r", result)
    return RedirectResponse(url="/preferences", status_code=303)
