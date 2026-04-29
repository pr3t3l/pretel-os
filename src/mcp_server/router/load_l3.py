"""L3 layer loader: skill catalog (contract §3.4).

Single DB-backed source per contract §3.4:
    tools_catalog WHERE kind='skill' AND name = ANY($1::text[])

The skill_ids list is computed by the Router orchestrator from
classifier_signals.needs_skills + the picked skill names. Phase B
receives the resolved list — no signal processing here.

Signature follows contract §3.4 + plan §4.2 (post-M4.reconcile):
    load_l3(conn, skill_ids: list[str] | None) -> LayerContent

NO bucket filter. Contract §3.4 is silent on bucket; the brief's
implicit bucket-isolation expectation was stale. Skills are
buckets-agnostic from Phase B's perspective.

Loaded decision tree:
    skill_ids is None                           → loaded=False, blocks=()
    skill_ids == []                             → loaded=False, blocks=()
    skill_ids = [...], DB error                 → loaded=False, blocks=()
    skill_ids = [...], query OK, rows found     → loaded=True, 1 block
    skill_ids = [...], query OK, 0 rows         → loaded=True, 1 block
                                                  (content="", row_count=0)

The "0 rows but loaded=True" case is intentional: the Router asked
for skills, the query succeeded, none matched. That's useful information
to surface (distinguishes "no skills wanted" from "skills wanted but
none available").
"""
from __future__ import annotations

import psycopg

from mcp_server.router._tokens import count_tokens
from mcp_server.router.types import ContextBlock, LayerContent


_L3_SKILLS_SQL = """
SELECT name, description_full
FROM tools_catalog
WHERE kind = 'skill'
  AND name = ANY(%s::text[])
ORDER BY name
"""


def _render_skills(rows: list[tuple[object, ...]]) -> str:
    """Render skills per the per-entry pattern.

    Layout per entry:
        ### <name>
        <description_full>

    No metadata badge — skills are atomic, no severity / domain / language
    fields to surface.
    """
    parts: list[str] = []
    for name, description_full in rows:
        parts.append(f"### {name}\n{description_full}")
    return "\n\n".join(parts)


def load_l3(
    conn: psycopg.Connection,
    skill_ids: list[str] | None,
) -> LayerContent:
    """Assemble L3 (skills) per contract §3.4.

    Args:
        conn: sync psycopg connection.
        skill_ids: list of tools_catalog.name values to load. None means
                   the Router did not request skills (skill_ids resolution
                   lives in assemble_bundle, not here).

    Returns:
        LayerContent with at most 1 block (source='tools_catalog'). See
        module docstring for the full loaded/blocks decision tree.
    """
    if skill_ids is None or len(skill_ids) == 0:
        return LayerContent(layer="L3", blocks=(), token_count=0, loaded=False)

    try:
        with conn.cursor() as cur:
            cur.execute(_L3_SKILLS_SQL, (skill_ids,))
            rows = cur.fetchall()
    except psycopg.Error:
        return LayerContent(layer="L3", blocks=(), token_count=0, loaded=False)

    content = _render_skills(list(rows))
    block = ContextBlock(
        source="tools_catalog",
        content=content,
        row_count=len(rows),
        token_count=count_tokens(content),
    )
    return LayerContent(
        layer="L3",
        blocks=(block,),
        token_count=block.token_count,
        loaded=True,
    )
