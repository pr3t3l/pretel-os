"""Pytest configuration + fixtures for the pretel-os test suite.

Adds repo root to sys.path so `from src.mcp_server...` works without an
installed package (the repo has no pyproject.toml yet — Module 1 shipped
with a flat layout). pytest's autodiscovery places test imports relative
to the test file's directory, not the repo root.

Beyond sys.path, this file provides M0.X Phase D fixtures:

- session-scoped event loop + test pool against `pretel_os_test`
- autouse TRUNCATE between tests so each test starts clean
- `patched_db` — replaces production db_mod with the test pool
- `patched_embed` — mocks OpenAI embedding with a deterministic 3072-dim vector
- `db_unhealthy` — flips is_healthy() to False for degraded-mode tests
- `journal_dir` — redirects fallback journal writes to a tmp_path
- `fixed_embedding` — the deterministic vector used by patched_embed

The M4 Phase A tests (tests/router/*) predate this file and use their
own setUp via mocks/monkeypatch on a per-test basis. They continue to
work because none of these fixtures are autouse-with-yield-effects
(only `_truncate_between_tests` is autouse and it's a no-op when no
test_pool fixture is requested transitively).
"""
from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import replace as dc_replace
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Optional

import pytest
import pytest_asyncio

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Also insert src/ so `from mcp_server...` works (the systemd unit runs
# python -m mcp_server.main from inside src/, so production imports use
# the bare `mcp_server` package; mirror that for tests).
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psycopg_pool import AsyncConnectionPool  # noqa: E402  (sys.path setup must precede)


TEST_DATABASE_URL = os.environ.get(
    "PRETEL_OS_TEST_DATABASE_URL",
    "postgresql://pretel_os@localhost/pretel_os_test",
)


# Tables that any M0.X test might touch — TRUNCATE in dependency-safe order.
# decisions and lessons NOT truncated by default — they hold ADR seeds and
# historical data. Tests that mutate them must clean up their own rows by id.
_TRUNCATE_TABLES = [
    "pending_embeddings",
    "router_feedback",
    "best_practices",
    "tasks",
    "operator_preferences",
]


@pytest.fixture(scope="session")
def event_loop() -> Any:
    """One event loop for the whole session — psycopg_pool dislikes multi-loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_pool() -> AsyncIterator[AsyncConnectionPool]:
    """Session-scoped pool against the test database."""
    pool = AsyncConnectionPool(
        conninfo=TEST_DATABASE_URL,
        min_size=1,
        max_size=4,
        open=False,
        timeout=5.0,
    )
    await pool.open(wait=True)
    try:
        yield pool
    finally:
        await pool.close()


@pytest_asyncio.fixture(autouse=True)
async def _truncate_between_tests(request: pytest.FixtureRequest) -> AsyncIterator[None]:
    """Reset M0.X table state after each test that touches the test DB.

    Gated on `patched_db` in fixturenames (not `test_pool`) because tools
    insert rows whenever they're called against the test DB, even when the
    test doesn't SELECT-verify directly. Every M0.X test requests
    `patched_db`; M4 router tests (mocks only) don't, so this fixture is a
    no-op for them and they pay no TRUNCATE cost.
    """
    yield
    if "patched_db" not in request.fixturenames:
        return
    pool: AsyncConnectionPool = request.getfixturevalue("test_pool")
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            for tbl in _TRUNCATE_TABLES:
                await cur.execute(f"TRUNCATE TABLE {tbl} RESTART IDENTITY CASCADE")
        await conn.commit()


@pytest_asyncio.fixture
async def patched_db(
    test_pool: AsyncConnectionPool, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[None]:
    """Force the production db_mod to use the test pool and report healthy.

    Each tool calls `db_mod.is_healthy()` and `db_mod.get_pool()`. We
    replace both so tools talk to `pretel_os_test`.
    """
    from mcp_server import db as db_mod

    monkeypatch.setattr(db_mod, "_pool", test_pool, raising=False)
    monkeypatch.setattr(db_mod, "_db_healthy", True, raising=False)
    monkeypatch.setattr(db_mod, "is_healthy", lambda: True)
    monkeypatch.setattr(db_mod, "get_pool", lambda: test_pool)
    yield


@pytest.fixture
def fixed_embedding() -> list[float]:
    """Deterministic 3072-dim vector for mock embedding."""
    return [(i % 100) / 100.0 for i in range(3072)]


@pytest_asyncio.fixture
async def patched_embed(
    monkeypatch: pytest.MonkeyPatch, fixed_embedding: list[float]
) -> AsyncIterator[Callable[[Optional[list[float]]], None]]:
    """Mock `embeddings.embed()` — returns `fixed_embedding` by default.

    Yields a setter so individual tests can override per-call:

        async def test_x(patched_embed):
            patched_embed(None)  # next call returns None (failure path)
    """
    from mcp_server import embeddings as emb_mod

    state: dict[str, Optional[list[float]]] = {"value": fixed_embedding}

    async def fake_embed(text: str) -> Optional[list[float]]:
        return state["value"]

    monkeypatch.setattr(emb_mod, "embed", fake_embed)

    def set_next(value: Optional[list[float]]) -> None:
        state["value"] = value

    yield set_next


@pytest_asyncio.fixture
async def db_unhealthy(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[None]:
    """Make tools believe the DB is down — for degraded-mode tests."""
    from mcp_server import db as db_mod

    monkeypatch.setattr(db_mod, "is_healthy", lambda: False)
    yield


@pytest.fixture
def journal_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the fallback journal to a tmp directory for this test.

    The production `journal_mod._journal_path()` resolves the journal
    directory each call via `config_mod.load_config().fallback_journal_dir`.
    `Config` is a frozen dataclass, so we patch the loader to return a
    clone with the directory replaced.
    """
    from mcp_server import config as config_mod

    original_load = config_mod.load_config

    def _patched_load() -> Any:
        cfg = original_load()
        return dc_replace(cfg, fallback_journal_dir=tmp_path)

    monkeypatch.setattr(config_mod, "load_config", _patched_load)
    return tmp_path
