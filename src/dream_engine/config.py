"""Configuration loaders for Dream Engine.

Archive thresholds live in `operator_preferences` (seeded by migration 0039
with defaults 500 / 0.5 / 90 per CONSTITUTION §5.5 rule 22 v5.2). The
worker reads them at run time and HARD-FAILS on any missing key — there
is no hardcoded fallback per spec §7 risk row.

The thresholds are read once per worker invocation (not once per job)
because the values do not change mid-run; if the operator runs
`preference_set` while the worker is executing, the new value applies on
the next nightly run, not the in-flight one.
"""
from __future__ import annotations

from dataclasses import dataclass

import psycopg


@dataclass(frozen=True)
class ArchiveThresholds:
    usage_window_days: int
    utility_threshold: float
    utility_lookback_days: int


_REQUIRED_KEYS = (
    "archive.usage_window_days",
    "archive.utility_threshold",
    "archive.utility_lookback_days",
)


def load_archive_thresholds(conn: psycopg.Connection) -> ArchiveThresholds:
    """Read the 3 archive thresholds from operator_preferences.

    Args:
        conn: open psycopg.Connection (sync).

    Returns:
        ArchiveThresholds.

    Raises:
        RuntimeError: if any of the 3 required keys is missing or inactive.
            The Dream Engine worker must NOT fall back to hardcoded defaults
            per spec §7 risk row + ADR-029 contract.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT key, value
            FROM   operator_preferences
            WHERE  key = ANY(%s)
              AND  scope = 'global'
              AND  active = true
            """,
            (list(_REQUIRED_KEYS),),
        )
        found = {row[0]: row[1] for row in cur.fetchall()}

    missing = set(_REQUIRED_KEYS) - found.keys()
    if missing:
        raise RuntimeError(
            f"Dream Engine archive thresholds missing from operator_preferences: "
            f"{sorted(missing)}. Apply migration 0039 or seed via preference_set. "
            f"No hardcoded fallback by design — see CONSTITUTION §5.5 rule 22 v5.2."
        )

    try:
        return ArchiveThresholds(
            usage_window_days=int(found["archive.usage_window_days"]),
            utility_threshold=float(found["archive.utility_threshold"]),
            utility_lookback_days=int(found["archive.utility_lookback_days"]),
        )
    except (TypeError, ValueError) as exc:
        raise RuntimeError(
            f"Dream Engine archive thresholds malformed in operator_preferences: "
            f"got {found!r}. Expected integer / float / integer."
        ) from exc
