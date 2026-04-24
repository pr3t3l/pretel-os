"""Lesson capture and retrieval tools."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from .. import db as db_mod
from .. import embeddings as emb_mod
from .. import journal as journal_mod
from ._common import Timer, degraded, log_usage, vector_literal

log = logging.getLogger(__name__)

_AUTO_APPROVE_DUP_THRESHOLD = 0.92  # CONSTITUTION §5.2 rule 13/14
_TECH_PATTERN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.\-]*")  # loose "technology/pattern" heuristic


async def save_lesson(
    title: str,
    content: str,
    bucket: str,
    tags: list[str],
    category: str,
    severity: Optional[str] = None,
    applicable_buckets: Optional[list[str]] = None,
    related_tools: Optional[list[str]] = None,
    next_time: Optional[str] = None,
) -> dict:
    """Persist a lesson.

    Inserts a row into `lessons` with status='pending_review'. Generates an
    OpenAI embedding for the title+content; on embedding failure the row is
    still saved and a pending_embeddings entry is queued for later retry.

    Pre-save duplicate detection runs against active lessons in the same
    bucket: any similarity >= 0.92 returns a `merge_candidate` response
    without inserting, per CONSTITUTION §5.2 rule 14.

    Auto-approval (status flipped to 'active' in-line) triggers only when
    all four CONSTITUTION §5.2 rule 13 conditions hold: title + content
    present, content mentions a concrete technology/pattern, a `next_time`
    clause is supplied, and no duplicate >= 0.92 exists.

    When the DB is unavailable, the intended write is persisted to the
    fallback journal and a `{status:'degraded', journal_id:...}` payload is
    returned.

    Args:
        title: short headline.
        content: body — the lesson itself.
        bucket: 'personal' | 'business' | 'scout' | 'freelance:<client>'.
        tags: free-form tags (GIN-indexed).
        category: PLAN | ARCH | COST | INFRA | AI | CODE | DATA | OPS | PROC.
        severity: 'critical' | 'moderate' | 'minor' (optional; stored in metadata).
        applicable_buckets: cross-bucket applicability; empty => origin only.
        related_tools: names from tools_catalog that this lesson relates to.
        next_time: the "next time X, do Y" clause — required for auto-approval.

    Returns:
        dict — `{status:'saved', id:uuid, auto_approved:bool, embedding_queued:bool}`
        on success; `{status:'merge_candidate', ...}` on dup hit;
        `{status:'degraded', journal_id:...}` when DB is down.
    """
    payload: dict[str, Any] = {
        "title": title,
        "content": content,
        "bucket": bucket,
        "tags": tags,
        "category": category,
        "severity": severity,
        "applicable_buckets": applicable_buckets or [],
        "related_tools": related_tools or [],
        "next_time": next_time,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("save_lesson", payload)
            await log_usage(
                tool_name="save_lesson",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        embedding = await emb_mod.embed(f"{title}\n\n{content}")
        embedding_queued = embedding is None

        pool = db_mod.get_pool()

        # Pre-save duplicate check — only when we have an embedding.
        if embedding is not None:
            try:
                async with pool.connection(timeout=5.0) as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            """
                            SELECT id, title, similarity
                            FROM find_duplicate_lesson(%s, %s::vector, %s, %s)
                            """,
                            (content, vector_literal(embedding), bucket, _AUTO_APPROVE_DUP_THRESHOLD),
                        )
                        dup_rows = await cur.fetchall()
            except Exception as exc:
                log.warning("find_duplicate_lesson failed: %s", exc)
                dup_rows = []

            if dup_rows:
                await log_usage(
                    tool_name="save_lesson",
                    bucket=bucket,
                    project=None,
                    invoked_by="client",
                    success=True,
                    duration_ms=t.ms,
                    metadata={"result": "merge_candidate", "candidates": len(dup_rows)},
                )
                return {
                    "status": "merge_candidate",
                    "threshold": _AUTO_APPROVE_DUP_THRESHOLD,
                    "candidates": [
                        {"id": str(r[0]), "title": r[1], "similarity": float(r[2])} for r in dup_rows
                    ],
                }

        auto_approved = _auto_approval_eligible(
            title=title, content=content, next_time=next_time, duplicate_hit=False
        )

        metadata = {"severity": severity} if severity else {}
        status = "active" if auto_approved else "pending_review"
        reviewed_by = "auto_approved" if auto_approved else None

        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO lessons (
                            title, content, next_time, bucket, category, tags,
                            applicable_buckets, related_tools, metadata,
                            status, source, evidence, embedding, reviewed_by,
                            reviewed_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s::jsonb,
                            %s, %s, %s::jsonb, %s, %s,
                            CASE WHEN %s THEN now() ELSE NULL END
                        ) RETURNING id
                        """,
                        (
                            title,
                            content,
                            next_time,
                            bucket,
                            category,
                            tags,
                            applicable_buckets or [],
                            related_tools or [],
                            json.dumps(metadata),
                            status,
                            "mcp_tool",
                            json.dumps({}),
                            vector_literal(embedding) if embedding is not None else None,
                            reviewed_by,
                            auto_approved,
                        ),
                    )
                    row = await cur.fetchone()
                    lesson_id = str(row[0])
        except Exception as exc:
            log.exception("save_lesson insert failed")
            await log_usage(
                tool_name="save_lesson",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="save_lesson",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "result": "saved",
            "auto_approved": auto_approved,
            "embedding_queued": embedding_queued,
        },
    )
    return {
        "status": "saved",
        "id": lesson_id,
        "auto_approved": auto_approved,
        "embedding_queued": embedding_queued,
    }


def _auto_approval_eligible(*, title: str, content: str, next_time: Optional[str], duplicate_hit: bool) -> bool:
    """CONSTITUTION §5.2 rule 13 — four conditions must all hold."""
    if duplicate_hit:
        return False
    if not (title and title.strip()):
        return False
    if not (content and content.strip()):
        return False
    if not (next_time and next_time.strip()):
        return False
    # Loose "references a specific technology/pattern" heuristic: require at
    # least one token that looks like a technology/identifier (mixed case,
    # dots, underscores, dashes). Stops vague entries like "do better" from
    # being auto-promoted.
    tokens = _TECH_PATTERN_RE.findall(content)
    has_technical_reference = any(
        any(c.isupper() for c in tok) or "_" in tok or "." in tok or "-" in tok
        for tok in tokens
    )
    return has_technical_reference


async def search_lessons(
    query: str,
    bucket: Optional[str] = None,
    tags: Optional[list[str]] = None,
    limit: int = 5,
    include_archived: bool = False,
) -> dict:
    """Semantic search over active (or all, with `include_archived=True`) lessons.

    Filter-first per CONSTITUTION §5.6 rule 26: bucket + tags + status
    filters apply before the vector sort. pgvector 0.6.0 cannot HNSW-index
    3072-dim vectors, so this is a sequential scan — acceptable at current
    scale (<5k vectors).

    Args:
        query: natural-language search text (embedded via text-embedding-3-large).
        bucket: restrict to one bucket when provided.
        tags: all tags must be present (array contains).
        limit: top-K (clamped to 50).
        include_archived: include rows with status='archived'.

    Returns:
        {status: 'ok', results: [{id, title, next_time, bucket, tags, similarity}, ...]}
        or a degraded payload when DB is down or embedding fails.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="search_lessons",
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
                tool_name="search_lessons",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "embedding_unavailable"},
            )
            return degraded("embedding_unavailable", results=[])

        status_filter = ("active",) if not include_archived else ("active", "archived")
        params: list[Any] = [list(status_filter)]
        where_parts = ["status = ANY(%s)", "deleted_at IS NULL", "embedding IS NOT NULL"]
        if bucket:
            where_parts.append("bucket = %s")
            params.append(bucket)
        if tags:
            where_parts.append("tags @> %s")
            params.append(tags)

        limit_val = max(1, min(int(limit), 50))
        params.append(vector_literal(q_emb))
        params.append(limit_val)

        sql = f"""
            SELECT id, title, next_time, bucket, tags,
                   (1 - (embedding <=> %s::vector)) AS similarity
            FROM lessons
            WHERE {" AND ".join(where_parts)}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        # The vector literal appears twice (SELECT + ORDER BY), so append once more.
        params_final = params[:-2] + [vector_literal(q_emb)] + params[-2:]

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params_final)
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("search_lessons failed")
            await log_usage(
                tool_name="search_lessons",
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
                "next_time": r[2],
                "bucket": r[3],
                "tags": list(r[4] or []),
                "similarity": float(r[5]) if r[5] is not None else None,
            }
            for r in rows
        ]

    await log_usage(
        tool_name="search_lessons",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}
