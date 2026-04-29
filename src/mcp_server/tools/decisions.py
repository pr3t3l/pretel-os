"""Decision recording, search, and supersession tools.

ADR-style architectural decisions (and lower-severity scope=operational
day-to-day decisions). Embedding on title+context+decision for semantic
search. HNSW deferred per ADR-024 — sequential scan only (acceptable at
current corpus size).

Schema: docs/DATA_MODEL.md §5.2 + §5.11 amendment (table from Module 2,
amended in migration 0028 with scope/applicable_buckets/decided_by/
tags/severity/adr_number/derived_from_lessons columns).
Spec: specs/module-0x-knowledge-architecture/spec.md §5.2.
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

_VALID_SUPERSEDE_KEYS: frozenset[str] = frozenset({
    "bucket", "project", "title", "context", "decision", "consequences",
    "alternatives", "client_id", "scope", "applicable_buckets",
    "decided_by", "severity", "adr_number", "derived_from_lessons", "tags",
})


async def decision_record(
    bucket: str,
    project: str,
    title: str,
    context: str,
    decision: str,
    consequences: str,
    alternatives: Optional[str] = None,
    client_id: Optional[str] = None,
    scope: str = "operational",
    applicable_buckets: Optional[list[str]] = None,
    decided_by: str = "operator",
    severity: str = "normal",
    adr_number: Optional[int] = None,
    derived_from_lessons: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Record an architectural / process / product / operational decision.

    Embeds title + context + decision via OpenAI text-embedding-3-large.
    On embedding failure the row is still saved with embedding=NULL;
    the existing notify_missing_embedding trigger (migration 0019, fixed
    in 0028a) queues it to pending_embeddings for later retry.

    NOTE: `project` is required because `decisions.project` is NOT NULL
    in the schema. The brief had it Optional but that contradicts the
    table constraint — this function takes the safe path.

    Args:
        bucket: 'personal' | 'business' | 'scout'.
        project: project slug within the bucket (required).
        title: short headline.
        context: what problem prompted this decision.
        decision: what was decided.
        consequences: what this enables / costs.
        alternatives: optional rejected alternatives.
        client_id: optional uuid when decision is client-specific.
        scope: architectural | process | product | operational (default 'operational').
        applicable_buckets: cross-bucket scope (empty => origin only).
        decided_by: provenance string (default 'operator').
        severity: 'critical' | 'normal' | 'minor' (default 'normal').
        adr_number: formal ADR number (UNIQUE; NULL allowed).
        derived_from_lessons: uuid[] of lessons that crystallized into this decision.
        tags: free-form tags (GIN-indexed).

    Returns:
        {status:'ok', id:uuid, adr_number:int|None, embedding_queued:bool} on success.
        {status:'degraded', journal_id:...} when DB is down.
        {status:'error', error:str} on DB failure.
    """
    payload: dict[str, Any] = {
        "bucket": bucket, "project": project, "title": title,
        "context": context, "decision": decision, "consequences": consequences,
        "alternatives": alternatives, "client_id": client_id,
        "scope": scope, "applicable_buckets": applicable_buckets,
        "decided_by": decided_by, "severity": severity,
        "adr_number": adr_number, "derived_from_lessons": derived_from_lessons,
        "tags": tags,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("decision_record", payload)
            await log_usage(
                tool_name="decision_record",
                bucket=bucket,
                project=project,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        embedding = await emb_mod.embed(f"{title}\n\n{context}\n\n{decision}")
        embedding_queued = embedding is None

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO decisions (
                            bucket, project, client_id, title, context, decision,
                            consequences, alternatives, scope, applicable_buckets,
                            decided_by, tags, severity, adr_number, derived_from_lessons,
                            embedding
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s::vector
                        ) RETURNING id, adr_number
                        """,
                        (
                            bucket, project, client_id, title, context, decision,
                            consequences, alternatives, scope, applicable_buckets or [],
                            decided_by, tags or [], severity, adr_number,
                            derived_from_lessons or [],
                            vector_literal(embedding) if embedding is not None else None,
                        ),
                    )
                    row = await cur.fetchone()
                    assert row is not None, "INSERT ... RETURNING produced no row"
                    dec_id = str(row[0])
                    returned_adr = row[1]
        except Exception as exc:
            log.exception("decision_record failed")
            await log_usage(
                tool_name="decision_record",
                bucket=bucket,
                project=project,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="decision_record",
        bucket=bucket,
        project=project,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "action": "inserted",
            "scope": scope,
            "severity": severity,
            "embedding_queued": embedding_queued,
        },
    )
    return {
        "status": "ok",
        "id": dec_id,
        "adr_number": returned_adr,
        "embedding_queued": embedding_queued,
    }


async def decision_search(
    query: str,
    bucket: Optional[str] = None,
    scope: Optional[str] = None,
    status: Optional[str] = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """Semantic search over decisions.

    Filter-first per CONSTITUTION §5.6 rule 26: bucket + scope + status
    apply as WHERE clauses, then ORDER BY embedding similarity. HNSW
    deferred per ADR-024 — sequential scan with `embedding <=> query`.

    Args:
        query: natural-language search text.
        bucket: restrict to one bucket when provided.
        scope: restrict to one scope when provided.
        status: exact status filter; default 'active' when None.
        top_k: clamped to 50.

    Returns:
        {status:'ok', results: [{id, title, scope, severity, bucket, status,
                                 adr_number, similarity}, ...]}
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="decision_search",
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
                tool_name="decision_search",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "embedding_unavailable"},
            )
            return degraded("embedding_unavailable", results=[])

        status_value = status if status is not None else "active"
        q_vec = vector_literal(q_emb)

        params: list[Any] = [q_vec, status_value]
        where_parts = ["status = %s", "embedding IS NOT NULL"]
        if bucket is not None:
            where_parts.append("bucket = %s")
            params.append(bucket)
        if scope is not None:
            where_parts.append("scope = %s")
            params.append(scope)

        limit_val = max(1, min(int(top_k), _SEARCH_LIMIT_MAX))
        params.extend([q_vec, limit_val])

        sql = f"""
            SELECT id, title, scope, severity, bucket, status, adr_number,
                   (1 - (embedding <=> %s::vector)) AS similarity
            FROM decisions
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
            log.exception("decision_search failed")
            await log_usage(
                tool_name="decision_search",
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
            "scope": r[2],
            "severity": r[3],
            "bucket": r[4],
            "status": r[5],
            "adr_number": r[6],
            "similarity": float(r[7]) if r[7] is not None else None,
        }
        for r in rows
    ]

    await log_usage(
        tool_name="decision_search",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}


async def decision_supersede(
    old_id: str,
    new_decision_payload: dict[str, Any],
) -> dict[str, Any]:
    """Atomically supersede an active decision.

    One transaction:
        1. Verify old row exists and status='active'
        2. Embed new payload
        3. INSERT new row
        4. UPDATE old row: status='superseded', superseded_by_id=new.id

    `new_decision_payload` is unpacked into `decision_record`-style
    columns within the same transaction. Required keys: bucket, project,
    title, context, decision, consequences. Other keys are optional and
    must be in `_VALID_SUPERSEDE_KEYS` (whitelist — unknown keys rejected).

    Args:
        old_id: uuid of the decision to supersede.
        new_decision_payload: dict with the new decision's fields.

    Returns:
        {status:'ok', new_id:uuid, old_id:uuid, embedding_queued:bool} on success.
        {status:'ok', found:False} when no active row matches `old_id`.
        {status:'error', error:str} on validation or DB failure.
        {status:'degraded', journal_id:...} when DB is down.
    """
    unknown_keys = set(new_decision_payload.keys()) - _VALID_SUPERSEDE_KEYS
    if unknown_keys:
        return {
            "status": "error",
            "error": f"unknown keys in new_decision_payload: {sorted(unknown_keys)}",
        }
    required = {"bucket", "project", "title", "context", "decision", "consequences"}
    missing = required - set(new_decision_payload.keys())
    if missing:
        return {
            "status": "error",
            "error": f"missing required keys: {sorted(missing)}",
        }

    payload: dict[str, Any] = {
        "old_id": old_id,
        "new_decision_payload": new_decision_payload,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("decision_supersede", payload)
            await log_usage(
                tool_name="decision_supersede",
                bucket=new_decision_payload.get("bucket"),
                project=new_decision_payload.get("project"),
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        n = new_decision_payload
        title = str(n["title"])
        context = str(n["context"])
        decision = str(n["decision"])
        embedding = await emb_mod.embed(f"{title}\n\n{context}\n\n{decision}")
        embedding_queued = embedding is None

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.transaction():
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "SELECT status FROM decisions WHERE id = %s FOR UPDATE",
                            (old_id,),
                        )
                        old_row = await cur.fetchone()

                        if old_row is None:
                            await log_usage(
                                tool_name="decision_supersede",
                                bucket=n.get("bucket"),
                                project=n.get("project"),
                                invoked_by="client",
                                success=True,
                                duration_ms=t.ms,
                                metadata={"result": "not_found", "old_id": old_id},
                            )
                            return {"status": "ok", "found": False}

                        if old_row[0] != "active":
                            return {
                                "status": "error",
                                "error": f"old decision status is {old_row[0]!r}, not 'active'",
                            }

                        await cur.execute(
                            """
                            INSERT INTO decisions (
                                bucket, project, client_id, title, context, decision,
                                consequences, alternatives, scope, applicable_buckets,
                                decided_by, tags, severity, adr_number, derived_from_lessons,
                                embedding
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s::vector
                            ) RETURNING id
                            """,
                            (
                                n["bucket"], n["project"], n.get("client_id"),
                                title, context, decision,
                                n["consequences"], n.get("alternatives"),
                                n.get("scope", "operational"),
                                n.get("applicable_buckets") or [],
                                n.get("decided_by", "operator"),
                                n.get("tags") or [],
                                n.get("severity", "normal"),
                                n.get("adr_number"),
                                n.get("derived_from_lessons") or [],
                                vector_literal(embedding) if embedding is not None else None,
                            ),
                        )
                        new_row = await cur.fetchone()
                        assert new_row is not None, "INSERT ... RETURNING produced no row"
                        new_id = str(new_row[0])

                        await cur.execute(
                            """
                            UPDATE decisions
                            SET status = 'superseded',
                                superseded_by_id = %s
                            WHERE id = %s
                            """,
                            (new_id, old_id),
                        )
        except Exception as exc:
            log.exception("decision_supersede failed")
            await log_usage(
                tool_name="decision_supersede",
                bucket=n.get("bucket"),
                project=n.get("project"),
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc), "old_id": old_id},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="decision_supersede",
        bucket=n.get("bucket"),
        project=n.get("project"),
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "action": "superseded",
            "old_id": old_id,
            "new_id": new_id,
            "embedding_queued": embedding_queued,
        },
    )
    return {
        "status": "ok",
        "new_id": new_id,
        "old_id": old_id,
        "embedding_queued": embedding_queued,
    }
