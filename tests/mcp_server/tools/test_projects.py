"""Integration tests for `mcp_server.tools.projects` + router unknown-project hint.

Eight tests covering create_project (happy path, dedup, invalid bucket,
slug normalization), get_project (found / not_found), list_projects
(filter by bucket), and the router's unknown_project hint when a
classifier picks a (bucket, project) that has no registry row and no
README on disk.

All tests are `@pytest.mark.slow` because they hit the real test DB
(`pretel_os_test`). Fixtures are inline in this file (no conftest.py
additions): each test gets a clean `projects` / `project_state` /
`project_versions` slate via TRUNCATE, and `config_mod.REPO_ROOT` is
redirected to a `tmp_path` so README writes don't pollute the working
tree.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, AsyncIterator
from unittest.mock import MagicMock

import psycopg
import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from mcp_server import config as config_mod
from mcp_server import db as db_mod
from mcp_server.router.types import (
    BundleMetadata,
    LayerBundle,
    LayerContent,
)
from mcp_server.tools.projects import (
    _normalize_slug,
    _validate_bucket,
    create_project,
    get_project,
    list_projects,
)

pytestmark = pytest.mark.slow


_TEST_DATABASE_URL = os.environ.get(
    "PRETEL_OS_TEST_DATABASE_URL",
    "postgresql://pretel_os@localhost/pretel_os_test",
)


# ───────────────────────── inline fixtures ────────────────────────────────

@pytest_asyncio.fixture
async def projects_pool() -> AsyncIterator[AsyncConnectionPool]:
    """Function-scoped pool against the test DB.

    Function-scoped (not session-scoped) on purpose: each test opens
    a fresh pool so we don't fight the suite-wide session pool's
    asyncio event loop binding. Cost is negligible — local Postgres,
    1 connection.
    """
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
async def patch_db(
    projects_pool: AsyncConnectionPool,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[None]:
    """Force production db_mod helpers to use the test pool."""
    async def _noop() -> None:
        return None

    monkeypatch.setattr(db_mod, "_pool", projects_pool, raising=False)
    monkeypatch.setattr(db_mod, "_db_healthy", True, raising=False)
    monkeypatch.setattr(db_mod, "is_healthy", lambda: True)
    monkeypatch.setattr(db_mod, "get_pool", lambda: projects_pool)
    monkeypatch.setattr(db_mod, "start_background_health_check", _noop)
    monkeypatch.setattr(db_mod, "stop_background_health_check", _noop)
    yield


@pytest_asyncio.fixture
async def clean_projects_tables(
    projects_pool: AsyncConnectionPool,
) -> AsyncIterator[None]:
    """TRUNCATE projects / project_state / project_versions before each test."""
    async with projects_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "TRUNCATE TABLE projects, project_state, project_versions "
                "RESTART IDENTITY CASCADE"
            )
        await conn.commit()
    yield


@pytest.fixture
def patch_repo_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Redirect README writes to tmp_path so the real repo stays clean."""
    monkeypatch.setattr(config_mod, "REPO_ROOT", tmp_path)
    return tmp_path


async def _select_one(
    pool: AsyncConnectionPool, sql: str, params: tuple[Any, ...]
) -> tuple[Any, ...] | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()


# ──────────────────────────── tests ──────────────────────────────────────


async def test_create_project_happy_path(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
    projects_pool: AsyncConnectionPool,
) -> None:
    r = await create_project(
        bucket="business",
        slug="declassified",
        name="Declassified Cases",
        description="True-crime product line",
        objective="Ship 50 packs by Q3",
        stack=["n8n", "python"],
        skills_used=["sdd"],
    )

    assert r["status"] == "ok"
    assert r["slug"] == "declassified"
    assert r["readme_path"] == "buckets/business/projects/declassified/README.md"
    project_id = r["id"]

    # 1) projects row written with readme_path populated.
    row = await _select_one(
        projects_pool,
        "SELECT bucket, slug, name, description, status, stack, skills_used, "
        "objective, readme_path FROM projects WHERE id = %s",
        (project_id,),
    )
    assert row == (
        "business",
        "declassified",
        "Declassified Cases",
        "True-crime product line",
        "active",
        ["n8n", "python"],
        ["sdd"],
        "Ship 50 packs by Q3",
        "buckets/business/projects/declassified/README.md",
    )

    # 2) README on disk under the patched REPO_ROOT.
    readme = patch_repo_root / "buckets/business/projects/declassified/README.md"
    assert readme.exists()
    body = readme.read_text(encoding="utf-8")
    assert body.startswith("# Declassified Cases")
    assert "Bucket: business" in body
    assert "Status: Active" in body
    assert "Objective: Ship 50 packs by Q3" in body
    assert "- n8n" in body
    assert "- sdd" in body

    # 3) initial project_state row.
    state_row = await _select_one(
        projects_pool,
        "SELECT state_key, content, status FROM project_state "
        "WHERE bucket = %s AND project = %s",
        ("business", "declassified"),
    )
    assert state_row == ("status", "active", "open")

    # 4) project_versions snapshot.
    snap_row = await _select_one(
        projects_pool,
        "SELECT snapshot_reason, triggered_by, "
        "       readme_content = %s AS body_match "
        "FROM project_versions WHERE bucket = %s AND project = %s",
        (body, "business", "declassified"),
    )
    assert snap_row == ("project_created", "create_project_tool", True)


async def test_create_project_already_exists(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
    projects_pool: AsyncConnectionPool,
) -> None:
    first = await create_project(
        bucket="personal",
        slug="garage-rebuild",
        name="Garage Rebuild",
        description="Workshop reorg",
    )
    assert first["status"] == "ok"

    second = await create_project(
        bucket="personal",
        slug="garage-rebuild",
        name="Garage Rebuild Take 2",
        description="Different description",
    )
    assert second["status"] == "exists"
    assert second["id"] == first["id"]
    assert second["slug"] == "garage-rebuild"
    assert "already exists" in second["message"].lower()

    # Exactly one row in projects, exactly one snapshot.
    row = await _select_one(
        projects_pool,
        "SELECT count(*)::int FROM projects WHERE bucket = %s AND slug = %s",
        ("personal", "garage-rebuild"),
    )
    assert row == (1,)
    snap = await _select_one(
        projects_pool,
        "SELECT count(*)::int FROM project_versions WHERE bucket = %s AND project = %s",
        ("personal", "garage-rebuild"),
    )
    assert snap == (1,)


async def test_create_project_invalid_bucket(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
) -> None:
    r = await create_project(
        bucket="random-bucket",
        slug="anything",
        name="X",
        description="Y",
    )
    assert r["status"] == "error"
    assert "invalid bucket" in r["error"]

    # Empty freelance suffix is also invalid.
    r2 = await create_project(
        bucket="freelance:",
        slug="anything",
        name="X",
        description="Y",
    )
    assert r2["status"] == "error"

    # Properly-suffixed freelance bucket passes validation.
    assert _validate_bucket("freelance:acme") is None


async def test_create_project_slug_normalization(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
    projects_pool: AsyncConnectionPool,
) -> None:
    # Pure helper sanity.
    assert _normalize_slug("My Project!") == "my-project"
    assert _normalize_slug("  Hello   World  ") == "hello-world"
    assert _normalize_slug("CAPS_with_under") == "caps-with-under"
    assert _normalize_slug("--leading--and--trailing--") == "leading-and-trailing"

    # End-to-end: passing the unnormalized slug stores the normalized one
    # and the README path uses the normalized slug too.
    r = await create_project(
        bucket="business",
        slug="My Project!",
        name="My Project",
        description="d",
    )
    assert r["status"] == "ok"
    assert r["slug"] == "my-project"
    assert r["readme_path"] == "buckets/business/projects/my-project/README.md"

    row = await _select_one(
        projects_pool,
        "SELECT slug FROM projects WHERE id = %s",
        (r["id"],),
    )
    assert row == ("my-project",)


async def test_get_project_found(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
) -> None:
    created = await create_project(
        bucket="scout",
        slug="vett-replit-april-2026",
        name="VETT Replit Apr 2026",
        description="First VETT eval",
        stack=["replit"],
        skills_used=["vett"],
    )
    assert created["status"] == "ok"

    r = await get_project(bucket="scout", slug="vett-replit-april-2026")
    assert r["status"] == "ok"
    assert r["found"] is True
    assert r["project"]["id"] == created["id"]
    assert r["project"]["bucket"] == "scout"
    assert r["project"]["slug"] == "vett-replit-april-2026"
    assert r["project"]["name"] == "VETT Replit Apr 2026"
    assert r["project"]["stack"] == ["replit"]
    assert r["project"]["skills_used"] == ["vett"]
    assert r["project"]["readme_path"] == (
        "buckets/scout/projects/vett-replit-april-2026/README.md"
    )

    # README content streams back from disk.
    assert r["readme_content"] is not None
    assert "VETT Replit Apr 2026" in r["readme_content"]
    assert "- replit" in r["readme_content"]


async def test_get_project_not_found(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
) -> None:
    r = await get_project(bucket="business", slug="does-not-exist")
    assert r["status"] == "ok"
    assert r["found"] is False
    assert "project" not in r
    assert "readme_content" not in r


async def test_list_projects_by_bucket(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
) -> None:
    await create_project(bucket="business", slug="biz-a", name="A", description="x")
    await create_project(bucket="business", slug="biz-b", name="B", description="x")
    await create_project(bucket="personal", slug="pers-a", name="P", description="x")
    await create_project(bucket="scout", slug="scout-a", name="S", description="x")

    biz = await list_projects(bucket="business")
    assert biz["status"] == "ok"
    slugs = sorted(row["slug"] for row in biz["results"])
    assert slugs == ["biz-a", "biz-b"]
    for row in biz["results"]:
        assert row["bucket"] == "business"
        assert row["status"] == "active"
        assert "id" in row and "name" in row and "created_at" in row

    # status filter still works alongside bucket filter.
    none_closed = await list_projects(bucket="business", status="closed")
    assert none_closed["status"] == "ok"
    assert none_closed["results"] == []

    # No filter: returns all four.
    all_proj = await list_projects()
    assert all_proj["status"] == "ok"
    assert {row["slug"] for row in all_proj["results"]} == {
        "biz-a", "biz-b", "pers-a", "scout-a",
    }


async def test_router_unknown_project_hint(
    patch_db: None,
    clean_projects_tables: None,
    patch_repo_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Classifier picks a (bucket, project) with no registry row and no
    on-disk README. Router response must carry the unknown_project hint."""
    from types import SimpleNamespace

    from mcp_server.router import router as router_mod
    from mcp_server.router.cache import LayerBundleCache

    classification = {
        "bucket": "business",
        "project": "ghost-project",
        "complexity": "LOW",
        "needs_lessons": False,
    }
    # _telemetry_to_llm_call_data only reads model + token fields, so a
    # duck-typed namespace is enough — avoids the full ChatJsonTelemetry
    # dataclass with its dozen required attributes.
    telemetry = SimpleNamespace(
        model="stub",
        prompt_tokens=0,
        completion_tokens=0,
        cache_read_tokens=0,
    )

    def fake_classify(**kwargs: Any) -> tuple[dict[str, Any], SimpleNamespace]:
        return classification, telemetry

    async def fake_assemble(**kwargs: Any) -> LayerBundle:
        layers = tuple(
            LayerContent(layer=name, blocks=(), token_count=0, loaded=False)
            for name in ("L0", "L1", "L2", "L3", "L4")
        )
        meta = BundleMetadata(
            bucket="business",
            project="ghost-project",
            classifier_hash="test",
            total_tokens=0,
            assembly_latency_ms=0,
            cache_hit=False,
            over_budget_layers=(),
        )
        return LayerBundle(layers=layers, metadata=meta)

    monkeypatch.setattr(router_mod, "classify", fake_classify)
    monkeypatch.setattr(router_mod, "assemble_bundle", fake_assemble)
    monkeypatch.setattr(router_mod, "detect_invariant_violations", lambda b: [])
    monkeypatch.setattr(router_mod, "_recommend_tools", lambda *a, **k: [])
    monkeypatch.setattr(router_mod, "start_request", lambda *a, **k: "req-test")
    monkeypatch.setattr(router_mod, "log_classification", lambda *a, **k: None)
    monkeypatch.setattr(router_mod, "log_layers", lambda *a, **k: None)
    monkeypatch.setattr(router_mod, "log_rag", lambda *a, **k: None)
    monkeypatch.setattr(router_mod, "log_conflicts", lambda *a, **k: None)
    monkeypatch.setattr(router_mod, "log_completion", lambda *a, **k: None)

    cache = MagicMock(spec=LayerBundleCache)

    with psycopg.connect(_TEST_DATABASE_URL) as conn:
        response = await router_mod.get_context(
            conn=conn,
            message="ping",
            session_id=None,
            client_origin="test",
            repo_root=patch_repo_root,
            cache=cache,
        )

    assert "unknown_project" in response, (
        f"expected unknown_project hint, got keys: {sorted(response.keys())}"
    )
    hint = response["unknown_project"]
    assert hint["bucket"] == "business"
    assert hint["slug"] == "ghost-project"
    assert hint["create_project_hint"] is True
    assert "create_project" in hint["message"]

    # Once the project is registered, the same call should NOT carry the hint.
    create_r = await create_project(
        bucket="business",
        slug="ghost-project",
        name="Ghost",
        description="now real",
    )
    assert create_r["status"] == "ok"

    with psycopg.connect(_TEST_DATABASE_URL) as conn2:
        response2 = await router_mod.get_context(
            conn=conn2,
            message="ping",
            session_id=None,
            client_origin="test",
            repo_root=patch_repo_root,
            cache=cache,
        )
    assert "unknown_project" not in response2
