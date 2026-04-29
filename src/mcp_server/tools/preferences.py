"""Operator preference tools — UPSERT, get, list, soft-delete.

Operator-controlled facts and overrides (communication style, tooling,
workflow, identity, language, schedule). UNIQUE(category, key, scope)
enables atomic upsert via `ON CONFLICT DO UPDATE`. No embedding —
direct lookup. Soft-delete via `active=false`.

Schema: docs/DATA_MODEL.md §5.8 (table created in migration 0025).
Spec: specs/module-0x-knowledge-architecture/spec.md §5.3.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from .. import db as db_mod
from .. import journal as journal_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)

_LIST_LIMIT_MAX = 500


async def preference_set(
    category: str,
    key: str,
    value: str,
    scope: str = "global",
    source: str = "operator_explicit",
) -> dict[str, Any]:
    """UPSERT an operator preference.

    Creates a new row or updates the existing row matching
    (category, key, scope). Always sets `active=true` so calling
    `preference_set` after `preference_unset` reactivates the row.

    Args:
        category: one of communication|tooling|workflow|identity|language|schedule.
        key: free-form key within the category.
        value: the preference value (text).
        scope: 'global' | 'bucket:<name>' | 'project:<bucket>/<name>'.
        source: one of operator_explicit|inferred|migration.

    Returns:
        {status:'ok', id:uuid, action:'inserted'|'updated'} on success.
        {status:'degraded', journal_id:...} when DB is down.
        {status:'error', error:str} on DB failure.
    """
    payload: dict[str, Any] = {
        "category": category,
        "key": key,
        "value": value,
        "scope": scope,
        "source": source,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("preference_set", payload)
            await log_usage(
                tool_name="preference_set",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO operator_preferences
                            (category, key, value, scope, source)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (category, key, scope) DO UPDATE
                        SET value = EXCLUDED.value,
                            source = EXCLUDED.source,
                            active = true
                        RETURNING id, (xmax = 0) AS inserted
                        """,
                        (category, key, value, scope, source),
                    )
                    row = await cur.fetchone()
                    assert row is not None, "INSERT ... RETURNING produced no row"
                    pref_id = str(row[0])
                    action = "inserted" if row[1] else "updated"
        except Exception as exc:
            log.exception("preference_set failed")
            await log_usage(
                tool_name="preference_set",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="preference_set",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": action, "category": category, "scope": scope},
    )
    return {"status": "ok", "id": pref_id, "action": action}


async def preference_get(
    category: str,
    key: str,
    scope: str = "global",
) -> dict[str, Any]:
    """Return single preference value or null.

    Returns the value regardless of `active` status; the caller decides
    whether to honor a soft-deleted preference.

    Args:
        category: one of communication|tooling|workflow|identity|language|schedule.
        key: free-form key within the category.
        scope: 'global' | 'bucket:<name>' | 'project:<bucket>/<name>'.

    Returns:
        {status:'ok', value:str|None, scope:str, active:bool, found:bool}
        {status:'degraded', degraded_reason:'db_unavailable'} when DB is down.
        {status:'error', error:str} on DB failure.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="preference_get",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", value=None, found=False)

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT value, scope, active
                        FROM operator_preferences
                        WHERE category = %s AND key = %s AND scope = %s
                        LIMIT 1
                        """,
                        (category, key, scope),
                    )
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("preference_get failed")
            await log_usage(
                tool_name="preference_get",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    if row is None:
        await log_usage(
            tool_name="preference_get",
            bucket=None,
            project=None,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"found": False, "category": category, "scope": scope},
        )
        return {"status": "ok", "value": None, "scope": scope, "active": False, "found": False}

    await log_usage(
        tool_name="preference_get",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"found": True, "category": category, "scope": scope},
    )
    return {
        "status": "ok",
        "value": row[0],
        "scope": row[1],
        "active": bool(row[2]),
        "found": True,
    }


async def preference_list(
    category: Optional[str] = None,
    scope: Optional[str] = None,
    active: bool = True,
    limit: int = 100,
) -> dict[str, Any]:
    """List preferences with optional filters.

    Args:
        category: restrict to one category when provided.
        scope: restrict to one scope when provided.
        active: when True, return only rows with active=true; when False,
            return ALL rows regardless of active status.
        limit: clamped to 500.

    Returns:
        {status:'ok', results: [{id, category, key, value, scope, active, source, updated_at}, ...]}
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="preference_list",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", results=[])

        where_parts: list[str] = []
        params: list[Any] = []
        if active:
            where_parts.append("active = true")
        if category is not None:
            where_parts.append("category = %s")
            params.append(category)
        if scope is not None:
            where_parts.append("scope = %s")
            params.append(scope)

        limit_val = max(1, min(int(limit), _LIST_LIMIT_MAX))
        params.append(limit_val)

        where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
        sql = f"""
            SELECT id, category, key, value, scope, active, source, updated_at
            FROM operator_preferences
            {where_sql}
            ORDER BY updated_at DESC
            LIMIT %s
        """

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("preference_list failed")
            await log_usage(
                tool_name="preference_list",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc), "results": []}

    results = [
        {
            "id": str(r[0]),
            "category": r[1],
            "key": r[2],
            "value": r[3],
            "scope": r[4],
            "active": bool(r[5]),
            "source": r[6],
            "updated_at": r[7].isoformat() if r[7] is not None else None,
        }
        for r in rows
    ]

    await log_usage(
        tool_name="preference_list",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}


async def preference_unset(
    category: str,
    key: str,
    scope: str = "global",
) -> dict[str, Any]:
    """Soft-delete: sets active=false. Does not DELETE row.

    Args:
        category: one of communication|tooling|workflow|identity|language|schedule.
        key: free-form key within the category.
        scope: 'global' | 'bucket:<name>' | 'project:<bucket>/<name>'.

    Returns:
        {status:'ok', id:uuid, found:True} when a row was deactivated.
        {status:'ok', found:False} when no row matched.
        {status:'degraded', journal_id:...} when DB is down.
        {status:'error', error:str} on DB failure.
    """
    payload: dict[str, Any] = {
        "category": category,
        "key": key,
        "scope": scope,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("preference_unset", payload)
            await log_usage(
                tool_name="preference_unset",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        UPDATE operator_preferences
                        SET active = false
                        WHERE category = %s AND key = %s AND scope = %s
                        RETURNING id
                        """,
                        (category, key, scope),
                    )
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("preference_unset failed")
            await log_usage(
                tool_name="preference_unset",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    if row is None:
        await log_usage(
            tool_name="preference_unset",
            bucket=None,
            project=None,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"found": False, "category": category, "scope": scope},
        )
        return {"status": "ok", "found": False}

    pref_id = str(row[0])
    await log_usage(
        tool_name="preference_unset",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"found": True, "category": category, "scope": scope},
    )
    return {"status": "ok", "id": pref_id, "found": True}
