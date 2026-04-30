"""Tests for `awareness.readme_consumer` — Module 7.5 Phase E E.2.

Three slow tests exercising LISTEN + debounce + multi-target dispatch.
The tests run their OWN consumer instance against `pretel_os_test`. The
in-production `pretel-os-readme.service` listens on `pretel_os` (prod)
— Postgres NOTIFY is per-database, so the two consumers are isolated
even though both use the `readme_dirty` channel name.

Strategy: monkeypatch `_dispatch_one` to capture (database_url, target)
tuples instead of running the renderer. The dispatch path is exercised
end-to-end via test_awareness.py / test_archive_project_*; here we
isolate the listener + debounce logic.

Note on the consumer's keyword arguments:
  consume_readme_dirty already accepts `debounce_secs`, `scan_interval_secs`,
  and `stop_event` parameters in its RUN 1 implementation. No source
  changes required for E.2.
"""
from __future__ import annotations

import asyncio
import os
import time
from typing import AsyncIterator

import psycopg
import pytest

from awareness import readme_consumer

_TEST_DATABASE_URL = os.environ.get(
    "PRETEL_OS_TEST_DATABASE_URL",
    "postgresql://pretel_os@localhost/pretel_os_test",
)


pytestmark = pytest.mark.slow


def _fire_notify(payload: str) -> None:
    """Emit pg_notify('readme_dirty', payload) from a fresh autocommit conn."""
    with psycopg.connect(_TEST_DATABASE_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_notify('readme_dirty', %s)", (payload,))


async def _spawn_consumer(
    monkeypatch: pytest.MonkeyPatch,
    *,
    debounce_secs: float = 1.5,
    scan_interval_secs: float = 0.3,
) -> tuple[
    asyncio.Task[None],
    asyncio.Event,
    list[tuple[str, str]],
]:
    """Spin up consume_readme_dirty with _dispatch_one stubbed.

    Returns (task, stop_event, calls). Caller is responsible for
    setting stop_event and awaiting the task.
    """
    calls: list[tuple[str, str]] = []

    def fake_dispatch(database_url: str, target: str) -> None:
        calls.append((database_url, target))

    monkeypatch.setattr(readme_consumer, "_dispatch_one", fake_dispatch)

    stop = asyncio.Event()
    task = asyncio.create_task(
        readme_consumer.consume_readme_dirty(
            _TEST_DATABASE_URL,
            debounce_secs=debounce_secs,
            scan_interval_secs=scan_interval_secs,
            stop_event=stop,
        )
    )
    # Give the LISTEN registration a chance to attach before the test
    # fires NOTIFYs on a different connection.
    await asyncio.sleep(0.5)
    return task, stop, calls


async def _shutdown(task: asyncio.Task[None], stop: asyncio.Event) -> None:
    stop.set()
    try:
        await asyncio.wait_for(task, timeout=3.0)
    except asyncio.TimeoutError:
        task.cancel()


# ---------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------

async def test_listener_receives_notification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pg_notify on `readme_dirty` reaches the consumer's dispatcher.

    With debounce=0.5s, a single NOTIFY → wait > debounce → expect one
    dispatch with the unique target.
    """
    task, stop, calls = await _spawn_consumer(
        monkeypatch, debounce_secs=0.5, scan_interval_secs=0.2
    )
    try:
        target = f"bucket:__test_listener_{int(time.monotonic_ns())}"
        _fire_notify(target)

        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and not any(
            t == target for _, t in calls
        ):
            await asyncio.sleep(0.1)

        assert any(t == target for _, t in calls), (
            f"expected dispatch for {target!r}; calls={calls}"
        )
    finally:
        await _shutdown(task, stop)


async def test_debounce_coalesces_signals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """5 rapid NOTIFYs for the same target produce ONE dispatch.

    The key contract: bulk operations (e.g. M6 reflection_worker writing
    several lessons) must not trigger a regeneration per row. The 30s
    production debounce is shrunk to 1.5s here so the test stays fast.
    """
    task, stop, calls = await _spawn_consumer(
        monkeypatch, debounce_secs=1.5, scan_interval_secs=0.2
    )
    try:
        target = f"bucket:__test_debounce_{int(time.monotonic_ns())}"
        for _ in range(5):
            _fire_notify(target)

        # Wait > debounce so the dispatch has fired.
        await asyncio.sleep(2.5)

        matched = [t for _, t in calls if t == target]
        assert len(matched) == 1, (
            f"expected exactly 1 dispatch for {target!r}, got {len(matched)}"
            f" — full calls: {calls}"
        )
    finally:
        await _shutdown(task, stop)


async def test_different_targets_dispatched_separately(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two distinct targets each receive their own dispatch."""
    task, stop, calls = await _spawn_consumer(
        monkeypatch, debounce_secs=1.0, scan_interval_secs=0.2
    )
    try:
        suffix = int(time.monotonic_ns())
        target_a = f"bucket:__test_multi_a_{suffix}"
        target_b = f"bucket:__test_multi_b_{suffix}"

        _fire_notify(target_a)
        _fire_notify(target_b)

        # Wait > debounce.
        await asyncio.sleep(2.0)

        seen = {t for _, t in calls}
        assert target_a in seen, f"missing dispatch for {target_a!r}; calls={calls}"
        assert target_b in seen, f"missing dispatch for {target_b!r}; calls={calls}"
    finally:
        await _shutdown(task, stop)
