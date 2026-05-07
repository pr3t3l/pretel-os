"""Costs dashboard — `v_daily_cost_by_purpose` last 30 days.

Numeric table V1 per phase_b_close §Q5. Charts are fase 2.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mcp_server import db as db_mod

log = logging.getLogger(__name__)

router = APIRouter()


def attach_templates(templates: Jinja2Templates) -> None:
    router.templates = templates  # type: ignore[attr-defined]


@router.get("/costs", response_class=HTMLResponse)
async def costs_view(request: Request) -> HTMLResponse:
    pool = db_mod.get_pool()
    rows: list[dict[str, Any]] = []
    total_cost = 0.0
    total_calls = 0
    by_purpose: dict[str, float] = defaultdict(float)
    by_day: dict[str, float] = defaultdict(float)

    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT day, purpose::text, model,
                       round(cost_usd::numeric, 6) AS cost_usd,
                       input_tokens, output_tokens, call_count
                FROM   v_daily_cost_by_purpose
                WHERE  day > current_date - interval '30 days'
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
        },
    )
