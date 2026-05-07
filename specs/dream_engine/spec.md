# Module 8 — Dream Engine (fase 1) — `spec.md`

**Status:** Draft (kickoff 2026-05-07)
**Module:** M8 / Dream Engine — fase 1 (MVP)
**Authority:** `CONSTITUTION.md §2.6` (chartered worker, v5.2 rescope) · `§5.3 rule 18` (utility formula) · `§5.4 rule 20` (cross_pollination_queue writer) · `§5.5 rule 22` (archive thresholds) · `§5.5 rule 24` (nightly dedup) · ADR-029 (consolidated amendment) · `decisions` row 9e8bacad (M6 cancellation prerequisite)
**Owner:** Alfredo Pretel Vargas
**Audience:** Operator + Claude implementer

---

## 1. Two-minute summary

Dream Engine is the nightly consolidation worker. It runs at 02:00 America/New_York via a systemd timer and executes three jobs in a single batch transaction-per-job (independent failure isolation):

1. **Recompute `utility_score`** on `tools_catalog` and `lessons` per the §5.3 rule 18 formula. Invokes the existing SQL function `recompute_utility_scores()` (migration 0019). Output: updated `utility_score` column. Cost: ~5 ms, $0.
2. **Dedup pass + cross_pollination_queue writer.** For every active lesson, find its top-K nearest neighbors above similarity ≥0.95 in *other* buckets (cross-bucket merge candidates). Insert a row into `cross_pollination_queue` with `proposed_by='dream_engine_dedup'`. UNIQUE constraint on `(origin_lesson, target_bucket, proposed_by)` makes re-runs idempotent — second-night INSERT for the same pair becomes a no-op via `ON CONFLICT DO NOTHING`. Cost: ~100 ms per night at current corpus (77 lessons), $0.
3. **Archive low-utility lessons** per §5.5 rule 22. SET status='archived' for any active lesson whose row matches all three predicates: `(now() - created_at) > archive.usage_window_days days`, `usage_count = 0`, `utility_score < archive.utility_threshold` over `archive.utility_lookback_days`, AND not referenced in `project_state`. Thresholds read from `operator_preferences` at run time (defaults: 500 / 0.5 / 90). Cost: ~10 ms, $0.

The four originally-chartered Dream Engine jobs that are NOT in this fase 1 (per ADR-029): summarize conversations >90d (deferred — no transcript pipeline), reindex changed embeddings (no-op since migration 0037 added trigger-based invalidation), expand pending cross-poll (off-charter — operationally redundant), morning-brief preparation (deferred — no n8n consumer).

---

## 2. Why now (motivation)

The M6 reflection_worker that was originally going to populate `cross_pollination_queue` was cancelled (decisions row 9e8bacad). The queue has existed since migration 0010 (M2) with **zero rows ever inserted by code**. Without a writer, the queue + its 2 MCP tools (`list_pending_cross_pollination`, `resolve_cross_pollination`) + Telegram `/cross_poll_review` handler are dead infrastructure.

`utility_score` on tools_catalog and lessons is computed once at insert time and never updated. The Router uses this score for ranking recommendations (§5.3 rule 18). Without nightly recompute, the score is stale — `usage_count`, `last_used_at`, and `cross_bucket_count` evolve but `utility_score` doesn't reflect them.

The lessons table grows monotonically. With 77 rows today the table is fine; at 500+ the noise from never-archived low-utility entries starts to contaminate default retrieval per §5.5 rule 22.

These three problems share a home: a nightly worker with SQL-and-vector-ops only. No LLM calls in fase 1.

---

## 3. Success criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| SC1 | systemd timer fires at 02:00 ET nightly and a `dream_engine_runs` row records start_at, end_at, jobs_run JSON, status (success / partial / failed) | `journalctl --user -u pretel-os-dream-engine.timer` + `SELECT * FROM dream_engine_runs ORDER BY started_at DESC LIMIT 7` shows 7 consecutive nightly rows |
| SC2 | After one nightly run, `tools_catalog.utility_score` reflects current `usage_count` and `last_used_at` per the formula | spot-check 3 rows: compute formula by hand, compare to `utility_score` column |
| SC3 | Cross-bucket lesson pairs with similarity ≥0.95 produce one `cross_pollination_queue` row per night with `proposed_by='dream_engine_dedup'`, status='pending' | `SELECT count(*) FROM cross_pollination_queue WHERE proposed_by='dream_engine_dedup'` increases by N on first run, stays at N on second run (idempotency proven) |
| SC4 | Lessons matching all three archive predicates have status flipped to 'archived' on the night they cross the threshold | seed test fixture with a row crossing the threshold, run worker, assert `status='archived'` |
| SC5 | Worker survives one job failing (e.g., dedup raises) — other two jobs still complete; `dream_engine_runs.status='partial'` with failed job named in `failures` JSON | inject a deliberate fault in a slow test |
| SC6 | Operator can tune thresholds via `preference_set('archive.usage_window_days', '700')` and the next run uses the new value (no constitutional amendment, no code change) | call `preference_set`, run worker manually, observe behavior change |
| SC7 | 7-day observation period after deployment with no cost anomalies, no DB pool starvation, no missed-run gaps in `dream_engine_runs` | `journalctl` + `dream_engine_runs` audit query in `runbooks/module_8_dream_engine.md` |

---

## 4. Out of scope (for fase 1)

- Conversation summarization (§5.5 rule 23, deferred per ADR-029).
- Embedding reindex job (covered by migration 0037).
- Morning brief data preparation (deferred per ADR-029).
- Expand pending cross-poll (off-charter per ADR-029).
- LLM-driven dedup or contradiction detection (vector-only in fase 1; LLM would be a fase 2 enhancement).
- Cross-bucket idea propagation that isn't a merge candidate (e.g., "this lesson about Postgres locks applies to MSSQL too" — out of scope until a real signal emerges).
- Failure alerting (Telegram notify on partial/failed run) — fase 2.
- Manual `fire_dream_engine` MCP tool — fase 2 if a real ad-hoc-trigger need emerges.

---

## 5. Non-functional requirements

| Requirement | Target |
|-------------|--------|
| **Cost per night** | $0 (no LLM, no embedding API). The worker uses pre-computed embeddings stored in the DB. |
| **Wall time per night** | < 60 s at current corpus (77 lessons, 42 catalog rows). Should remain < 5 min at 1000 lessons. |
| **Idempotency** | A second consecutive run of the same calendar date produces no duplicate rows in any output. UNIQUE constraint enforces this for cross_pollination_queue. |
| **Failure isolation** | Each of the 3 jobs runs in its own transaction. One job's failure does not roll back the others. The worker process exits with code 0 on partial success (non-failed jobs ran), 1 on full failure (worker itself crashed). |
| **Observability** | Every run inserts a `dream_engine_runs` row with started_at, completed_at, status, jobs_run JSON (per-job duration + counts), failures JSON (errors per failed job). |
| **Database connection** | Reuses the existing `db_mod.get_pool()` pattern. No new connection pool. |
| **Code budget** | Worker fits in ~300 lines of Python (single file at `src/dream_engine/worker.py`). Each job is ~50 lines. |

---

## 6. Open questions

These get answered at phase kickoff, not now:

| ID | Question | Phase to resolve |
|----|----------|------------------|
| Q1 | Exact UNIQUE-key shape on `cross_pollination_queue`. Options: `(origin_lesson, target_bucket, proposed_by)` (one row per cross-bucket relationship per source) vs `(origin_lesson, target_lesson_id, proposed_by)` (one row per pair). The second is more granular but requires `target_lesson_id` to be added since today the queue has `target_bucket` not `target_lesson_id`. | Phase A |
| Q2 | Where does `target_lesson_id` live? Add column to queue (migration), or derive from `idea`/`reasoning` text? | Phase A |
| Q3 | Should `dream_engine_runs` be a new table or fold into existing `llm_calls` (which is misnamed if no LLM is called)? | Phase A |
| Q4 | Top-K for the dedup nearest-neighbor query — K=3, K=5, K=10? Higher K = more candidate pairs = more queue noise. Lower K = miss real candidates. | Phase B |
| Q5 | Cosine similarity vs L2 distance for the ≥0.95 threshold — pgvector default is L2; the rest of the codebase uses cosine. Confirm consistency. | Phase B |
| Q6 | Does archival need to NOTIFY anything? Today archived lessons trigger `readme_dirty_bucket` via the existing trigger; verify it still fires on UPDATE-of-status. | Phase B |
| Q7 | Default values for `operator_preferences` — seed via migration or insert-on-first-run? | Phase A |

---

## 7. Risks and mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Dedup pass produces too many false-positive merge candidates and floods `cross_pollination_queue` | Medium | Medium — operator review backlog grows | Start with similarity ≥0.95 (per §5.5 rule 24), high bar. Monitor first-week count. Tighten to ≥0.97 if needed via M8 plan §6 tuning step. |
| Archive too aggressive at 500-day default and removes lessons the operator still finds useful | Low | Low — `status='archived'` is reversible (UPDATE back to 'active') and lessons remain queryable via `search_lessons(include_archive=true)` | Tunable via `preference_set` per ADR-029. 500 was the operator's instruction. |
| systemd timer drift causes missed runs (laptop suspended, server restart) | Medium | Low — one missed night is recoverable; `recompute_utility_scores` is idempotent and dedup runs against current state | Use `Persistent=true` in timer unit so a missed run fires on next boot. Document in runbook. |
| `recompute_utility_scores()` SQL function is broken or out of date with current schema | Low | High — utility scores stop updating | Phase A includes a "verify function exists and runs against current schema" step. If broken, fix before depending on it. |
| operator_preferences keys not seeded → archive runs against NULL thresholds → archives nothing or everything | Low | Medium | Worker hard-fails (raises) if any of the 3 keys is missing. Seeds via Phase A migration with explicit defaults. No silent fallback. |
| First night of dedup creates hundreds of cross_pollination_queue rows the operator must triage | Low | Medium | Start with single-night burst to clear pre-existing pairs, then steady-state is incremental. Alternatively, run a one-shot in Phase D with a bigger threshold (≥0.97) to seed the queue conservatively. |

---

## 8. Definition of done

Module 8 fase 1 is complete when:

1. All 7 success criteria above pass (SC1–SC7).
2. `runbooks/module_8_dream_engine.md` shipped (operations runbook: how to manually trigger, how to read `dream_engine_runs`, how to tune thresholds, how to recover from a missed run).
3. Tag `module-8-complete` created on the closing commit (operator-driven push).
4. CONSTITUTION §2.6 footnote updated if any deferred job got rechartered during M8 (none planned but possible).

---

## 9. Cross-references

- `specs/dream_engine/plan.md` — phased architecture and Q&A.
- `specs/dream_engine/tasks.md` — atomic checkboxes per phase.
- ADR-029 (`decisions` row a39bc9b9) — constitutional amendment v5.2 that chartered this scope.
- M6 cancellation (`decisions` row 9e8bacad) — prerequisite for the Dream Engine getting sole-writer status on cross_pollination_queue.
- Migration 0010 (`cross_pollination_queue` table schema).
- Migration 0019 (`recompute_utility_scores()` SQL function).
- Migration 0037 (embedding invalidation on UPDATE — closes the "reindex" job slot).
