"""Migrate ~203 lessons from openclaw-config (LL-MASTER + LL-FORGE +
LL-COPILOT-STUDIO YAML and workspace/cases/config/lessons_learned.json)
into the pretel-os `lessons` table via the `save_lesson` MCP tool.

Bucket policy is knowledge-driven (not source-file-driven): everything
defaults to `business` since the lessons encode productizable platform
patterns. Copilot Studio lessons cross-apply to scout via
`applicable_buckets`. See plan at .claude/plans/glimmering-squishing-hummingbird.md.

Why a script (not a SQL bulk insert):
- save_lesson generates the embedding via OpenAI and runs the dedup
  detector at >=0.92 similarity per CONSTITUTION 5.2 rule 14.
- save_lesson auto-routes to pending_review unless every auto-approval
  criterion is met (CONSTITUTION 5.2 rule 13).
- save_lesson honors the scout-safety DB trigger and the degraded-mode
  fallback journal.

Re-runnable: dedup at >=0.92 prevents double-insert. To re-map fields and
re-run, archive the existing migration first:
  UPDATE lessons SET status='archived'
  WHERE tags @> ARRAY['migration:openclaw'];

Usage (Phase 1 dry-run -> Phase 2 test DB -> Phase 3 prod):
    PYTHONPATH=src python scripts/migrate_openclaw_lessons.py \
        --source-dir /home/pretel/openclaw-config \
        --source all --dry-run

    PYTHONPATH=src python scripts/migrate_openclaw_lessons.py \
        --source-dir /home/pretel/openclaw-config \
        --source master --test-db --limit 10

    PYTHONPATH=src python scripts/migrate_openclaw_lessons.py \
        --source-dir /home/pretel/openclaw-config \
        --source all --concurrency 5
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from openclaw_taxonomy import (  # noqa: E402
    OpenclawLesson,
    SOURCE_FILES,
    build_save_lesson_kwargs,
    collect_lessons,
)

DEFAULT_AUDIT_DIR = Path("/home/pretel/pretel-os-data/migrations")


def _resolve_sources(arg: str) -> list[str]:
    if arg == "all":
        return list(SOURCE_FILES.keys())
    requested = [s.strip() for s in arg.split(",") if s.strip()]
    unknown = [s for s in requested if s not in SOURCE_FILES]
    if unknown:
        raise SystemExit(f"Unknown --source values: {unknown}. Allowed: {list(SOURCE_FILES)} or 'all'")
    return requested


def _open_audit_log(audit_dir: Path) -> Path:
    audit_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return audit_dir / f"openclaw-{stamp}.jsonl"


def _audit_record(
    audit_path: Path,
    *,
    lesson: OpenclawLesson,
    payload: dict[str, Any],
    response: dict[str, Any] | None,
    error: str | None,
) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source_file": lesson.source_file,
        "source_id": lesson.source_id,
        "title": lesson.title,
        "bucket": lesson.bucket,
        "category": lesson.category,
        "tags": lesson.tags,
        "needs_review": lesson.needs_review,
        "payload": payload,
        "response": response,
        "error": error,
    }
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


async def _save_one(
    save_lesson: Any,
    sem: asyncio.Semaphore,
    lesson: OpenclawLesson,
    audit_path: Path,
) -> dict[str, Any]:
    payload = build_save_lesson_kwargs(lesson)
    async with sem:
        try:
            response = await save_lesson(**payload)
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}"
            _audit_record(audit_path, lesson=lesson, payload=payload, response=None, error=err)
            return {"status": "error", "error": err, "source_id": lesson.source_id}
    _audit_record(audit_path, lesson=lesson, payload=payload, response=response, error=None)
    response = dict(response) if isinstance(response, dict) else {"status": "unknown", "raw": response}
    response["source_id"] = lesson.source_id
    return response


def _print_dry_run(lessons: list[OpenclawLesson], limit: int | None) -> None:
    sliced = lessons if limit is None else lessons[:limit]
    print(f"\nDry-run: showing {len(sliced)} of {len(lessons)} lessons\n")
    by_source: dict[str, int] = {}
    by_bucket: dict[str, int] = {}
    by_category: dict[str, int] = {}
    needs_review = 0
    for l in lessons:
        by_source[l.source_file] = by_source.get(l.source_file, 0) + 1
        by_bucket[l.bucket] = by_bucket.get(l.bucket, 0) + 1
        by_category[l.category] = by_category.get(l.category, 0) + 1
        if l.needs_review:
            needs_review += 1

    print("Counts by source file:")
    for k, v in sorted(by_source.items()):
        print(f"  {k}: {v}")
    print("\nCounts by bucket:")
    for k, v in sorted(by_bucket.items()):
        print(f"  {k}: {v}")
    print("\nCounts by category:")
    for k, v in sorted(by_category.items()):
        print(f"  {k}: {v}")
    print(f"\nNeeds-review (severity unknown OR draft OR no next_time): {needs_review}")
    print(f"Auto-approval-eligible (has next_time + severity set): {len(lessons) - needs_review}")
    print()
    for l in sliced:
        flags = []
        if l.needs_review:
            flags.append("needs-review")
        if l.applicable_buckets:
            flags.append(f"applicable_buckets={l.applicable_buckets}")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  {l.source_id} ({l.source_file}) bucket={l.bucket} category={l.category} severity={l.severity}{flag_str}")
        print(f"    title: {l.title}")
        print(f"    tags ({len(l.tags)}): {l.tags}")
        if l.next_time:
            preview = l.next_time[:120].replace("\n", " ")
            print(f"    next_time: {preview}{'...' if len(l.next_time) > 120 else ''}")
        else:
            print("    next_time: <none — will land in pending_review>")
        content_preview = l.content[:240].replace("\n", " ")
        print(f"    content: {content_preview}{'...' if len(l.content) > 240 else ''}")
        print()


async def _run_real(
    lessons: list[OpenclawLesson],
    *,
    use_test_db: bool,
    concurrency: int,
    audit_path: Path,
) -> int:
    if use_test_db:
        from dataclasses import replace as dc_replace

        from mcp_server import config as cfg_mod

        original = cfg_mod.load_config

        def _override() -> Any:
            return dc_replace(
                original(),
                database_url="postgresql://pretel_os@localhost/pretel_os_test",
            )

        cfg_mod.load_config = _override  # type: ignore[assignment]

    from mcp_server import db as db_mod

    pool = db_mod.get_pool()
    await pool.open(wait=True)
    await db_mod.start_background_health_check()
    for _ in range(20):
        if db_mod.is_healthy():
            break
        await asyncio.sleep(0.5)
    if not db_mod.is_healthy():
        print("ERROR: db_mod.is_healthy() never became True", file=sys.stderr)
        return 1

    from mcp_server.tools.lessons import save_lesson

    sem = asyncio.Semaphore(concurrency)

    print(f"Starting migration of {len(lessons)} lessons (concurrency={concurrency})")
    print(f"Audit log: {audit_path}\n")

    tasks = [asyncio.create_task(_save_one(save_lesson, sem, l, audit_path)) for l in lessons]
    results: list[dict[str, Any]] = []
    for fut in asyncio.as_completed(tasks):
        r = await fut
        results.append(r)
        sid = r.get("source_id", "?")
        status = r.get("status")
        if status == "saved":
            kind = "active" if r.get("auto_approved") else "pending_review"
            print(f"  ok  {sid} -> {r.get('id')} ({kind})")
        elif status == "merge_candidate":
            cands = r.get("candidates") or []
            top = cands[0] if cands else {}
            sim = top.get("similarity")
            sim_s = f"{sim:.3f}" if isinstance(sim, (int, float)) else str(sim)
            print(f"  dup {sid} -> matches {top.get('id')} (sim {sim_s})")
        elif status == "degraded":
            print(f"  degraded {sid} -> journal_id={r.get('journal_id')}")
        elif status == "error":
            print(f"  ERR {sid} -> {r.get('error')}")
        else:
            print(f"  ??? {sid} -> {r}")

    counts = {"active": 0, "pending_review": 0, "merge_candidate": 0, "degraded": 0, "error": 0, "other": 0}
    for r in results:
        st = r.get("status")
        if st == "saved":
            counts["active" if r.get("auto_approved") else "pending_review"] += 1
        elif st == "merge_candidate":
            counts["merge_candidate"] += 1
        elif st == "degraded":
            counts["degraded"] += 1
        elif st == "error":
            counts["error"] += 1
        else:
            counts["other"] += 1

    print("\n=== Summary ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"\nFull audit: {audit_path}")
    return 0 if counts["error"] == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("/home/pretel/openclaw-config"),
        help="Root of the cloned openclaw-config repo",
    )
    parser.add_argument(
        "--source",
        default="all",
        help="Comma-separated subset: master,forge,copilot,cases or 'all'",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse + summarize only, no MCP calls")
    parser.add_argument("--test-db", action="store_true", help="Use pretel_os_test instead of pretel_os")
    parser.add_argument("--limit", type=int, default=None, help="Cap entries processed (testing)")
    parser.add_argument("--concurrency", type=int, default=5, help="Parallel save_lesson calls")
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=DEFAULT_AUDIT_DIR,
        help=f"Where to write JSONL audit logs (default: {DEFAULT_AUDIT_DIR})",
    )
    args = parser.parse_args()

    sources = _resolve_sources(args.source)

    if not args.source_dir.exists():
        print(f"ERROR: --source-dir {args.source_dir} does not exist", file=sys.stderr)
        return 2

    print(f"Reading from {args.source_dir} (sources: {sources})")
    lessons = collect_lessons(args.source_dir, sources=sources)
    print(f"Parsed {len(lessons)} lessons total")

    if args.limit is not None:
        lessons = lessons[: args.limit]
        print(f"--limit {args.limit} applied -> {len(lessons)} lessons to process")

    if args.dry_run:
        _print_dry_run(lessons, limit=args.limit if args.limit else 20)
        return 0

    audit_path = _open_audit_log(args.audit_dir)
    return asyncio.run(
        _run_real(
            lessons,
            use_test_db=args.test_db,
            concurrency=max(1, args.concurrency),
            audit_path=audit_path,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
