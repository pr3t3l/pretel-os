"""Integration tests for assemble_bundle (B.9).

Real psycopg + real load_l0..l4. Embedding is monkeypatched in fast
tests (synthetic vector). The slow test exercises the full async
embed() + summarize_oversize round-trip.

Per Q4: assemble_bundle is async with sync conn. Tests are async too
(pytest-asyncio in auto mode handles `async def` tests).
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import psycopg
import pytest

from mcp_server.router.assemble import assemble_bundle
from mcp_server.router.cache import LayerBundleCache
from mcp_server.router.types import ClassifierSignals, LayerBundle


TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"
EMBED_DIM = 3072
REPO_ROOT = Path(__file__).resolve().parents[2]


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def writer_conn() -> Iterator[psycopg.Connection]:
    """autocommit=True writer for triggering NOTIFY."""
    conn = psycopg.connect(TEST_DSN, autocommit=True)
    try:
        yield conn
    finally:
        conn.close()


def _vec(seed: int) -> list[float]:
    v = [0.0] * EMBED_DIM
    v[seed % EMBED_DIM] = 1.0
    return v


def _signals(
    *, bucket: str | None = "business", project: str | None = None,
    needs_lessons: bool = False, needs_skills: bool = False,
    skill_ids: tuple[str, ...] | None = None,
    classifier_domain: str | None = None, complexity: str = "MEDIUM",
) -> ClassifierSignals:
    return ClassifierSignals(
        bucket=bucket, project=project, complexity=complexity,
        needs_lessons=needs_lessons, needs_skills=needs_skills,
        skill_ids=skill_ids, classifier_domain=classifier_domain,
    )


async def _stub_embed(_text: str, vec: list[float] | None = None) -> list[float] | None:
    return vec if vec is not None else _vec(0)


# -----------------------------------------------------------------------------
# Happy path: cache miss -> 5 LayerContent
# -----------------------------------------------------------------------------


async def test_happy_path_cache_miss_returns_five_layers(
    db_conn: psycopg.Connection, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """First call returns LayerBundle with 5 entries, cache_hit=False,
    metadata populated."""
    monkeypatch.setattr(
        "mcp_server.router.assemble.embed",
        lambda text: _stub_embed(text),
    )
    cache = LayerBundleCache()

    result = await assemble_bundle(
        conn=db_conn,
        bucket=None, project=None,
        classifier_signals=_signals(bucket=None, needs_lessons=False),
        repo_root=REPO_ROOT,
        query_text="anything",
        current_time=datetime.now(timezone.utc),
        cache=cache,
    )

    assert isinstance(result, LayerBundle)
    assert len(result.layers) == 5
    assert tuple(L.layer for L in result.layers) == ("L0", "L1", "L2", "L3", "L4")
    assert result.metadata.cache_hit is False
    assert result.metadata.classifier_hash != ""
    assert result.metadata.assembly_latency_ms >= 0
    # L0 is always loaded=True
    assert result.layers[0].loaded is True


# -----------------------------------------------------------------------------
# Cache hit: second call with same signals returns cache_hit=True
# -----------------------------------------------------------------------------


async def test_cache_hit_on_second_call(
    db_conn: psycopg.Connection, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mcp_server.router.assemble.embed",
        lambda text: _stub_embed(text),
    )
    cache = LayerBundleCache()
    sig = _signals(bucket="business", needs_lessons=False)

    first = await assemble_bundle(
        conn=db_conn, bucket="business", project=None,
        classifier_signals=sig, repo_root=REPO_ROOT,
        query_text="x", current_time=datetime.now(timezone.utc),
        cache=cache,
    )
    second = await assemble_bundle(
        conn=db_conn, bucket="business", project=None,
        classifier_signals=sig, repo_root=REPO_ROOT,
        query_text="x", current_time=datetime.now(timezone.utc),
        cache=cache,
    )
    assert first.metadata.cache_hit is False
    assert second.metadata.cache_hit is True
    # Layers identity preserved (same tuple of frozen dataclasses).
    assert second.layers == first.layers


# -----------------------------------------------------------------------------
# Cache invalidation via NOTIFY: writer INSERTs into trigger table -> next
# call is cache_hit=False.
# -----------------------------------------------------------------------------


async def test_cache_invalidation_via_notify(
    db_conn: psycopg.Connection,
    writer_conn: psycopg.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mcp_server.router.assemble.embed",
        lambda text: _stub_embed(text),
    )
    cache = LayerBundleCache()
    cache.start_listener(TEST_DSN)
    try:
        sig = _signals(bucket="business", needs_lessons=False)
        # Allow listener thread to register LISTEN before we proceed.
        time.sleep(0.2)

        first = await assemble_bundle(
            conn=db_conn, bucket="business", project=None,
            classifier_signals=sig, repo_root=REPO_ROOT,
            query_text="x", current_time=datetime.now(timezone.utc),
            cache=cache,
        )
        assert first.metadata.cache_hit is False

        # Trigger NOTIFY by writing to one of the four trigger tables.
        with writer_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO operator_preferences "
                "(category, key, value, scope, source) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                ("workflow", f"assemble_test_{int(time.time()*1000)}",
                 "v", "global", "operator_explicit"),
            )
            inserted_row = cur.fetchone()
        assert inserted_row is not None
        inserted_id = inserted_row[0]

        # Wait for listener to drain.
        deadline = time.time() + 2.0
        while time.time() < deadline and len(cache) > 0:
            time.sleep(0.05)

        # Use a NEW conn for the second call — db_conn's tx is still open
        # after first call and would see inconsistent state.
        third_conn = psycopg.connect(TEST_DSN, autocommit=False)
        try:
            second = await assemble_bundle(
                conn=third_conn, bucket="business", project=None,
                classifier_signals=sig, repo_root=REPO_ROOT,
                query_text="x", current_time=datetime.now(timezone.utc),
                cache=cache,
            )
            assert second.metadata.cache_hit is False, "cache was not invalidated"
        finally:
            third_conn.rollback()
            third_conn.close()

        # Cleanup
        with writer_conn.cursor() as cur:
            cur.execute(
                "DELETE FROM operator_preferences WHERE id = %s", (inserted_id,)
            )
    finally:
        cache.stop_listener()


# -----------------------------------------------------------------------------
# Over-budget L1 triggers summarization + writes a gotcha row
# -----------------------------------------------------------------------------


async def test_over_budget_l1_summarized_and_gotcha_written(
    db_conn: psycopg.Connection, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Insert ~50 huge-decision rows so L1 exceeds 3000-token budget;
    assemble_bundle compresses and writes a gotcha."""
    # Stub embed (not used here since needs_lessons=False)
    monkeypatch.setattr(
        "mcp_server.router.assemble.embed",
        lambda text: _stub_embed(text),
    )
    # Stub summarize_oversize so we don't make a real LLM call in unit tests.
    summarize_calls: list[tuple[str, int]] = []

    def fake_summarize(content: str, target_tokens: int) -> str:
        summarize_calls.append((content[:50], target_tokens))
        # Return a short string deterministically below the target budget.
        return "## Summarized L1\nCompressed bucket-scoped decisions."

    monkeypatch.setattr(
        "mcp_server.router.assemble.summarize_oversize", fake_summarize,
    )

    # Wipe + seed enough decisions to bust the 3000-token L1 budget.
    # Note: L1 SQL applies LEFT(decision, 500) per contract §3.2, so the
    # decision body is capped per row. We compensate by making titles
    # long (not truncated) and seeding many rows. ~40 rows × ~150 tokens
    # = ~6000 tokens, well over the 3000 budget.
    # Diverse English prose tokenizes ~1 token/word; repeated chars
    # tokenize ~1 token / 4 chars. Use prose to make the row payload big.
    big_title_words = (
        "architectural decision regarding postgres connection pooling "
        "strategy with pgbouncer transaction mode and explicit handling "
        "of prepared statements across application restarts and worker "
        "scale events including but not limited to embedding regeneration "
    )  # ~40 tokens of prose per copy
    big_title = (big_title_words * 3).strip()  # ~120 tokens per row title
    with db_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM decisions "
            "WHERE bucket = 'business' OR 'business' = ANY(applicable_buckets)"
        )
        for i in range(40):
            cur.execute(
                "INSERT INTO decisions "
                "(bucket, project, title, context, decision, consequences) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                ("business", "general", f"{big_title} variant {i}", "ctx",
                 "decision body", "consequence"),
            )

    # Snapshot gotchas count BEFORE assemble.
    with db_conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM gotchas WHERE 'over-budget' = ANY(tags)")
        before_count_row = cur.fetchone()
    assert before_count_row is not None
    before_count = before_count_row[0]

    cache = LayerBundleCache()
    result = await assemble_bundle(
        conn=db_conn,
        bucket="business", project=None,
        classifier_signals=_signals(bucket="business", needs_lessons=False),
        repo_root=REPO_ROOT,
        query_text="x",
        current_time=datetime.now(timezone.utc),
        cache=cache,
    )

    # L1 should be marked over-budget.
    assert "L1" in result.metadata.over_budget_layers, (
        f"expected L1 in over_budget_layers, got "
        f"{result.metadata.over_budget_layers}"
    )
    # Layer was rebuilt with the summarized block.
    l1 = result.layers[1]
    assert l1.layer == "L1"
    assert l1.loaded is True
    assert len(l1.blocks) == 1
    assert l1.blocks[0].source == "l1_summarized"
    # Summarize was called exactly once for L1.
    assert len(summarize_calls) == 1
    _content_preview, target = summarize_calls[0]
    assert target == int(3000 * 0.8)  # 80% of L1 budget

    # Gotcha row written.
    with db_conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM gotchas WHERE 'over-budget' = ANY(tags)")
        after_count_row = cur.fetchone()
    assert after_count_row is not None
    assert after_count_row[0] == before_count + 1


# -----------------------------------------------------------------------------
# Degraded mode: closed connection -> file-backed L0 still loads,
# DB-backed layers are skipped (loaded=False).
# -----------------------------------------------------------------------------


async def test_degraded_mode_closed_conn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mcp_server.router.assemble.embed",
        lambda text: _stub_embed(text),
    )
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    conn.close()  # All subsequent queries raise psycopg.Error.

    cache = LayerBundleCache()
    result = await assemble_bundle(
        conn=conn,
        bucket="business", project="some_project",
        classifier_signals=_signals(
            bucket="business", project="some_project",
            needs_lessons=True, needs_skills=True, skill_ids=("a",),
            classifier_domain="process",
        ),
        repo_root=REPO_ROOT,
        query_text="x",
        current_time=datetime.now(timezone.utc),
        cache=cache,
    )

    # L0 file-backed blocks survive DB outage; prefs query failure is
    # internalized to load_l0 (no prefs block).
    assert result.layers[0].layer == "L0"
    assert result.layers[0].loaded is True
    file_sources = [
        b.source for b in result.layers[0].blocks if b.row_count is None
    ]
    assert "CONSTITUTION.md" in file_sources

    # L1..L4 should all have loaded=False (DB queries failed).
    for layer in result.layers[1:]:
        assert layer.loaded is False, f"{layer.layer} should be loaded=False"


# -----------------------------------------------------------------------------
# Slow integration: real embed() + real classifier_default summarize.
# -----------------------------------------------------------------------------


def _real_litellm_key() -> str | None:
    path = os.path.expanduser("~/.env.litellm")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for line in f:
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1].strip()
    return None


@pytest.mark.slow
async def test_real_embed_and_summarize_e2e(
    db_conn: psycopg.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Full real-world round-trip: embed via OpenAI, decisions over budget,
    summarize via classifier_default. Cost ~$0.002 per run."""
    key = _real_litellm_key()
    if not key:
        pytest.skip("real LITELLM_MASTER_KEY not present")
    monkeypatch.setenv("LITELLM_API_KEY", key)

    # Seed an over-budget L1 (real summarize call exercised). Same
    # pattern as the fast over-budget test: long titles + many rows so
    # the L1 SQL's LEFT(decision,500) cap doesn't keep us under budget.
    big_title_words = (
        "architectural decision regarding postgres connection pooling "
        "strategy with pgbouncer transaction mode and explicit handling "
        "of prepared statements across application restarts and worker "
        "scale events including but not limited to embedding regeneration "
    )
    big_title = (big_title_words * 3).strip()
    with db_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM decisions "
            "WHERE bucket = 'business' OR 'business' = ANY(applicable_buckets)"
        )
        for i in range(40):
            cur.execute(
                "INSERT INTO decisions "
                "(bucket, project, title, context, decision, consequences) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                ("business", "general", f"{big_title} variant {i}",
                 "context", "decision body", "csq"),
            )

    cache = LayerBundleCache()
    result = await assemble_bundle(
        conn=db_conn,
        bucket="business", project=None,
        classifier_signals=_signals(
            bucket="business", needs_lessons=True,
            classifier_domain="process",
        ),
        repo_root=REPO_ROOT,
        query_text="postgres optimization for vector search",
        current_time=datetime.now(timezone.utc),
        cache=cache,
    )

    assert result.metadata.cache_hit is False
    assert "L1" in result.metadata.over_budget_layers
    l1 = result.layers[1]
    assert l1.blocks[0].source == "l1_summarized"
    # Summary should fit budget (target was 80% of 3000 = 2400, with some
    # variance from the LLM; assert a generous ceiling).
    assert l1.token_count < 3000
