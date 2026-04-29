"""Unit tests for `mcp_server.tools.tasks`.

Seven tests covering CRUD, self-FK (blocked_by), priority ordering,
partial update + reject-empty, completion_note merge, and reopen
metadata.reopened_history accumulation.

Each test asserts at least one DB-side fact via SELECT to catch
schema/payload contract drift (LL-M4-PHASE-A-001).
"""
from __future__ import annotations

from typing import Any

from psycopg_pool import AsyncConnectionPool

from mcp_server.tools.tasks import (
    task_close,
    task_create,
    task_list,
    task_reopen,
    task_update,
)


async def _select_one(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...]) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()


async def test_task_create_default_status_open(patched_db: None, test_pool: AsyncConnectionPool) -> None:
    r = await task_create(
        title="ship M0.X Phase D",
        bucket="business",
        source="operator",
        priority="high",
        module="M0.X",
        trigger_phase="Phase D",
    )

    assert r["status"] == "ok"
    assert r["status_value"] == "open"
    assert isinstance(r["id"], str)

    row = await _select_one(
        test_pool,
        "SELECT title, bucket, source, priority, module, trigger_phase, status, blocked_by FROM tasks WHERE id = %s",
        (r["id"],),
    )
    assert row == ("ship M0.X Phase D", "business", "operator", "high", "M0.X", "Phase D", "open", None)


async def test_task_create_with_blocked_by_sets_status_blocked(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    parent = await task_create(title="parent", bucket="business", source="operator")
    child = await task_create(
        title="child",
        bucket="business",
        source="operator",
        blocked_by=parent["id"],
    )

    assert child["status_value"] == "blocked"

    row = await _select_one(
        test_pool, "SELECT status, blocked_by FROM tasks WHERE id = %s", (child["id"],)
    )
    assert row is not None
    assert row[0] == "blocked"
    assert str(row[1]) == parent["id"]


async def test_task_list_orders_by_priority_then_created_at(patched_db: None) -> None:
    """4 tasks with 4 different priorities — list returns them in
    urgent → high → normal → low order regardless of insert order."""
    await task_create(title="a-low", bucket="business", source="operator", priority="low")
    await task_create(title="b-urgent", bucket="business", source="operator", priority="urgent")
    await task_create(title="c-normal", bucket="business", source="operator", priority="normal")
    await task_create(title="d-high", bucket="business", source="operator", priority="high")

    r = await task_list(bucket="business")
    titles = [row["title"] for row in r["results"]]
    assert titles == ["b-urgent", "d-high", "c-normal", "a-low"]


async def test_task_update_partial_only_changes_specified(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    created = await task_create(
        title="X", bucket="business", source="operator", priority="normal", description="original",
    )
    updated = await task_update(id=created["id"], priority="high")

    assert updated["status"] == "ok"
    assert updated["found"] is True

    row = await _select_one(
        test_pool,
        "SELECT title, priority, description, updated_at > created_at FROM tasks WHERE id = %s",
        (created["id"],),
    )
    assert row == ("X", "high", "original", True)


async def test_task_update_rejects_empty_payload(patched_db: None) -> None:
    created = await task_create(title="x", bucket="business", source="operator")
    r = await task_update(id=created["id"])  # no fields supplied

    assert r["status"] == "error"
    assert "no fields to update" in r["error"]


async def test_task_close_sets_done_at_and_completion_note(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    created = await task_create(title="x", bucket="business", source="operator")
    closed = await task_close(id=created["id"], completion_note="shipped clean")

    assert closed["status"] == "ok"
    assert closed["found"] is True

    row = await _select_one(
        test_pool,
        "SELECT status, done_at IS NOT NULL, metadata->>'completion_note' FROM tasks WHERE id = %s",
        (created["id"],),
    )
    assert row == ("done", True, "shipped clean")


async def test_task_reopen_appends_history_and_clears_done_at(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    created = await task_create(title="flaky", bucket="business", source="operator")
    await task_close(id=created["id"], completion_note="thought it shipped")
    await task_reopen(id=created["id"], reason="regression caught in eval")

    row = await _select_one(
        test_pool,
        "SELECT status, done_at, jsonb_array_length(metadata->'reopened_history') FROM tasks WHERE id = %s",
        (created["id"],),
    )
    assert row == ("open", None, 1)

    # Reopening twice accumulates entries
    await task_close(id=created["id"])
    await task_reopen(id=created["id"], reason="second regression")

    row2 = await _select_one(
        test_pool,
        "SELECT jsonb_array_length(metadata->'reopened_history'), metadata->'reopened_history'->1->>'reason' FROM tasks WHERE id = %s",
        (created["id"],),
    )
    assert row2 == (2, "second regression")


async def test_task_create_check_violation_returns_error(patched_db: None) -> None:
    """An invalid priority triggers a CHECK violation; tool returns
    {status:'error', error:...} via the except path."""
    r = await task_create(
        title="x", bucket="business", source="operator", priority="invalid_priority",
    )
    assert r["status"] == "error"
    assert "tasks_priority_check" in r["error"] or "check" in r["error"].lower()


async def test_task_update_check_violation_returns_error(patched_db: None) -> None:
    """An invalid status triggers a CHECK violation in UPDATE."""
    created = await task_create(title="x", bucket="business", source="operator")
    r = await task_update(id=created["id"], status="not_a_real_status")
    assert r["status"] == "error"
    assert "tasks_status_check" in r["error"] or "check" in r["error"].lower()


async def test_tasks_degraded_mode_writes_journal(
    patched_db: None, db_unhealthy: None, journal_dir: Any
) -> None:
    """Each mutation (create/update/close/reopen) returns degraded with
    journal_id when DB is down. task_list (read) returns degraded with
    no journal_id."""
    create_r = await task_create(title="x", bucket="business", source="operator")
    assert create_r["status"] == "degraded"
    assert "journal_id" in create_r

    update_r = await task_update(id="00000000-0000-0000-0000-000000000000", title="x")
    assert update_r["status"] == "degraded"
    assert "journal_id" in update_r

    close_r = await task_close(id="00000000-0000-0000-0000-000000000000")
    assert close_r["status"] == "degraded"
    assert "journal_id" in close_r

    reopen_r = await task_reopen(id="00000000-0000-0000-0000-000000000000", reason="x")
    assert reopen_r["status"] == "degraded"
    assert "journal_id" in reopen_r

    list_r = await task_list()
    assert list_r["status"] == "degraded"
    assert list_r["results"] == []
    assert "journal_id" not in list_r

    files = list(journal_dir.glob("*.jsonl"))
    assert len(files) == 1
    contents = files[0].read_text()
    for op in ("task_create", "task_update", "task_close", "task_reopen"):
        assert op in contents
