"""L2 layer loader: project-scoped context (contract §3.3).

Three DB-backed sources per contract §3.3:
    1. decisions       — WHERE status='active' AND bucket=$bucket AND project=$project
                         ORDER BY created_at DESC. Full content (all 4 long
                         text columns) — distinct from L1's LEFT(decision, 500).
    2. best_practices  — WHERE active=true AND scope='project:<bucket>/<project>'
                         ORDER BY domain, updated_at DESC.
                         Filter-first is mandatory per contract §5 / §3.3
                         performance contract.
    3. patterns        — WHERE $bucket = ANY(applicable_buckets)
                         ORDER BY language, updated_at DESC.

L2 is strictly nested in L1 — no project without a bucket.

Loaded decision tree:
    bucket is None OR project is None           → loaded=False, blocks=()
    all 3 queries fail (psycopg.Error)          → loaded=False, blocks=()
    at least one source returns a block         → loaded=True
                                                  (empty rows still count)
"""
from __future__ import annotations

import psycopg

from mcp_server.router._tokens import count_tokens
from mcp_server.router.types import ContextBlock, LayerContent


# Per Q2 confirmed render — drop id and scope (id is uuid LLM can't use;
# scope is redundant under WHERE bucket+project).
_L2_DECISIONS_SQL = """
SELECT title, severity, adr_number, decision, context, consequences, alternatives
FROM decisions
WHERE status = 'active' AND bucket = %s AND project = %s
ORDER BY created_at DESC
"""

# SQL — verbatim from contract §3.3.
_L2_BEST_PRACTICES_SQL = """
SELECT id, title, guidance, rationale, domain
FROM best_practices
WHERE active = true
  AND scope = 'project:' || %s || '/' || %s
ORDER BY domain, updated_at DESC
"""

_L2_PATTERNS_SQL = """
SELECT name, description, language, code, use_case
FROM patterns
WHERE %s = ANY(applicable_buckets)
ORDER BY language, updated_at DESC
"""


def _render_decisions(rows: list[tuple[object, ...]]) -> str:
    """Render full-content decisions per the per-entry pattern.

    Layout:
        ### <title>
        [severity: <severity> | ADR: <adr_number>]
        <decision>

        Context: <context>
        Consequences: <consequences>
        Alternatives: <alternatives>     # only if non-null

    `severity` always present; ADR badge only when adr_number non-null;
    Alternatives line only when alternatives is non-null.
    """
    parts: list[str] = []
    for title, severity, adr_number, decision, context, consequences, alternatives in rows:
        meta_bits = [f"severity: {severity}"]
        if adr_number is not None:
            meta_bits.append(f"ADR: {adr_number}")
        body_lines = [
            f"### {title}",
            f"[{' | '.join(meta_bits)}]",
            str(decision),
            "",
            f"Context: {context}",
            f"Consequences: {consequences}",
        ]
        if alternatives is not None:
            body_lines.append(f"Alternatives: {alternatives}")
        parts.append("\n".join(body_lines))
    return "\n\n".join(parts)


def _render_best_practices(rows: list[tuple[object, ...]]) -> str:
    """Render best_practices per the per-entry pattern.

    Layout:
        ### <title>
        [domain: <domain>]
        <guidance>

        Rationale: <rationale>     # only if non-null

    Drop `id` from render per Q2 consistency (uuid not LLM-actionable).
    """
    parts: list[str] = []
    for _id, title, guidance, rationale, domain in rows:
        body_lines = [
            f"### {title}",
            f"[domain: {domain}]",
            str(guidance),
        ]
        if rationale is not None:
            body_lines.append("")
            body_lines.append(f"Rationale: {rationale}")
        parts.append("\n".join(body_lines))
    return "\n\n".join(parts)


def _render_patterns(rows: list[tuple[object, ...]]) -> str:
    """Render code patterns per the per-entry pattern.

    Layout:
        ### <name>
        [language: <language>]     # only if language non-null
        <description>

        Use case: <use_case>

        ```<language>
        <code>
        ```

    Code fence info string mirrors the language column (markdown convention).
    Empty info string when language is NULL.
    """
    parts: list[str] = []
    for name, description, language, code, use_case in rows:
        body_lines = [f"### {name}"]
        if language is not None:
            body_lines.append(f"[language: {language}]")
        body_lines.append(str(description))
        body_lines.append("")
        body_lines.append(f"Use case: {use_case}")
        body_lines.append("")
        fence_lang = language if language is not None else ""
        body_lines.append(f"```{fence_lang}")
        body_lines.append(str(code))
        body_lines.append("```")
        parts.append("\n".join(body_lines))
    return "\n\n".join(parts)


def _load_decisions(
    conn: psycopg.Connection, bucket: str, project: str,
) -> ContextBlock | None:
    try:
        with conn.cursor() as cur:
            cur.execute(_L2_DECISIONS_SQL, (bucket, project))
            rows = cur.fetchall()
    except psycopg.Error:
        return None
    content = _render_decisions(list(rows))
    return ContextBlock(
        source="decisions", content=content,
        row_count=len(rows), token_count=count_tokens(content),
    )


def _load_best_practices(
    conn: psycopg.Connection, bucket: str, project: str,
) -> ContextBlock | None:
    try:
        with conn.cursor() as cur:
            cur.execute(_L2_BEST_PRACTICES_SQL, (bucket, project))
            rows = cur.fetchall()
    except psycopg.Error:
        return None
    content = _render_best_practices(list(rows))
    return ContextBlock(
        source="best_practices", content=content,
        row_count=len(rows), token_count=count_tokens(content),
    )


def _load_patterns(
    conn: psycopg.Connection, bucket: str,
) -> ContextBlock | None:
    try:
        with conn.cursor() as cur:
            cur.execute(_L2_PATTERNS_SQL, (bucket,))
            rows = cur.fetchall()
    except psycopg.Error:
        return None
    content = _render_patterns(list(rows))
    return ContextBlock(
        source="patterns", content=content,
        row_count=len(rows), token_count=count_tokens(content),
    )


def load_l2(
    conn: psycopg.Connection,
    bucket: str | None,
    project: str | None,
) -> LayerContent:
    """Assemble L2 (project-scoped context) per contract §3.3.

    Returns loaded=False when bucket is None OR project is None
    (L2 is strictly nested in L1 — no project without a bucket).

    Block order: decisions, best_practices, patterns.
    """
    if bucket is None or project is None:
        return LayerContent(layer="L2", blocks=(), token_count=0, loaded=False)

    blocks: list[ContextBlock] = []
    decisions_block = _load_decisions(conn, bucket, project)
    if decisions_block is not None:
        blocks.append(decisions_block)
    bp_block = _load_best_practices(conn, bucket, project)
    if bp_block is not None:
        blocks.append(bp_block)
    patterns_block = _load_patterns(conn, bucket)
    if patterns_block is not None:
        blocks.append(patterns_block)

    if not blocks:
        return LayerContent(layer="L2", blocks=(), token_count=0, loaded=False)

    return LayerContent(
        layer="L2",
        blocks=tuple(blocks),
        token_count=sum(b.token_count for b in blocks),
        loaded=True,
    )
