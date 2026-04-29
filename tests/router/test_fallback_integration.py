"""Fallback-path integration tests (Phase D.4.3, legacy E.2.2).

Mock LiteLLM as failing (5 distinct failure modes from spec §10) and
verify the orchestrator falls through to `fallback_classify`,
`routing_logs.classification_mode='fallback_rules'`, and zero
`llm_calls` rows are written for that request_id.

Cost: $0 — `classify` is patched to raise; no real LLM call.
Marked `@pytest.mark.slow` per repo convention because the test
exercises the live `pretel_os_test` DB.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import psycopg
import pytest

from mcp_server.router.cache import LayerBundleCache
from mcp_server.router.exceptions import (
    ClassifierParseError,
    ClassifierSchemaError,
    ClassifierTimeout,
    ClassifierTransportError,
)
from mcp_server.router.router import get_context

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"
REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def cache() -> LayerBundleCache:
    return LayerBundleCache(max_entries=8)


async def _run_with_failure(
    db_conn: psycopg.Connection,
    cache: LayerBundleCache,
    failure: Exception,
) -> dict[str, object]:
    with patch(
        "mcp_server.router.router.classify",
        side_effect=failure,
    ):
        return await get_context(
            conn=db_conn,
            message="help me debug my n8n batching",
            session_id="sess-fallback",
            client_origin="claude_code",
            repo_root=REPO_ROOT,
            cache=cache,
        )


def _assert_fallback_path(
    db_conn: psycopg.Connection, result: dict[str, object]
) -> None:
    assert result["classification_mode"] == "fallback_rules"
    assert result["degraded_mode"] is True
    request_id = result["request_id"]

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT classification_mode FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] == "fallback_rules"

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM llm_calls WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None and row[0] == 0, (
        f"unexpected llm_calls row(s): {row}"
    )


@pytest.mark.slow
async def test_fallback_on_litellm_timeout(
    db_conn: psycopg.Connection, cache: LayerBundleCache
) -> None:
    result = await _run_with_failure(
        db_conn, cache, ClassifierTimeout("simulated timeout")
    )
    _assert_fallback_path(db_conn, result)


@pytest.mark.slow
async def test_fallback_on_connection_refused(
    db_conn: psycopg.Connection, cache: LayerBundleCache
) -> None:
    result = await _run_with_failure(
        db_conn, cache, ClassifierTransportError("connection refused")
    )
    _assert_fallback_path(db_conn, result)


@pytest.mark.slow
async def test_fallback_on_5xx(
    db_conn: psycopg.Connection, cache: LayerBundleCache
) -> None:
    result = await _run_with_failure(
        db_conn, cache, ClassifierTransportError("provider 503")
    )
    _assert_fallback_path(db_conn, result)


@pytest.mark.slow
async def test_fallback_on_malformed_json(
    db_conn: psycopg.Connection, cache: LayerBundleCache
) -> None:
    result = await _run_with_failure(
        db_conn, cache, ClassifierParseError(
            "not valid JSON", raw_response=None, telemetry=None
        )
    )
    _assert_fallback_path(db_conn, result)


@pytest.mark.slow
async def test_fallback_on_schema_invalid(
    db_conn: psycopg.Connection, cache: LayerBundleCache
) -> None:
    result = await _run_with_failure(
        db_conn, cache, ClassifierSchemaError(
            "bucket invalid", parsed_response=None, telemetry=None
        )
    )
    _assert_fallback_path(db_conn, result)
