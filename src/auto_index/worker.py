"""Auto-index daemon — drains `pending_embeddings` into target rows.

The trigger `notify_missing_embedding` (migrations 0028a + 0030) inserts
a row into `pending_embeddings(target_table, target_id, source_text)`
and emits `pg_notify('embedding_queue', '<table>:<uuid>')` whenever a
write touches a table whose embedding column is NULL.

This worker is the consumer side of that contract. For each pending row
it calls OpenAI `text-embedding-3-large`, writes the vector back to the
target table, and deletes the queue row. On failure it bumps `attempts`
and records `last_error` so the operator can see the backlog in
mcp_admin.

Three event sources, in priority order:
  1. Initial drain on startup — covers any backlog accumulated while the
     daemon was down (Postgres does not replay missed NOTIFYs).
  2. LISTEN on `embedding_queue` — real-time wakeup for new writes.
  3. Periodic scan every SCAN_INTERVAL_SECS — safety net for any signal
     dropped between (1) and (2).

Concurrency: process at most MAX_CONCURRENT rows in flight. OpenAI's
embeddings tier limits are generous (≥3000 RPM at our usage), but
parallelism here is mostly about not blocking the LISTEN loop.

Schema-coupling: the set of tables that participate is the union of
TG_TABLE_NAME branches in `notify_missing_embedding`. We mirror that
list as `INDEXABLE_TABLES`. Any table added to the trigger must also
be added here — both lists move in the same migration.
"""
from __future__ import annotations

import asyncio
import logging
import signal
import time
from typing import Optional

import psycopg
from psycopg_pool import AsyncConnectionPool

from mcp_server import config as config_mod
from mcp_server import embeddings as emb_mod
from mcp_server.tools._common import vector_literal

log = logging.getLogger(__name__)

NOTIFY_CHANNEL = "embedding_queue"
SCAN_INTERVAL_SECS = 60.0
MAX_CONCURRENT = 4
MAX_ATTEMPTS = 5  # rows beyond this are surfaced via mcp_admin but not retried

# Exact mirror of `notify_missing_embedding` TG_TABLE_NAME branches.
INDEXABLE_TABLES: frozenset[str] = frozenset({
    "lessons",
    "tools_catalog",
    "projects_indexed",
    "conversations_indexed",
    "patterns",
    "decisions",
    "gotchas",
    "contacts",
    "ideas",
    "best_practices",
})


# ---------------------------------------------------------------------
# Per-row processing.
# ---------------------------------------------------------------------

async def _process_one(
    pool: AsyncConnectionPool,
    *,
    pending_id: str,
    target_table: str,
    target_id: str,
    source_text: str,
) -> bool:
    """Embed `source_text`, write to target, delete pending row.

    Returns True on success. On failure logs and bumps attempts/last_error
    on the pending row so the operator sees the backlog. Returns False.
    """
    if target_table not in INDEXABLE_TABLES:
        log.warning(
            "pending row %s targets unknown table %r — skipping (operator "
            "must clean up manually or add the table to INDEXABLE_TABLES)",
            pending_id, target_table,
        )
        return False

    try:
        vec = await emb_mod.embed(source_text)
    except Exception as exc:  # defense in depth — embed() already swallows
        log.exception("embed() raised on pending=%s", pending_id)
        await _mark_attempt(pool, pending_id, str(exc))
        return False

    if vec is None:
        await _mark_attempt(pool, pending_id, "embed returned None (api/key/timeout)")
        return False

    literal = vector_literal(vec)
    try:
        async with pool.connection(timeout=10.0) as conn:
            async with conn.cursor() as cur:
                # Atomic: set embedding on target. The BEFORE UPDATE
                # trigger `invalidate_embedding_on_content_change` checks
                # whether content also changed; since we change only
                # `embedding`, content_changed is False and the trigger
                # is a no-op.
                #
                # SQL injection concern: target_table is membership-checked
                # against INDEXABLE_TABLES above, so the f-string is safe.
                await cur.execute(
                    f'UPDATE "{target_table}" SET embedding = %s::vector '
                    f"WHERE id = %s AND embedding IS NULL",
                    (literal, target_id),
                )
                rows = cur.rowcount
                # Always remove the pending row — if rows == 0 the target
                # was already populated (someone else won the race) or
                # deleted; either way the pending row is now stale.
                await cur.execute(
                    "DELETE FROM pending_embeddings WHERE id = %s",
                    (pending_id,),
                )
        if rows == 0:
            log.info(
                "pending=%s already populated (or target deleted); "
                "removed pending row only",
                pending_id,
            )
        else:
            log.info(
                "indexed %s/%s (pending=%s)",
                target_table, target_id, pending_id,
            )
        return True
    except Exception as exc:
        log.exception("UPDATE failed for pending=%s", pending_id)
        await _mark_attempt(pool, pending_id, f"update_failed: {exc}")
        return False


async def _mark_attempt(
    pool: AsyncConnectionPool,
    pending_id: str,
    error: str,
) -> None:
    """Bump attempts + record last_error on a pending row."""
    try:
        async with pool.connection(timeout=5.0) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE pending_embeddings "
                    "SET attempts = attempts + 1, "
                    "    last_error = %s, "
                    "    last_attempt = now() "
                    "WHERE id = %s",
                    (error[:1000], pending_id),
                )
    except Exception:
        log.exception("mark_attempt itself failed for pending=%s", pending_id)


# ---------------------------------------------------------------------
# Batch fetch.
# ---------------------------------------------------------------------

async def _fetch_due_rows(
    pool: AsyncConnectionPool,
    *,
    limit: int = 50,
) -> list[tuple[str, str, str, str]]:
    """Return up to `limit` due pending rows: (id, table, target_id, text).

    Skips rows whose `attempts >= MAX_ATTEMPTS` so a poison-pill row
    doesn't block the queue forever. The operator can manually reset
    attempts via mcp_admin if they want a retry.
    """
    async with pool.connection(timeout=5.0) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, target_table, target_id, source_text "
                "FROM pending_embeddings "
                "WHERE attempts < %s "
                "ORDER BY created_at "
                "LIMIT %s",
                (MAX_ATTEMPTS, limit),
            )
            rows = await cur.fetchall()
    return [(str(r[0]), str(r[1]), str(r[2]), r[3]) for r in rows]


# ---------------------------------------------------------------------
# Drain helper — used both for the initial pass and the periodic scan.
# ---------------------------------------------------------------------

async def _drain_once(
    pool: AsyncConnectionPool,
    *,
    semaphore: asyncio.Semaphore,
) -> int:
    """Process one batch of due pending rows; return count processed.

    Concurrency capped at semaphore size so OpenAI parallelism is bounded
    across both the initial drain and live notifies.
    """
    rows = await _fetch_due_rows(pool)
    if not rows:
        return 0

    async def _gated(r: tuple[str, str, str, str]) -> bool:
        async with semaphore:
            pending_id, table, target_id, text = r
            return await _process_one(
                pool,
                pending_id=pending_id,
                target_table=table,
                target_id=target_id,
                source_text=text,
            )

    results = await asyncio.gather(*(_gated(r) for r in rows), return_exceptions=True)
    succeeded = sum(1 for r in results if r is True)
    log.info("drain pass: %d/%d succeeded", succeeded, len(rows))
    return len(rows)


# ---------------------------------------------------------------------
# Top-level loop.
# ---------------------------------------------------------------------

async def consume_embedding_queue(
    database_url: str,
    *,
    scan_interval_secs: float = SCAN_INTERVAL_SECS,
    max_concurrent: int = MAX_CONCURRENT,
    stop_event: Optional[asyncio.Event] = None,
) -> None:
    """LISTEN on `embedding_queue`, drain pending rows.

    Three coroutines run concurrently:
      • _listen_task: blocks on `conn.notifies()`, sets `wake.set()` on signal.
      • _drain_task: on wake or scan-tick, calls `_drain_once()`.
      • _scan_task: every `scan_interval_secs`, sets `wake.set()`.
    """
    if stop_event is None:
        stop_event = asyncio.Event()
    semaphore = asyncio.Semaphore(max_concurrent)
    wake = asyncio.Event()

    pool_dsn = database_url

    pool = AsyncConnectionPool(
        conninfo=pool_dsn,
        min_size=1,
        max_size=max(2, max_concurrent),
        open=False,
    )
    await pool.open(wait=True)

    async def _listen_task() -> None:
        """Maintain a long-lived LISTEN connection; resilient to drops."""
        backoff = 1.0
        while not stop_event.is_set():
            try:
                async with await psycopg.AsyncConnection.connect(
                    pool_dsn, autocommit=True
                ) as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(f"LISTEN {NOTIFY_CHANNEL}")
                    log.info(
                        "auto_index LISTENing on channel=%s (scan=%.0fs)",
                        NOTIFY_CHANNEL, scan_interval_secs,
                    )
                    backoff = 1.0  # reset after a clean LISTEN
                    while not stop_event.is_set():
                        try:
                            gen = conn.notifies(timeout=1.0)
                            async for notify in gen:
                                if notify.channel == NOTIFY_CHANNEL:
                                    log.debug("notify received: %s", notify.payload)
                                    wake.set()
                        except psycopg.Error:
                            # connection-level error → break inner loop
                            # to reconnect.
                            log.exception("LISTEN connection error")
                            break
            except Exception:
                log.exception("LISTEN setup failed (will retry)")
            if stop_event.is_set():
                return
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30.0)

    async def _scan_task() -> None:
        """Force a wake-up every scan_interval_secs as a safety net."""
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=scan_interval_secs)
                return  # stop_event fired
            except asyncio.TimeoutError:
                wake.set()

    async def _drain_task() -> None:
        """On wake, drain until empty; clear wake; loop."""
        # Initial drain on startup — clears the backlog.
        try:
            n = await _drain_once(pool, semaphore=semaphore)
            if n > 0:
                log.info("initial drain processed %d rows", n)
        except Exception:
            log.exception("initial drain failed")

        while not stop_event.is_set():
            try:
                await asyncio.wait_for(wake.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            wake.clear()
            # Drain in batches until empty so a burst of NOTIFYs collapses
            # into a single sweep.
            while not stop_event.is_set():
                try:
                    n = await _drain_once(pool, semaphore=semaphore)
                except Exception:
                    log.exception("drain pass failed")
                    break
                if n == 0:
                    break

    listen_task = asyncio.create_task(_listen_task(), name="listen")
    scan_task = asyncio.create_task(_scan_task(), name="scan")
    drain_task = asyncio.create_task(_drain_task(), name="drain")

    try:
        await stop_event.wait()
    finally:
        log.info("auto_index stopping")
        for t in (listen_task, scan_task, drain_task):
            t.cancel()
        await asyncio.gather(
            listen_task, scan_task, drain_task, return_exceptions=True
        )
        await pool.close()
        log.info("auto_index stopped")


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
            pass

    log.info("auto_index started")
    await consume_embedding_queue(cfg.database_url, stop_event=stop_event)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        asyncio.run(_main_async())
    except KeyboardInterrupt:
        log.info("auto_index interrupted")


if __name__ == "__main__":
    main()
