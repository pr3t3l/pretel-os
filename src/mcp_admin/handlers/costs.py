"""Costs dashboard — `v_daily_cost_by_purpose` last 30 days.

Numeric table V1 per phase_b_close §Q5. Charts are fase 2.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

log = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_WINDOWS = (7, 14, 30, 60)


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/costs", response_class=HTMLResponse)
async def costs_view(
    request: Request,
    days: int = Query(30, ge=1, le=60),
) -> HTMLResponse:
    if days not in ALLOWED_WINDOWS:
        days = 30
    pool = db_mod.get_pool()
    rows: list[dict[str, Any]] = []
    total_cost = 0.0
    total_calls = 0
    by_purpose: dict[str, float] = defaultdict(float)
    by_day: dict[str, float] = defaultdict(float)
    active_days = 0
    first_call_at: str | None = None
    total_llm_calls_ever = 0

    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT day, purpose::text, model,
                       round(cost_usd::numeric, 6) AS cost_usd,
                       input_tokens, output_tokens, call_count
                FROM   v_daily_cost_by_purpose
                WHERE  day > current_date - interval '{days} days'
                ORDER  BY day DESC, cost_usd DESC NULLS LAST
                """
            )
            for r in await cur.fetchall():
                cost = float(r[3]) if r[3] is not None else 0.0
                rows.append(
                    {
                        "day": r[0].isoformat() if r[0] else "",
                        "purpose": r[1],
                        "model": r[2],
                        "cost_usd": cost,
                        "input_tokens": int(r[4] or 0),
                        "output_tokens": int(r[5] or 0),
                        "call_count": int(r[6] or 0),
                    }
                )
                total_cost += cost
                total_calls += int(r[6] or 0)
                by_purpose[r[1]] += cost
                by_day[r[0].isoformat() if r[0] else ""] += cost
            active_days = len(by_day)

            await cur.execute(
                "SELECT min(created_at)::date::text, count(*) FROM llm_calls"
            )
            row = await cur.fetchone()
            if row:
                first_call_at = row[0]
                total_llm_calls_ever = int(row[1] or 0)

            await cur.execute(
                f"""
                SELECT tool_name, invoked_by, count(*) AS calls,
                       max(created_at) AS last_at
                FROM   usage_logs
                WHERE  created_at > now() - interval '{days} days'
                GROUP  BY tool_name, invoked_by
                ORDER  BY calls DESC
                LIMIT  20
                """
            )
            usage_by_tool: list[dict[str, Any]] = []
            for r in await cur.fetchall():
                usage_by_tool.append(
                    {
                        "tool_name": r[0],
                        "invoked_by": r[1],
                        "calls": int(r[2] or 0),
                        "last_at": r[3].isoformat()[:19].replace("T", " ") if r[3] else "",
                    }
                )

            await cur.execute(
                f"""
                SELECT count(*),
                       count(*) FILTER (WHERE degraded_mode),
                       max(created_at)
                FROM   routing_logs
                WHERE  created_at > now() - interval '{days} days'
                """
            )
            r = await cur.fetchone()
            routing_total = int(r[0] or 0) if r else 0
            routing_degraded = int(r[1] or 0) if r else 0
            routing_last_at = (
                r[2].isoformat()[:19].replace("T", " ") if r and r[2] else None
            )

            await cur.execute(
                f"""
                SELECT client_origin, count(*) AS n,
                       count(*) FILTER (WHERE degraded_mode) AS degraded
                FROM   routing_logs
                WHERE  created_at > now() - interval '{days} days'
                GROUP  BY client_origin
                ORDER  BY n DESC
                """
            )
            routing_by_client: list[dict[str, Any]] = []
            for r in await cur.fetchall():
                routing_by_client.append(
                    {
                        "client_origin": r[0],
                        "calls": int(r[1] or 0),
                        "degraded": int(r[2] or 0),
                    }
                )

    templates: Jinja2Templates = router.templates  # type: ignore[attr-defined]
    return templates.TemplateResponse(
        request=request,
        name="costs.html",
        context={
            "active_view": "costs",
            "user_email": getattr(request.state, "user_email", "anonymous"),
            "rows": rows,
            "total_cost": total_cost,
            "total_calls": total_calls,
            "by_purpose": sorted(by_purpose.items(), key=lambda x: -x[1]),
            "by_day": sorted(by_day.items(), reverse=True),
            "days": days,
            "allowed_windows": list(ALLOWED_WINDOWS),
            "active_days": active_days,
            "first_call_at": first_call_at,
            "total_llm_calls_ever": total_llm_calls_ever,
            "usage_by_tool": usage_by_tool,
            "routing_total": routing_total,
            "routing_degraded": routing_degraded,
            "routing_last_at": routing_last_at,
            "routing_by_client": routing_by_client,
        },
    )
