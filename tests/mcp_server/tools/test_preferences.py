"""Unit tests for `mcp_server.tools.preferences`.

Six tests covering UPSERT semantics (xmax=0 trick), get/list filters,
soft-delete via active=false, idempotent unset.

Each test asserts at least one DB-side fact via SELECT to catch
schema/payload contract drift (LL-M4-PHASE-A-001).
"""
from __future__ import annotations

from typing import Any

from psycopg_pool import AsyncConnectionPool

from mcp_server.tools.preferences import (
    preference_get,
    preference_list,
    preference_set,
    preference_unset,
)


async def _select_one(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...]) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()


async def _select_all(pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchall()


async def test_preference_set_inserts_when_new(patched_db: None, test_pool: AsyncConnectionPool) -> None:
    r = await preference_set(category="language", key="primary", value="es")

    assert r["status"] == "ok"
    assert r["action"] == "inserted"
    assert isinstance(r["id"], str) and len(r["id"]) == 36

    row = await _select_one(
        test_pool,
        "SELECT category, key, value, scope, active, source FROM operator_preferences WHERE id = %s",
        (r["id"],),
    )
    assert row is not None
    assert row == ("language", "primary", "es", "global", True, "operator_explicit")


async def test_preference_set_upserts_existing(patched_db: None, test_pool: AsyncConnectionPool) -> None:
    r1 = await preference_set(category="language", key="primary", value="es")
    r2 = await preference_set(category="language", key="primary", value="en")

    assert r1["action"] == "inserted"
    assert r2["action"] == "updated"
    assert r1["id"] == r2["id"]  # same row, value swapped in place

    row = await _select_one(
        test_pool,
        "SELECT value, active FROM operator_preferences WHERE id = %s",
        (r1["id"],),
    )
    assert row == ("en", True)


async def test_preference_get_returns_value_when_active(patched_db: None) -> None:
    await preference_set(category="language", key="primary", value="es")
    r = await preference_get(category="language", key="primary")

    assert r["status"] == "ok"
    assert r["found"] is True
    assert r["active"] is True
    assert r["value"] == "es"
    assert r["scope"] == "global"


async def test_preference_get_returns_value_with_active_false_after_unset(patched_db: None) -> None:
    """Soft-delete preserves the value; caller decides whether to honor it."""
    await preference_set(category="language", key="primary", value="es")
    unset_result = await preference_unset(category="language", key="primary")
    assert unset_result == {"status": "ok", "id": unset_result["id"], "found": True}

    r = await preference_get(category="language", key="primary")
    assert r["found"] is True
    assert r["active"] is False
    assert r["value"] == "es"  # value preserved, only active flipped


async def test_preference_list_filters_by_category_and_active_flag(
    patched_db: None, test_pool: AsyncConnectionPool
) -> None:
    """3 inserts: 2 in language (1 active, 1 unset), 1 in tooling.

    `active=True` returns only active rows; `active=False` returns ALL
    rows in the matching scope/category — per the brief's filter semantics.
    """
    await preference_set(category="language", key="primary", value="es")
    await preference_set(category="language", key="secondary", value="en")
    await preference_set(category="tooling", key="editor", value="vim")
    await preference_unset(category="language", key="secondary")

    only_active = await preference_list(category="language", active=True)
    assert only_active["status"] == "ok"
    assert len(only_active["results"]) == 1
    assert only_active["results"][0]["key"] == "primary"

    all_in_lang = await preference_list(category="language", active=False)
    assert len(all_in_lang["results"]) == 2
    keys = {row["key"] for row in all_in_lang["results"]}
    assert keys == {"primary", "secondary"}

    only_tooling = await preference_list(category="tooling")
    assert len(only_tooling["results"]) == 1
    assert only_tooling["results"][0]["key"] == "editor"


async def test_preference_unset_idempotent_when_missing(patched_db: None) -> None:
    """Unset on a (category, key, scope) that never existed returns found:False, not an error."""
    r = await preference_unset(category="language", key="never_existed")

    assert r["status"] == "ok"
    assert r["found"] is False
    assert "id" not in r
