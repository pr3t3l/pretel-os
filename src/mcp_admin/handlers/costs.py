"""Costs dashboard — `v_daily_cost_by_purpose` last N days + diagnostic.

Each query block runs on its own connection so a failure in one (e.g. a
partitioned table with no partition for the lookback range, a missing view,
a permission issue) does not poison the rest of the page.
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

    rows, total_cost, total_calls, by_purpose, by_day, active_days, costs_err = (
        await _fetch_costs(pool, days)
    )
    first_call_at, total_llm_calls_ever, llm_ever_err = await _fetch_llm_ever(pool)
    usage_by_tool, usage_err = await _fetch_usage_by_tool(pool, days)
    (
        routing_total,
        routing_degraded,
        routing_last_at,
        routing_by_client,
        routing_err,
    ) = await _fetch_routing(pool, days)

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
            "errors": {
                "costs": costs_err,
                "llm_ever": llm_ever_err,
                "usage": usage_err,
                "routing": routing_err,
            },
        },
    )


# ---------------------------------------------------------------------- helpers


async def _fetch_costs(
    pool: Any, days: int
) -> tuple[list[dict[str, Any]], float, int, dict[str, float], dict[str, float], int, str | None]:
    rows: list[dict[str, Any]] = []
    total_cost = 0.0
    total_calls = 0
    by_purpose: dict[str, float] = defaultdict(float)
    by_day: dict[str, float] = defaultdict(float)
    try:
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
        return rows, total_cost, total_calls, by_purpose, by_day, len(by_day), None
    except Exception as exc:
        log.warning("costs query failed: %s", exc)
        return [], 0.0, 0, {}, {}, 0, str(exc)


async def _fetch_llm_ever(pool: Any) -> tuple[str | None, int, str | None]:
    try:
        async with pool.connection(timeout=5.0) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT min(created_at)::date::text, count(*) FROM llm_calls"
                )
                r = await cur.fetchone()
                if r:
                    return r[0], int(r[1] or 0), None
    except Exception as exc:
        log.warning("llm_calls ever query failed: %s", exc)
        return None, 0, str(exc)
    return None, 0, None


async def _fetch_usage_by_tool(
    pool: Any, days: int
) -> tuple[list[dict[str, Any]], str | None]:
    out: list[dict[str, Any]] = []
    try:
        async with pool.connection(timeout=5.0) as conn:
            async with conn.cursor() as cur:
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
                for r in await cur.fetchall():
                    out.append(
                        {
                            "tool_name": r[0],
                            "invoked_by": r[1],
                            "calls": int(r[2] or 0),
                            "last_at": r[3].isoformat()[:19].replace("T", " ")
                            if r[3]
                            else "",
                        }
                    )
        return out, None
    except Exception as exc:
        log.warning("usage_logs query failed: %s", exc)
        return [], str(exc)


async def _fetch_routing(
    pool: Any, days: int
) -> tuple[int, int, str | None, list[dict[str, Any]], str | None]:
    total = 0
    degraded = 0
    last_at: str | None = None
    by_client: list[dict[str, Any]] = []
    try:
        async with pool.connection(timeout=5.0) as conn:
            async with conn.cursor() as cur:
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
                if r:
                    total = int(r[0] or 0)
                    degraded = int(r[1] or 0)
                    last_at = (
                        r[2].isoformat()[:19].replace("T", " ") if r[2] else None
                    )

                await cur.execute(
                    f"""
                    SELECT client_origin, count(*) AS n,
                           count(*) FILTER (WHERE degraded_mode) AS d
                    FROM   routing_logs
                    WHERE  created_at > now() - interval '{days} days'
                    GROUP  BY client_origin
                    ORDER  BY n DESC
                    """
                )
                for r in await cur.fetchall():
                    by_client.append(
                        {
                            "client_origin": r[0],
                            "calls": int(r[1] or 0),
                            "degraded": int(r[2] or 0),
                        }
                    )
        return total, degraded, last_at, by_client, None
    except Exception as exc:
        log.warning("routing_logs query failed: %s", exc)
        return 0, 0, None, [], str(exc)
