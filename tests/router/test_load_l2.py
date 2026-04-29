"""Tests for load_l2 — project-scoped decisions + best_practices + patterns (contract §3.3).

Same isolation pattern as B.2/B.3: sync psycopg with autocommit=False; rollback on teardown.

Note: contract §3.3 specifies L2 decisions ordering as "full content;
recency DESC" — NO severity CASE expression at L2 (that's L1-specific).
The brief's mention of L2 severity CASE was stale; we follow the contract.
"""
from __future__ import annotations

from typing import Iterator

import psycopg
import pytest

from mcp_server.router.load_l2 import (
    _L2_BEST_PRACTICES_SQL,
    load_l2,
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
    conn: psycopg.Connection, *,
    bucket: str, project: str,
    title: str = "T", severity: str = "normal", adr_number: int | None = None,
    decision: str = "decision body", context: str = "ctx",
    consequences: str = "csq", alternatives: str | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO decisions "
            "(bucket, project, title, context, decision, consequences, "
            " alternatives, severity, adr_number) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (bucket, project, title, context, decision, consequences,
             alternatives, severity, adr_number),
        )


def _insert_best_practice(
    conn: psycopg.Connection, *,
    title: str, guidance: str, domain: str, scope: str,
    rationale: str | None = None, source: str = "operator",
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO best_practices (title, guidance, rationale, domain, scope, source) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (title, guidance, rationale, domain, scope, source),
        )


def _insert_pattern(
    conn: psycopg.Connection, *,
    name: str, description: str, code: str, use_case: str,
    applicable_buckets: list[str], language: str | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO patterns "
            "(name, description, language, code, use_case, applicable_buckets) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, description, language, code, use_case, applicable_buckets),
        )


def _wipe_l2(conn: psycopg.Connection, bucket: str, project: str) -> None:
    """Delete any prior L2 rows for the test bucket+project to make assertions crisp."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM decisions WHERE bucket = %s AND project = %s",
            (bucket, project),
        )
        cur.execute(
            "DELETE FROM best_practices WHERE scope = %s",
            (f"project:{bucket}/{project}",),
        )
        cur.execute(
            "DELETE FROM patterns WHERE %s = ANY(applicable_buckets)",
            (bucket,),
        )


# -----------------------------------------------------------------------------
# Happy path: 3 blocks
# -----------------------------------------------------------------------------


def test_happy_path_three_blocks_in_order(db_conn: psycopg.Connection) -> None:
    _wipe_l2(db_conn, "business", "declassified")
    _insert_decision(db_conn, bucket="business", project="declassified",
                     title="d1", decision="d body")
    _insert_best_practice(db_conn, title="bp1", guidance="g",
                          domain="process", scope="project:business/declassified")
    _insert_pattern(db_conn, name="p1", description="desc", code="x=1",
                    use_case="uc", applicable_buckets=["business"])

    result = load_l2(db_conn, "business", "declassified")

    assert isinstance(result, LayerContent)
    assert result.layer == "L2"
    assert result.loaded is True
    sources = [b.source for b in result.blocks]
    assert sources == ["decisions", "best_practices", "patterns"]
    assert result.token_count == sum(b.token_count for b in result.blocks)


# -----------------------------------------------------------------------------
# Skip-when guards
# -----------------------------------------------------------------------------


def test_bucket_none_returns_skipped_layer(db_conn: psycopg.Connection) -> None:
    result = load_l2(db_conn, None, "declassified")
    assert result.loaded is False
    assert result.blocks == ()
    assert result.token_count == 0


def test_project_none_returns_skipped_layer(db_conn: psycopg.Connection) -> None:
    result = load_l2(db_conn, "business", None)
    assert result.loaded is False
    assert result.blocks == ()
    assert result.token_count == 0


# -----------------------------------------------------------------------------
# Scope isolation: decisions, best_practices, patterns
# -----------------------------------------------------------------------------


def test_decisions_project_isolation(db_conn: psycopg.Connection) -> None:
    """Decisions for project='X' must not leak into project='Y' query."""
    _wipe_l2(db_conn, "business", "declassified")
    _wipe_l2(db_conn, "business", "other")
    _insert_decision(db_conn, bucket="business", project="declassified",
                     title="declass-only")
    _insert_decision(db_conn, bucket="business", project="other",
                     title="other-only")

    result = load_l2(db_conn, "business", "declassified")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    assert "declass-only" in decisions_block.content
    assert "other-only" not in decisions_block.content


def test_decisions_cross_bucket_isolation(db_conn: psycopg.Connection) -> None:
    """Same project name in different buckets must not leak."""
    _wipe_l2(db_conn, "business", "shared")
    _wipe_l2(db_conn, "personal", "shared")
    _insert_decision(db_conn, bucket="business", project="shared",
                     title="biz-shared")
    _insert_decision(db_conn, bucket="personal", project="shared",
                     title="pers-shared")

    result = load_l2(db_conn, "business", "shared")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    assert "biz-shared" in decisions_block.content
    assert "pers-shared" not in decisions_block.content


def test_best_practices_scope_filter(db_conn: psycopg.Connection) -> None:
    """best_practices filter is exact match on scope='project:<bucket>/<project>'."""
    _wipe_l2(db_conn, "business", "declassified")
    _insert_best_practice(db_conn, title="match", guidance="g1",
                          domain="process", scope="project:business/declassified")
    _insert_best_practice(db_conn, title="other-project", guidance="g2",
                          domain="process", scope="project:business/other")
    _insert_best_practice(db_conn, title="global-shouldnt-match", guidance="g3",
                          domain="process", scope="global")

    result = load_l2(db_conn, "business", "declassified")
    bp_block = next(b for b in result.blocks if b.source == "best_practices")
    assert "match" in bp_block.content
    assert "other-project" not in bp_block.content
    assert "global-shouldnt-match" not in bp_block.content


def test_patterns_bucket_array_filter(db_conn: psycopg.Connection) -> None:
    """patterns filter is `bucket = ANY(applicable_buckets)`."""
    _wipe_l2(db_conn, "business", "declassified")
    _wipe_l2(db_conn, "personal", "declassified")
    _insert_pattern(db_conn, name="biz-pat", description="d", code="c",
                    use_case="u", applicable_buckets=["business"])
    _insert_pattern(db_conn, name="pers-pat", description="d", code="c",
                    use_case="u", applicable_buckets=["personal"])
    _insert_pattern(db_conn, name="cross-pat", description="d", code="c",
                    use_case="u", applicable_buckets=["business", "personal"])

    result = load_l2(db_conn, "business", "declassified")
    patterns_block = next(b for b in result.blocks if b.source == "patterns")
    assert "biz-pat" in patterns_block.content
    assert "cross-pat" in patterns_block.content
    assert "pers-pat" not in patterns_block.content


# -----------------------------------------------------------------------------
# Partial DB failure: monkeypatch one private helper to raise → other 2 still load
# -----------------------------------------------------------------------------


def test_partial_db_failure_emits_remaining_blocks(
    db_conn: psycopg.Connection, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When one source helper returns None (DB error), L2 still loaded=True."""
    _wipe_l2(db_conn, "business", "declassified")
    _insert_decision(db_conn, bucket="business", project="declassified", title="d1")
    _insert_best_practice(db_conn, title="bp1", guidance="g",
                          domain="process", scope="project:business/declassified")
    _insert_pattern(db_conn, name="p1", description="d", code="c",
                    use_case="u", applicable_buckets=["business"])

    from mcp_server.router import load_l2 as load_l2_module
    monkeypatch.setattr(load_l2_module, "_load_decisions",
                        lambda conn, b, p: None)

    result = load_l2(db_conn, "business", "declassified")

    assert result.loaded is True
    sources = [b.source for b in result.blocks]
    assert sources == ["best_practices", "patterns"]


# -----------------------------------------------------------------------------
# All-fail: closed connection → all 3 queries fail → loaded=False
# -----------------------------------------------------------------------------


def test_all_queries_fail_loaded_false() -> None:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    conn.close()

    result = load_l2(conn, "business", "declassified")

    assert result.loaded is False
    assert result.blocks == ()


# -----------------------------------------------------------------------------
# Filter-first at EXPLAIN level (best_practices) — contract §5
# -----------------------------------------------------------------------------


def test_best_practices_filter_first_at_explain_level(
    db_conn: psycopg.Connection,
) -> None:
    """The best_practices SQL must apply the WHERE filter at scan-time, not after sort.

    Filter-first is mandatory per CONSTITUTION §5.6 rule 26 + contract §5.
    We verify by inspecting EXPLAIN — the Sort node's child must be a
    Seq Scan / Index Scan with a Filter clause, NOT a separate Filter
    node above the scan. (PG can express the filter on the scan node
    itself either as `Filter:` or via `Index Cond:`; both qualify.)
    """
    # Seed enough rows to ensure the planner picks a sortable plan.
    _wipe_l2(db_conn, "business", "declassified")
    for i in range(10):
        scope = (
            "project:business/declassified" if i % 2 == 0 else "project:business/other"
        )
        _insert_best_practice(
            db_conn, title=f"bp{i}", guidance="g",
            domain="process" if i % 2 else "convention",
            scope=scope,
        )

    explain_sql = "EXPLAIN (FORMAT JSON, ANALYZE) " + _L2_BEST_PRACTICES_SQL
    with db_conn.cursor() as cur:
        cur.execute(explain_sql, ("business", "declassified"))
        plan_row = cur.fetchone()

    assert plan_row is not None
    plan_json = plan_row[0]
    if isinstance(plan_json, str):
        import json
        plan_json = json.loads(plan_json)
    plan = plan_json[0]["Plan"]

    def find_scan_with_filter(node: dict) -> dict | None:
        """Return any Scan node that carries a Filter or Index Cond attribute."""
        if "Scan" in node.get("Node Type", ""):
            if "Filter" in node or "Index Cond" in node:
                return node
        for sub in node.get("Plans", []):
            found = find_scan_with_filter(sub)
            if found is not None:
                return found
        return None

    scan = find_scan_with_filter(plan)
    assert scan is not None, (
        "expected a Scan node with Filter / Index Cond — filter-first "
        f"violated. Plan: {plan}"
    )


# -----------------------------------------------------------------------------
# Token count consistency
# -----------------------------------------------------------------------------


def test_token_count_consistency(db_conn: psycopg.Connection) -> None:
    _wipe_l2(db_conn, "business", "declassified")
    _insert_decision(db_conn, bucket="business", project="declassified", title="d1")
    _insert_best_practice(db_conn, title="bp1", guidance="g",
                          domain="process", scope="project:business/declassified")
    _insert_pattern(db_conn, name="p1", description="d", code="c",
                    use_case="u", applicable_buckets=["business"])

    result = load_l2(db_conn, "business", "declassified")
    assert result.token_count == sum(b.token_count for b in result.blocks)


# -----------------------------------------------------------------------------
# Render format — three sources
# -----------------------------------------------------------------------------


def test_decisions_render_format(db_conn: psycopg.Connection) -> None:
    _wipe_l2(db_conn, "business", "declassified")
    _insert_decision(
        db_conn, bucket="business", project="declassified",
        title="Use SQLite for ETL", severity="critical", adr_number=42,
        decision="SQLite is fine for ETL pipelines",
        context="ETL volumes are small",
        consequences="Easy to ship, no infra",
        alternatives="Postgres adds operational burden",
    )

    result = load_l2(db_conn, "business", "declassified")
    decisions_block = next(b for b in result.blocks if b.source == "decisions")
    expected = (
        "### Use SQLite for ETL\n"
        "[severity: critical | ADR: 42]\n"
        "SQLite is fine for ETL pipelines\n"
        "\n"
        "Context: ETL volumes are small\n"
        "Consequences: Easy to ship, no infra\n"
        "Alternatives: Postgres adds operational burden"
    )
    assert decisions_block.content == expected


def test_decisions_render_omits_alternatives_when_null(
    db_conn: psycopg.Connection,
) -> None:
    _wipe_l2(db_conn, "business", "declassified")
    _insert_decision(
        db_conn, bucket="business", project="declassified",
        title="No alternatives", severity="normal", adr_number=None,
        decision="d", context="ctx", consequences="csq", alternatives=None,
    )

    result = load_l2(db_conn, "business", "declassified")
    content = next(b for b in result.blocks if b.source == "decisions").content
    assert "Alternatives" not in content
    assert "[severity: normal]" in content
    assert "ADR" not in content


def test_best_practices_render_format(db_conn: psycopg.Connection) -> None:
    _wipe_l2(db_conn, "business", "declassified")
    _insert_best_practice(
        db_conn, title="Always log unique request_id", guidance="Include request_id in every log line",
        rationale="Joinable to llm_calls",
        domain="convention", scope="project:business/declassified",
    )

    result = load_l2(db_conn, "business", "declassified")
    bp_block = next(b for b in result.blocks if b.source == "best_practices")
    expected = (
        "### Always log unique request_id\n"
        "[domain: convention]\n"
        "Include request_id in every log line\n"
        "\n"
        "Rationale: Joinable to llm_calls"
    )
    assert bp_block.content == expected


def test_patterns_render_format(db_conn: psycopg.Connection) -> None:
    _wipe_l2(db_conn, "business", "declassified")
    _insert_pattern(
        db_conn, name="DB connection retry",
        description="Retry once on transient psycopg errors",
        language="python", code="try:\n    op()\nexcept psycopg.OperationalError:\n    op()",
        use_case="Dropped TCP connection at peak",
        applicable_buckets=["business"],
    )

    result = load_l2(db_conn, "business", "declassified")
    patterns_block = next(b for b in result.blocks if b.source == "patterns")
    expected = (
        "### DB connection retry\n"
        "[language: python]\n"
        "Retry once on transient psycopg errors\n"
        "\n"
        "Use case: Dropped TCP connection at peak\n"
        "\n"
        "```python\n"
        "try:\n    op()\nexcept psycopg.OperationalError:\n    op()\n"
        "```"
    )
    assert patterns_block.content == expected
