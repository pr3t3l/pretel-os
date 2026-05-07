"""Slow integration tests — full request → DB round-trip against pretel_os_test.

Verifies that the 3 archive thresholds seeded by migration 0039 appear
in the rendered HTML and that POST /preferences/{cat}/{key} actually
mutates the row through the MCP tool path.
"""
from __future__ import annotations

import psycopg
import pytest
from fastapi.testclient import TestClient

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"

pytestmark = pytest.mark.slow


@pytest.fixture
def db_conn() -> psycopg.Connection:  # type: ignore[misc]
    """Sync connection to test DB for verification queries."""
    conn = psycopg.connect(TEST_DSN, autocommit=False)
    try:
        yield conn  # type: ignore[misc]
    finally:
        conn.rollback()
        conn.close()


def test_get_preferences_renders_archive_thresholds(
    seed_archive_prefs: None,
    admin_client: TestClient,
) -> None:
    """SC3 verification — preferences view shows the 3 archive thresholds."""
    r = admin_client.get(
        "/preferences",
        headers={"Cf-Access-Authenticated-User-Email": "operator@example.com"},
    )
    assert r.status_code == 200, f"got {r.status_code}: {r.text[:300]}"
    html = r.text
    assert "archive.usage_window_days" in html
    assert "archive.utility_threshold" in html
    assert "archive.utility_lookback_days" in html
    # User pill renders identity from Cf-Access header
    assert "operator@example.com" in html


def test_post_preference_routes_through_mcp_tool(
    seed_archive_prefs: None,
    admin_client: TestClient,
    db_conn: psycopg.Connection,
) -> None:
    """SC4 verification — POST mutates via the MCP tool path."""
    # Read original value
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT value FROM operator_preferences
            WHERE  category='workflow'
              AND  key='archive.usage_window_days'
              AND  scope='global'
            """
        )
        row = cur.fetchone()
    assert row is not None, (
        "archive.usage_window_days missing in pretel_os_test — "
        "re-apply migration 0039 to test DB"
    )
    original = row[0]

    new_value = "777"
    try:
        r = admin_client.post(
            "/preferences/workflow/archive.usage_window_days",
            data={"value": new_value},
            headers={"Cf-Access-Authenticated-User-Email": "operator@example.com"},
            follow_redirects=False,
        )
        assert r.status_code == 303
        assert r.headers["location"] == "/preferences"

        # Verify the row changed (separate connection — preference_set
        # commits in its own transaction, not in db_conn's).
        verify = psycopg.connect(TEST_DSN, autocommit=True)
        try:
            with verify.cursor() as cur:
                cur.execute(
                    """
                    SELECT value FROM operator_preferences
                    WHERE  category='workflow'
                      AND  key='archive.usage_window_days'
                      AND  scope='global'
                    """
                )
                row = cur.fetchone()
        finally:
            verify.close()

        assert row is not None
        assert row[0] == new_value
    finally:
        # Restore original via direct UPDATE (test cleanup, not subject
        # to the §2.1 invariant)
        cleanup = psycopg.connect(TEST_DSN, autocommit=True)
        try:
            with cleanup.cursor() as cur:
                cur.execute(
                    """
                    UPDATE operator_preferences
                    SET    value = %s, updated_at = now()
                    WHERE  category='workflow'
                      AND  key='archive.usage_window_days'
                      AND  scope='global'
                    """,
                    (original,),
                )
        finally:
            cleanup.close()
