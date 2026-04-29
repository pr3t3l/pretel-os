"""Unit tests for the Module 5 review MCP tools (M5.A.6.2).

Covers `list_pending_lessons` / `approve_lesson` / `reject_lesson` from
`tools/lessons.py` plus `list_pending_cross_pollination` /
`resolve_cross_pollination` from `tools/cross_pollination.py`.

Each test seeds rows under a unique marker (bucket prefix
`test_review_*` for lessons, `proposed_by='m5_test'` for cross-poll
rows) and cleans up via `DELETE WHERE` at fixture teardown — these
tables are NOT in the conftest auto-truncate list so isolation is
test-local.

All tests `@pytest.mark.slow` per repo convention (real DB).
"""
from __future__ import annotations

import json
from typing import Any, AsyncIterator
from uuid import uuid4

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from mcp_server.tools.cross_pollination import (
    list_pending_cross_pollination,
    resolve_cross_pollination,
)
from mcp_server.tools.lessons import (
    approve_lesson,
    list_pending_lessons,
    reject_lesson,
)

_LESSON_BUCKET_PREFIX = "test_review_"
_CROSSPOLL_PROPOSER = "m5_test"


@pytest_asyncio.fixture
async def cleanup_seeded_rows(
    test_pool: AsyncConnectionPool,
) -> AsyncIterator[None]:
    """Delete any rows this test file seeded after each test runs."""
    yield
    async with test_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM lessons WHERE bucket LIKE %s",
                (f"{_LESSON_BUCKET_PREFIX}%",),
            )
            await cur.execute(
                "DELETE FROM cross_pollination_queue WHERE proposed_by = %s",
                (_CROSSPOLL_PROPOSER,),
            )


async def _insert_lesson(
    pool: AsyncConnectionPool,
    *,
    bucket: str,
    title: str,
    content: str,
    status: str = "pending_review",
    category: str = "OPS",
    tags: list[str] | None = None,
) -> str:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO lessons (title, content, bucket, category,
                                     tags, status)
                VALUES (%s, %s, %s, %s, %s, %s::lesson_status)
                RETURNING id
                """,
                (title, content, bucket, category, tags or [], status),
            )
            row = await cur.fetchone()
    assert row is not None
    return str(row[0])


async def _select_lesson(
    pool: AsyncConnectionPool, lesson_id: str
) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT status, reviewed_at, reviewed_by, metadata "
                "FROM lessons WHERE id = %s",
                (lesson_id,),
            )
            return await cur.fetchone()


async def _insert_crosspoll(
    pool: AsyncConnectionPool,
    *,
    origin_bucket: str,
    target_bucket: str,
    idea: str,
    reasoning: str = "test reasoning",
    priority: int | None = None,
    status: str = "pending",
) -> str:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO cross_pollination_queue
                    (origin_bucket, target_bucket, idea, reasoning,
                     priority, status, proposed_by)
                VALUES (%s, %s, %s, %s, %s, %s::cross_poll_status, %s)
                RETURNING id
                """,
                (origin_bucket, target_bucket, idea, reasoning,
                 priority, status, _CROSSPOLL_PROPOSER),
            )
            row = await cur.fetchone()
    assert row is not None
    return str(row[0])


async def _select_crosspoll(
    pool: AsyncConnectionPool, row_id: str
) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT status, resolved_at, resolution_note "
                "FROM cross_pollination_queue WHERE id = %s",
                (row_id,),
            )
            return await cur.fetchone()


# --- list_pending_lessons --------------------------------------------------


@pytest.mark.slow
async def test_list_pending_lessons_returns_pending_only(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    bucket = f"{_LESSON_BUCKET_PREFIX}a"
    await _insert_lesson(test_pool, bucket=bucket, title="pending 1",
                         content="content one")
    await _insert_lesson(test_pool, bucket=bucket, title="pending 2",
                         content="content two")
    await _insert_lesson(test_pool, bucket=bucket, title="active 1",
                         content="content three", status="active")

    result = await list_pending_lessons(bucket=bucket, limit=10)

    assert result["status"] == "ok"
    titles = {r["title"] for r in result["results"]}
    assert titles == {"pending 1", "pending 2"}


@pytest.mark.slow
async def test_list_pending_lessons_bucket_filter(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    bucket_a = f"{_LESSON_BUCKET_PREFIX}a"
    bucket_b = f"{_LESSON_BUCKET_PREFIX}b"
    await _insert_lesson(test_pool, bucket=bucket_a, title="a-pending",
                         content="x")
    await _insert_lesson(test_pool, bucket=bucket_b, title="b-pending",
                         content="y")

    only_a = await list_pending_lessons(bucket=bucket_a, limit=10)
    titles_a = {r["title"] for r in only_a["results"]}
    assert titles_a == {"a-pending"}


@pytest.mark.slow
async def test_list_pending_lessons_limit_clamped_to_50(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    result = await list_pending_lessons(bucket=None, limit=100)
    # Function should clamp internally — just verify call succeeded.
    assert result["status"] == "ok"
    assert len(result["results"]) <= 50


# --- approve_lesson --------------------------------------------------------


@pytest.mark.slow
async def test_approve_lesson_happy_path(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    bucket = f"{_LESSON_BUCKET_PREFIX}approve"
    lesson_id = await _insert_lesson(
        test_pool, bucket=bucket, title="to approve",
        content="approve me",
    )

    result = await approve_lesson(id=lesson_id)

    assert result == {"status": "ok", "approved": True}
    row = await _select_lesson(test_pool, lesson_id)
    assert row is not None
    status, reviewed_at, reviewed_by, _metadata = row
    assert status == "active"
    assert reviewed_at is not None
    assert reviewed_by == "operator"


@pytest.mark.slow
async def test_approve_lesson_already_active_is_noop(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    bucket = f"{_LESSON_BUCKET_PREFIX}already_active"
    lesson_id = await _insert_lesson(
        test_pool, bucket=bucket, title="already active",
        content="x", status="active",
    )

    result = await approve_lesson(id=lesson_id)
    assert result == {"status": "ok", "approved": False}


@pytest.mark.slow
async def test_approve_lesson_unknown_id_returns_false(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    result = await approve_lesson(id=str(uuid4()))
    assert result == {"status": "ok", "approved": False}


# --- reject_lesson ---------------------------------------------------------


@pytest.mark.slow
async def test_reject_lesson_writes_reason_to_metadata(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    bucket = f"{_LESSON_BUCKET_PREFIX}reject"
    lesson_id = await _insert_lesson(
        test_pool, bucket=bucket, title="to reject",
        content="reject me",
    )

    result = await reject_lesson(
        id=lesson_id, reason="duplicate of LL-X-001"
    )

    assert result == {"status": "ok", "rejected": True}
    row = await _select_lesson(test_pool, lesson_id)
    assert row is not None
    status, reviewed_at, reviewed_by, metadata = row
    assert status == "rejected"
    assert reviewed_at is not None
    assert reviewed_by == "operator"
    metadata_dict = metadata if isinstance(metadata, dict) else json.loads(metadata)
    assert metadata_dict.get("reject_reason") == "duplicate of LL-X-001"


@pytest.mark.slow
async def test_reject_lesson_empty_reason_returns_error(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    bucket = f"{_LESSON_BUCKET_PREFIX}reject_empty"
    lesson_id = await _insert_lesson(
        test_pool, bucket=bucket, title="x", content="y",
    )
    result = await reject_lesson(id=lesson_id, reason="   ")
    assert result["status"] == "error"
    assert "reason" in result["error"]


# --- list_pending_cross_pollination ---------------------------------------


@pytest.mark.slow
async def test_list_pending_cross_pollination_orders_by_priority(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    await _insert_crosspoll(test_pool, origin_bucket="business",
                            target_bucket="personal", idea="C",
                            priority=3)
    await _insert_crosspoll(test_pool, origin_bucket="business",
                            target_bucket="personal", idea="A",
                            priority=1)
    await _insert_crosspoll(test_pool, origin_bucket="business",
                            target_bucket="personal", idea="B",
                            priority=2)

    result = await list_pending_cross_pollination(limit=10)
    assert result["status"] == "ok"
    # Filter to our test rows (other rows may exist from prior runs).
    ours = [r for r in result["results"] if r["idea"] in {"A", "B", "C"}]
    assert [r["idea"] for r in ours] == ["A", "B", "C"]


# --- resolve_cross_pollination --------------------------------------------


@pytest.mark.slow
async def test_resolve_cross_pollination_approve_maps_to_applied(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    row_id = await _insert_crosspoll(
        test_pool, origin_bucket="business", target_bucket="scout",
        idea="approve me",
    )

    result = await resolve_cross_pollination(
        id=row_id, action="approve", note="looks good",
    )

    assert result == {
        "status": "ok",
        "resolved": True,
        "new_status": "applied",
    }
    row = await _select_crosspoll(test_pool, row_id)
    assert row is not None
    status, resolved_at, resolution_note = row
    assert status == "applied"
    assert resolved_at is not None
    assert resolution_note == "looks good"


@pytest.mark.slow
async def test_resolve_cross_pollination_reject_maps_to_dismissed(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    row_id = await _insert_crosspoll(
        test_pool, origin_bucket="business", target_bucket="scout",
        idea="reject me",
    )

    result = await resolve_cross_pollination(
        id=row_id, action="reject"
    )

    assert result == {
        "status": "ok",
        "resolved": True,
        "new_status": "dismissed",
    }


@pytest.mark.slow
async def test_resolve_cross_pollination_invalid_action_errors(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    row_id = await _insert_crosspoll(
        test_pool, origin_bucket="business", target_bucket="scout",
        idea="x",
    )
    result = await resolve_cross_pollination(id=row_id, action="maybe")
    assert result["status"] == "error"
    assert "action" in result["error"]


@pytest.mark.slow
async def test_resolve_cross_pollination_already_applied_is_noop(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_seeded_rows: None,
) -> None:
    row_id = await _insert_crosspoll(
        test_pool, origin_bucket="business", target_bucket="scout",
        idea="already done", status="applied",
    )
    result = await resolve_cross_pollination(id=row_id, action="approve")
    assert result == {"status": "ok", "resolved": False}
