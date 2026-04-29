"""Telemetry primitives for the Router orchestrator (spec §9, plan §6).

Phase D wiring per `phase_d_close.md` Q2 ("INSERT-early, UPDATE per
step"). `start_request()` creates the `routing_logs` row immediately
with placeholder values for the NOT-NULL columns lacking server-side
defaults (`classification='{}'`, `layers_loaded='{}'`,
`tokens_assembled_total=0`, `rag_expected=false`, `latency_ms=0`).
Each subsequent `log_*()` UPDATEs a slice. `log_completion()` is the
final UPDATE, called from the orchestrator's `try/finally` so it
always fires — even on crash, the row gets `degraded_mode=true` and a
`degraded_reason`.

Schema verification (2026-04-29 against `pretel_os_test`):
- `routing_logs` matches spec §9.1 column-for-column. No drift.
- `llm_calls` matches spec §9.2 column-for-column. `purpose` is the
  Postgres enum `llm_purpose`; the literal `'classification'` casts
  cleanly server-side.
- Both tables are `RANGE(created_at)` partitioned (Module 0X.A);
  inserts route transparently via the `now()` default.

Commit semantics: these functions DO NOT commit. The caller controls
transaction boundaries. Production callers (`router.py` via the MCP
server) should use `autocommit=True` so each step is durable across
crashes per Q2; integration tests use `autocommit=False` with rollback
at fixture teardown.

Each function wraps its SQL in `try/except psycopg.Error: pass` — per
spec §10, telemetry loss is acceptable; the user-facing response must
never fail because of a logging error.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from typing import Any

import psycopg

from .types import InvariantViolation, LayerBundle


def start_request(
    conn: psycopg.Connection,
    message: str,
    session_id: str | None,
    client_origin: str,
) -> str:
    """Generate a request_id, INSERT a placeholder row, return the id.

    `session_id` is accepted for symmetry with the orchestrator
    signature; it is NOT written to `routing_logs` (no column per spec
    §9.1). Sessions live in `conversation_sessions` and are joined by
    application logic, not by FK.

    Returns the generated UUID4 even if the INSERT fails — the caller
    can still pass it through the rest of the pipeline; subsequent
    `log_*` UPDATEs will simply hit zero rows.
    """
    request_id = str(uuid.uuid4())
    excerpt = message[:200]
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO routing_logs (
                    request_id, client_origin, message_excerpt,
                    classification, layers_loaded, tokens_assembled_total,
                    rag_expected, latency_ms
                )
                VALUES (
                    %s, %s, %s,
                    '{}'::jsonb, '{}'::text[], 0,
                    false, 0
                )
                """,
                (request_id, client_origin, excerpt),
            )
    except psycopg.Error:
        pass
    return request_id


def log_classification(
    conn: psycopg.Connection,
    request_id: str,
    classification: dict[str, Any],
    mode: str,
    llm_call_data: dict[str, Any] | None,
) -> None:
    """UPDATE `routing_logs.classification` + `classification_mode`.

    If `mode == 'llm'` and `llm_call_data is not None`, also INSERT
    one `llm_calls` row with the spec §9.2 columns. When the fallback
    classifier ran (`mode == 'fallback_rules'`), no `llm_calls` row is
    written — `routing_logs.classification_mode` is the only signal.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE routing_logs
                SET classification = %s::jsonb,
                    classification_mode = %s
                WHERE request_id = %s
                """,
                (json.dumps(classification), mode, request_id),
            )
    except psycopg.Error:
        pass

    if mode != "llm" or llm_call_data is None:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO llm_calls (
                    request_id, purpose, provider, model,
                    input_tokens, output_tokens, cache_read_tokens,
                    cost_usd, latency_ms, success, error,
                    client_id, project
                )
                VALUES (
                    %s, 'classification', %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    NULL, %s
                )
                """,
                (
                    request_id,
                    llm_call_data.get("provider", "unknown"),
                    llm_call_data.get("model", "unknown"),
                    llm_call_data.get("input_tokens", 0),
                    llm_call_data.get("output_tokens", 0),
                    llm_call_data.get("cache_read_tokens", 0),
                    llm_call_data.get("cost_usd", 0),
                    llm_call_data.get("latency_ms"),
                    llm_call_data.get("success", True),
                    llm_call_data.get("error"),
                    llm_call_data.get("project"),
                ),
            )
    except psycopg.Error:
        pass


def log_layers(
    conn: psycopg.Connection,
    request_id: str,
    bundle: LayerBundle,
) -> None:
    """UPDATE `routing_logs` with layer-shaped telemetry.

    Populated columns: `layers_loaded` (text[] of names where
    `loaded=True`), `tokens_assembled_total` (sum across loaded
    layers), `tokens_per_layer` (JSONB mapping for loaded layers),
    `over_budget_layers` (text[] from `BundleMetadata`).
    """
    layers_loaded = [layer.layer for layer in bundle.layers if layer.loaded]
    tokens_per_layer = {
        layer.layer: layer.token_count
        for layer in bundle.layers
        if layer.loaded
    }
    total = sum(tokens_per_layer.values())
    over_budget = list(bundle.metadata.over_budget_layers)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE routing_logs
                SET layers_loaded = %s,
                    tokens_assembled_total = %s,
                    tokens_per_layer = %s::jsonb,
                    over_budget_layers = %s
                WHERE request_id = %s
                """,
                (
                    layers_loaded,
                    total,
                    json.dumps(tokens_per_layer),
                    over_budget,
                    request_id,
                ),
            )
    except psycopg.Error:
        pass


def log_rag(
    conn: psycopg.Connection,
    request_id: str,
    rag_expected: bool,
    rag_executed: bool,
    lessons_returned: int,
    tools_returned: int,
) -> None:
    """UPDATE `routing_logs` RAG-signal columns (spec §9.1)."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE routing_logs
                SET rag_expected = %s,
                    rag_executed = %s,
                    lessons_returned = %s,
                    tools_returned = %s
                WHERE request_id = %s
                """,
                (
                    rag_expected,
                    rag_executed,
                    lessons_returned,
                    tools_returned,
                    request_id,
                ),
            )
    except psycopg.Error:
        pass


def log_conflicts(
    conn: psycopg.Connection,
    request_id: str,
    violations: list[InvariantViolation],
) -> None:
    """UPDATE `routing_logs.source_conflicts` with the JSON-serialized
    list of violations from Phase C. Empty `violations` writes `'[]'`,
    which Phase D audit queries treat as "no conflict" cleanly.
    """
    payload = json.dumps([asdict(v) for v in violations])
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE routing_logs
                SET source_conflicts = %s::jsonb
                WHERE request_id = %s
                """,
                (payload, request_id),
            )
    except psycopg.Error:
        pass


def log_completion(
    conn: psycopg.Connection,
    request_id: str,
    degraded_mode: bool,
    degraded_reason: str | None,
    latency_ms: int,
) -> None:
    """Final UPDATE — always called from the orchestrator's
    `try/finally`. Writes the partial-row signal (`degraded_mode`,
    `degraded_reason`) and the end-to-end `latency_ms`.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE routing_logs
                SET degraded_mode = %s,
                    degraded_reason = %s,
                    latency_ms = %s
                WHERE request_id = %s
                """,
                (degraded_mode, degraded_reason, latency_ms, request_id),
            )
    except psycopg.Error:
        pass
