"""Integration tests for `auto_index.worker`.

The worker drains `pending_embeddings` by calling OpenAI and writing the
result back to the target row. These tests run against `pretel_os_test`,
mock `embeddings.embed()` (no live API), and verify the four invariants:

  1. _drain_once processes a pending row end-to-end (embed → UPDATE → DELETE).
  2. consume_embedding_queue wakes on pg_notify and drains promptly.
  3. embed() returning None bumps attempts + last_error; row stays pending.
  4. Rows with attempts >= MAX_ATTEMPTS are skipped (poison-row handling).

Cleanup: `_truncate_between_tests` (repo-root conftest) truncates
`pending_embeddings` automatically when `patched_db` is in fixturenames.
The target `decisions` table is NOT in that list, so each test deletes
its own seeded rows by tag.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from typing import Any, AsyncIterator, Callable, Optional

import psycopg
import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from auto_index import worker

pytestmark = pytest.mark.slow

_TEST_DSN = os.environ.get(
    "PRETEL_OS_TEST_DATABASE_URL",
    "postgresql://pretel_os@localhost/pretel_os_test",
)


# ---------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------

def _seed_decision_with_null_embedding(tag: str) -> str:
    """INSERT a decisions row with embedding=NULL.

    The notify_missing_embedding trigger fires automatically and inserts
    the matching pending_embeddings row + emits pg_notify. Returns the
    decision id as a string.
    """
    with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO decisions (
                    bucket, project, title, context, decision, consequences,
                    scope, decided_by, severity, tags
                ) VALUES (
                    'business', 'pretel-os',
                    'auto_index test',
                    'context for ' || %s,
                    'decision text for ' || %s,
                    'consequences for ' || %s,
                    'operational', 'test', 'minor', ARRAY[%s, 'auto-index-test']
                ) RETURNING id
                """,
                (tag, tag, tag, tag),
            )
            row = cur.fetchone()
            assert row is not None
            return str(row[0])


def _cleanup_tag(tag: str) -> None:
    """DELETE the seeded decisions row by tag. Idempotent."""
    with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM decisions WHERE %s = ANY(tags)",
                (tag,),
            )


def _fetch_decision_state(decision_id: str) -> tuple[bool, bool]:
    """Return (row_exists, embedding_is_null) for a decisions row."""
    with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT embedding IS NULL FROM decisions WHERE id = %s",
                (decision_id,),
            )
            row = cur.fetchone()
            if row is None:
                return False, False
            return True, bool(row[0])


def _fetch_pending(decision_id: str) -> Optional[tuple[int, Optional[str]]]:
    """Return (attempts, last_error) for the pending row pointing at decision_id, or None if absent."""
    with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT attempts, last_error FROM pending_embeddings "
                "WHERE target_table = 'decisions' AND target_id = %s",
                (decision_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return int(row[0]), (row[1] if row[1] else None)


def _fire_notify(payload: str) -> None:
    """Emit pg_notify('embedding_queue', payload) on a fresh autocommit conn."""
    with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_notify('embedding_queue', %s)", (payload,))


@pytest_asyncio.fixture
async def worker_pool() -> AsyncIterator[AsyncConnectionPool]:
    """Dedicated pool the worker functions can use directly.

    `_drain_once` and `_process_one` accept an `AsyncConnectionPool`; we
    open one per test so test-level connection state stays isolated from
    the session-scoped `test_pool`.
    """
    pool = AsyncConnectionPool(
        conninfo=_TEST_DSN, min_size=1, max_size=2, open=False, timeout=5.0
    )
    await pool.open(wait=True)
    try:
        yield pool
    finally:
        await pool.close()


# ---------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------

async def test_drain_once_processes_pending_row(
    patched_db: None,
    patched_embed: Callable[[Optional[list[float]]], None],
    worker_pool: AsyncConnectionPool,
) -> None:
    """End-to-end: insert decision (NULL embedding) → trigger queues
    pending → _drain_once embeds + writes vector + deletes pending row."""
    tag = f"drain-once-{uuid.uuid4().hex[:8]}"
    decision_id = _seed_decision_with_null_embedding(tag)
    try:
        # Trigger fired on INSERT — pending row should already exist.
        pre = _fetch_pending(decision_id)
        assert pre is not None, "trigger did not queue pending row"

        sem = asyncio.Semaphore(2)
        processed = await worker._drain_once(worker_pool, semaphore=sem)
        assert processed >= 1

        exists, is_null = _fetch_decision_state(decision_id)
        assert exists
        assert is_null is False, "embedding should be populated"

        post = _fetch_pending(decision_id)
        assert post is None, "pending row should be deleted on success"
    finally:
        _cleanup_tag(tag)


async def test_embed_failure_marks_attempt(
    patched_db: None,
    patched_embed: Callable[[Optional[list[float]]], None],
    worker_pool: AsyncConnectionPool,
) -> None:
    """When embed() returns None (API down / quota / invalid key), the
    pending row stays alive with attempts++ and a last_error string."""
    tag = f"embed-fail-{uuid.uuid4().hex[:8]}"
    decision_id = _seed_decision_with_null_embedding(tag)
    try:
        patched_embed(None)  # next call → None

        sem = asyncio.Semaphore(2)
        await worker._drain_once(worker_pool, semaphore=sem)

        # Target embedding still NULL.
        exists, is_null = _fetch_decision_state(decision_id)
        assert exists and is_null is True

        # Pending row alive with attempts=1.
        post = _fetch_pending(decision_id)
        assert post is not None
        attempts, last_error = post
        assert attempts == 1
        assert last_error is not None
        assert "embed returned None" in last_error
    finally:
        _cleanup_tag(tag)


async def test_max_attempts_skips_poison_row(
    patched_db: None,
    patched_embed: Callable[[Optional[list[float]]], None],
    worker_pool: AsyncConnectionPool,
) -> None:
    """A pending row with attempts >= MAX_ATTEMPTS is invisible to
    _fetch_due_rows — operator must reset attempts to retry."""
    tag = f"poison-{uuid.uuid4().hex[:8]}"
    decision_id = _seed_decision_with_null_embedding(tag)
    try:
        # Fast-forward attempts to MAX so the row is poison-pilled.
        with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE pending_embeddings SET attempts = %s "
                    "WHERE target_table = 'decisions' AND target_id = %s",
                    (worker.MAX_ATTEMPTS, decision_id),
                )

        rows = await worker._fetch_due_rows(worker_pool)
        target_ids = {r[2] for r in rows}
        assert decision_id not in target_ids, "poison row should be filtered out"

        # Sanity — a non-poison row in the same batch IS returned.
        live_tag = f"poison-live-{uuid.uuid4().hex[:8]}"
        live_id = _seed_decision_with_null_embedding(live_tag)
        try:
            rows2 = await worker._fetch_due_rows(worker_pool)
            target_ids2 = {r[2] for r in rows2}
            assert live_id in target_ids2
            assert decision_id not in target_ids2
        finally:
            _cleanup_tag(live_tag)
    finally:
        _cleanup_tag(tag)


async def test_unknown_target_table_is_skipped(
    patched_db: None,
    patched_embed: Callable[[Optional[list[float]]], None],
    worker_pool: AsyncConnectionPool,
) -> None:
    """Defensive path: a pending row pointing at a table not in
    INDEXABLE_TABLES is not embedded (the f-string UPDATE would be unsafe).
    _process_one returns False and does not crash."""
    pending_id = str(uuid.uuid4())
    fake_target = str(uuid.uuid4())
    with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pending_embeddings "
                "(id, target_table, target_id, source_text) "
                "VALUES (%s, 'not_a_real_table', %s, 'irrelevant')",
                (pending_id, fake_target),
            )

    ok = await worker._process_one(
        worker_pool,
        pending_id=pending_id,
        target_table="not_a_real_table",
        target_id=fake_target,
        source_text="irrelevant",
    )
    assert ok is False
    # Row should remain — skipped, not modified.
    with psycopg.connect(_TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM pending_embeddings WHERE id = %s",
                (pending_id,),
            )
            row = cur.fetchone()
            assert row is not None and int(row[0]) == 1


async def test_listen_wakes_drain_on_notify(
    patched_db: None,
    patched_embed: Callable[[Optional[list[float]]], None],
) -> None:
    """consume_embedding_queue starts → seed a pending row → fire pg_notify
    → within a few seconds the embedding should be written.

    Uses a short scan_interval as a safety net (LISTEN should win the race;
    the scan exists so even if the notify is lost the test still passes
    in <2× scan_interval)."""
    tag = f"listen-{uuid.uuid4().hex[:8]}"
    decision_id = _seed_decision_with_null_embedding(tag)
    stop = asyncio.Event()
    task = asyncio.create_task(
        worker.consume_embedding_queue(
            _TEST_DSN,
            scan_interval_secs=2.0,
            max_concurrent=2,
            stop_event=stop,
        )
    )
    try:
        # The INSERT trigger already fired its NOTIFY; the worker's initial
        # drain on startup will pick this row up. We just need to give it
        # time. Race condition: the worker must finish its
        # AsyncConnectionPool.open() before the drain runs — we poll for
        # up to ~5s.
        deadline = asyncio.get_event_loop().time() + 5.0
        while asyncio.get_event_loop().time() < deadline:
            exists, is_null = _fetch_decision_state(decision_id)
            if exists and is_null is False:
                break
            await asyncio.sleep(0.2)

        exists, is_null = _fetch_decision_state(decision_id)
        assert exists
        assert is_null is False, (
            "consume loop did not embed within 5s "
            "(initial drain or LISTEN/NOTIFY broken)"
        )

        # Re-test the live path: insert a SECOND row after the worker is
        # already running so we exercise the LISTEN→drain path, not the
        # initial-drain path.
        tag2 = f"listen-live-{uuid.uuid4().hex[:8]}"
        decision_id2 = _seed_decision_with_null_embedding(tag2)
        try:
            deadline = asyncio.get_event_loop().time() + 5.0
            while asyncio.get_event_loop().time() < deadline:
                exists, is_null = _fetch_decision_state(decision_id2)
                if exists and is_null is False:
                    break
                await asyncio.sleep(0.2)
            exists, is_null = _fetch_decision_state(decision_id2)
            assert is_null is False, (
                "live LISTEN→drain did not embed within 5s"
            )
        finally:
            _cleanup_tag(tag2)
    finally:
        stop.set()
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except asyncio.TimeoutError:
            task.cancel()
        _cleanup_tag(tag)
