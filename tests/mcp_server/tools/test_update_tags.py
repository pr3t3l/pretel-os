"""Unit tests for tag-only update tools (2026-06-01 patch).

Covers:
    * `lesson_update_tags`
    * `decision_update_tags`
    * `best_practice_update_tags`

Each tool offers tags_add / tags_remove semantics. Tests verify:
    * Insert → add idempotency (re-adding a present tag is a no-op)
    * Remove correctness (subtracting an absent tag is a no-op)
    * not-found returns {ok, found:False} without touching anything
    * empty operation returns an explicit error
    * degraded mode journals the call

Lessons + decisions are not in conftest's auto-truncate list, so the
test_pool fixture stays clean via per-test DELETE BY id at teardown.
best_practices IS auto-truncated.

All tests @pytest.mark.slow because they exercise the real test DB.
"""
from __future__ import annotations

from typing import Any, AsyncIterator
from uuid import uuid4

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from mcp_server.tools.best_practices import (
    best_practice_record,
    best_practice_update_tags,
)
from mcp_server.tools.decisions import (
    decision_record,
    decision_update_tags,
)
from mcp_server.tools.lessons import (
    lesson_update_tags,
    save_lesson,
)

_LESSON_BUCKET = "test_update_tags_personal"
_DECISION_BUCKET = "personal"
_DECISION_PROJECT_PREFIX = "test_update_tags_proj_"


@pytest_asyncio.fixture
async def cleanup_rows(
    test_pool: AsyncConnectionPool,
) -> AsyncIterator[None]:
    yield
    async with test_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM lessons WHERE bucket = %s",
                (_LESSON_BUCKET,),
            )
            await cur.execute(
                "DELETE FROM decisions WHERE project LIKE %s",
                (f"{_DECISION_PROJECT_PREFIX}%",),
            )


async def _seed_lesson(
    pool: AsyncConnectionPool,
    *,
    tags: list[str],
    title: str = "seed lesson",
    content: str = "seed content with Anthropic_SDK technology reference",
) -> str:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO lessons (title, content, bucket, category, tags, status)
                VALUES (%s, %s, %s, %s, %s, 'active'::lesson_status)
                RETURNING id
                """,
                (title, content, _LESSON_BUCKET, "OPS", tags),
            )
            row = await cur.fetchone()
    assert row is not None
    return str(row[0])


async def _fetch_lesson_tags(pool: AsyncConnectionPool, lesson_id: str) -> list[str]:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT tags FROM lessons WHERE id = %s", (lesson_id,))
            row = await cur.fetchone()
    assert row is not None
    return list(row[0])


async def _fetch_lesson_embedding_dim(pool: AsyncConnectionPool, lesson_id: str) -> int | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT vector_dims(embedding) FROM lessons WHERE id = %s",
                (lesson_id,),
            )
            row = await cur.fetchone()
    return row[0] if row else None


# --- lesson_update_tags ---------------------------------------------------


@pytest.mark.slow
async def test_lesson_update_tags_adds_union(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_rows: None,
) -> None:
    lesson_id = await _seed_lesson(test_pool, tags=["course:lidr-ai-engineer", "anthropic-sdk"])

    r = await lesson_update_tags(id=lesson_id, tags_add=["LIDR"])

    assert r["status"] == "ok"
    assert r["found"] is True
    assert set(r["tags"]) == {"course:lidr-ai-engineer", "anthropic-sdk", "LIDR"}
    assert r["tags"][0] == "course:lidr-ai-engineer"  # original order preserved
    assert r["tags"][-1] == "LIDR"                    # new tag appended

    assert await _fetch_lesson_tags(test_pool, lesson_id) == r["tags"]


@pytest.mark.slow
async def test_lesson_update_tags_add_existing_is_idempotent(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_rows: None,
) -> None:
    lesson_id = await _seed_lesson(test_pool, tags=["LIDR", "anthropic-sdk"])

    r = await lesson_update_tags(id=lesson_id, tags_add=["LIDR"])

    assert r["status"] == "ok"
    assert r["found"] is True
    assert r["tags"] == ["LIDR", "anthropic-sdk"]  # unchanged


@pytest.mark.slow
async def test_lesson_update_tags_remove_subtracts(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_rows: None,
) -> None:
    lesson_id = await _seed_lesson(test_pool, tags=["LIDR", "stale-tag", "anthropic-sdk"])

    r = await lesson_update_tags(id=lesson_id, tags_remove=["stale-tag"])

    assert r["status"] == "ok"
    assert r["tags"] == ["LIDR", "anthropic-sdk"]


@pytest.mark.slow
async def test_lesson_update_tags_add_and_remove_together(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_rows: None,
) -> None:
    lesson_id = await _seed_lesson(test_pool, tags=["old-tag"])

    r = await lesson_update_tags(
        id=lesson_id, tags_add=["new-tag"], tags_remove=["old-tag"]
    )

    assert r["status"] == "ok"
    assert r["tags"] == ["new-tag"]


@pytest.mark.slow
async def test_lesson_update_tags_does_not_invalidate_embedding(
    patched_db: None,
    patched_embed: Any,
    test_pool: AsyncConnectionPool,
    cleanup_rows: None,
) -> None:
    """Tag-only UPDATE must not null the embedding (mig 0037 trigger only
    fires on title/content change)."""
    save = await save_lesson(
        title="trigger check lesson",
        content="references pgvector_HNSW config",
        bucket=_LESSON_BUCKET,
        tags=["initial"],
        category="OPS",
        next_time="never re-embed on tag change",
    )
    assert save["status"] == "saved"
    lesson_id = save["id"]

    before = await _fetch_lesson_embedding_dim(test_pool, lesson_id)
    assert before == 3072

    r = await lesson_update_tags(id=lesson_id, tags_add=["LIDR"])
    assert r["status"] == "ok"

    after = await _fetch_lesson_embedding_dim(test_pool, lesson_id)
    assert after == 3072, "tag-only update must not null the embedding"


@pytest.mark.slow
async def test_lesson_update_tags_not_found(patched_db: None) -> None:
    r = await lesson_update_tags(id=str(uuid4()), tags_add=["x"])
    assert r == {"status": "ok", "found": False}


@pytest.mark.slow
async def test_lesson_update_tags_empty_op_is_error(patched_db: None) -> None:
    r = await lesson_update_tags(id=str(uuid4()))
    assert r["status"] == "error"
    assert "no tag operation" in r["error"]


@pytest.mark.slow
async def test_lesson_update_tags_degraded(
    db_unhealthy: None, journal_dir: Any
) -> None:
    r = await lesson_update_tags(id=str(uuid4()), tags_add=["x"])
    assert r["status"] == "degraded"
    assert "journal_id" in r


# --- decision_update_tags -------------------------------------------------


async def _seed_decision(
    pool: AsyncConnectionPool, *, project: str, tags: list[str]
) -> str:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO decisions
                    (bucket, project, title, context, decision, consequences, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    _DECISION_BUCKET,
                    project,
                    "seed decision",
                    "context",
                    "decision",
                    "consequences",
                    tags,
                ),
            )
            row = await cur.fetchone()
    assert row is not None
    return str(row[0])


async def _fetch_decision_tags(pool: AsyncConnectionPool, dec_id: str) -> list[str]:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT tags FROM decisions WHERE id = %s", (dec_id,))
            row = await cur.fetchone()
    assert row is not None
    return list(row[0])


@pytest.mark.slow
async def test_decision_update_tags_adds_union(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_rows: None,
) -> None:
    project = f"{_DECISION_PROJECT_PREFIX}a"
    dec_id = await _seed_decision(test_pool, project=project, tags=["original"])

    r = await decision_update_tags(id=dec_id, tags_add=["doctrine", "ADR"])

    assert r["status"] == "ok"
    assert r["found"] is True
    assert set(r["tags"]) == {"original", "doctrine", "ADR"}
    assert await _fetch_decision_tags(test_pool, dec_id) == r["tags"]


@pytest.mark.slow
async def test_decision_update_tags_remove_idempotent(
    patched_db: None,
    test_pool: AsyncConnectionPool,
    cleanup_rows: None,
) -> None:
    project = f"{_DECISION_PROJECT_PREFIX}b"
    dec_id = await _seed_decision(test_pool, project=project, tags=["a", "b"])

    r = await decision_update_tags(id=dec_id, tags_remove=["c"])

    assert r["status"] == "ok"
    assert r["tags"] == ["a", "b"]


@pytest.mark.slow
async def test_decision_update_tags_not_found(patched_db: None) -> None:
    r = await decision_update_tags(id=str(uuid4()), tags_add=["x"])
    assert r == {"status": "ok", "found": False}


# --- best_practice_update_tags --------------------------------------------


@pytest.mark.slow
async def test_best_practice_update_tags_adds_union(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    rec = await best_practice_record(
        title="bp-tag-test",
        guidance="always foo",
        domain="convention",
        tags=["original"],
    )
    bp_id = rec["id"]

    r = await best_practice_update_tags(id=bp_id, tags_add=["LIDR"])

    assert r["status"] == "ok"
    assert r["found"] is True
    assert set(r["tags"]) == {"original", "LIDR"}


@pytest.mark.slow
async def test_best_practice_update_tags_does_not_consume_rollback_slot(
    patched_db: None, patched_embed: Any, test_pool: AsyncConnectionPool
) -> None:
    """`previous_guidance` must remain NULL after a tag-only update —
    the rollback slot belongs to `best_practice_record(update_id=...)`."""
    rec = await best_practice_record(
        title="bp-rollback-slot-test",
        guidance="version A",
        rationale="rationale A",
        domain="process",
        tags=["initial"],
    )
    bp_id = rec["id"]

    r = await best_practice_update_tags(id=bp_id, tags_add=["added"])
    assert r["status"] == "ok"

    async with test_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT guidance, previous_guidance, previous_rationale "
                "FROM best_practices WHERE id = %s",
                (bp_id,),
            )
            row = await cur.fetchone()
    assert row == ("version A", None, None)


@pytest.mark.slow
async def test_best_practice_update_tags_not_found(patched_db: None) -> None:
    r = await best_practice_update_tags(id=str(uuid4()), tags_add=["x"])
    assert r == {"status": "ok", "found": False}


@pytest.mark.slow
async def test_best_practice_update_tags_empty_op_is_error(patched_db: None) -> None:
    r = await best_practice_update_tags(id=str(uuid4()))
    assert r["status"] == "error"
    assert "no tag operation" in r["error"]
