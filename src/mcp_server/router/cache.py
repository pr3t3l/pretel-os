"""LayerBundle cache + LISTEN/NOTIFY invalidation (Phase B B.8).

In-memory dict cache keyed by `(bucket, project, classifier_hash)` with
thread-safe access via threading.Lock. A daemon background thread runs
LISTEN on the 'layer_loader_cache' channel (per migration 0031); on
each notification the cache is fully cleared.

Per Q2 decision (specs/router/phase_b_close.md §1): one shared
NOTIFY channel feeds all four contract §6 tables; the cache treats
ALL payloads as "clear all" — fine-grained invalidation by
(bucket, project) is a future optimization once telemetry shows we
need it. At expected scale (single operator, ~5K rows per table)
clearing the cache on every write is cheap.

Caller-managed connections: the listener owns ITS OWN psycopg
connection (autocommit=True for LISTEN to deliver notifications
without an open tx). The cache get/put paths do NOT touch the DB.

The cache is process-lifetime by default. The MCP server lifespan
hook should construct one LayerBundleCache + start_listener() at
startup and stop_listener() on shutdown.
"""
from __future__ import annotations

import logging
import threading
from typing import Optional

import psycopg

from mcp_server.router.types import LayerBundle


log = logging.getLogger(__name__)

NOTIFY_CHANNEL = "layer_loader_cache"


CacheKey = tuple[Optional[str], Optional[str], str]


class LayerBundleCache:
    """Thread-safe in-memory cache for assembled LayerBundles.

    Key: (bucket, project, classifier_hash). The classifier_hash
    captures classifier signals; bucket/project are kept in the key
    explicitly so the cache map matches the spec's wording in
    layer_loader_contract.md §6.
    """

    def __init__(self, max_entries: int = 256) -> None:
        self._cache: dict[CacheKey, LayerBundle] = {}
        self._lock = threading.Lock()
        self._max_entries = max_entries
        self._listener_thread: threading.Thread | None = None
        self._listener_stop = threading.Event()
        self._listener_conn: psycopg.Connection | None = None

    # ------------------------------------------------------------------
    # Synchronous get/put — hot path, no I/O.
    # ------------------------------------------------------------------

    def get(self, key: CacheKey) -> LayerBundle | None:
        with self._lock:
            return self._cache.get(key)

    def put(self, key: CacheKey, bundle: LayerBundle) -> None:
        with self._lock:
            # Cheap eviction when over cap: drop oldest insertion via
            # rebuild. Python 3.7+ dict preserves insertion order, so
            # `next(iter(...))` gives the oldest key.
            if len(self._cache) >= self._max_entries and key not in self._cache:
                oldest = next(iter(self._cache))
                self._cache.pop(oldest, None)
            self._cache[key] = bundle

    def invalidate_all(self) -> None:
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    # ------------------------------------------------------------------
    # LISTEN/NOTIFY background thread.
    # ------------------------------------------------------------------

    def start_listener(self, conninfo: str) -> None:
        """Launch a daemon thread that listens on the NOTIFY channel.

        Args:
            conninfo: psycopg connection string. The listener opens its
                OWN connection (separate from any caller's connection
                pool) and keeps it autocommit=True so notifications
                deliver without an open transaction.
        """
        if self._listener_thread is not None and self._listener_thread.is_alive():
            log.warning("listener already running; ignoring start_listener call")
            return

        self._listener_stop.clear()
        self._listener_conn = psycopg.connect(conninfo, autocommit=True)
        with self._listener_conn.cursor() as cur:
            cur.execute(f"LISTEN {NOTIFY_CHANNEL}")

        thread = threading.Thread(
            target=self._listener_loop,
            name=f"layer-cache-listener-{NOTIFY_CHANNEL}",
            daemon=True,
        )
        thread.start()
        self._listener_thread = thread

    def stop_listener(self, timeout: float = 2.0) -> None:
        """Signal the listener to exit and wait briefly for it to do so."""
        self._listener_stop.set()
        if self._listener_conn is not None:
            try:
                self._listener_conn.close()
            except Exception:
                pass
            self._listener_conn = None
        if self._listener_thread is not None:
            self._listener_thread.join(timeout=timeout)
            self._listener_thread = None

    def _listener_loop(self) -> None:
        """Drain notifications; clear cache on each."""
        assert self._listener_conn is not None
        conn = self._listener_conn
        log.info("layer-cache listener started on channel=%s", NOTIFY_CHANNEL)
        try:
            while not self._listener_stop.is_set():
                # psycopg3: conn.notifies() yields psycopg.Notify objects;
                # with timeout it returns control so we can re-check the
                # stop flag.
                gen = conn.notifies(timeout=1.0, stop_after=1)
                got_any = False
                for _notify in gen:
                    got_any = True
                    self.invalidate_all()
                    log.debug("cache invalidated by NOTIFY %s", _notify.payload)
                # If gen exited without yielding, the timeout fired —
                # loop and re-check stop flag.
                if not got_any:
                    continue
        except psycopg.Error as exc:
            # Connection lost; exit thread. Caller can call
            # start_listener again to recover.
            log.warning("layer-cache listener stopped on psycopg error: %s", exc)
        except Exception:
            log.exception("layer-cache listener crashed")
        finally:
            log.info("layer-cache listener exited")
