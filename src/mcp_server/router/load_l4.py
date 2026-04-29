"""L4 layer loader: vector search over lessons + cross-cutting best_practices (contract §3.5).

Two DB-backed sources, each producing one ContextBlock with similarity-
ordered top-K rows:

    1. lessons          — sequential pgvector scan, filter-first per
                          ADR-024 (no HNSW). Bucket filter is a 3-way:
                          NULL passthrough, exact match, OR membership
                          in applicable_buckets array.

    2. best_practices   — sequential pgvector scan, filter-first.
                          Cross-cutting filter is OR'd: row matches if
                          its domain equals classifier_domain OR the
                          query bucket is in applicable_buckets array.

Embedding is NOT computed here. The orchestrator (assemble_bundle in
B.9) calls `mcp_server.embeddings.embed()` once and passes the vector
to load_l4 — both sources share the same query_embedding, so embedding
twice would be wasteful and inconsistent.

Loaded decision tree:
    not needs_lessons OR query_embedding is None        → loaded=False, ()
    bucket=None AND classifier_domain=None              → BP block skipped
                                                          (no discriminating
                                                          filter ⇒ would
                                                          load global state)
    lessons query OK (rows or empty)                    → 1 block
    BP attempted AND query OK                           → 1 more block
    one query fails, other OK                           → loaded=True with
                                                          remaining blocks
    all attempted queries fail                          → loaded=False, ()
"""
from __future__ import annotations

from typing import cast

import psycopg

from mcp_server.router._tokens import count_tokens
from mcp_server.router.types import ContextBlock, LayerContent


# Verbatim from contract §3.5: 3-way bucket filter (NULL pass / exact / array).
_L4_LESSONS_SQL = """
SELECT id, title, next_time, similarity
FROM (
  SELECT id, title, next_time,
         (1 - (embedding <=> %s::vector)) AS similarity
  FROM lessons
  WHERE status = 'active'
    AND deleted_at IS NULL
    AND embedding IS NOT NULL
    AND (%s::text IS NULL OR bucket = %s OR %s = ANY(applicable_buckets))
) sub
ORDER BY similarity DESC
LIMIT %s
"""

# Cross-cutting BP filter per contract §3.5: domain OR applicable_buckets.
# `embedding IS NOT NULL` is implicit per Phase B convention (rows without
# embeddings cannot participate in vector search).
_L4_BP_SQL = """
SELECT id, title, guidance, rationale, domain,
       (1 - (embedding <=> %s::vector)) AS similarity
FROM best_practices
WHERE active = true
  AND embedding IS NOT NULL
  AND (domain = %s OR %s = ANY(applicable_buckets))
ORDER BY similarity DESC
LIMIT %s
"""


def _vector_literal(vec: list[float]) -> str:
    """Format a list[float] as a pgvector literal '[a,b,c,...]'."""
    return "[" + ",".join(f"{x:.10g}" for x in vec) + "]"


def _render_lessons(rows: list[tuple[object, ...]]) -> str:
    """Render lesson rows: ### title + [id: <8 chars> | similarity: 0.87] + next_time.

    Body (next_time) is omitted when NULL — header + metadata bracket
    survives so the consumer still sees the entry.
    """
    parts: list[str] = []
    for id_, title, next_time, similarity in rows:
        short_id = str(id_)[:8]
        sim = float(cast(float, similarity)) if similarity is not None else 0.0
        lines = [
            f"### {title}",
            f"[id: {short_id} | similarity: {sim:.2f}]",
        ]
        if next_time:
            lines.append(str(next_time))
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def _render_bp(rows: list[tuple[object, ...]]) -> str:
    """Render cross-cutting BP: ### title + [domain | similarity] + guidance + Rationale.

    Rationale line is omitted entirely (header + blank line included)
    when rationale is NULL.
    """
    parts: list[str] = []
    for _id, title, guidance, rationale, domain, similarity in rows:
        sim = float(cast(float, similarity)) if similarity is not None else 0.0
        lines = [
            f"### {title}",
            f"[domain: {domain} | similarity: {sim:.2f}]",
            str(guidance),
        ]
        if rationale is not None:
            lines.append("")
            lines.append(f"Rationale: {rationale}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def _load_relevant_lessons(
    conn: psycopg.Connection,
    bucket: str | None,
    query_embedding: list[float],
    top_k: int,
) -> ContextBlock | None:
    try:
        with conn.cursor() as cur:
            cur.execute(
                _L4_LESSONS_SQL,
                (_vector_literal(query_embedding), bucket, bucket, bucket, top_k),
            )
            rows = cur.fetchall()
    except psycopg.Error:
        return None
    content = _render_lessons(list(rows))
    return ContextBlock(
        source="lessons",
        content=content,
        row_count=len(rows),
        token_count=count_tokens(content),
    )


def _load_cross_cutting_bp(
    conn: psycopg.Connection,
    bucket: str | None,
    classifier_domain: str | None,
    query_embedding: list[float],
    top_k: int,
) -> ContextBlock | None:
    try:
        with conn.cursor() as cur:
            cur.execute(
                _L4_BP_SQL,
                (_vector_literal(query_embedding), classifier_domain, bucket, top_k),
            )
            rows = cur.fetchall()
    except psycopg.Error:
        return None
    content = _render_bp(list(rows))
    return ContextBlock(
        source="best_practices",
        content=content,
        row_count=len(rows),
        token_count=count_tokens(content),
    )


def load_l4(
    conn: psycopg.Connection,
    bucket: str | None,
    query_embedding: list[float] | None,
    needs_lessons: bool,
    classifier_domain: str | None = None,
    top_k: int = 5,
) -> LayerContent:
    """Assemble L4 (vector-search) per contract §3.5.

    Args:
        conn: sync psycopg connection.
        bucket: workspace bucket; passes through as NULL in lessons SQL,
                participates in BP applicable_buckets array filter.
        query_embedding: pre-computed embedding (Phase B does NOT embed;
                see module docstring). None means the orchestrator did
                not produce a vector — L4 is skipped.
        needs_lessons: classifier signal; False → L4 skipped.
        classifier_domain: optional best_practices domain to match. None
                until classifier output is extended (see contract §3.5
                forward-looking note).
        top_k: per-source LIMIT; default 5 per contract §3.5.

    Returns:
        LayerContent with up to 2 blocks (lessons, best_practices) in
        that order. See module docstring for the full loaded decision
        tree.
    """
    if not needs_lessons or query_embedding is None:
        return LayerContent(layer="L4", blocks=(), token_count=0, loaded=False)

    blocks: list[ContextBlock] = []

    lessons_block = _load_relevant_lessons(conn, bucket, query_embedding, top_k)
    if lessons_block is not None:
        blocks.append(lessons_block)

    if bucket is not None or classifier_domain is not None:
        bp_block = _load_cross_cutting_bp(
            conn, bucket, classifier_domain, query_embedding, top_k,
        )
        if bp_block is not None:
            blocks.append(bp_block)
    # else: degenerate case — both filters NULL; skip BP query entirely
    # to avoid loading the global state of best_practices into L4.

    if not blocks:
        return LayerContent(layer="L4", blocks=(), token_count=0, loaded=False)

    return LayerContent(
        layer="L4",
        blocks=tuple(blocks),
        token_count=sum(b.token_count for b in blocks),
        loaded=True,
    )
