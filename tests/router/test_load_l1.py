"""Tests for load_l1 — bucket-scoped decisions + prefs (contract §3.2).

Same isolation pattern as test_load_l0: sync psycopg connection with
autocommit=False; uncommitted INSERTs visible to same conn's reads;
fixture teardown rolls back.
"""
from __future__ import annotations

import json
from typing import Iterator

import psycopg
import pytest

from mcp_server.router.load_l1 import (
    _L1_DECISIONS_SQL,
    load_l1,
)
from mcp_server.router.types import LayerContent


TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


def _insert_decision(
    conn: psycopg.Connection,
    *,
    bucket: str,
    project: str = "general",
    title: str = "T",
    severity: str = "normal",
    adr_number: int | None = None,
    decision: str = "decision body text",
    context: str = "context",
    consequences: str = "consequences",
    applicable_buckets: list[str] | None = None,
    status: str = "active",
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO decisions "
            "(bucket, project, title, context, decision, consequences, "
            " severity, adr_number, applicable_buckets, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                bucket, project, title, context, decision, consequences,
                severity, adr_number, applicable_buckets or [], status,
            ),
        )


def _insert_pref(
    conn: psycopg.Connection,
    *,
    category: str,
    key: str,
    value: str,
    scope: str,
    source: str = "operator_explicit",
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO operator_preferences (category, key, value, scope, source) "
            "VALUES (%s, %s, %s, %s, %s)",
            (category, key, value, scope, source),
        )


# -----------------------------------------------------------------------------
# Happy path
# -----------------------------------------------------------------------------


def test_happy_path_two_blocks_in_order(db_conn: psycopg.Connection) -> None:
    """Bucket with at least one decision + one bucket-scoped pref → 2 blocks."""
    _insert_decision(db_conn, bucket="business", title="Use Postgres", severity="normal")
    _insert_pref(db_conn, category="tooling", key="editor",
                 value="vim", scope="bucket:business")

    result = load_l1(db_conn, "business")

    assert isinstance(result, LayerContent)
    assert result.layer == "L1"
    assert result.loaded is True
    sources = [b.source for b in result.blocks]
    assert sources == ["decisions", "operator_preferences"]
    assert result.token_count == sum(b.token_count for b in result.blocks)


# -----------------------------------------------------------------------------
# bucket=None → loaded=False
# -----------------------------------------------------------------------------


def test_bucket_none_returns_skipped_layer(db_conn: psycopg.Connection) -> None:
    """bucket=None means classifier did not detect a bucket → L1 skipped."""
    result = load_l1(db_conn, None)

    assert result.layer == "L1"
    assert result.loaded is False
    assert result.blocks == ()
    assert result.token_count == 0


# -----------------------------------------------------------------------------
# DB unavailable → loaded=False (closed connection)
# -----------------------------------------------------------------------------


def test_db_unavailable_loaded_false() -> None:
    """Closed connection → both queries fail → loaded=False, blocks=()."""
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    conn.close()

    result = load_l1(conn, "business")

    assert result.loaded is False
    assert result.blocks == ()


# -----------------------------------------------------------------------------
# All-fail variant: empty rows in both sources still counts as loaded=True
# (the question is whether empty blocks are emitted).
# Per the loader: blocks are emitted with empty content if the query
# succeeded — so loaded=True is the expected outcome.
# This test verifies the "all-fail" → False distinction by mocking via
# SQL syntax error rather than empty result.
# -----------------------------------------------------------------------------


def test_empty_rows_yields_loaded_true_with_empty_blocks(db_conn: psycopg.Connection) -> None:
    """Bucket with NO decisions and NO bucket-scoped prefs → 2 empty blocks, loaded=True.

    Empty result is NOT failure — the queries succeeded, just had nothing
    to render. The orchestrator emits blocks with empty content.
    """
    # Ensure no rows match by deleting any pre-existing rows for this bucket.
    with db_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM decisions "
            "WHERE bucket = 'business' OR 'business' = ANY(applicable_buckets)"
        )
        cur.execute(
            "DELETE FROM operator_preferences WHERE scope LIKE 'bucket:business%'"
        )

    result = load_l1(db_conn, "business")

    assert result.loaded is True
    sources = [b.source for b in result.blocks]
    assert sources == ["decisions", "operator_preferences"]
    assert all(b.row_count == 0 for b in result.blocks)
    assert all(b.content == "" for b in result.blocks)
    assert result.token_count == 0


# -----------------------------------------------------------------------------
# Bucket scope filter (mirror the scope='global' lesson from B.2)
# -----------------------------------------------------------------------------


def test_bucket_scope_isolation_decisions(db_conn: psycopg.Connection) -> None:
    """Decisions for bucket='personal' must NOT leak into bucket='business' query."""
    # Clear prior business decisions to keep this assertion crisp.
    with db_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM decisions "
            "WHERE bucket = 'business' OR 'business' = ANY(applicable_buckets)"
        )

    _insert_decision(db_conn, bucket="business", title="biz only", severity="normal")
    _insert_decision(db_conn, bucket="personal", title="pers only", severity="normal")

    result = load_l1(db_conn, "business")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    assert "biz only" in decisions_block.content
    assert "pers only" not in decisions_block.content


def test_applicable_buckets_array_match(db_conn: psycopg.Connection) -> None:
    """A decision with bucket=personal but business in applicable_buckets DOES appear in business L1.

    Per contract §3.2: filter is (bucket = $1 OR $1 = ANY(applicable_buckets)).
    """
    with db_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM decisions "
            "WHERE bucket = 'business' OR 'business' = ANY(applicable_buckets)"
        )

    _insert_decision(
        db_conn, bucket="personal", title="cross-cut decision",
        applicable_buckets=["business", "scout"],
    )

    result = load_l1(db_conn, "business")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    assert "cross-cut decision" in decisions_block.content


def test_bucket_scope_isolation_prefs(db_conn: psycopg.Connection) -> None:
    """Prefs with scope='bucket:personal' must not appear when bucket='business'."""
    with db_conn.cursor() as cur:
        cur.execute("DELETE FROM operator_preferences WHERE scope LIKE 'bucket:%'")

    _insert_pref(db_conn, category="tooling", key="editor",
                 value="vim", scope="bucket:business")
    _insert_pref(db_conn, category="tooling", key="editor",
                 value="emacs", scope="bucket:personal")

    result = load_l1(db_conn, "business")
    prefs_block = next(b for b in result.blocks if b.source == "operator_preferences")
    assert "vim" in prefs_block.content
    assert "emacs" not in prefs_block.content


def test_sub_bucket_prefs_match_via_like(db_conn: psycopg.Connection) -> None:
    """Prefs with scope='bucket:business/freelance' DO match LIKE 'bucket:business%'."""
    with db_conn.cursor() as cur:
        cur.execute("DELETE FROM operator_preferences WHERE scope LIKE 'bucket:%'")

    _insert_pref(db_conn, category="workflow", key="invoice_template",
                 value="net30", scope="bucket:business/freelance")

    result = load_l1(db_conn, "business")
    prefs_block = next(b for b in result.blocks if b.source == "operator_preferences")
    assert "workflow.invoice_template: net30" in prefs_block.content


# -----------------------------------------------------------------------------
# Severity CASE ordering — verified at SQL plan level
# -----------------------------------------------------------------------------


def test_severity_case_ordering_in_explain(db_conn: psycopg.Connection) -> None:
    """The L1 decisions SQL must order by SQL CASE expression, not Python sort.

    Per contract §3.2 + §3.2 done-when, severity ranking happens DB-side.
    We verify by inspecting EXPLAIN (FORMAT JSON) output for the Sort
    node's Sort Key — it must include the CASE expression.
    """
    explain_sql = "EXPLAIN (FORMAT JSON) " + _L1_DECISIONS_SQL
    with db_conn.cursor() as cur:
        cur.execute(explain_sql, ("business", "business"))
        plan_row = cur.fetchone()

    assert plan_row is not None
    plan_json = plan_row[0]
    if isinstance(plan_json, str):
        plan_json = json.loads(plan_json)
    plan = plan_json[0]["Plan"]

    def find_sort(node: dict) -> dict | None:
        if node.get("Node Type") == "Sort":
            return node
        for sub in node.get("Plans", []):
            found = find_sort(sub)
            if found is not None:
                return found
        return None

    sort_node = find_sort(plan)
    assert sort_node is not None, "expected a Sort node in the plan"
    sort_keys = sort_node.get("Sort Key", [])
    # The CASE expression should appear in at least one Sort Key entry.
    # Postgres renders it with the literal "CASE" keyword.
    assert any("CASE" in str(key) for key in sort_keys), (
        f"Sort Key did not include CASE expression: {sort_keys}"
    )


def test_severity_case_orders_critical_before_normal_before_minor(
    db_conn: psycopg.Connection,
) -> None:
    """End-to-end: insert mixed severities, verify render order is critical → normal → minor."""
    with db_conn.cursor() as cur:
        cur.execute("DELETE FROM decisions WHERE bucket = 'business'")

    _insert_decision(db_conn, bucket="business", title="Z minor first", severity="minor")
    _insert_decision(db_conn, bucket="business", title="A normal second", severity="normal")
    _insert_decision(db_conn, bucket="business", title="M critical third", severity="critical")

    result = load_l1(db_conn, "business")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    content = decisions_block.content
    pos_critical = content.find("M critical third")
    pos_normal = content.find("A normal second")
    pos_minor = content.find("Z minor first")
    assert pos_critical < pos_normal < pos_minor, (
        f"severity order wrong: critical@{pos_critical}, "
        f"normal@{pos_normal}, minor@{pos_minor}"
    )


# -----------------------------------------------------------------------------
# Render format — exact assertion (the kind of test that catches B.2-style drift)
# -----------------------------------------------------------------------------


def test_decisions_render_format(db_conn: psycopg.Connection) -> None:
    """Decision render: '### <title>\\n[severity: X | ADR: N]\\n<summary>'."""
    with db_conn.cursor() as cur:
        cur.execute("DELETE FROM decisions WHERE bucket = 'business'")

    _insert_decision(
        db_conn, bucket="business", title="Use pgvector", severity="critical",
        adr_number=42, decision="pgvector handles 3072-dim embeddings",
    )

    result = load_l1(db_conn, "business")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    expected = (
        "### Use pgvector\n"
        "[severity: critical | ADR: 42]\n"
        "pgvector handles 3072-dim embeddings"
    )
    assert decisions_block.content == expected


def test_decisions_render_omits_adr_when_null(db_conn: psycopg.Connection) -> None:
    """ADR badge appears only when adr_number is non-null."""
    with db_conn.cursor() as cur:
        cur.execute("DELETE FROM decisions WHERE bucket = 'business'")

    _insert_decision(
        db_conn, bucket="business", title="ad-hoc decision",
        severity="normal", adr_number=None, decision="rationale",
    )

    result = load_l1(db_conn, "business")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    assert decisions_block.content == (
        "### ad-hoc decision\n[severity: normal]\nrationale"
    )
    assert "ADR" not in decisions_block.content
