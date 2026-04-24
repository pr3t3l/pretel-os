"""Shared helpers for MCP tools — degraded responses + usage_logs insert."""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

from .. import db as db_mod

log = logging.getLogger(__name__)


def degraded(reason: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "degraded",
        "degraded_reason": reason,
    }
    payload.update(extra)
    return payload


def vector_literal(values: list[float]) -> str:
    """Serialize a vector as the pgvector text literal `[v1,v2,...]`."""
    return "[" + ",".join(repr(float(v)) for v in values) + "]"


class Timer:
    def __enter__(self) -> "Timer":
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._t1 = time.perf_counter()

    @property
    def ms(self) -> int:
        end = getattr(self, "_t1", time.perf_counter())
        return int((end - self._t0) * 1000)


async def log_usage(
    *,
    tool_name: str,
    bucket: Optional[str],
    project: Optional[str],
    invoked_by: str,
    success: bool,
    duration_ms: int,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Insert one row into usage_logs. Swallows DB errors — best effort."""
    if not db_mod.is_healthy():
        return
    pool = db_mod.get_pool()
    try:
        async with pool.connection(timeout=2.0) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO usage_logs (tool_name, bucket, project, invoked_by, success, duration_ms, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    """,
                    (
                        tool_name,
                        bucket,
                        project,
                        invoked_by,
                        success,
                        duration_ms,
                        json.dumps(metadata or {}, default=str),
                    ),
                )
    except Exception as exc:
        log.debug("usage_logs insert failed: %s", exc)
