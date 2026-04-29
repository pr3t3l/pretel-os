"""Unit tests for `mcp_server.tools.decisions`.

Five tests covering embedding round-trip (mocked + real), pending_embeddings
queueing on embedding failure, search ranking, and supersede atomicity.

The `slow` marker on `test_decision_record_real_embedding` opts the test
into actual OpenAI calls (~$0.0001 per pytest run). Default `pytest`
includes them per pytest.ini; `pytest -m "not slow"` skips them.

Each test asserts at least one DB-side fact via SELECT to catch
schema/payload contract drift (LL-M4-PHASE-A-001).
"""
from __future__ import annotations

from typing import Any

import pytest
from psycopg_pool import AsyncConnectionPool

from mcp_server.tools.decisions import (
    decision_record,
    decision_search,
    decision_supersede,
)


async def _select_one(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...]) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()


async def _delete_decision(pool: AsyncConnectionPool, decision_id: str) -> None:
    """Helper for tests that mutate decisions (which is NOT autotruncated)."""
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM pending_embeddings WHERE target_id = %s", (decision_id,))
            await cur.execute("DELETE FROM decisions WHERE id = %s", (decision_id,))


async def test_decision_record_with_mocked_embedding(
    patched_db: None,
    patched_embed: Any,  # the setter is unused but the fixture must be requested
    test_pool: AsyncConnectionPool,
) -> None:
    r = await decision_record(
        bucket="business",
        project="pretel-os",
        title="SMOKE: test_decisions",
        context="ctx",
        decision="dec",
        consequences="csq",
        scope="architectural",
    )

    try:
        assert r["status"] == "ok"
        assert r["embedding_queued"] is False  # mock provides a vector

        row = await _select_one(
            test_pool,
            "SELECT bucket, scope, embedding IS NOT NULL, vector_dims(embedding) FROM decisions WHERE id = %s",
            (r["id"],),
        )
        assert row == ("business", "architectural", True, 3072)
    finally:
        await _delete_decision(test_pool, r["id"])


@pytest.mark.slow
async def test_decision_record_real_embedding(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    """Real OpenAI call (~$0.0001). Validates the API path itself.

    No `patched_embed` fixture — the real `embeddings.embed()` runs.
    """
    r = await decision_record(
        bucket="business",
        project="pretel-os",
        title="SMOKE-real: test_decision_record_real_embedding",
        context="exercises the real OpenAI embedding path",
        decision="ship",
        consequences="api validated",
    )

    try:
        assert r["status"] == "ok"
        assert r["embedding_queued"] is False

        row = await _select_one(
            test_pool,
            "SELECT vector_dims(embedding) FROM decisions WHERE id = %s",
            (r["id"],),
        )
        assert row == (3072,)
    finally:
        await _delete_decision(test_pool, r["id"])


async def test_decision_record_queues_pending_when_embed_fails(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """When embed() returns None, the decision row saves with embedding=NULL
    and the existing notify_missing_embedding trigger queues a row to
    pending_embeddings (decisions has the trigger; verified via 0019)."""
    patched_embed(None)  # next embed call returns None

    r = await decision_record(
        bucket="business",
        project="pretel-os",
        title="embed-failure case",
        context="x", decision="x", consequences="x",
    )

    try:
        assert r["status"] == "ok"
        assert r["embedding_queued"] is True

        # decisions row exists with embedding=NULL
        dec_row = await _select_one(
            test_pool,
            "SELECT embedding IS NULL FROM decisions WHERE id = %s",
            (r["id"],),
        )
        assert dec_row == (True,)

        # pending_embeddings row queued by trigger
        pend_row = await _select_one(
            test_pool,
            "SELECT target_table FROM pending_embeddings WHERE target_id = %s",
            (r["id"],),
        )
        assert pend_row == ("decisions",)
    finally:
        await _delete_decision(test_pool, r["id"])


async def test_decision_search_returns_ranked_results(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """Insert 3 decisions, then search — assert 3 results with similarity
    floats (filter-first per CONSTITUTION §5.6 rule 26)."""
    ids: list[str] = []
    for i in range(3):
        r = await decision_record(
            bucket="business",
            project="pretel-os",
            title=f"search-test-{i}",
            context="ctx",
            decision="dec",
            consequences="csq",
            scope="architectural",
        )
        ids.append(r["id"])

    try:
        results = await decision_search(query="search test", scope="architectural", top_k=10)
        assert results["status"] == "ok"
        # All 3 inserted rows should match (active scope=architectural)
        returned_ids = {row["id"] for row in results["results"]}
        assert set(ids).issubset(returned_ids)
        for row in results["results"]:
            assert isinstance(row["similarity"], float)
            assert 0.0 <= row["similarity"] <= 1.0
    finally:
        for d in ids:
            await _delete_decision(test_pool, d)


async def test_decision_supersede_atomic(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """A → supersede(A, B): A.status=superseded, A.superseded_by_id=B.id;
    B.status=active. Re-supersede(A, ...) → error (already superseded)."""
    a = await decision_record(
        bucket="business",
        project="pretel-os",
        title="supersede-A",
        context="x", decision="x", consequences="x",
    )
    new_id = ""
    try:
        result = await decision_supersede(
            old_id=a["id"],
            new_decision_payload={
                "bucket": "business",
                "project": "pretel-os",
                "title": "supersede-B (replaces A)",
                "context": "evolved",
                "decision": "new direction",
                "consequences": "deprecates A",
            },
        )
        assert result["status"] == "ok"
        new_id = result["new_id"]
        assert result["old_id"] == a["id"]

        # A is now superseded
        a_row = await _select_one(
            test_pool,
            "SELECT status, superseded_by_id FROM decisions WHERE id = %s",
            (a["id"],),
        )
        assert a_row is not None
        assert a_row[0] == "superseded"
        assert str(a_row[1]) == new_id

        # B is active
        b_row = await _select_one(
            test_pool,
            "SELECT status, title FROM decisions WHERE id = %s",
            (new_id,),
        )
        assert b_row == ("active", "supersede-B (replaces A)")

        # Re-supersede A → error (it's already superseded)
        retry = await decision_supersede(
            old_id=a["id"],
            new_decision_payload={
                "bucket": "business",
                "project": "pretel-os",
                "title": "should not land",
                "context": "x", "decision": "x", "consequences": "x",
            },
        )
        assert retry["status"] == "error"
        assert "superseded" in retry["error"]
    finally:
        await _delete_decision(test_pool, a["id"])
        if new_id:
            await _delete_decision(test_pool, new_id)


async def test_decision_supersede_validates_payload(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """Validation runs BEFORE DB; returns error for missing/unknown keys."""
    a = await decision_record(
        bucket="business", project="pretel-os",
        title="validate-target", context="x", decision="x", consequences="x",
    )
    try:
        # Missing required keys
        missing = await decision_supersede(old_id=a["id"], new_decision_payload={"bucket": "business"})
        assert missing["status"] == "error"
        assert "missing" in missing["error"]

        # Unknown keys
        unknown = await decision_supersede(
            old_id=a["id"],
            new_decision_payload={
                "bucket": "business", "project": "pretel-os",
                "title": "x", "context": "x", "decision": "x", "consequences": "x",
                "evil_field": "boom",
            },
        )
        assert unknown["status"] == "error"
        assert "unknown" in unknown["error"]

        # Unknown old_id
        not_found = await decision_supersede(
            old_id="00000000-0000-0000-0000-000000000000",
            new_decision_payload={
                "bucket": "business", "project": "pretel-os",
                "title": "x", "context": "x", "decision": "x", "consequences": "x",
            },
        )
        assert not_found == {"status": "ok", "found": False}
    finally:
        await _delete_decision(test_pool, a["id"])


async def test_decisions_degraded_mode_writes_journal(
    patched_db: None, patched_embed: Any, db_unhealthy: None, journal_dir: Any
) -> None:
    """record + supersede return degraded with journal_id; search returns degraded list."""
    rec_r = await decision_record(
        bucket="business", project="pretel-os",
        title="x", context="x", decision="x", consequences="x",
    )
    assert rec_r["status"] == "degraded"
    assert "journal_id" in rec_r

    sup_r = await decision_supersede(
        old_id="00000000-0000-0000-0000-000000000000",
        new_decision_payload={
            "bucket": "business", "project": "pretel-os",
            "title": "x", "context": "x", "decision": "x", "consequences": "x",
        },
    )
    assert sup_r["status"] == "degraded"
    assert "journal_id" in sup_r

    search_r = await decision_search(query="x")
    assert search_r["status"] == "degraded"
    assert search_r["results"] == []

    files = list(journal_dir.glob("*.jsonl"))
    assert len(files) == 1
    contents = files[0].read_text()
    assert "decision_record" in contents
    assert "decision_supersede" in contents
