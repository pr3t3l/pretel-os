"""Tests for load_l0 — identity files + operator_preferences (contract §3.1).

Uses a sync psycopg.Connection against pretel_os_test. Test isolation via
the uncommitted-write pattern: each test inserts prefs in its own
connection (BEGIN implicit), reads via the same connection (sees its own
uncommitted writes), then the fixture teardown rolls back so nothing
persists.

File-backed blocks use a tmp_path fake repo per test so file-missing
scenarios can be exercised without touching the real repo.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

import psycopg
import pytest

from mcp_server.router.load_l0 import (
    L0_FILES,
    _load_operator_preferences,
    load_l0,
)
from mcp_server.router.types import ContextBlock, LayerContent


TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    """Sync connection with autocommit=False; rolled back on teardown."""
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """tmp_path with all 4 L0 files present."""
    (tmp_path / "CONSTITUTION.md").write_text("# Constitution\nrules\n")
    (tmp_path / "identity.md").write_text("# Identity\nfacts\n")
    (tmp_path / "AGENTS.md").write_text("# Agents\nread order\n")
    (tmp_path / "SOUL.md").write_text("# Soul\nvoice\n")
    return tmp_path


def _insert_pref(
    conn: psycopg.Connection,
    *,
    category: str,
    key: str,
    value: str,
    scope: str = "global",
    source: str = "operator_explicit",
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO operator_preferences (category, key, value, scope, source) "
            "VALUES (%s, %s, %s, %s, %s)",
            (category, key, value, scope, source),
        )


# -----------------------------------------------------------------------------
# Happy path + render format
# -----------------------------------------------------------------------------


def test_happy_path_5_blocks_in_pinned_order(
    db_conn: psycopg.Connection, fake_repo: Path
) -> None:
    """All 4 files + at least one global pref → 5 blocks in pinned order."""
    _insert_pref(db_conn, category="communication", key="language", value="english")
    _insert_pref(db_conn, category="tooling", key="editor", value="vim")

    result = load_l0(db_conn, fake_repo)

    assert isinstance(result, LayerContent)
    assert result.layer == "L0"
    assert result.loaded is True
    assert len(result.blocks) == 5
    assert [b.source for b in result.blocks] == [
        "CONSTITUTION.md",
        "IDENTITY.md",
        "AGENTS.md",
        "SOUL.md",
        "operator_preferences",
    ]
    assert result.token_count == sum(b.token_count for b in result.blocks)


def test_pref_render_format_is_inline_category_key_value(
    db_conn: psycopg.Connection, fake_repo: Path
) -> None:
    """Render is exactly `category.key: value\\n...` — no headers, no bullets, no bold."""
    _insert_pref(db_conn, category="communication", key="language", value="english")
    _insert_pref(db_conn, category="tooling", key="editor", value="vim")

    result = load_l0(db_conn, fake_repo)
    prefs_block = result.blocks[-1]

    assert prefs_block.source == "operator_preferences"
    # ORDER BY category, key → communication first, tooling second.
    assert prefs_block.content == "communication.language: english\ntooling.editor: vim"
    # No markdown headers / bullets / bold.
    assert "# " not in prefs_block.content
    assert "## " not in prefs_block.content
    assert "- **" not in prefs_block.content


def test_excludes_bucket_scoped_prefs(
    db_conn: psycopg.Connection, fake_repo: Path
) -> None:
    """Validates contract §3.1: L0 prefs filter is scope='global' only.

    Inserts one global pref + one bucket-scoped pref with the same key.
    L0 must include only the global one.
    """
    _insert_pref(
        db_conn, category="communication", key="language",
        value="spanish", scope="global",
    )
    _insert_pref(
        db_conn, category="communication", key="language",
        value="english", scope="bucket:business",
    )

    result = load_l0(db_conn, fake_repo)
    prefs_block = result.blocks[-1]

    assert prefs_block.row_count == 1
    assert prefs_block.content == "communication.language: spanish"
    assert "english" not in prefs_block.content


# -----------------------------------------------------------------------------
# Missing file (file-backed survives partial)
# -----------------------------------------------------------------------------


def test_missing_file_drops_block_but_l0_still_loaded(
    db_conn: psycopg.Connection, tmp_path: Path
) -> None:
    """SOUL.md absent → 3 file blocks + prefs (or 0 prefs) — L0 stays loaded=True."""
    (tmp_path / "CONSTITUTION.md").write_text("c")
    (tmp_path / "identity.md").write_text("i")
    (tmp_path / "AGENTS.md").write_text("a")
    # SOUL.md intentionally not created

    result = load_l0(db_conn, tmp_path)

    sources = [b.source for b in result.blocks]
    assert "SOUL.md" not in sources
    assert sources[:3] == ["CONSTITUTION.md", "IDENTITY.md", "AGENTS.md"]
    assert result.loaded is True


# -----------------------------------------------------------------------------
# DB unavailable (file-backed survives DB outage)
# -----------------------------------------------------------------------------


def test_db_unavailable_omits_prefs_block(fake_repo: Path) -> None:
    """Closed connection → _load_operator_preferences returns None → only file blocks."""
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    conn.close()  # subsequent operations raise psycopg.InterfaceError (subclass of psycopg.Error)

    result = load_l0(conn, fake_repo)

    assert result.loaded is True
    assert len(result.blocks) == 4  # no prefs block
    assert [b.source for b in result.blocks] == [
        "CONSTITUTION.md",
        "IDENTITY.md",
        "AGENTS.md",
        "SOUL.md",
    ]


# -----------------------------------------------------------------------------
# Empty prefs table — block present with empty content + row_count=0
# -----------------------------------------------------------------------------


def test_empty_prefs_yields_zero_row_block(
    db_conn: psycopg.Connection, fake_repo: Path
) -> None:
    """Prefs query returns 0 rows → block present with content='' and row_count=0."""
    # Make the result deterministically empty by deleting any existing
    # global prefs in this transaction (rolls back on teardown).
    with db_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM operator_preferences WHERE active = true AND scope = 'global'"
        )

    block = _load_operator_preferences(db_conn)

    assert block is not None
    assert block.source == "operator_preferences"
    assert block.content == ""
    assert block.row_count == 0
    assert block.token_count == 0


# -----------------------------------------------------------------------------
# Token count consistency
# -----------------------------------------------------------------------------


def test_token_count_consistency(db_conn: psycopg.Connection, fake_repo: Path) -> None:
    """LayerContent.token_count must equal sum of blocks.token_count."""
    _insert_pref(db_conn, category="schedule", key="standup_time", value="09:00")

    result = load_l0(db_conn, fake_repo)

    expected = sum(b.token_count for b in result.blocks)
    assert result.token_count == expected
    # Also the LayerContent invariant in __post_init__ would have raised
    # if this were inconsistent — this test makes the contract explicit.


# -----------------------------------------------------------------------------
# Real-repo integration test
# -----------------------------------------------------------------------------


def test_real_repo_integration(db_conn: psycopg.Connection) -> None:
    """Real pretel_os_test DB + real repo root.

    Asserts:
      - All 4 file blocks present (CONSTITUTION, IDENTITY, AGENTS, SOUL all
        exist in the actual repo per pre-flight ls)
      - L0 loaded=True
      - IDENTITY.md block ≤1,200 tokens (contract §7 hard budget)
    """
    repo_root = Path(__file__).resolve().parents[2]
    # Sanity: this test only meaningful if the 4 files exist on disk.
    for rel_path, _label in L0_FILES:
        assert (repo_root / rel_path).is_file(), f"missing {rel_path}"

    result = load_l0(db_conn, repo_root)

    assert result.loaded is True
    file_sources = [b.source for b in result.blocks if b.row_count is None]
    assert file_sources == ["CONSTITUTION.md", "IDENTITY.md", "AGENTS.md", "SOUL.md"]

    identity_block = next(b for b in result.blocks if b.source == "IDENTITY.md")
    assert identity_block.token_count <= 1200, (
        f"IDENTITY.md token_count={identity_block.token_count} exceeds "
        "contract §7 hard budget of 1200"
    )
