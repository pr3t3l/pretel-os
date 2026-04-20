# CONSTITUTION — pretel-os

**Status:** Active
**Last updated:** 2026-04-18 (v3)
**Owner:** Alfredo Pretel Vargas

This document contains the immutable rules of pretel-os. Every module, agent, skill, and human operator must respect these rules without exception. Rules in this document only change through an explicit decision-log entry in `PROJECT_FOUNDATION.md §Decisions`, never silently.

---

## 1. Identity

pretel-os is a personal cognitive operating system. Its purpose is to give any LLM client (Claude.ai web, Claude Code, Claude mobile, future MCP-compatible agents) hierarchical context, persistent memory, cross-bucket awareness, and portable access to the operator's three life domains: personal, business (freelance + products), and Scout (W2 employment).

The operator is Alfredo Pretel Vargas. The system serves one human; it is not multi-tenant today. The architecture is **migration-aware** — meaning `client_id` columns exist on every table where client-scoped data will accumulate (lessons, project_state, project_versions, tools_catalog, patterns, decisions, ideas, contacts, conversations_indexed, llm_calls), and the filter-first retrieval in `CONSTITUTION §5.6` is designed to append `WHERE client_id = ? OR client_id IS NULL` at the SQL level when scoping to a freelance engagement. "Migration-aware" is not "multi-tenant-ready"; full row-level isolation, per-client backup boundaries, and tenant-specific deployments remain future work. See `PROJECT_FOUNDATION §1.4` for the scope of the migration gap.

---

## 2. Core architecture (load-bearing entities)

These entities are named and bounded here. Every other rule references them.

### 2.1 The MCP server is the single gateway

All clients (Claude.ai, Claude Code, Claude mobile, future agents) reach pretel-os exclusively through the MCP server. The MCP server exposes tools, resources, and prompts over Streamable HTTP, proxied publicly via Cloudflare Tunnel at a subdomain of `alfredopretelvargas.com`. No client talks directly to Postgres, to n8n, to the Telegram bot, or to the git repo. The MCP server is the only contract.

### 2.2 The Router is the sole context-assembly authority

The Router is a component **inside the MCP server**. No other system — no client, no background worker, no skill — performs context assembly. The Router has exactly these responsibilities:

1. **Classify** every incoming turn into `{bucket, project, skill, complexity, needs_lessons}` using Haiku 4.5.
2. **Load layers L0–L4** per §2.3, loading only what classification demands.
3. **Decide RAG activation**: whether to run lesson retrieval, tool-catalog retrieval, and project retrieval for this turn.
4. **Enforce token budgets** per §2.3 before returning context to the client.
5. **Resolve source conflicts** per §2.7 when multiple layers speak on the same topic.
6. **Log** every routing decision to `routing_logs` for cost audit and improvement.

The Router never reasons about the user's problem. That is the client-side model's job (Opus 4.7 or equivalent). The Router only decides what to feed it.

### 2.3 Context layers L0–L4 are the only context taxonomy

The system exposes exactly five context layers. No layer may be added, split, merged, or renamed without a constitutional amendment.

| Layer | Name | Source | Contents | Budget | Load rule |
|-------|------|--------|----------|-------:|-----------|
| L0 | Identity | Git (`identity.md`) | Operator identity, bucket names, tool catalog names, meta-rules | 500 tok | Always |
| L1 | Bucket | Git (`buckets/{bucket}/README.md` + sub-bucket files when present) | Bucket purpose, project index (recent + sub-bucket pointers), bucket rules | 1,500 tok | When bucket classified |
| L2 | Project | Git (`buckets/{bucket}/projects/{project}/`) | Project README + state +, for multi-module projects, the specific module file | 2,000 tok | When project classified |
| L3 | Skill / Procedural | Git (`skills/{skill}.md`) | Full methodology of a reusable skill | 4,000 tok | On-demand, when skill classified |
| L4 | Retrieved lessons | Postgres + pgvector | Top-K lessons by semantic similarity, filtered by bucket/tags | 1,500 tok | When `needs_lessons=true` |

Layers exceeding their budget trigger an automatic summarization task before serving. The Router never silently truncates. Write-time enforcement via pre-commit hook (see §7) blocks commits that push a layer over budget, forcing the operator to refactor instead of absorbing latency at read-time.

**L1 sub-bucket pattern (scalability at scale).** When a bucket's project count risks exceeding the L1 budget (empirically: ~15 active projects fills the budget with index + prose), the bucket splits into sub-buckets:

```
buckets/business/
├── README.md                                  # L1: overview + sub-bucket pointers + 5 most recent
├── freelance/
│   ├── README.md                              # sub-bucket L1: only loaded when bucket classified as 'business/freelance'
│   └── clients/
│       ├── README.md                          # paginated: 10 most recent + link to full index
│       ├── acme_corp/README.md                # L2: full project
│       └── biomex/README.md                   # L2
├── declassified/README.md                     # L2 (internal product, not freelance)
└── openclaw/archive/README.md                 # archived project index
```

The Router loads only the sub-bucket relevant to the current turn's classification — `business/freelance/clients` is a different L1 load from `business/declassified`. This bounds L1 at any scale. Detection of when to sub-bucket is automatic: the pre-commit hook (§7.36) signals when a bucket's README exceeds 1,200 tokens (80% of budget).

### 2.4 Git vs database is a strict boundary

Every persistent asset lives in exactly one of two places. Dual-homing is forbidden.

**Git (`pr3t3l/pretel-os` repo) — stable knowledge:**
- `identity.md`, `CONSTITUTION.md`, `PROJECT_FOUNDATION.md`, `DATA_MODEL.md`, `INTEGRATIONS.md`, `LESSONS_LEARNED.md`
- All content under `buckets/*/README.md`, `buckets/*/projects/*/*.md`
- All content under `skills/*.md`
- All SDD templates under `templates/`
- MCP server source code, schema migrations, worker source code
- `AGENTS.md` (the entry point any LLM reads first)

**Database (Postgres + pgvector, local or Supabase) — dynamic memory:**
- `lessons` (with embeddings)
- `tools_catalog` (with embeddings, usage_count, utility_score)
- `projects_indexed` (with embeddings, past-project retrieval)
- `project_versions` (snapshots of project state at decision boundaries)
- `conversations_indexed` (with embeddings)
- `cross_pollination_queue`
- `project_state` (live TODOs, active decisions, not in git)
- `routing_logs`, `usage_logs`
- `skill_versions` (history of skill changes)
- `patterns`, `decisions`, `gotchas`, `contacts`, `ideas`
- `reflection_pending` (degraded-mode queue for Reflection worker outputs when Sonnet is unreachable)
- `conversation_sessions` (live session ledger — session_id, client_origin, started_at, last_seen_at, closed_at)

A file-system asset that is dynamic, an embedding, a counter, a queue, or a log belongs in the database. A document that is reviewed, versioned, and read by humans or LLMs as canonical knowledge belongs in git. Anything ambiguous defaults to git until it demonstrates dynamic behavior that justifies migration.

### 2.5 Embeddings model is fixed

The system uses `text-embedding-3-large` (OpenAI, 3072 dimensions) for every embedding operation — writes and queries. Switching models requires a full reindex and a constitutional amendment. Queries embedded with one model and stored vectors embedded with another produce garbage; mixing is forbidden by construction.

### 2.6 Background workers are named and chartered

The system runs exactly four background workers. Each has a fixed charter, a trigger, and a home. No worker operates outside these boundaries.

| Worker | Trigger | Responsibility | Home |
|--------|---------|----------------|------|
| **Reflection** | Event: `close_session` (10 min idle), `task_complete` tool call, fallback every 20 turns, or fallback every 60 minutes of session lifespan (whichever fires first) | Read the transcript. Propose 0–3 lessons, 0–N cross-pollination flags, state updates to the active project. Insert lessons with `status='pending_review'`, write `cross_pollination_queue` and `project_state` rows. If Sonnet unreachable, queue to `reflection_pending` for later replay. | Python script on the Vivobook server, triggered by MCP |
| **Nightly consolidation (Dream Engine)** | Cron 02:00 America/New_York | Recompute `utility_score` on `tools_catalog` and `lessons`. Detect duplicates and contradictions. Expand pending cross-pollination entries. Archive low-utility lessons per §5.5. Summarize old conversations per §5.5. Reindex changed embeddings. Prepare morning-intelligence brief. | systemd timer on the Vivobook server |
| **Morning intelligence** | Cron 06:00 America/New_York | Deliver conversational Spanish voice + written brief via Telegram covering: critical changes, strategic AI news, macro and markets, business opportunities, professional edge. Max 15 items. | n8n workflow |
| **Auto-index on save** | Postgres trigger `ON INSERT` for rows lacking `embedding` | Compute the missing embedding and populate the column. | Python listener or `pg_cron` on the Vivobook server |

Any desire to add a fifth worker triggers a constitutional amendment. No ad-hoc cron jobs.

### 2.7 Source priority resolves conflicts between layers

Two distinct conflict-resolution regimes:

**(a) Immutable invariants — non-overridable.** The following rules from L0 are never subject to priority arbitration — they are preconditions, not context. If any lower layer contradicts them, the lower source is wrong and the invariant wins:

- Security and data-sovereignty rules in `CONSTITUTION §3` (Scout compliance, credential handling, Scout denylist)
- Token-budget ceilings per layer (§2.3)
- The Git/DB boundary (§2.4)
- The agent rules in §9 (no guessing parameters, no executing code by reading, etc.)

These are collectively the **immutable invariant class** of L0. They sit above the ordered resolution and are enforced structurally (pre-commit hooks, DB triggers, MCP middleware).

**(b) Contextual resolution — ordered priority.** For conflicts over non-invariant content (e.g., "which tool should we use for this task," "is Postgres the right database," "how should we structure this module"), the Router and the client-side agent apply this priority order (highest wins):

1. **L2 current project state** — the live reality of the active project. If the project state says "we decided to use Postgres", that is truth for this turn.
2. **L3 skill** — the methodology being executed. Skills override general lessons because the skill is the explicit procedure being followed.
3. **L4 lesson** — crystallized past learning. Lessons override general bucket rules because lessons encode specific discoveries.
4. **L1 bucket** — general rules for the domain.
5. **L0 contextual identity** — personal preferences, style, communication defaults (non-invariant parts of identity).

The agent never silently resolves conflicts. When a higher-priority source contradicts a lower one, the agent follows the higher one and mentions the conflict in its reasoning so the operator sees it. Conflicts are logged to `routing_logs.source_conflicts` JSONB so patterns emerge over time. If the higher-priority source is wrong, the operator corrects the source (not the agent's behavior on that turn).

If *any* source contradicts an immutable invariant, the invariant wins silently at the system level (write is blocked, tool refuses, etc.) and the agent receives a structured error rather than a context value.

---

## 3. Security and data sovereignty

1. **Scout bucket never stores proprietary employer data.** Patterns are abstract and reusable (e.g., "VBA InputBox pattern for context capture"). Concrete employer data (supplier names, internal specs, organizational details, financial figures, product roadmaps) is forbidden in any location: git, database, prompts, logs, or backups.
2. **Pre-commit hook enforces Scout security.** Any commit touching `buckets/scout/` runs a keyword filter. If the filter flags content, the commit is blocked pending human review. The filter lives at `.github/hooks/scout-guard.sh` and its denylist is editable only by the operator, never by an LLM.
3. **`save_lesson` enforces Scout abstraction.** Calls with `bucket=scout` run the denylist check before insert. Flagged content returns an error to the caller; the LLM must reformulate abstractly or cancel.
4. **Secrets never live in git.** API keys, tokens, connection strings, passwords live only in `.env` files listed in `.gitignore`, or in Supabase Vault, or in systemd environment files with `0600` permissions.
5. **Backups are encrypted at rest.** Daily backups to Supabase Storage or GitHub use AES-256 with a key stored offline (password manager).

---

## 4. Token economy and cost discipline

6. **L0 is always loaded. L1–L4 are loaded only when classification demands them.** The Router never loads layers reflexively.
7. **Layers respect their budgets** per §2.3. Over-budget content is summarized before serving; the Router never silently truncates.
8. **Classification runs on Haiku 4.5, never on Opus.** Reasoning runs on the client-side model (Opus 4.7 or equivalent). Reflection runs on Sonnet 4.6. Model-to-task mapping is immutable without amendment.
9. **Embeddings model is `text-embedding-3-large`.** Writes and queries use the same model. Per §2.5.
10. **Monthly API budget is explicit and tracked.** Phase 0–3 target: under $30/month combined (Anthropic + OpenAI). Overruns trigger an immediate audit and a lesson.
11. **Cloud spend is revenue-gated.** Migration from local Postgres/n8n to managed cloud services only after the associated product (Forge, Declassified, freelance) generates revenue covering the new spend with a 3x margin.

---

## 5. Memory, retrieval, and knowledge hygiene

### 5.1 Complexity classification drives retrieval behavior

Every turn is classified by the Router into one of three complexity levels. The level determines whether L4 (retrieved lessons) and tool-catalog retrieval fire. Agents never override this decision.

**LOW complexity — L4 never loads, tool-catalog never queried**
- Factual queries with an objectively correct answer ("what day is today", "what time is it in Tokyo")
- Casual conversation and greetings
- Single-step requests with no ambiguity ("list the files in this folder")
- Explicit acknowledgments or confirmations from the operator

**MEDIUM complexity — L4 loads conditionally, tool-catalog conditional**
- Structured tasks following a known workflow (executing a VETT phase, running the SDD spec template)
- Minor problem solving with obvious scope ("fix this typo", "add this field to the schema")
- Requests for information the system should already have indexed

Conditional means: the Router first runs a cheap lessons-count query filtered by bucket+tags. If zero matches, skip retrieval. If ≥1 match, load top-3 into L4.

**HIGH complexity — L4 always loads, tool-catalog queried**
- Debugging and investigation
- Architectural decisions and design choices with lasting consequences
- Multi-step reasoning over unfamiliar territory
- Requests for recommendation ("which should I choose", "how should I approach this")
- Problems the system has not seen before

### 5.2 Lessons

12. **Lessons are captured by event, not by turn count.** Triggers: `task_complete` tool call, `close_session` (10 minutes idle or explicit close), or fallback every 20 turns. Never by arbitrary N-message windows.
13. **Lessons are inserted with `status='pending_review'` before becoming canonical.** The `lessons` table has a single-table lifecycle per `DATA_MODEL §2.1` — `status` values are `pending_review | active | archived | merged_into | rejected`. Auto-approval (promoting from `pending_review` to `active` without operator intervention) is allowed only when a proposal matches all four conditions: has title + content, references a specific technology or pattern, includes a "next time" clause, and has no semantic duplicate already active (similarity < 0.92). Any proposal with similarity ≥ 0.92 to an existing active lesson is flagged as `merge_candidate` and routed to manual review — the system does not attempt to detect polarity or contradiction, since vector similarity cannot distinguish "always do X" from "never do X." Anything not auto-approved goes to manual review via Telegram `/review_pending`.
14. **Duplicate lessons are merged, not stacked.** Pre-save embedding similarity against existing lessons runs. Similarity ≥ 0.92 triggers a merge proposal instead of insert.
15. **Lessons are mandatory on significant issues.** Any bug, misconfiguration, or architectural surprise costing more than 30 minutes of debugging must be logged with evidence (error message, fix, preventive rule).
16. **The agent consults lessons per complexity classification** (§5.1). The Router pre-loads L4 when complexity is HIGH. For MEDIUM the Router checks filter-first whether any lessons exist before loading. For LOW it never loads. Agents never decide on their own whether to consult — the Router decides and pre-loads.

### 5.3 Tools catalog

17. **Every reusable tool or skill is registered in `tools_catalog`.** An unregistered tool is invisible to the recommendation system. Registration happens via `register_skill()` / `register_tool()` MCP tools, never manually.
18. **Tool recommendations use a published utility score.** Formula:
    ```
    utility_score = log(1 + usage_count)
                  + recency_weight(last_used)
                  + 2 * cross_bucket_count
                  + manual_boost
    ```
    Recomputed nightly by the Dream Engine (§2.6). The Router uses utility score + semantic similarity to rank recommendations. Ties break toward higher cross-bucket reach (favor reusable tools).
19. **Tools are surfaced by name in L0 and by detail via MCP.** L0 holds only tool names and one-line descriptions (fits in the 500 tok budget). When a tool is needed, the agent calls `load_skill(name)` to retrieve full procedural memory (L3). This prevents L0 bloat as the catalog grows.

### 5.4 Cross-pollination

20. **Cross-pollination is a first-class signal.** When the Reflection worker detects that an insight applies to a bucket other than its origin, it writes to `cross_pollination_queue` with status `pending`, including origin_bucket, target_bucket, idea, and reasoning.
21. **Queue entries never expire silently.** They are reviewed via Telegram `/cross_poll_review` or explicitly dismissed with reason. The Dream Engine highlights items pending more than 14 days in the morning brief.

### 5.5 Knowledge lifecycle (archival, degradation, retention)

22. **Lessons with sustained low utility are archived, not deleted.** During nightly Dream Engine run, any lesson meeting all three conditions has its `status` set to `archived` (same row, excluded from default retrieval):
    - `usage_count = 0` after 180 days from creation
    - `utility_score < 0.5` over the past 90 days
    - Not referenced by any active project in `project_state`

    Archived lessons remain queryable via explicit `search_lessons(include_archive=true)` but do not count toward token budgets or default retrieval.

23. **Conversations older than 90 days are summarized, not kept raw.** The Dream Engine replaces raw `conversations_indexed` rows with a summary row (original embedding preserved, original text replaced with 200-token summary). This keeps retrieval working while controlling storage and noise.

24. **Duplicate detection runs nightly, not only on insert.** Pre-save dedup (§5.2 rule 14) catches obvious duplicates. Nightly the Dream Engine runs a deeper pass: any two lessons with similarity ≥ 0.95 generate a merge proposal written to `cross_pollination_queue` with `proposal_type='merge_candidate'`. The operator reviews, approves, or dismisses via Telegram. Approved merges set the losing lesson's `status='merged_into'` and populate `merged_into_id`.

25. **Project snapshots preserve history at decision boundaries.** When a major architectural decision changes a project's state (ADR-equivalent inside a project), the MCP tool `snapshot_project(project, reason)` writes the current L2 content to `project_versions` with timestamp and reason. This is called automatically by `add_module`, `change_stack`, and similar structural operations, and can be called manually by the operator. Answers "how did we do this before" without relying on git archaeology.

### 5.6 Scalability of memory

26. **Retrieval scales by filter before similarity.** Every retrieval query applies bucket/project/tag filters first, then runs semantic search within the filtered subset. At 100+ freelance clients, this keeps query latency flat.
27. **Projects are lazy-loaded.** Only the active project's L2 is loaded per turn. Sibling projects in the same bucket are referenced by the bucket README (one line each) and retrieved on demand via `search_projects_indexed()`.
28. **Multi-module projects follow the project/modules split.** Large projects (> ~2,000 tokens of description) must split into `buckets/{b}/projects/{p}/README.md` (overview + module index) plus `buckets/{b}/projects/{p}/modules/*.md` (one file per module). Loading one module does not load siblings.
29. **L2 never loads more than one module file per turn by default.** When a turn needs content from multiple modules, the agent first requests a `list_modules(project)` call to see options, then explicitly requests each module. Default loading of "all modules because the project is complex" is forbidden — that path leads to context explosion. The Router enforces this: project README + single classified module, period.
30. **Historical projects remain queryable via `projects_indexed`.** Closed projects move out of the active L1 index but stay retrievable by semantic search, enabling "we built this 14 months ago" recall.

---

## 6. SDD process compliance

31. **Spec before code.** No module is implemented before its `spec.md`, `plan.md`, and `tasks.md` are written and pass their respective gates (explainable in 2 minutes / every phase has "done when" / every task < 30 minutes).
32. **Two consecutive task failures halt implementation.** The spec is revisited before any further attempt. Forcing a fix is forbidden.
33. **Documentation lives in the doc registry.** If a document is not listed in `PROJECT_FOUNDATION.md §Doc Registry`, it does not exist for the system. Unlisted documents are deleted during monthly hygiene.
34. **Git commits are atomic per task.** One task = one commit. Message format: `[MODULE/TASK-XX] description`. No "WIP" commits on `main`.

---

## 7. Tool usage and execution discipline

35. **State mutations go through MCP tools, never direct file writes by LLMs.** Creating a project, adding a module, registering a skill, saving a lesson — all through MCP tools that handle scaffolding, updates to parent layers, and git commits atomically.

36. **Cross-layer synchronization is mandatory and automatic.** Any operation that creates, modifies, or removes an entity at layer N must update the parent layer N-1 in the same atomic operation. The MCP tools below own these updates; LLMs and humans invoke the tools, they do not write files directly:

    | Tool | Triggers update at |
    |------|--------------------|
    | `create_project(bucket, name, ...)` | L1 bucket README (adds project to index) |
    | `close_project(bucket, name)` | L1 bucket README (moves to archived section) + `projects_indexed` (insert) |
    | `add_module(bucket, project, module, ...)` | L2 project README (adds module to index) |
    | `remove_module(bucket, project, module)` | L2 project README (removes) |
    | `register_skill(name, ...)` | L0 identity (adds skill name + 1-line description) + `tools_catalog` insert |
    | `register_tool(name, ...)` | L0 identity (adds tool name + 1-line description) + `tools_catalog` insert |
    | `deprecate_skill(name)` | L0 identity (removes line) + `skill_versions` (final entry) |
    | `create_bucket(name, ...)` | L0 identity (adds bucket name) |
    | `change_stack(project, new_stack)` | L2 project README (updates stack) + `snapshot_project` (auto-triggered) |

    A manual file edit that bypasses these tools is a violation. CI check runs on every PR to detect orphaned layer entries (child without parent index line or parent index line without child file).

    **Write-time token budget enforcement.** A pre-commit hook at `infra/hooks/pre-commit-token-budget.sh` counts tokens (via `tiktoken` with the `cl100k_base` encoding for ballpark parity with Claude tokenization) on every modified markdown file and blocks the commit if any layer exceeds its budget:

    - L0 `identity.md` > 500 tokens → commit blocked
    - L1 `buckets/{b}/README.md` > 1,500 tokens → commit blocked (signals time to sub-bucket per §2.3)
    - L2 `buckets/{b}/projects/{p}/README.md` > 2,000 tokens → commit blocked (signals time to split into modules)
    - L3 `skills/*.md` > 4,000 tokens → commit blocked (signals time to split the skill)

    The hook advises the corrective action in its error message — it never truncates silently, and it never runs at read-time where latency would spike (per GPT audit FINDING-004 and Gemini-adv FINDING-004). Read-time summarization remains as a belt-and-suspenders fallback only.

37. **LLMs never execute code by reading it.** Code execution happens only through explicit MCP tools (`run_finance_analysis`, `run_forge_pipeline`, `run_vett_phase`, etc.) that spawn real subprocesses via `subprocess.run()` or HTTP calls to n8n webhooks. An LLM simulating a Python script mentally is a violation. Every executable procedure ships as an MCP tool wrapping the real execution; the agent's only way to run it is to call the tool.

38. **LLMs do not guess MCP tool parameters.** When uncertain, the agent calls `tool_search` first to load the exact schema.

---

## 8. Client portability and reliability

39. **No client lock-in.** pretel-os must remain usable from Claude.ai web, Claude Code, Claude mobile, and any future MCP-compatible client without code changes. Client-specific assumptions in the MCP server are forbidden.

40. **The MCP server is stateless.** All persistent state lives in Postgres. The MCP process can be killed and restarted at any time without data loss.

41. **Git repo is the portable brain.** A `git clone` plus environment setup on any Linux machine reconstructs the full system. No implicit state on the host OS beyond what the repo or database contains.

42. **Routing logic is server-side, not client-side.** Clients call `get_context(message)` and receive pre-assembled context. Clients never implement their own layer-loading, their own RAG, or their own classification. This preserves sovereignty — switching clients does not change behavior.

43. **Degraded mode is a first-class operating state.** The MCP server must continue serving when downstream components fail. Three design requirements:

    (a) **Lazy DB initialization.** The MCP server starts and registers its tools with clients regardless of Postgres availability. It does NOT block startup on DB connection. A global `db_healthy` boolean is set at startup and refreshed every 30 seconds by a background health check. Tool functions check `db_healthy` at execution time and return degraded-mode payloads when false. This prevents startup deadlock per GPT audit FINDING-003.

    (b) **Fallback-file contract for DB outages.** When `db_healthy=false`, mutation tools persist their intended writes to a local append-only JSONL at `/home/operator/pretel-os-data/fallback-journal/YYYYMMDD.jsonl` with mode 0600. Each line contains: `{journal_id: uuid, ts: iso, operation: 'save_lesson'|'snapshot_project'|..., payload: {...}, idempotency_key: sha256(operation+payload+ts_minute)}`. File is encrypted at rest (LUKS on the data volume); no additional app-level encryption needed. On DB recovery, a dedicated `journal_replay` worker processes the file in order, using `idempotency_key` to skip already-applied writes, and moves processed lines to `fallback-journal/processed/`. Replay is idempotent by design — re-running is safe. Failed replays after 5 attempts escalate to a Telegram alert with the offending journal_id. Journal retention: 90 days after processing.

    (c) **Per-integration degraded behavior:**
    - **Postgres unreachable**: Router operates in `git-only` mode. L0, L1, L2, L3 continue to serve from the git repo. L4 (lessons) returns an explicit "retrieval unavailable" marker instead of silent empty results. Tool-catalog returns only the L0-embedded names. State mutations (`save_lesson`, `snapshot_project`, `update_project_state`) return `{status: 'degraded', journal_id: ...}` with the write persisted to the fallback journal per (b).
    - **OpenAI embeddings API unreachable**: writes that need new embeddings queue to `pending_embeddings` table; reads against existing embeddings continue normally. Dream Engine flushes the queue when the API returns.
    - **Anthropic API for Haiku classification unreachable**: Router falls back to a rule-based classifier (keyword + regex match against bucket/project names in L0) and returns results with `classification_mode=fallback_rules` flag.
    - **Sonnet unreachable (Reflection worker)**: pending reflection payloads queue to `reflection_pending` table per `DATA_MODEL §4.5`; retried by Dream Engine.
    - **n8n down**: Forge pipeline and Morning Intelligence are skipped with logged incidents. Router and core retrieval continue normally.
    - **Telegram bot down**: outbound notifications queue in memory (bounded 100 most recent); operator uses Claude.ai web as fallback interface.
    - **Hard failure** (MCP process itself down): clients receive the MCP framework's standard disconnection error. Clients are responsible for showing this to the operator; no silent failure is acceptable.

    Every degraded response carries a `degraded_mode=true` flag plus a human-readable `degraded_reason`. The agent surfaces the reduced-functionality state to the operator rather than pretending everything works.

44. **Timeouts and retries are explicit.** Every external call (OpenAI, Anthropic, n8n, Supabase) has a declared timeout in configuration (`infra/timeouts.yaml`). Retries use exponential backoff with jitter, maximum 3 attempts. Silent retries that hide failures are forbidden.

---

## 9. AI agent rules

These rules apply to any LLM operating within or through pretel-os (Claude via MCP, Claude Code with the repo loaded, the Reflection worker, the Dream Engine's LLM calls).

1. The agent does not decide whether to consult lessons. The Router decides via `complexity` classification (§5.1) and pre-loads L4. The agent uses what arrives.
2. The agent never fabricates attributions. If unsure of a source, the agent omits the claim.
3. The agent never guesses parameter names for MCP tools. It calls `tool_search` first when uncertain.
4. The agent does not bypass the pre-commit Scout guard by rewriting content until the filter passes. The filter flagging content is a signal to reconsider, not an obstacle to circumvent.
5. The agent writes lessons only when a real loop closed (problem encountered and resolved) or when the Reflection worker proposes one from transcript analysis. It does not fabricate lessons to appear productive.
6. The agent's memory of past conversations comes only from `conversations_indexed` retrieval or the MCP memory tools, never from context-window guessing.
7. The agent does not simulate code execution. If a procedure needs to run, the agent calls the corresponding MCP tool. If no tool exists, the agent proposes creating one before proceeding.
8. The agent honors source priority per §2.7. When layers disagree, it follows the higher-priority source and explicitly surfaces the conflict rather than silently reconciling.
9. The agent never bypasses the cross-layer sync tools per §7.36. Creating a project means calling `create_project`, not writing a README file directly.

---

## 10. Amendment process

A rule in this document changes only when:

1. An explicit decision-log entry is added to `PROJECT_FOUNDATION.md §Decisions` stating: context, rule being changed, old text, new text, rationale, date, author.
2. The CONSTITUTION.md file is updated with the new rule text and the `Last updated` field is bumped.
3. The change is committed with message format `[CONSTITUTION] Amend rule X.Y: brief reason`.

No rule is changed through conversation alone. Speech is not law; the commit is.
