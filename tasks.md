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

## Module 5 — telegram_bot (COMPLETE 2026-04-29)

- [x] **M5.T1** SDD trinity at `specs/telegram_bot/` (commit `7488589`)
- [x] **M5.T2** Phase A — Review MCP tools (commit `04cae82`; 5 new tools + 13 tests; all green)
- [x] **M5.T3** Phase B — Bot skeleton + core commands (commits `14bfd19`, `e5c02e3`, `5d7e2ba`; /start /help /save /idea /status + operator guard + systemd unit; 10 handler tests; ~$0 cost)
- [x] **M5.T4** Phase C — Review flows (commit `c873488`; /review_pending with [✅][❌][⏭] inline buttons + reject-reason follow-up; /cross_poll_review with [✅][❌] inline buttons; 11 mocked tests; ~$0 cost)
- [x] **M5.T5** Phase D — Voice (Whisper) + session tracking (commits `4239b69`, `ceb2126`; voice handler with mocked-Whisper tests, session middleware + idle-close loop, 11 tests; ~$0 cost in tests, ~$0.003 per real voice clip in production; unblocks M4 D.2 Q8 deferral)
- [x] **M5.T6** Phase E — Module 5 gate + cleanup + `module-5-complete` tag (this commit; 45/45 tests across full M5 surface; mypy clean across 15 source files; tag created + pushed per operator authorization)

Per-module detail: `specs/telegram_bot/tasks.md` (all M5.A–M5.E rows `[x]`).
Tag: `module-5-complete` on this commit (pushed).

## Module 6 — reflection_worker

- [ ] SDD trinity (M6.T1)
- [ ] Implementation
- [ ] Production deployment (unblocked by M7.5 — lessons / tasks / decisions now carry `project_id` FK so M6 outputs are queryable per project)

Per-module detail: TBD (created at M6 kickoff per `runbooks/sdd_module_kickoff.md`)

## Module 7 — skills_migration (IN PROGRESS — phases A+B closed, ad-hoc per-phase briefs)

- [ ] SDD trinity (M7.T1) — **deferred:** module is being driven via per-phase operator briefs (no canonical M7 trinity yet). When the remaining phases are scoped, retro-build the trinity to capture the running record.
- [x] **M7.A** — Generic skills + Scout overlay (closed 2026-04-29, commit `3a41d7f`):
  `skills/sdd.md` (455 lines) + `skills/vett.md` (655 lines, organization-agnostic) + `buckets/scout/skills/vett_scout_context.md` (182 lines, L2 overlay) + `buckets/scout/README.md` rewritten (52 lines). SQL fallback `migrations/0032_seed_skills_sdd_vett.sql` registers both skills in `tools_catalog` (MCP `register_skill` was unavailable mid-task → SQL form on disk, idempotent `ON CONFLICT DO UPDATE`; **NOT yet applied to either DB** — see "Open follow-ups").
- [x] **M7.B** — `create_project` MCP tool + live `projects` registry + router unknown-project hint (closed 2026-04-30, commit `fbe3a66`):
  Migration `0033_projects_table.sql` applied to `pretel_os` and `pretel_os_test` (live registry distinct from `projects_indexed`; bucket+slug unique). `src/mcp_server/tools/projects.py` ships `create_project` / `get_project` / `list_projects`. `router.py` adds `_check_project_exists()` and surfaces `unknown_project` hint in the bundle response when the classifier picks a (bucket, project) with no registry row and no L2 README on disk. 8/8 tests in `tests/mcp_server/tools/test_projects.py` (all `@pytest.mark.slow`, inline fixtures). main.py registers the three tools; service restarted clean on 2026-04-30.
- [ ] **M7.C** — TBD scope. Candidates from plan §6 Module 7: migrate the remaining 5 skills (`scout_slides`, `declassified_pipeline`, `forge`, `marketing_system`, `finance_system`); write the 3 new skills (`client_discovery`, `sow_generator`, `mtm_efficiency_audit`); apply migration 0032 to populate embeddings for sdd+vett; ship `runbooks/module_7_skills.md`. Operator picks scope at M7.C kickoff.
- [ ] **M7 exit gate** (per plan §6 Module 7): all 10 skills exist + each registered in `tools_catalog` with embeddings + each under L3 4K-token budget + per-bucket retrieval test passes top-3 + `runbooks/module_7_skills.md` shipped.

Per-module detail: TBD. Open follow-ups carried forward:
- **M7.A.fu1** — Apply `migrations/0032_seed_skills_sdd_vett.sql` to `pretel_os` (and `pretel_os_test`). Will register sdd+vett rows in `tools_catalog`; trigger `trg_tools_emb` queues embedding generation; auto-index worker fills `embedding`. Required before M7 exit gate.
- **M7.A.fu2** — Reconcile `infra/db/migrate.py`: it stores `path.stem` (e.g. `0024_tasks`) as `version` while older rows use 4-digit prefixes (`0024`). Re-running the runner re-attempts already-applied migrations. Sidestep used in M7.B was direct `psql -1 -f` + manual `INSERT INTO schema_migrations` with prefix-only version. Worth a one-shot reconciliation migration that backfills the missing stems. Captured in DECISIONS as "deferred fix" and as `LL-INFRA-001` in LESSONS_LEARNED.

## Module 7.5 — awareness_layer (COMPLETE 2026-04-30)

- [x] **M7.5.AB** — Migration 0034 + readme renderer + LISTEN/NOTIFY consumer (commit `ebd51f0`):
  Schema migration adding `project_id` FK on lessons / tasks / decisions, `archived_at` + `archive_reason` + `applicable_skills` on projects, `trigger_keywords` on tools_catalog. 4 NOTIFY trigger functions (`project_lifecycle`, `readme_dirty_bucket`, `readme_dirty_project`, `catalog_changed`) attached across the 5 affected tables. `src/awareness/readme_renderer.py` (idempotent parse + render + sync regenerate_*; preserves operator notes between `<!-- pretel:notes -->` markers). `src/awareness/readme_consumer.py` (async LISTEN on `readme_dirty`, 30s debounce, dispatch via `asyncio.to_thread`). `infra/systemd/pretel-os-readme.service` active. Two new MCP tools: `regenerate_bucket_readme` + `regenerate_project_readme`.
- [x] **M7.5.C** — Router awareness injection + new tools + project_id population (commit `6e64b39`):
  `router.py` adds `_get_skills_for_bucket` + `_get_active_projects_for_bucket`; `available_skills` + `active_projects` injected into ContextBundle; schema updated. `create_project` calls `regenerate_bucket_readme` post-INSERT (best-effort). New `archive_project` MCP tool emits lifecycle notify and regenerates bucket README inline. New `recommend_skills_for_query` MCP tool (keyword + utility scoring per Q5). `task_create` + `decision_record` resolve `project_id` from (bucket, project) with no-silent-fallback warning on miss. `save_lesson` signature unchanged; project_id stays NULL until M6 wires its own write path.
- [x] **M7.5.D** — `skills/skill_discovery.md` + utility seeding + initial README regeneration (commit `81c52bf`):
  222-line skill teaching LLM the discovery cycle (3 worked examples, anti-patterns, references). Migration 0035 seeds tools_catalog with utility_score per Q6 + trigger_keywords for vett/sdd/skill_discovery + skill_discovery row at utility=1.0; idempotent ON CONFLICT. All 3 bucket READMEs (personal/business/scout) regenerated; legacy hand-authored content preserved verbatim under operator-notes blocks via the one-time D.0 wrap.
- [x] **M7.5.E** — Phase E gate: tests + 7 success criteria + cleanup + tag candidate (this commit):
  6 renderer tests + 3 slow consumer tests + 6 awareness-tool tests; existing test_e2e.py (6 tests) and test_create_project_happy_path updated with awareness assertions; 7 success criteria all PASS — see `runbooks/m7_5_demo.md`. Tag candidate `module-7-5-complete` (operator-driven push).

Per-module reference: rationale + plan + atomic_tasks + 4-run code briefings live at `~/Downloads/M7_5_*.md`. Demonstration runbook: `runbooks/m7_5_demo.md`. No formal SDD trinity (per-phase operator briefs same pattern as Module 7).

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
