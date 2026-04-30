"""End-to-end tests for the Router pipeline (Phase D.4.2).

Calls `router.get_context()` against live infrastructure: LiteLLM
classifier proxy, Postgres test DB, OpenAI embeddings. 6 tests per
phase_d_close.md D.4.2; total cost ~$0.10–0.30 per full run.

Marked `@pytest.mark.slow` per repo convention. Skip-guards mirror
`test_classifier_eval`: LiteLLM proxy reachable on 127.0.0.1:4000
AND `LITELLM_MASTER_KEY` available in `~/.env.litellm`.

Each test additionally captures any Phase C invariant violations the
detector flags against real bundle content and prints them to stdout
so the operator can evaluate them as legitimate signal vs false
positives. Printing is non-blocking — tests pass regardless of the
violations count.
"""
from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any, Iterator

import jsonschema
import psycopg
import pytest

from mcp_server.router.cache import LayerBundleCache
from mcp_server.router.router import get_context

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = Path(__file__).parent / "context_bundle_schema.json"


def _proxy_reachable(
    host: str = "127.0.0.1", port: int = 4000, timeout: float = 0.5
) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _real_litellm_key() -> str | None:
    path = os.path.expanduser("~/.env.litellm")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for line in f:
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def _print_violations(
    capsys: pytest.CaptureFixture[str], test_name: str, result: dict[str, Any]
) -> None:
    """Surface Phase C source_conflicts to the operator for evaluation."""
    violations = result.get("source_conflicts") or []
    with capsys.disabled():
        print(
            f"\n[D.4.2 violations] {test_name}: "
            f"{len(violations)} flagged (mode={result.get('classification_mode')}, "
            f"degraded={result.get('degraded_mode')})"
        )
        for v in violations:
            print(
                f"  - {v.get('invariant_id')} @ {v.get('layer')}: "
                f"{v.get('evidence')}"
            )


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


@pytest.fixture
def schema() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(SCHEMA_PATH.read_text())
    return loaded


@pytest.fixture(autouse=True)
def _litellm_key(monkeypatch: pytest.MonkeyPatch) -> None:
    if not _proxy_reachable():
        pytest.skip("LiteLLM proxy not reachable on 127.0.0.1:4000")
    key = _real_litellm_key()
    if not key:
        pytest.skip("LITELLM_MASTER_KEY not present in ~/.env.litellm")
    monkeypatch.setenv("LITELLM_API_KEY", key)


def _assert_routing_log_row(
    conn: psycopg.Connection, request_id: str
) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT classification_mode, layers_loaded, latency_ms, "
            "       source_conflicts, degraded_mode "
            "FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None, f"no routing_logs row for request_id={request_id}"
    return {
        "classification_mode": row[0],
        "layers_loaded": row[1],
        "latency_ms": row[2],
        "source_conflicts": row[3],
        "degraded_mode": row[4],
    }


def _assert_schema_valid(result: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate against context_bundle_schema.json post-JSON-roundtrip."""
    jsonschema.validate(instance=json.loads(json.dumps(result)), schema=schema)


def _assert_awareness_keys(result: dict[str, Any]) -> None:
    """Module 7.5 RUN 2 contract — Router injects per-bucket awareness.

    Both keys must always be present on the response (the schema
    enforces it too). Both must be lists. Counts may be zero — the
    fixtures here run against the test DB which has no projects, and
    `available_skills` reflects whatever the test DB's tools_catalog
    holds for the classified bucket.
    """
    assert "available_skills" in result, sorted(result.keys())
    assert "active_projects" in result, sorted(result.keys())
    assert isinstance(result["available_skills"], list)
    assert isinstance(result["active_projects"], list)


@pytest.mark.slow
async def test_n8n_debug_query(
    db_conn: psycopg.Connection,
    cache: LayerBundleCache,
    schema: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = await get_context(
        conn=db_conn,
        message="help me debug my n8n batching",
        session_id="sess-e2e-1",
        client_origin="claude_code",
        repo_root=REPO_ROOT,
        cache=cache,
    )
    _print_violations(capsys, "test_n8n_debug_query", result)
    _assert_schema_valid(result, schema)
    _assert_awareness_keys(result)
    assert result["classification"]["bucket"] == "business"
    assert result["classification"]["complexity"] in ("MEDIUM", "HIGH")
    assert result["latency_ms"] > 0

    rl = _assert_routing_log_row(db_conn, result["request_id"])
    assert rl["classification_mode"] in ("llm", "fallback_rules")
    assert isinstance(rl["source_conflicts"], list)
    assert rl["latency_ms"] > 0

    if rl["classification_mode"] == "llm":
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM llm_calls WHERE request_id = %s",
                (result["request_id"],),
            )
            llm_row = cur.fetchone()
            assert llm_row is not None and llm_row[0] == 1


@pytest.mark.slow
async def test_known_bucket_no_project(
    db_conn: psycopg.Connection,
    cache: LayerBundleCache,
    schema: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = await get_context(
        conn=db_conn,
        message="what's the latest pretel-os decision?",
        session_id="sess-e2e-2",
        client_origin="claude_code",
        repo_root=REPO_ROOT,
        cache=cache,
    )
    _print_violations(capsys, "test_known_bucket_no_project", result)
    _assert_schema_valid(result, schema)
    _assert_awareness_keys(result)
    assert result["classification"]["bucket"] == "business"
    assert result["latency_ms"] > 0
    rl = _assert_routing_log_row(db_conn, result["request_id"])
    assert isinstance(rl["source_conflicts"], list)


@pytest.mark.slow
async def test_ambiguous_message(
    db_conn: psycopg.Connection,
    cache: LayerBundleCache,
    schema: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = await get_context(
        conn=db_conn,
        message="what should I do?",
        session_id="sess-e2e-3",
        client_origin="claude_code",
        repo_root=REPO_ROOT,
        cache=cache,
    )
    _print_violations(capsys, "test_ambiguous_message", result)
    _assert_schema_valid(result, schema)
    _assert_awareness_keys(result)
    assert result["classification_mode"] in ("llm", "fallback_rules")
    assert result["latency_ms"] > 0


@pytest.mark.slow
async def test_greeting_low_complexity(
    db_conn: psycopg.Connection,
    cache: LayerBundleCache,
    schema: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = await get_context(
        conn=db_conn,
        message="hi",
        session_id="sess-e2e-4",
        client_origin="claude_code",
        repo_root=REPO_ROOT,
        cache=cache,
    )
    _print_violations(capsys, "test_greeting_low_complexity", result)
    _assert_schema_valid(result, schema)
    _assert_awareness_keys(result)
    assert result["classification"]["complexity"] == "LOW"
    assert result["tools_recommended"] == []
    # L4 must NOT load on LOW complexity (spec §5.2)
    l4 = next(
        layer for layer in result["bundle"]["layers"] if layer["layer"] == "L4"
    )
    assert l4["loaded"] is False


@pytest.mark.slow
async def test_high_complexity_recommendation(
    db_conn: psycopg.Connection,
    cache: LayerBundleCache,
    schema: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = await get_context(
        conn=db_conn,
        message="recommend a database architecture for my new freelance project",
        session_id="sess-e2e-5",
        client_origin="claude_code",
        repo_root=REPO_ROOT,
        cache=cache,
    )
    _print_violations(capsys, "test_high_complexity_recommendation", result)
    _assert_schema_valid(result, schema)
    _assert_awareness_keys(result)
    assert result["classification"]["complexity"] in ("MEDIUM", "HIGH")
    assert result["latency_ms"] > 0
    # tools_recommended is best-effort: tools_catalog may be empty in
    # the test DB. Verify the field is at least the right shape.
    assert isinstance(result["tools_recommended"], list)


@pytest.mark.slow
async def test_scout_query_abstract(
    db_conn: psycopg.Connection,
    cache: LayerBundleCache,
    schema: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = await get_context(
        conn=db_conn,
        message="how is my assembly station tracking?",
        session_id="sess-e2e-6",
        client_origin="claude_code",
        repo_root=REPO_ROOT,
        cache=cache,
    )
    _print_violations(capsys, "test_scout_query_abstract", result)
    _assert_schema_valid(result, schema)
    _assert_awareness_keys(result)
    # bucket may be 'scout' (best case), 'business' (LLM picks freelance
    # association), or null (rules-only fallback). All three respect the
    # CONSTITUTION §3 "abstract patterns only" rule because the message
    # contains no employer/vendor identifiers.
    assert result["classification"]["bucket"] in ("scout", "business", None)
    assert result["latency_ms"] > 0
