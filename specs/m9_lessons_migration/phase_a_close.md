# Module 9 — lessons_migration — close-out

**Status:** Closed 2026-05-07
**Authority:** `tasks.md` Module 9 placeholder + scope correction during execution.
**Audience:** Operator + future Claude reading the migration trail.

---

## Scope correction

`tasks.md` listed M9 as "89 foundation-era lessons + 12 ideas from `docs/LESSONS_LEARNED.md` seed corpus into the live `lessons` table". **Reality during execution:**

- `LESSONS_LEARNED.md §9` contains **17 seed lessons**, not 89.
- The 89-count refers to the OpenClaw-era `LL-MASTER.yaml` corpus living in a separate repo (`github.com/pr3t3l/openclaw-config/lessons-learned`, per the references at line 776 of `LESSONS_LEARNED.md`). That repo wasn't cloned into this workspace.
- The "12 ideas" line referred to the OpenClaw ideas file, similarly in the external repo.

**Decision:** scope M9 fase 1 to the 17 in-tree seed lessons. The 89 OpenClaw lessons stay as a future M9.fu1 if/when the operator wants them — would require cloning the openclaw-config repo and writing a YAML→save_lesson parser variant.

---

## What ran

`scripts/migrate_seed_lessons.py` parses `LESSONS_LEARNED.md §9` into 17 `SeedLesson` dataclasses and feeds them through the `save_lesson` MCP tool. Per CONSTITUTION §2.1, the script never writes SQL DML — every row enters via the canonical mutation path. Embeddings are generated synchronously by save_lesson using `text-embedding-3-large`.

### Parser handles two markdown formats

- **Format A** (LL-PROC/ARCH/DATA/COST/AI/INFRA): tagline `**Category:** X / **Severity:** Y / **Bucket:** Z`, then `**Problem.** / **Evidence.** / **Fix.** / **Next time.** / **Tags:** / **Related tools:**` — period-terminated labels.
- **Format B** (LL-M4-PHASE-A-* and LL-M0X-*): `**Severity:**` only, plus `**Captured:**`, then colon-terminated labels (`**Problem:**`, `**Fix:**`, `**Lesson:**`).

The regex `\*\*Label[.:]?\*\*` accepts both. When `**Next time.**` is missing, the parser falls back to `**Lesson:**`, then to `**Fix:**` as a last resort. This guarantees a non-empty `next_time` clause on every row, which is required for §5.2 rule 13 auto-approval.

### Idempotency

Verified: a second run of the script against pretel_os_test reported `0 inserted, 17 duplicates, 0 errors`. `save_lesson` returns `merge_candidate` when a row above similarity 0.92 already exists — the script counts those as duplicates and continues.

---

## Execution timeline

| Step | DB | Result |
|------|----|--------|
| Dry-run | n/a | 17 lessons parsed correctly |
| Idempotency tag-fix | n/a | parser regex updated to stop at `\n---` separator |
| First run | `pretel_os_test` | 17 inserted, all auto-approved |
| Second run | `pretel_os_test` | 17 duplicates (idempotency confirmed) |
| Production run | `pretel_os` | 17 inserted, all auto-approved |

---

## Verification (post-prod-run)

```
=== Lessons table summary post-M9 ===
  bucket   |     status     | count
-----------+----------------+-------
 business  | active         |    41   (was 25 before; +16 foundation lessons)
 personal  | active         |     0
 scout     | active         |    46   (was 45; +1 foundation: LL-AI-001)
 (...)
```

(LL-AI-001 has `bucket=scout` because the lesson is *about* Scout's defense-in-depth filter — the right place for an abstract lesson about Scout security.)

```
=== All foundation-lesson tagged rows ===
 total
-------
    17
```

---

## What's now visible in admin

After this migration:

- `/memory?tab=lessons` shows the 17 new entries — each title with its `LL-XYZ-NNN — short title` format
- `/memory?tab=lessons&q=foundation-lesson` filters to just these
- `/memory?tab=lessons&bucket=scout` shows LL-AI-001 alongside operational scout lessons
- `/buckets` counts now reflect the new totals per bucket
- Each lesson clickable → `/memory/lessons/{id}` drill-down with full content + next_time + tags + metadata

---

## Cost

OpenAI embedding API: 17 calls × ~$0.0002 = **~$0.003 total**.

---

## Out of scope (deferred)

- **89 OpenClaw lessons** in `github.com/pr3t3l/openclaw-config/lessons-learned`. Tracked as M9.fu1.
- **12 ideas** from the same external repo. Tracked as M9.fu2.
- **Drift between LESSONS_LEARNED.md §9 and the now-canonical lessons table.** Going forward the seed text in §9 is historical — new lessons land directly in the table via `save_lesson`. Optional cleanup (M9.fu3): mark §9 as "migrated 2026-05-07; canonical lives in `lessons` table" without deleting the human-readable narrative.
