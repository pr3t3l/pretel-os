"""report_satisfaction — companion tool to get_context (Phase D.3.2).

Per `specs/router/spec.md §4.3`: takes a `request_id` returned by a
prior `get_context` call plus an integer score in [1, 5], and updates
`routing_logs.user_satisfaction` for that row. The signal feeds the
audit query in spec §9.3 (`per-model classification cost AND quality`)
which orders models by `avg(user_satisfaction)`.

Response shape is the spec §4.3 contract: `{"status": "ok"}` or
`{"status": "error", "reason": str}`. When the DB is unhealthy the
tool returns the existing repo's `degraded(...)` shape (Module 0X
convention) so operator-facing dashboards can distinguish "couldn't
write" from "wrote and rejected".
"""
from __future__ import annotations

import logging
from typing import Any

from .. import db as db_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)

_MIN_SCORE = 1
_MAX_SCORE = 5


async def report_satisfaction(
    request_id: str,
    score: int,
) -> dict[str, Any]:
    """Update `routing_logs.user_satisfaction` for `request_id`.

    Args:
        request_id: The `request_id` returned from a prior `get_context`.
        score: Integer in [1, 5] (clamped to smallint server-side).

    Returns:
        `{"status": "ok"}` when the row was updated.
        `{"status": "error", "reason": str}` when the input is invalid
        or the row does not exist.
        `degraded(...)` when the DB is unavailable.
    """
    if not isinstance(request_id, str) or not request_id.strip():
        return {"status": "error", "reason": "request_id must be a non-empty string"}
    if not isinstance(score, int) or isinstance(score, bool):
        return {"status": "error", "reason": "score must be an integer"}
    if not (_MIN_SCORE <= score <= _MAX_SCORE):
        return {"status": "error", "reason": f"score must be in [{_MIN_SCORE}, {_MAX_SCORE}]"}

    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="report_satisfaction",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"request_id": request_id, "degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable")

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        UPDATE routing_logs
                        SET user_satisfaction = %s
                        WHERE request_id = %s
                        """,
                        (score, request_id),
                    )
                    rowcount = cur.rowcount
        except Exception as exc:
            log.exception("report_satisfaction failed")
            await log_usage(
                tool_name="report_satisfaction",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"request_id": request_id, "error": str(exc)},
            )
            return {"status": "error", "reason": str(exc)}

    if rowcount == 0:
        await log_usage(
            tool_name="report_satisfaction",
            bucket=None,
            project=None,
            invoked_by="client",
            success=False,
            duration_ms=t.ms,
            metadata={"request_id": request_id, "error": "request_id not found"},
        )
        return {"status": "error", "reason": "request_id not found"}

    await log_usage(
        tool_name="report_satisfaction",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"request_id": request_id, "score": score},
    )
    return {"status": "ok"}
