"""Unit tests for `mcp_server.tools.router_feedback`.

Four tests covering record-pending, jsonb proposed_correction round-trip,
applied vs dismissed status (applied_at semantics).

Each test asserts at least one DB-side fact via SELECT to catch
schema/payload contract drift (LL-M4-PHASE-A-001).
"""
from __future__ import annotations

import json
from typing import Any

from psycopg_pool import AsyncConnectionPool

from mcp_server.tools.router_feedback import (
    router_feedback_record,
    router_feedback_review,
)


async def _select_one(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...]) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()


async def test_router_feedback_record_creates_pending(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    r = await router_feedback_record(
        feedback_type="missing_context",
        operator_note="Did not load relevant lesson",
    )

    assert r["status"] == "ok"
    assert r["status_value"] == "pending"
    assert isinstance(r["id"], str)

    row = await _select_one(
        test_pool,
        "SELECT feedback_type, status, operator_note, request_id, applied_at FROM router_feedback WHERE id = %s",
        (r["id"],),
    )
    assert row == ("missing_context", "pending", "Did not load relevant lesson", None, None)


async def test_router_feedback_record_with_proposed_correction_jsonb(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    """proposed_correction is dict → serialized to jsonb → round-trips back."""
    r = await router_feedback_record(
        feedback_type="wrong_bucket",
        request_id="req-abc-123",
        operator_note="should have been scout",
        proposed_correction={"bucket": "scout", "reason": "MTM context"},
    )

    row = await _select_one(
        test_pool,
        "SELECT request_id, proposed_correction FROM router_feedback WHERE id = %s",
        (r["id"],),
    )
    assert row is not None
    assert row[0] == "req-abc-123"
    # psycopg returns jsonb as Python dict
    correction = row[1] if isinstance(row[1], dict) else json.loads(row[1])
    assert correction == {"bucket": "scout", "reason": "MTM context"}


async def test_router_feedback_review_applied_sets_applied_at(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    record = await router_feedback_record(feedback_type="missing_context")
    review = await router_feedback_review(
        id=record["id"], status="applied", reviewed_by="operator"
    )

    assert review["status"] == "ok"
    assert review["status_value"] == "applied"

    row = await _select_one(
        test_pool,
        "SELECT status, reviewed_by, applied_at IS NOT NULL FROM router_feedback WHERE id = %s",
        (record["id"],),
    )
    assert row == ("applied", "operator", True)


async def test_router_feedback_review_dismissed_leaves_applied_at_null(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    """Only status='applied' sets applied_at. dismissed/reviewed leave it NULL."""
    record = await router_feedback_record(feedback_type="too_much_context")
    await router_feedback_review(id=record["id"], status="dismissed", reviewed_by="operator")

    row = await _select_one(
        test_pool,
        "SELECT status, reviewed_by, applied_at FROM router_feedback WHERE id = %s",
        (record["id"],),
    )
    assert row == ("dismissed", "operator", None)


async def test_router_feedback_review_rejects_invalid_status(patched_db: None) -> None:
    """status='pending' (transition into pending) and 'garbage' (not in enum) both rejected."""
    record = await router_feedback_record(feedback_type="missing_context")

    pending = await router_feedback_review(id=record["id"], status="pending", reviewed_by="x")
    assert pending["status"] == "error"
    assert "pending" in pending["error"]

    garbage = await router_feedback_review(id=record["id"], status="garbage", reviewed_by="x")
    assert garbage["status"] == "error"
    assert "invalid status" in garbage["error"]


async def test_router_feedback_degraded_mode_writes_journal(
    patched_db: None, db_unhealthy: None, journal_dir: Any
) -> None:
    """Both record + review return degraded with journal_id when DB down."""
    rec_r = await router_feedback_record(feedback_type="wrong_bucket")
    assert rec_r["status"] == "degraded"
    assert "journal_id" in rec_r

    rev_r = await router_feedback_review(
        id="00000000-0000-0000-0000-000000000000",
        status="reviewed",
        reviewed_by="operator",
    )
    assert rev_r["status"] == "degraded"
    assert "journal_id" in rev_r

    files = list(journal_dir.glob("*.jsonl"))
    assert len(files) == 1
    contents = files[0].read_text()
    assert "router_feedback_record" in contents
    assert "router_feedback_review" in contents
