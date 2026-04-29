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

## Module 4 — router

- [x] M4.T1 SDD trinity (commits 3589673, 7ec4764, etc.)
- [x] Phase A — Classifier (closed; live eval bucket 1.0, complexity 0.8)
- [ ] Phase B — Layer Loader (blocked on Module 0.X)
- [ ] Phase C — RAG activation
- [ ] Phase D — Telemetry & orchestrator
- [ ] Phase E — Fallback classifier
- [ ] Phase F — Tuning

Per-module detail: `specs/router/tasks.md`

## Module 0.X — knowledge_architecture

- [x] M0X.T1 spec.md (commit 8a6cf7d)
- [x] M0X.T2 plan.md (commit ff81538)
- [x] M0X.T3 tasks.md (commit c4b4649)
- [x] M0X.T4.A — Phase A schema migrations (closed; 7 migrations applied; commits db73a67 through bc4e5df)
- [x] M0X.T4.B — Phase B SOUL.md (closed; commit pending)
- [x] M0X.T4.C — Phase C MCP tools (18 tools — count corrected from 17 due to best_practice_rollback split)
- [ ] M0X.T4.D — Phase D tests
- [ ] M0X.T4.E — Phase E docs + close-out + tag

Per-module detail: `specs/module-0x-knowledge-architecture/tasks.md`

## Module 5 — telegram_bot

- [ ] SDD trinity (M5.T1: spec, plan, tasks per `runbooks/sdd_module_kickoff.md`)
- [ ] Implementation

Per-module detail: TBD (created at M5 kickoff per `runbooks/sdd_module_kickoff.md`)

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
