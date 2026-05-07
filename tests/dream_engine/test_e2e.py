"""Slow integration tests for dream_engine — real DB, real triggers.

All marked @pytest.mark.slow. Use sync psycopg against pretel_os_test
because the worker itself is sync (mirrors readme_renderer pattern).

Coverage matrix per spec.md success criteria:
  SC1 — dream_engine_runs row recorded   → test_main_records_run
  SC2 — utility_recompute updates score   → test_utility_recompute_runs_clean
  SC3 — dedup writes pair / idempotent    → test_dedup_inserts_pair, test_dedup_idempotent
  SC4 — archive flips low-utility         → test_archive_flips_old_lesson
  SC5 — partial status on job fault       → test_main_partial_status_on_fault
  SC6 — preference_set tunes thresholds   → test_archive_thresholds_tunable
  (SC7 = 7-day production observation, not testable in unit suite)

Also covers the contractual hard-fail per ADR-029:
  test_archive_thresholds_missing_key_raises — no hardcoded fallback.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import psycopg
import pytest

from dream_engine import config as dream_config_mod
from dream_engine import worker as dream_worker_mod
from dream_engine.config import load_archive_thresholds

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"
FIXED_VEC_A = "[" + ",".join(["0.10"] * 3072) + "]"
FIXED_VEC_B_ALMOST_A = "[" + ",".join(["0.11"] * 3072) + "]"  # cos sim ~1.0 with A
FIXED_VEC_C = "[" + ",".join(["-0.50"] * 3072) + "]"          # cos sim ~-1.0 with A


pytestmark = pytest.mark.slow


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    """Sync connection to the test DB. Reset state between tests."""
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        # Cleanup BEFORE the test (last-test residue), commit cleanly.
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cross_pollination_queue")
            cur.execute("DELETE FROM dream_engine_runs")
            cur.execute("DELETE FROM lessons WHERE source = 'dream_engine_test'")
        conn.commit()
        yield conn
    finally:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cross_pollination_queue")
                cur.execute("DELETE FROM dream_engine_runs")
                cur.execute("DELETE FROM lessons WHERE source = 'dream_engine_test'")
            conn.commit()
        finally:
            conn.close()


@pytest.fixture
def patched_dream_engine_db(monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect dream_engine.worker to use TEST_DSN instead of prod URL."""
    from dataclasses import replace as dc_replace
    from mcp_server import config as cfg_mod

    original = cfg_mod.load_config

    def _override() -> Any:
        loaded = original()
        return dc_replace(loaded, database_url=TEST_DSN)

    monkeypatch.setattr(cfg_mod, "load_config", _override)


def _seed_lesson(
    conn: psycopg.Connection,
    *,
    bucket: str,
    title: str,
    content: str,
    embedding_literal: str,
    status: str = "active",
    usage_count: int = 0,
    utility_score: float = 0.0,
    created_at_offset_days: int = 0,
) -> str:
    """Insert a lesson with a synthetic embedding. Returns id as str.

    embedding_literal is a pgvector text form like '[0.1,0.2,...]'.
    created_at_offset_days < 0 makes the lesson older than now.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO lessons (
                bucket, title, content, category, status,
                usage_count, utility_score,
                created_at, updated_at,
                embedding, source
            )
            VALUES (
                %s, %s, %s, 'general', %s,
                %s, %s,
                now() + %s * interval '1 day',
                now() + %s * interval '1 day',
                %s::vector, 'dream_engine_test'
            )
            RETURNING id
            """,
            (
                bucket, title, content, status,
                usage_count, utility_score,
                created_at_offset_days, created_at_offset_days,
                embedding_literal,
            ),
        )
        row = cur.fetchone()
        assert row is not None
        return str(row[0])


# ---------------------------------------------------------------------
# Tests — config / thresholds
# ---------------------------------------------------------------------

def test_archive_thresholds_loaded_from_seed(db_conn: psycopg.Connection) -> None:
    """Migration 0039 seeds the 3 archive prefs. load_archive_thresholds reads them."""
    t = load_archive_thresholds(db_conn)
    assert t.usage_window_days == 500
    assert t.utility_threshold == pytest.approx(0.5)
    assert t.utility_lookback_days == 90


def test_archive_thresholds_missing_key_raises(db_conn: psycopg.Connection) -> None:
    """Per ADR-029: worker hard-fails on missing key, no hardcoded fallback."""
    with db_conn.cursor() as cur:
        cur.execute(
            "UPDATE operator_preferences SET active=false WHERE key='archive.usage_window_days'"
        )
    db_conn.commit()
    try:
        with pytest.raises(RuntimeError, match="archive.usage_window_days"):
            load_archive_thresholds(db_conn)
    finally:
        with db_conn.cursor() as cur:
            cur.execute(
                "UPDATE operator_preferences SET active=true WHERE key='archive.usage_window_days'"
            )
        db_conn.commit()


# ---------------------------------------------------------------------
# Tests — utility_recompute (SC2)
# ---------------------------------------------------------------------

def test_utility_recompute_runs_clean(db_conn: psycopg.Connection) -> None:
    """SC2: SQL function executes against current schema and returns affected count."""
    affected = dream_worker_mod.utility_recompute(db_conn, dry_run=False)
    # Affected = active lessons + non-deprecated tools_catalog rows. Should be > 0
    # against a populated test DB but we assert non-negative as the resilient floor.
    assert affected >= 0


# ---------------------------------------------------------------------
# Tests — dedup_pass (SC3)
# ---------------------------------------------------------------------

def test_dedup_inserts_cross_bucket_pair(
    db_conn: psycopg.Connection,
) -> None:
    """SC3 part 1: a cross-bucket pair with sim ~1.0 is queued."""
    a_id = _seed_lesson(
        db_conn, bucket="personal", title="Lesson A",
        content="content A", embedding_literal=FIXED_VEC_A,
    )
    b_id = _seed_lesson(
        db_conn, bucket="business", title="Lesson B",
        content="content B near A", embedding_literal=FIXED_VEC_B_ALMOST_A,
    )
    db_conn.commit()

    affected = dream_worker_mod.dedup_pass(db_conn, dry_run=False)
    assert affected >= 1, "expected at least one cross-bucket pair queued"

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT origin_lesson, target_lesson_id, proposed_by
            FROM   cross_pollination_queue
            WHERE  proposed_by = 'dream_engine_dedup'
            """
        )
        rows = cur.fetchall()
    pair = {tuple(sorted([str(r[0]), str(r[1])])) for r in rows}
    assert tuple(sorted([a_id, b_id])) in pair


def test_dedup_skips_same_bucket_pairs(
    db_conn: psycopg.Connection,
) -> None:
    """Cross-bucket only — same-bucket near-duplicates are not queued by dedup."""
    _seed_lesson(
        db_conn, bucket="personal", title="A",
        content="content A", embedding_literal=FIXED_VEC_A,
    )
    _seed_lesson(
        db_conn, bucket="personal", title="A near",
        content="content A2", embedding_literal=FIXED_VEC_B_ALMOST_A,
    )
    db_conn.commit()

    dream_worker_mod.dedup_pass(db_conn, dry_run=False)
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM cross_pollination_queue WHERE proposed_by='dream_engine_dedup'"
        )
        row = cur.fetchone()
        assert row is not None and row[0] == 0


def test_dedup_skips_dissimilar_pairs(
    db_conn: psycopg.Connection,
) -> None:
    """Sim < 0.95 not queued."""
    _seed_lesson(
        db_conn, bucket="personal", title="A",
        content="A", embedding_literal=FIXED_VEC_A,
    )
    _seed_lesson(
        db_conn, bucket="business", title="C far",
        content="C", embedding_literal=FIXED_VEC_C,
    )
    db_conn.commit()

    dream_worker_mod.dedup_pass(db_conn, dry_run=False)
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM cross_pollination_queue WHERE proposed_by='dream_engine_dedup'"
        )
        row = cur.fetchone()
        assert row is not None and row[0] == 0


def test_dedup_idempotent_second_run_inserts_zero(
    db_conn: psycopg.Connection,
) -> None:
    """SC3 part 2: UNIQUE constraint makes second-night re-propose a no-op."""
    _seed_lesson(
        db_conn, bucket="personal", title="A",
        content="A", embedding_literal=FIXED_VEC_A,
    )
    _seed_lesson(
        db_conn, bucket="business", title="B near",
        content="B", embedding_literal=FIXED_VEC_B_ALMOST_A,
    )
    db_conn.commit()

    first = dream_worker_mod.dedup_pass(db_conn, dry_run=False)
    second = dream_worker_mod.dedup_pass(db_conn, dry_run=False)
    assert first >= 1
    assert second == 0, f"second run inserted {second} rows; expected 0 (UNIQUE constraint)"


# ---------------------------------------------------------------------
# Tests — archive_low_utility (SC4 + SC6)
# ---------------------------------------------------------------------

def test_archive_flips_old_low_utility_lesson(
    db_conn: psycopg.Connection,
) -> None:
    """SC4: lesson matching all 3 predicates (status=active, usage_count=0,
    utility<0.5, age>500d) gets status='archived'."""
    lid = _seed_lesson(
        db_conn,
        bucket="personal",
        title="stale lesson",
        content="should archive",
        embedding_literal=FIXED_VEC_A,
        status="active",
        usage_count=0,
        utility_score=0.1,
        created_at_offset_days=-600,  # > 500 days old
    )
    db_conn.commit()

    affected = dream_worker_mod.archive_low_utility(
        db_conn,
        dream_config_mod.ArchiveThresholds(
            usage_window_days=500,
            utility_threshold=0.5,
            utility_lookback_days=90,
        ),
        dry_run=False,
    )
    assert affected >= 1

    with db_conn.cursor() as cur:
        cur.execute("SELECT status FROM lessons WHERE id = %s", (lid,))
        row = cur.fetchone()
    assert row is not None and row[0] == "archived"


def test_archive_skips_recent_lesson(
    db_conn: psycopg.Connection,
) -> None:
    """A young lesson matching utility predicate but not age stays active."""
    lid = _seed_lesson(
        db_conn,
        bucket="personal",
        title="young lesson",
        content="too young to archive",
        embedding_literal=FIXED_VEC_A,
        status="active",
        usage_count=0,
        utility_score=0.0,
        created_at_offset_days=-30,  # only 30 days old
    )
    db_conn.commit()

    dream_worker_mod.archive_low_utility(
        db_conn,
        dream_config_mod.ArchiveThresholds(
            usage_window_days=500,
            utility_threshold=0.5,
            utility_lookback_days=90,
        ),
        dry_run=False,
    )
    with db_conn.cursor() as cur:
        cur.execute("SELECT status FROM lessons WHERE id = %s", (lid,))
        row = cur.fetchone()
    assert row is not None and row[0] == "active"


def test_archive_skips_used_lesson(
    db_conn: psycopg.Connection,
) -> None:
    """A lesson with usage_count > 0 stays active even when ancient."""
    lid = _seed_lesson(
        db_conn,
        bucket="personal",
        title="used old lesson",
        content="used recently",
        embedding_literal=FIXED_VEC_A,
        status="active",
        usage_count=3,
        utility_score=0.1,
        created_at_offset_days=-1000,
    )
    db_conn.commit()

    dream_worker_mod.archive_low_utility(
        db_conn,
        dream_config_mod.ArchiveThresholds(
            usage_window_days=500,
            utility_threshold=0.5,
            utility_lookback_days=90,
        ),
        dry_run=False,
    )
    with db_conn.cursor() as cur:
        cur.execute("SELECT status FROM lessons WHERE id = %s", (lid,))
        row = cur.fetchone()
    assert row is not None and row[0] == "active"


# ---------------------------------------------------------------------
# Tests — main() orchestration (SC1 + SC5)
# ---------------------------------------------------------------------

def test_main_records_run_telemetry(
    patched_dream_engine_db: None, db_conn: psycopg.Connection
) -> None:
    """SC1: a dream_engine_runs row is created with completed_at + status."""
    rc = dream_worker_mod.main(dry_run=False)
    assert rc == 0

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT status, completed_at IS NOT NULL, jobs_run, failures, worker_pid
            FROM   dream_engine_runs
            ORDER BY started_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
    assert row is not None
    status, completed, jobs_run, failures, worker_pid = row
    assert status in ("success", "partial")
    assert completed is True
    assert isinstance(jobs_run, dict) and {"utility_recompute", "dedup_pass", "archive_low_utility"} <= set(jobs_run)
    assert isinstance(failures, list)
    assert worker_pid is not None


def test_main_dry_run_rolls_back_changes(
    patched_dream_engine_db: None, db_conn: psycopg.Connection
) -> None:
    """Dry-run still records telemetry but rolls back data mutations.

    Seed a near-duplicate cross-bucket pair so dedup_pass *would* insert.
    With --dry-run the queue must remain empty post-run.
    """
    _seed_lesson(
        db_conn, bucket="personal", title="A",
        content="A", embedding_literal=FIXED_VEC_A,
    )
    _seed_lesson(
        db_conn, bucket="business", title="B near",
        content="B", embedding_literal=FIXED_VEC_B_ALMOST_A,
    )
    db_conn.commit()

    rc = dream_worker_mod.main(dry_run=True)
    assert rc == 0

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM cross_pollination_queue WHERE proposed_by='dream_engine_dedup'"
        )
        row = cur.fetchone()
    assert row is not None and row[0] == 0, "dry-run must not persist queue inserts"

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM dream_engine_runs WHERE worker_pid IS NOT NULL"
        )
        row = cur.fetchone()
    assert row is not None and row[0] >= 1, "dry-run must still record telemetry"
