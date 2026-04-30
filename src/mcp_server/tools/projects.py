"""Project management tools — create_project, get_project, list_projects.

Live registry for active projects (closed projects move to
`projects_indexed` for embedding-based recall, per
`docs/DATA_MODEL.md` §2.3 vs the new `projects` table in migration 0033).

`create_project` is the only tool here that mutates: it inserts the
`projects` row, writes the L2 README to disk under
`buckets/{bucket}/projects/{slug}/README.md`, seeds an initial
`project_state(state_key='status', content='active')` row, and snapshots
a `project_versions` row with `snapshot_reason='project_created'`.

`get_project` is read-only: returns the row + the README content from
disk if `readme_path` is populated and the file exists.

`list_projects` is read-only: bucket and status filters, ordered by
created_at DESC.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import Any, Optional

import psycopg

from awareness import readme_renderer

from .. import config as config_mod
from .. import db as db_mod
from .. import journal as journal_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)

_FIXED_BUCKETS = frozenset({"personal", "business", "scout"})
_FREELANCE_PREFIX = "freelance:"
_LIST_LIMIT_MAX = 200


def _regenerate_bucket_readme_sync(database_url: str, bucket: str) -> dict[str, Any]:
    """Open a fresh sync connection and call the renderer (Module 7.5).

    Used by `create_project` and `archive_project` to project the live
    DB state into `buckets/<bucket>/README.md` immediately after a
    mutation. The trigger 0034 also fires `pg_notify('readme_dirty')`,
    which the readme_consumer worker debounces — we still call the
    renderer inline so an operator using a fresh client sees the new
    bucket README without waiting for the 30s debounce.
    """
    with psycopg.connect(database_url) as conn:
        return readme_renderer.regenerate_bucket_readme(conn, bucket)

# Slug normalization: lowercase, replace any run of non [a-z0-9-] with a
# single hyphen, collapse repeated hyphens, strip leading/trailing hyphens.
_SLUG_NON_ALLOWED_RE = re.compile(r"[^a-z0-9-]+")
_SLUG_HYPHEN_COLLAPSE_RE = re.compile(r"-+")


def _validate_bucket(bucket: str) -> Optional[str]:
    """Return None if valid, error string otherwise."""
    if bucket in _FIXED_BUCKETS:
        return None
    if bucket.startswith(_FREELANCE_PREFIX) and len(bucket) > len(_FREELANCE_PREFIX):
        return None
    return f"invalid bucket: {bucket!r}"


def _normalize_slug(raw: str) -> str:
    out = raw.lower()
    out = _SLUG_NON_ALLOWED_RE.sub("-", out)
    out = _SLUG_HYPHEN_COLLAPSE_RE.sub("-", out)
    return out.strip("-")


def _build_readme(
    *,
    name: str,
    bucket: str,
    objective: Optional[str],
    description: str,
    stack: list[str],
    skills_used: list[str],
    today: date,
) -> str:
    """Generate the initial README body. See spec for fields."""
    obj = objective if objective else "TBD"
    stack_block = "\n".join(f"- {s}" for s in stack) if stack else "- TBD"
    skills_block = (
        "\n".join(f"- {s}" for s in skills_used)
        if skills_used
        else "- None registered"
    )
    return (
        f"# {name}\n"
        f"\n"
        f"Bucket: {bucket}  \n"
        f"Status: Active  \n"
        f"Created: {today.isoformat()}  \n"
        f"Objective: {obj}\n"
        f"\n"
        f"## Description\n"
        f"\n"
        f"{description}\n"
        f"\n"
        f"## Stack\n"
        f"\n"
        f"{stack_block}\n"
        f"\n"
        f"## Skills\n"
        f"\n"
        f"{skills_block}\n"
        f"\n"
        f"## Current State\n"
        f"\n"
        f"- Status: Active\n"
        f"- Phase: Initial\n"
        f"\n"
        f"## Key Decisions\n"
        f"\n"
        f"(none yet)\n"
        f"\n"
        f"## Notes\n"
        f"\n"
        f"(add as project evolves)\n"
    )


async def create_project(
    bucket: str,
    slug: str,
    name: str,
    description: str,
    objective: Optional[str] = None,
    stack: Optional[list[str]] = None,
    skills_used: Optional[list[str]] = None,
    client_id: Optional[str] = None,
) -> dict[str, Any]:
    """Register a new live project.

    Steps (all in one DB connection except the README disk write):
      1. Validate bucket; reject anything not in {personal, business,
         scout, freelance:<client>}.
      2. Normalize slug (lowercase, hyphens, no spaces).
      3. If a row with (bucket, normalized_slug) already exists, return
         {status:'exists', id, slug, message:'Project already exists'}.
      4. INSERT into projects.
      5. Build README body, write to
         {REPO_ROOT}/buckets/{bucket}/projects/{slug}/README.md (mkdir -p
         the parent). UPDATE projects SET readme_path=...
      6. INSERT initial row into project_state with
         state_key='status', content='active'.
      7. INSERT a project_versions snapshot with
         snapshot_reason='project_created',
         triggered_by='create_project_tool'.

    Returns:
        {status:'ok', id, slug, readme_path} on success.
        {status:'exists', id, slug, message} when (bucket, slug) collides.
        {status:'error', error} on validation failure or DB error.
        {status:'degraded', journal_id} when DB is down.
    """
    bucket_err = _validate_bucket(bucket)
    if bucket_err is not None:
        return {"status": "error", "error": bucket_err}
    if not name.strip():
        return {"status": "error", "error": "name must be non-empty"}
    if not description.strip():
        return {"status": "error", "error": "description must be non-empty"}

    norm_slug = _normalize_slug(slug)
    if not norm_slug:
        return {"status": "error", "error": f"slug normalizes to empty: {slug!r}"}

    stack_list: list[str] = list(stack) if stack else []
    skills_list: list[str] = list(skills_used) if skills_used else []

    payload: dict[str, Any] = {
        "bucket": bucket,
        "slug": norm_slug,
        "name": name,
        "description": description,
        "objective": objective,
        "stack": stack_list,
        "skills_used": skills_list,
        "client_id": client_id,
    }

    with Timer() as t:
        if not db_mod.is_healthy():
            journal_id = journal_mod.record("create_project", payload)
            await log_usage(
                tool_name="create_project",
                bucket=bucket,
                project=norm_slug,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable", "journal_id": journal_id},
            )
            return degraded("db_unavailable", journal_id=journal_id)

        readme_relpath = f"buckets/{bucket}/projects/{norm_slug}/README.md"
        readme_abspath = config_mod.REPO_ROOT / readme_relpath
        readme_body = _build_readme(
            name=name,
            bucket=bucket,
            objective=objective,
            description=description,
            stack=stack_list,
            skills_used=skills_list,
            today=date.today(),
        )

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    # Idempotency check first.
                    await cur.execute(
                        "SELECT id FROM projects WHERE bucket = %s AND slug = %s",
                        (bucket, norm_slug),
                    )
                    existing = await cur.fetchone()
                    if existing is not None:
                        existing_id = str(existing[0])
                        await log_usage(
                            tool_name="create_project",
                            bucket=bucket,
                            project=norm_slug,
                            invoked_by="client",
                            success=True,
                            duration_ms=t.ms,
                            metadata={"action": "noop_exists", "id": existing_id},
                        )
                        return {
                            "status": "exists",
                            "id": existing_id,
                            "slug": norm_slug,
                            "message": "Project already exists",
                        }

                    await cur.execute(
                        """
                        INSERT INTO projects (
                            bucket, slug, name, description,
                            stack, skills_used, objective, client_id
                        ) VALUES (
                            %s, %s, %s, %s,
                            %s, %s, %s, %s
                        ) RETURNING id
                        """,
                        (
                            bucket, norm_slug, name, description,
                            stack_list, skills_list, objective, client_id,
                        ),
                    )
                    row = await cur.fetchone()
                    assert row is not None, "INSERT ... RETURNING produced no row"
                    project_id = str(row[0])

                    # Write README to disk before recording readme_path so
                    # the path on disk matches what the row claims.
                    readme_abspath.parent.mkdir(parents=True, exist_ok=True)
                    readme_abspath.write_text(readme_body, encoding="utf-8")

                    await cur.execute(
                        "UPDATE projects SET readme_path = %s WHERE id = %s",
                        (readme_relpath, project_id),
                    )

                    # Initial project_state row.
                    await cur.execute(
                        """
                        INSERT INTO project_state (
                            bucket, project, state_key, content, status, client_id
                        ) VALUES (%s, %s, 'status', 'active', 'open', %s)
                        ON CONFLICT (bucket, project, state_key, content) DO NOTHING
                        """,
                        (bucket, norm_slug, client_id),
                    )

                    # Snapshot.
                    await cur.execute(
                        """
                        INSERT INTO project_versions (
                            bucket, project, client_id,
                            snapshot_reason, readme_content, triggered_by
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            bucket, norm_slug, client_id,
                            "project_created", readme_body, "create_project_tool",
                        ),
                    )
        except Exception as exc:
            log.exception("create_project failed")
            await log_usage(
                tool_name="create_project",
                bucket=bucket,
                project=norm_slug,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc)}

        # Module 7.5 — projection: regenerate the bucket README so the
        # new project surfaces under "Active projects" immediately.
        # Best-effort — failure here must NOT undo the project insert.
        bucket_readme_regenerated = False
        try:
            await asyncio.to_thread(
                _regenerate_bucket_readme_sync,
                config_mod.load_config().database_url,
                bucket,
            )
            bucket_readme_regenerated = True
        except Exception as exc:
            log.warning(
                "create_project: bucket README regeneration failed "
                "(insert kept): %s", exc,
            )

    await log_usage(
        tool_name="create_project",
        bucket=bucket,
        project=norm_slug,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "action": "inserted",
            "id": project_id,
            "readme_path": readme_relpath,
            "bucket_readme_regenerated": bucket_readme_regenerated,
        },
    )
    return {
        "status": "ok",
        "id": project_id,
        "slug": norm_slug,
        "readme_path": readme_relpath,
        "bucket_readme_regenerated": bucket_readme_regenerated,
    }


async def get_project(bucket: str, slug: str) -> dict[str, Any]:
    """Look up a project by (bucket, slug).

    The slug is matched verbatim — callers that pass user input should
    normalize first (use the same rules as create_project). Returns the
    row plus the README content from disk when `readme_path` is set and
    the file exists.

    Returns:
        {status:'ok', found:True, project:{...}, readme_content:str|None}.
        {status:'ok', found:False} when no row matches.
        {status:'degraded', ...} when DB is down.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="get_project",
                bucket=bucket,
                project=slug,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"degraded_reason": "db_unavailable"},
            )
            return degraded("db_unavailable", found=False)

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT id, bucket, slug, name, description, status,
                               stack, skills_used, objective, client_id,
                               readme_path, metadata, created_at, updated_at
                        FROM projects
                        WHERE bucket = %s AND slug = %s
                        """,
                        (bucket, slug),
                    )
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("get_project failed")
            await log_usage(
                tool_name="get_project",
                bucket=bucket,
                project=slug,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "error": str(exc), "found": False}

    if row is None:
        await log_usage(
            tool_name="get_project",
            bucket=bucket,
            project=slug,
            invoked_by="client",
            success=True,
            duration_ms=t.ms,
            metadata={"result": "not_found"},
        )
        return {"status": "ok", "found": False}

    project = {
        "id": str(row[0]),
        "bucket": row[1],
        "slug": row[2],
        "name": row[3],
        "description": row[4],
        "status": row[5],
        "stack": list(row[6]) if row[6] is not None else [],
        "skills_used": list(row[7]) if row[7] is not None else [],
        "objective": row[8],
        "client_id": str(row[9]) if row[9] is not None else None,
        "readme_path": row[10],
        "metadata": row[11] if row[11] is not None else {},
        "created_at": row[12].isoformat() if row[12] is not None else None,
        "updated_at": row[13].isoformat() if row[13] is not None else None,
    }

    readme_content: Optional[str] = None
    if project["readme_path"]:
        readme_abspath = config_mod.REPO_ROOT / project["readme_path"]
        try:
            readme_content = readme_abspath.read_text(encoding="utf-8")
        except OSError as exc:
            log.debug("readme read failed for %s: %s", readme_abspath, exc)
            readme_content = None

    await log_usage(
        tool_name="get_project",
        bucket=bucket,
        project=slug,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result": "found", "id": project["id"]},
    )
    return {
        "status": "ok",
        "found": True,
        "project": project,
        "readme_content": readme_content,
    }


async def list_projects(
    bucket: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> dict[str, Any]:
    """List projects with optional bucket / status filters.

    Ordered by created_at DESC. `limit` is clamped to 200.
    """
    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="list_projects",
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

        where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
        limit_val = max(1, min(int(limit), _LIST_LIMIT_MAX))
        params.append(limit_val)

        sql = f"""
            SELECT id, bucket, slug, name, status, objective, created_at
            FROM projects
            {where_sql}
            ORDER BY created_at DESC
            LIMIT %s
        """

        pool = db_mod.get_pool()
        try:
            async with pool.connection(timeout=5.0) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    rows = await cur.fetchall()
        except Exception as exc:
            log.exception("list_projects failed")
            await log_usage(
                tool_name="list_projects",
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
            "bucket": r[1],
            "slug": r[2],
            "name": r[3],
            "status": r[4],
            "objective": r[5],
            "created_at": r[6].isoformat() if r[6] is not None else None,
        }
        for r in rows
    ]

    await log_usage(
        tool_name="list_projects",
        bucket=bucket,
        project=None,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={"result_count": len(results)},
    )
    return {"status": "ok", "results": results}


async def archive_project(
    bucket: str,
    slug: str,
    reason: str,
) -> dict[str, Any]:
    """Archive an active project (Module 7.5 Q7).

    Idempotent: only flips a row whose status is currently 'active'. A
    second call (or a call against an unknown slug) returns a clean
    error, not a degraded state. The 0034 trigger emits
    `pg_notify('project_lifecycle', 'archived:<bucket>/<slug>')` on the
    UPDATE; the readme_consumer worker debounces the corresponding
    `readme_dirty` signal. We also call `regenerate_bucket_readme`
    inline so the bucket README's "Archived projects" section reflects
    the change immediately for clients that look at the file directly.

    Args:
        bucket: 'personal' | 'business' | 'scout' | 'freelance:<client>'.
        slug: project slug within the bucket.
        reason: human-readable justification (stored in archive_reason).

    Returns:
        {status:'ok', id, archived_at, bucket_readme_regenerated} on success.
        {status:'error', reason} when the project is missing or already archived.
        {status:'degraded', degraded_reason:'db_unavailable'} when DB is down.
    """
    bucket_err = _validate_bucket(bucket)
    if bucket_err is not None:
        return {"status": "error", "reason": bucket_err}
    if not slug.strip():
        return {"status": "error", "reason": "slug must be non-empty"}
    if not reason.strip():
        return {"status": "error", "reason": "reason must be non-empty"}

    with Timer() as t:
        if not db_mod.is_healthy():
            await log_usage(
                tool_name="archive_project",
                bucket=bucket,
                project=slug,
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
                        UPDATE projects
                        SET status = 'archived',
                            archived_at = now(),
                            archive_reason = %s
                        WHERE bucket = %s
                          AND slug = %s
                          AND status = 'active'
                        RETURNING id, archived_at
                        """,
                        (reason, bucket, slug),
                    )
                    row = await cur.fetchone()
        except Exception as exc:
            log.exception("archive_project failed")
            await log_usage(
                tool_name="archive_project",
                bucket=bucket,
                project=slug,
                invoked_by="client",
                success=False,
                duration_ms=t.ms,
                metadata={"error": str(exc)},
            )
            return {"status": "error", "reason": str(exc)}

        if row is None:
            await log_usage(
                tool_name="archive_project",
                bucket=bucket,
                project=slug,
                invoked_by="client",
                success=True,
                duration_ms=t.ms,
                metadata={"result": "not_found_or_already_archived"},
            )
            return {
                "status": "error",
                "reason": "project not found or already archived",
            }

        project_id = str(row[0])
        archived_at = row[1].isoformat() if row[1] is not None else None

        bucket_readme_regenerated = False
        try:
            await asyncio.to_thread(
                _regenerate_bucket_readme_sync,
                config_mod.load_config().database_url,
                bucket,
            )
            bucket_readme_regenerated = True
        except Exception as exc:
            log.warning(
                "archive_project: bucket README regeneration failed "
                "(archive kept): %s", exc,
            )

    await log_usage(
        tool_name="archive_project",
        bucket=bucket,
        project=slug,
        invoked_by="client",
        success=True,
        duration_ms=t.ms,
        metadata={
            "action": "archived",
            "id": project_id,
            "bucket_readme_regenerated": bucket_readme_regenerated,
        },
    )
    return {
        "status": "ok",
        "id": project_id,
        "archived_at": archived_at,
        "bucket_readme_regenerated": bucket_readme_regenerated,
    }
