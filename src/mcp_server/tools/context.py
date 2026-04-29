"""get_context — MCP tool wrapper for the Router (Phase D.3.1).

Replaces the Module-3 L0-only stub. The wrapper's only job is the
async-to-sync bridge: open a sync `psycopg.Connection` for the Phase
B/D router stack via `asyncio.to_thread`, hand it to
`router.get_context()`, and close it on the way out.

The router orchestrator (`router.router.get_context`) owns:
- start_request / log_classification / log_layers / log_conflicts /
  log_rag / log_completion (telemetry, spec §9)
- classify or fallback (Phase A / D.0)
- assemble_bundle (Phase B)
- detect_invariant_violations (Phase C)
- recommend_tools (Q7)
- the try/finally that always fires log_completion (Q5)

Per spec §11 and Q5, this tool NEVER raises into the MCP transport.
Failures degrade to a coherent ContextBundle with `degraded_mode=True`
and a reason. If the sync DB connect itself fails, the wrapper builds
a minimal ContextBundle skeleton inline (no router stack invocation
because that requires a live connection for telemetry).

Open follow-ups (not blocking D.3):
- Wire LISTEN/NOTIFY listener via the MCP server lifespan hook
  (cache.py docstring describes the contract). The lazy-init below
  works without it; the cost is potentially-stale entries between
  process restarts. `max_entries=256` bounds blast radius.
- Plumb `client_origin` from the FastMCP transport context once the
  framework exposes it via a tool-arg `Context` injection. Today the
  wrapper hard-codes `'unknown'`.
- Replace the per-call `psycopg.connect` with a sync
  `psycopg_pool.ConnectionPool` if telemetry shows connection-open
  latency dominating the warm path.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any, Optional

import psycopg

from .. import config as config_mod
from .. import db as db_mod
from ..router.cache import LayerBundleCache
from ..router.router import get_context as router_get_context
from ._common import Timer, log_usage

log = logging.getLogger(__name__)

_CONNECT_TIMEOUT_S = 2.0

# Process-lifetime cache singleton. Lazy-initialized on first call.
_layer_cache: Optional[LayerBundleCache] = None


def _get_cache() -> LayerBundleCache:
    global _layer_cache
    if _layer_cache is None:
        _layer_cache = LayerBundleCache(max_entries=256)
    return _layer_cache


def _open_sync_conn(database_url: str) -> psycopg.Connection:
    """Open a fresh sync connection for the router stack.

    `autocommit=True` so each telemetry INSERT/UPDATE issued by
    `router.telemetry` is durable across crashes (Q2 INSERT-early
    strategy — partial rows must survive a mid-pipeline failure).
    """
    return psycopg.connect(
        database_url,
        autocommit=True,
        connect_timeout=int(_CONNECT_TIMEOUT_S),
    )


def _db_unreachable_skeleton(message: str, session_id: Optional[str]) -> dict[str, Any]:
    """Return a spec §4.2-shaped dict when the sync DB connect fails."""
    return {
        "request_id": str(uuid.uuid4()),
        "session_id": session_id,
        "classification": {
            "bucket": None,
            "project": None,
            "skill": None,
            "complexity": "LOW",
            "needs_lessons": False,
            "confidence": 0.0,
        },
        "classification_mode": "fallback_rules",
        "bundle": {
            "layers": [
                {"layer": layer, "loaded": False, "token_count": 0, "blocks": []}
                for layer in ("L0", "L1", "L2", "L3", "L4")
            ],
            "metadata": {
                "bucket": None,
                "project": None,
                "classifier_hash": "db_unreachable",
                "total_tokens": 0,
                "assembly_latency_ms": 0,
                "cache_hit": False,
                "over_budget_layers": [],
            },
        },
        "tools_recommended": [],
        "source_conflicts": [],
        "over_budget_layers": [],
        "degraded_mode": True,
        "degraded_reason": "db_unreachable",
        "latency_ms": 0,
    }


async def get_context(
    message: str,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    """Real Router entry point — replaces the Module-3 L0 stub.

    Args:
        message: The operator's raw turn text.
        session_id: Optional client-provided session id; threaded through
            telemetry so reflection / replay can correlate by session.

    Returns:
        ContextBundle dict matching `specs/router/spec.md §4.2`.
    """
    cfg = config_mod.load_config()
    repo_root = cfg.identity_path.parent
    cache = _get_cache()

    with Timer() as t:
        try:
            conn: psycopg.Connection = await asyncio.to_thread(
                _open_sync_conn, cfg.database_url
            )
        except (psycopg.Error, OSError) as exc:
            log.warning("router conn open failed: %s", exc)
            response = _db_unreachable_skeleton(message, session_id)
            await log_usage(
                tool_name="get_context",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={
                    "request_id": response["request_id"],
                    "session_id": session_id,
                    "degraded_reason": "db_unreachable",
                },
            )
            return response

        try:
            response = await router_get_context(
                conn=conn,
                message=message,
                session_id=session_id,
                client_origin="unknown",
                repo_root=repo_root,
                cache=cache,
            )
        finally:
            await asyncio.to_thread(conn.close)

    await log_usage(
        tool_name="get_context",
        bucket=(response.get("classification") or {}).get("bucket"),
        project=(response.get("classification") or {}).get("project"),
        invoked_by="client",
        success=not response.get("degraded_mode", False),
        duration_ms=t.ms,
        metadata={
            "request_id": response.get("request_id"),
            "session_id": session_id,
            "classification_mode": response.get("classification_mode"),
            "degraded_reason": response.get("degraded_reason"),
        },
    )
    return response
