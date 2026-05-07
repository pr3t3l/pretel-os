"""Shared fixtures for mcp_admin tests.

Patches `mcp_server.config.load_config` to redirect the FastAPI app's
DB pool at `pretel_os_test`. Uses fastapi.testclient.TestClient which
runs the lifespan correctly (opens + closes the DB pool around tests).

`seed_archive_prefs` fixture guarantees the 3 thresholds from migration
0039 are present even after the autouse `_truncate_between_tests`
fixture in the repo-root conftest wipes `operator_preferences`.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace as dc_replace
from typing import Any

import psycopg
import pytest
from fastapi.testclient import TestClient

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"


@pytest.fixture
def seed_archive_prefs() -> None:
    """Idempotent seed of the 3 archive thresholds from migration 0039."""
    conn = psycopg.connect(TEST_DSN, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO operator_preferences
                    (category, key, value, scope, source, metadata)
                VALUES
                    ('workflow', 'archive.usage_window_days',     '500', 'global', 'migration',
                        '{"unit": "days", "purpose": "Days-since-creation threshold for archive eligibility"}'::jsonb),
                    ('workflow', 'archive.utility_threshold',     '0.5', 'global', 'migration',
                        '{"unit": "score", "purpose": "utility_score floor below which a low-usage lesson is archive-eligible"}'::jsonb),
                    ('workflow', 'archive.utility_lookback_days',  '90', 'global', 'migration',
                        '{"unit": "days", "purpose": "Lookback window over which utility_threshold is evaluated"}'::jsonb)
                ON CONFLICT (category, key, scope) DO UPDATE
                SET value = EXCLUDED.value,
                    active = true,
                    updated_at = now()
                """
            )
    finally:
        conn.close()


@pytest.fixture
def patched_admin_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect mcp_server.config.load_config to use the test DB,
    and force is_healthy() = True (no background poller in tests)."""
    from mcp_server import config as cfg_mod
    from mcp_server import db as db_mod

    original = cfg_mod.load_config

    def _override() -> Any:
        loaded = original()
        return dc_replace(loaded, database_url=TEST_DSN)

    monkeypatch.setattr(cfg_mod, "load_config", _override)
    # Force a fresh pool against the patched DSN
    monkeypatch.setattr(db_mod, "_pool", None, raising=False)
    # Skip the lifespan health-check poller in tests
    monkeypatch.setattr(db_mod, "_db_healthy", True, raising=False)
    monkeypatch.setattr(db_mod, "is_healthy", lambda: True)

    async def _noop() -> None:
        return None

    monkeypatch.setattr(db_mod, "start_background_health_check", _noop)
    monkeypatch.setattr(db_mod, "stop_background_health_check", _noop)


@pytest.fixture
def admin_client(patched_admin_config: None) -> Iterator[TestClient]:
    """TestClient wrapping the FastAPI app — runs lifespan on enter/exit."""
    # Late import so the patched config is in place when build_app runs.
    from mcp_admin.main import build_app

    app = build_app()
    with TestClient(app) as client:
        yield client
