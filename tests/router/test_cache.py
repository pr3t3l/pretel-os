"""Tests for B.8 — classifier_hash determinism + LayerBundleCache + NOTIFY listener.

Integration test exercises the full LISTEN/NOTIFY round-trip via real
psycopg connections to pretel_os_test (migration 0031 must be applied
— pre-flight asserts the triggers exist).
"""
from __future__ import annotations

import time
from typing import Iterator

import psycopg
import pytest

from mcp_server.router._classifier_hash import classifier_hash
from mcp_server.router.cache import LayerBundleCache, NOTIFY_CHANNEL
from mcp_server.router.types import (
    BundleMetadata,
    ContextBlock,
    LayerBundle,
    LayerContent,
)


TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


def _make_empty_layer(layer: str) -> LayerContent:
    return LayerContent(layer=layer, blocks=(), token_count=0, loaded=False)


def _make_bundle(bucket: str = "business", total: int = 0) -> LayerBundle:
    """Build a synthetic empty bundle for cache-key testing."""
    layers = tuple(_make_empty_layer(L) for L in ("L0", "L1", "L2", "L3", "L4"))
    return LayerBundle(
        layers=layers,
        metadata=BundleMetadata(
            bucket=bucket, project=None, classifier_hash="abc123",
            total_tokens=total, assembly_latency_ms=0, cache_hit=False,
        ),
    )


@pytest.fixture
def writer_conn() -> Iterator[psycopg.Connection]:
    """Separate sync connection used to fire NOTIFYs by mutating tables.

    autocommit=True so triggers/notifies fire immediately on each
    INSERT — listeners on a different connection receive them without
    waiting for a manual commit.
    """
    conn = psycopg.connect(TEST_DSN, autocommit=True)
    try:
        yield conn
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# classifier_hash determinism
# -----------------------------------------------------------------------------


def test_hash_is_deterministic_across_calls() -> None:
    h1 = classifier_hash(
        bucket="business", project="declassified", complexity="MEDIUM",
        needs_lessons=True, needs_skills=False, skill_ids=None,
    )
    h2 = classifier_hash(
        bucket="business", project="declassified", complexity="MEDIUM",
        needs_lessons=True, needs_skills=False, skill_ids=None,
    )
    assert h1 == h2
    assert len(h1) == 16


def test_hash_changes_when_any_field_changes() -> None:
    base = classifier_hash(
        bucket="business", project=None, complexity="LOW",
        needs_lessons=False, needs_skills=False, skill_ids=None,
    )
    variations = [
        classifier_hash(bucket="personal", project=None, complexity="LOW",
                        needs_lessons=False, needs_skills=False, skill_ids=None),
        classifier_hash(bucket="business", project="x", complexity="LOW",
                        needs_lessons=False, needs_skills=False, skill_ids=None),
        classifier_hash(bucket="business", project=None, complexity="HIGH",
                        needs_lessons=False, needs_skills=False, skill_ids=None),
        classifier_hash(bucket="business", project=None, complexity="LOW",
                        needs_lessons=True, needs_skills=False, skill_ids=None),
        classifier_hash(bucket="business", project=None, complexity="LOW",
                        needs_lessons=False, needs_skills=True, skill_ids=None),
        classifier_hash(bucket="business", project=None, complexity="LOW",
                        needs_lessons=False, needs_skills=False, skill_ids=("a",)),
        classifier_hash(bucket="business", project=None, complexity="LOW",
                        needs_lessons=False, needs_skills=False, skill_ids=None,
                        classifier_domain="process"),
    ]
    for v in variations:
        assert v != base, f"expected hash to differ from base for variation"


def test_empty_skill_ids_normalized_to_none() -> None:
    """Per docstring: skill_ids=() and skill_ids=None hash the same."""
    h_none = classifier_hash(
        bucket="business", project=None, complexity="LOW",
        needs_lessons=False, needs_skills=False, skill_ids=None,
    )
    h_empty = classifier_hash(
        bucket="business", project=None, complexity="LOW",
        needs_lessons=False, needs_skills=False, skill_ids=(),
    )
    assert h_none == h_empty


def test_skill_ids_order_matters() -> None:
    """skill_ids is a tuple — order is significant."""
    h_ab = classifier_hash(
        bucket="business", project=None, complexity="LOW",
        needs_lessons=False, needs_skills=True, skill_ids=("a", "b"),
    )
    h_ba = classifier_hash(
        bucket="business", project=None, complexity="LOW",
        needs_lessons=False, needs_skills=True, skill_ids=("b", "a"),
    )
    assert h_ab != h_ba


# -----------------------------------------------------------------------------
# LayerBundleCache get/put/invalidate (no listener)
# -----------------------------------------------------------------------------


def test_cache_get_returns_none_for_missing_key() -> None:
    cache = LayerBundleCache()
    assert cache.get(("business", None, "abc")) is None


def test_cache_put_then_get_returns_same_bundle() -> None:
    cache = LayerBundleCache()
    bundle = _make_bundle()
    cache.put(("business", None, "abc"), bundle)
    fetched = cache.get(("business", None, "abc"))
    assert fetched is bundle


def test_cache_invalidate_all_clears_everything() -> None:
    cache = LayerBundleCache()
    cache.put(("a", None, "h1"), _make_bundle("a"))
    cache.put(("b", None, "h2"), _make_bundle("b"))
    assert len(cache) == 2
    cache.invalidate_all()
    assert len(cache) == 0


def test_cache_eviction_when_max_entries_exceeded() -> None:
    cache = LayerBundleCache(max_entries=3)
    cache.put(("a", None, "h1"), _make_bundle("a"))
    cache.put(("b", None, "h2"), _make_bundle("b"))
    cache.put(("c", None, "h3"), _make_bundle("c"))
    assert len(cache) == 3
    cache.put(("d", None, "h4"), _make_bundle("d"))   # evicts oldest ("a")
    assert len(cache) == 3
    assert cache.get(("a", None, "h1")) is None
    assert cache.get(("d", None, "h4")) is not None


# -----------------------------------------------------------------------------
# LISTEN/NOTIFY round-trip — real DB
# -----------------------------------------------------------------------------


def test_notify_invalidates_cache(writer_conn: psycopg.Connection) -> None:
    """End-to-end: writer INSERTs a row in a contract §6 table; listener
    receives the notification and clears the cache.

    Uses a unique bucket scope on operator_preferences to avoid colliding
    with other test data. Cleans up the row at the end.
    """
    cache = LayerBundleCache()
    cache.put(("business", None, "h"), _make_bundle())
    assert len(cache) == 1

    cache.start_listener(TEST_DSN)
    try:
        # Give the listener a moment to register the LISTEN.
        time.sleep(0.2)

        # Trigger a NOTIFY by writing to operator_preferences.
        with writer_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO operator_preferences "
                "(category, key, value, scope, source) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("workflow", f"cache_test_{int(time.time()*1000)}",
                 "v", "global", "operator_explicit"),
            )
            inserted_id_row = None
            cur.execute(
                "SELECT id FROM operator_preferences "
                "WHERE key LIKE 'cache_test_%' ORDER BY created_at DESC LIMIT 1"
            )
            inserted_id_row = cur.fetchone()
        assert inserted_id_row is not None
        inserted_id = inserted_id_row[0]

        # Wait up to 2 seconds for the listener to drain the notification.
        deadline = time.time() + 2.0
        while time.time() < deadline:
            if len(cache) == 0:
                break
            time.sleep(0.05)

        assert len(cache) == 0, "cache was not invalidated within 2s"

        # Cleanup the inserted row.
        with writer_conn.cursor() as cur:
            cur.execute(
                "DELETE FROM operator_preferences WHERE id = %s",
                (inserted_id,),
            )
    finally:
        cache.stop_listener()


def test_listener_can_be_started_twice_safely() -> None:
    """Calling start_listener twice should not raise; second call is a no-op."""
    cache = LayerBundleCache()
    cache.start_listener(TEST_DSN)
    try:
        cache.start_listener(TEST_DSN)  # no-op, just logs a warning
        # Cache still functional
        cache.put(("a", None, "h"), _make_bundle())
        assert cache.get(("a", None, "h")) is not None
    finally:
        cache.stop_listener()
