"""Module 7.5 awareness MCP tools.

Wraps the synchronous renderer in `src/awareness/readme_renderer.py` for
exposure as MCP tools. The renderer is sync because the readme_consumer
worker dispatches via a sync `psycopg.connect`; here we use
`asyncio.to_thread` to keep the MCP request handler non-blocking.

Tools:
  - regenerate_bucket_readme(bucket)
  - regenerate_project_readme(bucket, slug)
  - recommend_skills_for_query(message, bucket)  [Phase C / Q5]
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import psycopg

from awareness import readme_renderer

from .. import config as config_mod
from .. import db as db_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)

_PREVIEW_CHARS = 500
_RECOMMEND_THRESHOLD = 1.0
_RECOMMEND_TOP_K = 3


def _regenerate_bucket_sync(database_url: str, bucket: str) -> dict[str, Any]:
    with psycopg.connect(database_url) as conn:
        return readme_renderer.regenerate_bucket_readme(conn, bucket)


def _regenerate_project_sync(
    database_url: str, bucket: str, slug: str
) -> dict[str, Any]:
    with psycopg.connect(database_url) as conn:
        return readme_renderer.regenerate_project_readme(conn, bucket, slug)


async def regenerate_bucket_readme(bucket: str) -> dict[str, Any]:
    """Regenerate the README for `buckets/<bucket>/README.md`.

    Reads current state from the DB, renders the templated README, and
    writes atomically. Idempotent: re-running with no DB change is a
    no-op (the file is byte-identical).

    Returns:
        {status:'ok', regenerated:bool, path, content_preview}.
        {status:'degraded', degraded_reason:'db_unavailable'} when DB
            is unreachable.
        {status:'error', error} on unexpected failure.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="regenerate_bucket_readme",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable")

        cfg = config_mod.load_config()
        try:
            result = await asyncio.to_thread(
                _regenerate_bucket_sync, cfg.database_url, bucket
            )
        except Exception as exc:
            log.exception("regenerate_bucket_readme failed")
            await log_usage(
                tool_name="regenerate_bucket_readme",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    content = result.get("content") or ""
    payload: dict[str, Any] = {
        "status": "ok",
        "regenerated": bool(result.get("regenerated")),
        "path": result.get("path"),
        "content_preview": content[:_PREVIEW_CHARS],
    }
    await log_usage(
        tool_name="regenerate_bucket_readme",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"regenerated": payload["regenerated"]},
    )
    return payload


async def regenerate_project_readme(
    bucket: str, slug: str
) -> dict[str, Any]:
    """Regenerate `buckets/<bucket>/projects/<slug>/README.md`.

    Returns:
        {status:'ok', regenerated:bool, path, content_preview}.
        {status:'error', error:'project_not_found'} when no projects
            row matches (bucket, slug).
        {status:'degraded', ...} when DB is down.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="regenerate_project_readme",
                bucket=bucket,
                project=slug,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable")

        cfg = config_mod.load_config()
        try:
            result = await asyncio.to_thread(
                _regenerate_project_sync, cfg.database_url, bucket, slug
            )
        except Exception as exc:
            log.exception("regenerate_project_readme failed")
            await log_usage(
                tool_name="regenerate_project_readme",
                bucket=bucket,
                project=slug,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    if result.get("status") == "error":
        await log_usage(
            tool_name="regenerate_project_readme",
            bucket=bucket,
            project=slug,
            invoked_by="client",
            success=False,
            duration_ms=t.ms,
            metadata={"error": result.get("error")},
        )
        return {"status": "error", "error": result.get("error")}

    content = result.get("content") or ""
    payload: dict[str, Any] = {
        "status": "ok",
        "regenerated": bool(result.get("regenerated")),
        "path": result.get("path"),
        "content_preview": content[:_PREVIEW_CHARS],
    }
    await log_usage(
        tool_name="regenerate_project_readme",
        bucket=bucket,
        project=slug,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"regenerated": payload["regenerated"]},
    )
    return payload


def _score_skills_sync(
    database_url: str, message: str, bucket: str
) -> list[dict[str, Any]]:
    """Score every skill applicable to `bucket` against `message` (Q5).

    Algorithm (no LLM):
      score = 1.0 * keyword_hit + 0.3 * utility_score
    Filter score >= 1.0 → with utility ∈ [0, 1] alone giving max 0.3,
    this only passes skills whose trigger_keywords matched the message.
    Sorted descending; capped at top 3.
    """
    msg_lower = message.lower()
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, description_short, utility_score, trigger_keywords
                FROM tools_catalog
                WHERE kind = 'skill'
                  AND %s = ANY(applicable_buckets)
                  AND deprecated = false
                  AND archived_at IS NULL
                """,
                (bucket,),
            )
            rows = cur.fetchall()

    scored: list[dict[str, Any]] = []
    for name, description_short, utility_score, trigger_keywords in rows:
        keywords = list(trigger_keywords or [])
        utility = float(utility_score or 0.0)
        matched_keyword: str | None = None
        for kw in keywords:
            if not kw:
                continue
            if kw.lower() in msg_lower:
                matched_keyword = kw
                break
        keyword_hit = 1.0 if matched_keyword is not None else 0.0
        score = keyword_hit + 0.3 * utility
        if score < _RECOMMEND_THRESHOLD:
            continue
        if matched_keyword is not None:
            reason = f"matched keyword: {matched_keyword!r}"
        else:
            reason = "utility-only"
        scored.append(
            {
                "name": name,
                "score": round(score, 4),
                "reason": reason,
                "description_short": description_short,
                "utility_score": utility,
            }
        )

    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:_RECOMMEND_TOP_K]


async def recommend_skills_for_query(
    message: str,
    bucket: str,
) -> dict[str, Any]:
    """Suggest top-3 skills for `(message, bucket)` (Module 7.5 Q5).

    Pure SQL + Python keyword scoring — no LLM, no embedding. Each skill
    in `tools_catalog` whose `applicable_buckets` includes `bucket` is
    scored on:
        score = 1.0 * (1 if any trigger_keyword in lowercased message else 0)
              + 0.3 * utility_score
    Skills with score < 1.0 are dropped. Top 3 returned.

    Returns:
        {status:'ok', recommendations: [{name, score, reason,
            description_short, utility_score}]}
        {status:'degraded', ...} when DB is unreachable.
        {status:'error', error} on unexpected failure.
    """
    if not isinstance(message, str) or not message.strip():
        return {
            "status": "error",
            "error": "message must be a non-empty string",
        }
    if not isinstance(bucket, str) or not bucket.strip():
        return {
            "status": "error",
            "error": "bucket must be a non-empty string",
        }

    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="recommend_skills_for_query",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", recommendations=[])

        cfg = config_mod.load_config()
        try:
            recommendations = await asyncio.to_thread(
                _score_skills_sync, cfg.database_url, message, bucket
            )
        except Exception as exc:
            log.exception("recommend_skills_for_query failed")
            await log_usage(
                tool_name="recommend_skills_for_query",
                bucket=bucket,
                project=None,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

    await log_usage(
        tool_name="recommend_skills_for_query",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"recommendation_count": len(recommendations)},
    )
    return {"status": "ok", "recommendations": recommendations}
