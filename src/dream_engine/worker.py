"""Dream Engine nightly worker — main entry point.

Invocation:
    python -m dream_engine.worker [--dry-run]

  --dry-run: open a transaction per job, run the SQL, then ROLLBACK
             instead of COMMIT. Telemetry rows are still inserted so the
             operator sees what would have been done.

Three jobs run sequentially. Each in its own transaction so one failure
does not roll back the others. Status state machine:

  Worker starts                          → INSERT dream_engine_runs(running)
  All 3 jobs succeed                     → UPDATE status='success'
  >= 1 job raises, but worker survives   → UPDATE status='partial'
  Worker itself crashes (uncaught)       → row stays at 'running' until
                                           operator queries; the next run
                                           does not depend on prior state.

Exit codes:
  0 — full success or partial-success (telemetry recorded)
  1 — fatal error before any job ran (config load failure, DB unreachable)

The systemd unit checks exit codes for alerting.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass, field
from typing import Any

import psycopg

from mcp_server import config as config_mod

from . import queries as Q
from .config import ArchiveThresholds, load_archive_thresholds

log = logging.getLogger("dream_engine")


# ---------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------

@dataclass
class JobResult:
    name: str
    duration_ms: int
    rows_affected: int
    error: str | None = None
    error_class: str | None = None
    traceback: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error is None

    def to_telemetry(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "duration_ms": self.duration_ms,
            "rows_affected": self.rows_affected,
        }
        if self.error is not None:
            out["error"] = self.error
            out["error_class"] = self.error_class
        return out

    def to_failure_record(self) -> dict[str, Any]:
        return {
            "job": self.name,
            "error_class": self.error_class,
            "error_message": self.error,
            "traceback": self.traceback,
        }


# ---------------------------------------------------------------------
# Job runners
# ---------------------------------------------------------------------

def _time_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


def _safe(name: str, fn: Any) -> JobResult:
    """Wrap a job function, catching any exception into a JobResult."""
    start = time.monotonic()
    try:
        rows_affected = fn()
        return JobResult(name=name, duration_ms=_time_ms(start), rows_affected=rows_affected)
    except Exception as exc:
        log.exception("Dream Engine job %s failed", name)
        return JobResult(
            name=name,
            duration_ms=_time_ms(start),
            rows_affected=0,
            error=str(exc),
            error_class=type(exc).__name__,
            traceback=traceback.format_exc(),
        )


def utility_recompute(conn: psycopg.Connection, *, dry_run: bool) -> int:
    """Job 1: recompute utility_score on tools_catalog and lessons.

    Returns the total number of rows whose score was potentially updated
    (active lessons + non-deprecated tools_catalog rows). The SQL
    function returns void, so we read counts before/after via a separate
    query — for fase 1 we just report the affected universe size.
    """
    with conn.cursor() as cur:
        cur.execute(Q.UTILITY_RECOMPUTE)
        cur.execute(Q.UTILITY_AFFECTED_COUNTS)
        row = cur.fetchone()
        affected = (int(row[0]) if row else 0) + (int(row[1]) if row else 0)
    if dry_run:
        conn.rollback()
    else:
        conn.commit()
    return affected


def dedup_pass(conn: psycopg.Connection, *, dry_run: bool) -> int:
    """Job 2: write merge-candidate rows to cross_pollination_queue.

    Idempotent — second run inserts zero rows for the same pairs via
    UNIQUE constraint + ON CONFLICT DO NOTHING.
    """
    with conn.cursor() as cur:
        cur.execute(
            Q.DEDUP_INSERT_CANDIDATES,
            {
                "distance_threshold": Q.DEDUP_DISTANCE_THRESHOLD,
                "top_k": Q.DEDUP_TOP_K,
            },
        )
        rows = cur.fetchall()
        affected = len(rows)
    if dry_run:
        conn.rollback()
    else:
        conn.commit()
    return affected


def archive_low_utility(
    conn: psycopg.Connection, thresholds: ArchiveThresholds, *, dry_run: bool
) -> int:
    """Job 3: flip status='archived' on stale low-utility lessons."""
    with conn.cursor() as cur:
        cur.execute(
            Q.ARCHIVE_LOW_UTILITY,
            {
                "utility_threshold": thresholds.utility_threshold,
                "window_days": thresholds.usage_window_days,
            },
        )
        rows = cur.fetchall()
        affected = len(rows)
    if dry_run:
        conn.rollback()
    else:
        conn.commit()
    return affected


# ---------------------------------------------------------------------
# Telemetry helpers
# ---------------------------------------------------------------------

def _start_run(conn: psycopg.Connection) -> str:
    with conn.cursor() as cur:
        cur.execute(Q.INSERT_RUN_START, {"worker_pid": os.getpid()})
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Failed to insert dream_engine_runs row")
        run_id = str(row[0])
    conn.commit()
    return run_id


def _finish_run(
    conn: psycopg.Connection,
    run_id: str,
    results: list[JobResult],
) -> str:
    """Compute final status from JobResult list and update telemetry row."""
    failed = [r for r in results if not r.succeeded]
    if not failed:
        status = "success"
    elif len(failed) < len(results):
        status = "partial"
    else:
        status = "failed"

    jobs_run = {r.name: r.to_telemetry() for r in results}
    failures = [r.to_failure_record() for r in failed]

    with conn.cursor() as cur:
        cur.execute(
            Q.UPDATE_RUN_FINISH,
            {
                "run_id": run_id,
                "status": status,
                "jobs_run": json.dumps(jobs_run),
                "failures": json.dumps(failures),
            },
        )
    conn.commit()
    return status


# ---------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------

def main(*, dry_run: bool = False) -> int:
    """Run the 3 jobs sequentially. Returns process exit code (0 on
    success or partial; 1 on fatal pre-job error)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    )

    log.info("Dream Engine starting (dry_run=%s, pid=%d)", dry_run, os.getpid())

    try:
        cfg = config_mod.load_config()
    except Exception:
        log.exception("Failed to load config — cannot connect to DB")
        return 1

    try:
        conn = psycopg.connect(cfg.database_url, autocommit=False)
    except Exception:
        log.exception("Failed to open database connection")
        return 1

    try:
        run_id = _start_run(conn)
        log.info("Dream Engine run_id=%s", run_id)

        thresholds = load_archive_thresholds(conn)
        log.info(
            "Archive thresholds: window_days=%d, utility_threshold=%.3f, lookback_days=%d",
            thresholds.usage_window_days,
            thresholds.utility_threshold,
            thresholds.utility_lookback_days,
        )

        results = [
            _safe("utility_recompute",   lambda: utility_recompute(conn, dry_run=dry_run)),
            _safe("dedup_pass",          lambda: dedup_pass(conn, dry_run=dry_run)),
            _safe("archive_low_utility", lambda: archive_low_utility(conn, thresholds, dry_run=dry_run)),
        ]

        status = _finish_run(conn, run_id, results)

        for r in results:
            if r.succeeded:
                log.info(
                    "  %-22s OK  rows=%-6d duration=%dms",
                    r.name, r.rows_affected, r.duration_ms,
                )
            else:
                log.error(
                    "  %-22s FAIL %s: %s (duration=%dms)",
                    r.name, r.error_class, r.error, r.duration_ms,
                )

        log.info("Dream Engine finished status=%s%s", status, " (dry-run, all changes rolled back)" if dry_run else "")
        return 0
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _cli() -> None:
    parser = argparse.ArgumentParser(prog="dream_engine.worker")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run all jobs but ROLLBACK each transaction instead of COMMIT. "
             "Telemetry rows are still recorded so the operator sees what "
             "would have happened.",
    )
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))


if __name__ == "__main__":
    _cli()
