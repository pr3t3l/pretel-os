"""tools_catalog tools: register_skill, register_tool, load_skill, tool_search."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

from .. import config as config_mod
from .. import db as db_mod
from .. import embeddings as emb_mod
from .. import journal as journal_mod
from ._common import Timer, degraded, log_usage, vector_literal

log = logging.getLogger(__name__)


async def register_skill(
    name: str,
    description_short: str,
    description_full: str,
    applicable_buckets: list[str],
    skill_file_path: str,
) -> dict:
    """Register a methodology (skill) in tools_catalog with kind='skill'.

    Skills are procedural memory stored in `skills/*.md` (L3 content per
    CONSTITUTION §2.3). This tool registers the catalog entry so the
    recommendation system can surface it by utility score and tool_search
    can find it by query. `skill_file_path` is relative to the repo root
    and is stored verbatim — `load_skill` resolves it against REPO_ROOT.

    Args:
        name: unique skill identifier (e.g. 'vett', 'sdd').
        description_short: <=80 chars, lives in L0.
        description_full: multi-line description used for embedding.
        applicable_buckets: buckets where this skill applies.
        skill_file_path: e.g. 'skills/vett.md'.

    Returns:
        {status:'registered', id:uuid} on success; degraded with journal_id on DB down.
    """
    return await _register(
        kind="skill",
        name=name,
        description_short=description_short,
        description_full=description_full,
        applicable_buckets=applicable_buckets,
        skill_file_path=skill_file_path,
        mcp_tool_name=None,
    )


async def register_tool(
    name: str,
    description_short: str,
    description_full: str,
    applicable_buckets: list[str],
    mcp_tool_name: Optional[str] = None,
) -> dict:
    """Register an executable tool in tools_catalog with kind='tool'.

    Tools are MCP tool wrappers or external functions — anything
    invokable, as opposed to a skill (methodology). Same catalog, distinct
    `kind`. No skill_file_path is associated.

    Args:
        name: unique tool identifier.
        description_short: <=80 chars, lives in L0.
        description_full: multi-line description used for embedding.
        applicable_buckets: buckets where this tool applies.
        mcp_tool_name: MCP-tool identifier if this row wraps one.

    Returns:
        {status:'registered', id:uuid} on success; degraded on DB down.
    """
    return await _register(
        kind="tool",
        name=name,
        description_short=description_short,
        description_full=description_full,
        applicable_buckets=applicable_buckets,
        skill_file_path=None,
        mcp_tool_name=mcp_tool_name,
    )


async def _register(
    *,
    kind: str,
    name: str,
    description_short: str,
    description_full: str,
    applicable_buckets: list[str],
    skill_file_path: Optional[str],
    mcp_tool_name: Optional[str],
) -> dict:
    payload: dict[str, Any] = {
        "kind": kind,
        "name": name,
        "description_short": description_short,
        "description_full": description_full,
        "applicable_buckets": applicable_buckets,
        "skill_file_path": skill_file_path,
        "mcp_tool_name": mcp_tool_name,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record(f"register_{kind}", payload)
            await log_usage(
                tool_name=f"register_{kind}",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        embedding = await emb_mod.embed(f"{name}\n{description_full}")
        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO tools_catalog (
                            name, kind, description_short, description_full,
                            applicable_buckets, skill_file_path, mcp_tool_name,
                            embedding
                        ) VALUES (%s, %s::catalog_kind, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET
                            description_short = EXCLUDED.description_short,
                            description_full = EXCLUDED.description_full,
                            applicable_buckets = EXCLUDED.applicable_buckets,
                            skill_file_path = EXCLUDED.skill_file_path,
                            mcp_tool_name = EXCLUDED.mcp_tool_name,
                            embedding = COALESCE(EXCLUDED.embedding, tools_catalog.embedding),
                            updated_at = now()
                        RETURNING id
                        """,
                        (
                            name,
                            kind,
                            description_short,
                            description_full,
                            applicable_buckets,
                            skill_file_path,
                            mcp_tool_name,
                            vector_literal(embedding) if embedding is not None else None,
                        ),
                    )
                    row = await cur.fetchone()
                    row_id = str(row[0])
        except Exception as exc:
            log.exception("register_%s failed", kind)
            await log_usage(
                tool_name=f"register_{kind}",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name=f"register_{kind}",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"name": name, "embedding_queued": embedding is None},
    )
    return {"status": "registered", "id": row_id, "embedding_queued": embedding is None}


async def load_skill(name: str) -> dict:
    """Load a skill's full content (L3) by name.

    Looks up `tools_catalog` for kind='skill' and `name=?`, then reads the
    file at `skill_file_path` (resolved relative to the repo root). Errors
    surface explicitly — no silent fallbacks — per CONSTITUTION §9 rule 7.

    Args:
        name: the skill name as registered.

    Returns:
        {status:'ok', name, skill_file_path, content} on success;
        {status:'error', error: '...'} when not in catalog or file missing;
        degraded when DB is down.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="load_skill",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable")

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT id, skill_file_path, description_short
                        FROM tools_catalog
                        WHERE kind = 'skill' AND name = %s AND deprecated = false AND archived_at IS NULL
                        """,
                        (name,),
                    )
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("load_skill DB lookup failed")
            return {"status": "error", "error": str(exc)}

        if row is None:
            await log_usage(
                tool_name="load_skill",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"name": name, "error": "not_in_catalog"},
            )
            return {"status": "error", "error": f"skill '{name}' not registered in tools_catalog"}

        skill_id, skill_file_path, desc = row
        if not skill_file_path:
            return {"status": "error", "error": f"skill '{name}' has no skill_file_path"}

        cfg = config_mod.load_config()
        resolved = (config_mod.REPO_ROOT / skill_file_path).resolve()
        try:
            # Defensive: refuse path traversal outside the repo.
            resolved.relative_to(config_mod.REPO_ROOT.resolve())
        except ValueError:
            return {
                "status": "error",
                "error": f"skill_file_path escapes repo: {skill_file_path}",
            }

        if not resolved.exists():
            await log_usage(
                tool_name="load_skill",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"name": name, "error": "file_missing", "path": str(resolved)},
            )
            return {"status": "error", "error": f"file missing on disk: {resolved}"}

        content = resolved.read_text(encoding="utf-8")

        # Update last_used_at / usage_count so the nightly utility_score run reflects real use.
        try:
            async with pool.connection(timeout=2.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        UPDATE tools_catalog
                        SET usage_count = usage_count + 1, last_used_at = now(), updated_at = now()
                        WHERE id = %s
                        """,
                        (skill_id,),
                    )
        except Exception as exc:
            log.debug("usage counter update failed: %s", exc)

    await log_usage(
        tool_name="load_skill",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"name": name, "path": skill_file_path, "bytes": len(content)},
    )
    return {
        "status": "ok",
        "name": name,
        "description_short": desc,
        "skill_file_path": skill_file_path,
        "content": content,
    }


async def tool_search(query: str, limit: int = 50) -> dict:
    """Fuzzy catalog search by name or description.

    Required by CONSTITUTION §9 rule 3 so agents can discover tools without
    guessing. Uses ILIKE + pg_trgm similarity on name and description_short;
    returns the top matches ordered by trigram similarity, then utility.

    NOTE: this is a *search* — it filters by query. To enumerate the full
    catalog without filtering, use `list_catalog()` instead. The default
    limit is 50 (catalog ceiling) so a generic query (e.g. ' ') returns
    every match; narrow queries return what they match.

    Args:
        query: free-text query.
        limit: top-K (clamped to 50).

    Returns:
        {status:'ok', results: [{name, kind, description_short, applicable_buckets, utility_score}, ...]}
        or degraded payload when DB is down.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="tool_search",
                bucket=None,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", results=[])

        limit_val = max(1, min(int(limit), 50))
        pool = db_mod.get_pool()
        pattern = f"%{query}%"
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT name, kind, description_short, applicable_buckets, utility_score,
                               GREATEST(similarity(name, %s), similarity(description_short, %s)) AS sim
                        FROM tools_catalog
                        WHERE deprecated = false
                          AND archived_at IS NULL
                          AND (
                              name ILIKE %s
                              OR description_short ILIKE %s
                              OR similarity(name, %s) > 0.2
                              OR similarity(description_short, %s) > 0.2
                          )
                        ORDER BY sim DESC, utility_score DESC
                        LIMIT %s
                        """,
                        (query, query, pattern, pattern, query, query, limit_val),
                    )
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("tool_search failed")
            await log_usage(
                tool_name="tool_search",
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
            "name": r[0],
            "kind": r[1],
            "description_short": r[2],
            "applicable_buckets": list(r[3] or []),
            "utility_score": float(r[4]) if r[4] is not None else 0.0,
            "similarity": float(r[5]) if r[5] is not None else 0.0,
        }
        for r in rows
    ]

    await log_usage(
        tool_name="tool_search",
        bucket=None,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}


_LIST_CATALOG_LIMIT_MAX = 200


async def list_catalog(
    kind: Optional[str] = None,
    bucket: Optional[str] = None,
    include_archived: bool = False,
    include_deprecated: bool = False,
    limit: int = 200,
    offset: int = 0,
) -> dict:
    """Enumerate the full tools_catalog (Module 7.5 follow-up).

    `tool_search` is filtered + capped at 50 results — useful for "find
    me a tool that does X". This function is the canonical "what's
    in the catalog" enumeration: paginated, optionally filtered by
    `kind` (`'skill'` | `'tool'` | `'prompt'`) or `bucket`, and
    returning a `total_count` so the caller knows whether to paginate.

    Args:
        kind: optional `catalog_kind` filter.
        bucket: optional applicable_buckets filter.
        include_archived: include rows where `archived_at IS NOT NULL`.
        include_deprecated: include rows where `deprecated = true`.
        limit: page size (default 200, clamped to 200).
        offset: page start.

    Returns:
        {status:'ok', total_count:int, returned:int, offset:int, limit:int,
         results: [{name, kind, description_short, applicable_buckets,
                    utility_score, deprecated, archived_at}, ...]}
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="list_catalog",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded(
                "db_unavailable", results=[], total_count=0,
            )

        limit_val = max(1, min(int(limit), _LIST_CATALOG_LIMIT_MAX))
        offset_val = max(0, int(offset))

        where_parts: list[str] = []
        params: list[Any] = []
        if kind is not None:
            where_parts.append("kind = %s")
            params.append(kind)
        if bucket is not None:
            where_parts.append("%s = ANY(applicable_buckets)")
            params.append(bucket)
        if not include_deprecated:
            where_parts.append("deprecated = false")
        if not include_archived:
            where_parts.append("archived_at IS NULL")

        where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
        count_sql = f"SELECT count(*) FROM tools_catalog{where_sql}"
        list_sql = f"""
            SELECT name, kind, description_short, applicable_buckets,
                   utility_score, deprecated, archived_at
            FROM tools_catalog
            {where_sql}
            ORDER BY kind, utility_score DESC NULLS LAST, name ASC
            LIMIT %s OFFSET %s
        """

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(count_sql, params)
                    count_row = await cur.fetchone()
                    total_count = int(count_row[0]) if count_row is not None else 0

                    await cur.execute(
                        list_sql, params + [limit_val, offset_val]
                    )
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("list_catalog failed")
            await log_usage(
                tool_name="list_catalog",
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
            "name": r[0],
            "kind": r[1],
            "description_short": r[2],
            "applicable_buckets": list(r[3] or []),
            "utility_score": float(r[4]) if r[4] is not None else 0.0,
            "deprecated": bool(r[5]),
            "archived_at": r[6].isoformat() if r[6] is not None else None,
        }
        for r in rows
    ]

    await log_usage(
        tool_name="list_catalog",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "total_count": total_count,
            "returned": len(results),
            "kind": kind,
            "bucket_filter": bucket,
        },
    )
    return {
        "status": "ok",
        "total_count": total_count,
        "returned": len(results),
        "offset": offset_val,
        "limit": limit_val,
        "results": results,
    }
