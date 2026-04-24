#!/usr/bin/env python3
"""Post-migration health check for the pretel-os data layer.

Verifies that the schema landed as DATA_MODEL.md describes:
- All 21 canonical tables exist
- Extensions vector / pg_trgm / btree_gin are installed
- Every named function exists
- Every named trigger is wired
- control_registry is seeded with the 6 expected controls
- Each partitioned log table has partitions for the current and next month

Exit code is non-zero if any check fails.
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import date

EXPECTED_TABLES = [
    "lessons",
    "tools_catalog",
    "projects_indexed",
    "project_state",
    "project_versions",
    "skill_versions",
    "conversations_indexed",
    "conversation_sessions",
    "cross_pollination_queue",
    "routing_logs",
    "usage_logs",
    "llm_calls",
    "pending_embeddings",
    "reflection_pending",
    "scout_denylist",
    "control_registry",
    "patterns",
    "decisions",
    "gotchas",
    "contacts",
    "ideas",
]

EXPECTED_EXTENSIONS = ["vector", "pg_trgm", "btree_gin"]

EXPECTED_FUNCTIONS = [
    "set_updated_at",
    "notify_missing_embedding",
    "find_duplicate_lesson",
    "recompute_utility_scores",
    "archive_low_utility_lessons",
    "summarize_old_conversation",
    "scout_safety_check",
    "archive_dormant_tools",
]

EXPECTED_TRIGGERS = [
    # updated_at
    "trg_lessons_updated_at",
    "trg_tools_updated_at",
    "trg_projects_updated_at",
    "trg_state_updated_at",
    "trg_patterns_updated_at",
    "trg_contacts_updated_at",
    # embeddings
    "trg_lessons_emb",
    "trg_tools_emb",
    "trg_projects_emb",
    "trg_conv_emb",
    "trg_patterns_emb",
    "trg_decisions_emb",
    "trg_gotchas_emb",
    "trg_contacts_emb",
    "trg_ideas_emb",
    # scout safety
    "trg_scout_safety_lessons",
]

EXPECTED_CONTROL_NAMES = [
    "scout_audit",
    "restore_drill",
    "key_rotation_anthropic",
    "key_rotation_openai",
    "pricing_verification",
    "uptime_review",
]

PARTITIONED_TABLES = ["routing_logs", "usage_logs", "llm_calls"]


def psql(database_url: str, sql: str) -> list[str]:
    proc = subprocess.run(
        ["psql", "-X", "-A", "-t", "-d", database_url, "-c", sql],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"psql failed: {proc.stderr.strip()}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def check(label: str, ok: bool, detail: str = "") -> bool:
    mark = "OK  " if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"[{mark}] {label}{suffix}")
    return ok


def month_partition_name(table: str, d: date) -> str:
    return f"{table}_{d.year:04d}_{d.month:02d}"


def expected_partitions() -> list[str]:
    today = date.today()
    cur = date(today.year, today.month, 1)
    if cur.month == 12:
        nxt = date(cur.year + 1, 1, 1)
    else:
        nxt = date(cur.year, cur.month + 1, 1)
    out = []
    for tbl in PARTITIONED_TABLES:
        out.append(month_partition_name(tbl, cur))
        out.append(month_partition_name(tbl, nxt))
    return out


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set. Source ~/.env.pretel_os first.", file=sys.stderr)
        return 2

    all_ok = True

    # Tables
    rows = psql(
        database_url,
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename",
    )
    present = set(rows)
    for t in EXPECTED_TABLES:
        all_ok &= check(f"table {t}", t in present)

    # Extensions
    rows = psql(database_url, "SELECT extname FROM pg_extension ORDER BY extname")
    present_ext = set(rows)
    for ext in EXPECTED_EXTENSIONS:
        all_ok &= check(f"extension {ext}", ext in present_ext)

    # Functions
    rows = psql(
        database_url,
        "SELECT proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace "
        "WHERE n.nspname='public' ORDER BY proname",
    )
    present_fns = set(rows)
    for fn in EXPECTED_FUNCTIONS:
        all_ok &= check(f"function {fn}", fn in present_fns)

    # Triggers
    rows = psql(
        database_url,
        "SELECT tgname FROM pg_trigger WHERE NOT tgisinternal ORDER BY tgname",
    )
    present_trg = set(rows)
    for trg in EXPECTED_TRIGGERS:
        all_ok &= check(f"trigger {trg}", trg in present_trg)

    # control_registry seed
    rows = psql(database_url, "SELECT control_name FROM control_registry ORDER BY control_name")
    present_controls = set(rows)
    for name in EXPECTED_CONTROL_NAMES:
        all_ok &= check(f"control_registry seed {name}", name in present_controls)
    all_ok &= check(
        "control_registry row count",
        len(present_controls) == 6,
        detail=f"found {len(present_controls)}",
    )

    # Partitions for current + next month
    rows = psql(
        database_url,
        "SELECT c.relname FROM pg_inherits i "
        "JOIN pg_class c ON c.oid = i.inhrelid "
        "JOIN pg_class p ON p.oid = i.inhparent "
        "WHERE p.relname IN ('routing_logs','usage_logs','llm_calls') "
        "ORDER BY c.relname",
    )
    present_parts = set(rows)
    for part in expected_partitions():
        all_ok &= check(f"partition {part}", part in present_parts)

    print()
    if all_ok:
        print("All checks passed.")
        return 0
    print("One or more checks failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
