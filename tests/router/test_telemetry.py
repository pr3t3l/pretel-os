"""Unit tests for `mcp_server.router.telemetry` (Phase D.4.1).

Pure-DB tests — no LLM, no embeddings. Verifies the six telemetry
functions write the spec §9.1 / §9.2 columns correctly. Each test
uses a sync `psycopg.Connection` with `autocommit=False`; the fixture
rolls back at teardown so the test DB stays clean.

Cost: $0. Marked `@pytest.mark.slow` per repo convention for any test
that hits a real DB (pytest.ini lets the operator skip with
`pytest -m "not slow"`).
"""
from __future__ import annotations

import json
from typing import Iterator

import psycopg
import pytest

from mcp_server.router.telemetry import (
    log_classification,
    log_completion,
    log_conflicts,
    log_layers,
    log_rag,
    start_request,
)
from mcp_server.router.types import (
    BundleMetadata,
    ContextBlock,
    InvariantViolation,
    LayerBundle,
    LayerContent,
)

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


def _make_bundle(
    layer_token_counts: dict[str, int] | None = None,
    over_budget: tuple[str, ...] = (),
) -> LayerBundle:
    """Build a valid LayerBundle for telemetry tests."""
    counts = layer_token_counts or {}
    layers = []
    for name in ("L0", "L1", "L2", "L3", "L4"):
        tc = counts.get(name, 0)
        loaded = name in counts
        if tc > 0:
            block = ContextBlock(
                source=f"src:{name}",
                content="x",
                row_count=None,
                token_count=tc,
            )
            layers.append(
                LayerContent(layer=name, blocks=(block,), token_count=tc, loaded=loaded)
            )
        else:
            layers.append(
                LayerContent(layer=name, blocks=(), token_count=0, loaded=loaded)
            )
    total = sum(layer.token_count for layer in layers)
    metadata = BundleMetadata(
        bucket="business",
        project=None,
        classifier_hash="test",
        total_tokens=total,
        assembly_latency_ms=10,
        cache_hit=False,
        over_budget_layers=over_budget,
    )
    return LayerBundle(layers=tuple(layers), metadata=metadata)


@pytest.mark.slow
def test_start_request_creates_row(db_conn: psycopg.Connection) -> None:
    request_id = start_request(
        db_conn, "test message" * 50, session_id="sess-1", client_origin="claude_code"
    )
    assert len(request_id) == 36

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT request_id, message_excerpt, client_origin "
            "FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    rid, excerpt, origin = row
    assert rid == request_id
    assert len(excerpt) == 200
    assert origin == "claude_code"


@pytest.mark.slow
def test_log_classification_updates_row(db_conn: psycopg.Connection) -> None:
    request_id = start_request(db_conn, "msg", None, "claude_code")
    classification = {
        "bucket": "personal",
        "project": None,
        "skill": None,
        "complexity": "MEDIUM",
        "needs_lessons": False,
        "confidence": 0.8,
    }
    log_classification(db_conn, request_id, classification, "fallback_rules", None)

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT classification, classification_mode "
            "FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    cls, mode = row
    assert cls["bucket"] == "personal"
    assert cls["complexity"] == "MEDIUM"
    assert mode == "fallback_rules"


@pytest.mark.slow
def test_log_classification_llm_mode_writes_llm_calls(
    db_conn: psycopg.Connection,
) -> None:
    request_id = start_request(db_conn, "msg", None, "claude_code")
    classification = {"bucket": "business", "complexity": "HIGH"}
    llm_call_data = {
        "provider": "anthropic",
        "model": "claude-haiku-4-5",
        "input_tokens": 850,
        "output_tokens": 110,
        "cache_read_tokens": 0,
        "cost_usd": 0.001,
        "latency_ms": 420,
        "success": True,
        "error": None,
        "project": "business",
    }
    log_classification(db_conn, request_id, classification, "llm", llm_call_data)

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT model, input_tokens, output_tokens, cost_usd, success "
            "FROM llm_calls WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    model, in_tok, out_tok, cost, success = row
    assert model == "claude-haiku-4-5"
    assert in_tok == 850
    assert out_tok == 110
    assert float(cost) == 0.001
    assert success is True


@pytest.mark.slow
def test_log_classification_fallback_no_llm_calls(
    db_conn: psycopg.Connection,
) -> None:
    request_id = start_request(db_conn, "msg", None, "claude_code")
    log_classification(
        db_conn, request_id, {"bucket": None}, "fallback_rules", None
    )

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM llm_calls WHERE request_id = %s", (request_id,)
        )
        row = cur.fetchone()
    assert row is not None and row[0] == 0


@pytest.mark.slow
def test_log_layers_populates_token_columns(db_conn: psycopg.Connection) -> None:
    request_id = start_request(db_conn, "msg", None, "claude_code")
    bundle = _make_bundle(
        layer_token_counts={"L0": 50, "L1": 1200, "L4": 2000},
        over_budget=("L1",),
    )
    log_layers(db_conn, request_id, bundle)

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT layers_loaded, tokens_assembled_total, tokens_per_layer, "
            "       over_budget_layers "
            "FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    layers_loaded, total, tpl, over_budget = row
    assert sorted(layers_loaded) == ["L0", "L1", "L4"]
    assert total == 3250
    assert tpl == {"L0": 50, "L1": 1200, "L4": 2000}
    assert over_budget == ["L1"]


@pytest.mark.slow
def test_log_conflicts_serializes_violations(db_conn: psycopg.Connection) -> None:
    request_id = start_request(db_conn, "msg", None, "claude_code")
    violations = [
        InvariantViolation(
            layer="L4",
            source="lessons:abc",
            invariant_id="agent_rule_no_guessing",
            evidence="matched 'guess mcp tool params' at pos 8",
            severity="critical",
        ),
        InvariantViolation(
            layer="L1",
            source="layer:L1",
            invariant_id="budget_ceiling",
            evidence="layer L1 token_count=3500 exceeds ceiling 3000 (slack 5%)",
            severity="normal",
        ),
    ]
    log_conflicts(db_conn, request_id, violations)

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT source_conflicts FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    conflicts = row[0]
    assert isinstance(conflicts, list)
    assert len(conflicts) == 2
    assert conflicts[0]["invariant_id"] == "agent_rule_no_guessing"
    assert conflicts[0]["severity"] == "critical"
    assert conflicts[1]["invariant_id"] == "budget_ceiling"
    assert conflicts[1]["severity"] == "normal"


@pytest.mark.slow
def test_log_completion_always_fires(db_conn: psycopg.Connection) -> None:
    """Simulate a crash after log_classification, verify log_completion
    still wrote degraded_mode + latency_ms (the try/finally contract)."""
    request_id = start_request(db_conn, "msg", None, "claude_code")
    log_classification(
        db_conn, request_id, {"bucket": "business"}, "llm", None
    )
    # Simulate a crash by jumping straight to log_completion (skipping
    # log_layers / log_rag / log_conflicts).
    log_completion(
        db_conn, request_id,
        degraded_mode=True,
        degraded_reason="simulated_crash_after_classification",
        latency_ms=512,
    )

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT degraded_mode, degraded_reason, latency_ms "
            "FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    degraded, reason, latency = row
    assert degraded is True
    assert reason == "simulated_crash_after_classification"
    assert latency == 512


@pytest.mark.slow
def test_log_rag_populates_columns(db_conn: psycopg.Connection) -> None:
    request_id = start_request(db_conn, "msg", None, "claude_code")
    log_rag(
        db_conn, request_id,
        rag_expected=True, rag_executed=True,
        lessons_returned=4, tools_returned=2,
    )

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT rag_expected, rag_executed, lessons_returned, tools_returned "
            "FROM routing_logs WHERE request_id = %s",
            (request_id,),
        )
        row = cur.fetchone()
    assert row is not None
    rag_exp, rag_exec, lessons, tools = row
    assert rag_exp is True
    assert rag_exec is True
    assert lessons == 4
    assert tools == 2
