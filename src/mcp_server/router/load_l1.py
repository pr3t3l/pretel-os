"""L1 layer loader: bucket-scoped context (contract §3.2).

Two DB-backed sources per contract §3.2:
    1. decisions  — active rows where bucket matches via direct equality
                    OR via applicable_buckets array; severity-ordered
                    (CASE expression at SQL level — pull-then-sort-in-Python
                    is non-conformant per contract §3.2).
    2. operator_preferences — active rows where scope LIKE 'bucket:<bucket>%'.

L1 has NO file-backed sources (the per-bucket README files in
`buckets/<bucket>/README.md` exist for human reference but are not part of
the Router context — see contract §3.2 + spec/router/spec.md §6.1).

Loaded decision tree:
    bucket is None                          → loaded=False, blocks=()
    both sources fail (psycopg.Error)       → loaded=False, blocks=()
    at least one source returns a block     → loaded=True
"""
from __future__ import annotations

import psycopg

from mcp_server.router._tokens import count_tokens
from mcp_server.router.types import ContextBlock, LayerContent


# SQL — verbatim from contract §3.2 (severity CASE is mandatory at DB level).
_L1_DECISIONS_SQL = """
SELECT id, title, scope, severity, adr_number,
       LEFT(decision, 500) AS summary
FROM decisions
WHERE status = 'active'
  AND (bucket = %s OR %s = ANY(applicable_buckets))
ORDER BY
  CASE severity
    WHEN 'critical' THEN 0
    WHEN 'normal'   THEN 1
    WHEN 'minor'    THEN 2
    ELSE 99
  END,
  created_at DESC
"""

_L1_PREFS_SQL = """
SELECT category, key, value
FROM operator_preferences
WHERE active = true
  AND scope LIKE 'bucket:' || %s || '%%'
ORDER BY category, key
"""


def _render_decisions(rows: list[tuple[object, ...]]) -> str:
    """Render decision rows per the per-entry pattern.

    Layout per entry:
        ### <title>
        [severity: <severity> | ADR: <adr_number>]
        <summary>

    `severity` is always present (column has a default). `ADR: N` only
    appears when adr_number is non-null.
    """
    parts: list[str] = []
    for _id, title, _scope, severity, adr_number, summary in rows:
        meta_bits = [f"severity: {severity}"]
        if adr_number is not None:
            meta_bits.append(f"ADR: {adr_number}")
        parts.append(
            f"### {title}\n"
            f"[{' | '.join(meta_bits)}]\n"
            f"{summary}"
        )
    return "\n\n".join(parts)


def _render_prefs(rows: list[tuple[object, ...]]) -> str:
    """Render bucket-scoped preferences as inline `category.key: value` lines.

    Mirrors the L0 prefs render — same shape (key/value), same format.
    """
    return "\n".join(f"{category}.{key}: {value}" for category, key, value in rows)


def _load_decisions(conn: psycopg.Connection, bucket: str) -> ContextBlock | None:
    """Load L1 decisions per contract §3.2. Returns None on DB error."""
    try:
        with conn.cursor() as cur:
            cur.execute(_L1_DECISIONS_SQL, (bucket, bucket))
            rows = cur.fetchall()
    except psycopg.Error:
        return None

    content = _render_decisions(list(rows))
    return ContextBlock(
        source="decisions",
        content=content,
        row_count=len(rows),
        token_count=count_tokens(content),
    )


def _load_prefs(conn: psycopg.Connection, bucket: str) -> ContextBlock | None:
    """Load bucket-scoped operator_preferences per contract §3.2.

    Filter is `scope LIKE 'bucket:<bucket>%'`, which captures both the
    bare bucket scope (`bucket:business`) and any sub-bucket pattern
    (`bucket:business/freelance`, etc.).
    """
    try:
        with conn.cursor() as cur:
            cur.execute(_L1_PREFS_SQL, (bucket,))
            rows = cur.fetchall()
    except psycopg.Error:
        return None

    content = _render_prefs(list(rows))
    return ContextBlock(
        source="operator_preferences",
        content=content,
        row_count=len(rows),
        token_count=count_tokens(content),
    )


def load_l1(conn: psycopg.Connection, bucket: str | None) -> LayerContent:
    """Assemble L1 (bucket-scoped context) per contract §3.2.

    Args:
        conn: sync psycopg connection. Caller owns the transaction.
        bucket: 'business' | 'personal' | 'scout' (or sub-bucket form).
                None means the classifier did not identify a bucket; L1
                is skipped (loaded=False).

    Returns:
        LayerContent with up to 2 blocks (decisions, operator_preferences),
        in that order. loaded=False when bucket is None or when all DB
        queries failed.
    """
    if bucket is None:
        return LayerContent(layer="L1", blocks=(), token_count=0, loaded=False)

    blocks: list[ContextBlock] = []
    decisions_block = _load_decisions(conn, bucket)
    if decisions_block is not None:
        blocks.append(decisions_block)
    prefs_block = _load_prefs(conn, bucket)
    if prefs_block is not None:
        blocks.append(prefs_block)

    if not blocks:
        return LayerContent(layer="L1", blocks=(), token_count=0, loaded=False)

    return LayerContent(
        layer="L1",
        blocks=tuple(blocks),
        token_count=sum(b.token_count for b in blocks),
        loaded=True,
    )
