# PROJECT FOUNDATION — pretel-os

**Status:** Active
**Last updated:** 2026-04-18
**Owner:** Alfredo Pretel Vargas
**Repo:** `github.com/pr3t3l/pretel-os` (private)

This document defines the vision, technology stack, constraints, roadmap, architectural decisions, and documentation registry for pretel-os. It is the entry point for any human or AI agent joining the project. It defers detailed rules to `CONSTITUTION.md`, schemas to `DATA_MODEL.md`, external APIs to `INTEGRATIONS.md`, and failure patterns to `LESSONS_LEARNED.md`.

---

## 1. Vision

### 1.1 What pretel-os is

A personal cognitive operating system. One repository plus one database plus one MCP server that give any LLM client (Claude.ai web, Claude Code, Claude mobile, future MCP-compatible agents) hierarchical context, persistent memory, cross-bucket awareness, and portable access to the operator's three life domains.

### 1.2 Why it exists

Three observations drove the project:

1. **Context is the bottleneck.** The operator works across three unrelated domains (personal, business freelance/products, Scout W2). Each LLM conversation currently starts from near-zero context. Lessons learned in one domain are not applied in another. Tools built for one project are not reused in another.
2. **OpenClaw hit a ceiling.** The prior personal-agent stack (OpenClaw + Robotin + custom bots) accreted architectural choices without a plan. Debugging and extension cost more than rebuild.
3. **The operator's future is freelance.** As the freelance client count grows toward hundreds, the system must scale by filter-first retrieval and lazy loading, not by context-window stuffing.

pretel-os is the consolidation of existing assets (SDD System, VETT framework, Forge pipeline, 89 logged lessons) onto a clean architecture with the explicit design goals of portability, token-economy, and cross-domain awareness.

### 1.3 Success criteria at 12 months

By 2027-04-18, all six must be true:

1. **Uptime.** Phase 1–3 target is 95% reachability per month from any client, measured by UptimeRobot external pings against `https://mcp.alfredopretelvargas.com/health` (5-minute interval, free tier). The 99%+ target is deferred to Phase 4+ when revenue-gated migration to Supabase + managed hosting provides the redundancy the local-first topology doesn't. This honesty is intentional — a single consumer laptop with one public ingress path cannot structurally deliver 99% without failover, per GPT audit FINDING-009. External pings are the source of truth; the Vivobook's internal health checks cannot report a hard shutdown. UptimeRobot's monthly email report is the evidence artifact referenced by `control_registry.uptime_review`.
2. **Scale.** The system holds more than 200 lessons, more than 20 active projects across buckets, and more than 5 registered skills with measured utility scores.
3. **Cross-pollination works.** The Reflection worker has flagged at least 20 transfers, of which at least 10 have been reviewed and applied in a different bucket than their origin.
4. **Client portability is proved.** The operator has successfully used pretel-os from at least three distinct MCP clients (Claude.ai web, Claude Code, Claude mobile or successor) with no feature regression between them.
5. **Cost discipline.** Monthly API spend (Anthropic + OpenAI) has stayed under $30 during phases 0–3 and under $100 in phase 4+ unless revenue from Forge or freelance covers the increase with a 3x margin per `CONSTITUTION §4.11`.
6. **Freelance proof of concept.** At least one freelance engagement has used pretel-os skills or workflows (SDD, VETT, Forge, or Marketing System) and generated documented revenue.

### 1.4 Productized services

A secondary purpose of pretel-os is to produce freelance revenue streams by packaging internal skills and workflows as services for external clients. The following are explicit productization targets — every skill in `skills/` is designed so it can be offered externally without exposing operator-specific context:

| Offering | Underlying skill | Client deliverable |
|----------|------------------|--------------------|
| **VETT-as-a-Service** | `skills/vett.md` | 4-phase validated market/product research report |
| **SDD-on-Demand** | `skills/sdd.md` + `templates/` | Spec-driven architecture package (foundation docs + module specs) |
| **Forge Product Intelligence** | `skills/forge.md` | 8-phase product-analysis pipeline run on client's product set |
| **Finance AI-parsing** | `skills/finance_system.md` | Monthly financial analysis adapted for small businesses |
| **Marketing System setup** | `skills/marketing_system.md` | Product-agnostic marketing playbook customized per client |
| **AI Governance Starter Pack** | `skills/sdd.md` + abstracted Scout Motors AI policy work | Localized, secure AI policy + architecture plan. Target: mid-market manufacturing, logistics, healthcare. $5–10k one-off + 2 workshops. |
| **Competitor Intel Briefs** | Morning Intelligence n8n workflow + OpenAI TTS | Daily/weekly voice + text brief on competitor moves. Target: B2B SaaS founders, marketing directors. $500–1k/month retainer. |
| **MTM Digital Efficiency Audit** | `skills/mtm_efficiency_audit.md` (new, see roadmap §4 Module 7) | Industrial-engineering-grade audit of a client's digital workflow stack with n8n/AI automation proposals. Target: mid-size agencies, logistics. $2.5–5k per audit. |

Each offering shares the same underlying skill that pretel-os uses internally. Cross-bucket learnings (a lesson discovered while running Forge for Declassified that also applies to client X) flow automatically through the cross-pollination system.

**Migration-aware, not multi-tenant-ready.** The productization layer uses the `client_id` columns already present on every client-relevant table (see `DATA_MODEL §5` and §2.1). Filter-first retrieval enforces client scoping at the SQL level — a turn classified to Client A cannot see Client B's data because the query appends `WHERE client_id = 'A' OR client_id IS NULL`. This prevents LLM-level leakage per Gemini Strategic CONCERN-002. True multi-tenant isolation (per-client backups, tenant-specific deployments, RLS policies) remains future work and is explicitly out of scope until Phase 5+.

**Weak controls.** Some controls (Scout audit, restore drill, key rotation, uptime review, quarterly pricing verification) depend on manual operator action. These are tracked in `control_registry` (`DATA_MODEL §5.6`) with cadence and overdue alerting. Per GPT audit FINDING-012, acknowledging that these are weak controls — rather than pretending they are automated — is the honest baseline.

### 1.5 Failure criteria

If any of these is true at 12 months, the project has failed its design goals and triggers a deep review:

1. The operator is still using OpenClaw or a successor wrapper for core routing.
2. Average context assembly per turn exceeds 10,000 tokens for routine queries.
3. A Scout-labeled lesson has leaked proprietary employer data into another bucket, the database, or a public commit.
4. The system works from fewer devices than the current setup does (Claude.ai web, Telegram on mobile, Claude Code on the Vivobook).
5. The operator has repeated a mistake the system already had a lesson for, and the Router failed to surface that lesson.
6. Adding a new freelance client requires more than 10 minutes of scaffolding (all of it must be automatable through the `create_project` tool).

## 2. Stack

Every technology below is confirmed. Changing any of these requires a decision-log entry per `§5`.

### 2.1 Runtime and infrastructure

| Layer | Choice | Version | Role |
|-------|--------|---------|------|
| Host OS | Ubuntu 24.04 Desktop | LTS | Single-boot on Vivobook S15 OLED S5506 server |
| Containerization | Docker Engine | Latest stable | n8n and optional service isolation |
| Service supervisor | systemd + systemd timers | OS-native | Replaces cron and OpenClaw's process management |
| Network — private | Tailscale | Latest | Operator access from any device |
| Network — public | Cloudflare Tunnel (`cloudflared`) | Latest | Public MCP endpoint on subdomain of `alfredopretelvargas.com` |
| DNS | IONOS (primary) + Cloudflare (subdomain delegation) | n/a | Option A from conversation — website stays in IONOS, `mcp.alfredopretelvargas.com` subdomain routed through Cloudflare |

### 2.2 Data

| Layer | Choice | Version | Role |
|-------|--------|---------|------|
| Primary database | PostgreSQL | 16 | All dynamic state per `CONSTITUTION §2.4` |
| Vector extension | `pgvector` | Latest | Embeddings and similarity search |
| Embeddings model | OpenAI `text-embedding-3-large` | 3072 dim | Every write and query, immutable per `CONSTITUTION §2.5` |
| Backup target (local) | External SSD + rclone mirror | — | Daily encrypted |
| Backup target (remote) | Supabase Storage (free tier) | — | Daily encrypted, for cross-device recovery |
| Planned cloud target | Supabase (Pro when revenue-gated) | Postgres 16 + pgvector | Activated in phase 4+ |

### 2.3 Application

| Layer | Choice | Version | Role |
|-------|--------|---------|------|
| Language (MCP server, Router, workers) | Python | 3.12+ | |
| MCP framework | FastMCP | 2.x | Streamable HTTP transport |
| Telegram bot | `python-telegram-bot` | 21.x | Replaces OpenClaw's Telegram layer |
| Workflow orchestration | n8n | Latest self-hosted | Forge pipeline (existing) + new workflows |
| Scheduling | systemd timers (primary), APScheduler (for complex cases) | — | |
| LiteLLM proxy | LiteLLM | Latest | Multi-provider model routing (existing, reused) |

### 2.4 Models

Model-to-task mapping per `CONSTITUTION §4.8`:

| Task | Model | Rationale |
|------|-------|-----------|
| Client-side reasoning (what the operator sees) | Claude Opus 4.7 | Best available general reasoning |
| Router classification (bucket/project/skill/complexity) | LiteLLM alias `classifier_default` (currently Gemini 2.5 Flash) | Operator-tunable via config.yaml; ~$0.00003 per call at current alias, fast |
| Reflection worker (transcript analysis, lesson proposal) | Claude Sonnet 4.6 | Balance cost/quality |
| Embeddings (writes and queries) | OpenAI `text-embedding-3-large` | Industry standard, portable |
| Morning intelligence synthesis | Existing n8n configuration | Unchanged |

### 2.5 MCP server tool inventory (phase-3 target)

The MCP server exposes exactly these tool categories. Listed here as the authoritative surface; detailed schemas live in `src/mcp_server/tools/`.

**Context and retrieval:**
- `get_context(message)` — the Router's main entry point per `CONSTITUTION §2.2`
- `search_lessons(query, bucket?, tags?, include_archived?)`
- `search_projects_indexed(query, bucket?)`
- `search_conversations(query, date_range?)`
- `recommend_tools(context)` — utility-score-ranked tool suggestions
- `tool_search(query)` — returns tool definitions on demand (signature, params, description). Required by `CONSTITUTION §9` agent rules so agents never invoke tools with guessed parameter names.

**Knowledge capture:**
- `save_lesson(title, content, bucket, tags, category, severity?, applicable_buckets?, related_tools?)`
- `flag_cross_pollination(origin_bucket, target_bucket, idea, reasoning)`
- `update_project_state(project, changes)`
- `log_time_and_cost(project, duration_mins, cost_usd, description, client_id?)` — explicit time + external-API cost tracking per freelance project. Enables margin calculation per `llm_calls` + this table. Per Gemini Strategic TOOL-003.

**Cross-layer sync (per `CONSTITUTION §7.36`):**
- `create_project(bucket, name, description, modules?)` — creates scaffolding + updates L1
- `close_project(bucket, name)` — archives + updates L1 + inserts `projects_indexed`
- `add_module(bucket, project, module_name, description)` — creates module + updates L2 index
- `remove_module(bucket, project, module_name)` — removes + updates L2 index
- `create_bucket(name, description)` — creates bucket + updates L0
- `change_stack(project, new_stack)` — updates project's declared stack + triggers `snapshot_project`
- `snapshot_project(project, reason)` — writes to `project_versions`

**Skills and tools catalog:**
- `load_skill(name)` — loads full procedural memory (L3)
- `register_skill(name, description, applicable_buckets, skill_file_path)`
- `register_tool(name, description, applicable_buckets)`
- `deprecate_skill(name, reason)`
- `list_modules(project)` — returns module index without loading content

**Validation:**
- `request_second_opinion(context, problem_summary, original_proposal, model='second_opinion_default')` — operator-invoked cross-model validation via LiteLLM. Returns structured agreement/disagreement, key risks, missing assumptions, and recommended next step. Logs to `usage_logs` (tool invocation) and `llm_calls` with `purpose='second_opinion'`. See `INTEGRATIONS §4.5` for routing and timeout.

**Execution wrappers (per `CONSTITUTION §7.37`):**
- `run_forge_pipeline(product_url)` — webhook to n8n
- `run_finance_analysis(month, year)` — subprocess
- `run_vett_phase(topic, phase)` — subprocess or n8n
- (additional wrappers added per skill as needed)

**Prompts (user-invokable via slash commands):**
- `/new_project`, `/reflect_session`, `/morning_review`, `/vett_start`, `/sdd_init`

**Resources:**
- `pretel://identity` — L0 content
- `pretel://skills/{name}` — skill content (mirror of L3 for client-picker UIs)

### 2.6 Components reused from the previous stack

Three existing components are explicitly preserved and reused without rebuild, per the conversation of 2026-04-18:

1. **SDD System** — `github.com/pr3t3l/sdd-system` templates. Used to structure pretel-os itself and every future module.
2. **VETT framework** — 4-phase investigation methodology. Migrated to `skills/vett.md` in the new repo, wrapped as an MCP tool and MCP prompt.
3. **Forge pipeline** — 8-phase n8n Product Intelligence workflow. Left on its current Postgres until phase 4 cloud migration. Connects to pretel-os via MCP tool `run_forge_pipeline`.

Everything else from the OpenClaw era is discarded.

---

## 3. Constraints and budgets

### 3.1 API spend

| Phase | Target monthly | Hard ceiling | Action on overrun |
|-------|---------------:|-------------:|-------------------|
| 0–3 (build) | $30 | $50 | Immediate audit + lesson logged |
| 4+ (post-revenue) | $100 | revenue × 0.3 | Quarterly review |

Breakdown estimate at steady state (phase 3):

- Router classification (`classifier_default` via LiteLLM): ~$1–3
- Embedding writes + queries: ~$1–2
- Reflection worker (Sonnet): ~$5–10
- Client-side Opus reasoning: ~$10–20 (operator usage, variable)

### 3.2 Cross-device targets

Phase 1 must work from:

- **Claude.ai web** from any browser on any machine (primary daily driver)
- **Claude mobile app** on iPhone and iPad
- **Telegram bot** on any device (secondary input, for voice and on-the-go)
- **Claude Code** on the Vivobook itself and on the Asus Rock when the operator is away from home

All four paths reach the same MCP server. Feature parity between paths is a design goal, not a stretch.

### 3.3 Scout compliance

Beyond `CONSTITUTION §3`, one additional operator rule:

- **Quarterly Scout bucket audit.** Every 90 days the operator manually reviews every lesson, note, and pattern in `buckets/scout/` and in Scout-labeled database rows. Anything ambiguous is abstracted further or deleted. The audit itself is logged as an event.

### 3.4 Hardware lifetime

The Vivobook S15 OLED S5506 is consumer-grade and not designed for 24/7 operation. Expected reliable lifetime: 2–4 years of always-on use. Mitigations:

- Daily encrypted backups to Supabase Storage and to the Asus Rock over Tailscale
- Temperature monitoring via `lm-sensors` with Telegram alert on sustained thermal throttle
- Annual review of hardware health (SSD SMART, battery cycles)
- Explicit upgrade trigger: when Forge revenue covers a Beelink SER8 or equivalent Mini PC ($600–800), migrate in one evening using `pg_dump` + `git clone` + environment script

---

## 4. Roadmap

Modules in dependency order. Each follows full SDD process (`spec.md` → `plan.md` → `tasks.md` → BUILD → VALIDATE → REVIEW → CLOSE) per `CONSTITUTION §6`.

### Module 1: `infra_migration`

Consolidation of all existing infrastructure onto the Vivobook S15 OLED running Ubuntu 24.04 Desktop. Backup and retire the current split setup (Asus Robotin WSL + Asus Rock Docker). Establish the baseline: Postgres, Docker, n8n restored from Forge backup, Tailscale, Cloudflare Tunnel, SSH, systemd timers, Python 3.12 toolchain.

**Blocks:** every subsequent module.
**Estimated duration:** 1 week (4 weeks elapsed including backup and verification).
**Done when:** Forge runs end-to-end on the Vivobook, Tailscale reachable from Asus Rock and mobile, cloudflared tunnel serves a test page on `mcp.alfredopretelvargas.com`, the Asus Rock has been clean-wiped to personal-laptop role, and `/tmp/forge_backup.sql` is restored into the new Postgres and verified.

### Module 2: `data_layer`

Postgres schema for all 16 Phase-1 MVP tables defined in `DATA_MODEL.md §1.2` (21 total including Phase-2 extensions, delivered later), pgvector extension enabled, indexes, triggers for auto-indexing (`CONSTITUTION §2.6` worker 4), migration scripts. No data yet — empty schema, ready to populate.

**Blocks:** 3, 4, 5, 6, 7, 8.
**Estimated duration:** 3 days.
**Done when:** `psql` can connect, all tables exist, a test row with a computed embedding round-trips via similarity query, auto-index trigger fires and populates `embedding` column on insert.

### Module 3: `mcp_server_v0`

FastMCP server with the minimum tool set to be useful: `get_context`, `search_lessons`, `save_lesson`, `register_skill`, `load_skill`, `tool_search`. Streamable HTTP transport. Deployed via systemd on the Vivobook, exposed at `mcp.alfredopretelvargas.com` via Cloudflare Tunnel. Connected to Claude.ai as a custom connector and to Claude Code.

**Blocks:** 4, 5, 6, 7, 8.
**Estimated duration:** 1 week.
**Done when:** Claude.ai web can call all six tools and receive expected responses, the server reconnects automatically after `systemctl restart`, and a round-trip `save_lesson` → `search_lessons` cycle works end-to-end.

### Module 4: `router`

The Router per `CONSTITUTION §2.2`: classifier via LiteLLM alias `classifier_default` (per ADR-020), layer loaders L0–L4, RAG activation logic, token budget enforcement, logging to `routing_logs` + `llm_calls`. Exposed as the `get_context` tool in the MCP server.

**Blocks:** 5, 6.
**Estimated duration:** 1 week.
**Done when:** For a test suite of 20 sample messages across buckets, the Router correctly classifies bucket/project/skill with > 90% accuracy, respects every layer budget, and logs each decision. Cost per classification is measured and recorded in `llm_calls.cost_usd`.

### Module 0.X: `knowledge_architecture`

Inserted 2026-04-28 between Module 4 Phase A and Phase B. Splits `lessons` table into typed knowledge stores: `tasks`, `operator_preferences`, `router_feedback`, `best_practices` (new) + amendments to `decisions` (existing). Adds `SOUL.md` voice file. 17 new MCP tools. See specs/module-0x-knowledge-architecture/.

**Phase A status (2026-04-28):** COMPLETE. 7 migrations applied to production: 0024 (tasks), 0025 (operator_preferences), 0026 (router_feedback), 0027 (best_practices, HNSW deferred per ADR-024), 0028 (decisions amendment), 0028a (Module 2 trigger fix), 0029 (ADR seed + lessons split). Schema audit at `migrations/audit/0029_post_state.md`. Phases B-E pending.

### Module 5: `telegram_bot`

Replacement for OpenClaw's Telegram interface using `python-telegram-bot`. Commands: `/start`, `/review_pending`, `/cross_poll_review`, `/morning_brief`, `/save`, `/reflect`. Voice-message input via Whisper for hands-free capture. Runs as a systemd service on the Vivobook.

**Blocks:** 6 (only for operator-facing review flows).
**Estimated duration:** 4 days.
**Done when:** the operator can approve/reject entries with `status='pending_review'` in the `lessons` table and entries in `cross_pollination_queue` from Telegram, and a voice note becomes a persisted ingestion via MCP `save_lesson`.

### Module 6: `reflection_worker`

The Reflection worker per `CONSTITUTION §2.6`. Event-triggered (`task_complete`, `close_session`, fallback every 20 turns or 60 minutes of session lifespan — whichever fires first). Reads transcript, produces proposals, inserts lessons with `status='pending_review'`, writes `cross_pollination_queue` and `project_state` rows. Uses Sonnet 4.6. Degraded mode: queues to `reflection_pending` when Sonnet is unreachable.

**Blocks:** none — but gates the cross-pollination and lesson-flywheel guarantees of `§1.3`.
**Estimated duration:** 4 days.
**Done when:** a test session with a known resolved problem produces at least one lesson proposal with title/content/"next time" clause, and a known cross-domain insight produces a queue entry with origin/target/reasoning.

### Module 7: `skills_migration`

Port the existing skills from their current locations into the canonical `skills/` directory and register them in `tools_catalog`:

**Existing skills (migrate):**
- `skills/vett.md` (VETT framework)
- `skills/sdd.md` (Spec-Driven Development process)
- `skills/scout_slides.md` (Scout presentation methodology — abstracted patterns only)
- `skills/declassified_pipeline.md` (4-agent pipeline methodology, abstracted away from the product)
- `skills/forge.md` (Product Intelligence 8-phase pipeline)
- `skills/marketing_system.md` (product-agnostic marketing playbook)
- `skills/finance_system.md` (personal/business financial analysis)

**New skills (author during Module 7, per Gemini Strategic Review):**
- `skills/client_discovery.md` — 5-question structured intake when a new freelance client is added. Inputs: raw meeting transcripts or voice notes. Outputs: structured JSON updating `project_state` + a drafted L2 project README. Internal-only.
- `skills/sow_generator.md` — drafts Statements of Work and proposals. Inputs: client_id + target service (Forge/VETT/SDD). Outputs: Markdown SOW with deliverables, timeline, cost. Internal-only.
- `skills/mtm_efficiency_audit.md` — applies Methods-Time Measurement to digital workflows. Inputs: client workflow descriptions + tool stacks + time-to-completion metrics. Outputs: structured audit report with bottlenecks + n8n/AI automation proposals. Productizable ($2.5–5k per audit).

Each registered via `register_skill` with `applicable_buckets` metadata so the Router can recommend correctly.

**Blocks:** none.
**Estimated duration:** 5 days (2 days extra for the three new skills).
**Done when:** all ten skills appear in `tools_catalog` with embeddings, `load_skill("vett")` returns the full procedural memory, and a test query from each applicable bucket surfaces the right skill in top-3. The three new skills have at least one end-to-end test invocation documented.

### Module 8: `lessons_migration`

Migrate the existing 89 lessons from `LL-MASTER.yaml` and `LL-FORGE.yaml` into the `lessons` table with embeddings. Deduplicate during migration (similarity ≥ 0.92 triggers merge). Preserve original category tags (PLAN, ARCH, COST, INFRA, AI, CODE, DATA, OPS, PROC).

**Blocks:** none.
**Estimated duration:** 2 days.
**Done when:** `SELECT count(*) FROM lessons` is in the range 75–89 (depending on dedup), every row has a non-null embedding, and a semantic query for a known past problem ("n8n batching") returns the correct lesson in top-3.

### Roadmap summary

Total estimated duration, serialized: approximately **6 weeks** of focused work. Realistic calendar time given operator's W2 schedule and Scout priorities: **10–14 weeks**, with `infra_migration` as week 1–4.

After all 8 modules complete, phase 3 closes. Phase 4 (cloud migration, revenue-gated) opens.

---

## 5. Decisions log

Each decision in Architecture Decision Record (ADR) format: Context → Decision → Consequences → Date. Decisions here are immutable unless explicitly superseded by a later entry.

### ADR-001: Separate repository from OpenClaw

**Context.** OpenClaw accumulated configuration debt and architectural decisions that were never documented. Debugging routinely exceeds the cost of rebuild.

**Decision.** pretel-os is a new repository (`pr3t3l/pretel-os`) built from scratch using the SDD process. OpenClaw is deprecated and will be retired once pretel-os reaches feature parity for daily workflows.

**Consequences.** Short-term effort cost (rebuild). Long-term gain: known architecture, explicit decisions, tested modules. Three existing assets (SDD System repo, VETT, Forge n8n workflow) are preserved unchanged and reused.

**Date.** 2026-04-18.

### ADR-002: MCP server as the single gateway

**Context.** Clients (Claude.ai, Claude Code, Claude mobile, future agents) need a portable contract. Direct database access from a client would lock pretel-os to specific clients and leak schema details.

**Decision.** Every client reaches pretel-os exclusively through the MCP server over Streamable HTTP. The MCP server exposes tools, resources, and prompts. Postgres, n8n, the Telegram bot, and the git repo are never addressed directly by clients.

**Consequences.** Portability is guaranteed by construction. Schema changes only require MCP tool signature stability. One deployment surface to secure and monitor.

**Date.** 2026-04-18.

### ADR-003: The Router lives in the MCP server, not in any client and not in OpenClaw

**Context.** Context assembly (which layers to load, when to run RAG, how to respect token budgets) is a first-class responsibility that previously lived ambiguously across OpenClaw, skills, and ad-hoc prompts. That ambiguity was the root cause of token waste and inconsistent behavior.

**Decision.** The Router is a named component inside the MCP server per `CONSTITUTION §2.2`. Clients call one tool, `get_context(message)`, and receive pre-assembled context. No client-side routing, no client-side RAG, no client-side classification.

**Consequences.** Switching clients does not change behavior. Router logic is testable in isolation. Cost control is enforceable at one point. Rule 36 of the CONSTITUTION depends on this decision.

**Date.** 2026-04-18.

### ADR-004: Stack D chosen over OpenClaw reconfiguration and over fully custom stack

**Context.** Three options evaluated:
- A: fully custom (build everything)
- B: OpenClaw reconfigured carefully
- C: hybrid (custom router + OpenClaw UI)
- D: mature-components stack (`python-telegram-bot` + n8n + FastMCP + systemd)

**Decision.** Option D. Each component is independently battle-tested. No wrapper hides architectural decisions. Replaceability is preserved (any component can swap without touching the others).

**Consequences.** Loses OpenClaw's community and update cadence. Gains stability, testability, explicit ownership of every choice. Requires operator to manage Telegram bot updates and n8n upgrades directly (acceptable — all of these have mature ecosystems).

**Date.** 2026-04-18.

### ADR-005: Ubuntu 24.04 Desktop replaces Windows 11 on the Vivobook

**Context.** Windows 11 on the Vivobook consumes more than 70% of RAM at idle, leaving insufficient headroom for Postgres + n8n + MCP server + bot concurrently. Dual boot adds GRUB complexity and risks leaving the machine at a boot menu after a power event. Windows Server is overpriced for this use.

**Decision.** Clean install Ubuntu 24.04 LTS Desktop on the Vivobook S15 OLED, single boot. GUI available on demand; services run as systemd units regardless of login state.

**Consequences.** All RAM (16–32 GB) available for workloads. Native Linux tooling (apt, Docker, systemd, Python). Operator loses Windows on the Vivobook — acceptable because the Asus Rock remains the personal laptop and carries Windows if needed.

**Date.** 2026-04-18.

### ADR-006: OpenAI `text-embedding-3-large` as the embeddings model

**Context.** Three candidates considered: OpenAI `text-embedding-3-small` (cheap, 1536 dim), OpenAI `text-embedding-3-large` (3072 dim, industry standard), Voyage-3-large (best benchmark but less portable). Local sentence-transformers rejected due to dependency on machine availability.

**Decision.** `text-embedding-3-large`, 3072 dimensions. Cost at expected volume is negligible (~$1/month). Supported by every major tutorial, framework, and vector DB provider. Portable by construction.

**Consequences.** Switching to Voyage or local requires full reindex (cheap at current scale, more expensive later — acceptable trade). Pinned in `CONSTITUTION §2.5` to prevent silent drift.

**Date.** 2026-04-18.

### ADR-007: Postgres + pgvector locally, migrate to Supabase when schema stable

**Context.** Vector database options evaluated: pgvector local, Supabase (Postgres + pgvector managed), Pinecone, Turbopuffer, Qdrant Cloud, Neon. Scale estimates show Postgres + pgvector comfortable at 10M+ vectors; projected dataset is under 100k vectors in 5 years.

**Decision.** Phase 2 builds on pgvector locally on the Vivobook. Phase 4–5 migrates to Supabase managed Postgres when the schema has stabilized. Pinecone and others are held in reserve but not adopted.

**Consequences.** Schema iteration cost is zero during build (local dev). Migration to Supabase is a one-hour `pg_dump`/`psql` operation when triggered. Forge's existing Postgres remains separate and untouched until its own revenue-gated migration.

**Date.** 2026-04-18.

### ADR-008: Five context layers L0–L4, fixed

**Context.** An arbitrary layer count is a source of drift: adding layers whenever a new need appears leads to bloat. A fixed, small set forces design discipline.

**Decision.** Exactly five context layers — L0 Identity, L1 Bucket, L2 Project, L3 Skill, L4 Retrieved lessons — as defined in `CONSTITUTION §2.3`. Adding a sixth requires constitutional amendment.

**Consequences.** Every new feature must fit into one of the five. Multi-module projects split within L2 (project README + module file), they do not create a new layer. Tool-catalog detail lives in L3, not L0.

**Date.** 2026-04-18.

### ADR-009: Four background workers, fixed

**Context.** Cron jobs proliferate. Without a named charter, every new automation becomes a cron entry nobody remembers maintaining.

**Decision.** Exactly four background workers — Reflection, Dream Engine, Morning Intelligence, Auto-index — as defined in `CONSTITUTION §2.6`. Each has a named charter and a single home. Adding a fifth requires constitutional amendment.

**Consequences.** Operational surface is bounded and documentable. Failure modes are enumerable. Every scheduled behavior traces to one of four owners.

**Date.** 2026-04-18.

### ADR-010: Reflection triggered by event, never by turn count

**Context.** Earlier proposal used "every N messages" (N=100 suggested). Analysis showed most sessions never reach 100 messages, so reflection would rarely fire. Event-driven triggers (task completion, session close, or fallback) fire reliably.

**Decision.** Reflection fires on `task_complete` tool call, on `close_session` (10 minutes idle or explicit close), or on a fallback every 20 turns — whichever arrives first. Never on arbitrary message-count windows.

**Consequences.** Lessons capture happens when loops actually close. The fallback catches long exploratory sessions that never formally close. Rule 12 of `CONSTITUTION §5.1` depends on this.

**Date.** 2026-04-18.

### ADR-011: Dedicated `tools_catalog` table, not mixed into `lessons`

**Context.** Alternatives were: (a) dedicated table with embeddings and utility score, (b) mix into `lessons` with a `tool_metadata` tag, (c) YAML in git with no embeddings. Option (b) mixes semantically different entities and complicates queries. Option (c) has no ranking or retrieval.

**Decision.** Dedicated `tools_catalog` table in Postgres with its own columns (usage_count, utility_score, applicable_buckets, skill_file_path) and its own embedding column.

**Consequences.** Tool recommendations run against a small, purpose-shaped table. Utility score formula (`CONSTITUTION §5.2`) has a clean home. No semantic pollution in `lessons`.

**Date.** 2026-04-18.

### ADR-012: Subdomain of `alfredopretelvargas.com` via Cloudflare Tunnel (Option A)

**Context.** Operator already owns `alfredopretelvargas.com` on IONOS hosting. Two options: (A) keep DNS at IONOS, delegate a subdomain to Cloudflare for tunnel use, or (B) move entire DNS zone to Cloudflare.

**Decision.** Option A. `mcp.alfredopretelvargas.com` (and future subdomains) are routed through Cloudflare Tunnel via CNAME from IONOS. Main website and webmail continue at IONOS unchanged.

**Consequences.** Zero disruption to existing website or `support@declassified.shop` email. Cloudflare-managed subdomains have TLS, DDoS protection, and tunnel routing for free. Adding new public subdomains requires one CNAME record each in IONOS.

**Date.** 2026-04-18.

### ADR-013: Asus Rock as personal laptop, Vivobook S15 OLED as always-on server

**Context.** Operator has two Asus laptops. Only one can be the always-on server (thermal, location, reliability profile differ). The Vivobook S15 OLED has higher specs (Intel Ultra 9, up to 32 GB RAM, NVMe Gen4). The Asus Rock is older and portable.

**Decision.** The Vivobook S15 OLED is reinstalled with Ubuntu 24.04 Desktop and becomes the pretel-os server, always on, at home. The Asus Rock remains on Windows and serves as the operator's daily portable laptop for travel and in-office work.

**Consequences.** Clean role separation. The Asus Rock can reach the server via Tailscale from anywhere. Failover plan: if the Vivobook fails, the Asus Rock can temporarily host the stack (reduced uptime but functional).

**Date.** 2026-04-18.

### ADR-014: Cloud migration is revenue-gated with 3x margin

**Context.** Running fully in the cloud costs $50–100/month at minimum. Running locally costs near-zero in cash but requires the Vivobook to remain healthy.

**Decision.** Cloud migration happens per product: the associated product's revenue (Forge, Declassified, freelance) must cover 3x the new monthly spend before migration. Until then, local wins.

**Consequences.** The system's cash floor stays low during build. Cloud migration, when it happens, is economically safe. `CONSTITUTION §4.11` encodes this rule.

**Date.** 2026-04-18.

### ADR-015: Preserve SDD System, VETT, and Forge from prior stack

**Context.** Not every asset from the OpenClaw era is waste. Three things work well and would cost more to rebuild than to port.

**Decision.** `github.com/pr3t3l/sdd-system` remains the canonical SDD template source. VETT migrates to `skills/vett.md` unchanged. Forge's 8-phase n8n pipeline migrates with Postgres dump to the Vivobook and remains on its current design.

**Consequences.** Faster ramp. The three preserved assets become early `tools_catalog` entries and early content for `skills/`.

**Date.** 2026-04-18.

### ADR-016: Complexity classification drives retrieval (LOW/MEDIUM/HIGH)

**Context.** Rule 16 of an earlier draft referenced "complex problems" without an operational definition. Agents were left to decide when to consult lessons, which is exactly what the Router is supposed to own.

**Decision.** Router classifies every turn as LOW, MEDIUM, or HIGH per `CONSTITUTION §5.1`. HIGH always loads L4 and queries tool-catalog. MEDIUM conditionally loads (filter-first existence check). LOW never loads L4. The definition is operational (not subjective): factual queries and casual conversation are LOW; structured known-workflow tasks are MEDIUM; debugging, architecture, and recommendation requests are HIGH.

**Consequences.** Predictable cost per turn by category. No agent-side guessing. Operator can review `routing_logs` to see classification history and tune rules if needed.

**Date.** 2026-04-18.

### ADR-017: Degraded mode for MCP dependency failures

**Context.** The MCP server is the single gateway (ADR-002). A naive implementation would make every dependency outage a full system outage. Postgres unreachable → no context. OpenAI down → no embeddings. Classifier LLM down → no classification. Unacceptable.

**Decision.** Degraded mode is a first-class operating state per `CONSTITUTION §8.43`. Git-only mode serves L0–L3 without the DB. Embedding writes queue to `pending_embeddings` when OpenAI is down. Classifier LLM (via LiteLLM `classifier_default`) falls back to keyword/regex rules. Morning Intelligence skips with logged incident. Every degraded response carries an explicit flag so the agent surfaces reduced functionality instead of pretending everything works.

**Consequences.** System stays usable during partial outages. Failure modes are enumerable and testable. Cost of implementation is one additional code path per external dependency — acceptable.

**Date.** 2026-04-18.

### ADR-018: Project snapshots separate from skill versions

**Context.** `skill_versions` preserves the evolution of methodology files. But projects also evolve (Declassified changes its stack, Healthy Families adds modules), and "how did we do it before this change" is a common recall need.

**Decision.** Add `project_versions` table (separate from `skill_versions`). Snapshots are written automatically by structural tools (`add_module`, `change_stack`, etc.) and can be invoked manually via `snapshot_project(project, reason)`. Each snapshot stores the full L2 content at that point in time with reason and timestamp.

**Consequences.** "How did we do this 6 months ago" returns actual historical state, not inferred from git log. Storage cost is trivial (project files are small, snapshots rare). Rule 25 of `CONSTITUTION §5.5` depends on this decision.

**Date.** 2026-04-18.

### ADR-019: Knowledge lifecycle (archive, summarize, nightly dedup)

**Context.** Without lifecycle rules, the system accumulates noise. Old lessons nobody uses still match retrieval queries. Six-month-old conversations clog `conversations_indexed`. Near-duplicates missed at insert time proliferate.

**Decision.** Three lifecycle rules encoded in `CONSTITUTION §5.5`: (1) lessons with zero usage + low utility after 180 days have their `status` set to `archived` (same row, excluded from default retrieval); (2) conversations older than 90 days are replaced with 200-token summaries (embedding preserved); (3) nightly dedup pass at similarity ≥ 0.95 generates merge proposals in `cross_pollination_queue` with `proposal_type='merge_candidate'`. All three run in the Dream Engine.

**Consequences.** Retrieval precision holds as the corpus grows. Archived lessons remain queryable with explicit flag. Operator retains final say on merges — no automatic deletion.

**Date.** 2026-04-18.

### ADR-020: Router and Second Opinion route through LiteLLM proxy aliases

**Context.** ADR-002 (MCP server as single gateway) and the original wording of `CONSTITUTION §2.2` and `§4 rule 8` mandated Haiku 4.5 for Router classification, called via the Anthropic SDK directly. INTEGRATIONS §4.5 reinforced "pretel-os calls Anthropic directly, not through LiteLLM" for Router and Reflection. At end-of-session 2026-04-26 the operator decided to route Router classification and `request_second_opinion` through the existing LiteLLM proxy instead of direct Anthropic SDK calls. Reflection worker alias remains TBD until Module 6 spec.

**Decision.** All MCP-server LLM calls used by the Router and the `request_second_opinion` tool go through LiteLLM proxy aliases:
- `classifier_default` for Router classification.
- `second_opinion_default` for the second-opinion tool.

The alias-to-model mapping lives in `~/.litellm/config.yaml` and is operator-tunable (today both point to `gemini/gemini-2.5-flash`). The task-to-alias mapping is immutable without amendment. Reflection worker's alias is deferred to Module 6 spec.

**Consequences.**
1. The operator can A/B between providers (Anthropic, OpenAI, Gemini, Kimi K2, etc.) by editing `~/.litellm/config.yaml` + `systemctl --user restart litellm`. No code changes.
2. Provider-specific prompt caching becomes a per-alias optimization, not a code-path concern. Deferred until classification cost exceeds $5/month.
3. `routing_logs.classification_mode` becomes provider-agnostic (`'llm' | 'fallback_rules'`). The concrete model lives in `llm_calls.model`, joinable via `request_id`.
4. INTEGRATIONS §4.5 prior wording is reversed for Router and `request_second_opinion` paths.
5. Telemetry stays unified in `llm_calls` regardless of which provider is currently behind each alias.

**Date.** 2026-04-27.

---

### ADR-021: Split `lessons` into typed knowledge stores

**Date:** 2026-04-28. Context: M4 Phase A.6.1 surfaced that lessons table is being used as catch-all for tasks/decisions/best practices/preferences. Decision: introduce `tasks`, `operator_preferences`, `router_feedback` tables (new) and amend existing `decisions` (DATA_MODEL §5.2). Add `SOUL.md` workspace file. Migration moves 4 misclassified lessons rows. Full spec at specs/module-0x-knowledge-architecture/spec.md.

---

## 5.2 Ideas backlog (seeded to `ideas` table during Module 8)

The following ideas came out of Gemini Strategic Review 2026-04-18 but were not promoted to the Phase 1 roadmap. They are seeded into the `ideas` table (per `DATA_MODEL §5.5`) with `status='new'` and revisited during quarterly review. The operator decides then which promote to projects via `promoted_to`.

| Idea summary | Category | Effort | Origin |
|-------------|----------|:------:|--------|
| `request_second_opinion` — manual cross-model validation tool. MCP tool `request_second_opinion(context, problem_summary, original_proposal, model='second_opinion_default')`. Operator-invoked only, no Router involvement. Routes through LiteLLM to a configured secondary-model alias. Returns structured response: `{status, model_used, agreement_level, key_risks, missing_assumptions, recommended_next_step, degraded_reason}`. Logs to `usage_logs` + `llm_calls` with `purpose='second_opinion'`. Timeout 15,000 ms. Degraded mode: if LiteLLM fails after 3 retries, returns `{status:'degraded', degraded_reason:'litellm_unavailable'}`. On implementation, register via `register_tool()`. Phase 3+ deferred scope: Reflection worker may suggest second-opinion review when transcript patterns indicate repetition — suggestion only, never auto-invoke. Requires empirical calibration after 30+ days of `routing_logs` data. | tool | hours | Operator observation: multi-model validation pattern from OpenClaw |
| Context-switching sandbox: `suspend_context(bucket, project, notes)` + `/resume` commands for mental-offload during interruptions | workflow | hours | Gemini USE-CASE-002 |
| Academic research ingestion: n8n webhook accepting PDFs, parsing via vision model, chunking into L4 lessons tagged `master_ia` | skill | days | Gemini USE-CASE-003 |
| Automated transaction categorization: `log_transaction(amount, description)` routes to active properties/projects using Haiku + writes to `financial_ledger` | skill | days | Gemini USE-CASE-004 |
| Content repurposer skill: `skills/content_repurposer.md` — transforms technical logs into LinkedIn/TikTok content EN/ES. Productizable $1.5k/month retainer | skill | days | Gemini SKILL-004 |
| `create_client_engagement(client_name, service_tier, target_bucket)` — higher-level wrapper around `create_project` that initializes billing metadata + communication cadence | tool | hours | Gemini TOOL-001 |
| `generate_client_report(project, report_type)` — extracts work done and packages as client-ready summary (not raw state) | tool | days | Gemini TOOL-002 |
| White-label Declassified content engine — custom interactive digital mysteries for HR / brand marketing. $3–8k per campaign | freelance_offering | weeks | Gemini SERVICE-003 |
| Stripe integration for automated invoicing: webhook → n8n → `project_state` update | workflow | days | Gemini complementary integration |
| Google Workspace integration: Gmail forwarding alias → n8n → `project_state` / `contacts` auto-update | workflow | days | Gemini complementary integration |
| Toggl Track integration: MCP starts/stops timers on context switches, surfaces margin-per-project | workflow | days | Gemini complementary integration |
| LatAm / Spanish AI market play: translate VETT + AI Governance Starter Pack deliverables to Spanish, target LatAm digital agencies | freelance_offering | weeks | Gemini OPPORTUNITY-001 |
| Automated failover environment: Ansible/docker-compose script to provision pretel-os on Asus Rock or VPS in <15 min | workflow | days | Gemini RISK-002 |

**Deferred-with-rationale (not seeded as ideas, rejected):**
- Local quantized router model (Gemini OPPORTUNITY-002) — rejected: API cost via LiteLLM is $1–3/month at current alias; maintaining a local model adds complexity that outweighs savings at current volume.
- Ollama 8B local DLP for Scout (Gemini challenge 1) — rejected: regex denylist + MCP filter + DB trigger is sufficient defense in depth. Running an 8B model 24/7 for every insert is over-engineering.
- Redis for queues (Gemini challenge 2) — rejected: `pending_embeddings` + `reflection_pending` as DB-native partitioned tables plus `pg_notify` for wake-up is simpler and sufficient at operator volume.

---

## 6. Doc registry

Every document in pretel-os must appear in this registry. Documents not listed here are deleted during monthly hygiene per `CONSTITUTION §6.33`.

### Foundation documents (`/`)

| Document | Purpose | Update cadence |
|----------|---------|---------------:|
| `CONSTITUTION.md` | Immutable rules and core architecture | Per amendment process |
| `PROJECT_FOUNDATION.md` | This document: vision, stack, roadmap, decisions | Per ADR |
| `DATA_MODEL.md` | Postgres schema: 16 Phase-1 tables + 5 Phase-2 tables (21 total) | Per schema migration |
| `INTEGRATIONS.md` | External APIs (Anthropic, OpenAI, Supabase, Cloudflare, Telegram, n8n) | Per API change |
| `LESSONS_LEARNED.md` | Significant issues + fixes + preventive rules | Continuously |
| `AGENTS.md` | Entry point for any LLM: what to read first | Per major architecture change |

### Identity and buckets (`/buckets/`, `/`)

| Document | Purpose |
|----------|---------|
| `identity.md` | L0 content: operator identity, bucket names, tool catalog names, meta-rules |
| `buckets/personal/README.md` | L1 Personal bucket |
| `buckets/business/README.md` | L1 Business bucket |
| `buckets/scout/README.md` | L1 Scout bucket (abstract patterns only) |
| `buckets/{bucket}/projects/{project}/README.md` | L2 project overview per project |
| `buckets/{bucket}/projects/{project}/modules/*.md` | L2 module detail for multi-module projects |

### Skills (`/skills/`)

| Document | Purpose |
|----------|---------|
| `skills/vett.md` | VETT framework procedural memory |
| `skills/sdd.md` | Spec-Driven Development process |
| `skills/scout_slides.md` | Scout presentation methodology (abstract) |
| `skills/declassified_pipeline.md` | 4-agent pipeline methodology |
| `skills/forge.md` | Product Intelligence 8-phase pipeline |
| `skills/marketing_system.md` | Product-agnostic marketing playbook |
| `skills/finance_system.md` | Personal/business financial analysis |

### Module specifications (`/specs/`)

One directory per module in the `§4 Roadmap`, each containing `spec.md`, `plan.md`, `tasks.md` per SDD:

| Directory | Status |
|-----------|--------|
| `specs/infra_migration/` | Pending |
| `specs/data_layer/` | Pending |
| `specs/mcp_server_v0/` | Pending |
| `specs/router/` | Pending |
| `specs/telegram_bot/` | Pending |
| `specs/reflection_worker/` | Pending |
| `specs/skills_migration/` | Pending |
| `specs/lessons_migration/` | Pending |

### Source code (`/src/`, `/workers/`, `/migrations/`)

| Path | Contents |
|------|----------|
| `src/mcp_server/` | FastMCP server code, tool definitions, Router |
| `src/telegram_bot/` | `python-telegram-bot` service |
| `workers/reflection.py` | Reflection worker |
| `workers/dream_engine.py` | Nightly consolidation |
| `workers/auto_index.py` | Postgres auto-index listener |
| `migrations/` | SQL migration files, applied in order |

### Infrastructure (`/infra/`, `/.github/`)

| Path | Contents |
|------|----------|
| `infra/systemd/` | `.service` and `.timer` files for all workers |
| `infra/cloudflared/` | Tunnel configuration |
| `infra/backup/` | Daily backup scripts, encryption key management |
| `.github/hooks/scout-guard.sh` | Pre-commit Scout denylist filter |
| `.github/workflows/` | GitHub Actions for CI checks on foundation docs |

### Templates (`/templates/`)

Copied from `pr3t3l/sdd-system` during `Module 1` for project bootstrapping:

| Template | Use |
|----------|-----|
| `templates/MODULE_SPEC.md` | Copy into `specs/{module}/spec.md` |
| `templates/WORKFLOW_SPEC.md` | Copy into `specs/{workflow}/spec.md` for n8n workflows |
| `templates/PLAN.md` | Copy into `specs/{module}/plan.md` |
| `templates/TASKS.md` | Copy into `specs/{module}/tasks.md` |
