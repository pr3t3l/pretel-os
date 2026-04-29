"""Cross-pollination queue review tools (Module 5 Phase A.5).

Two MCP tools that surface and resolve `cross_pollination_queue` rows.
Used by Module 5 (`/cross_poll_review`) and Claude.ai review surfaces.

Action mapping (per `specs/telegram_bot/spec.md` §3.2):
    `'approve'` → `cross_poll_status='applied'`
    `'reject'`  → `cross_poll_status='dismissed'`

`under_review` is reserved for Reflection-worker hand-offs and is
never written by these tools.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from .. import db as db_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)

_VALID_ACTIONS = {"approve": "applied", "reject": "dismissed"}


async def list_pending_cross_pollination(limit: int = 10) -> dict[str, Any]:
    """List `cross_pollination_queue` rows awaiting operator review.

    Ordered by `priority ASC NULLS LAST, created_at ASC` so highest-
    priority unreviewed proposals surface first; rows without an
    explicit priority sort at the bottom.

    Args:
        limit: clamped to [1, 50]; default 10.

    Returns:
        `{status:'ok', results:[{id, origin_bucket, origin_project,
        target_bucket, idea, reasoning, suggested_application, priority,
        confidence_score, impact_score, created_at}, ...]}`. Returns
        degraded payload when DB is unavailable.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="list_pending_cross_pollination",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", results=[])

        limit_val = max(1, min(int(limit), 50))

        sql = """
            SELECT id, origin_bucket, origin_project, target_bucket,
                   idea, reasoning, suggested_application,
                   priority, confidence_score, impact_score, created_at
            FROM   cross_pollination_queue
            WHERE  status = 'pending'
            ORDER BY COALESCE(priority, 99) ASC, created_at ASC
            LIMIT  %s
        """

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, (limit_val,))
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("list_pending_cross_pollination failed")
            await log_usage(
                tool_name="list_pending_cross_pollination",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc), "results": []}

        results = [
            {
                "id": str(r[0]),
                "origin_bucket": r[1],
                "origin_project": r[2],
                "target_bucket": r[3],
                "idea": r[4],
                "reasoning": r[5],
                "suggested_application": r[6],
                "priority": int(r[7]) if r[7] is not None else None,
                "confidence_score": float(r[8]) if r[8] is not None else None,
                "impact_score": float(r[9]) if r[9] is not None else None,
                "created_at": r[10].isoformat() if r[10] is not None else None,
            }
            for r in rows
        ]

    await log_usage(
        tool_name="list_pending_cross_pollination",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}


async def resolve_cross_pollination(
    id: str,
    action: str,
    note: Optional[str] = None,
) -> dict[str, Any]:
    """Resolve a pending cross-pollination row.

    `action='approve'` writes `status='applied'`; `action='reject'`
    writes `status='dismissed'`. UPDATE only fires when the row is
    currently `pending` or `under_review` — already-resolved rows
    return `{resolved: False}` without modification.

    Args:
        id: UUID string of the queue row.
        action: `'approve'` or `'reject'`.
        note: optional resolution note (lands in
            `cross_pollination_queue.resolution_note`).

    Returns:
        `{status:'ok', resolved: True, new_status: 'applied'|'dismissed'}`
        on successful flip; `{status:'ok', resolved: False}` when no
        row matched; degraded payload when DB is down;
        `{status:'error', error: ...}` on invalid input.
    """
    if not isinstance(id, str) or not id.strip():
        return {"status": "error", "error": "id must be a non-empty string"}
    if action not in _VALID_ACTIONS:
        return {
            "status": "error",
            "error": f"action must be one of {sorted(_VALID_ACTIONS)}, got {action!r}",
        }
    new_status = _VALID_ACTIONS[action]

    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="resolve_cross_pollination",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={
                    "id": id,
                    "action": action,
                    "degraded_reason": "db_unavailable",
                },
            )
            return degraded("db_unavailable")

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        UPDATE cross_pollination_queue
                        SET    status = %s::cross_poll_status,
                               resolved_at = now(),
                               reviewed_at = COALESCE(reviewed_at, now()),
                               resolution_note = %s
                        WHERE  id = %s
                          AND  status IN ('pending', 'under_review')
                        RETURNING id
                        """,
                        (new_status, note, id),
                    )
                    resolved = (await cur.fetchone()) is not None
        except Exception as exc:
            log.exception("resolve_cross_pollination failed")
            await log_usage(
                tool_name="resolve_cross_pollination",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"id": id, "action": action, "error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="resolve_cross_pollination",
        bucket=None,
        project=None,
        invoked_by="client",
        success=resolved,
        duration_ms=t.ms,
        metadata={"id": id, "action": action, "resolved": resolved},
    )
    if resolved:
        return {"status": "ok", "resolved": True, "new_status": new_status}
    return {"status": "ok", "resolved": False}
