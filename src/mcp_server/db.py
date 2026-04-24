"""Lazy async Postgres connection pool with a 30 s health poller.

Per CONSTITUTION §8.43 (a): the MCP server starts and registers tools with
clients regardless of Postgres availability. A module-level boolean
`_db_healthy` is flipped by the poller every 30 s. Tools call `is_healthy()`
before doing DB work and branch into degraded-mode responses when false.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from psycopg_pool import AsyncConnectionPool

from . import config as config_mod

log = logging.getLogger(__name__)

_pool: Optional[AsyncConnectionPool] = None
_db_healthy: bool = False
_poller_task: Optional[asyncio.Task] = None
_HEALTH_INTERVAL_SECONDS = 30


def get_pool() -> AsyncConnectionPool:
    """Return the process-wide async pool, creating it on first call.

    Creation does not open connections eagerly — psycopg_pool's `open=False`
    plus an explicit `.open()` call below keeps the startup non-blocking even
    when Postgres is down. Connections are opened lazily on first use.
    """
    global _pool
    if _pool is None:
        cfg = config_mod.load_config()
        _pool = AsyncConnectionPool(
            conninfo=cfg.database_url,
            min_size=1,
            max_size=10,
            open=False,
            timeout=5.0,
        )
    return _pool


async def _open_pool_once() -> None:
    pool = get_pool()
    try:
        await pool.open(wait=False)
    except Exception as exc:
        log.warning("pool open failed (will retry on demand): %s", exc)


async def _probe_once() -> bool:
    pool = get_pool()
    try:
        async with pool.connection(timeout=3.0) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                row = await cur.fetchone()
                return row is not None and row[0] == 1
    except Exception as exc:
        log.debug("db probe failed: %s", exc)
        return False


async def _poller() -> None:
    global _db_healthy
    while True:
        healthy = await _probe_once()
        if healthy != _db_healthy:
            log.info("db_healthy transition: %s -> %s", _db_healthy, healthy)
        _db_healthy = healthy
        await asyncio.sleep(_HEALTH_INTERVAL_SECONDS)


async def start_background_health_check() -> None:
    global _poller_task
    await _open_pool_once()
    if _poller_task is None or _poller_task.done():
        _poller_task = asyncio.create_task(_poller(), name="db-health-poller")


async def stop_background_health_check() -> None:
    global _poller_task, _pool
    if _poller_task is not None:
        _poller_task.cancel()
        try:
            await _poller_task
        except asyncio.CancelledError:
            pass
        _poller_task = None
    if _pool is not None:
        try:
            await _pool.close()
        except Exception:
            pass
        _pool = None


def is_healthy() -> bool:
    return _db_healthy
