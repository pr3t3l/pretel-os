"""Task management tools — create, list, update, close, reopen.

Pending and in-progress work items. No embedding — structured query only.
Self-referential FK on `blocked_by` for dependency chains. CHECK
constraints on `status` (5 values) and `priority` (4 values).

Schema: docs/DATA_MODEL.md §5.7 (table created in migration 0024).
Spec: specs/module-0x-knowledge-architecture/spec.md §5.1.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from .. import db as db_mod
from .. import journal as journal_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)

_LIST_LIMIT_MAX = 200

# Whitelist of columns task_update is allowed to modify.
# Building SET clauses from this list (not from the kwarg dict directly)
# prevents SQL injection via crafted parameter names.
_UPDATABLE_COLUMNS: frozenset[str] = frozenset({
    "title",
    "description",
    "status",
    "priority",
    "blocked_by",
    "trigger_phase",
    "estimated_minutes",
    "github_issue_url",
})


async def task_create(
    title: str,
    bucket: str,
    source: str,
    description: Optional[str] = None,
    project: Optional[str] = None,
    module: Optional[str] = None,
    priority: str = "normal",
    trigger_phase: Optional[str] = None,
    estimated_minutes: Optional[int] = None,
    blocked_by: Optional[str] = None,
    github_issue_url: Optional[str] = None,
) -> dict[str, Any]:
    """Create a task.

    Default status='open'. When `blocked_by` is provided, the new task
    starts in status='blocked' instead — caller can flip it back to
    'open' via `task_update` once the blocker is resolved.

    Args:
        title: short headline.
        bucket: 'personal' | 'business' | 'scout'.
        source: one of operator | claude | reflection_worker | migration.
        description: optional body.
        project: project slug within the bucket (optional).
        module: module identifier (e.g. 'M4', 'M0.X') (optional).
        priority: urgent | high | normal | low (default 'normal').
        trigger_phase: free-form phase trigger (e.g. 'Phase D', 'before Module 5').
        estimated_minutes: rough estimate (optional).
        blocked_by: uuid of another task that blocks this one (optional).
        github_issue_url: backref to GitHub issue (optional).

    Returns:
        {status:'ok', id:uuid, status_value:'open'|'blocked'} on success.
        {status:'degraded', journal_id:...} when DB is down.
        {status:'error', error:str} on DB failure.
    """
    payload: dict[str, Any] = {
        "title": title,
        "bucket": bucket,
        "source": source,
        "description": description,
        "project": project,
        "module": module,
        "priority": priority,
        "trigger_phase": trigger_phase,
        "estimated_minutes": estimated_minutes,
        "blocked_by": blocked_by,
        "github_issue_url": github_issue_url,
    }
    initial_status = "blocked" if blocked_by is not None else "open"

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("task_create", payload)
            await log_usage(
                tool_name="task_create",
                bucket=bucket,
                project=project,
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
                        INSERT INTO tasks (
                            title, description, bucket, project, module,
                            status, priority, blocked_by, trigger_phase,
                            source, estimated_minutes, github_issue_url
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s
                        ) RETURNING id, status
                        """,
                        (
                            title, description, bucket, project, module,
                            initial_status, priority, blocked_by, trigger_phase,
                            source, estimated_minutes, github_issue_url,
                        ),
                    )
                    row = await cur.fetchone()
                    assert row is not None, "INSERT ... RETURNING produced no row"
                    task_id = str(row[0])
                    status_value = str(row[1])
        except Exception as exc:
            log.exception("task_create failed")
            await log_usage(
                tool_name="task_create",
                bucket=bucket,
                project=project,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="task_create",
        bucket=bucket,
        project=project,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": "inserted", "status": status_value, "module": module},
    )
    return {"status": "ok", "id": task_id, "status_value": status_value}


async def task_list(
    bucket: Optional[str] = None,
    status: Optional[str] = None,
    module: Optional[str] = None,
    trigger_phase: Optional[str] = None,
    limit: int = 50,
) -> dict[str, Any]:
    """List tasks with optional filters.

    Default ordering: priority (urgent→high→normal→low), then created_at ASC.
    When filtering by `status='done'`, ordering switches to `done_at DESC`
    so the most recently closed work surfaces first.

    Args:
        bucket: restrict to one bucket when provided.
        status: exact status filter (one of open|in_progress|blocked|done|cancelled).
        module: exact module filter (e.g. 'M4').
        trigger_phase: exact trigger_phase filter.
        limit: clamped to 200.

    Returns:
        {status:'ok', results: [{id, title, bucket, status, priority, module,
                                 trigger_phase, created_at, done_at}, ...]}
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="task_list",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", results=[])

        where_parts: list[str] = []
        params: list[Any] = []
        if bucket is not None:
            where_parts.append("bucket = %s")
            params.append(bucket)
        if status is not None:
            where_parts.append("status = %s")
            params.append(status)
        if module is not None:
            where_parts.append("module = %s")
            params.append(module)
        if trigger_phase is not None:
            where_parts.append("trigger_phase = %s")
            params.append(trigger_phase)

        if status == "done":
            order_sql = "done_at DESC NULLS LAST"
        else:
            order_sql = (
                "CASE priority "
                "WHEN 'urgent' THEN 1 "
                "WHEN 'high' THEN 2 "
                "WHEN 'normal' THEN 3 "
                "WHEN 'low' THEN 4 "
                "ELSE 5 END, "
                "created_at ASC"
            )

        limit_val = max(1, min(int(limit), _LIST_LIMIT_MAX))
        params.append(limit_val)

        where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
        sql = f"""
            SELECT id, title, bucket, status, priority, module,
                   trigger_phase, created_at, done_at
            FROM tasks
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s
        """

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("task_list failed")
            await log_usage(
                tool_name="task_list",
                bucket=bucket,
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
            "title": r[1],
            "bucket": r[2],
            "status": r[3],
            "priority": r[4],
            "module": r[5],
            "trigger_phase": r[6],
            "created_at": r[7].isoformat() if r[7] is not None else None,
            "done_at": r[8].isoformat() if r[8] is not None else None,
        }
        for r in rows
    ]

    await log_usage(
        tool_name="task_list",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}


async def task_update(
    id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    blocked_by: Optional[str] = None,
    trigger_phase: Optional[str] = None,
    estimated_minutes: Optional[int] = None,
    github_issue_url: Optional[str] = None,
) -> dict[str, Any]:
    """Partial update — only fields with non-None values are changed.

    The set of updatable columns is whitelisted via `_UPDATABLE_COLUMNS`
    (not derived from kwarg names) so a renamed parameter cannot become
    a SQL injection vector.

    Args:
        id: task uuid (required).
        Other args are optional; only non-None values are written.

    Returns:
        {status:'ok', id:uuid, status_value:str, found:True} on success.
        {status:'ok', found:False} when no row matches `id`.
        {status:'error', error:'no fields to update'} when every optional
        kwarg was None.
        {status:'degraded', journal_id:...} when DB is down.
    """
    candidate_updates: dict[str, Any] = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "blocked_by": blocked_by,
        "trigger_phase": trigger_phase,
        "estimated_minutes": estimated_minutes,
        "github_issue_url": github_issue_url,
    }
    updates: dict[str, Any] = {
        col: val
        for col, val in candidate_updates.items()
        if val is not None and col in _UPDATABLE_COLUMNS
    }

    if not updates:
        return {"status": "error", "error": "no fields to update"}

    payload: dict[str, Any] = {"id": id, **updates}

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("task_update", payload)
            await log_usage(
                tool_name="task_update",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        ordered_cols = list(updates.keys())
        set_clauses = ", ".join(f"{col} = %s" for col in ordered_cols)
        sql = f"""
            UPDATE tasks
            SET {set_clauses}
            WHERE id = %s
            RETURNING id, status
        """
        params: list[Any] = [updates[col] for col in ordered_cols] + [id]

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("task_update failed")
            await log_usage(
                tool_name="task_update",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc), "id": id},
            )
            return {"status": "error", "error": str(exc)}

    if row is None:
        await log_usage(
            tool_name="task_update",
            bucket=None,
            project=None,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"result": "not_found", "id": id},
        )
        return {"status": "ok", "found": False}

    task_id = str(row[0])
    status_value = str(row[1])
    await log_usage(
        tool_name="task_update",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": "updated", "id": task_id, "fields": list(updates.keys())},
    )
    return {"status": "ok", "id": task_id, "status_value": status_value, "found": True}


async def task_close(
    id: str,
    completion_note: Optional[str] = None,
) -> dict[str, Any]:
    """Mark a task done. Sets status='done', done_at=now().

    Optional `completion_note` is merged into `metadata` as a top-level
    `completion_note` key. Re-closing an already-done task is a no-op
    (the WHERE filter excludes status='done' rows) and returns found=False.

    Args:
        id: task uuid.
        completion_note: optional human-readable closure note.

    Returns:
        {status:'ok', id:uuid, found:True} on success.
        {status:'ok', found:False} when no open row matches `id`.
        {status:'degraded', journal_id:...} when DB is down.
    """
    payload: dict[str, Any] = {"id": id, "completion_note": completion_note}

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("task_close", payload)
            await log_usage(
                tool_name="task_close",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        if completion_note is not None:
            sql = """
                UPDATE tasks
                SET status = 'done',
                    done_at = now(),
                    metadata = metadata || jsonb_build_object('completion_note', %s::text)
                WHERE id = %s AND status != 'done'
                RETURNING id
            """
            params: list[Any] = [completion_note, id]
        else:
            sql = """
                UPDATE tasks
                SET status = 'done',
                    done_at = now()
                WHERE id = %s AND status != 'done'
                RETURNING id
            """
            params = [id]

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("task_close failed")
            await log_usage(
                tool_name="task_close",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc), "id": id},
            )
            return {"status": "error", "error": str(exc)}

    if row is None:
        await log_usage(
            tool_name="task_close",
            bucket=None,
            project=None,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"result": "not_found_or_already_done", "id": id},
        )
        return {"status": "ok", "found": False}

    task_id = str(row[0])
    await log_usage(
        tool_name="task_close",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": "closed", "id": task_id, "had_note": completion_note is not None},
    )
    return {"status": "ok", "id": task_id, "found": True}


async def task_reopen(id: str, reason: str) -> dict[str, Any]:
    """Reopen a task. Sets status='open', clears done_at, appends to metadata.reopened_history.

    `reason` is required so reopen events leave an audit trail. The
    reopened_history array accumulates entries `{at, reason}` across the
    lifetime of the task.

    Args:
        id: task uuid.
        reason: why the task is being reopened (required).

    Returns:
        {status:'ok', id:uuid, found:True} on success.
        {status:'ok', found:False} when no row matches `id`.
        {status:'degraded', journal_id:...} when DB is down.
    """
    payload: dict[str, Any] = {"id": id, "reason": reason}

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("task_reopen", payload)
            await log_usage(
                tool_name="task_reopen",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        sql = """
            UPDATE tasks
            SET status = 'open',
                done_at = NULL,
                metadata = jsonb_set(
                    metadata,
                    '{reopened_history}',
                    COALESCE(metadata -> 'reopened_history', '[]'::jsonb)
                        || jsonb_build_array(
                               jsonb_build_object('at', now(), 'reason', %s::text)
                           )
                )
            WHERE id = %s
            RETURNING id
        """
        params: list[Any] = [reason, id]

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("task_reopen failed")
            await log_usage(
                tool_name="task_reopen",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc), "id": id},
            )
            return {"status": "error", "error": str(exc)}

    if row is None:
        await log_usage(
            tool_name="task_reopen",
            bucket=None,
            project=None,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"result": "not_found", "id": id},
        )
        return {"status": "ok", "found": False}

    task_id = str(row[0])
    await log_usage(
        tool_name="task_reopen",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": "reopened", "id": task_id},
    )
    return {"status": "ok", "id": task_id, "found": True}
