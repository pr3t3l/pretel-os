"""L0 layer loader: identity files + operator preferences (contract §3.1).

L0 is always loaded=True. File-backed blocks survive a DB outage — only
the operator_preferences block depends on the database. Block ordering is
pinned per contract §10:

    1. CONSTITUTION.md
    2. IDENTITY.md
    3. AGENTS.md
    4. SOUL.md
    5. operator_preferences (WHERE active=true AND scope='global')

Source labels (the value stored in ContextBlock.source) are uppercase per
contract §10 even when the on-disk filename is lowercase. The label is
the contract identity, not the filename.
"""
from __future__ import annotations

import json
from pathlib import Path

import psycopg

from mcp_server.router._tokens import count_tokens
from mcp_server.router.types import ContextBlock, LayerContent


# Pinned order per contract §10. The first element of each tuple is the
# repo-relative path; the second is the source label used in ContextBlock.
L0_FILES: tuple[tuple[str, str], ...] = (
    ("CONSTITUTION.md", "CONSTITUTION.md"),
    ("identity.md",     "IDENTITY.md"),
    ("AGENTS.md",       "AGENTS.md"),
    ("SOUL.md",         "SOUL.md"),
)


def _load_file_block(repo_root: Path, rel_path: str, source_label: str) -> ContextBlock | None:
    """Read a file-backed L0 block. Returns None if the file is missing."""
    path = repo_root / rel_path
    if not path.is_file():
        return None
    content = path.read_text(encoding="utf-8")
    return ContextBlock(
        source=source_label,
        content=content,
        row_count=None,
        token_count=count_tokens(content),
    )


def _render_value(value: object) -> str:
    """Render a pref value as a single inline string.

    Handles text, JSONB, and other types defensively. JSONB renders as
    compact JSON (no indent) to keep the output one-line-per-pref.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _load_operator_preferences(conn: psycopg.Connection) -> ContextBlock | None:
    """Load global-scope operator preferences from DB.

    Per contract §3.1: WHERE active=true AND scope='global', ORDER BY
    category, key. Render as inline `category.key: value` lines (one
    per row) — qualifying with `category` disambiguates collisions
    where the same key appears under multiple categories.

    Returns None when the DB query raises (degraded mode); the orchestrator
    still emits L0 with loaded=True from the file-backed blocks.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT category, key, value FROM operator_preferences "
                "WHERE active = true AND scope = 'global' "
                "ORDER BY category, key"
            )
            rows = cur.fetchall()
    except psycopg.Error:
        return None

    if not rows:
        return ContextBlock(
            source="operator_preferences",
            content="",
            row_count=0,
            token_count=0,
        )

    content = "\n".join(
        f"{category}.{key}: {_render_value(value)}"
        for category, key, value in rows
    )
    return ContextBlock(
        source="operator_preferences",
        content=content,
        row_count=len(rows),
        token_count=count_tokens(content),
    )


def load_l0(conn: psycopg.Connection, repo_root: Path) -> LayerContent:
    """Assemble L0 in pinned order per contract §10.

    L0 is ALWAYS loaded=True. File-backed blocks survive DB outage
    (operator_preferences may be absent, but the rest still load).
    Missing files are simply omitted from blocks (logged at orchestrator
    level in assemble_bundle); L0 itself stays loaded=True as long as
    at least the file-backed identity is present.
    """
    blocks: list[ContextBlock] = []

    for rel_path, source_label in L0_FILES:
        block = _load_file_block(repo_root, rel_path, source_label)
        if block is not None:
            blocks.append(block)

    prefs_block = _load_operator_preferences(conn)
    if prefs_block is not None:
        blocks.append(prefs_block)

    return LayerContent(
        layer="L0",
        blocks=tuple(blocks),
        token_count=sum(b.token_count for b in blocks),
        loaded=True,
    )
