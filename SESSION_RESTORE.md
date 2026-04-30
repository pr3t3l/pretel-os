# SESSION_RESTORE.md — pretel-os

**Read this first if you are an LLM coming into this project.**
**Read this first if you are the operator opening a new chat.**

This file is the bridge between chats. It tells you where the project is, what to say, and where to find everything else.

---

## 1. What is pretel-os

A personal cognitive operating system for Alfredo Pretel Vargas (solo developer, Columbia SC, transitioning from W2 at Scout Motors toward freelance). It gives any MCP-compatible client (Claude.ai web, Claude Code, Claude mobile, future MCP clients) hierarchical context, persistent memory, and cross-domain awareness across three buckets: **personal**, **business** (freelance + products), **scout** (W2, data-sensitive).

It replaces a prior stack called OpenClaw. It is **not** an app — it is a substrate that other apps (Claude surfaces, n8n workflows) use.

---

## 2. Current state

**Phase:** Modules 4 + 5 + 7.5 complete. Module 7 in progress (Phases A + B closed via per-phase operator briefs; Phase C scope pending). Module 6 (reflection_worker) implementation pending — production deployment now unblocked by M7.5 closing.

**What is done:**
- Foundation, Modules 1–3.
- M4 Phase A (Router classifier — 19 unit tests + live eval Haiku 4.5: bucket 1.0, complexity 0.8, schema_violations 0). LiteLLM cascade configured. ChatJsonTelemetry captures truncation, cache hits, reasoning tokens, finish_reason classification.
- M0.X SDD trinity (spec/plan/tasks at `specs/module-0x-knowledge-architecture/`).
- M0.X Phase A: 7 migrations applied to production (0024 tasks, 0025 operator_preferences, 0026 router_feedback, 0027 best_practices, 0028 decisions amendment, 0028a notify_missing_embedding fix, 0029 ADR seed + lessons split). 5 ADRs seeded (020-024). 4 misclassified lessons archived with cross-table pointers. Schema audit at `migrations/audit/0029_post_state.md`.
- M0.X Phase B: `SOUL.md` shipped to L0 (operator voice contract). `AGENTS.md` updated with SOUL.md in read order. Spec drift #4 (L0 budget interpretation) fixed in same commit.
- M0.X Phase C: 18 MCP tools across 5 files (tasks, operator_preferences, decisions, router_feedback, best_practices).
- M0.X Phase D: 47 tests, coverage ≥80% per file.
- M0.X Phase E: `layer_loader_contract.md` frozen as M4 Phase B input contract. Tag `module-0x-complete` pushed. ADR-025 added registering the contract as architectural commitment.
- M0X.0030: `notify_missing_embedding` trigger attached to `best_practices` (replaces the manual `pending_embeddings` INSERT workaround in `best_practice_record`). Closes the only known M0.X-era workaround in production.
- M4 Phase B (Layer Loader): all 9 atomic groups shipped 2026-04-29. 5 sync loaders (L0..L4) per contract §3.1-§3.5, async `assemble_bundle` orchestrator wiring `embed()` + loaders + `summarize_oversize` + cache, in-memory `LayerBundleCache` with LISTEN/NOTIFY invalidation via migration 0031 trigger function. 103 fast + 3 slow tests, mypy clean across 16 router source files. Architecture decisions tracked in `specs/router/phase_b_close.md`. Tag candidate: `phase-b-complete` at commit `97a67d6`.
- M4 Phase C (Invariant violation detection — post-rescope): `detect_invariant_violations(bundle)` scans every `ContextBlock` against 6 registered invariant checks (3 agent-rule, 1 git/DB boundary, 1 budget ceiling, 1 Scout stub). 12 tests, mypy clean. Scout denylist deferred (Q3). Architecture decisions in `specs/router/phase_c_close.md`.
- M4 Phase D + E (Telemetry + orchestrator + fallback classifier): full pipeline shipped 2026-04-29. 6 atomic groups (D.0-D.5) per `specs/router/phase_d_close.md`. `router.get_context()` async orchestrator wires classify → assemble_bundle → detect_invariant_violations → telemetry, with try/finally degraded handling per spec §10. 6 telemetry functions (start_request + 5 log_*) write spec §9.1/§9.2 columns; INSERT-early per Q2. MCP tool wrappers `tools/context.py` (replaces Module-3 stub) + `tools/report_satisfaction.py`. 19 D.4 tests green: 8 telemetry + 5 fallback integration + 6 e2e (~$0.018 actual cost). 3 audit queries from spec §9.3 saved to `runbooks/router_audit_queries.sql`. Q5 Q-decisions captured in `phase_d_close.md`.
- M4 exit (M4.T9.x): plan §10 exit gate verified (9/10 ✓, bullet 8 partial — provider-variance pushes individual HIGH-complexity turns to ~3.5s vs the 2s gate; warm steady-state is ~1s; 5s `ClassifierTimeout` triggers fallback to protect UX). `runbooks/module_4_router.md` rewritten as consolidated module runbook (5 sections + gate verification table + file-to-responsibility map). `runbooks/router_tuning.md` (F.1.1) ships 3 baseline §9.3 queries + 5 Phase F tuning queries. Tag candidate `module-4-complete` (operator-driven).
- M5 Module 5 — telegram_bot (COMPLETE 2026-04-29). Mobile-first capture + review surface: 7 commands (`/start /help /save /idea /status /review_pending /cross_poll_review`) + voice handler (Whisper `whisper-1` ES). Bot imports MCP tools directly per Q2 (no HTTP/MCP-protocol round-trip). 5 new MCP tools shipped in Phase A (`list_pending_lessons`, `approve_lesson`, `reject_lesson`, `list_pending_cross_pollination`, `resolve_cross_pollination`) — benefits Claude.ai too. `session_middleware` populates `conversation_sessions` per turn — unblocks the M4 D.2 Q8 deferral that left `_get_session_excerpt()` returning `""`. Idle-close loop (300s interval, 10-min idle) closes stale sessions via `app.bot_data` lifecycle hooks. 45 tests (32 bot + 13 review tools) green; ~$0 in CI, ~$0.003/30s in production Whisper smoke. Tag `module-5-complete` pushed.
- M7.A Generic skills + Scout overlay (commit `3a41d7f`, 2026-04-29). `skills/sdd.md` (455 lines) and `skills/vett.md` (655 lines, organization-agnostic with `{the organization}` / `{client_tech_stack}` / `{client_governance_team}` variable bindings — verified `grep -i scout|zscaler|databricks|kubernetes|eks|livekit|pinecone` returns 0 matches). Scout L2 overlay at `buckets/scout/skills/vett_scout_context.md` (182 lines, supplies tech stack + governance + compliance + data taxonomy + scoring deltas + presentation visuals). `buckets/scout/README.md` rewritten as bucket manifest. SQL fallback `migrations/0032_seed_skills_sdd_vett.sql` registers sdd + vett in `tools_catalog` (idempotent ON CONFLICT DO UPDATE) — **NOT yet applied** to either DB; MCP `register_skill` returned "Session not found" mid-task and the operator chose to ship the SQL form rather than rabbit-hole into MCP debugging.
- M7.B `create_project` MCP tool + live `projects` registry + router unknown-project hint (commit `fbe3a66`, 2026-04-30). Migration `0033` applied to `pretel_os` and `pretel_os_test` directly via `psql -1 -f` + manual prefix-only INSERT into `schema_migrations` (the `infra/db/migrate.py` runner has a pre-existing version-format bug; documented in `LL-INFRA-001`). New tools `create_project / get_project / list_projects` in `src/mcp_server/tools/projects.py`; main.py wiring + service restart clean. Router helper `_check_project_exists()` and conditional `unknown_project` key in the bundle response (only set when classifier picks bucket+project and neither registry nor on-disk README matches). 8/8 slow tests green; mypy clean.
- M7.5 (Awareness layer, COMPLETE 2026-04-30): four commits across four runs.
  - **RUN 1 / M7.5.AB** (`ebd51f0`): migration 0034 (`project_id` FK on lessons/tasks/decisions; `archived_at`/`archive_reason`/`applicable_skills` on projects; `trigger_keywords` on tools_catalog; 4 NOTIFY trigger functions). `src/awareness/readme_renderer.py` (idempotent parse/render with stable-timestamp logic and atomic write); `src/awareness/readme_consumer.py` (async LISTEN on `readme_dirty`, 30s debounce, 5s scan); `src/mcp_server/tools/awareness.py` exposes `regenerate_bucket_readme` + `regenerate_project_readme` MCP tools. systemd unit `pretel-os-readme.service` active.
  - **RUN 2 / M7.5.C** (`6e64b39`): Router `_get_skills_for_bucket` + `_get_active_projects_for_bucket` injected into ContextBundle; schema updated. `create_project` regenerates bucket README post-INSERT (best-effort). New `archive_project` MCP tool. New `recommend_skills_for_query` MCP tool (keyword + utility scoring). `task_create` + `decision_record` resolve `project_id` from `(bucket, project)` with no-silent-fallback warning on miss.
  - **RUN 3 / M7.5.D** (`81c52bf`): `skills/skill_discovery.md` (222 lines, 3 worked examples). Migration 0035 seeds `tools_catalog`: skill_discovery row at utility=1.0; vett (0.85) and sdd (0.90) with trigger_keywords; 26 tool rows with utility_score per Q6 (idempotent ON CONFLICT). Initial regeneration of all 3 bucket READMEs (personal/business/scout) with the one-time D.0 wrap preserving legacy content under operator-notes blocks.
  - **RUN 4 / M7.5.E** (this commit): tests/awareness/ (6 renderer + 3 slow consumer = 9), tests/mcp_server/tools/test_awareness.py (6 tests). test_e2e.py + test_create_project_happy_path updated with awareness assertions. 7 success criteria all PASS — `runbooks/m7_5_demo.md` (419 lines). Tag candidate `module-7-5-complete` (operator-driven push).
  Reference docs: `~/Downloads/M7_5_{awareness_layer_rationale,plan,atomic_tasks,code_briefings}.md`. Demo runbook: `runbooks/m7_5_demo.md`. The `pretel-os-readme.service` is now production infrastructure — any future write that should regenerate READMEs depends on it being active.
- Tasks structure migrated to milestone-only at root with per-module trinity rule documented in `runbooks/sdd_module_kickoff.md`.
- 4 spec drifts caught at scratch test time (LL-M0X-001): request_id type, scope DEFAULT, lessons.status enum, L0 budget interpretation. Zero production damage.

**What is not done:**
- **Module 6 (Reflection worker) production deployment** — code committed; M7.5 unblock is now done so M6 outputs (lessons + cross_pollination_queue rows) will carry `project_id` FKs and be queryable per project. This is the new top-of-stack.
- **Module 7 Phase C** — operator picks scope at next kickoff. Candidates: migrate the 5 remaining skills (`scout_slides`, `declassified_pipeline`, `forge`, `marketing_system`, `finance_system`); write the 3 new ones (`client_discovery`, `sow_generator`, `mtm_efficiency_audit`); apply migration `0032` to populate `tools_catalog` rows + embeddings for sdd+vett; ship `runbooks/module_7_skills.md` (required for the Module 7 exit gate per plan §6).
- Module 8 (lessons migration).
- M4 Phase F (post-30-day tuning, ongoing — not gated; queries shipped in `runbooks/router_tuning.md`).
- Follow-ups (non-blocking):
  - M4 `5db4bc6f` LayerBundleCache listener wiring (closed 2026-04-29 by commit `8123a82`; verify if any residual remains).
  - Router `_get_session_excerpt()` swap to real `conversation_sessions` query now that M5 populates the table.
  - cost_usd plumbing from LiteLLM proxy to `llm_calls`.
  - **M7.A.fu1** — apply `migrations/0032_seed_skills_sdd_vett.sql` to `pretel_os` (and `pretel_os_test`); the embedding trigger will queue both rows for the auto-index worker.
  - **M7.A.fu2** — reconcile `infra/db/migrate.py` version-format bug (stem vs prefix). Workaround: direct `psql -1 -f` + manual prefix-only `schema_migrations` INSERT. Captured as `LL-INFRA-001`. Backfill migration to retro-apply prefixes is the cleanest fix.

**Top of stack:** **Module 6 — Reflection worker production deployment.** M7.5 closed end-to-end (4 commits, tag candidate `module-7-5-complete` pending operator push); the FK linkage M6 needs is in place (migration 0034 + RUN 2 C.5 wiring) and demonstrated end-to-end in `runbooks/m7_5_demo.md` criteria #2 + #7. SDD trinity for M6 still pending — kickoff via `runbooks/sdd_module_kickoff.md`. M6 reads `routing_logs` low-confidence clusters / RAG mismatches / repeat queries, `conversations_indexed`, `usage_logs`, and proposes lessons + cross-pollination rows for operator review via M5's already-wired `/review_pending` + `/cross_poll_review`. M6 worker code is committed but NOT running in production.

**Where to find recently-closed module sources-of-truth:**
- Module 4: `runbooks/module_4_router.md`, `runbooks/router_tuning.md`, `runbooks/router_audit_queries.sql`, `specs/router/{spec,plan,tasks,phase_b_close,phase_c_close,phase_d_close}.md`.
- Module 5: `specs/telegram_bot/{spec,plan,tasks}.md`, `infra/systemd/pretel-os-bot.service`, `tests/telegram_bot/`, `tests/mcp_server/tools/test_review_tools.py`.
- Module 7 (in progress, no SDD trinity yet): closure summaries in `tasks.archive.md` (Phase A and Phase B sections, dated 2026-04-29 and 2026-04-30); generic skill files at `skills/{sdd,vett}.md`; Scout overlay at `buckets/scout/skills/vett_scout_context.md`; tool implementations at `src/mcp_server/tools/projects.py`; tests at `tests/mcp_server/tools/test_projects.py`. Open follow-ups in `tasks.md` Module 7 section (M7.A.fu1, M7.A.fu2).
- Module 7.5 (COMPLETE 2026-04-30, no SDD trinity — operator briefs at `~/Downloads/M7_5_{awareness_layer_rationale,plan,atomic_tasks,code_briefings}.md`): migrations at `migrations/{0034_awareness_layer,0035_seed_awareness}.sql`; renderer + consumer at `src/awareness/`; MCP wrappers at `src/mcp_server/tools/awareness.py`; systemd unit at `infra/systemd/pretel-os-readme.service`; tests at `tests/awareness/` + `tests/mcp_server/tools/test_awareness.py`; demo runbook at `runbooks/m7_5_demo.md`; new skill `skills/skill_discovery.md`. Production state: `pretel-os-readme.service` active (the consumer **must** stay running for any write to lessons/tasks/decisions/projects/tools_catalog to project to its bucket README — stopping it leaves READMEs stale until next regenerate).

---

## 3. What to say to the LLM in a new chat

Copy this into the first message of your new chat, after the LLM has read this file:

> I'm continuing work on pretel-os. Read these in order before responding:
>
> 1. `SESSION_RESTORE.md` (this file — for state)
> 2. `CONSTITUTION.md` (for immutable rules)
> 3. `plan.md §2` and `plan.md §5` (for project state and phase gates)
> 4. `tasks.md` — find the first unchecked `[ ]` — that's where I am
>
> Do not suggest alternative architectures. Do not propose new audits unless I explicitly request one. Do not estimate time in hours or days. Match my language (Spanish or English) to what I write.
>
> My next task is: **[copy the first unchecked task from tasks.md here]**.

That's it. No 5-paragraph project re-explanation. The docs are the context.

---

## 4. How to find where you are

Three ways, in order of reliability:

### 4.1 tasks.md (primary)

Open `tasks.md` and search for the first unchecked `[ ]`. That line is exactly where you are. The surrounding 3-5 lines give you local context. The section header tells you which module.

### 4.2 git log (secondary)

```bash
cd ~/dev/pretel-os     # or wherever the repo is
git log --oneline -20
git tag -l 'module-*'
```

The most recent `module-N-complete` tag tells you the last completed phase gate. If no module tag exists yet, you're still in Phase 0 or Pre-Module 1.

### 4.3 control_registry (once Module 2 is live)

```sql
SELECT control_name, last_completed_at, next_due_at,
       CASE WHEN next_due_at < now() THEN 'OVERDUE' ELSE 'OK' END AS status
FROM control_registry;
```

Shows operational controls and their cadence state.

---

## 5. Document map

Where everything lives (paths relative to repo root):

```
pretel-os/
├── CONSTITUTION.md                          # Immutable rules
├── plan.md                                  # Project-wide plan, phase gates
├── tasks.md                                 # Milestone tracker (one line per phase)
├── tasks.archive.md                         # Closed atomic detail (grep convenience + pre-rule snapshot)
├── DECISIONS.md                             # ADR log (020+); legacy 001-019 in PROJECT_FOUNDATION §5
├── SESSION_RESTORE.md                       # This file
├── README.md                                # Repo entry point
├── identity.md                              # L0 operator identity / facts (populated in Module 3)
├── SOUL.md                                  # L0 operator voice / behavior contract (added M0X Phase B)
├── AGENTS.md                                # LLM reading order (updated M0X Phase B for SOUL.md)
│
├── docs/
│   ├── PROJECT_FOUNDATION.md                # Vision, stack, roadmap, ADRs
│   ├── DATA_MODEL.md                        # DB schema (25 tables)
│   ├── INTEGRATIONS.md                      # External services (10 integrations)
│   ├── LESSONS_LEARNED.md                   # Process doc for lessons
│   └── audits/
│       ├── CHANGELOG_AUDIT_PASS_3.md        # 19 audit fixes applied
│       └── prompts/
│           ├── AUDIT_PROMPT_GPT.md
│           └── AUDIT_PROMPT_GEMINI.md
│
├── specs/                                   # Per-module specs (each created at module start)
├── buckets/                                 # L1 content (personal, business, scout)
├── skills/                                  # L3 content (methodologies)
├── templates/                               # SDD templates
├── src/                                     # Code (mcp_server, workers, telegram_bot)
├── migrations/                              # Postgres schema migrations
├── infra/                                   # systemd, hooks, backup, monitoring
├── exports/                                 # Weekly YAML lesson exports (by Dream Engine)
├── runbooks/                                # Per-module operational procedures
└── .env.pretel_os.example                   # Credentials template
```

**Tasks granularity:** root `tasks.md` carries milestone-level status (one line per phase). Atomic detail (one checkbox per migration index / function / test) lives in `specs/<module>/tasks.md`. See `runbooks/sdd_module_kickoff.md` for the rule.

**Credentials** live at `/home/operator/.env.pretel_os` (mode 0600, NOT in the repo).

---

## 6. Health check on entry

If you've been away for more than a few days, run these before resuming work. Each should return a positive signal.

### 6.1 Repo health (always safe to run)

```bash
cd ~/dev/pretel-os
git status                            # expect: clean or known in-progress work
git log --oneline -5                  # last 5 commits should match what you remember
git tag -l 'module-*'                 # which modules are complete?
```

### 6.2 Server health (Module 1+)

```bash
# On the Vivobook, via SSH through Tailscale:
ssh operator@100.80.39.23             # or current Tailscale IP
uptime                                # how long has it been running?
systemctl --user list-units --state=failed   # any services down?
df -h                                 # disk space OK?
docker ps                             # Docker containers running?
```

### 6.3 Database health (Module 2+)

```bash
psql -h localhost -U pretel_os -d pretel_os -f ~/pretel-os/infra/db/health_check.py
```

### 6.4 MCP server health (Module 3+)

```bash
curl -f https://mcp.alfredopretelvargas.com/health
# expect: {"status": "ok", "db_healthy": true}
```

### 6.5 Uptime record (Module 3+)

Log into UptimeRobot dashboard. Review last 30 days. Note the percentage against the SLO target (95% Phase 1-3).

### 6.6 Pending work (Module 5+)

Open Telegram, message the bot:

```
/status
```

Returns 🟢🟡🔴 across all integrations.

```
/review_pending
```

Shows lessons pending operator review.

---

## 7. What to do if something is broken

Order of investigation when the system misbehaves after a gap:

1. **Is the Vivobook up?** `ssh operator@<tailscale-ip>`. If fails → hardware issue, physical check required.
2. **Is the tunnel up?** `curl -f https://mcp.alfredopretelvargas.com/health`. If fails → `sudo systemctl status cloudflared` on the Vivobook.
3. **Is the MCP server up?** `systemctl --user status pretel-os-mcp`. Check logs: `journalctl --user -u pretel-os-mcp -n 100`.
4. **Is the DB up?** `sudo systemctl status postgresql`.
5. **Is n8n up?** `curl -f http://127.0.0.1:5678/healthz` (from the Vivobook or Tailscale).
6. **Is LiteLLM up?** `curl -f http://127.0.0.1:4000/health`.
7. **Is Telegram bot up?** `systemctl --user status pretel-os-bot`.

For each layer, the relevant runbook lives at `runbooks/module_N_*.md`.

**Never debug by guessing.** Always read `journalctl` logs for the offending service before changing anything.

---

## 8. What NOT to change without thought

These decisions are load-bearing. Changing them breaks other decisions. Do not suggest changes to:

- **`text-embedding-3-large` (3072 dims)** — challenged three times in audits and kept. Numbers favor keeping. See ADR-006.
- **Single-table `lessons` with status enum** — contradicting this breaks Module 3 auto-approval, Module 6 lifecycle, Module 8 migration. See `CONSTITUTION §5.1 rule 13`.
- **MCP Router as single gateway** — moving routing to clients breaks portability promise. See `CONSTITUTION §2.2`, `LESSONS_LEARNED LL-ARCH-001`.
- **Git/DB strict boundary** — dual-homing is forbidden. See `CONSTITUTION §2.4`, `LESSONS_LEARNED LL-ARCH-003`.
- **MCP_SHARED_SECRET required from Phase 1** — Option A was chosen explicitly over Tailscale-only. See `INTEGRATIONS §11.1`.
- **Router classifier calls LiteLLM aliases, not Anthropic / OpenAI directly.** The classifier (and `second_opinion`) hit `classifier_default` / `second_opinion_default` on the LiteLLM proxy. Swapping the underlying model is a config change in `~/.litellm/config.yaml`, not a code change. Do not hardwire `model="claude-..."` or `model="gpt-..."` in Router code.
- **`decisions` and `patterns` already exist in DATA_MODEL §5.1 and §5.2.** Module 0.X must NOT propose new tables for these; instead it amends the existing schemas if needed and adds genuinely new tables only (`tasks`, `operator_preferences`, `router_feedback`).

If you think one of these needs reconsideration, it requires a **constitutional amendment** — a full ADR with the specific failure mode documented. Not a casual suggestion mid-chat.

---

## 9. Rules for LLMs in this project

These are excerpts of `CONSTITUTION §9`. The full list is there; these are the operationally critical ones:

1. **Never guess MCP tool parameters.** Call `tool_search` first to get the schema.
2. **Never execute code by reading it.** Use MCP tools that spawn real subprocesses. An LLM simulating a Python script mentally is a violation.
3. **Never fabricate citations.** If a lesson, doc section, or ADR is cited, it must exist at the cited location.
4. **Honor source priority per CONSTITUTION §2.7.** When layers disagree, surface the conflict explicitly.
5. **Never propose changes to the operator's stated preferences.** Spanish responses stay Spanish. Concise stays concise. Terminal-ready code is pasted ready to run.
6. **Never add time estimates to tasks or plans.** Modules ship when their gates pass. Not before, not after.
7. **Never commit `.env*` files.** Never include `sk-ant-`, `sk-proj-`, `sk-litellm-` patterns in code or suggestions.
8. **Respect degraded mode.** When an integration is down, return explicit degraded responses per `CONSTITUTION §8.43`. Do not pretend.
9. **Scout bucket is abstract only.** Never surface or store identifiable employer data. Defense in depth: pre-commit hook + MCP tool filter + DB trigger.

---

## 10. Communication conventions with Alfredo

These live in his user preferences and should carry across chats:

- **Direct and actionable.** Give the command or code first, explain after.
- **Copy-paste ready.** Full commands, not placeholders (unless the placeholder is case-specific).
- **Tell him what to share back.** After a command, say "Share the output" or "Share what you see."
- **Concise for simple things, thorough for complex ones.** One-line answer for yes/no. Full analysis for architecture decisions.
- **Opinions and recommendations required.** Don't present 5 equal options. Say which one you'd pick and why.
- **Honesty over politeness.** If an idea won't work, say why + propose an alternative.
- **Spanish or English — match what he writes.** Don't switch unless he does.
- **No flattery, no filler.** Skip "Great question!" and "Absolutely!"
- **Only failures reported.** Assume success unless he tells you otherwise.
- **Budget-conscious.** Flag cost implications of API calls and model choices.
- **Planning first, then execution.** Think through the approach before implementation.

---

## 11. How this file stays accurate

`SESSION_RESTORE.md` is updated when:

- A module completes (update §2 "Current state").
- A major architectural decision lands (update §8 "What NOT to change").
- An operational pattern crystallizes (update §7 or §10).
- A new integration goes live (update §5 document map, §6 health checks).

If you complete a module but don't update this file, you've broken the bridge. Every chat-ending moment should ask: "is this file still accurate?"

---

## 12. If things feel really stuck

You're not lost — the docs are the context. Specifically:

- **"What was I building?"** → `tasks.md`, first unchecked `[ ]`.
- **"Why did we decide X?"** → `docs/PROJECT_FOUNDATION.md §5` (ADRs) or `docs/LESSONS_LEARNED.md §9` (seed lessons).
- **"What does the schema look like?"** → `docs/DATA_MODEL.md`.
- **"How does X integrate?"** → `docs/INTEGRATIONS.md`.
- **"What are the rules?"** → `CONSTITUTION.md`.
- **"How did we get here?"** → `docs/audits/CHANGELOG_AUDIT_PASS_3.md` for the last round of consolidation.
- **"What's our product offering look like?"** → `docs/PROJECT_FOUNDATION.md §1.4` (8 productized services).

Nothing interesting lives only in a chat. If something mattered, it's in a doc. If it's not in a doc, it doesn't matter yet.

---

## 13. Last-known state snapshot



Last session: 2026-04-27
Last task completed: Module 3 complete (tag module-3-complete, commit 5b39773)
Next task: M4.T1.1
Tailscale IP: 100.94.235.92
Cloudflare Tunnel: pretel-os HEALTHY, mcp.alfredopretelvargas.com
MCP server: 7 tools, open auth (TODO OAuth)
LiteLLM: 2 healthy endpoints (classifier_default, second_opinion_default), both on gemini-2.5-flash
Postgres: password rotated (no longer pretel_os_temp_2026)
n8n: password rotated (no longer changeme_replace_this)
Commits on main: 14
Tags: foundation-v1.0, module-1-complete, module-2-complete, module-3-complete


Last session: 2026-04-28
Last task completed: M4 Phase A complete (commits a4f976b through e59b943)
  - a4f976b: A.4.3 truncation detection + telemetry
  - 4964a7d: A.4.4 deferred to Phase F
  - 4a85fd9: A.5.1 + A.5.2 classifier.py
  - 8b5bf71: A.5.3 request_id parameter
  - e466796: Module 0.X spec draft
  - e59b943: A.6.1 live eval (bucket 1.0, complexity 0.8)
Next task: Revise Module 0.X spec (deduplicate vs existing decisions/patterns
            tables), then write plan.md and tasks.md following SDD trinity.
LiteLLM aliases: classifier_default → claude-haiku-4-5-20251001 (primary),
                  claude-sonnet-4-6-20250929 + gpt-4o-mini (fallbacks)
                  second_opinion_default → claude-sonnet-4-6-20250929 (primary),
                  claude-opus-4-7 + gpt-4o (fallbacks)
Lessons captured this session: 7 (3 Phase A + 1 verbal-acknowledgment anti-pattern
  + 3 deferred-todos: pyproject.toml, prompt-caching, LiteLLM concrete model)
Tags: foundation-v1.0, module-1-complete, module-2-complete, module-3-complete
      (pending: tag module-4-phase-a-complete on e59b943)


Last session: 2026-04-28 (continuation)
Last task completed: M0.X SDD trinity complete (commits 8a6cf7d, ff81538, c4b4649, edf3b66)
  - 8a6cf7d: M0X.T1 spec.md revised, OQ-6 + OQ-2 resolved (best_practices new table)
  - ff81538: M0X.T2 plan.md (5 phases A-E, gates, dependencies)
  - c4b4649: M0X.T3 tasks.md (141 atomic tasks)
  - edf3b66: top-level tasks.md close-out (M0X.T1/T2/T3 marked [x])
Next task: M0X.T4 implementation, starting with M0X.PRE.1-5 (pre-flight)
  then M0X.A.1.x (migration 0024 tasks table)
M0.X scope: 4 new tables (tasks, operator_preferences, router_feedback,
  best_practices) + decisions amendment + SOUL.md + 17 MCP tools
Lessons captured this session: 0 (operator deferred 1 push-policy decision
  to be persisted via decision_record once that tool exists post-Phase C)
Tags: foundation-v1.0, module-1-complete, module-2-complete,
  module-3-complete (pending: module-4-phase-a-complete on e59b943,
  module-0x-complete after Phase E)


Last session: 2026-04-28 (Phase A close)
Last task completed: M0.X Phase A complete — 7 migrations applied to production
  - db73a67: M0X.A.1 migration 0024 tasks
  - 394bf1a: M0X.A.2 migration 0025 operator_preferences
  - fe923a9: M0X.A.3 migration 0026 router_feedback + spec §5.4 amendment (request_id text)
  - 885adba: M0X.A.4 migration 0027 best_practices (HNSW deferred per ADR-024)
  - cb56311: fix M2 — 0028a notify_missing_embedding polymorphic CASE bug
  - acac675: M0X.A.5 migration 0028 decisions amendment + spec §5.2 fix (default 'operational')
  - 40d51cc: M0X.A.6 migration 0029 ADR seed + lessons split + spec §7 fix (status archived)
  - 3e55baf: M0X.A.7 schema audit captured at migrations/audit/0029_post_state.md
  - bc4e5df: M0X.A close-out, all 46 atomic tasks marked [x]
Production state: 25 tables (21 base + 4 new), 5 ADRs (020-024) seeded,
  4 misclassified lessons archived to decisions+tasks with metadata
  cross-pointers, notify_missing_embedding rewritten using IF/ELSIF.
Next task: Phase B — draft SOUL.md, measure L0 token budget, register in AGENTS.md
  (M0X.B.1 through M0X.B.8 in specs/module-0x-knowledge-architecture/tasks.md)
Operator setup gaps documented (runbooks/module_2_data_layer.md):
  - ~/.pgpass for non-interactive psql
  - ALTER ROLE pretel_os CREATEDB
  - Pre-load extensions into template1 (pgvector 0.6.0 not trusted)
Lessons captured this session: 2 new (LL-M0X-001 spec drift, LL-M0X-002
  polymorphic PL/pgSQL CASE bug — see docs/LESSONS_LEARNED.md §9)
Tags: foundation-v1.0, module-1-complete, module-2-complete,
  module-3-complete (pending: module-4-phase-a-complete on e59b943,
  module-0x-phase-a-complete on bc4e5df, module-0x-complete after Phase E)


Last session: 2026-04-28 (Phase B close + tasks structure refactor)
Last task completed: M0.X Phase B complete + Opción B tasks.md restructure
  - 567703f: M0.X Phase A doc reconciliation across 5 long-lived files
  - 12b3d1f: DATA_MODEL stub for 4 new tables + decisions amendment
  - 74f858c: tasks.md migration to milestone-only + tasks.archive.md
  - 167c349: runbooks/sdd_module_kickoff.md (per-module trinity rule)
  - e59f79e: SESSION_RESTORE map + plan.md §6 sync with new tasks.md
  - 26c7189: M0X.B SOUL.md to L0 + spec/plan/ADR-022 budget drift fix
Phase B artifacts:
  - SOUL.md created (324 tok, no per-file cap; ~200 token target was
    aspirational — every section load-bearing)
  - AGENTS.md L0 read order updated: SOUL.md inserted as item 3
  - identity.md unchanged at 1091/1200 tok (only HARD gate, OK)
Spec drift fix #4 (same family as LL-M0X-001):
  - M0.X spec/plan/ADR-022 had asserted "L0 budget 1,200 tokens combined"
  - CONSTITUTION §2.3 actually budgets ONLY identity.md at 1,200 tok
  - CONSTITUTION/AGENTS/SOUL load into L0 without per-file caps
  - All 3 docs corrected in commit 26c7189
Tasks structure now: root tasks.md is milestone-only (115 lines, 1 line
  per module phase). Atomic detail in specs/<module>/tasks.md per
  runbooks/sdd_module_kickoff.md. Pre-rule snapshot preserved verbatim
  in tasks.archive.md (1196 lines). Modules 1-3 closed before the rule;
  M4 + M0.X partial-retrofitted; M5-M8 follow rule from kickoff.
Next task: Phase C — 17 MCP tools across 5 files (tasks.py, decisions.py,
  preferences.py, router_feedback.py, best_practices.py).
Phase C source-of-truth:
  - Spec: specs/module-0x-knowledge-architecture/spec.md §5 (schemas), §6 (tools)
  - Plan: specs/module-0x-knowledge-architecture/plan.md §3 Phase C (deliverables, Gate C)
  - Atomic: specs/module-0x-knowledge-architecture/tasks.md (~38 tasks under C.1-C.6)
  - Constraints: DECISIONS.md ADR-020 (LiteLLM aliases for any chat completion
    — best_practices does not call chat models, only embeddings via OpenAI direct)
    and ADR-024 (HNSW deferred — best_practice_search uses sequential scan)
Lessons captured this session: 0 new (drift #4 same family as LL-M0X-001;
  not a new lesson, just one more incident under the existing one)
Tags: foundation-v1.0, module-1-complete, module-2-complete,
  module-3-complete (pending: module-4-phase-a-complete on e59b943,
  module-0x-phase-a-complete on bc4e5df, module-0x-phase-b-complete on
  26c7189, module-0x-complete after Phase E)


Last session: 2026-04-29 (M0.X Phase E close — Module 0.X COMPLETE, pushed to origin)
Status: knowledge architecture shipped, M4 Phase B unblocked.
Last task completed: M0.X Phase E — tag module-0x-complete pushed; long-lived docs registered
  Phase E commit chain (see `git log 59127aa..HEAD`):
  - 9cbc639 chore: .gitignore .coverage + htmlcov/
  - 469e79e M0X.E.1   layer_loader_contract.md NEW (Phase B input contract frozen)
  - 532581b M0X.E.1.1 contract patch — bundle shape, severity SQL CASE, token method
                      (3 patches from operator review: §10 LayerBundle dataclass,
                       §11 tiktoken cl100k_base, §3.2 mandatory DB-side severity CASE)
  - 5d35835 M0X.E.2   DATA_MODEL.md §5.7-5.10 full DDL + §5.2.1 decisions amendment
                      (folded former §5.11 into §5.2.1 for cleaner pairing)
  - 714d1a9 M0X.E.3   INTEGRATIONS.md §14 — 18 tool entries (5 sources × tool group)
  - 93b1b43 M0X.E.4   SESSION_RESTORE.md §13 update + §14 cleanup
  - 9a94e93 M0X.E.5   spec.md drift fixes — tool count 18, decisions.project NOT NULL note
                      (closed task 80462622 via task_close MCP tool — dogfood)
  - 85188db M0X.E.6   plan.md status complete + tasks.md M0X.* closed
  - 49edc0c M0X.E.7   cross-ref consistency — 2 stale "17 tools" refs → 18
  - (tag)   module-0x-complete annotated, points at 49edc0c, pushed to origin (582e4a3)
  - cc7c87a M0X.E close-out: long-lived docs (README, plan.md root, runbook §20-21,
                      DECISIONS.md ADR-025) + ADR-025 persisted to decisions table
                      via decision_record MCP tool — id 88edd357, embedding generated
                      inline. All 6 ADRs (020-025) now in canonical + queryable form.
M0.X scope shipped (Phases A→E):
  - 4 new tables: tasks, operator_preferences, router_feedback, best_practices
  - decisions amended (+7 columns: scope, applicable_buckets, decided_by,
    tags, severity, adr_number, derived_from_lessons)
  - 6 ADRs total (020-025); ADR-025 added post-tag in cc7c87a registering the
    layer loader contract as a frozen architectural commitment
  - SOUL.md L0 voice file (324 tok)
  - 18 MCP tools across 5 files (Phase C)
  - 47 tests, coverage ≥80% per file (Phase D)
  - layer_loader_contract.md frozen (Phase E) — Phase B reads this
Open follow-up tasks (post-tag, all in `tasks` table):
  - 92cac1b3 — CLOSED 2026-04-29 by M0X.0030 (commit d18a43d).
  - 16d4056e — lessons.py mypy --strict alignment (lower priority)
  - 80462622 — CLOSED in this Phase E (decisions.project NOT NULL doc drift)
Known workarounds in production:
  - RESOLVED 2026-04-29 by migration 0030 (commit d18a43d): the manual
    `INSERT INTO pending_embeddings` in best_practice_record's INSERT
    and UPDATE paths has been removed. trg_best_practices_emb AFTER
    INSERT now handles the queue, mirroring 0019's pattern verbatim.
Next module: M4 Phase B (Layer Loader) — reads
  specs/module-0x-knowledge-architecture/layer_loader_contract.md and
  produces its own spec/plan/tasks per runbooks/sdd_module_kickoff.md.
  The contract is FROZEN as of module-0x-complete; deviations require ADR.
Tags after this push:
  foundation-v1.0, module-1-complete, module-2-complete, module-3-complete,
  module-0x-complete
  (still-pending intermediate tags not created — operator chose to skip
   module-0x-phase-a/b/c/d intermediate tags in favor of the single
   module-0x-complete tag covering A→E end-to-end)


Last session: 2026-04-29 (M0.X close-out follow-ups + M4 Phase B prep)
Status: M0.X workarounds eliminated; tools_catalog populated; Router
  docs aligned with layer_loader_contract.md. M4 Phase B ready to start.
Last task completed: M4.reconcile committed and pushed (commit 8ac5ff1).
Three commits pushed this session, in order:
  - d18a43d M0X.0030: best_practices embedding trigger — replaces manual
            pending_embeddings INSERT workaround in best_practice_record.
            Migration 0030 extends notify_missing_embedding() with a
            best_practices branch + attaches trg_best_practices_emb AFTER
            INSERT (mirrors 0019's pattern verbatim — UPDATE-with-embed=None
            is now a silent no-op for the queue, same as every other table;
            the embedding worker reconciles). Closed task 92cac1b3 via
            task_close MCP tool. 47 Phase D tests still green.
  - 2d07588 scripts: bootstrap_tools_catalog.py — interim seed until M4.
            tools_catalog was empty in prod (0022 is intentionally a no-op
            per its own comment: "Module 4 populates MCP tools"). The empty
            catalog meant tool_search returned [] for every MCP-client
            query. Script uses FastMCP introspection (app.list_tools()) so
            name drift with main.py is auto-detected. Idempotent (ON
            CONFLICT DO UPDATE). Seeded 25 rows on prod, all embedded
            inline. Trade-off: re-embeds all 25 every run (~$0.005)
            because register_tool always re-embeds. Documented in M4
            replacement task.
  - 8ac5ff1 M4.reconcile: align Router spec/plan with M0.X
            layer_loader_contract.md. 6 surgical patches across spec.md
            and plan.md: dual file+DB layer table, Router-no-pre-resolve
            (conflict resolution moved to consumer per contract §10),
            LayerBundle / LayerContent / ContextBlock as canonical types,
            severity SQL CASE rule (contract §3.2), tiktoken cl100k_base
            (contract §11), cache invalidation via LISTEN/NOTIFY (contract
            §6). No code changes. Substantive verifications passed; 4
            cosmetic regex checks failed due to brief-internal off-by-one
            issues, not patch errors (patches applied byte-for-byte per
            brief §3).
Open follow-up tasks added this session (in `tasks` table):
  M6:
  - f9922063 — audit pending_embeddings staleness on UPDATE-with-embed-failure
              across all tables (low priority, before reflection worker prod)
  M4:
  - 1502afac — replace scripts/bootstrap_tools_catalog.py with M4 canonical
              solution (normal priority, during M4 implementation). Includes
              fixes for the re-embed-on-every-run inefficiency.
  - 58903216 — clean up legacy LayerPayload reference in plan.md §5
              Phase C (low priority, when re-scoping Phase C)
  Tool-family scaffolds (low priority, no module assigned — surfaced during
   tools_catalog audit; these tables exist in DATA_MODEL but have no MCP tools):
  - ff2118d0 pattern_*       — code snippets / templates
  - 4d8b00e1 gotcha_*        — anti-patterns
  - 0698a9dc contact_*       — CRM-lite
  - cf623e61 idea_*          — promote-to-task
  - a70f9417 conversation_*  — record / search / summarize
  - 7beb2da0 project_*       — record / state-update / search
Decisions worth surfacing (full reasoning in commit messages):
  - 0030 mirrors 0019's AFTER INSERT verbatim (no UPDATE OF embedding).
    The regression test's UPDATE-path "refined guidance" assertion was
    manual-insert-specific and removed; count-1 no-duplicate assertion
    stays.
  - tools_catalog bootstrap chose Option B (versioned introspection-driven
    script) over A (one-shot) and C (SQL migration). Option B detects
    drift with main.py automatically; tracked for M4 replacement.
  - M4.reconcile patches applied byte-for-byte despite 4 verification
    grep mismatches; fixing the greps would have meant deviating from
    brief's prescribed text.
Next module: M4 Phase B (Layer Loader). Input contract:
  specs/module-0x-knowledge-architecture/layer_loader_contract.md (FROZEN
  per ADR-025). Router spec.md and plan.md now reflect the contract.
  Phase B should produce its own atomic tasks per
  runbooks/sdd_module_kickoff.md.
Lessons captured this session: 0 new (no novel failure mode; 0030 was
  documented gap-closure, bootstrap was prepared option, reconcile was
  mechanical).
Tags unchanged from prior session: foundation-v1.0, module-1-complete,
  module-2-complete, module-3-complete, module-0x-complete.


Last session: 2026-04-29 (M4 Phase B close — Layer Loader complete)
Status: M4 Phase B shipped end-to-end; all 9 atomic groups (B.1–B.9)
  green; tag candidate `phase-b-complete` at commit 97a67d6. Phase C
  unblocked.
Last task completed: M4.B.9 assemble_bundle orchestrator + integration
  tests (commit 97a67d6).
Phase B chain pushed in three sessions:
  1. B.1+B.2 — types.py, _tokens.py, load_l0.py
     (commits 83190af, f4aa9cb, 6195693)
  2. B.3+B.4+B.5 — load_l1, load_l2, load_l3
     (commits d84fb4c, af8f2ef, f04f38c)
  3. B.6 — load_l4 vector search (commit 9fc5139)
  4. B.7+B.8+B.9 — summarize, cache+migration 0031, assemble_bundle
     (commits d31c8d7, fd4dc4a, 97a67d6)
Plus 2 chore commits with Phase A eval result JSONs (dd38850, 6ebd251).
Total Phase B output: ~1900 LoC code + ~2400 LoC tests across 17 router
  source files. 103 fast + 3 slow router tests green. mypy clean
  across the entire router/ directory; no `# type: ignore`.
Migration 0031 applied to prod + test (4 NOTIFY triggers on
  operator_preferences, decisions, best_practices, lessons feeding the
  layer_loader_cache channel).
Architecture decisions tracker: specs/router/phase_b_close.md (Q1-Q4
  + 14 atomic tasks, all marked complete).
Lessons saved this session arc (across the 4 sub-sessions): 2 lessons
  (PROC: brief-as-structure-contract-as-truth, ARCH: L1-vs-L2
  decisions ordering asymmetry) + 1 best_practice
  (convention: EXPLAIN via FORMAT JSON not text grep). All auto-
  approved. See lessons table.
Next module: M4 Phase C — invariant violation detection only (per
  M4.C-rescope commit 2eb963e). Scope reduced from "Source priority
  resolution" because contract §10 moved that to the consumer.
Tags unchanged: foundation-v1.0, module-1-complete, module-2-complete,
  module-3-complete, module-0x-complete. Tag candidate this session:
  phase-b-complete on 97a67d6 (operator-driven creation, not auto).


Last session: 2026-04-29 (M4 Phase C close — invariant detector complete)
Status: M4 Phase C shipped; 6 invariant checks registered (5 per-block
  + 1 per-bundle); 12 tests green in 0.06s; mypy clean across 3 router
  source files. Scout denylist deferred (Q3, stub returns []).
Last task completed: C.5 gate verification + tasks.md cleanup.
Commits pushed this session (Phase C chain):
  - 51da98f C.1: InvariantViolation dataclass + invariants registry skeleton
  - 1cf95f8 C.2: six invariant checks + mention-vs-instruction helper
  - 0292247 C.3 + C.4: detector orchestrator + examples doc + 12 tests
  - 7b6f926 C.5: gate + tasks.md cleanup + SESSION_RESTORE
Phase C output: ~750 LoC code + tests across 4 new router files.
  invariant_detector.py (42 LoC), invariants.py (~260 LoC),
  test_invariant_detector.py (~260 LoC), invariant_examples.md (~183 LoC).
Tags: phase-c-complete on 7b6f926 (operator-driven).
Next: M4 Phase D — Telemetry.


Last session: 2026-04-29 (M4 Phase D + E close — orchestrator + telemetry complete)
Status: M4 Phases D + E shipped end-to-end. Router pipeline integrated
  through `router.get_context()` async orchestrator wiring classify ->
  assemble_bundle -> detect_invariant_violations -> 6 telemetry writes
  per spec §9. INSERT-early strategy per Q2 ensures partial rows
  survive crashes. Fallback classifier (Phase E) bundled as D.0. MCP
  tool wrappers replace the Module-3 stub; report_satisfaction
  registered. 19 D.4 tests green; ~$0.018 actual cost on the e2e run.
  3 audit queries from spec §9.3 saved to runbook + verified live.
Last task completed: D.5 gate verification + tasks.md cleanup +
  SESSION_RESTORE + audit-query runbook.
Commits pushed this session (Phase D + E chain):
  - c5e1f11 D.0: fallback_classifier + 7 tests (Phase E bundled)
  - b33fc15 D.1: telemetry primitives (6 functions, INSERT-early)
  - afea9ff D.2: router.py orchestrator + context_bundle_schema.json
  - a91ef61 D.3: tools/context.py + tools/report_satisfaction.py
  - 7c1f7af D.4: 19 tests (8 telemetry + 5 fallback + 6 e2e)
  - 210e22f hot-fix: 2 false positives in invariant detector
    (NEGATION_TOKENS gap + _LAYER_CEILINGS["L0"] mis-scope)
  - 8bda98d D.5: gate + tasks.md cleanup + audit-query
    runbook + SESSION_RESTORE
Phase D + E output: ~1900 LoC across 7 new files + 1 modified main.py.
  fallback_keywords.py (47), fallback_classifier.py (92),
  test_fallback_classifier.py (58), telemetry.py (273), router.py (397),
  context_bundle_schema.json (136), tools/context.py rewrite (243),
  tools/report_satisfaction.py (112), test_telemetry.py (301),
  test_fallback_integration.py (146), test_e2e.py (285),
  router_audit_queries.sql (~85).
Tags candidate this session (operator-driven): phase-e-complete on
  c5e1f11, phase-d-complete on the D.5 close-out commit.
Next: M4.T9.x — Module 4 exit gate (runbook + module-4-complete tag).


Last session: 2026-04-29 (M4.T9.x — Module 4 exit complete)
Status: Module 4 closed. plan §10 exit gate verified line-by-line:
  9/10 ✓ + 1 partial (bullet 8 per-turn latency < 2s for HIGH:
  warm steady-state ~1s, but provider-variance pushes individual
  turns to ~3.5s — full table in `runbooks/module_4_router.md`).
  Two new runbooks: `module_4_router.md` consolidated (5 sections +
  gate verification + file-to-responsibility map) and
  `router_tuning.md` (3 baseline §9.3 queries + 5 Phase F tuning
  queries). Tag candidate: module-4-complete (operator-driven).
Last task completed: M4.T9.3 — runbook + tasks.md cleanup +
  SESSION_RESTORE update.
Commits pushed this session arc (full Module 4 close):
  - c5e1f11 D.0: fallback_classifier + 7 tests (Phase E bundled)
  - b33fc15 D.1: telemetry primitives (6 functions, INSERT-early)
  - afea9ff D.2: router.py orchestrator + context_bundle_schema.json
  - a91ef61 D.3: tools/context.py + tools/report_satisfaction.py
  - 7c1f7af D.4: 19 tests (8 telemetry + 5 fallback + 6 e2e)
  - 210e22f hot-fix: 2 false positives in invariant detector
  - 8bda98d D.5: Phase D + E gate + tasks.md cleanup + audit-query runbook
  - [this commit hash] M4.T9: Module 4 exit — runbook + tuning + gate verified
Tags candidate this session (operator-driven): module-4-complete
  on this commit.
Next: Module 5 — Telegram bot (writes per-turn content to
  `conversation_sessions`, unblocks the Phase D Q8 session-excerpt
  deferral).


Last session: 2026-04-29 (Module 5 — telegram_bot COMPLETE)
Status: Module 5 closed end-to-end in 6 commits across 5 phases.
  Bot package `src/telegram_bot/` ships 7 commands + voice handler +
  session middleware + idle-close background loop. 5 new MCP review
  tools (`list_pending_lessons`, `approve_lesson`, `reject_lesson`,
  `list_pending_cross_pollination`, `resolve_cross_pollination`) live
  in the MCP server alongside Module 4's existing surface; benefits
  Claude.ai too. 45/45 tests across the full M5 surface (32 bot + 13
  review tools) green; mypy clean across 15 source files. Bot ↔ MCP
  boundary is direct Python imports (no HTTP) per plan Q2.
Last task completed: M5.E gate + cleanup + tag.
Commits pushed this session arc (full Module 5 close):
  - 7488589 M5.T1: SDD trinity for telegram_bot module
  - 04cae82 M5.A.2-A.6: review MCP tools + 13 tests
  - 14bfd19 M5.B.1-B.3: bot skeleton + operator guard + /start /help
  - e5c02e3 M5.B.4-B.7: /save /idea /status + systemd unit
  - 5d7e2ba M5.B.8: 10 mocked handler tests
  - c873488 M5.C: review flows (/review_pending + /cross_poll_review)
  - 4239b69 M5.D.1: voice capture (Whisper)
  - ceb2126 M5.D.2 + D.3: session tracking + idle-close + 6 tests
  - [this commit hash] M5.E: gate + cleanup + tag
Tag created and pushed this session: module-5-complete on this commit
  (operator authorized in the phase-close brief).
Side effect: M4 D.2 Q8 deferral is now technically unblocked —
  `conversation_sessions` is populated for every operator turn from
  Telegram. Router's `_get_session_excerpt()` swap to a real query
  is a small follow-up commit on the Router (not blocking M5 close).
Next: Module 6 — Reflection worker (reads routing_logs +
  conversations_indexed, proposes lessons + cross_pollination_queue
  rows for the operator to triage via M5's /review_pending +
  /cross_poll_review).


Last session: 2026-04-30 (Module 7.5 COMPLETE — 4-RUN arc closed)
Status: M7.5 shipped end-to-end in 4 commits. Tag candidate
  module-7-5-complete pending operator push. M6 (reflection_worker)
  production deployment is now unblocked — the FK linkage M6 needs
  (lessons.project_id / tasks.project_id / decisions.project_id) is
  in place and demonstrated by criteria #2 + #7 of the demo runbook.
Last task completed: M7.5 RUN 4 — Phase E gate.
Commits pushed during this M7.5 arc (in order):
  - ebd51f0 M7.5.AB (RUN 1) — migration 0034 + readme renderer +
                   readme_consumer worker + 2 MCP tools.
  - 1722627 docs    — SESSION_RESTORE update for RUN 1 closure.
  - 6e64b39 M7.5.C  (RUN 2) — Router awareness injection
                   (available_skills + active_projects), archive_project,
                   recommend_skills_for_query, project_id population in
                   task_create + decision_record.
  - 81c52bf M7.5.D  (RUN 3) — skills/skill_discovery.md (222 ln) +
                   migration 0035 (utility_score + trigger_keywords) +
                   bucket README regeneration with legacy preservation.
  - <THIS>  M7.5.E  (RUN 4) — tests + 7 success criteria demos +
                   tasks.md / SESSION_RESTORE update + tag candidate.
Test count this session arc:
  - tests/awareness/test_readme_renderer.py — 7 tests (1 bonus over E.1
    minimum) — pure, no DB.
  - tests/awareness/test_readme_consumer.py — 3 slow tests (LISTEN /
    debounce / multi-target dispatch).
  - tests/mcp_server/tools/test_awareness.py — 6 tests (3 recommend
    cases + regenerate + archive moves + lifecycle notify).
  - tests/router/test_e2e.py — 6 existing tests, each augmented with
    available_skills + active_projects assertions.
  - tests/mcp_server/tools/test_projects.py — 8 existing tests; the
    happy-path test now also asserts the bucket README projection.
Total new + modified: 16 new tests, 14 existing tests augmented.
Demonstration: runbooks/m7_5_demo.md (419 lines) walks through the 7
  rationale-doc success criteria with command transcripts and DB
  evidence. All 7 PASS. Criterion #6 archived the m7-5-demo fixture
  project (intentionally retained as forensic trail for the demo).
  Criterion #7 emulates M6 via direct INSERT — M6 not yet running.
Open follow-ups carried forward (unchanged):
  M7.A.fu1 (apply 0032), M7.A.fu2 (migrate.py runner bug), the M6
  scaffold tasks, the M4 5db4bc6f / cost_usd / session_excerpt
  follow-ups, and the lessons.py mypy item.
New observation worth noting: pretel-os-readme.service is now load-
  bearing infrastructure. If it stops, every write to lessons /
  tasks / decisions / projects / tools_catalog still emits the
  readme_dirty NOTIFY (the migration 0034 triggers persist), but no
  one is listening — bucket and project READMEs go stale until the
  service is restarted or `regenerate_*_readme` is called manually.
  Any subsequent module that adds NEW writers to these tables should
  be aware of the projection contract.
Tags unchanged: foundation-v1.0, module-1-complete, module-2-complete,
  module-3-complete, module-0x-complete, module-5-complete (plus M4
  phase tags). Tag candidate this session: module-7-5-complete on
  the M7.5.E commit (operator-driven push).
Next: Module 6 (reflection_worker) — SDD trinity + production
  deployment. OR Module 7 Phase C (operator-driven brief).


Last session: 2026-04-30 (Module 7.5 RUN 1 of 4 — awareness layer foundation)
Status: M7.5 in progress. RUN 1 of the 4-run code briefing closed end-
  to-end: schema migration + lifecycle hooks (Phase A) + README renderer
  + LISTEN/NOTIFY consumer + 2 MCP tools (Phase B). RUNs 2-4 pending,
  each self-contained per the briefings doc.
Last task completed: M7.5 RUN 1 — commit ebd51f0.
Commit pushed this session arc:
  - ebd51f0 M7.5.AB: awareness migration 0034 + readme renderer +
            consumer worker. 8 files, +1364 LoC.
            Migration 0034: project_id UUID FK on lessons/tasks/decisions
            (NULLABLE + ON DELETE SET NULL); archived_at + archive_reason
            + applicable_skills on projects; trigger_keywords on
            tools_catalog; backfill UPDATE 0/0/0 (projects empty); 4
            NOTIFY trigger functions (project_lifecycle, readme_dirty_
            bucket fans out per applicable_buckets, readme_dirty_project
            looks up bucket+slug from FK, catalog_changed); 10 triggers
            attached. Applied to pretel_os AND pretel_os_test;
            schema_migrations row '0034' inserted in-migration (idempotent
            ON CONFLICT). Manual workaround for migrate.py runner bug
            still applies (matches LL-INFRA-001).
            src/awareness/readme_renderer.py: pure parse_readme +
            render_bucket_readme + render_project_readme; sync
            regenerate_bucket_readme + regenerate_project_readme
            orchestrators. Marker pattern <!-- pretel:auto:start NAME -->
            ... <!-- pretel:auto:end NAME --> per Q3 plan; operator
            notes preserved byte-for-byte between <!-- pretel:notes -->.
            Atomic write: tempfile.NamedTemporaryFile in same dir +
            fsync + os.rename. Idempotency via stable-timestamp logic
            (reuses old timestamp when data unchanged) — running twice
            in a row = byte-identical file.
            src/awareness/readme_consumer.py: async LISTEN on
            'readme_dirty' channel via psycopg.AsyncConnection
            autocommit=True; debounce 30s, scan every 5s; dispatch via
            asyncio.to_thread to a sync psycopg.connect calling the
            renderer's regenerate_*. Graceful shutdown on SIGTERM/SIGINT
            via add_signal_handler -> stop_event.
            src/awareness/__main__.py: python -m awareness =
            readme_consumer.main().
            infra/systemd/pretel-os-readme.service: user unit mirroring
            pretel-os-bot.service. systemctl --user start showed
            "active (running)" + "LISTENing on channel=readme_dirty
            (debounce=30s, scan=5s)".
            src/mcp_server/tools/awareness.py: async MCP wrappers
            regenerate_bucket_readme(bucket) + regenerate_project_readme
            (bucket, slug). Use asyncio.to_thread + fresh sync
            psycopg.connect; respect db_mod.is_healthy degraded gate;
            log_usage on every call; return content_preview (first 500
            chars).
            mcp_server/main.py: imports + app.tool registrations under
            "Module 7.5 — awareness layer".
Smoke verified: imports OK; consumer boots clean and shuts down on
  SIGTERM; mypy --strict clean across src/awareness/ + tools/awareness.py
  + main.py.
Open follow-ups carried forward (unchanged from prior session):
  M7.A.fu1 (apply 0032), M7.A.fu2 (migrate.py runner bug), and the
  M6 / tool-family / lessons.py-mypy items already tracked.
Next: M7.5 RUN 2 — Phase C (Router awareness injection + new MCP
  tools + tool updates). Operator pastes RUN 2 briefing from
  ~/Downloads/M7_5_code_briefings.md when ready.
Tags unchanged: foundation-v1.0, module-1-complete, module-2-complete,
  module-3-complete, module-0x-complete, module-5-complete (plus M4
  phase tags). M7.5 will tag module-7-5-complete on RUN 4 close
  (operator-driven push, per the briefing).


Last session: 2026-04-30 (Module 7 Phases A + B closed via per-phase operator briefs)
Status: Module 7 in progress without a formal SDD trinity. Two phases
  closed via standalone operator briefs (M7.A on 2026-04-29, M7.B on
  2026-04-30). Phase C scope pending — operator picks at next kickoff.
Last task completed: doc-only update across this session — `tasks.md`,
  `plan.md`, `tasks.archive.md`, `SESSION_RESTORE.md`, `DECISIONS.md`,
  `docs/DATA_MODEL.md`, `docs/LESSONS_LEARNED.md`.
Commits pushed earlier in this session arc:
  - 3a41d7f M7.A: skills/sdd.md (455 ln, generic across all buckets) +
            skills/vett.md (655 ln, organization-agnostic — verified
            zero matches for "scout|zscaler|databricks|kubernetes|eks
            |livekit|pinecone") + buckets/scout/skills/vett_scout_context.md
            (182 ln L2 overlay supplying tech stack / governance /
            compliance / data taxonomy / scoring deltas) +
            buckets/scout/README.md rewrite (52 ln) +
            migrations/0032_seed_skills_sdd_vett.sql (SQL fallback,
            idempotent ON CONFLICT DO UPDATE — MCP register_skill
            session was lost mid-task). Migration 0032 NOT yet
            applied to either DB.
  - fbe3a66 M7.B: migration 0033_projects_table.sql (live registry,
            distinct from projects_indexed) applied directly via
            psql -1 -f to both pretel_os and pretel_os_test +
            manual prefix-only INSERT into schema_migrations
            (sidesteps the migrate.py runner version-format bug).
            src/mcp_server/tools/projects.py: create_project +
            get_project + list_projects, registered in main.py
            (line 49 import, lines 156-158 app.tool calls).
            src/mcp_server/router/router.py: _check_project_exists
            helper + conditional unknown_project key in get_context
            response. tests/mcp_server/tools/test_projects.py:
            8 tests, @pytest.mark.slow, inline fixtures, all green
            in 1.15s. mypy clean. systemctl --user restart
            pretel-os-mcp succeeded; service active running.
Open follow-ups carried forward:
  - M7.A.fu1 — apply migration 0032 to populate tools_catalog rows +
              queue embeddings for sdd + vett. Required before M7
              exit gate per plan §6.
  - M7.A.fu2 — reconcile infra/db/migrate.py: stores path.stem as
              version while older rows use 4-digit prefix only.
              Workaround in M7.B was direct psql -1 -f + manual
              prefix-only schema_migrations INSERT. See LL-INFRA-001
              and DECISIONS ADR-026.
  - M7 trinity retro-build — when Phase C closes (or earlier), build
              specs/skills_migration/{spec,plan,tasks}.md to capture
              the running record. Anti-pattern logged.
Decisions captured this session arc (full reasoning in DECISIONS.md):
  - ADR-026 (NEW) — migrate.py version-format bug deferred; direct
              psql + manual schema_migrations INSERT is the
              sanctioned workaround until reconciliation lands.
  - ADR-027 (NEW) — projects (live, M7.B) and projects_indexed
              (closed/archived with embeddings, M2) are intentionally
              two tables. Live rows move to projects_indexed at
              project close-time (no automatic copy yet — manual or
              future tool).
Lessons captured this session arc (in docs/LESSONS_LEARNED.md §9):
  - LL-INFRA-001 — migrate.py version-format mismatch (stem vs
              prefix); how to detect and how to work around.
  - LL-PROC-003 — MCP session loss mid-task: ship the durable
              on-disk form of the mutation (SQL with idempotent
              upsert) rather than rabbit-holing into MCP debugging
              when the on-disk form is the canonical answer anyway.
Next:
  - Operator drives M7.C scope (per the SDD-skill convention, the
    L1+L3 context for Phase C is already in place: skills/sdd.md
    and skills/vett.md plus the Scout overlay).
  - OR resume Module 6 (Reflection worker) in parallel —
    SDD trinity not yet drafted.
Tags unchanged this session arc: foundation-v1.0, module-1-complete,
  module-2-complete, module-3-complete, module-0x-complete,
  module-5-complete (and the M4 phase tags from Module 4's session arc).
  M7 phases tracked by commit hash only — no intermediate tags
  (consistent with the operator pattern from M0.X).
---

**End of SESSION_RESTORE.md.**

If you are an LLM reading this: you have enough context to help. Ask the operator to confirm state, then proceed with the first unchecked task in `tasks.md`.

If you are the operator: the system is ready to build. Start with `tasks.md → P0.T1.1`.
