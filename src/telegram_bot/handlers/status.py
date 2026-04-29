"""/status — health summary across MCP + DB + LiteLLM + n8n (M5.B.6.1).

Four checks run concurrently via `asyncio.gather`. Each returns a
`Check` dataclass (healthy bool + per-check detail + latency_ms).
The reply is color-coded: 🟢 all healthy, 🟡 partial, 🔴 all down,
with a per-row status line per integration.

Endpoint URLs are env-overridable so the same code works against
production (mcp.alfredopretelvargas.com) and local Tailscale loopback
without code changes.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass

import httpx
import psycopg
from telegram import Update
from telegram.ext import ContextTypes

from .. import config as config_mod
from ._guard import operator_only

log = logging.getLogger(__name__)

_TIMEOUT_S = 5.0

_MCP_HEALTH_URL = os.environ.get(
    "MCP_HEALTH_URL", "https://mcp.alfredopretelvargas.com/health"
)
_LITELLM_HEALTH_URL = os.environ.get(
    "LITELLM_HEALTH_URL", "http://127.0.0.1:4000/health"
)
_N8N_HEALTH_URL = os.environ.get(
    "N8N_HEALTH_URL", "http://127.0.0.1:5678/healthz"
)


@dataclass(frozen=True)
class Check:
    name: str
    healthy: bool
    detail: str
    latency_ms: int


async def _http_check(name: str, url: str) -> Check:
    """GET `url` with `_TIMEOUT_S`. 2xx = healthy."""
    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
            response = await client.get(url)
        latency_ms = int((time.monotonic() - t0) * 1000)
        if 200 <= response.status_code < 300:
            return Check(
                name=name,
                healthy=True,
                detail=f"HTTP {response.status_code}",
                latency_ms=latency_ms,
            )
        return Check(
            name=name,
            healthy=False,
            detail=f"HTTP {response.status_code}",
            latency_ms=latency_ms,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - t0) * 1000)
        return Check(
            name=name,
            healthy=False,
            detail=type(exc).__name__,
            latency_ms=latency_ms,
        )


async def _db_check(database_url: str) -> Check:
    """Run `SELECT 1` against `database_url` via a sync psycopg conn
    wrapped in `asyncio.to_thread`. Conn timeout = `_TIMEOUT_S`.
    """
    t0 = time.monotonic()

    def _probe() -> bool:
        with psycopg.connect(
            database_url, connect_timeout=int(_TIMEOUT_S)
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()
                return row is not None and row[0] == 1

    try:
        ok = await asyncio.to_thread(_probe)
        latency_ms = int((time.monotonic() - t0) * 1000)
        return Check(
            name="postgres",
            healthy=ok,
            detail="SELECT 1 OK" if ok else "SELECT 1 returned unexpected row",
            latency_ms=latency_ms,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - t0) * 1000)
        return Check(
            name="postgres",
            healthy=False,
            detail=type(exc).__name__,
            latency_ms=latency_ms,
        )


def _format_status(checks: list[Check]) -> str:
    """Format the 4-check result list into a Telegram-friendly reply."""
    healthy_count = sum(1 for c in checks if c.healthy)
    if healthy_count == len(checks):
        header = "🟢 All systems healthy"
    elif healthy_count == 0:
        header = "🔴 All systems down"
    else:
        header = "🟡 Partial availability"

    lines = [header, ""]
    for check in checks:
        marker = "🟢" if check.healthy else "🔴"
        lines.append(
            f"{marker} {check.name}: {check.detail} ({check.latency_ms}ms)"
        )
    return "\n".join(lines)


@operator_only
async def status_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """`/status` — parallel health checks across the 4 integrations."""
    if update.message is None:
        return
    cfg = config_mod.load_config()
    checks_tuple = await asyncio.gather(
        _http_check("mcp_server", _MCP_HEALTH_URL),
        _db_check(cfg.database_url),
        _http_check("litellm", _LITELLM_HEALTH_URL),
        _http_check("n8n", _N8N_HEALTH_URL),
    )
    await update.message.reply_text(_format_status(list(checks_tuple)))
