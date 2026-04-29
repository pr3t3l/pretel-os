"""Best-practice tools — record/search/deactivate/rollback.

Reusable PROCESS guidance — narrative rules ("always X when Y"). Distinct
from `patterns` (DATA_MODEL §5.1) which holds CODE snippets. Single-step
rollback via `previous_guidance` + `previous_rationale` columns: every
update copies current values into previous_* before overwriting.

HNSW DEFERRED per ADR-024. Sequential scan only.

Embedding: this table does NOT have the notify_missing_embedding trigger
attached (the trigger from migration 0019 only covers tables that existed
at that time; best_practices was added in migration 0027). When embedding
fails, the row is saved with embedding=NULL and `embedding_queued=True`
in the response — but the row is NOT manually queued to pending_embeddings
in this phase (Phase E will reconcile).

Schema: docs/DATA_MODEL.md §5.10 (table created in migration 0027).
Spec: specs/module-0x-knowledge-architecture/spec.md §5.5.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from .. import db as db_mod
from .. import embeddings as emb_mod
from .. import journal as journal_mod
from ._common import Timer, degraded, log_usage, vector_literal

log = logging.getLogger(__name__)

_SEARCH_LIMIT_MAX = 50


async def best_practice_record(
    title: str,
    guidance: str,
    domain: str,
    rationale: Optional[str] = None,
    scope: str = "global",
    applicable_buckets: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    source: str = "operator",
    derived_from_lessons: Optional[list[str]] = None,
    update_id: Optional[str] = None,
) -> dict[str, Any]:
    """Insert a new best-practice OR update an existing one with rollback semantics.

    INSERT path (`update_id is None`):
        Embeds title + guidance + rationale, inserts a row.
        previous_guidance and previous_rationale start NULL.

    UPDATE path (`update_id is not None`, transactional):
        SELECT current row FOR UPDATE; if missing, returns
        {status:'error', error:'not found'}. Copies current
        guidance → previous_guidance and rationale → previous_rationale
        BEFORE overwriting with the new values, then re-embeds. The
        copy-then-overwrite makes `best_practice_rollback` a single-step
        revert (no version chain).

    Args:
        title: short headline.
        guidance: the prose rule ("always X when Y").
        domain: process | convention | workflow | communication.
        rationale: optional why-this-works text.
        scope: 'global' | 'bucket:<name>' | 'project:<bucket>/<name>'.
        applicable_buckets: cross-bucket scope (empty => origin only).
        tags: free-form tags (GIN-indexed).
        source: operator | derived_from_lessons | migration.
        derived_from_lessons: uuid[] of lessons that informed this practice.
        update_id: when provided, UPDATE this row instead of INSERT.

    Returns:
        INSERT: {status:'ok', id:uuid, action:'inserted', embedding_queued:bool}
        UPDATE: {status:'ok', id:uuid, action:'updated', embedding_queued:bool, rollback_available:True}
        UPDATE not-found: {status:'error', error:'not found'}
        {status:'degraded', journal_id:...} when DB is down.
    """
    payload: dict[str, Any] = {
        "title": title, "guidance": guidance, "rationale": rationale,
        "domain": domain, "scope": scope,
        "applicable_buckets": applicable_buckets, "tags": tags,
        "source": source, "derived_from_lessons": derived_from_lessons,
        "update_id": update_id,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("best_practice_record", payload)
            await log_usage(
                tool_name="best_practice_record",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        embedding = await emb_mod.embed(f"{title}\n\n{guidance}\n\n{rationale or ''}")
        embedding_queued = embedding is None

        pool = db_mod.get_pool()

        if update_id is None:
            # INSERT path
            try:
                async with pool.connection(timeout=5.0) as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            """
                            INSERT INTO best_practices (
                                title, guidance, rationale, domain, scope,
                                applicable_buckets, tags, source,
                                derived_from_lessons, embedding
                            ) VALUES (
                                %s, %s, %s, %s, %s,
                                %s, %s, %s,
                                %s, %s::vector
                            ) RETURNING id
                            """,
                            (
                                title, guidance, rationale, domain, scope,
                                applicable_buckets or [], tags or [], source,
                                derived_from_lessons or [],
                                vector_literal(embedding) if embedding is not None else None,
                            ),
                        )
                        row = await cur.fetchone()
                        assert row is not None, "INSERT ... RETURNING produced no row"
                        bp_id = str(row[0])

                        # best_practices has no notify_missing_embedding trigger
                        # (migration 0019 predates the table). Manually queue when
                        # embedding failed so caller's `embedding_queued=True` is
                        # actually true. Tracked for trigger fix in a M0.X task.
                        if embedding is None:
                            await cur.execute(
                                """
                                INSERT INTO pending_embeddings
                                    (target_table, target_id, source_text)
                                VALUES ('best_practices', %s, %s)
                                ON CONFLICT (target_table, target_id) DO UPDATE
                                SET source_text = EXCLUDED.source_text,
                                    attempts = 0,
                                    last_error = NULL
                                """,
                                (bp_id, f"{title}\n\n{guidance}\n\n{rationale or ''}"),
                            )
            except Exception as exc:
                log.exception("best_practice_record insert failed")
                await log_usage(
                    tool_name="best_practice_record",
                    bucket=None,
                    project=None,
                    invoked_by="client",
                    success=False,
                    duration_ms=t.ms,
                    metadata={"error": str(exc), "path": "insert"},
                )
                return {"status": "error", "error": str(exc)}

            await log_usage(
                tool_name="best_practice_record",
                bucket=None,
                project=None,
                invoked_by="client",
                success=True,
                duration_ms=t.ms,
                metadata={
                    "action": "inserted",
                    "domain": domain,
                    "embedding_queued": embedding_queued,
                },
            )
            return {
                "status": "ok",
                "id": bp_id,
                "action": "inserted",
                "embedding_queued": embedding_queued,
            }

        # UPDATE path — transactional rollback semantics
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.transaction():
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "SELECT guidance, rationale FROM best_practices WHERE id = %s FOR UPDATE",
                            (update_id,),
                        )
                        existing = await cur.fetchone()
                        if existing is None:
                            return {"status": "error", "error": "not found"}

                        await cur.execute(
                            """
                            UPDATE best_practices
                            SET guidance = %s,
                                rationale = %s,
                                domain = %s,
                                scope = %s,
                                applicable_buckets = %s,
                                tags = %s,
                                source = %s,
                                derived_from_lessons = %s,
                                previous_guidance = %s,
                                previous_rationale = %s,
                                embedding = %s::vector
                            WHERE id = %s
                            RETURNING id
                            """,
                            (
                                guidance, rationale, domain, scope,
                                applicable_buckets or [], tags or [], source,
                                derived_from_lessons or [],
                                existing[0],   # previous_guidance ← current guidance
                                existing[1],   # previous_rationale ← current rationale
                                vector_literal(embedding) if embedding is not None else None,
                                update_id,
                            ),
                        )
                        upd_row = await cur.fetchone()
                        assert upd_row is not None, "UPDATE ... RETURNING produced no row inside FOR UPDATE block"
                        bp_id = str(upd_row[0])

                        # Same manual queue as INSERT path — no trigger.
                        if embedding is None:
                            await cur.execute(
                                """
                                INSERT INTO pending_embeddings
                                    (target_table, target_id, source_text)
                                VALUES ('best_practices', %s, %s)
                                ON CONFLICT (target_table, target_id) DO UPDATE
                                SET source_text = EXCLUDED.source_text,
                                    attempts = 0,
                                    last_error = NULL
                                """,
                                (bp_id, f"{title}\n\n{guidance}\n\n{rationale or ''}"),
                            )
        except Exception as exc:
            log.exception("best_practice_record update failed")
            await log_usage(
                tool_name="best_practice_record",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc), "path": "update", "update_id": update_id},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="best_practice_record",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "action": "updated",
            "domain": domain,
            "embedding_queued": embedding_queued,
        },
    )
    return {
        "status": "ok",
        "id": bp_id,
        "action": "updated",
        "embedding_queued": embedding_queued,
        "rollback_available": True,
    }


async def best_practice_search(
    query: str,
    scope: Optional[str] = None,
    domain: Optional[str] = None,
    bucket: Optional[str] = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """Semantic search over active best_practices.

    Sequential-scan vector similarity (HNSW deferred per ADR-024). Filters
    are applied as WHERE clauses (filter-first per CONSTITUTION §5.6
    rule 26): active=true is always required, plus optional scope, domain,
    and bucket (matches via `applicable_buckets @> ARRAY[bucket]`).

    Args:
        query: natural-language search text.
        scope: optional scope filter (e.g. 'global', 'bucket:business').
        domain: process | convention | workflow | communication.
        bucket: bucket name; matches rows where applicable_buckets contains it.
        top_k: clamped to 50.

    Returns:
        {status:'ok', results: [{id, title, guidance, rationale, domain, scope, similarity}, ...]}
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="best_practice_search",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", results=[])

        q_emb = await emb_mod.embed(query)
        if q_emb is None:
            await log_usage(
                tool_name="best_practice_search",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "embedding_unavailable"},
            )
            return degraded("embedding_unavailable", results=[])

        q_vec = vector_literal(q_emb)
        params: list[Any] = [q_vec]
        where_parts = ["active = true", "embedding IS NOT NULL"]
        if scope is not None:
            where_parts.append("scope = %s")
            params.append(scope)
        if domain is not None:
            where_parts.append("domain = %s")
            params.append(domain)
        if bucket is not None:
            where_parts.append("applicable_buckets @> ARRAY[%s]::text[]")
            params.append(bucket)

        limit_val = max(1, min(int(top_k), _SEARCH_LIMIT_MAX))
        params.extend([q_vec, limit_val])

        sql = f"""
            SELECT id, title, guidance, rationale, domain, scope,
                   (1 - (embedding <=> %s::vector)) AS similarity
            FROM best_practices
            WHERE {" AND ".join(where_parts)}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("best_practice_search failed")
            await log_usage(
                tool_name="best_practice_search",
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
            "guidance": r[2],
            "rationale": r[3],
            "domain": r[4],
            "scope": r[5],
            "similarity": float(r[6]) if r[6] is not None else None,
        }
        for r in rows
    ]

    await log_usage(
        tool_name="best_practice_search",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}


async def best_practice_deactivate(id: str, reason: str) -> dict[str, Any]:
    """Soft-delete a best_practice. Sets active=false.

    `reason` is logged via `log_usage(metadata={...})` only — the
    best_practices schema doesn't carry a metadata column for deactivation
    reasons, so the audit trail lives in usage_logs.

    Args:
        id: uuid of the best_practice.
        reason: required human-readable explanation.

    Returns:
        {status:'ok', id:uuid, found:True} on success.
        {status:'ok', found:False} when no row matches `id`.
        {status:'degraded', journal_id:...} when DB is down.
    """
    payload: dict[str, Any] = {"id": id, "reason": reason}

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("best_practice_deactivate", payload)
            await log_usage(
                tool_name="best_practice_deactivate",
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
                        UPDATE best_practices
                        SET active = false
                        WHERE id = %s
                        RETURNING id
                        """,
                        (id,),
                    )
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("best_practice_deactivate failed")
            await log_usage(
                tool_name="best_practice_deactivate",
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
            tool_name="best_practice_deactivate",
            bucket=None,
            project=None,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"result": "not_found", "id": id, "deactivate_reason": reason},
        )
        return {"status": "ok", "found": False}

    bp_id = str(row[0])
    await log_usage(
        tool_name="best_practice_deactivate",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": "deactivated", "id": bp_id, "deactivate_reason": reason},
    )
    return {"status": "ok", "id": bp_id, "found": True}


async def best_practice_rollback(id: str) -> dict[str, Any]:
    """Restore previous_guidance / previous_rationale into the live columns.

    Single-step only — after rollback, previous_* are NULL'd. There is no
    chain. Per spec §10 non-goal: no full version history.

    Re-embeds title + restored guidance + restored rationale because the
    embedding now corresponds to old content. Inline (not via the
    pending_embeddings queue) so the row is immediately searchable
    against the restored content.

    Args:
        id: uuid of the best_practice.

    Returns:
        {status:'ok', id:uuid, action:'rolled_back'} on success.
        {status:'ok', found:False} when no row matches `id`.
        {status:'error', error:'no rollback available'} when previous_guidance is NULL.
        {status:'degraded', journal_id:...} when DB is down.
    """
    payload: dict[str, Any] = {"id": id}

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("best_practice_rollback", payload)
            await log_usage(
                tool_name="best_practice_rollback",
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
                async with conn.transaction():
                    async with conn.cursor() as cur:
                        await cur.execute(
                            """
                            SELECT title, previous_guidance, previous_rationale
                            FROM best_practices
                            WHERE id = %s
                            FOR UPDATE
                            """,
                            (id,),
                        )
                        existing = await cur.fetchone()
                        if existing is None:
                            return {"status": "ok", "found": False}

                        title, prev_guidance, prev_rationale = existing
                        if prev_guidance is None:
                            return {"status": "error", "error": "no rollback available"}

                        embedding = await emb_mod.embed(
                            f"{title}\n\n{prev_guidance}\n\n{prev_rationale or ''}"
                        )

                        await cur.execute(
                            """
                            UPDATE best_practices
                            SET guidance = previous_guidance,
                                rationale = previous_rationale,
                                previous_guidance = NULL,
                                previous_rationale = NULL,
                                embedding = %s::vector
                            WHERE id = %s
                            RETURNING id
                            """,
                            (
                                vector_literal(embedding) if embedding is not None else None,
                                id,
                            ),
                        )
                        roll_row = await cur.fetchone()
                        assert roll_row is not None, "UPDATE inside transaction returned no row"
                        bp_id = str(roll_row[0])
        except Exception as exc:
            log.exception("best_practice_rollback failed")
            await log_usage(
                tool_name="best_practice_rollback",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc), "id": id},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="best_practice_rollback",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"action": "rolled_back", "id": bp_id},
    )
    return {"status": "ok", "id": bp_id, "action": "rolled_back"}
