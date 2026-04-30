"""Tests for `mcp_server.tools.awareness` — Module 7.5 Phase E E.3.

Six tests covering:
  1. recommend_skills_for_query → vett surfaces for a vendor query.
  2. recommend_skills_for_query → sdd surfaces for a spec query.
  3. recommend_skills_for_query → empty when no keyword crosses 1.0 threshold.
  4. regenerate_bucket_readme MCP tool returns updated content.
  5. archive_project moves a project from Active to Archived in the README.
  6. archive_project emits a `project_lifecycle` pg_notify with an
     `archived:<bucket>/<slug>` payload.

Tests 4-6 are slow (DB + filesystem). The recommend_* tests hit the test
DB tools_catalog (seeded by migration 0035) but stay fast.

The shared `awareness_env` fixture replaces:
  - `db_mod.is_healthy()` → True
  - `db_mod.get_pool()` → the projects-test pool (test DB)
  - `config_mod.load_config().database_url` → TEST_DATABASE_URL so the
    sync renderer (called via asyncio.to_thread) hits the same DB
  - `config_mod.REPO_ROOT` → tmp_path so README writes do not pollute
    the working tree
"""
from __future__ import annotations

import asyncio
import os
import time
from dataclasses import replace as dc_replace
from pathlib import Path
from typing import AsyncIterator

import psycopg
import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from mcp_server import config as config_mod
from mcp_server import db as db_mod
from mcp_server.tools.awareness import (
    recommend_skills_for_query,
    regenerate_bucket_readme,
)
from mcp_server.tools.projects import archive_project, create_project

_TEST_DATABASE_URL = os.environ.get(
    "PRETEL_OS_TEST_DATABASE_URL",
    "postgresql://pretel_os@localhost/pretel_os_test",
)


# ---------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------

@pytest_asyncio.fixture
async def aware_pool() -> AsyncIterator[AsyncConnectionPool]:
    pool = AsyncConnectionPool(
        conninfo=_TEST_DATABASE_URL,
        min_size=1,
        max_size=2,
        open=False,
        timeout=5.0,
    )
    await pool.open(wait=True)
    try:
        yield pool
    finally:
        await pool.close()


@pytest_asyncio.fixture
async def awareness_env(
    aware_pool: AsyncConnectionPool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> AsyncIterator[Path]:
    """Wire the test DB + tmp REPO_ROOT into both async-pool and sync paths."""
    async def _noop() -> None:
        return None

    monkeypatch.setattr(db_mod, "_pool", aware_pool, raising=False)
    monkeypatch.setattr(db_mod, "_db_healthy", True, raising=False)
    monkeypatch.setattr(db_mod, "is_healthy", lambda: True)
    monkeypatch.setattr(db_mod, "get_pool", lambda: aware_pool)
    monkeypatch.setattr(db_mod, "start_background_health_check", _noop)
    monkeypatch.setattr(db_mod, "stop_background_health_check", _noop)

    original = config_mod.load_config

    def _patched_load() -> object:
        cfg = original()
        return dc_replace(
            cfg, database_url=_TEST_DATABASE_URL
        )

    monkeypatch.setattr(config_mod, "load_config", _patched_load)
    monkeypatch.setattr(config_mod, "REPO_ROOT", tmp_path)
    yield tmp_path


@pytest_asyncio.fixture
async def clean_test_artifacts(
    aware_pool: AsyncConnectionPool,
) -> AsyncIterator[None]:
    """Best-effort cleanup of rows that tests in this file create.

    Acts before each test so a previous run's leftover does not leak in.
    """
    async with aware_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM projects WHERE slug LIKE %s",
                ("test-archive-%",),
            )
            await cur.execute(
                "DELETE FROM projects WHERE slug LIKE %s",
                ("test-regen-%",),
            )
        await conn.commit()
    yield


# ---------------------------------------------------------------------
# 1-3. recommend_skills_for_query (no slow mark — read-only).
# ---------------------------------------------------------------------

async def test_recommend_skills_for_query_returns_vett_for_vendor_query(
    awareness_env: Path,
) -> None:
    r = await recommend_skills_for_query(
        message="evalúa este vendor para business",
        bucket="business",
    )
    assert r["status"] == "ok"
    names = [rec["name"] for rec in r["recommendations"]]
    assert "vett" in names, f"recommendations: {r['recommendations']}"
    vett_score = next(rec["score"] for rec in r["recommendations"] if rec["name"] == "vett")
    assert vett_score >= 1.0


async def test_recommend_skills_for_query_returns_sdd_for_spec_query(
    awareness_env: Path,
) -> None:
    r = await recommend_skills_for_query(
        message="ayúdame a planear este módulo paso a paso",
        bucket="personal",
    )
    assert r["status"] == "ok"
    names = [rec["name"] for rec in r["recommendations"]]
    assert "sdd" in names, f"recommendations: {r['recommendations']}"


async def test_recommend_skills_for_query_empty_when_no_match_above_threshold(
    awareness_env: Path,
) -> None:
    r = await recommend_skills_for_query(
        message="qué hora es",
        bucket="scout",
    )
    assert r["status"] == "ok"
    assert r["recommendations"] == [], (
        f"expected no recommendations for greeting, got: {r['recommendations']}"
    )


# ---------------------------------------------------------------------
# 4. regenerate_bucket_readme MCP tool.
# ---------------------------------------------------------------------

@pytest.mark.slow
async def test_regenerate_bucket_readme_returns_updated_content(
    awareness_env: Path,
    clean_test_artifacts: None,
    aware_pool: AsyncConnectionPool,
) -> None:
    suffix = int(time.monotonic_ns())
    slug = f"test-regen-{suffix}"
    create_r = await create_project(
        bucket="business",
        slug=slug,
        name=f"Test Regen {suffix}",
        description="Regen smoke",
    )
    assert create_r["status"] == "ok"

    r = await regenerate_bucket_readme(bucket="business")
    assert r["status"] == "ok"
    assert r["path"].endswith("buckets/business/README.md")
    preview = r["content_preview"]
    assert "<!-- pretel:auto:start" in preview
    assert "Bucket: business" in preview

    # Re-read the file to confirm the slug landed under Active projects.
    body = (awareness_env / "buckets" / "business" / "README.md").read_text(
        encoding="utf-8"
    )
    assert slug in body, "new project slug should appear in regenerated README"


# ---------------------------------------------------------------------
# 5. archive_project moves project to Archived section.
# ---------------------------------------------------------------------

@pytest.mark.slow
async def test_archive_project_moves_to_archived_section(
    awareness_env: Path,
    clean_test_artifacts: None,
) -> None:
    suffix = int(time.monotonic_ns())
    slug = f"test-archive-{suffix}"

    create_r = await create_project(
        bucket="scout",
        slug=slug,
        name=f"Test Archive {suffix}",
        description="will be archived",
    )
    assert create_r["status"] == "ok"

    body_before = (
        awareness_env / "buckets" / "scout" / "README.md"
    ).read_text(encoding="utf-8")
    # The project should land in the active_projects section.
    active_section = body_before.split(
        "<!-- pretel:auto:end active_projects -->"
    )[0]
    assert slug in active_section

    # Now archive.
    arch_r = await archive_project(
        bucket="scout", slug=slug, reason="smoke-test archive"
    )
    assert arch_r["status"] == "ok", arch_r
    assert arch_r["bucket_readme_regenerated"] is True

    body_after = (
        awareness_env / "buckets" / "scout" / "README.md"
    ).read_text(encoding="utf-8")
    archived_section = body_after.split(
        "<!-- pretel:auto:start archived_projects -->"
    )[1].split("<!-- pretel:auto:end archived_projects -->")[0]
    assert slug in archived_section, (
        "archived slug should appear in archived_projects auto section"
    )
    # And it should NOT be in the active section anymore.
    new_active = body_after.split(
        "<!-- pretel:auto:end active_projects -->"
    )[0]
    assert slug not in new_active


# ---------------------------------------------------------------------
# 6. archive_project emits project_lifecycle notify.
# ---------------------------------------------------------------------

@pytest.mark.slow
async def test_archive_project_emits_lifecycle_notify(
    awareness_env: Path,
    clean_test_artifacts: None,
) -> None:
    """archive_project triggers `pg_notify('project_lifecycle','archived:b/s')`.

    The trigger fires when status transitions active→archived (migration
    0034 `notify_project_lifecycle`). Strategy: open a dedicated sync
    listener connection and LISTEN before the archive happens, then run
    archive_project, then poll `notifies()` for the expected payload.
    """
    suffix = int(time.monotonic_ns())
    slug = f"test-archive-{suffix}"

    create_r = await create_project(
        bucket="scout",
        slug=slug,
        name=f"Lifecycle Notify {suffix}",
        description="watch the notify",
    )
    assert create_r["status"] == "ok"

    listener = psycopg.connect(_TEST_DATABASE_URL, autocommit=True)
    try:
        with listener.cursor() as cur:
            cur.execute("LISTEN project_lifecycle")

        arch_r = await archive_project(
            bucket="scout", slug=slug, reason="lifecycle smoke"
        )
        assert arch_r["status"] == "ok", arch_r

        # Drain notifications for up to 5 seconds. Pull the polling
        # off the event loop so async fixtures can finalize cleanly
        # if the assertion fails.
        def _collect() -> list[str]:
            out: list[str] = []
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                gen = listener.notifies(timeout=0.3, stop_after=1)
                for n in gen:
                    out.append(n.payload)
                if out:
                    break
            return out

        received = await asyncio.to_thread(_collect)
    finally:
        try:
            listener.close()
        except Exception:
            pass

    matching = [p for p in received if p == f"archived:scout/{slug}"]
    assert matching, (
        f"expected archived notify for scout/{slug}; received: {received}"
    )
