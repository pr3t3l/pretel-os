"""README parsing + rendering for buckets and projects (Module 7.5 B.1).

Bucket and project READMEs are projections of the database. The DB is the
source of truth (CONSTITUTION §2.4). The renderer parses an existing
README, preserves any operator-edited block delimited by
`<!-- pretel:notes:start -->` ... `<!-- pretel:notes:end -->` byte-for-
byte, and replaces the auto-generated sections delimited by
`<!-- pretel:auto:start NAME -->` ... `<!-- pretel:auto:end NAME -->`.

Two correctness invariants the tests rely on:

  1. Round-trip: `parse → render → parse` returns the same notes block
     verbatim.
  2. Idempotency: running `regenerate_*` twice in a row produces a byte-
     identical file. To preserve this in the presence of the
     `Last regenerated:` timestamp we compare the freshly rendered
     content with the existing file ignoring the timestamp line, and
     reuse the old timestamp when the data has not changed.

The orchestrator functions take a synchronous `psycopg.Connection` so the
readme_consumer worker (sync dispatch) and the MCP tool wrappers (async,
delegated through `asyncio.to_thread`) share one implementation.
"""
from __future__ import annotations

import logging
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import psycopg

from mcp_server import config as config_mod

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Marker constants.
# ---------------------------------------------------------------------

_AUTO_START = "<!-- pretel:auto:start {name} -->"
_AUTO_END = "<!-- pretel:auto:end {name} -->"
_NOTES_START = "<!-- pretel:notes:start -->"
_NOTES_END = "<!-- pretel:notes:end -->"

_AUTO_RE = re.compile(
    r"<!-- pretel:auto:start (\S+) -->(.*?)<!-- pretel:auto:end \1 -->",
    re.DOTALL,
)
_NOTES_RE = re.compile(
    r"<!-- pretel:notes:start -->(.*?)<!-- pretel:notes:end -->",
    re.DOTALL,
)
_TIMESTAMP_RE = re.compile(r"\*\*Last regenerated:\*\* [^\n]*")

_DEFAULT_NOTES_BODY = (
    "\n## Operator notes\n\n"
    "(operator-edited content preserved across regenerations)\n"
)


# ---------------------------------------------------------------------
# Parsing.
# ---------------------------------------------------------------------

def parse_readme(path: Path) -> dict[str, Any]:
    """Read a README and split it into auto sections + notes block.

    Always returns a dict with keys:
        raw          str   — full file contents ("" if missing).
        auto_sections dict — name -> body between matching auto markers.
        notes_block  str   — body between notes markers ("" if absent).

    A brand-new file (or a file with no markers at all) yields empty
    auto_sections and empty notes_block. The caller is expected to fill
    those in via render_*().
    """
    if not path.exists():
        return {"raw": "", "auto_sections": {}, "notes_block": ""}
    raw = path.read_text(encoding="utf-8")
    auto_sections: dict[str, str] = {}
    for m in _AUTO_RE.finditer(raw):
        auto_sections[m.group(1)] = m.group(2)
    notes_block = ""
    nm = _NOTES_RE.search(raw)
    if nm is not None:
        notes_block = nm.group(1)
    return {"raw": raw, "auto_sections": auto_sections, "notes_block": notes_block}


# ---------------------------------------------------------------------
# Render helpers.
# ---------------------------------------------------------------------

def _auto_block(name: str, body: str) -> str:
    return (
        f"{_AUTO_START.format(name=name)}\n"
        f"{body.rstrip()}\n"
        f"{_AUTO_END.format(name=name)}"
    )


def _notes_block(body: str) -> str:
    if not body.strip():
        body = _DEFAULT_NOTES_BODY
    return f"{_NOTES_START}{body}{_NOTES_END}"


def _fmt_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _projects_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "_(none)_"
    lines = []
    for p in items:
        slug = p["slug"]
        name = p.get("name") or slug
        status = p.get("status") or "active"
        objective = p.get("objective") or ""
        suffix = f" — {objective}" if objective else ""
        lines.append(
            f"- [{slug}](projects/{slug}/README.md) — {name} ({status}){suffix}"
        )
    return "\n".join(lines)


def _skills_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "_(none)_"
    lines = []
    for s in items:
        desc = s.get("description_short") or ""
        suffix = f" — {desc}" if desc else ""
        lines.append(f"- **{s['name']}**{suffix}")
    return "\n".join(lines)


def _decisions_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "_(none)_"
    lines = []
    for d in items:
        adr = d.get("adr_number")
        prefix = f"ADR-{adr}" if adr is not None else "ADR-?"
        title = d.get("title") or ""
        date_str = d.get("created_at") or ""
        lines.append(f"- {prefix} — {title} ({date_str})")
    return "\n".join(lines)


def _tasks_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "_(none)_"
    lines = []
    for t in items:
        priority = t.get("priority") or "normal"
        title = t.get("title") or ""
        lines.append(f"- {priority} — {title}")
    return "\n".join(lines)


def _lessons_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "_(none)_"
    lines = []
    for ll in items:
        title = ll.get("title") or ""
        category = ll.get("category") or ""
        date_str = ll.get("created_at") or ""
        lines.append(f"- {title} — {category} ({date_str})")
    return "\n".join(lines)


# ---------------------------------------------------------------------
# Pure render functions (no I/O, no DB).
# ---------------------------------------------------------------------

def render_bucket_readme(
    *,
    bucket: str,
    active_projects: list[dict[str, Any]],
    archived_projects: list[dict[str, Any]],
    skills: list[dict[str, Any]],
    recent_decisions: list[dict[str, Any]],
    count_open_tasks: int,
    notes_block: str,
    timestamp: datetime,
) -> str:
    """Build the full bucket README text per Q3 template."""
    summary = (
        f"**Active projects:** {len(active_projects)}  \n"
        f"**Archived projects:** {len(archived_projects)}  \n"
        f"**Open tasks:** {count_open_tasks}  \n"
        f"**Last regenerated:** {_fmt_iso(timestamp)}"
    )
    active_body = "## Active projects\n\n" + _projects_list(active_projects)
    archived_body = "## Archived projects\n\n" + _projects_list(archived_projects)
    skills_body = "## Available skills\n\n" + _skills_list(skills)
    decisions_body = (
        "## Recent decisions (5 most recent)\n\n" + _decisions_list(recent_decisions)
    )
    return (
        f"# Bucket: {bucket}\n\n"
        f"{_auto_block('summary', summary)}\n\n"
        f"{_auto_block('active_projects', active_body)}\n\n"
        f"{_auto_block('archived_projects', archived_body)}\n\n"
        f"{_auto_block('applicable_skills', skills_body)}\n\n"
        f"{_auto_block('recent_decisions', decisions_body)}\n\n"
        f"{_notes_block(notes_block)}\n"
    )


def render_project_readme(
    *,
    project: dict[str, Any],
    open_tasks: list[dict[str, Any]],
    recent_decisions: list[dict[str, Any]],
    recent_lessons: list[dict[str, Any]],
    notes_block: str,
    timestamp: datetime,
) -> str:
    """Build the full project README text per Q3 template."""
    bucket = project.get("bucket", "")
    slug = project.get("slug", "")
    name = project.get("name") or slug
    status = project.get("status") or "active"
    created_at = project.get("created_at") or ""
    objective = project.get("objective") or "_(not set)_"
    stack = project.get("stack") or []
    applicable_skills = project.get("applicable_skills") or []

    summary = (
        f"**Bucket:** {bucket}  \n"
        f"**Slug:** {slug}  \n"
        f"**Status:** {status}  \n"
        f"**Created:** {created_at}  \n"
        f"**Last regenerated:** {_fmt_iso(timestamp)}"
    )
    stack_str = "\n".join(f"- {s}" for s in stack) if stack else "_(none)_"
    skills_str = (
        "\n".join(f"- {s}" for s in applicable_skills)
        if applicable_skills
        else "_(none)_"
    )
    objective_body = (
        f"## Objective\n\n{objective}\n\n"
        f"## Stack\n\n{stack_str}\n\n"
        f"## Applicable skills\n\n{skills_str}"
    )
    tasks_body = "## Open tasks\n\n" + _tasks_list(open_tasks)
    decisions_body = "## Recent decisions\n\n" + _decisions_list(recent_decisions)
    lessons_body = (
        "## Applicable lessons (5 most recent)\n\n" + _lessons_list(recent_lessons)
    )
    return (
        f"# {name}\n\n"
        f"{_auto_block('summary', summary)}\n\n"
        f"{_auto_block('objective', objective_body)}\n\n"
        f"{_auto_block('open_tasks', tasks_body)}\n\n"
        f"{_auto_block('recent_decisions', decisions_body)}\n\n"
        f"{_auto_block('applicable_lessons', lessons_body)}\n\n"
        f"{_notes_block(notes_block)}\n"
    )


# ---------------------------------------------------------------------
# Atomic write.
# ---------------------------------------------------------------------

def _atomic_write(path: Path, content: str) -> None:
    """Write `content` to `path` atomically (tempfile + rename + fsync)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = None
    tmp_path: Optional[str] = None
    try:
        fh = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(path.parent),
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        )
        tmp_path = fh.name
        try:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        finally:
            fh.close()
        os.rename(tmp_path, str(path))
        tmp_path = None
    finally:
        if tmp_path is not None and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


# ---------------------------------------------------------------------
# DB queries.
# ---------------------------------------------------------------------

def _bucket_path(bucket: str) -> Path:
    return config_mod.REPO_ROOT / "buckets" / bucket / "README.md"


def _project_path(bucket: str, slug: str) -> Path:
    return (
        config_mod.REPO_ROOT
        / "buckets" / bucket / "projects" / slug / "README.md"
    )


def _fetch_bucket_data(
    conn: psycopg.Connection, bucket: str
) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT slug, name, status, objective
            FROM projects
            WHERE bucket = %s AND status = 'active'
            ORDER BY updated_at DESC
            """,
            (bucket,),
        )
        active = [
            {"slug": r[0], "name": r[1], "status": r[2], "objective": r[3]}
            for r in cur.fetchall()
        ]
        cur.execute(
            """
            SELECT slug, name, status, objective
            FROM projects
            WHERE bucket = %s AND status = 'archived'
            ORDER BY archived_at DESC NULLS LAST, updated_at DESC
            """,
            (bucket,),
        )
        archived = [
            {"slug": r[0], "name": r[1], "status": r[2], "objective": r[3]}
            for r in cur.fetchall()
        ]
        cur.execute(
            """
            SELECT name, description_short
            FROM tools_catalog
            WHERE kind = 'skill'
              AND %s = ANY(applicable_buckets)
              AND deprecated = false
              AND archived_at IS NULL
            ORDER BY utility_score DESC NULLS LAST, name ASC
            LIMIT 20
            """,
            (bucket,),
        )
        skills = [
            {"name": r[0], "description_short": r[1]} for r in cur.fetchall()
        ]
        cur.execute(
            """
            SELECT adr_number, title,
                   to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD')
            FROM decisions
            WHERE bucket = %s AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (bucket,),
        )
        decisions = [
            {"adr_number": r[0], "title": r[1], "created_at": r[2]}
            for r in cur.fetchall()
        ]
        cur.execute(
            """
            SELECT count(*)
            FROM tasks
            WHERE bucket = %s
              AND status IN ('open', 'in_progress', 'blocked')
            """,
            (bucket,),
        )
        row = cur.fetchone()
        count_open_tasks = int(row[0]) if row is not None else 0

    return {
        "active_projects": active,
        "archived_projects": archived,
        "skills": skills,
        "recent_decisions": decisions,
        "count_open_tasks": count_open_tasks,
    }


def _fetch_project_data(
    conn: psycopg.Connection, bucket: str, slug: str
) -> Optional[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, bucket, slug, name, status, objective,
                   stack, applicable_skills,
                   to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD')
            FROM projects
            WHERE bucket = %s AND slug = %s
            """,
            (bucket, slug),
        )
        row = cur.fetchone()
        if row is None:
            return None
        project = {
            "id": str(row[0]),
            "bucket": row[1],
            "slug": row[2],
            "name": row[3],
            "status": row[4],
            "objective": row[5],
            "stack": list(row[6]) if row[6] is not None else [],
            "applicable_skills": list(row[7]) if row[7] is not None else [],
            "created_at": row[8],
        }
        project_id = project["id"]
        cur.execute(
            """
            SELECT priority, title
            FROM tasks
            WHERE project_id = %s
              AND status IN ('open', 'in_progress', 'blocked')
            ORDER BY
                CASE priority
                    WHEN 'urgent' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'normal' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END,
                updated_at DESC
            LIMIT 50
            """,
            (project_id,),
        )
        open_tasks = [
            {"priority": r[0], "title": r[1]} for r in cur.fetchall()
        ]
        cur.execute(
            """
            SELECT adr_number, title,
                   to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD')
            FROM decisions
            WHERE project_id = %s AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (project_id,),
        )
        decisions = [
            {"adr_number": r[0], "title": r[1], "created_at": r[2]}
            for r in cur.fetchall()
        ]
        cur.execute(
            """
            SELECT title, category,
                   to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD')
            FROM lessons
            WHERE project_id = %s
              AND deleted_at IS NULL
              AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (project_id,),
        )
        lessons = [
            {"title": r[0], "category": r[1], "created_at": r[2]}
            for r in cur.fetchall()
        ]

    return {
        "project": project,
        "open_tasks": open_tasks,
        "recent_decisions": decisions,
        "recent_lessons": lessons,
    }


# ---------------------------------------------------------------------
# Idempotency: stable timestamp logic.
# ---------------------------------------------------------------------

def _strip_timestamp(text: str) -> str:
    return _TIMESTAMP_RE.sub("**Last regenerated:** __PLACEHOLDER__", text)


def _stable_timestamp(
    existing_raw: str, new_content: str, fallback: datetime
) -> datetime:
    """Reuse the existing file's timestamp when nothing else changed.

    This is what gives the renderer its byte-identical idempotency: a
    second `regenerate_*` call within the same second (or even hours
    later, with no DB change) produces the same file contents.
    """
    if not existing_raw:
        return fallback
    if _strip_timestamp(existing_raw) != _strip_timestamp(new_content):
        return fallback
    m = _TIMESTAMP_RE.search(existing_raw)
    if m is None:
        return fallback
    iso = m.group(0).removeprefix("**Last regenerated:** ").strip()
    try:
        # Stored format: YYYY-MM-DDTHH:MM:SSZ
        return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return fallback


# ---------------------------------------------------------------------
# Orchestrators.
# ---------------------------------------------------------------------

def regenerate_bucket_readme(
    conn: psycopg.Connection, bucket: str
) -> dict[str, Any]:
    """Read DB state for `bucket`, render, write atomically.

    Returns:
        {status:'ok', path, regenerated:bool, content}.
        regenerated is False when the file already matched the rendered
        output (no write performed).
    """
    path = _bucket_path(bucket)
    parsed = parse_readme(path)
    data = _fetch_bucket_data(conn, bucket)

    now = datetime.now(timezone.utc)
    candidate = render_bucket_readme(
        bucket=bucket,
        active_projects=data["active_projects"],
        archived_projects=data["archived_projects"],
        skills=data["skills"],
        recent_decisions=data["recent_decisions"],
        count_open_tasks=data["count_open_tasks"],
        notes_block=parsed["notes_block"],
        timestamp=now,
    )
    stable_ts = _stable_timestamp(parsed["raw"], candidate, fallback=now)
    final = render_bucket_readme(
        bucket=bucket,
        active_projects=data["active_projects"],
        archived_projects=data["archived_projects"],
        skills=data["skills"],
        recent_decisions=data["recent_decisions"],
        count_open_tasks=data["count_open_tasks"],
        notes_block=parsed["notes_block"],
        timestamp=stable_ts,
    )

    if parsed["raw"] == final:
        return {
            "status": "ok",
            "path": str(path),
            "regenerated": False,
            "content": final,
        }
    _atomic_write(path, final)
    log.info("regenerated bucket README: %s", path)
    return {
        "status": "ok",
        "path": str(path),
        "regenerated": True,
        "content": final,
    }


def regenerate_project_readme(
    conn: psycopg.Connection, bucket: str, slug: str
) -> dict[str, Any]:
    """Read DB state for `(bucket, slug)`, render, write atomically.

    Returns:
        {status:'ok', path, regenerated:bool, content} on success.
        {status:'error', error:'project_not_found'} if the project row
        does not exist.
    """
    data = _fetch_project_data(conn, bucket, slug)
    if data is None:
        return {"status": "error", "error": "project_not_found"}

    path = _project_path(bucket, slug)
    parsed = parse_readme(path)
    now = datetime.now(timezone.utc)

    candidate = render_project_readme(
        project=data["project"],
        open_tasks=data["open_tasks"],
        recent_decisions=data["recent_decisions"],
        recent_lessons=data["recent_lessons"],
        notes_block=parsed["notes_block"],
        timestamp=now,
    )
    stable_ts = _stable_timestamp(parsed["raw"], candidate, fallback=now)
    final = render_project_readme(
        project=data["project"],
        open_tasks=data["open_tasks"],
        recent_decisions=data["recent_decisions"],
        recent_lessons=data["recent_lessons"],
        notes_block=parsed["notes_block"],
        timestamp=stable_ts,
    )

    if parsed["raw"] == final:
        return {
            "status": "ok",
            "path": str(path),
            "regenerated": False,
            "content": final,
        }
    _atomic_write(path, final)
    log.info("regenerated project README: %s", path)
    return {
        "status": "ok",
        "path": str(path),
        "regenerated": True,
        "content": final,
    }
