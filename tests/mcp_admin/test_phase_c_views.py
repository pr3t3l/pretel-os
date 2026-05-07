"""Phase C drill-down view tests — smoke for each detail page.

All tests are slow (DB-backed) — they hit pretel_os_test for fixture
rows of lessons / decisions / projects / dream_engine_runs / skills.
"""
from __future__ import annotations

import psycopg
import pytest
from fastapi.testclient import TestClient

TEST_DSN = "postgresql://pretel_os@localhost/pretel_os_test"

pytestmark = pytest.mark.slow


# ---------------------------------------------------------------- /db/{table}/{id}

def test_db_browser_rejects_unknown_table(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/db/pg_catalog.pg_user/x",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 404


def test_db_browser_renders_known_table_even_if_row_missing(
    admin_client: TestClient,
) -> None:
    """Allowed table + nonexistent id → renders shell (columns) + 'not found' panel.

    The handler does NOT 404 on missing row — it shows the column shape.
    Drill-down view always loads even when the id is bogus, which is friendlier
    for diagnostics than a hard 404.
    """
    r = admin_client.get(
        "/db/lessons/00000000-0000-0000-0000-000000000000",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Row not found" in r.text or "lessons" in r.text


# ---------------------------------------------------------------- /skills/{name}

def test_skills_detail_renders_known_skill(admin_client: TestClient) -> None:
    """skill_discovery is seeded by migration 0035 in pretel_os_test."""
    # Ensure the skill row exists; if test DB is missing it, skip
    conn = psycopg.connect(TEST_DSN, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM tools_catalog WHERE name='skill_discovery' AND kind='skill'"
            )
            if cur.fetchone() is None:
                pytest.skip("skill_discovery not seeded in pretel_os_test")
    finally:
        conn.close()

    r = admin_client.get(
        "/skills/skill_discovery",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "skill_discovery" in r.text
    assert "Metadata" in r.text


def test_skills_detail_404_for_unknown(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/skills/__nonexistent__",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 404


# ---------------------------------------------------------------- /projects/{bucket}/{slug}

def test_project_detail_404_for_unknown(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/projects/personal/__nonexistent__",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 404


# ---------------------------------------------------------------- /dream-engine/run/{run_id}

def test_dream_run_detail_404_for_unknown(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/dream-engine/run/00000000-0000-0000-0000-000000000000",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 404


def test_dream_run_detail_renders_real_run(admin_client: TestClient) -> None:
    """Seed a fake row in dream_engine_runs and render its detail page."""
    conn = psycopg.connect(TEST_DSN, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dream_engine_runs (status, jobs_run, failures, worker_pid)
                VALUES ('success',
                        '{"utility_recompute": {"duration_ms": 8, "rows_affected": 42}}'::jsonb,
                        '[]'::jsonb,
                        12345)
                RETURNING id
                """
            )
            row = cur.fetchone()
            assert row is not None
            run_id = str(row[0])
            cur.execute(
                "UPDATE dream_engine_runs SET completed_at = started_at + interval '15 ms' WHERE id = %s",
                (run_id,),
            )

        try:
            r = admin_client.get(
                f"/dream-engine/run/{run_id}",
                headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
            )
            assert r.status_code == 200
            assert "utility_recompute" in r.text
            assert "12345" in r.text  # worker_pid
        finally:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM dream_engine_runs WHERE id = %s", (run_id,))
    finally:
        conn.close()


# ---------------------------------------------------------------- /memory/lessons/{id}

def test_lesson_detail_404_for_unknown(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/memory/lessons/00000000-0000-0000-0000-000000000000",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 404


def test_lesson_detail_renders_real_lesson(admin_client: TestClient) -> None:
    """Seed a lesson and verify the detail page renders title + content + tags."""
    conn = psycopg.connect(TEST_DSN, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO lessons
                    (title, content, next_time, bucket, category, tags, status, source)
                VALUES
                    ('Phase C smoke test lesson',
                     'Body content for the smoke test',
                     'Next time, ensure the smoke test passes',
                     'business', 'INFRA', ARRAY['m10', 'phase-c-smoke'],
                     'active', 'phase_c_test')
                RETURNING id
                """
            )
            row = cur.fetchone()
            assert row is not None
            lesson_id = str(row[0])

        try:
            r = admin_client.get(
                f"/memory/lessons/{lesson_id}",
                headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
            )
            assert r.status_code == 200
            assert "Phase C smoke test lesson" in r.text
            assert "Body content for the smoke test" in r.text
            assert "phase-c-smoke" in r.text
        finally:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM lessons WHERE id = %s", (lesson_id,))
    finally:
        conn.close()


# ---------------------------------------------------------------- hyperlinks from list views

def test_memory_list_links_to_drill_downs(admin_client: TestClient) -> None:
    """Lessons tab title cells are clickable links to /memory/lessons/{id}."""
    r = admin_client.get(
        "/memory?tab=lessons",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    # Either a real link is present or the table is empty (acceptable in test DB)
    assert 'href="/memory/lessons/' in r.text or "Sin resultados" in r.text


def test_dream_engine_list_links_to_run_detail(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/dream-engine",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert 'href="/dream-engine/run/' in r.text or "No runs" in r.text
