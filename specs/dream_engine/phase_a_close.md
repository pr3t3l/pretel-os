# Module 8 Dream Engine — Phase A close

**Status:** Decisions in progress (kickoff 2026-05-07)
**Authority:** companion to `specs/dream_engine/spec.md` §6 (open questions) and `specs/dream_engine/plan.md` §2 Phase A.

This document resolves Q1 / Q2 / Q3 / Q7 from the spec before writing migration 0039. Each decision names alternatives considered and rationale.

---

## Q1 — UNIQUE-key shape on `cross_pollination_queue`

**Decision:** `UNIQUE (origin_lesson, target_lesson_id, proposed_by)` — per-pair granularity. New column `target_lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE` added in migration 0039.

**Alternatives considered:**

A. `UNIQUE (origin_lesson, target_bucket, proposed_by)` — coarse, one row per (source lesson, target bucket, proposer). No schema change (target_bucket already exists). **Rejected:** loses information about *which* target lesson was matched. If lesson A in personal has high-similarity matches with lessons B and C in business, only the first INSERT succeeds; B vs C is silently lost. Operator triaging via Telegram would see "this matches *something* in business" without knowing which lesson — useless for the merge decision.

B. **`UNIQUE (origin_lesson, target_lesson_id, proposed_by)` — chosen.** Each pair gets its own row. Operator sees exactly which two lessons to compare. Multiple candidates from the same source can coexist with different target_lesson_ids. Schema cost is one column + one FK + one index — trivial. Idempotency holds: same pair re-proposed on subsequent nights → ON CONFLICT DO NOTHING.

C. `UNIQUE (origin_lesson, target_lesson_id)` (no `proposed_by`) — even tighter. **Rejected:** `dream_engine_dedup` and `dream_engine_cross_bucket` are conceptually different proposals (one is about merging, the other about idea propagation). They could legitimately both exist for the same pair. Including `proposed_by` in the key keeps them distinguishable.

**Reasoning text** in the queue row should still describe *why* the pair was flagged (e.g., "cosine similarity 0.97; both reference Postgres triggers"). The structured columns hold the IDs; the prose holds the explanation.

---

## Q2 — `target_lesson_id` column or derive from text

**Decision:** Add column. `ALTER TABLE cross_pollination_queue ADD COLUMN target_lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE` in migration 0039. NULLable to preserve compatibility with non-merge-candidate rows (`proposed_by='manual'` future entries that operate at bucket-idea level instead of lesson-pair level).

**Alternatives considered:**

A. Derive `target_lesson_id` by parsing the `idea` or `reasoning` text. **Rejected:** parsing free-text for IDs is fragile and prevents the FK constraint. The whole point of the per-pair key (Q1) is making the pair queryable as structured data.

B. **Add column, NULLable, FK with ON DELETE CASCADE — chosen.** NULL allowed because future `'manual'` rows might be bucket-level ideas without a specific target lesson. The FK + CASCADE means if a target lesson is deleted, the queue row dies with it (clean state). The UNIQUE constraint from Q1 must allow NULL semantics: PostgreSQL treats NULLs as distinct in UNIQUE constraints by default, so multiple NULL target_lesson_id rows for the same origin coexist — that's actually the desired behavior for `'manual'` bucket-level ideas.

**Caveat:** for `dream_engine_dedup` rows specifically, target_lesson_id must be NON-NULL. The Dream Engine worker enforces this in code (the SQL function refuses to INSERT a `dream_engine_dedup` row with NULL target_lesson_id). No schema-level CHECK constraint — would over-constrain the table for future writers.

---

## Q3 — `dream_engine_runs` new table or fold into `llm_calls`

**Decision:** New table `dream_engine_runs`.

**Alternatives considered:**

A. Fold into `llm_calls` (the existing partitioned table for LLM API call telemetry). **Rejected** for three reasons: (1) Dream Engine fase 1 makes zero LLM calls — putting non-LLM rows in a table named `llm_calls` is semantic vandalism. (2) `llm_calls` schema (per migration 0013) has columns like `model`, `prompt_tokens`, `completion_tokens`, `cost_usd`, `purpose` — none apply to Dream Engine. Forcing fit means leaving 80% of fields NULL. (3) `llm_calls` is partitioned by month for query performance over its expected volume; Dream Engine emits ~1 row per day = ~365/year, which is fine in a single small table.

B. **New table `dream_engine_runs` — chosen.** Slim schema:
```
id            UUID PK
started_at    TIMESTAMPTZ NOT NULL DEFAULT now()
completed_at  TIMESTAMPTZ
status        TEXT NOT NULL CHECK (status IN ('running', 'success', 'partial', 'failed'))
jobs_run      JSONB NOT NULL DEFAULT '{}'   -- per-job: {duration_ms, rows_affected, error?}
failures      JSONB NOT NULL DEFAULT '[]'   -- list of {job, error_class, error_message}
worker_pid    INTEGER                        -- helpful for debugging concurrent run scenarios
```

Index on `(started_at DESC)` for the operator's "show last 7 nights" query. No partitioning until volume justifies (years from now if ever).

C. Append to `routing_logs`. **Rejected:** routing_logs is per-MCP-turn telemetry. Different concern, different cardinality.

---

## Q7 — Seed `operator_preferences` defaults via migration vs first-run

**Decision:** Seed via migration 0039 with INSERT ... ON CONFLICT DO NOTHING.

**Alternatives considered:**

A. First-run insert (Dream Engine worker checks for keys on startup, inserts defaults if missing). **Rejected:** hides defaults in code, makes them less observable (`SELECT * FROM operator_preferences WHERE key LIKE 'archive.%'` returns 0 rows until first run), and creates an order-dependency (worker must run before any other code reads thresholds — for tests this is annoying).

B. **Seed via migration — chosen.** Defaults are configuration; configuration belongs in migrations. Three rows inserted explicitly:
```
('archive.usage_window_days',    '500', 'archive', 'integer')
('archive.utility_threshold',    '0.5', 'archive', 'numeric')
('archive.utility_lookback_days', '90', 'archive', 'integer')
```

(Exact column names match the operator_preferences schema from M0.X / migration 0025 — to be verified at migration write time.)

C. Hardcode defaults in `src/dream_engine/config.py` with a fallback ladder (env var → operator_preferences → hardcoded). **Rejected:** the constitutional amendment §5.5 rule 22 v5.2 says "Three thresholds (formerly hardcoded 180/0.5/90) now parametrized as `operator_preferences` keys" — having a hardcoded fallback weakens that contract. Worker hard-fails on missing key per spec §7 risk row "operator_preferences keys not seeded".

---

## Decisions summary

| Q | Resolution | Schema impact |
|---|------------|---------------|
| Q1 | UNIQUE (origin_lesson, target_lesson_id, proposed_by) | + new constraint on cross_pollination_queue |
| Q2 | Add target_lesson_id UUID FK NULLable, ON DELETE CASCADE | + new column on cross_pollination_queue |
| Q3 | New table `dream_engine_runs` | + new table |
| Q7 | Seed defaults via migration | + 3 rows in operator_preferences |

**Migration 0039** writes all four changes in a single transaction. Idempotent (UNIQUE … IF NOT EXISTS, ON CONFLICT DO NOTHING). Estimated DDL: ~50 lines.

Q4 / Q5 / Q6 remain open — those are Phase B questions (worker code semantics), not Phase A schema.
