# Module 8 — Dream Engine (fase 1) — `plan.md`

**Status:** Draft (kickoff 2026-05-07)
**Authority:** companion to `specs/dream_engine/spec.md`
**Audience:** Claude implementer (per-phase brief)

---

## 1. Architecture overview

Single Python script `src/dream_engine/worker.py` invoked once per night by a systemd timer. Three jobs run sequentially; each in its own database transaction so one job's failure does not roll back the others. Run telemetry lands in `dream_engine_runs` (Phase A migration).

```
┌──────────────────────────────────────────────────────────────────────┐
│ systemd timer (02:00 ET)                                             │
│   ↓                                                                  │
│ pretel-os-dream-engine.service                                       │
│   ↓                                                                  │
│ python -m dream_engine.worker                                        │
│   ↓                                                                  │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ INSERT dream_engine_runs(started_at)  ── return run_id         │  │
│ │                                                                │  │
│ │ Job 1: utility_recompute()                                     │  │
│ │   BEGIN; CALL recompute_utility_scores(); COMMIT;              │  │
│ │   record duration + row counts in jobs_run JSON                │  │
│ │                                                                │  │
│ │ Job 2: dedup_pass()                                            │  │
│ │   BEGIN;                                                       │  │
│ │     SELECT pairs WHERE cosine_sim >= 0.95 AND cross-bucket     │  │
│ │     INSERT INTO cross_pollination_queue ... ON CONFLICT DO NOTHING │
│ │   COMMIT;                                                      │  │
│ │   record inserted/skipped counts                               │  │
│ │                                                                │  │
│ │ Job 3: archive_low_utility()                                   │  │
│ │   BEGIN;                                                       │  │
│ │     SELECT thresholds FROM operator_preferences (HARD FAIL on  │  │
│ │       missing key)                                             │  │
│ │     UPDATE lessons SET status='archived' WHERE <predicates>    │  │
│ │   COMMIT;                                                      │  │
│ │   record affected count                                        │  │
│ │                                                                │  │
│ │ UPDATE dream_engine_runs SET completed_at, status, jobs_run,   │  │
│ │   failures WHERE id=run_id                                     │  │
│ └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

Each job is a function returning `JobResult { duration_ms, rows_affected, error?: string }`. Worker collects three JobResults, decides overall status (success / partial / failed), writes the close record.

No LLM calls. No HTTP I/O. Only DB.

---

## 2. Phases

### Phase A — Schema prep + observability scaffolding

**Scope:**
- Migration 0038: add UNIQUE constraint to `cross_pollination_queue` (key shape decided per Q1), add `target_lesson_id` column if Q1 picks the per-pair option, create `dream_engine_runs` table, seed `operator_preferences` defaults for the 3 archive thresholds.
- Verify `recompute_utility_scores()` SQL function (from migration 0019) still runs against current schema. If broken, fix in 0038 or a sibling migration.
- Apply migration to `pretel_os` and `pretel_os_test` per the M7.B sanctioned workaround.

**Exit gate:**
- Migration applied to both DBs without error.
- `\d cross_pollination_queue` shows the UNIQUE constraint.
- `SELECT * FROM operator_preferences WHERE key LIKE 'archive.%'` returns 3 rows with default values.
- `SELECT recompute_utility_scores()` succeeds against `pretel_os_test`.
- `\d dream_engine_runs` shows the new telemetry table.

**Q&A to answer in this phase:**
- Q1, Q2, Q3, Q7 from spec §6.

**Cost:** $0. Trivial migration.

---

### Phase B — Worker core + 3 jobs

**Scope:**
- `src/dream_engine/__init__.py` (empty package marker).
- `src/dream_engine/worker.py` — main entry: `main()` orchestrates, `utility_recompute()`, `dedup_pass()`, `archive_low_utility()` are top-level functions returning JobResult.
- `src/dream_engine/queries.py` — SQL strings (separate module so they're testable + readable).
- `src/dream_engine/config.py` — reads operator_preferences for archive thresholds; raises on missing keys (no silent fallback per spec §7 risk row).
- Inline unit tests at `tests/dream_engine/test_worker.py` for each job (mocked DB).
- Slow integration test at `tests/dream_engine/test_e2e.py` against `pretel_os_test` — seeds fixture lessons, runs worker, asserts outcomes for each SC2/SC3/SC4/SC5.

**Exit gate:**
- Worker can be invoked manually as `PYTHONPATH=src python -m dream_engine.worker --dry-run` (dry-run prints what it would do without committing).
- `PYTHONPATH=src pytest tests/dream_engine/ -v` all green (unit + slow).
- mypy clean on `src/dream_engine/`.
- Manual run against `pretel_os_test` fixtures produces expected `dream_engine_runs` row + cross_pollination_queue inserts + lesson archival.

**Q&A to answer in this phase:**
- Q4, Q5, Q6 from spec §6.

**Cost:** $0 in tests (no LLM, no embedding API — embeddings are pre-existing).

---

### Phase C — systemd integration + dry-run in production

**Scope:**
- `infra/systemd/pretel-os-dream-engine.service` — Type=oneshot, Environment for DATABASE_URL, ExecStart=python -m dream_engine.worker.
- `infra/systemd/pretel-os-dream-engine.timer` — OnCalendar=*-*-* 02:00 America/New_York, Persistent=true.
- Install both as `--user` units. Enable timer.
- First production run is **dry-run mode** (manual invocation with --dry-run flag) to inspect what would change against real prod data. Decision-point: review dry-run output before letting the timer fire for real.

**Exit gate:**
- `systemctl --user list-timers | grep dream-engine` shows the timer with next firing.
- Dry-run output reviewed by operator. No surprises (no archival of valuable lessons, no flood of dedup proposals).
- Timer enabled but operator has flipped a "go-live" flag (or simply done the first manual non-dry-run successfully).

---

### Phase D — Live production + 7-day observation

**Scope:**
- Let the timer fire for 7 consecutive nights.
- Daily check: `SELECT * FROM dream_engine_runs ORDER BY started_at DESC LIMIT 7;` — all 7 rows present, all status='success' (or known-acceptable 'partial').
- Daily check: `SELECT count(*) FROM cross_pollination_queue WHERE proposed_by='dream_engine_dedup' AND created_at > now() - interval '24 hours';` — incremental small numbers, not flooding.
- If any night fails: inspect `dream_engine_runs.failures`, journalctl, fix root cause, re-run manually.

**Exit gate:**
- 7 consecutive successful nights logged.
- No operator complaints about archival or dedup decisions.
- Cost confirmed at $0 (verified via `v_daily_cost_by_purpose` — should show no change).

---

### Phase E — Module exit

**Scope:**
- Author `runbooks/module_8_dream_engine.md` (ops runbook):
  - How to manually trigger (`systemctl --user start pretel-os-dream-engine.service`).
  - How to read `dream_engine_runs` for incident triage.
  - How to tune the 3 archive thresholds via `preference_set`.
  - How to recover from a missed run (it auto-recovers via `Persistent=true` but document it).
  - 3 audit queries for the SDD §6 doc registry.
- `tasks.md` (root) row marked `[x] Module 8 complete (tag `module-8-complete`)`.
- Tag `module-8-complete` on the closing commit.

**Exit gate:**
- Runbook in repo.
- Tag created locally; operator chooses when to push.

---

## 3. Test strategy

| Test type | Location | What it covers | Cost |
|-----------|----------|----------------|------|
| Unit | `tests/dream_engine/test_worker.py` | Each job function in isolation, DB mocked. Verifies SQL string shape, JobResult shape, error handling. | $0, fast (~ms) |
| Slow integration | `tests/dream_engine/test_e2e.py` (`@pytest.mark.slow`) | Full worker run against `pretel_os_test` with seeded fixtures. Verifies SC2 / SC3 / SC4 / SC5. | $0, ~few seconds |
| Manual dry-run | Phase C, Phase D | Production data, --dry-run flag, no commit. | $0 |
| Production observation | Phase D | 7-day timer fire, real data. | $0 |

**Test-DB drift watchdog:** before running slow tests, re-apply migrations 0028a + 0030 + 0037 to `pretel_os_test` if they appear missing (per CLAUDE.md "When something feels off"). Add a one-line check to `tests/dream_engine/conftest.py` if it isn't already in the shared fixtures.

---

## 4. Cost forecast

| Item | Forecast |
|------|----------|
| Module build (Phase A–E) | $0. Pure SQL + Python. No LLM in fase 1. |
| Steady-state production | $0 / month. No external API calls. |
| Future fase 2 (LLM-driven dedup, contradiction detection) | TBD when chartered. |

This module is the **cheapest** in pretel-os history.

---

## 5. Dependencies and load-bearing assumptions

**Hard dependencies (must be true at Phase A start):**
- `recompute_utility_scores()` SQL function exists and works (migration 0019, last touched in M0.X / 0028a).
- `cross_pollination_queue` exists with current schema (migration 0010).
- `lessons` table has `embedding` column populated for all active rows (auto-index worker handles this — verified: 77/77 active lessons have embeddings, per a quick `SELECT count(*) FROM lessons WHERE status='active' AND embedding IS NOT NULL` to be run at Phase A start).
- `operator_preferences` table exists (M0.X / 0025) — verified by Router Phase B.

**Load-bearing assumptions:**
- Operator does not delete or rename `cross_pollination_queue` rows mid-night. Worker is idempotent against re-inserts but not against active concurrent edits.
- Vivobook server is up at 02:00 ET. (`Persistent=true` in the timer mitigates downtime.)
- pgvector cosine similarity computation remains < 60 s for the entire active-lesson cross-product. At 1000 lessons this is 1M comparisons — still fine for nightly. At 100k we need ANN indexing (HNSW per ADR-024 — deferred).

---

## 6. Tuning playbook (post-deployment)

| Symptom | Knob | How |
|---------|------|-----|
| Too many dedup proposals per night | similarity threshold | edit dedup query in `src/dream_engine/queries.py`, raise from 0.95 to 0.97 (constitutional rule still says ≥0.95 as the floor; nothing forbids running tighter operationally) |
| Too few dedup proposals (false negatives) | top-K | increase from K=5 to K=10 in dedup query |
| Lessons being archived too aggressively | `archive.usage_window_days` | `preference_set('archive.usage_window_days', '700')` — next run respects new value |
| Lessons not being archived enough (corpus growing) | same key | `preference_set('archive.usage_window_days', '365')` — tighter |
| Worker missing nightly runs | systemd timer | `systemctl --user status pretel-os-dream-engine.timer` + check `Persistent=true` is set |

---

## 7. Out of scope handling (the 4 deferred Dream Engine jobs)

Each deferred job has a future trigger:

| Deferred job | Re-charter trigger |
|--------------|-------------------|
| Summarize conversations >90d (§5.5 rule 23) | A transcript pipeline lands. Likely candidates: Telegram conversational mode without per-turn tool calls, or an external agent that hits the MCP server with raw transcripts. At that point §5.5 rule 23 becomes operational; a follow-up amendment lifts the "deferred" mark. |
| Reindex changed embeddings | Currently no-op since migration 0037. If the embedding model changes (§2.5 amendment), this job becomes load-bearing for a one-shot reindex; spec'd separately at amendment time. |
| Expand pending cross-poll | Off-charter. If a real signal emerges that operators want enrichment of cross-poll proposals beyond what `morning_brief_pending` covers, re-charter with concrete UX. |
| Morning-brief preparation | n8n morning intelligence worker lands. At that point we know the consumer's data shape; we build the producer to match. |

---

## 8. References

- `specs/dream_engine/spec.md` — what we're building.
- `specs/dream_engine/tasks.md` — atomic checkboxes.
- ADR-029 — the consolidated amendment chartering this scope.
- ADR-024 — HNSW indexes deferred until pgvector >= 0.7 or volume justifies. Relevant if dedup query gets slow at scale.
- `runbooks/sdd_module_kickoff.md` — Trinity rule.
- Migration 0019 — `recompute_utility_scores()` source.
- Migration 0010 — cross_pollination_queue source.
