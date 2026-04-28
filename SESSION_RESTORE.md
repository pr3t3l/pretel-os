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

**Phase:** Module 4 Phase A complete, Module 0.X (Knowledge Architecture) next.

**What is done:** Foundation, Modules 1–3, Module 4 Phase A (Router classifier — 19 unit tests + 1 live eval against Haiku 4.5 cleared all thresholds: bucket 1.0, complexity 0.8, schema_violations 0). LiteLLM cascade Anthropic+OpenAI configured. ChatJsonTelemetry captures truncation, cache hits, reasoning tokens, finish_reason classification with provider-agnostic edge case handling.

**What is not done:** Module 0.X (knowledge architecture: tasks/operator_preferences/router_feedback tables + SOUL.md), Module 4 Phase B (Layer Loader — depends on M0.X), Module 4 Phase C-F, Modules 5–8.

**Top of stack:** Module 0.X SDD trinity (spec exists at commit e466796; needs revision then plan.md and tasks.md).

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
├── tasks.md                                 # Atomic tasks (source of truth for "what next")
├── SESSION_RESTORE.md                       # This file
├── README.md                                # Repo entry point
├── identity.md                              # L0 operator identity (populated in Module 3)
├── AGENTS.md                                # LLM reading order (populated in Module 3)
│
├── docs/
│   ├── PROJECT_FOUNDATION.md                # Vision, stack, roadmap, ADRs
│   ├── DATA_MODEL.md                        # DB schema (21 tables)
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



## 14. Last-known state snapshot

Update this section each time you end a significant work session.

```
Last session: 2026-04-27
Last task completed: M4.T1 complete (spec + plan + tasks committed)
  - 3589673: M4.T1.1 spec.md
  - 7ec4764: M4.T1.2 plan.md
  - <hash>:  M4.T1.3 tasks.md
  - <hash>:  parent tasks.md M4.T1.x checkboxes closed
  - 50de55d: ADR-020 LiteLLM proxy amendment (constitutional)
Next task: A.1.1 in specs/router/tasks.md — create src/mcp_server/router/
            directory with __init__.py
LiteLLM: 2 healthy endpoints (classifier_default, second_opinion_default), both on gemini-2.5-flash
Lessons captured: f6cb027c (MCP cost model)
Tags: foundation-v1.0, module-1-complete, module-2-complete, module-3-complete
```
---

**End of SESSION_RESTORE.md.**

If you are an LLM reading this: you have enough context to help. Ask the operator to confirm state, then proceed with the first unchecked task in `tasks.md`.

If you are the operator: the system is ready to build. Start with `tasks.md → P0.T1.1`.
