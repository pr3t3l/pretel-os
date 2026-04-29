"""Router feedback tools — record + review.

Explicit feedback loop signals from operator to Router. Captures
"missing context", "wrong bucket", "wrong complexity", etc. Status
workflow: pending → reviewed | applied | dismissed.

`request_id` is `text` with NO foreign key (soft reference to
routing_logs.request_id). routing_logs is partitioned by created_at
which prevents a UNIQUE constraint, so referential integrity is
enforced at the MCP-tool layer rather than at the schema. See spec
§5.4 for the full rationale.

Schema: docs/DATA_MODEL.md §5.9 (table created in migration 0026).
Spec: specs/module-0x-knowledge-architecture/spec.md §5.4.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from .. import db as db_mod
from .. import journal as journal_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)


async def router_feedback_record(
    feedback_type: str,
    request_id: Optional[str] = None,
    operator_note: Optional[str] = None,
    proposed_correction: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Record router feedback. Inserts a row with status='pending'.

    `request_id` may be None (orphan feedback — operator can't always
    correlate to a specific routing_logs row). `proposed_correction` is
    free-form jsonb captured for the Phase D reviewer.

    Args:
        feedback_type: one of missing_context | wrong_bucket | wrong_complexity
            | irrelevant_lessons | too_much_context | low_quality_response.
        request_id: optional soft reference to routing_logs.request_id.
        operator_note: free-form text describing what went wrong.
        proposed_correction: optional jsonb payload describing the
            correction the operator suggests (e.g. correct bucket name).

    Returns:
        {status:'ok', id:uuid, status_value:'pending'} on success.
        {status:'degraded', journal_id:...} when DB is down.
        {status:'error', error:str} on DB failure.
    """
    payload: dict[str, Any] = {
        "feedback_type": feedback_type,
        "request_id": request_id,
        "operator_note": operator_note,
        "proposed_correction": proposed_correction,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("router_feedback_record", payload)
            await log_usage(
                tool_name="router_feedback_record",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        proposed_jsonb = json.dumps(proposed_correction) if proposed_correction else "{}"

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO router_feedback
                            (feedback_type, request_id, operator_note, proposed_correction)
                        VALUES (%s, %s, %s, %s::jsonb)
                        RETURNING id, status
                        """,
                        (feedback_type, request_id, operator_note, proposed_jsonb),
                    )
                    row = await cur.fetchone()
                    assert row is not None, "INSERT ... RETURNING produced no row"
                    fb_id = str(row[0])
                    status_value = str(row[1])
        except Exception as exc:
            log.exception("router_feedback_record failed")
            await log_usage(
                tool_name="router_feedback_record",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="router_feedback_record",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "action": "inserted",
            "feedback_type": feedback_type,
            "has_request_id": request_id is not None,
        },
    )
    return {"status": "ok", "id": fb_id, "status_value": status_value}


async def router_feedback_review(
    id: str,
    status: str,
    reviewed_by: str,
) -> dict[str, Any]:
    """Transition a pending feedback row OUT of pending.

    `status='applied'` additionally sets `applied_at=now()`. Other
    transition statuses leave `applied_at` NULL (the feedback was
    reviewed but no system change followed).

    Args:
        id: uuid of the feedback row.
        status: one of reviewed | applied | dismissed. `pending` is
            rejected — reviewing means transitioning OUT of pending.
        reviewed_by: identifier of the reviewer (e.g. 'operator').

    Returns:
        {status:'ok', id:uuid, found:True, status_value:str} on success.
        {status:'ok', found:False} when no row matches `id`.
        {status:'error', error:str} on invalid status or DB failure.
        {status:'degraded', journal_id:...} when DB is down.
    """
    if status == "pending":
        return {"status": "error", "error": "status='pending' is invalid for review (must transition OUT of pending)"}
    if status not in ("reviewed", "applied", "dismissed"):
        return {"status": "error", "error": f"invalid status: {status!r}"}

    payload: dict[str, Any] = {"id": id, "status": status, "reviewed_by": reviewed_by}

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("router_feedback_review", payload)
            await log_usage(
                tool_name="router_feedback_review",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        if status == "applied":
            sql = """
                UPDATE router_feedback
                SET status = %s,
                    reviewed_by = %s,
                    applied_at = now()
                WHERE id = %s
                RETURNING id, status
            """
        else:
            sql = """
                UPDATE router_feedback
                SET status = %s,
                    reviewed_by = %s
                WHERE id = %s
                RETURNING id, status
            """
        params: list[Any] = [status, reviewed_by, id]

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("router_feedback_review failed")
            await log_usage(
                tool_name="router_feedback_review",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc), "id": id},
            )
            return {"status": "error", "error": str(exc)}

    if row is None:
        await log_usage(
            tool_name="router_feedback_review",
            bucket=None,
            project=None,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"result": "not_found", "id": id},
        )
        return {"status": "ok", "found": False}

    fb_id = str(row[0])
    status_value = str(row[1])
    await log_usage(
        tool_name="router_feedback_review",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": "reviewed", "id": fb_id, "new_status": status_value},
    )
    return {"status": "ok", "id": fb_id, "status_value": status_value, "found": True}
