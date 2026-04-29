"""Tests for load_l3 — skill catalog (contract §3.4).

Same isolation pattern as B.2/B.3/B.4: sync psycopg, autocommit=False, rollback.

Note: contract §3.4 is silent on bucket filtering for L3. The brief's
proposed bucket-isolation test was stale; we omit it. Skills are
identified by name (the skill_ids list parameter), not by bucket scope.
"""
from __future__ import annotations

from typing import Iterator

import psycopg
import pytest

from mcp_server.router.load_l3 import load_l3
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


def _insert_catalog_row(
    conn: psycopg.Connection, *,
    name: str, kind: str, description_short: str = "short", description_full: str = "full",
    applicable_buckets: list[str] | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tools_catalog "
            "(name, kind, description_short, description_full, applicable_buckets) "
            "VALUES (%s, %s::catalog_kind, %s, %s, %s)",
            (name, kind, description_short, description_full, applicable_buckets or []),
        )


def _wipe_catalog(conn: psycopg.Connection, names: list[str]) -> None:
    """Delete prior rows by name to keep the test deterministic against
    the seeded production tools_catalog."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tools_catalog WHERE name = ANY(%s)", (names,))


# -----------------------------------------------------------------------------
# Happy path
# -----------------------------------------------------------------------------


def test_happy_path_skills_loaded(db_conn: psycopg.Connection) -> None:
    names = ["sk_alpha", "sk_beta"]
    _wipe_catalog(db_conn, names)
    _insert_catalog_row(db_conn, name="sk_alpha", kind="skill",
                        description_full="Alpha skill body")
    _insert_catalog_row(db_conn, name="sk_beta", kind="skill",
                        description_full="Beta skill body")

    result = load_l3(db_conn, names)

    assert isinstance(result, LayerContent)
    assert result.layer == "L3"
    assert result.loaded is True
    assert len(result.blocks) == 1
    block = result.blocks[0]
    assert block.source == "tools_catalog"
    assert block.row_count == 2
    assert "Alpha skill body" in block.content
    assert "Beta skill body" in block.content


# -----------------------------------------------------------------------------
# skill_ids=None → loaded=False
# -----------------------------------------------------------------------------


def test_skill_ids_none_returns_skipped_layer(db_conn: psycopg.Connection) -> None:
    """skill_ids=None means the Router did not request skills."""
    result = load_l3(db_conn, None)
    assert result.loaded is False
    assert result.blocks == ()
    assert result.token_count == 0


# -----------------------------------------------------------------------------
# skill_ids=[] → loaded=False
# -----------------------------------------------------------------------------


def test_skill_ids_empty_returns_skipped_layer(db_conn: psycopg.Connection) -> None:
    """skill_ids=[] means classifier resolved to zero skills — skip layer."""
    result = load_l3(db_conn, [])
    assert result.loaded is False
    assert result.blocks == ()
    assert result.token_count == 0


# -----------------------------------------------------------------------------
# skill_ids=['nonexistent'] → loaded=True with empty block
# -----------------------------------------------------------------------------


def test_nonexistent_skill_id_emits_empty_loaded_block(
    db_conn: psycopg.Connection,
) -> None:
    """Router asked for a skill, query succeeded, 0 rows — emit empty block, loaded=True.

    Distinct from skill_ids=None (router didn't ask). The empty block
    surfaces "skills wanted but none matched" to the consumer.
    """
    _wipe_catalog(db_conn, ["sk_does_not_exist"])

    result = load_l3(db_conn, ["sk_does_not_exist"])

    assert result.loaded is True
    assert len(result.blocks) == 1
    block = result.blocks[0]
    assert block.source == "tools_catalog"
    assert block.row_count == 0
    assert block.content == ""
    assert block.token_count == 0


# -----------------------------------------------------------------------------
# DB unavailable → loaded=False
# -----------------------------------------------------------------------------


def test_db_unavailable_loaded_false() -> None:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    conn.close()

    result = load_l3(conn, ["any_skill"])

    assert result.loaded is False
    assert result.blocks == ()


# -----------------------------------------------------------------------------
# kind filter — kind='tool' rows must NOT appear in L3
# -----------------------------------------------------------------------------


def test_kind_filter_excludes_non_skills(db_conn: psycopg.Connection) -> None:
    """tools_catalog rows with kind='tool' (not 'skill') must be filtered out."""
    names = ["sk_real", "tool_imposter"]
    _wipe_catalog(db_conn, names)
    _insert_catalog_row(db_conn, name="sk_real", kind="skill",
                        description_full="real skill")
    _insert_catalog_row(db_conn, name="tool_imposter", kind="tool",
                        description_full="not a skill")

    # Even though both names are in skill_ids, only kind='skill' should match.
    result = load_l3(db_conn, names)

    assert result.loaded is True
    block = result.blocks[0]
    assert block.row_count == 1
    assert "real skill" in block.content
    assert "not a skill" not in block.content


# -----------------------------------------------------------------------------
# Token count consistency
# -----------------------------------------------------------------------------


def test_token_count_consistency(db_conn: psycopg.Connection) -> None:
    names = ["sk_for_tokens"]
    _wipe_catalog(db_conn, names)
    _insert_catalog_row(db_conn, name="sk_for_tokens", kind="skill",
                        description_full="some content for token counting")

    result = load_l3(db_conn, names)
    assert result.token_count == sum(b.token_count for b in result.blocks)


# -----------------------------------------------------------------------------
# Render format
# -----------------------------------------------------------------------------


def test_skills_render_format(db_conn: psycopg.Connection) -> None:
    """Render: '### <name>\\n<description_full>' per entry, blank line between."""
    names = ["sk_a", "sk_b"]
    _wipe_catalog(db_conn, names)
    _insert_catalog_row(db_conn, name="sk_a", kind="skill",
                        description_full="Body of A")
    _insert_catalog_row(db_conn, name="sk_b", kind="skill",
                        description_full="Body of B")

    result = load_l3(db_conn, names)
    block = result.blocks[0]
    expected = (
        "### sk_a\n"
        "Body of A\n"
        "\n"
        "### sk_b\n"
        "Body of B"
    )
    assert block.content == expected
