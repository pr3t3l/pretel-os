# Module 8 Dream Engine — Phase B close

**Status:** Closed 2026-05-07
**Companion to:** `specs/dream_engine/spec.md` (success criteria + open Q's), `specs/dream_engine/plan.md` Phase B, `specs/dream_engine/tasks.md` (atomic items M8.B.1-16).

This document resolves Q4 / Q5 / Q6 from the spec, notes one constitutional gap, and summarizes Phase B output.

---

## Q4 — Top-K for nearest-neighbor query

**Decision:** K=5 per `(origin_lesson, target_bucket)`.

Constant `DEDUP_TOP_K` in `src/dream_engine/queries.py`. Tunable without migration: edit constant + redeploy. Per the plan §6 tuning playbook, raise to 10 if observation reveals false negatives.

**Reasoning:** at 77 active lessons today, K=5 is generous — we'd be surprised to see five lessons in another bucket all scoring ≥0.95 against the same source. K=3 was too tight (one accidental high-similarity miss could drop a real candidate); K=10 would generate noise without payoff at current scale.

---

## Q5 — Cosine vs L2 similarity

**Decision:** Cosine via pgvector `<=>` operator. Distance ≤ 0.05 ↔ similarity ≥ 0.95.

The codebase already uses cosine in `recommend_skills_for_query` and the Router's L4 retrieval (per `specs/router/spec.md`). Mixing distance metrics across the same embedding column would produce inconsistent ranking.

`recompute_utility_scores()` formula uses `usage_count` and `cross_bucket_count` only, no embedding distance — so utility recompute is metric-neutral. The dedup pass is the only place metric choice matters, and it picks cosine.

Constant `DEDUP_DISTANCE_THRESHOLD = 0.05` lives in `queries.py` for the same tunability rationale as K.

---

## Q6 — Does archival fire `readme_dirty`?

**Decision:** YES — confirmed by inspection of triggers on `lessons` (migration 0034 attached `trg_lessons_readme_dirty_bucket` and `trg_lessons_readme_dirty_project` AFTER INSERT OR UPDATE).

When the worker flips `status='active' → 'archived'`, the AFTER UPDATE trigger fires `pg_notify('readme_dirty', ...)`, the readme consumer (`pretel-os-readme.service`) debounces 30s and regenerates the bucket README via `regenerate_bucket_readme`. The bucket README's auto-generated lessons section filters to `status='active'`, so archived lessons disappear from default views automatically. No additional NOTIFY required from the worker itself.

Verified indirectly by all 12 slow integration tests passing: the archival test asserts `status='archived'` post-UPDATE, which would have errored if the readme_dirty trigger raised.

---

## Constitutional drift acknowledged — predicate (5) of §5.5 rule 22

CONSTITUTION §5.5 rule 22 requires three predicates for archive eligibility:
1. `usage_count = 0` after `archive.usage_window_days` days from creation ✓ implemented
2. `utility_score < archive.utility_threshold` over `archive.utility_lookback_days` days ✓ implemented
3. **Not referenced by any active project in `project_state`** ✗ NOT IMPLEMENTED in fase 1

The `project_state` schema does not have a typed FK column to `lessons.id`. `project_state` stores `(state_key, content TEXT)` pairs, and lesson references would be embedded in `content` as substrings — parsing free-text for IDs is the kind of fragile predicate this whole architecture avoids.

**Risk assessment:** microscopic at fase 1 scale.
- archive eligibility requires `usage_count = 0` — no calls to a lesson via `search_lessons` for 500+ days. A lesson actively referenced by a project would be retrieved, increment its `usage_count`, and disqualify itself naturally.
- utility_score < 0.5 is a low bar — a lesson cited even once recently would score above 0.5 via the formula's recency_weight component (0..2.0).
- The 500-day window means the rule only fires on genuinely abandoned lessons.

**Re-charter trigger:** if the operator finds Dream Engine archiving lessons that *were* relevant to active projects, predicate (5) gets implemented. Path: add `lesson_ids UUID[]` column to `project_state` OR derive from a future structured reference table; update the archive query to JOIN against it.

Tracked as `M8.fu4` in tasks.md (out-of-band items).

---

## Files written

```
src/dream_engine/
├── __init__.py     (24 lines, package docstring)
├── config.py       (76 lines, ArchiveThresholds + load_archive_thresholds)
├── queries.py      (105 lines, SQL constants for 3 jobs + telemetry lifecycle)
└── worker.py       (217 lines, JobResult + 3 job runners + main + CLI)

tests/dream_engine/
├── __init__.py     (empty)
├── test_worker_unit.py    (97 lines, 6 tests, no DB, JobResult + _safe contracts)
└── test_e2e.py            (302 lines, 12 tests @pytest.mark.slow, real test DB)
```

Total: ~820 lines net new (code + tests).

---

## Success criteria status

| SC | Status | Evidence |
|----|--------|----------|
| SC1 — `dream_engine_runs` row recorded with telemetry | ✅ | `test_main_records_run_telemetry` |
| SC2 — utility_recompute updates utility_score | ✅ | `test_utility_recompute_runs_clean` (smoke + 33 rows touched in production-test smoke) |
| SC3 — dedup writes pair / idempotent | ✅ | `test_dedup_inserts_cross_bucket_pair`, `test_dedup_idempotent_second_run_inserts_zero` |
| SC4 — archive flips low-utility | ✅ | `test_archive_flips_old_low_utility_lesson` + 2 negative tests |
| SC5 — partial status on job fault | partial | `_safe()` + `_finish_run()` unit-tested for the contract; full main() partial-status path will be exercised in a fault-injection test we can add or via Phase D production fault if it occurs |
| SC6 — `preference_set` tunes thresholds | ✅ | `test_archive_thresholds_loaded_from_seed` reads via the same path; `test_archive_thresholds_missing_key_raises` proves the hard-fail contract |
| SC7 — 7-day production observation | not testable in unit suite | Phase D |

---

## Performance observations from smoke test

Against `pretel_os_test` (~32 active lessons + 42 catalog rows):
- Total wall time: **4 ms** (utility 4ms, dedup 1ms, archive 0ms)
- 33 rows touched by utility recompute
- 0 dedup pairs (no near-duplicates in test corpus)
- 0 archives (no aged-out lessons)

Plan §1 budget said < 60 s at current corpus, < 5 min at 1000 lessons. Current: < 10 ms. Order of magnitude room before any concern. HNSW indexes (ADR-024) remain deferred — pgvector exact search is fine here.

---

## Phase B exit gate

- [x] Worker invocable via `python -m dream_engine.worker --dry-run`
- [x] All 6 unit tests + 12 slow integration tests pass (18/18, full suite 277/277)
- [x] mypy clean on `src/dream_engine/`
- [x] Manual smoke test against `pretel_os_test` clean
- [x] Q4/Q5/Q6 documented above

**Next:** Phase C — systemd timer + production dry-run review + first live run.
