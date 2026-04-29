"""Migration test for `migrations/0029_data_migration_lessons_split.sql`.

Two tests:

1. `test_0029_migrates_four_misclassified_lessons` — apply 0001-0028 to
   a scratch database, INSERT the 4 known lessons (matching prefixes
   c40e09fc / d7f1e119 / 89c11602 / 3d98464b), apply 0029, assert each
   landed in its target table with the right shape and the source rows
   were marked archived with metadata pointers.

2. `test_0029_idempotent` — apply 0029 a second time on the post-state,
   assert row counts unchanged (5 ADRs, 1 decision from c40e09fc, 3
   tasks; 4 archived lessons) — no duplicates introduced.

The fixture creates a `pretel_os_migration_test` database from outside
psycopg's transactional context (CREATE DATABASE can't run inside one)
and drops it on teardown. We use `psql` via subprocess for the
CREATE/DROP because psycopg's pool can't issue them on a connection
that is already attached to another database.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any, AsyncIterator
from uuid import UUID

import pytest_asyncio
from psycopg_pool import AsyncConnectionPool


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "migrations"

SCRATCH_DB = "pretel_os_migration_test"
SCRATCH_DSN = f"postgresql://pretel_os@localhost/{SCRATCH_DB}"

# Hard-coded UUIDs that match the prefixes the migration's DO blocks
# look for. They DON'T have to be the production UUIDs — only the
# 8-char prefix matters for the migration's `WHERE id::text LIKE 'XX%'`.
_LESSON_C40E = UUID("c40e09fc-0000-0000-0000-000000000001")
_LESSON_D7F1 = UUID("d7f1e119-0000-0000-0000-000000000002")
_LESSON_89C1 = UUID("89c11602-0000-0000-0000-000000000003")
_LESSON_3D98 = UUID("3d98464b-0000-0000-0000-000000000004")


def _apply_migration_via_psql(database: str, sql_file: Path) -> None:
    """Run a migration file through psql as a subprocess."""
    result = subprocess.run(
        ["psql", "-h", "localhost", "-U", "pretel_os", "-d", database,
         "-v", "ON_ERROR_STOP=1", "-f", str(sql_file)],
        capture_output=True, text=True, env=os.environ,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"migration {sql_file.name} failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


def _create_database(name: str) -> None:
    subprocess.run(
        ["psql", "-h", "localhost", "-U", "pretel_os", "-d", "postgres",
         "-c", f"CREATE DATABASE {name};"],
        check=True, capture_output=True, env=os.environ,
    )


def _drop_database(name: str) -> None:
    subprocess.run(
        ["psql", "-h", "localhost", "-U", "pretel_os", "-d", "postgres",
         "-c", f"DROP DATABASE IF EXISTS {name};"],
        capture_output=True, env=os.environ,
    )


@pytest_asyncio.fixture
async def scratch_pool() -> AsyncIterator[AsyncConnectionPool]:
    """Build a fresh scratch DB with migrations 0000..0028 + 0028a applied
    (everything except 0029, which is the migration under test).

    Yields a pool against the scratch DB. Drops the DB on teardown.
    """
    _drop_database(SCRATCH_DB)  # in case a previous run left it
    _create_database(SCRATCH_DB)

    # Apply all migrations EXCEPT 0029 — sorted gives correct order.
    for f in sorted(MIGRATIONS_DIR.glob("00*.sql")):
        if "0029" in f.name:
            continue
        _apply_migration_via_psql(SCRATCH_DB, f)

    pool = AsyncConnectionPool(
        conninfo=SCRATCH_DSN, min_size=1, max_size=2, open=False, timeout=5.0,
    )
    await pool.open(wait=True)
    try:
        yield pool
    finally:
        await pool.close()
        # Wait briefly so the close completes before DROP DATABASE
        await asyncio.sleep(0.1)
        _drop_database(SCRATCH_DB)


async def _insert_4_lessons(pool: AsyncConnectionPool) -> None:
    """Insert 4 lessons matching the prefixes the 0029 DO blocks gate on."""
    rows = [
        (_LESSON_C40E, "Anti-pattern: verbal acknowledgment", "deferral discipline content"),
        (_LESSON_D7F1, "DEFERRED: LiteLLM concrete model", "Phase D telemetry fix"),
        (_LESSON_89C1, "DEFERRED: pyproject.toml at repo root", "before Module 5 unblock"),
        (_LESSON_3D98, "DEFERRED: prompt caching", "Phase F when classify.txt > 1024 tok"),
    ]
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            for lid, title, content in rows:
                await cur.execute(
                    """
                    INSERT INTO lessons
                        (id, title, content, bucket, category, tags, source, status, evidence)
                    VALUES (%s, %s, %s, 'business', 'PROC', ARRAY['deferred-todo'],
                            'manual', 'active', '{}'::jsonb)
                    """,
                    (str(lid), title, content),
                )


async def _select_one(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...]) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()


async def _scalar(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...] = ()) -> Any:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            row = await cur.fetchone()
    assert row is not None
    return row[0]


async def test_0029_migrates_four_misclassified_lessons(
    scratch_pool: AsyncConnectionPool,
) -> None:
    """Apply migration 0029 against a scratch DB seeded with the 4 known
    lessons. Assert all 5 ADRs land + 4 lessons split correctly."""
    await _insert_4_lessons(scratch_pool)

    _apply_migration_via_psql(SCRATCH_DB, MIGRATIONS_DIR / "0029_data_migration_lessons_split.sql")

    # 5 ADRs seeded
    adr_count = await _scalar(
        scratch_pool, "SELECT count(*) FROM decisions WHERE adr_number BETWEEN 20 AND 24"
    )
    assert adr_count == 5

    # 4 source lessons archived with metadata pointers
    archived = await _scalar(
        scratch_pool,
        "SELECT count(*) FROM lessons WHERE status='archived' "
        "AND metadata->>'superseded_by_migration' = '0029'",
    )
    assert archived == 4

    # c40e09fc → decisions with scope='process'
    proc_dec = await _select_one(
        scratch_pool,
        """
        SELECT title, scope, derived_from_lessons FROM decisions
        WHERE scope='process' AND %s = ANY(derived_from_lessons)
        """,
        (str(_LESSON_C40E),),
    )
    assert proc_dec is not None
    assert proc_dec[1] == "process"

    # d7f1e119 + 89c11602 + 3d98464b → tasks
    task_count = await _scalar(
        scratch_pool, "SELECT count(*) FROM tasks WHERE source='migration'"
    )
    assert task_count == 3

    # Verify each task's destination metadata
    for lid, expected_module, expected_phase in [
        (_LESSON_D7F1, "M4", "Phase D"),
        (_LESSON_89C1, "M0.X", "before Module 5"),
        (_LESSON_3D98, "M4", "Phase F"),
    ]:
        row = await _select_one(
            scratch_pool,
            "SELECT module, trigger_phase FROM tasks WHERE metadata->>'migrated_from_lesson' = %s",
            (str(lid),),
        )
        assert row == (expected_module, expected_phase), f"lesson {lid} → {row}"


async def test_0029_idempotent(scratch_pool: AsyncConnectionPool) -> None:
    """Apply 0029, capture row counts, apply again, assert no duplicates."""
    await _insert_4_lessons(scratch_pool)

    # First application
    _apply_migration_via_psql(SCRATCH_DB, MIGRATIONS_DIR / "0029_data_migration_lessons_split.sql")

    pre_adr = await _scalar(scratch_pool, "SELECT count(*) FROM decisions")
    pre_tasks = await _scalar(scratch_pool, "SELECT count(*) FROM tasks WHERE source='migration'")
    pre_archived = await _scalar(
        scratch_pool, "SELECT count(*) FROM lessons WHERE status='archived'"
    )

    # Second application — should be a no-op
    _apply_migration_via_psql(SCRATCH_DB, MIGRATIONS_DIR / "0029_data_migration_lessons_split.sql")

    post_adr = await _scalar(scratch_pool, "SELECT count(*) FROM decisions")
    post_tasks = await _scalar(scratch_pool, "SELECT count(*) FROM tasks WHERE source='migration'")
    post_archived = await _scalar(
        scratch_pool, "SELECT count(*) FROM lessons WHERE status='archived'"
    )

    assert post_adr == pre_adr, f"ADR count drifted: {pre_adr} → {post_adr}"
    assert post_tasks == pre_tasks, f"task count drifted: {pre_tasks} → {post_tasks}"
    assert post_archived == pre_archived, f"archived count drifted: {pre_archived} → {post_archived}"
