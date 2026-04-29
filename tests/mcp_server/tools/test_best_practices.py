"""Unit tests for `mcp_server.tools.best_practices`.

Eight tests covering insert/update/rollback round-trip, supersession,
real-OpenAI integration (slow), and the regression test for the silent
Phase C bug (commit aba04c7) where embedding=None on best_practices was
returning embedding_queued=True without actually queueing — because the
table has no notify_missing_embedding trigger.

Each test asserts at least one DB-side fact via SELECT to catch
schema/payload contract drift (LL-M4-PHASE-A-001).
"""
from __future__ import annotations

from typing import Any

import pytest
from psycopg_pool import AsyncConnectionPool

from mcp_server.tools.best_practices import (
    best_practice_deactivate,
    best_practice_record,
    best_practice_rollback,
    best_practice_search,
)


async def _select_one(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...]) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()


async def _select_all(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchall()


async def test_best_practice_record_insert_with_mocked_embedding(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    r = await best_practice_record(
        title="Test BP",
        guidance="Always foo when bar.",
        rationale="Because baz.",
        domain="process",
    )

    assert r["status"] == "ok"
    assert r["action"] == "inserted"
    assert r["embedding_queued"] is False
    assert "rollback_available" not in r  # only set on UPDATE path

    row = await _select_one(
        test_pool,
        """
        SELECT title, guidance, rationale, domain, scope, active,
               previous_guidance, previous_rationale,
               embedding IS NOT NULL, vector_dims(embedding)
        FROM best_practices WHERE id = %s
        """,
        (r["id"],),
    )
    assert row == (
        "Test BP", "Always foo when bar.", "Because baz.",
        "process", "global", True,
        None, None,            # previous_* are NULL on fresh insert
        True, 3072,            # embedding present, full dim
    )


@pytest.mark.slow
async def test_best_practice_record_real_embedding(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    """Real OpenAI call (~$0.0001). Validates the API path."""
    r = await best_practice_record(
        title="SMOKE-real: best_practice real embed",
        guidance="exercise the OpenAI embedding path",
        domain="convention",
    )

    row = await _select_one(
        test_pool,
        "SELECT vector_dims(embedding) FROM best_practices WHERE id = %s",
        (r["id"],),
    )
    assert row == (3072,)


async def test_best_practice_record_update_copies_to_previous_fields(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """UPDATE path copies current guidance/rationale into previous_* before
    overwriting. Caller gets rollback_available=True."""
    initial = await best_practice_record(
        title="iterating BP",
        guidance="version A",
        rationale="rationale A",
        domain="process",
    )

    updated = await best_practice_record(
        title="iterating BP",
        guidance="version B",
        rationale="rationale B",
        domain="process",
        update_id=initial["id"],
    )

    assert updated["status"] == "ok"
    assert updated["action"] == "updated"
    assert updated["rollback_available"] is True

    row = await _select_one(
        test_pool,
        "SELECT guidance, rationale, previous_guidance, previous_rationale FROM best_practices WHERE id = %s",
        (initial["id"],),
    )
    assert row == ("version B", "rationale B", "version A", "rationale A")


async def test_best_practice_rollback_round_trip(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """record(A) → record(update_id, B) → rollback → guidance back to A,
    previous_* cleared. Second rollback returns 'no rollback available'."""
    a = await best_practice_record(
        title="rollback BP",
        guidance="A",
        rationale="rationale A",
        domain="process",
    )
    await best_practice_record(
        title="rollback BP",
        guidance="B",
        rationale="rationale B",
        domain="process",
        update_id=a["id"],
    )

    # State after update
    pre = await _select_one(
        test_pool,
        "SELECT guidance, previous_guidance FROM best_practices WHERE id = %s",
        (a["id"],),
    )
    assert pre == ("B", "A")

    # Rollback
    rolled = await best_practice_rollback(id=a["id"])
    assert rolled["status"] == "ok"
    assert rolled["action"] == "rolled_back"

    # State restored
    post = await _select_one(
        test_pool,
        "SELECT guidance, rationale, previous_guidance, previous_rationale FROM best_practices WHERE id = %s",
        (a["id"],),
    )
    assert post == ("A", "rationale A", None, None)

    # Second rollback rejected
    again = await best_practice_rollback(id=a["id"])
    assert again["status"] == "error"
    assert "no rollback" in again["error"]


async def test_best_practice_rollback_re_embeds_restored_content(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """Rollback re-embeds inline so the embedding column matches the
    restored content (not the version that was just rolled back from)."""
    fixed_a = [0.10] * 3072  # all 0.10s
    fixed_b = [0.50] * 3072  # all 0.50s

    patched_embed(fixed_a)
    a = await best_practice_record(
        title="re-embed BP", guidance="A", domain="process",
    )

    patched_embed(fixed_b)
    await best_practice_record(
        title="re-embed BP", guidance="B", domain="process", update_id=a["id"],
    )

    # Sanity: embedding currently encodes B (all 0.50s)
    pre = await _select_one(
        test_pool,
        "SELECT (embedding::real[])[1] FROM best_practices WHERE id = %s",
        (a["id"],),
    )
    assert pre is not None
    assert abs(float(pre[0]) - 0.50) < 1e-3

    # Rollback re-embeds — set the next embed call to fixed_a's value
    patched_embed(fixed_a)
    await best_practice_rollback(id=a["id"])

    post = await _select_one(
        test_pool,
        "SELECT guidance, (embedding::real[])[1] FROM best_practices WHERE id = %s",
        (a["id"],),
    )
    assert post is not None
    assert post[0] == "A"
    assert abs(float(post[1]) - 0.10) < 1e-3


async def test_best_practice_record_queues_pending_embedding_on_failure(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """REGRESSION TEST for the Phase C bug (commit aba04c7).

    best_practices receives the notify_missing_embedding trigger in
    migration 0030 (added 2026-04-29 to close the gap from migration 0027
    being created after 0019's bulk attachment). When embed() returns
    None on INSERT, the trigger queues a row in pending_embeddings —
    same as lessons / decisions / patterns / etc.

    INSERT path: 1 row in pending_embeddings (queued by trigger).
    UPDATE path: still 1 row (trigger is AFTER INSERT only — UPDATE
    with embed=None is a silent no-op for the queue, consistent with
    every other table).
    """
    patched_embed(None)  # force failure path

    # INSERT
    r1 = await best_practice_record(
        title="regression BP",
        guidance="initial guidance",
        domain="process",
    )
    assert r1["embedding_queued"] is True

    rows_after_insert = await _select_all(
        test_pool,
        "SELECT target_table, source_text, attempts FROM pending_embeddings WHERE target_id = %s",
        (r1["id"],),
    )
    assert len(rows_after_insert) == 1
    assert rows_after_insert[0][0] == "best_practices"
    assert "initial guidance" in rows_after_insert[0][1]
    assert rows_after_insert[0][2] == 0  # attempts default

    # UPDATE — embed still patched to None
    r2 = await best_practice_record(
        title="regression BP",
        guidance="refined guidance",
        domain="process",
        update_id=r1["id"],
    )
    assert r2["embedding_queued"] is True

    # Trigger is AFTER INSERT only, so UPDATE-with-embed=None doesn't
    # change the queue. Still exactly the 1 row from the INSERT — no
    # duplicate, but source_text is NOT refreshed to "refined guidance".
    rows_after_update = await _select_all(
        test_pool,
        "SELECT count(*) FROM pending_embeddings WHERE target_id = %s",
        (r1["id"],),
    )
    assert rows_after_update[0][0] == 1


async def test_best_practice_search_excludes_inactive(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """search() filters active=true. Deactivated rows shouldn't appear."""
    a = await best_practice_record(
        title="active BP", guidance="A", domain="process",
    )
    b = await best_practice_record(
        title="to be deactivated BP", guidance="B", domain="process",
    )

    deact = await best_practice_deactivate(id=b["id"], reason="smoke")
    assert deact["status"] == "ok"
    assert deact["found"] is True

    results = await best_practice_search(query="bp", domain="process", top_k=10)
    assert results["status"] == "ok"
    returned_ids = {row["id"] for row in results["results"]}
    assert a["id"] in returned_ids
    assert b["id"] not in returned_ids


async def test_best_practice_supersede_chain(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """supersede semantics live in the SCHEMA (self-FK superseded_by) but
    no MCP tool currently writes superseded_by — by design (operator works
    via record/update/rollback chain instead). Test the schema invariant
    by setting superseded_by directly via SQL: the FK and active filter
    behavior must work.

    If a future Phase E adds a public supersede tool, this test exercises
    the underlying schema; only the orchestration changes."""
    a = await best_practice_record(title="A", guidance="orig", domain="process")
    b = await best_practice_record(title="B replaces A", guidance="new", domain="process")

    # Manually link via SQL — there's no public tool for this in Phase C.
    async with test_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE best_practices SET active=false, superseded_by=%s WHERE id=%s",
                (b["id"], a["id"]),
            )

    # Verify the chain — A points to B; B is the live row
    chain = await _select_one(
        test_pool,
        """
        SELECT bp.title, bp.active, bp.superseded_by, new.title
        FROM best_practices bp
        LEFT JOIN best_practices new ON bp.superseded_by = new.id
        WHERE bp.id = %s
        """,
        (a["id"],),
    )
    assert chain is not None
    assert chain[0] == "A"
    assert chain[1] is False
    assert str(chain[2]) == b["id"]
    assert chain[3] == "B replaces A"

    # And search excludes the inactive (superseded) row
    results = await best_practice_search(query="A", domain="process", top_k=10)
    returned_ids = {row["id"] for row in results["results"]}
    assert a["id"] not in returned_ids
    assert b["id"] in returned_ids


async def test_best_practice_record_update_not_found(
    patched_db: None, patched_embed: Any
) -> None:
    """update_id pointing at a non-existent row returns {status:error, error:'not found'}."""
    r = await best_practice_record(
        title="x", guidance="y", domain="process",
        update_id="00000000-0000-0000-0000-000000000000",
    )
    assert r["status"] == "error"
    assert "not found" in r["error"]


async def test_best_practice_deactivate_and_rollback_not_found(
    patched_db: None, patched_embed: Any
) -> None:
    """Both tools handle missing id with found:False, not error."""
    deact = await best_practice_deactivate(
        id="00000000-0000-0000-0000-000000000000", reason="x"
    )
    assert deact["status"] == "ok"
    assert deact["found"] is False

    rollback = await best_practice_rollback(id="00000000-0000-0000-0000-000000000000")
    assert rollback["status"] == "ok"
    assert rollback["found"] is False


async def test_best_practices_degraded_mode_writes_journal(
    patched_db: None, patched_embed: Any, db_unhealthy: None, journal_dir: Any
) -> None:
    """record + deactivate + rollback return degraded with journal_id; search returns degraded list."""
    rec_r = await best_practice_record(title="x", guidance="y", domain="process")
    assert rec_r["status"] == "degraded"
    assert "journal_id" in rec_r

    deact_r = await best_practice_deactivate(
        id="00000000-0000-0000-0000-000000000000", reason="x"
    )
    assert deact_r["status"] == "degraded"
    assert "journal_id" in deact_r

    roll_r = await best_practice_rollback(id="00000000-0000-0000-0000-000000000000")
    assert roll_r["status"] == "degraded"
    assert "journal_id" in roll_r

    search_r = await best_practice_search(query="x")
    assert search_r["status"] == "degraded"
    assert search_r["results"] == []

    files = list(journal_dir.glob("*.jsonl"))
    assert len(files) == 1
    contents = files[0].read_text()
    for op in ("best_practice_record", "best_practice_deactivate", "best_practice_rollback"):
        assert op in contents
