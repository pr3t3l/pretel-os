"""LISTEN/NOTIFY consumer that regenerates dirty READMEs (Module 7.5 B.2).

Listens on the `readme_dirty` Postgres channel emitted by the migration
0034 triggers, debounces 30 seconds, and dispatches one regeneration per
distinct dirty target. Same isolation rationale as the M6 reflection
worker: filesystem I/O should not block MCP turns; failure of the
regenerator must not affect the MCP server.

Payload contract (set by 0034 triggers):
    'bucket:<bucket_name>'
    'project:<bucket_name>/<slug>'

Run as:  python -m awareness.readme_consumer
Stop as: SIGTERM (the systemd unit sends this on stop/restart).
"""
from __future__ import annotations

import asyncio
import logging
import signal
import time
from typing import Optional

import psycopg

from awareness import readme_renderer
from mcp_server import config as config_mod

log = logging.getLogger(__name__)

NOTIFY_CHANNEL = "readme_dirty"
DEBOUNCE_SECS = 30.0
SCAN_INTERVAL_SECS = 5.0


# ---------------------------------------------------------------------
# Dispatch (sync — runs in worker thread).
# ---------------------------------------------------------------------

def _dispatch_one(database_url: str, target: str) -> None:
    """Open a fresh sync connection and regenerate a single target.

    The renderer module's regenerate_* functions are sync. We open a
    short-lived psycopg.connect() per dispatch — no pool needed at the
    expected churn rate (single-operator, debounced to 30s).
    """
    if ":" not in target:
        log.warning("invalid readme_dirty payload: %r", target)
        return
    kind, rest = target.split(":", 1)
    try:
        with psycopg.connect(database_url) as conn:
            if kind == "bucket":
                bucket = rest
                if not bucket:
                    log.warning("empty bucket in payload: %r", target)
                    return
                result = readme_renderer.regenerate_bucket_readme(conn, bucket)
                log.info(
                    "dispatched bucket=%s regenerated=%s path=%s",
                    bucket,
                    result.get("regenerated"),
                    result.get("path"),
                )
            elif kind == "project":
                if "/" not in rest:
                    log.warning("invalid project payload: %r", target)
                    return
                bucket, slug = rest.split("/", 1)
                if not bucket or not slug:
                    log.warning("empty bucket/slug in payload: %r", target)
                    return
                result = readme_renderer.regenerate_project_readme(
                    conn, bucket, slug
                )
                log.info(
                    "dispatched project=%s/%s regenerated=%s status=%s",
                    bucket,
                    slug,
                    result.get("regenerated"),
                    result.get("status"),
                )
            else:
                log.warning("unknown readme_dirty kind: %r", kind)
    except Exception:
        log.exception("dispatch failed for %r", target)


# ---------------------------------------------------------------------
# Async LISTEN + debounce loop.
# ---------------------------------------------------------------------

async def consume_readme_dirty(
    database_url: str,
    *,
    debounce_secs: float = DEBOUNCE_SECS,
    scan_interval_secs: float = SCAN_INTERVAL_SECS,
    stop_event: Optional[asyncio.Event] = None,
) -> None:
    """LISTEN on `readme_dirty`, debounce, dispatch.

    `dirty` maps target -> last-signal monotonic timestamp. Each scan
    cycle (every `scan_interval_secs`) finds targets idle for
    `debounce_secs` and dispatches them to the sync regenerator via
    `asyncio.to_thread`. Coalescing happens naturally: signals received
    during the wait simply reset the same target's timestamp.
    """
    if stop_event is None:
        stop_event = asyncio.Event()
    dirty: dict[str, float] = {}

    async def _drain_notifies() -> None:
        async with await psycopg.AsyncConnection.connect(
            database_url, autocommit=True
        ) as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"LISTEN {NOTIFY_CHANNEL}")
            log.info(
                "readme consumer LISTENing on channel=%s "
                "(debounce=%.0fs, scan=%.0fs)",
                NOTIFY_CHANNEL,
                debounce_secs,
                scan_interval_secs,
            )
            while not stop_event.is_set():
                # psycopg3 AsyncConnection.notifies() is an async iterator.
                # Use a short timeout so we re-check stop_event regularly.
                try:
                    gen = conn.notifies(timeout=1.0)
                    async for notify in gen:
                        if notify.channel != NOTIFY_CHANNEL:
                            continue
                        payload = notify.payload
                        if not payload:
                            continue
                        dirty[payload] = time.monotonic()
                        log.debug("dirty signal: %s", payload)
                except psycopg.Error as exc:
                    log.warning(
                        "readme consumer LISTEN error: %s", exc
                    )
                    # Brief backoff before re-LISTEN attempt; the outer
                    # `async with` connection is still alive in normal
                    # error cases (timeout). Cycle the loop.
                    await asyncio.sleep(1.0)

    async def _dispatch_loop() -> None:
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(
                    stop_event.wait(), timeout=scan_interval_secs
                )
                # stop_event fired; exit cleanly.
                return
            except asyncio.TimeoutError:
                pass
            now = time.monotonic()
            ready = [
                target
                for target, ts in list(dirty.items())
                if (now - ts) >= debounce_secs
            ]
            for target in ready:
                dirty.pop(target, None)
                try:
                    await asyncio.to_thread(
                        _dispatch_one, database_url, target
                    )
                except Exception:
                    log.exception("scheduling dispatch failed for %s", target)

    drain_task = asyncio.create_task(_drain_notifies())
    dispatch_task = asyncio.create_task(_dispatch_loop())

    await stop_event.wait()
    log.info("readme consumer stopping")
    drain_task.cancel()
    dispatch_task.cancel()
    await asyncio.gather(drain_task, dispatch_task, return_exceptions=True)
    log.info("readme consumer stopped")


# ---------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------

async def _main_async() -> None:
    cfg = config_mod.load_config()
    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            # Windows fallback — not relevant here, but keeps the
            # module importable in test environments.
            pass

    log.info("readme consumer started")
    await consume_readme_dirty(cfg.database_url, stop_event=stop_event)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        asyncio.run(_main_async())
    except KeyboardInterrupt:
        log.info("readme consumer interrupted")


if __name__ == "__main__":
    main()
