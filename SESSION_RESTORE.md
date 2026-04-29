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

**Phase:** Module 0.X complete (tag `module-0x-complete`, commit `49edc0c`). M4 Phase B (Layer Loader) next.

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
- Tasks structure migrated to milestone-only at root with per-module trinity rule documented in `runbooks/sdd_module_kickoff.md`.
- 4 spec drifts caught at scratch test time (LL-M0X-001): request_id type, scope DEFAULT, lessons.status enum, L0 budget interpretation. Zero production damage.

**What is not done:**
- M4 Phase B (Layer Loader — unblocked, ready to start).
- M4 Phase C-F, Modules 5-8.

**Top of stack:** M4 Phase B (Layer Loader). Input contract frozen at `specs/module-0x-knowledge-architecture/layer_loader_contract.md`. Router `spec.md` and `plan.md` reconciled with the contract on 2026-04-29 (commit `8ac5ff1`).

**Where to find M4 Phase B source-of-truth:**
- Frozen input contract: `specs/module-0x-knowledge-architecture/layer_loader_contract.md` (deviations require ADR)
- Aligned spec: `specs/router/spec.md` §4.2 (ContextBundle / LayerBundle), §6.1 (dual-source layer table), §8.2 (Router does NOT pre-resolve conflicts)
- Aligned plan: `specs/router/plan.md` §4.2 Phase B scope (DB-backed loaders + `assemble_bundle` orchestrator), §4.3-4.5 deliverables + done-when + risk notes (incl. Phase C re-scope note)
- Constraints: `DECISIONS.md` ADR-020 (LiteLLM aliases for any chat completion), ADR-024 (HNSW deferred — sequential pgvector scan), ADR-025 (layer loader contract is frozen)

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
---

**End of SESSION_RESTORE.md.**

If you are an LLM reading this: you have enough context to help. Ask the operator to confirm state, then proceed with the first unchecked task in `tasks.md`.

If you are the operator: the system is ready to build. Start with `tasks.md → P0.T1.1`.
