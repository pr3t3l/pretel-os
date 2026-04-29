"""Bootstrap tools_catalog with the MCP tools registered in mcp_server.main.

INTERIM SOLUTION — Module 4 will replace this. The original plan, per the
comment in migrations/0022_seed_tools_catalog.sql, was for Module 4 to
populate the catalog as part of its tool/skill inventory work. This script
exists because the catalog was empty in production and `tool_search` was
returning [] for every query, blocking discovery from MCP clients before
M4 ships. When M4 implements its canonical seed (likely a startup hook in
main.py or a dedicated migration), delete this script and the
`bootstrap_tools_catalog_interim` task should be closed.

Design notes:

- **Names are introspected**, not hardcoded. We call `build_app()` (a safe
  factory — no I/O beyond config + log, no server start) and then
  `app.list_tools()` to get the FastMCP-registered tool list. This makes
  the script auto-detect when `main.py` adds or removes a tool — see the
  drift warnings printed at the start of every run.

- **Short descriptions are curated** (DESCRIPTIONS_SHORT below) because
  first-line-of-docstring would often exceed the 80-char L0 budget or
  read awkwardly. When you add a tool to main.py, add an entry here too;
  the script will warn about missing entries and skip those tools rather
  than fail.

- **Full descriptions come from each function's docstring** — same source
  the FastMCP runtime uses for its tool description. Single source of
  truth for the long-form text.

- **Idempotent.** `register_tool` issues `INSERT ... ON CONFLICT (name)
  DO UPDATE`, so re-running refreshes metadata in place. Embeddings are
  refreshed only when OpenAI returns a new vector (COALESCE preserves
  the existing one if embed() fails).

Usage:
    PYTHONPATH=src python3 scripts/bootstrap_tools_catalog.py

Exits non-zero if any registration fails (so CI / Make targets can
catch it). Prints drift warnings to stderr but does not exit on those.
"""
from __future__ import annotations

import asyncio
import inspect
import sys
from typing import Any

from mcp_server import db as db_mod
from mcp_server.main import build_app
from mcp_server.tools.catalog import register_tool


# applicable_buckets — universal: every knowledge tool applies in any workspace.
# Module 4 may refine to per-tool granularity (e.g., gotcha_search → ['business']).
UNIVERSAL_BUCKETS: list[str] = ["business", "personal", "scout"]


# Curated short descriptions (<=80 chars). Used for L0 surface where space matters.
# When you add a new app.tool() in main.py, add an entry here. Missing entries
# trigger a drift warning; the tool is skipped rather than registered with a
# generic auto-truncated docstring.
DESCRIPTIONS_SHORT: dict[str, str] = {
    "get_context":              "Retrieve project context (lessons, decisions, preferences, best_practices)",
    "save_lesson":              "Save a lesson learned with auto-approval and dedup",
    "search_lessons":           "Semantic search across lessons (HNSW)",
    "register_skill":           "Register a methodology skill in tools_catalog",
    "register_tool":            "Register an executable tool in tools_catalog",
    "load_skill":               "Load full skill content (L3) by name",
    "tool_search":              "Fuzzy catalog search by name/description (trigram)",
    "preference_set":           "Set or update an operator preference",
    "preference_get":           "Get an operator preference by key",
    "preference_list":          "List operator preferences with filters",
    "preference_unset":         "Remove an operator preference",
    "task_create":              "Create a task in the tracker",
    "task_list":                "List tasks with filters (status, bucket, priority)",
    "task_update":              "Update task fields (status, priority, blocked_by)",
    "task_close":               "Close a task with completion note",
    "task_reopen":              "Reopen a previously-closed task with reason",
    "router_feedback_record":   "Record router routing feedback for analysis",
    "router_feedback_review":   "Review aggregated router feedback",
    "decision_record":          "Record an architectural decision (ADR-style)",
    "decision_search":          "Semantic search across recorded decisions",
    "decision_supersede":       "Mark a decision superseded by another",
    "best_practice_record":     "Record/update a process best-practice with rollback",
    "best_practice_search":     "Semantic search across active best_practices",
    "best_practice_deactivate": "Soft-delete a best_practice (active=false)",
    "best_practice_rollback":   "Restore previous_guidance on a best_practice",
}


async def _discover_tools() -> list[tuple[str, Any]]:
    """Return [(name, fn), ...] for every tool currently registered in main.py.

    Uses FastMCP's public list_tools() API. The fn attribute is the original
    Python coroutine that app.tool() wrapped — its __doc__ is the source of
    the description_full we register.
    """
    app = build_app()
    tools = await app.list_tools()
    return [(t.name, t.fn) for t in tools]


def _check_drift(discovered_names: list[str]) -> None:
    """Warn about mismatches between main.py registrations and DESCRIPTIONS_SHORT."""
    discovered = set(discovered_names)
    curated = set(DESCRIPTIONS_SHORT)

    missing = discovered - curated      # registered in main.py, no short here
    orphaned = curated - discovered     # short here, no longer registered

    if missing:
        print(
            f"WARN: tools registered in main.py but missing from DESCRIPTIONS_SHORT "
            f"(will be skipped — add a short description for each): "
            f"{sorted(missing)}",
            file=sys.stderr,
        )
    if orphaned:
        print(
            f"WARN: DESCRIPTIONS_SHORT has entries no longer registered in main.py "
            f"(consider removing or running deprecation): {sorted(orphaned)}",
            file=sys.stderr,
        )


async def main() -> int:
    discovered = await _discover_tools()
    _check_drift([n for n, _ in discovered])

    # Bring the DB health poller up so register_tool's degraded-mode check passes.
    await db_mod.start_background_health_check()
    await asyncio.sleep(2)

    ok = 0
    skipped = 0
    failed: list[tuple[str, str]] = []

    for name, fn in discovered:
        if name not in DESCRIPTIONS_SHORT:
            skipped += 1
            print(f"  SKIP {name} (no DESCRIPTIONS_SHORT entry)")
            continue

        short = DESCRIPTIONS_SHORT[name]
        full = inspect.getdoc(fn) or short

        result = await register_tool(
            name=name,
            description_short=short,
            description_full=full,
            applicable_buckets=UNIVERSAL_BUCKETS,
            mcp_tool_name=name,
        )
        if result.get("status") == "registered":
            ok += 1
            queued = " (embedding queued)" if result.get("embedding_queued") else ""
            print(f"  OK   {name:30s} id={result['id']}{queued}")
        else:
            failed.append((name, str(result)))
            print(f"  FAIL {name:30s} {result}")

    await db_mod.stop_background_health_check()

    total = len(discovered)
    print(f"\nregistered={ok}/{total}  skipped={skipped}  failed={len(failed)}")
    if failed:
        for name, msg in failed:
            print(f"  - {name}: {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
