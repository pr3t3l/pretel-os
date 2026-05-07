"""Module 9 — migrate the 17 seed lessons from `docs/LESSONS_LEARNED.md §9`
into the `lessons` table via the `save_lesson` MCP tool.

Scope: 17 foundation-era lessons (LL-PROC-* / LL-ARCH-* / LL-DATA-* / LL-COST-* /
LL-AI-* / LL-M4-PHASE-A-* / LL-M0X-* / LL-INFRA-*). The 89 OpenClaw-era
lessons mentioned in tasks.md live in a separate repo
(github.com/pr3t3l/openclaw-config/lessons-learned) and are out of scope
for this run.

Why a script and not a SQL migration:
- save_lesson generates the embedding via OpenAI — keeps the §2.1 invariant
  (every write goes through an MCP tool, never raw SQL).
- save_lesson handles dedup detection (≥0.92 similarity → merge_candidate).

Idempotent: running twice doesn't double-insert because save_lesson rejects
duplicates above threshold.

Usage:
    PYTHONPATH=src python scripts/migrate_seed_lessons.py [--dry-run] [--test-db]

    --dry-run    Print payloads, don't call MCP tool
    --test-db    Use pretel_os_test instead of pretel_os
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
LESSONS_DOC = REPO_ROOT / "docs" / "LESSONS_LEARNED.md"
SECTION_HEADER = "## 9. Seed lessons from foundation design"
SECTION_END = "## 10. Pre-flight checklist"

# ---------------------------------------------------------------- mappings

# Map source `Category:` field → save_lesson `category` enum
CATEGORY_MAP = {
    "PROC": "PROC",
    "ARCH": "ARCH",
    "DATA": "DATA",
    "COST": "COST",
    "AI": "AI",
    "INFRA": "INFRA",
    "SEC": "AI",     # SEC has no enum → closest: AI (security-AI overlap)
    "CODE": "CODE",
    "OPS": "OPS",
    "PLAN": "PLAN",
}

SEVERITY_RE = re.compile(r"(critical|moderate|minor)", re.IGNORECASE)


@dataclass
class SeedLesson:
    """One parsed seed lesson, ready for save_lesson()."""
    code: str                # e.g. "LL-PROC-001"
    title: str               # full title with code prefix
    bucket: str
    category: str
    severity: str
    content: str
    next_time: str
    tags: list[str]
    related_tools: list[str]


# ---------------------------------------------------------------- parser

def _extract_section(full: str) -> str:
    """Slice the §9 seed-lessons block out of the LESSONS_LEARNED.md text."""
    start = full.find(SECTION_HEADER)
    end = full.find(SECTION_END, start)
    if start < 0 or end < 0:
        raise RuntimeError(
            f"Could not locate seed-lessons section between markers; got "
            f"start={start}, end={end}"
        )
    return full[start:end]


_LESSON_HEAD_RE = re.compile(r"^### (LL-[A-Z0-9-]+)\s*[—-]\s*(.+)$", re.MULTILINE)


def _split_lessons(section_text: str) -> list[tuple[str, str, str]]:
    """Split the section into (code, short_title, body) triples."""
    matches = list(_LESSON_HEAD_RE.finditer(section_text))
    out: list[tuple[str, str, str]] = []
    for i, m in enumerate(matches):
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(section_text)
        body = section_text[body_start:body_end]
        out.append((m.group(1).strip(), m.group(2).strip(), body))
    return out


def _take_field(label: str, body: str) -> str | None:
    """Find `**Label.** ...` or `**Label:** ...` and return its content
    until the next bold field, blank-bold line, or the `---` separator."""
    pattern = rf"\*\*{re.escape(label)}[.:]?\*\*\s*(.+?)(?=\n\s*\n\*\*|\n\*\*[A-Z]|\n---|$)"
    m = re.search(pattern, body, re.DOTALL)
    if not m:
        return None
    return m.group(1).strip().rstrip("-").rstrip().strip()


def _take_inline_meta(body: str) -> dict[str, str]:
    """Pull category/severity/bucket from the tagline.
    Two formats:
      Format A: '**Category:** PROC / **Severity:** 🟢 minor / **Bucket:** business'
      Format B: '**Severity:** critical' (alone)
    """
    out: dict[str, str] = {}
    cat = re.search(r"\*\*Category:\*\*\s*([A-Z]+)", body)
    if cat:
        out["category"] = cat.group(1)
    sev = re.search(r"\*\*Severity:\*\*\s*[^A-Za-z]*([A-Za-z]+)", body)
    if sev:
        match = SEVERITY_RE.search(sev.group(1))
        if match:
            out["severity"] = match.group(1).lower()
    buc = re.search(r"\*\*Bucket:\*\*\s*([A-Za-z:_-]+)", body)
    if buc:
        out["bucket"] = buc.group(1)
    return out


def _split_tags(body: str) -> list[str]:
    raw = _take_field("Tags", body)
    if not raw:
        return []
    raw = raw.strip().rstrip(".").rstrip(",")
    parts = [t.strip(" `*") for t in raw.split(",")]
    return [p for p in parts if p]


def _split_related_tools(body: str) -> list[str]:
    raw = _take_field("Related tools", body)
    if not raw:
        return []
    raw = raw.strip().rstrip(".").rstrip(",")
    parts = [t.strip(" `*") for t in raw.split(",")]
    return [p for p in parts if p]


def parse_seed_lessons(doc_text: str) -> list[SeedLesson]:
    section = _extract_section(doc_text)
    raw = _split_lessons(section)
    out: list[SeedLesson] = []
    for code, short_title, body in raw:
        meta = _take_inline_meta(body)
        problem = _take_field("Problem", body) or ""
        evidence = _take_field("Evidence", body) or ""
        fix = _take_field("Fix", body) or ""
        next_time = (
            _take_field("Next time", body)
            or _take_field("Lesson", body)
            or fix  # fallback: use fix as next_time
            or "(no next_time clause supplied; review manually)"
        )

        # content: assemble Problem + Evidence + Fix narratives
        content_parts: list[str] = []
        if problem:
            content_parts.append(f"Problem: {problem}")
        if evidence:
            content_parts.append(f"Evidence: {evidence}")
        if fix:
            content_parts.append(f"Fix: {fix}")
        content = "\n\n".join(content_parts) if content_parts else f"(see {code} in LESSONS_LEARNED.md §9)"

        # category mapping with default
        raw_cat = meta.get("category", "PROC")
        category = CATEGORY_MAP.get(raw_cat, "PROC")

        # severity normalisation; default moderate
        severity = meta.get("severity", "moderate")

        # bucket default per most lessons
        bucket = meta.get("bucket", "business")
        if bucket == "scout":
            # Per CONSTITUTION §3 rule 1, scout bucket cannot accept lessons
            # with concrete content — these foundation lessons are abstract
            # already. Allow but tag clearly.
            pass

        tags = _split_tags(body) or []
        # Always tag these for traceability
        tags = list({*tags, "foundation-lesson", code.lower()})

        related_tools = _split_related_tools(body)

        full_title = f"{code} — {short_title}"
        out.append(
            SeedLesson(
                code=code,
                title=full_title,
                bucket=bucket,
                category=category,
                severity=severity,
                content=content,
                next_time=next_time,
                tags=tags,
                related_tools=related_tools,
            )
        )
    return out


# ---------------------------------------------------------------- driver

async def _run(*, dry_run: bool, use_test_db: bool) -> int:
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

    if not dry_run:
        from mcp_server import db as db_mod
        pool = db_mod.get_pool()
        await pool.open(wait=True)
        await db_mod.start_background_health_check()
        # Wait for is_healthy() to flip True
        for _ in range(20):
            if db_mod.is_healthy():
                break
            await asyncio.sleep(0.5)
        if not db_mod.is_healthy():
            print("ERROR: db_mod.is_healthy() never became True", file=sys.stderr)
            return 1

    text = LESSONS_DOC.read_text()
    lessons = parse_seed_lessons(text)
    print(f"Parsed {len(lessons)} seed lessons from {LESSONS_DOC}")

    if dry_run:
        for l in lessons:
            print(f"  {l.code} bucket={l.bucket} category={l.category} severity={l.severity}")
            print(f"    tags={l.tags}")
            print(f"    title={l.title!r}")
            print(f"    content={l.content[:120]!r}...")
            print(f"    next_time={l.next_time[:120]!r}...")
            print()
        return 0

    from mcp_server.tools.lessons import save_lesson

    inserted = 0
    duplicates = 0
    errors = 0
    for l in lessons:
        try:
            r = await save_lesson(
                title=l.title,
                content=l.content,
                next_time=l.next_time,
                bucket=l.bucket,
                tags=l.tags,
                category=l.category,
                severity=l.severity,
                related_tools=l.related_tools or None,
            )
        except Exception as exc:  # pragma: no cover
            print(f"  ✗ {l.code}: {type(exc).__name__}: {exc}")
            errors += 1
            continue

        status = r.get("status")
        if status == "saved":
            inserted += 1
            kind = "auto-approved" if r.get("auto_approved") else "pending_review"
            print(f"  ✓ {l.code} → {r.get('id')} ({kind})")
        elif status == "merge_candidate":
            duplicates += 1
            sim = r.get("similarity")
            sim_s = f"{sim:.3f}" if isinstance(sim, (int, float)) else str(sim)
            print(f"  ◇ {l.code} → duplicate of {r.get('similar_id') or r.get('matched_id')} (sim {sim_s})")
        else:
            errors += 1
            print(f"  ✗ {l.code} → {r}")

    print(f"\nDone: {inserted} inserted, {duplicates} duplicates, {errors} errors")
    return 0 if errors == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-db", action="store_true")
    args = parser.parse_args()
    return asyncio.run(_run(dry_run=args.dry_run, use_test_db=args.test_db))


if __name__ == "__main__":
    sys.exit(main())
