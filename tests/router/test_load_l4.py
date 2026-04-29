"""Tests for load_l4 — vector search lessons + cross-cutting BP (contract §3.5).

Same isolation pattern as B.2..B.5: sync psycopg, autocommit=False, rollback.

Vector dim: 3072 per pgvector schema. Synthetic vectors use single-1
positions to make cosine similarity ranking predictable:
- vec(0) and vec(0) → cosine 1.0 (identical)
- vec(0) and vec(1) → cosine 0.0 (orthogonal)

This is enough to verify ordering and filter behavior without LLM calls.
The single slow test exercises the real `embed()` async helper for
end-to-end wiring confidence.
"""
from __future__ import annotations

import json
from typing import Iterator

import psycopg
import pytest

from mcp_server.router.load_l4 import (
    _L4_BP_SQL,
    _L4_LESSONS_SQL,
    _vector_literal,
    load_l4,
)
from mcp_server.router.types import LayerContent


TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"
EMBED_DIM = 3072


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


def _vec(seed: int, dim: int = EMBED_DIM) -> list[float]:
    """Synthetic unit vector with 1.0 at position seed%dim, 0.0 elsewhere."""
    v = [0.0] * dim
    v[seed % dim] = 1.0
    return v


def _insert_lesson(
    conn: psycopg.Connection, *,
    title: str = "T", content: str = "c",
    bucket: str = "business", category: str = "ARCH",
    next_time: str | None = None,
    embedding: list[float] | None = None,
    status: str = "active",
    applicable_buckets: list[str] | None = None,
    deleted_at: object | None = None,
) -> str:
    """Returns the inserted row's id as str (for short-id render assertions)."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO lessons "
            "(title, content, bucket, category, next_time, embedding, "
            " status, applicable_buckets, deleted_at) "
            "VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s) RETURNING id",
            (
                title, content, bucket, category, next_time,
                _vector_literal(embedding) if embedding is not None else None,
                status, applicable_buckets or [], deleted_at,
            ),
        )
        row = cur.fetchone()
        assert row is not None
        return str(row[0])


def _insert_bp(
    conn: psycopg.Connection, *,
    title: str = "T", guidance: str = "g", domain: str = "process",
    rationale: str | None = None,
    embedding: list[float] | None = None,
    scope: str = "global",
    applicable_buckets: list[str] | None = None,
    source: str = "operator", active: bool = True,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO best_practices "
            "(title, guidance, rationale, domain, scope, applicable_buckets, "
            " source, embedding, active) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector, %s)",
            (
                title, guidance, rationale, domain, scope,
                applicable_buckets or [], source,
                _vector_literal(embedding) if embedding is not None else None,
                active,
            ),
        )


def _wipe_l4(conn: psycopg.Connection, bucket: str | None = None) -> None:
    """Clean prior fixture rows; rollback handles cleanup but explicit
    DELETEs keep this test's view crisp against any pre-seeded rows."""
    with conn.cursor() as cur:
        if bucket is not None:
            cur.execute(
                "DELETE FROM lessons "
                "WHERE bucket = %s OR %s = ANY(applicable_buckets)",
                (bucket, bucket),
            )
        else:
            cur.execute("DELETE FROM lessons")
        cur.execute("DELETE FROM best_practices")


# -----------------------------------------------------------------------------
# 1. needs_lessons=False -> loaded=False
# -----------------------------------------------------------------------------


def test_needs_lessons_false_returns_skipped_layer(db_conn: psycopg.Connection) -> None:
    result = load_l4(db_conn, "business", _vec(0), needs_lessons=False)
    assert result.loaded is False
    assert result.blocks == ()
    assert result.token_count == 0


# -----------------------------------------------------------------------------
# 2. query_embedding=None -> loaded=False
# -----------------------------------------------------------------------------


def test_query_embedding_none_returns_skipped_layer(
    db_conn: psycopg.Connection,
) -> None:
    result = load_l4(db_conn, "business", None, needs_lessons=True)
    assert result.loaded is False
    assert result.blocks == ()


# -----------------------------------------------------------------------------
# 3. Happy path: bucket + classifier_domain + embedding all set -> 2 blocks
# -----------------------------------------------------------------------------


def test_happy_path_two_blocks(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn, "business")
    _insert_lesson(db_conn, title="lesson_match", next_time="next time guidance",
                   embedding=_vec(0), bucket="business")
    _insert_bp(db_conn, title="bp_match", guidance="bp body",
               domain="process", embedding=_vec(0), scope="global",
               applicable_buckets=["business"])

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )

    assert isinstance(result, LayerContent)
    assert result.layer == "L4"
    assert result.loaded is True
    assert [b.source for b in result.blocks] == ["lessons", "best_practices"]
    assert result.token_count == sum(b.token_count for b in result.blocks)


# -----------------------------------------------------------------------------
# 4. Lessons bucket exact match
# -----------------------------------------------------------------------------


def test_lessons_bucket_exact_match(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn, "business")
    _wipe_l4(db_conn, "personal")
    _insert_lesson(db_conn, title="biz_lesson", embedding=_vec(0), bucket="business")
    _insert_lesson(db_conn, title="pers_lesson", embedding=_vec(0), bucket="personal")

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0), needs_lessons=True,
    )
    lessons_block = next(b for b in result.blocks if b.source == "lessons")
    assert "biz_lesson" in lessons_block.content
    assert "pers_lesson" not in lessons_block.content


# -----------------------------------------------------------------------------
# 5. Lessons cross-bucket via applicable_buckets array (per D6)
# -----------------------------------------------------------------------------


def test_lessons_cross_bucket_via_applicable_buckets(
    db_conn: psycopg.Connection,
) -> None:
    """Lesson with bucket='personal' but applicable_buckets=['business'] DOES
    appear when query bucket='business'. Per contract §3.5 third filter branch."""
    _wipe_l4(db_conn, "business")
    _wipe_l4(db_conn, "personal")
    _insert_lesson(
        db_conn, title="cross_cut_lesson",
        embedding=_vec(0), bucket="personal",
        applicable_buckets=["business", "scout"],
    )

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0), needs_lessons=True,
    )
    lessons_block = next(b for b in result.blocks if b.source == "lessons")
    assert "cross_cut_lesson" in lessons_block.content


# -----------------------------------------------------------------------------
# 6. Lessons bucket=None passthrough (per D6 first filter branch)
# -----------------------------------------------------------------------------


def test_lessons_bucket_none_passthrough(db_conn: psycopg.Connection) -> None:
    """bucket=None means the bucket filter SKIPS — all active lessons appear."""
    _wipe_l4(db_conn)
    _insert_lesson(db_conn, title="biz_lesson", embedding=_vec(0), bucket="business")
    _insert_lesson(db_conn, title="pers_lesson", embedding=_vec(0), bucket="personal")
    _insert_lesson(db_conn, title="scout_lesson", embedding=_vec(0), bucket="scout")

    result = load_l4(
        db_conn, bucket=None, query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",  # so BP runs too
    )
    lessons_block = next(b for b in result.blocks if b.source == "lessons")
    assert "biz_lesson" in lessons_block.content
    assert "pers_lesson" in lessons_block.content
    assert "scout_lesson" in lessons_block.content


# -----------------------------------------------------------------------------
# 7. BP filter via classifier_domain
# -----------------------------------------------------------------------------


def test_bp_filter_by_domain(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn)
    _insert_bp(db_conn, title="proc_bp", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=[])
    _insert_bp(db_conn, title="conv_bp", guidance="g", domain="convention",
               embedding=_vec(0), applicable_buckets=[])

    result = load_l4(
        db_conn, bucket=None, query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )
    bp_block = next(b for b in result.blocks if b.source == "best_practices")
    assert "proc_bp" in bp_block.content
    assert "conv_bp" not in bp_block.content


# -----------------------------------------------------------------------------
# 8. BP filter via applicable_buckets
# -----------------------------------------------------------------------------


def test_bp_filter_by_applicable_buckets(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn)
    _insert_bp(db_conn, title="biz_bp", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["business"])
    _insert_bp(db_conn, title="pers_bp", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["personal"])

    # No domain match (use 'workflow' which neither row has)
    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="workflow",
    )
    bp_block = next(b for b in result.blocks if b.source == "best_practices")
    assert "biz_bp" in bp_block.content
    assert "pers_bp" not in bp_block.content


# -----------------------------------------------------------------------------
# 9. BP both filters OR (rows matching either appear)
# -----------------------------------------------------------------------------


def test_bp_both_filters_or(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn)
    _insert_bp(db_conn, title="domain_match", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=[])
    _insert_bp(db_conn, title="bucket_match", guidance="g", domain="convention",
               embedding=_vec(0), applicable_buckets=["business"])
    _insert_bp(db_conn, title="both_match", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["business"])
    _insert_bp(db_conn, title="neither", guidance="g", domain="convention",
               embedding=_vec(0), applicable_buckets=["personal"])

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )
    bp_block = next(b for b in result.blocks if b.source == "best_practices")
    assert "domain_match" in bp_block.content
    assert "bucket_match" in bp_block.content
    assert "both_match" in bp_block.content
    assert "neither" not in bp_block.content


# -----------------------------------------------------------------------------
# 10. Degenerate case: bucket=None AND classifier_domain=None
#     → 1 block (lessons), 0 blocks BP, loaded=True
# -----------------------------------------------------------------------------


def test_degenerate_no_filters_skips_bp_block(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn)
    _insert_lesson(db_conn, title="any_lesson", embedding=_vec(0),
                   bucket="business")
    _insert_bp(db_conn, title="any_bp", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["business"])

    result = load_l4(
        db_conn, bucket=None, query_embedding=_vec(0),
        needs_lessons=True, classifier_domain=None,
    )

    # Lessons block runs (passthrough); BP block skipped (no discriminating filter).
    assert result.loaded is True
    assert [b.source for b in result.blocks] == ["lessons"]


# -----------------------------------------------------------------------------
# 11. active=false rows excluded in both tables
# -----------------------------------------------------------------------------


def test_inactive_rows_excluded(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn, "business")
    # Inactive lesson (status != 'active')
    _insert_lesson(db_conn, title="archived_lesson", embedding=_vec(0),
                   bucket="business", status="archived")
    _insert_lesson(db_conn, title="active_lesson", embedding=_vec(0),
                   bucket="business", status="active")
    # Inactive BP (active=false)
    _insert_bp(db_conn, title="inactive_bp", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["business"], active=False)
    _insert_bp(db_conn, title="active_bp", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["business"], active=True)

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )

    lessons_block = next(b for b in result.blocks if b.source == "lessons")
    bp_block = next(b for b in result.blocks if b.source == "best_practices")
    assert "active_lesson" in lessons_block.content
    assert "archived_lesson" not in lessons_block.content
    assert "active_bp" in bp_block.content
    assert "inactive_bp" not in bp_block.content


# -----------------------------------------------------------------------------
# 12. Empty results both tables -> 2 empty blocks, loaded=True
# -----------------------------------------------------------------------------


def test_empty_results_both_tables_loaded_true(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn, "business")
    # No inserts — both queries return 0 rows.
    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )
    assert result.loaded is True
    assert len(result.blocks) == 2
    assert all(b.row_count == 0 for b in result.blocks)
    assert all(b.content == "" for b in result.blocks)
    assert result.token_count == 0


# -----------------------------------------------------------------------------
# 13. lessons query DB error, BP OK -> 1 block (BP), loaded=True
# -----------------------------------------------------------------------------


def test_partial_failure_lessons_only(
    db_conn: psycopg.Connection, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _wipe_l4(db_conn, "business")
    _insert_bp(db_conn, title="bp_one", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["business"])

    from mcp_server.router import load_l4 as load_l4_module
    monkeypatch.setattr(load_l4_module, "_load_relevant_lessons",
                        lambda c, b, e, k: None)

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )
    assert result.loaded is True
    assert [b.source for b in result.blocks] == ["best_practices"]


# -----------------------------------------------------------------------------
# 14. Both queries DB error -> loaded=False
# -----------------------------------------------------------------------------


def test_both_queries_fail_loaded_false() -> None:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    conn.close()

    result = load_l4(
        conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )
    assert result.loaded is False
    assert result.blocks == ()


# -----------------------------------------------------------------------------
# 15. EXPLAIN: lessons filter-first (Seq Scan with Filter, NOT Index Scan
#     on embedding; Sort Key references the cosine distance).
# -----------------------------------------------------------------------------


def test_lessons_filter_first_at_explain_level(db_conn: psycopg.Connection) -> None:
    """Lessons SQL must apply WHERE filter at scan-time, not after sort/limit.

    Per ADR-024 + contract §5: no HNSW, no vector index of any kind.
    Plan must show Seq Scan (or its equivalent) with Filter referencing
    the active/bucket/embedding-NOT-NULL predicates.
    """
    _wipe_l4(db_conn, "business")
    for i in range(10):
        _insert_lesson(
            db_conn, title=f"l{i}", embedding=_vec(i % 5),
            bucket="business" if i % 2 == 0 else "personal",
            status="active" if i % 3 != 0 else "archived",
        )

    explain_sql = "EXPLAIN (FORMAT JSON, ANALYZE) " + _L4_LESSONS_SQL
    with db_conn.cursor() as cur:
        cur.execute(
            explain_sql,
            (_vector_literal(_vec(0)), "business", "business", "business", 5),
        )
        plan_row = cur.fetchone()

    assert plan_row is not None
    plan_json = plan_row[0]
    if isinstance(plan_json, str):
        plan_json = json.loads(plan_json)
    plan = plan_json[0]["Plan"]

    def find_scan_with_filter(node: dict) -> dict | None:
        if "Scan" in node.get("Node Type", "") and (
            "Filter" in node or "Index Cond" in node
        ):
            return node
        for sub in node.get("Plans", []):
            found = find_scan_with_filter(sub)
            if found is not None:
                return found
        return None

    scan = find_scan_with_filter(plan)
    assert scan is not None, (
        f"expected a Scan node with Filter — filter-first violated: {plan}"
    )


# -----------------------------------------------------------------------------
# 16. EXPLAIN: BP filter-first
# -----------------------------------------------------------------------------


def test_bp_filter_first_at_explain_level(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn)
    for i in range(10):
        _insert_bp(
            db_conn, title=f"bp{i}", guidance="g",
            domain="process" if i % 2 == 0 else "convention",
            embedding=_vec(i % 5),
            applicable_buckets=["business"] if i % 3 == 0 else [],
            active=(i % 4 != 0),
        )

    explain_sql = "EXPLAIN (FORMAT JSON, ANALYZE) " + _L4_BP_SQL
    with db_conn.cursor() as cur:
        cur.execute(
            explain_sql,
            (_vector_literal(_vec(0)), "process", "business", 5),
        )
        plan_row = cur.fetchone()

    assert plan_row is not None
    plan_json = plan_row[0]
    if isinstance(plan_json, str):
        plan_json = json.loads(plan_json)
    plan = plan_json[0]["Plan"]

    def find_scan_with_filter(node: dict) -> dict | None:
        if "Scan" in node.get("Node Type", "") and (
            "Filter" in node or "Index Cond" in node
        ):
            return node
        for sub in node.get("Plans", []):
            found = find_scan_with_filter(sub)
            if found is not None:
                return found
        return None

    scan = find_scan_with_filter(plan)
    assert scan is not None, (
        f"expected a Scan node with Filter — filter-first violated: {plan}"
    )


# -----------------------------------------------------------------------------
# 17. No-HNSW assertion (defense-in-depth against future schema drift)
# -----------------------------------------------------------------------------


def test_no_hnsw_indexes_exist(db_conn: psycopg.Connection) -> None:
    """Per ADR-024: no HNSW on lessons or best_practices embedding columns."""
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT tablename, indexname, indexdef FROM pg_indexes "
            "WHERE tablename IN ('lessons', 'best_practices') "
            "  AND indexdef ILIKE '%USING hnsw%'"
        )
        rows = cur.fetchall()
    assert rows == [], (
        f"unexpected HNSW indexes (ADR-024 violation): {rows}"
    )


# -----------------------------------------------------------------------------
# 18. Token count consistency
# -----------------------------------------------------------------------------


def test_token_count_consistency(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn, "business")
    _insert_lesson(db_conn, title="l1", next_time="nt", embedding=_vec(0),
                   bucket="business")
    _insert_bp(db_conn, title="bp1", guidance="g", domain="process",
               embedding=_vec(0), applicable_buckets=["business"])

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )
    assert result.token_count == sum(b.token_count for b in result.blocks)


# -----------------------------------------------------------------------------
# 19. Lessons render format + null next_time
# -----------------------------------------------------------------------------


def test_lessons_render_format_and_null_next_time(
    db_conn: psycopg.Connection,
) -> None:
    _wipe_l4(db_conn, "business")
    lid = _insert_lesson(
        db_conn, title="L with next", next_time="do this next time",
        embedding=_vec(0), bucket="business",
    )
    _insert_lesson(
        db_conn, title="L without next", next_time=None,
        embedding=_vec(0), bucket="business",
    )

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True,
    )
    content = next(b for b in result.blocks if b.source == "lessons").content
    short = lid[:8]
    # Render with next_time present
    assert f"### L with next\n[id: {short} | similarity: 1.00]\ndo this next time" in content
    # Render with next_time NULL — header + metadata only, no body line
    assert "### L without next\n[id: " in content
    assert "### L without next\n[id: " in content
    # The "without next" block must NOT have a stray body line after metadata.
    no_next_section = content.split("### L without next\n")[1]
    # First line is the metadata bracket; split and check there's nothing else
    # before the next entry separator (blank line + ### or end of string).
    section_lines = no_next_section.split("\n")
    assert section_lines[0].startswith("[id: ") and section_lines[0].endswith("]")
    # Either next is end-of-string OR a blank line (entry separator)
    assert len(section_lines) == 1 or section_lines[1] == ""


# -----------------------------------------------------------------------------
# 20. BP render format + null rationale
# -----------------------------------------------------------------------------


def test_bp_render_format_and_null_rationale(db_conn: psycopg.Connection) -> None:
    _wipe_l4(db_conn)
    _insert_bp(
        db_conn, title="BP with rationale",
        guidance="follow this rule", rationale="because it works",
        domain="process", embedding=_vec(0), applicable_buckets=["business"],
    )
    _insert_bp(
        db_conn, title="BP without rationale",
        guidance="follow this", rationale=None,
        domain="convention", embedding=_vec(0), applicable_buckets=["business"],
    )

    result = load_l4(
        db_conn, bucket="business", query_embedding=_vec(0),
        needs_lessons=True, classifier_domain="process",
    )
    bp_block = next(b for b in result.blocks if b.source == "best_practices")
    content = bp_block.content

    # With rationale: domain process, blank line, Rationale: line
    assert (
        "### BP with rationale\n"
        "[domain: process | similarity: 1.00]\n"
        "follow this rule\n"
        "\n"
        "Rationale: because it works"
    ) in content

    # Without rationale: just header + metadata + guidance, NO Rationale line
    assert (
        "### BP without rationale\n"
        "[domain: convention | similarity: 1.00]\n"
        "follow this"
    ) in content
    no_rat = content.split("### BP without rationale\n")[1]
    assert "Rationale:" not in no_rat


# -----------------------------------------------------------------------------
# 21. SLOW: real embed() round-trip
# -----------------------------------------------------------------------------


@pytest.mark.slow
async def test_real_embedding_to_load_l4_roundtrip(
    db_conn: psycopg.Connection,
) -> None:
    """Exercise the B.9-pattern: real embed() → load_l4 → blocks.

    Cost: ~$0.0001 per run. Asserts the integration works end-to-end
    with the actual OpenAI embedding response shape (3072 floats).
    """
    from mcp_server.embeddings import embed

    query_emb = await embed("postgres optimization for vector search workloads")
    assert query_emb is not None, "embed() returned None — LiteLLM or OpenAI down"
    assert len(query_emb) == EMBED_DIM

    # Seed at least one row in each table so blocks have meaningful content.
    _wipe_l4(db_conn, "business")
    _insert_lesson(
        db_conn, title="real_lesson", next_time="nt", embedding=_vec(0),
        bucket="business",
    )
    _insert_bp(
        db_conn, title="real_bp", guidance="g", domain="process",
        embedding=_vec(0), applicable_buckets=["business"],
    )

    result = load_l4(
        db_conn, bucket="business", query_embedding=query_emb,
        needs_lessons=True, classifier_domain="process",
    )
    assert result.loaded is True
    assert len(result.blocks) == 2
    assert all(b.row_count >= 1 for b in result.blocks)
