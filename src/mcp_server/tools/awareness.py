"""Module 7.5 awareness MCP tools.

Wraps the synchronous renderer in `src/awareness/readme_renderer.py` for
exposure as MCP tools. The renderer is sync because the readme_consumer
worker dispatches via a sync `psycopg.connect`; here we use
`asyncio.to_thread` to keep the MCP request handler non-blocking.

Tools registered (this run):
  - regenerate_bucket_readme(bucket)
  - regenerate_project_readme(bucket, slug)

The `recommend_skills_for_query` tool lands in RUN 2 / Phase C.
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
