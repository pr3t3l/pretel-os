"""Unit tests for `telegram_bot.session` (M5.D.3.1 session slice).

Mix of real-DB tests (`@pytest.mark.slow`) and a file-I/O test (no
marker — `tmp_path` only).

Each DB test scopes itself with a unique `client_origin` (e.g.
`telegram_test_<uuid8>`) so concurrent test runs don't collide and
the cleanup fixture only deletes rows the test created.
`conversation_sessions` is NOT in conftest's auto-truncate list, so
this isolation is mandatory.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterator
from uuid import uuid4

import psycopg
import pytest

from telegram_bot.session import (
    append_transcript,
    close_idle_sessions_sync,
    ensure_session_sync,
)

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    """Sync conn with autocommit=True so the function-under-test sees
    test-seeded rows in its own (separate) connection."""
    conn = psycopg.connect(TEST_DSN, autocommit=True)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def isolation_marker() -> Iterator[str]:
    """Yield a unique client_origin string for the test, then DELETE
    all conversation_sessions rows tagged with it on teardown."""
    marker = f"telegram_test_{uuid4().hex[:8]}"
    yield marker
    with psycopg.connect(TEST_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM conversation_sessions WHERE client_origin = %s",
                (marker,),
            )


# --- ensure_session_sync ---------------------------------------------------


@pytest.mark.slow
def test_ensure_session_inserts_first_time(
    db_conn: psycopg.Connection, isolation_marker: str
) -> None:
    session_id = ensure_session_sync(
        db_conn, operator_id="test_alfredo", client_origin=isolation_marker
    )
    assert isinstance(session_id, str) and len(session_id) == 36

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT turn_count, closed_at FROM conversation_sessions "
            "WHERE id = %s",
            (session_id,),
        )
        row = cur.fetchone()
    assert row is not None
    turn_count, closed_at = row
    assert turn_count == 1
    assert closed_at is None


@pytest.mark.slow
def test_ensure_session_updates_existing(
    db_conn: psycopg.Connection, isolation_marker: str
) -> None:
    first = ensure_session_sync(
        db_conn, operator_id="test_alfredo", client_origin=isolation_marker
    )
    # Tiny delay so last_seen_at advances measurably.
    time.sleep(0.05)
    second = ensure_session_sync(
        db_conn, operator_id="test_alfredo", client_origin=isolation_marker
    )

    assert first == second  # same open session reused

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT turn_count FROM conversation_sessions WHERE id = %s",
            (first,),
        )
        row = cur.fetchone()
    assert row is not None and row[0] == 2


@pytest.mark.slow
def test_ensure_session_opens_new_after_close(
    db_conn: psycopg.Connection, isolation_marker: str
) -> None:
    """When the existing session is closed, ensure_session opens a
    fresh row instead of reviving the old one."""
    first = ensure_session_sync(
        db_conn, operator_id="test_alfredo", client_origin=isolation_marker
    )
    with db_conn.cursor() as cur:
        cur.execute(
            "UPDATE conversation_sessions SET closed_at = now(), "
            "       close_reason = 'manual_test_close' "
            "WHERE id = %s",
            (first,),
        )

    second = ensure_session_sync(
        db_conn, operator_id="test_alfredo", client_origin=isolation_marker
    )
    assert second != first


# --- close_idle_sessions_sync ---------------------------------------------


@pytest.mark.slow
def test_close_idle_sessions_marks_old_sessions(
    db_conn: psycopg.Connection, isolation_marker: str
) -> None:
    session_id = ensure_session_sync(
        db_conn, operator_id="test_alfredo", client_origin=isolation_marker
    )
    # Backdate last_seen_at past the idle threshold.
    with db_conn.cursor() as cur:
        cur.execute(
            "UPDATE conversation_sessions "
            "SET last_seen_at = now() - interval '15 minutes' "
            "WHERE id = %s",
            (session_id,),
        )

    closed = close_idle_sessions_sync(
        db_conn, idle_minutes=10, client_origin=isolation_marker
    )
    assert closed == 1

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT closed_at, close_reason FROM conversation_sessions "
            "WHERE id = %s",
            (session_id,),
        )
        row = cur.fetchone()
    assert row is not None
    closed_at, reason = row
    assert closed_at is not None
    assert reason == "idle_10min"


@pytest.mark.slow
def test_close_idle_sessions_keeps_recent(
    db_conn: psycopg.Connection, isolation_marker: str
) -> None:
    session_id = ensure_session_sync(
        db_conn, operator_id="test_alfredo", client_origin=isolation_marker
    )
    closed = close_idle_sessions_sync(
        db_conn, idle_minutes=10, client_origin=isolation_marker
    )
    assert closed == 0

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT closed_at FROM conversation_sessions WHERE id = %s",
            (session_id,),
        )
        row = cur.fetchone()
    assert row is not None and row[0] is None


# --- append_transcript (file I/O, no DB) ----------------------------------


def test_append_transcript_writes_jsonl(tmp_path: Path) -> None:
    transcripts_dir = tmp_path
    session_id = "abc-123"
    append_transcript(transcripts_dir, session_id, "user", "primer mensaje")
    append_transcript(transcripts_dir, session_id, "user", "segundo")

    path = transcripts_dir / f"{session_id}.jsonl"
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    rows = [json.loads(line) for line in lines]
    assert [r["content"] for r in rows] == ["primer mensaje", "segundo"]
    assert all(r["role"] == "user" for r in rows)
    assert all("timestamp" in r for r in rows)
