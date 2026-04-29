# tasks.md — Project milestones

**Status:** Live milestone tracker
**Audience:** Operator picking next thing across modules

This file tracks milestone-level status across all modules. Atomic tasks (the kind with checkbox per migration index, per code function, per test) live in per-module SDD trinity at `specs/<module>/tasks.md`.

**Convention:** Every module starts its life with an SDD trinity at `specs/<module>/{spec.md, plan.md, tasks.md}` BEFORE first line of code. This file's milestone for that module is one line: status + link to per-module tasks.md. See `runbooks/sdd_module_kickoff.md` for the procedure.

Completed atomic detail is archived to `tasks.archive.md` when a module phase closes.

---

## Module 1 — infra_migration

- [x] Module 1 complete (tag `module-1-complete`)

## Module 2 — data_layer

- [x] Module 2 complete (tag `module-2-complete`)
- [x] Setup gaps documented (commit a507a86, runbooks/module_2_data_layer.md)
- [x] notify_missing_embedding polymorphic CASE bug fixed (commit cb56311, migration 0028a)

## Module 3 — mcp_server_v0

- [x] Module 3 complete (tag `module-3-complete`)

## Module 4 — router (COMPLETE 2026-04-29)

- [x] M4.T1 SDD trinity (commits 3589673, 7ec4764, etc.)
- [x] Phase A — Classifier (closed 2026-04-28; live eval bucket 1.0, complexity 0.8)
- [x] Phase B — Layer Loader (closed 2026-04-29; commits d31c8d7..97a67d6; 103 fast + 3 slow tests, mypy clean across 16 router files)
- [x] Phase C — Invariant violation detection (closed 2026-04-29; commits 51da98f, 1cf95f8, 0292247, 7b6f926; re-scoped per M4.C-rescope — source priority moved to consumer per contract §10; 12 tests, 6 invariant checks registered, Scout denylist deferred per Q3)
- [x] Phase D + E — Telemetry, orchestrator, fallback classifier (closed 2026-04-29; commits c5e1f11..8bda98d; INSERT-early telemetry per Q2; `router.get_context()` async wires classify→assemble→detect→log; 19 tests in D.4: 8 telemetry + 5 fallback + 6 e2e at ~$0.018; 3 audit queries from spec §9.3 saved to `runbooks/router_audit_queries.sql`)
- [x] M4.T9 — Module 4 exit (closed 2026-04-29 commit `bf3807e`; plan §10 gate verified 9/10 ✓ + 1 partial — bullet 8 latency provider-variance dependent; `runbooks/module_4_router.md` rewritten as consolidated module runbook; `runbooks/router_tuning.md` ships F.1.1 baseline + 5 tuning queries)
- [ ] Phase F — Tuning (post-30-day, ongoing — no exit gate; queries shipped in `runbooks/router_tuning.md`)

Per-module detail: `specs/router/tasks.md` (full atomic tree, all M4 rows
[x] except E.3.2 / D.6.2 phase-tag rows which are operator-driven).
Architecture decision trackers: `specs/router/phase_b_close.md`,
`phase_c_close.md`, `phase_d_close.md` (Q1-Q9 per phase).
Tag candidates (operator-driven): `phase-b-complete` on 97a67d6,
`phase-c-complete` on 7b6f926, `phase-e-complete` on c5e1f11,
`phase-d-complete` on 8bda98d, `module-4-complete` on bf3807e.

## Module 0.X — knowledge_architecture

- [x] M0X.T1 spec.md (commit 8a6cf7d)
- [x] M0X.T2 plan.md (commit ff81538)
- [x] M0X.T3 tasks.md (commit c4b4649)
- [x] M0X.T4.A — Phase A schema migrations (closed; 7 migrations applied; commits db73a67 through bc4e5df)
- [x] M0X.T4.B — Phase B SOUL.md (closed; commit pending)
- [x] M0X.T4.C — Phase C MCP tools (18 tools — count corrected from 17 due to best_practice_rollback split)
- [x] M0X.T4.D — Phase D tests (closed; 47 tests green, coverage ≥80% on all 5 M0.X tool files)
- [x] M0X.T4.E — Phase E docs + close-out + tag (commits `9cbc639`–`module-0x-complete` chain; layer_loader_contract.md frozen, DATA_MODEL/INTEGRATIONS/SESSION_RESTORE/spec drift fixes shipped; tag created locally, pending operator-approved push)
- [x] **Module 0.X COMPLETE** — knowledge architecture shipped, M4 Phase B unblocked

Per-module detail: `specs/module-0x-knowledge-architecture/tasks.md`

## Module 5 — telegram_bot

- [x] **M5.T1** SDD trinity at `specs/telegram_bot/` (this commit)
- [x] **M5.T2** Phase A — Review MCP tools (5 new tools + 13 tests; all green)
- [ ] **M5.T3** Phase B — Bot skeleton + core commands (/start, /save, /idea, /status, systemd)
- [ ] **M5.T4** Phase C — Review flows (/review_pending, /cross_poll_review)
- [ ] **M5.T5** Phase D — Voice (Whisper) + session tracking (unblocks M4 D.2 Q8)
- [ ] **M5.T6** Phase E — Module 5 gate + cleanup + `module-5-complete` tag

Per-module detail: `specs/telegram_bot/tasks.md`

## Module 6 — reflection_worker

- [ ] SDD trinity (M6.T1)
- [ ] Implementation

Per-module detail: TBD (created at M6 kickoff per `runbooks/sdd_module_kickoff.md`)

## Module 7 — skills_migration

- [ ] SDD trinity (M7.T1)
- [ ] Implementation (10 skills + 3 new)

Per-module detail: TBD (created at M7 kickoff per `runbooks/sdd_module_kickoff.md`)

## Module 8 — lessons_migration

- [ ] SDD trinity (M8.T1)
- [ ] Implementation (89 lessons + 12 ideas)

Per-module detail: TBD (created at M8 kickoff per `runbooks/sdd_module_kickoff.md`)

---

## Recurring tasks

These are not module tasks. They happen in the background once the relevant module is live.

### Weekly review ritual (Sundays)

- [ ] (Recurring) `/review_pending` in Telegram — walk through new lessons.
- [ ] (Recurring) `/cross_poll_review` — apply or dismiss cross-pollination proposals.
- [ ] (Recurring) Check `control_registry` for overdue controls.
- [ ] (Recurring) Review Dream Engine's weekly YAML export (in `exports/`) — scan for patterns.

### Monthly review ritual

- [ ] (Recurring) UptimeRobot monthly report review; update `control_registry.uptime_review.last_completed_at`.
- [ ] (Recurring) Review `v_daily_cost_by_purpose` for the month — look for cost anomalies.
- [ ] (Recurring) Scan `ideas` table for items to promote.

### Quarterly review ritual

- [ ] (Recurring) Scout audit per `control_registry.scout_audit` — review `buckets/scout/` for leaks.
- [ ] (Recurring) Restore drill per `control_registry.restore_drill`.
- [ ] (Recurring) Pricing verification per `control_registry.pricing_verification`.
- [ ] (Recurring) Review CONSTITUTION for amendment candidates — any rules that reality disproved?

### Biannual (every 180 days)

- [ ] (Recurring) Key rotation per `control_registry.key_rotation_*`.

---

**For atomic-level visibility:** open the relevant `specs/<module>/tasks.md`. The per-module tasks.md has every checkbox down to "create idx_X on column Y."

**For completed history:** see `tasks.archive.md` or `git log`.
