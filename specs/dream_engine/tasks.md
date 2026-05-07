# Module 8 — Dream Engine (fase 1) — `tasks.md`

**Status:** Draft (kickoff 2026-05-07)
**Convention:** Atomic — one checkbox per migration / function / test / config file. < 30 minutes per item.
**Phases match `specs/dream_engine/plan.md` §2.**

---

## Phase A — Schema prep + observability

- [ ] **M8.A.1** — Decide Q1 (UNIQUE-key shape on cross_pollination_queue). Document choice in `specs/dream_engine/phase_a_close.md` Q1.
- [ ] **M8.A.2** — Decide Q2 (target_lesson_id column or derive from text). Document in phase_a_close Q2.
- [ ] **M8.A.3** — Decide Q3 (`dream_engine_runs` new table vs fold into existing). Document in phase_a_close Q3.
- [ ] **M8.A.4** — Decide Q7 (seed defaults via migration vs first-run insert). Document in phase_a_close Q7.
- [ ] **M8.A.5** — Verify `recompute_utility_scores()` runs against current schema: `psql "$TEST_DSN" -c "SELECT recompute_utility_scores();"`. If it errors, escalate before continuing.
- [ ] **M8.A.6** — Write migration `0038_dream_engine_schema.sql`:
  - UNIQUE constraint on cross_pollination_queue per Q1 outcome.
  - (conditional on Q2) ALTER TABLE cross_pollination_queue ADD COLUMN target_lesson_id UUID REFERENCES lessons(id).
  - CREATE TABLE dream_engine_runs (id UUID PK, started_at, completed_at, status TEXT CHECK IN ('success','partial','failed'), jobs_run JSONB, failures JSONB).
  - INSERT into operator_preferences (key, value, category) VALUES (...) for `archive.usage_window_days='500'`, `archive.utility_threshold='0.5'`, `archive.utility_lookback_days='90'` with ON CONFLICT DO NOTHING.
  - INSERT INTO schema_migrations with md5 self-hash per project convention.
- [ ] **M8.A.7** — Apply 0038 to `pretel_os` via `psql -1 -f`.
- [ ] **M8.A.8** — Apply 0038 to `pretel_os_test` via `psql -1 -f`.
- [ ] **M8.A.9** — Verify constraints: `psql "$DATABASE_URL" -c "\d cross_pollination_queue"` shows UNIQUE; `\d dream_engine_runs` shows the new table.
- [ ] **M8.A.10** — Verify operator_preferences seeded: `SELECT * FROM operator_preferences WHERE key LIKE 'archive.%';` returns 3 rows.
- [ ] **M8.A.11** — Phase A close: write `specs/dream_engine/phase_a_close.md` answering Q1/Q2/Q3/Q7 with decision rationale.
- [ ] **M8.A.12** — Commit Phase A: `[M8.A] Schema prep + observability scaffolding (migration 0038)`.

## Phase B — Worker core + 3 jobs

- [ ] **M8.B.1** — Create `src/dream_engine/__init__.py` (empty package marker).
- [ ] **M8.B.2** — Write `src/dream_engine/queries.py` — SQL strings for each job. Keep as `_const` strings so they're testable + readable.
- [ ] **M8.B.3** — Write `src/dream_engine/config.py` — `load_archive_thresholds()` reads operator_preferences for the 3 keys, raises `RuntimeError` on missing key (no silent fallback).
- [ ] **M8.B.4** — Write `src/dream_engine/worker.py` — `JobResult` dataclass, `utility_recompute()`, `dedup_pass()`, `archive_low_utility()`, `main(dry_run: bool)`.
- [ ] **M8.B.5** — Resolve Q4 (top-K for nearest-neighbor query). Document in `specs/dream_engine/phase_b_close.md`.
- [ ] **M8.B.6** — Resolve Q5 (cosine vs L2 similarity). Document in phase_b_close Q5.
- [ ] **M8.B.7** — Resolve Q6 (does archival fire readme_dirty trigger). Verify by running an UPDATE on a test row and watching `pg_notify` payload. Document.
- [ ] **M8.B.8** — Write `tests/dream_engine/__init__.py`.
- [ ] **M8.B.9** — Write `tests/dream_engine/conftest.py` — fixtures: `dream_engine_test_db` (re-applies 0028a + 0030 + 0037 + 0038 if missing per CLAUDE.md drift watchdog), `seeded_lessons_for_dedup`, `seeded_lessons_for_archive`.
- [ ] **M8.B.10** — Write unit tests `tests/dream_engine/test_worker.py`:
  - utility_recompute calls SQL function and returns rows_affected
  - dedup_pass produces correct INSERT statements + ON CONFLICT
  - archive_low_utility builds correct WHERE clause from preferences
  - JobResult shape on error
  - main() partial-success path (one job raises, others complete)
- [ ] **M8.B.11** — Write slow integration test `tests/dream_engine/test_e2e.py` (@pytest.mark.slow):
  - SC2 verification: spot-check utility_score after recompute matches formula
  - SC3 verification: cross_pollination_queue row inserted with proposed_by='dream_engine_dedup'; second run is no-op (UNIQUE conflict)
  - SC4 verification: lesson crossing threshold gets status='archived'
  - SC5 verification: deliberate fault → partial status + other jobs complete
- [ ] **M8.B.12** — Run `PYTHONPATH=src pytest tests/dream_engine/ -v` — all green (unit + slow).
- [ ] **M8.B.13** — Run `mypy src/dream_engine/` — clean.
- [ ] **M8.B.14** — Manual smoke test: `PYTHONPATH=src python -m dream_engine.worker --dry-run` against `pretel_os_test` — output matches expectations.
- [ ] **M8.B.15** — Phase B close: `specs/dream_engine/phase_b_close.md` documenting Q4/Q5/Q6 + any spec deltas.
- [ ] **M8.B.16** — Commit Phase B: `[M8.B] Dream Engine worker + 3 jobs + tests`.

## Phase C — systemd integration + production dry-run

- [ ] **M8.C.1** — Write `infra/systemd/pretel-os-dream-engine.service` — Type=oneshot, EnvironmentFile=$HOME/.env.pretel_os, ExecStart=python -m dream_engine.worker.
- [ ] **M8.C.2** — Write `infra/systemd/pretel-os-dream-engine.timer` — OnCalendar=*-*-* 02:00 America/New_York, Persistent=true, RandomizedDelaySec=60.
- [ ] **M8.C.3** — Install user units: `cp infra/systemd/pretel-os-dream-engine.* ~/.config/systemd/user/`.
- [ ] **M8.C.4** — Reload + enable timer: `systemctl --user daemon-reload && systemctl --user enable --now pretel-os-dream-engine.timer`.
- [ ] **M8.C.5** — Verify timer registered: `systemctl --user list-timers | grep dream-engine` shows next firing at 02:00 ET.
- [ ] **M8.C.6** — Manual dry-run against PRODUCTION: `systemctl --user start pretel-os-dream-engine.service` *with worker invoked in --dry-run mode* (one-time override). Capture stdout to `/tmp/dream_engine_dry_run_$(date +%s).log`. Operator review required before going live.
- [ ] **M8.C.7** — Operator review of dry-run output. Sign off in commit message of M8.C.10.
- [ ] **M8.C.8** — Live first manual run (no --dry-run): `systemctl --user start pretel-os-dream-engine.service`. Verify `dream_engine_runs` row inserted, status=success.
- [ ] **M8.C.9** — Verify SC1–SC4 against production data after first run:
  - SC1: dream_engine_runs row present
  - SC2: spot-check 3 tools_catalog utility_scores
  - SC3: count cross_pollination_queue rows with proposed_by='dream_engine_dedup'; document the burst size
  - SC4: spot-check any newly-archived lessons; if zero, that's expected for a young corpus
- [ ] **M8.C.10** — Commit Phase C: `[M8.C] systemd timer + dry-run + first live run`.

## Phase D — 7-day production observation

- [ ] **M8.D.1** — Day 1 — verify timer fired: `journalctl --user -u pretel-os-dream-engine.service --since "yesterday 02:00" --until "yesterday 02:30"` shows clean exit. `dream_engine_runs` row present.
- [ ] **M8.D.2** — Day 2 — same check. Cross_pollination_queue increment small (idempotency proof).
- [ ] **M8.D.3** — Day 3 — same check.
- [ ] **M8.D.4** — Day 4 — same check.
- [ ] **M8.D.5** — Day 5 — same check.
- [ ] **M8.D.6** — Day 6 — same check.
- [ ] **M8.D.7** — Day 7 — same check. SC7 satisfied: 7 consecutive runs, no failures, no cost anomalies (verify via `v_daily_cost_by_purpose`).
- [ ] **M8.D.8** — Commit Phase D: `[M8.D] 7-day observation gate passed`.

## Phase E — Module exit

- [ ] **M8.E.1** — Author `runbooks/module_8_dream_engine.md`:
  - How to manually trigger.
  - How to read `dream_engine_runs` for incident triage.
  - How to tune the 3 archive thresholds via `preference_set`.
  - How to recover from a missed run.
  - 3 audit queries.
- [ ] **M8.E.2** — Update `tasks.md` (root) — Module 8 row marked complete, link to runbook.
- [ ] **M8.E.3** — Update `tools.md` if any new MCP tool was added (none planned in fase 1).
- [ ] **M8.E.4** — Update `SESSION_RESTORE.md §13` (last session snapshot).
- [ ] **M8.E.5** — Tag `module-8-complete` on the closing commit (operator authorizes push).
- [ ] **M8.E.6** — Final commit: `[M8.E] Module 8 (Dream Engine fase 1) complete — runbook + tag`.

---

## Out-of-band items (track here, do later)

- [ ] **M8.fu1** — Stale schema-default cleanup: `cross_pollination_queue.proposed_by DEFAULT 'reflection_worker'` is a leftover from migration 0010. Optionally migrate the default to `'manual'` or DROP DEFAULT entirely once M8 is stable. Low priority.
- [ ] **M8.fu2** — If first-week dedup pass burst is large (>50 rows), evaluate raising similarity threshold from 0.95 to 0.97 in queries.py. Document via plan §6 tuning playbook.
- [ ] **M8.fu3** — Consider `report_satisfaction` on `dream_engine_runs` rows from operator (post-archival, post-merge) to feed back into utility scoring. Fase 2.

---

**For atomic completion tracking:** check the box and commit per the SDD convention "one task = one commit, prefix `[M8.X.Y]`." The phase-close commits (`M8.A.12`, `M8.B.16`, etc.) collect the phase-close documents.
