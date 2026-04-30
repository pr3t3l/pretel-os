# LESSONS LEARNED — pretel-os

**Status:** Active
**Last updated:** 2026-04-30
**Owner:** Alfredo Pretel Vargas
**Primary storage:** Postgres `lessons` table (see `DATA_MODEL.md §2.1`)
**Git export:** `exports/lessons_YYYYMMDD.yaml` (weekly, produced by Dream Engine)

This document is the **process reference** for how lessons are captured, categorized, reviewed, retrieved, and retired in pretel-os. The actual lesson content lives in the database; this document defines the rules, schema, and lifecycle that govern that content. It also seeds the initial corpus with lessons already learned during foundation design.

---

## 1. Where lessons live

### 1.1 Primary: database

Every lesson is a row in the `lessons` table. The table has embeddings for semantic retrieval, a status enum for lifecycle, cross-references to tools and projects, and utility scoring for ranking. Per `CONSTITUTION §2.4`, this is the only source of truth for active lesson content.

### 1.2 Secondary: weekly YAML export in git

Every Sunday at 02:30 local (run by Dream Engine, per `CONSTITUTION §2.6`), all active lessons are exported to `exports/lessons_YYYYMMDD.yaml` and committed to the `pretel-os` repo. Purpose:

- **Human readability** — YAML diff-able in PRs, readable without DB tooling.
- **Offline access** — if Postgres is unreachable, the git export is the fallback corpus for manual lookup. Degraded-mode retrieval (`CONSTITUTION §8.43`) reads from this file when the DB is down.
- **Historical archive** — `git log exports/` shows how the corpus evolved.
- **Migration safety** — if the DB ever needs to be rebuilt from scratch, the most recent YAML export is the restore source.

The export file is generated, not edited. Manual edits are discarded on the next run.

### 1.3 Why not YAML-only (previous OpenClaw approach)

The prior OpenClaw system stored lessons in `LL-MASTER.yaml` directly. That worked at 89 entries. It does not scale:

- At 500 entries a single-file load exceeds 60k tokens — unusable as context.
- No semantic search — the only queries are `grep` and eyeballing.
- No lifecycle automation — archive, merge, and dedup require bespoke scripts.
- No cross-pollination detection — embeddings are required for that.

Per `ADR-007`, lessons move to Postgres + pgvector. Per this document §1.2, the YAML export preserves the OpenClaw-era benefits (diff, human reading, backup) without the scale limits.

---

## 2. Schema mapping

The database schema (`DATA_MODEL §2.1`) maps to the OpenClaw-era YAML fields as follows. Any future migration in either direction uses this mapping.

| OpenClaw YAML field | pretel-os DB column | Notes |
|---------------------|---------------------|-------|
| `id` (e.g., `LL-PLAN-001`) | derived from `category` + row number | Not stored explicitly; rendered on export |
| `date` | `created_at` | `TIMESTAMPTZ` |
| `category` | `category` | Enum-like (see §3) |
| `severity` | `metadata.severity` | `'critical' \| 'moderate' \| 'minor'` |
| `system` | `bucket` + `metadata.system` | Bucket covers the domain; `system` covers sub-system |
| `status` | `status` (enum) | `pending_review \| active \| archived \| merged_into \| rejected` |
| `problem_statement` | `content` (first paragraph) | |
| `immediate_cause` | `content` (section) | |
| `root_cause` | `content` (section) | |
| `contributing_factors` | `content` (section) | |
| `failed_attempts` | `content` (section) | |
| `solution` | `content` (section) | |
| `prevention_action` | `next_time` | Single-sentence preventive rule |
| `keywords` | `tags` | `TEXT[]` |
| `applies_to` | `related_tools` + `applicable_buckets` | See §3.2 |
| `references` | `metadata.references` | External links, LL cross-refs |
| `validated` | `metadata.validated` | `BOOLEAN`, set when enforcement is confirmed working |
| (new) | `related_tools` | Tools/skills this lesson is about |
| (new) | `embedding` | 3072-dim vector for RAG |
| (new) | `utility_score` | Recomputed nightly |
| (new) | `usage_count`, `last_used_at` | Filled by retrieval logs |

### 2.1 The `content` field is structured Markdown

To preserve the richness of the OpenClaw format without fragmenting it across many columns, `content` holds structured Markdown with fixed subsections:

```markdown
## Problem
[What went wrong — specific, observable]

## Evidence
[How you know — logs, error messages, time/cost lost]

## Root cause
[Why it happened, at the right level of abstraction]

## Fix
[What was done to resolve it]

## Failed attempts
- [Attempt 1 — why it didn't work]
- [Attempt 2 — what happened]

## Enforced by
[Script, validator, test, or process that prevents recurrence.
"Manual discipline" is NOT enforcement.]
```

The Reflection worker and the Auto-index worker both know this structure and extract the relevant sentences when generating embeddings (embedding is computed over `title + full content` to maximize retrieval recall).

---

## 3. Categories

Ten categories. No subcategories. Adding a new category requires a decision-log entry per `CONSTITUTION §10`.

| Code | Name | What belongs here |
|------|------|-------------------|
| PLAN | Planning | Wrong scope, missing requirements, unrealistic estimates, spec failures |
| ARCH | Architecture | Design decisions that were wrong, coupling/decoupling mistakes, layer violations |
| CODE | Code-level | Bugs and patterns in specific code. Library quirks. Language gotchas. |
| COST | Cost | Budget surprises, unexpected API spend, resource sizing errors |
| INFRA | Infrastructure | WSL, Linux, networking, deployment, systemd, Docker, Postgres ops |
| AI | AI/LLM behavior | Model-specific quirks, prompt patterns that fail, context-window issues |
| DATA | Data & schemas | Schema migration pain, query performance, data integrity |
| SEC | Security | Credential handling, permission escalation, Scout compliance, sanitization |
| OPS | Operations | Incident response, downtime handling, on-call patterns |
| PROC | Process | Workflow failures, git hygiene, documentation drift, coordination |

### 3.1 Category selection rule

Pick the category that best describes **where the preventive rule applies**, not where the symptom appeared. A Postgres query that slowed down because of a bad plan is ARCH, not DATA, if the fix is "think about indexes earlier." A Scout lesson is SEC only if the rule is about security; if it's about how to structure Scout content, it's PROC.

### 3.2 `applies_to` vs `related_tools`

- `applicable_buckets` (array) — which buckets can benefit from this lesson. Used by the Router's filter-first retrieval per `CONSTITUTION §5.6 rule 26`.
- `related_tools` (array) — specific tools or skills this lesson is about. Used by the reverse lookup view `v_tool_lessons` to answer "which tool has the most lessons about it?" per `DATA_MODEL §7`.

A lesson can have both: "VETT phase 3 sometimes returns empty when web search fails" has `applicable_buckets=['business','scout']` and `related_tools=['vett']`.

---

## 4. Severity

Three levels. Stored in `metadata.severity`. Used to prioritize review and to weight utility score slightly.

| Level | Emoji | Criteria |
|-------|:---:|----------|
| Critical | 🔴 | Cost > $50, time lost > 4 hours, user-facing failure, or security incident |
| Moderate | 🟡 | Cost $5–$50, time lost 30 min – 4 hours, recoverable with workaround |
| Minor | 🟢 | Cost < $5, time lost < 30 min, informational |

Severity is the operator's judgment, not automatic. The Reflection worker proposes a level; the operator adjusts during review.

---

## 5. Lifecycle

Every lesson moves through this state machine. Transitions are logged; skipping states is forbidden.

```
proposed ──┐
           ↓
      pending_review ──→ active ──→ archived
           │                │
           │                ↓
           │           merged_into (another lesson)
           │
           └─→ rejected
```

### 5.1 `pending_review`

Entry point. Created by:
- The Reflection worker when a session closes or a task completes (`CONSTITUTION §5.1 rule 12`).
- The operator directly via Telegram `/save <text>` or MCP tool `save_lesson(..., auto_approve=false)`.

Must have: title, content with at least the Problem and Fix sections, bucket, category, tags.

### 5.2 → `active`

Promoted when one of:

1. **Operator review.** Operator sees the lesson in Telegram `/review_pending` and approves. This is the default path.
2. **Auto-approval.** All four conditions met per `CONSTITUTION §5.1 rule 13`:
   - Has title + content
   - References a specific technology or pattern
   - Includes a `next_time` (prevention_rule) clause
   - Does not contradict an existing active lesson (semantic similarity < 0.92 with any existing lesson of opposite advice)

Rejected proposals go to `rejected` with operator reason.

### 5.3 → `archived`

By the Dream Engine per `CONSTITUTION §5.5 rule 22`:
- `usage_count = 0` after 180 days from creation
- `utility_score < 0.5` over the past 90 days
- Not referenced by any active project in `project_state`

Archived lessons remain queryable with `include_archive=true` in `search_lessons()`. They don't count toward default retrieval or the L4 budget.

### 5.4 → `merged_into`

Pre-save dedup (similarity ≥ 0.92) or nightly dedup (similarity ≥ 0.95) per `CONSTITUTION §5.5 rule 24` triggers a merge proposal. Operator approves the merge in Telegram. The losing lesson sets `status='merged_into'` and its `merged_into_id` points to the surviving lesson. The surviving lesson accumulates the usage counts.

### 5.5 → `rejected`

Only the operator rejects. Usually because the proposal was noise (Reflection worker false positive) or the "lesson" was too specific to be reusable. The rejected row stays in the table (for auditing) but never appears in retrieval.

---

## 6. Capture triggers

Per `CONSTITUTION §5.1 rule 12`, lessons are captured by event, never by turn count.

**Automatic triggers:**

1. **`task_complete` tool call** — the agent explicitly signals a loop closed.
2. **`close_session`** — 10 minutes of inactivity, or operator explicitly closes.
3. **Fallback** — every 20 turns of the same session, the Reflection worker fires even if no explicit close.

**Manual triggers:**

- Operator sends `/save_lesson <text>` via Telegram.
- Operator calls `save_lesson(...)` via MCP tool directly.
- Operator records a voice note — bot transcribes, then routes to `save_lesson`.

### 6.1 Mandatory capture

Per `CONSTITUTION §5.1 rule 15`, these situations mandate capture regardless of triggers:

- Any bug or misconfiguration that cost more than 30 minutes of debugging.
- Any task that had to be redone after the first completion.
- Any cost surprise where actual spend exceeded estimate by 2x.
- Any architectural assumption proven wrong during implementation.
- Any AI/model behavior that was unexpected (e.g., a prompt that worked yesterday and fails today).
- Any incident that affected the operator's workflow or real users.

---

## 7. Review process

### 7.1 Telegram `/review_pending`

The operator reviews the queue in batches, typically weekly on Sunday morning after the Dream Engine run. The bot presents pending lessons one at a time:

```
[LL-INFRA pending #12]
Title: Cowork Dispatch timeout on LiteLLM calls
Content: [truncated preview]
Proposed tags: cowork, litellm, tmux, timeout
Severity: 🟡 moderate
Auto-approval eligible: NO (contradicts LL-INFRA-003)

Actions:
  [Approve] [Edit] [Reject] [Merge into LL-INFRA-003]
```

### 7.2 Cross-pollination review (`/cross_poll_review`)

Separate from lesson review. Operator sees entries in `cross_pollination_queue` and decides: apply, dismiss, or merge. Per `CONSTITUTION §5.4 rule 21`, entries never expire silently; the Dream Engine surfaces items pending more than 14 days.

### 7.3 Merge review

When the Dream Engine proposes a merge (similarity ≥ 0.95), the operator decides which lesson wins. Default: the one with higher `utility_score`. The operator can override and consolidate content from both into the winner.

---

## 8. Migration of existing 89 lessons

Scope: `LL-MASTER.yaml` (OpenClaw) + `LL-FORGE.yaml` — 89 total entries across PLAN, ARCH, COST, INFRA, AI, CODE, DATA, OPS, PROC.

### 8.1 Approach

Ten steps, mapped to `Module 8: lessons_migration` (`PROJECT_FOUNDATION §4`):

1. **Export** existing YAML to a staging directory in the pretel-os repo.
2. **Validate** schema against this document's §2 mapping — flag any OpenClaw fields that don't map cleanly.
3. **Transform** each YAML entry into an `INSERT INTO lessons_pending_review` statement with `source='migration_LL-MASTER'` or `source='migration_LL-FORGE'`.
4. **Auto-index** kicks in on insert; embeddings are computed in batch via OpenAI's Batch API (50% discount — one-time cost, no rush).
5. **Dedup pass** after embeddings are populated — run `find_duplicate_lesson()` cross-check on the whole imported set. Flag any pairs at similarity ≥ 0.92 for merge review.
6. **Operator batch review** via `/review_pending` — expected ~60 entries with auto-approval eligible, ~30 need manual review (failed_attempts=unknown per `MIGRATION_TODO.md`).
7. **Promote** approved entries to `status='active'`.
8. **Tag gaps** — during review, any entry with missing failed_attempts gets the section left blank rather than fabricated. The Reflection worker will fill these in organically as the gaps become relevant.
9. **Verify retrieval** — seed test: query "n8n batching" — should return the 3 relevant lessons from the migration. Query "Scout VBA inputbox" — should return the relevant patterns.
10. **Delete staging** — YAML staging files removed after successful migration, retained only in git history.

### 8.2 Known gaps documented in the migration

From the prior migration's `MIGRATION_TODO.md`:
- 9 entries with `severity=unknown` — operator assigns during review.
- 61 entries with `failed_attempts=unknown` — these remain blank. The pattern is captured; what was tried before isn't critical if the fix is clear.
- Some entries need `validated=true` set based on current Forge state — operator confirms.

### 8.3 Category remapping

The OpenClaw YAML used category codes that largely match pretel-os. Two small renames:
- OpenClaw's unused category slots (if any) are dropped.
- The new `SEC` category (not in prior migration) absorbs any security-related entries previously classified as INFRA or OPS. The operator reviews each candidate during step 6.

### 8.4 Success criteria

Per `PROJECT_FOUNDATION §4 Module 8`: `SELECT count(*) FROM lessons WHERE source LIKE 'migration_%'` in the range 75–89 after dedup. Every row has a non-null embedding. A test query for "n8n batching" returns the correct lesson in top-3.

---

## 9. Seed lessons from foundation design (2026-04-16 to 2026-04-18)

Ten lessons already learned during the four-document foundation cycle of pretel-os itself. These are inserted into `lessons_pending_review` on Module 8 completion (not before — the table must exist first), then promoted to `active` by the operator in batch review. They bootstrap the corpus with real learnings about how to run this kind of project.

### LL-PROC-001 — Dogfood the methodology before selling it

**Category:** PROC / **Severity:** 🟢 minor / **Bucket:** business

**Problem.** An earlier impulse was to start building pretel-os in code without first applying SDD to it. SDD was treated as a tool for other projects, not for itself.

**Evidence.** Prior stack (OpenClaw) accumulated architectural decisions without documentation and reached a state where debugging cost more than rebuild.

**Fix.** Apply the full SDD process to pretel-os: CONSTITUTION → PROJECT_FOUNDATION → DATA_MODEL → INTEGRATIONS → module specs, before any code.

**Next time.** When building a project that operationalizes a methodology you plan to sell, use the methodology on itself first. Dogfooding catches spec gaps before external clients see them.

**Tags:** sdd, dogfooding, methodology, freelance
**Related tools:** sdd

---

### LL-PROC-002 — Cross-model review has diminishing returns after round 2

**Category:** PROC / **Severity:** 🟡 moderate / **Bucket:** business

**Problem.** Running the same document through GPT + Gemini + Opus adversarial review repeatedly starts producing false positives — reviewers invent gaps that the document already covers.

**Evidence.** Round 1 of foundation review found ~15 real gaps. Round 2 found ~6 real gaps. Round 3 produced 6 "critical" gaps, all of which were false positives (the doc covered every one explicitly).

**Fix.** Cap cross-model review at 2 rounds per document. On round 3, if the reviewer invents gaps, stop iterating and ship.

**Next time.** When a reviewer's feedback starts listing concerns the doc already addresses textually, that's the signal to close the review cycle — not to defend point by point.

**Tags:** review, cross-model, process, diminishing-returns
**Related tools:** sdd

---

### LL-ARCH-001 — The Router belongs in the MCP server, not in a wrapper

**Category:** ARCH / **Severity:** 🔴 critical / **Bucket:** business

**Problem.** Temptation was to put context-routing logic in OpenClaw or in each client application. Both paths couple routing to a specific stack and make multi-client portability impossible.

**Evidence.** OpenClaw's context-routing responsibility was entangled with Telegram bot lifecycle, LiteLLM proxy config, and cron jobs. Debugging took days.

**Fix.** Router is a named component inside the MCP server. Clients call `get_context(message)` and receive pre-assembled context. No client-side routing, ever.

**Next time.** If a piece of logic needs to behave identically across clients, it belongs on the server side of the client-server boundary — always.

**Tags:** router, mcp, architecture, portability
**Related tools:** mcp_server

---

### LL-ARCH-002 — Event-triggered reflection, never turn-count triggered

**Category:** ARCH / **Severity:** 🟡 moderate / **Bucket:** business

**Problem.** Initial proposal was "reflect every 100 messages." Most sessions never reach 100 messages, so reflection rarely fired; the system stopped learning.

**Evidence.** Median session length was 12–30 turns. At N=100, reflection fired less than once per week.

**Fix.** Trigger by event: `task_complete`, `close_session` (10-min idle or explicit), or fallback every 20 turns. Whichever arrives first.

**Next time.** When designing a periodic trigger, verify the actual distribution of the underlying event. "Every N units" only works if N is calibrated to empirical distribution.

**Tags:** reflection, triggers, distribution, design
**Related tools:** reflection_worker

---

### LL-DATA-001 — Single table with status enum beats parallel pending/archive tables

**Category:** DATA / **Severity:** 🟢 minor / **Bucket:** business

**Problem.** First draft had `lessons`, `lessons_pending_review`, and `lessons_archive` as three separate tables. Queries required UNION across tables. Dedup across them was painful.

**Evidence.** Pre-save dedup logic had to check three tables in sequence. Merge operations required cross-table MOVE.

**Fix.** Single `lessons` table with `status` enum (`pending_review | active | archived | merged_into | rejected`). All queries add `WHERE status = ...`. Partial HNSW index targets only `status='active'`.

**Next time.** When the "same entity in different states" pattern appears, reach for a status enum before a second table. Parallel tables are appropriate only when schema diverges meaningfully.

**Tags:** schema, enum, dedup, lifecycle
**Related tools:** postgres

---

### LL-COST-001 — Reject micro-optimization without numbers

**Category:** COST / **Severity:** 🟡 moderate / **Bucket:** business

**Problem.** A reviewer pressed three times to switch embeddings from `text-embedding-3-large` to `text-embedding-3-small`, citing "optimization."

**Evidence.** Actual cost delta at projected volume: 6 cents per month. Precision delta on MTEB retrieval: +3.7 points for 3-large. Storage delta: 60 MB vs 120 MB (both well under free tier 500 MB).

**Fix.** Produced the numbers once, refused the change, moved on. Held the line across three rounds.

**Next time.** When pushback feels principled but vague, compute the actual delta before conceding. A measured 6-cent difference is not a reason to reduce precision by 3.7 points in a retrieval system where missed matches fail silently.

**Tags:** optimization, embeddings, cost, decision-discipline
**Related tools:** openai_embeddings

---

### LL-PROC-003 — Spec-driven development for the project that builds SDD

**Category:** PROC / **Severity:** 🟢 minor / **Bucket:** business

**Problem.** Pretel-os could have been built "agent-first" — start with MCP code, iterate. Given the complexity (15+ modules, multi-client, cross-bucket), this would have produced a second OpenClaw.

**Evidence.** OpenClaw's failure mode was accreting architecture without documentation. Replicating that would destroy the project's premise.

**Fix.** Four foundation documents before any code: CONSTITUTION, PROJECT_FOUNDATION, DATA_MODEL, INTEGRATIONS. Plus this LESSONS_LEARNED. Plus per-module specs.

**Next time.** For any project with > 10 modules or > 3 distinct integrations, write the foundation documents before the first line of code. The up-front cost (1–2 weeks) is dwarfed by the debugging cost it avoids (months).

**Tags:** sdd, foundation, planning, discipline
**Related tools:** sdd

---

### LL-AI-001 — Defense in depth for agent-generated content

**Category:** SEC / **Severity:** 🔴 critical / **Bucket:** scout

**Problem.** Relying solely on an MCP tool's Scout guard is single-layered. If a future code path or direct SQL bypasses the MCP tool (operator error, new tool forgot the check), Scout data could leak.

**Evidence.** Single-layer filters have a history of being bypassed by innocent refactoring.

**Fix.** Two layers: (1) MCP tool `save_lesson` filters before insert. (2) Postgres trigger `trg_scout_safety_lessons` refuses inserts or updates where `bucket='scout'` and content matches the denylist.

**Next time.** For security-critical filters, implement at two independent layers that can't both be bypassed by the same code change.

**Tags:** scout, security, defense-in-depth, triggers
**Related tools:** postgres, mcp_server

---

### LL-ARCH-003 — Git and DB have non-overlapping responsibilities

**Category:** ARCH / **Severity:** 🟡 moderate / **Bucket:** business

**Problem.** Before formalizing `CONSTITUTION §2.4`, the plan drifted toward dual-homing some assets in both git and DB for "safety."

**Evidence.** Every dual-homed asset becomes a sync problem. The prior stack had several and they all drifted.

**Fix.** Strict boundary: stable human-curated knowledge in git, dynamic embedded/counted/queued data in DB. Weekly YAML export bridges them without dual-homing: the export is a snapshot, not a source.

**Next time.** When the question is "should this live in git or the database?", the answer is one or the other, never both. If the instinct says "both for safety," replace it with "one authoritative source plus a scheduled snapshot."

**Tags:** git, database, boundaries, single-source-of-truth
**Related tools:** postgres

---

### LL-PROC-004 — Documentation has a threshold; beyond it, ship

**Category:** PROC / **Severity:** 🟢 minor / **Bucket:** business

**Problem.** The foundation review cycle started producing diminishing returns while feeling important. Continuing would have delayed implementation indefinitely without meaningful quality gain.

**Evidence.** Round 1 review: 15 real gaps, high value. Round 2: 6 real gaps, medium value. Round 3: 0 real gaps, 6 false positives, high cost (operator time, model cost, decision fatigue).

**Fix.** Recognize the inflection point — when the reviewer starts listing gaps the document covers, the review cycle is done. Applied to 4 of 4 foundation documents.

**Next time.** Track review-round value quantitatively. When the ratio of real findings to false positives inverts, close the review and move to implementation.

**Tags:** review, diminishing-returns, shipping, decision-fatigue
**Related tools:** sdd

---

### LL-M4-PHASE-A-001 — Integration tests catch what mock fidelity cannot

**Severity:** critical
**Captured:** 2026-04-28 during M4.A.4.3 review.

**Problem:** In `_build_telemetry`, the local variable `provider_metadata` was computed correctly (~991 chars from `response.model_dump()`) but never passed to `ChatJsonTelemetry(...)` constructor. The dataclass field had `default_factory=dict`, so the constructor used `{}` silently. Six mocked unit tests asserted shape (`isinstance(telemetry, ChatJsonTelemetry)`) and individual numeric fields, but no test asserted `telemetry.provider_metadata` truthiness. Only the integration test against live LiteLLM proxy caught it.

**Fix:** `provider_metadata=provider_metadata,` added to constructor call.

**Lesson:** Mock-shape tests that don't assert content for every field that should be populated leave gaps. Integration tests against real upstreams catch bugs that mock fidelity cannot. CONSTITUTION rule "always require at least 1 integration test running real handlers through full dispatcher loop with schema validation" is now empirically validated, not just a principle.

### LL-M4-PHASE-A-002 — Verbal acknowledgment is not persistence

**Severity:** moderate
**Captured:** 2026-04-28 mid-session by operator.

**Problem:** During session, deferred items were repeatedly noted with phrases like "I'll keep this in mind" or "registered as technical debt". Operator observed that this pattern fails ~40% of the time: conversation moves on, context window churns, item never gets recorded anywhere durable.

**Fix:** Any deferred item, future-task, or technical-debt note must be persisted immediately to the appropriate MCP table (`save_lesson` for now, `task_create` after M0.X). Verbal acknowledgment alone is forbidden.

**Lesson:** When discussion surfaces "we'll handle this later", the right tool call IS the acknowledgment. This is the seed for M0.X's typed knowledge store split.

### LL-M4-PHASE-A-003 — LiteLLM exposes alias not concrete model

**Severity:** moderate
**Captured:** 2026-04-28 during A.6.1 eval.

**Problem:** Eval JSON's `concrete_models_seen` field showed `["classifier_default"]` instead of `["claude-haiku-4-5-20251001"]`. LiteLLM proxy returns `response.model = "<alias>"` rather than the concrete provider model identifier. This means `routing_logs.provider_metadata` cannot distinguish primary from fallback when cascade fires.

**Workaround for M4 Phase D:** Extract concrete model from `provider_metadata` jsonb dump (where LiteLLM does include `_response_ms` and provider-specific fields).

**Lesson:** Provider-agnostic abstractions hide telemetry detail. Always query underlying metadata fields for true model identity.

### LL-M0X-001 — Spec drift caught at scratch test time (no production damage)

**Severity:** moderate
**Captured:** 2026-04-28 during M0.X Phase A migration smoke tests.

**Problem:** Three independent schema mismatches between the M0.X spec and actual production schema surfaced during scratch DB testing of migrations 0026-0029:

1. **`router_feedback.request_id`** — spec §5.4 declared `uuid REFERENCES routing_logs(request_id) ON DELETE SET NULL`. Reality: `routing_logs.request_id` is `text` (not uuid), and `routing_logs` is partitioned by `created_at` so no UNIQUE constraint on `request_id` is possible. The hard FK was impossible. Fixed in commit `fe923a9`: `request_id text` with no FK (soft reference).

2. **`decisions.scope` DEFAULT** — spec §5.2 declared `DEFAULT 'project' CHECK (scope IN ('architectural','process','product','operational'))`. The default value `'project'` is not in the CHECK enum. Any legacy-style INSERT without explicit scope violated CHECK. Fixed in commit `acac675`: `DEFAULT 'operational'`.

3. **`lessons.status='superseded'`** — spec §7 instructed migration 0029 to mark migrated source rows `status='superseded'`. Reality: `lessons.status` is enum `lesson_status` with allowed values `pending_review|active|archived|merged_into|rejected`. `'superseded'` is not a valid enum value. Fixed in commit `40d51cc`: `status='archived'` (closest semantic match) with cross-table pointer in `metadata.superseded_to_table`.

**Pattern:** spec was written referencing the *intended* schema, not the *actual* production schema. All 3 errors would have failed at production-apply time.

**Mitigation that saved us:** the discipline of "scratch DB first, smoke test, then production" caught all 3 before any production damage. Production was never in a broken state.

**Lesson:** Before writing any migration that references existing tables, run `\d <table>` on production to verify column types, constraints, partitioning, and enum values match what the spec assumes. Spec source-of-truth claims should be cross-checked, not trusted. The pre-check step in tasks.md (e.g., M0X.A.5 pre-check counted existing decisions rows) should also include schema verification.

**Tags:** spec-drift, scratch-testing, migration-discipline, m0x

### LL-M0X-002 — Polymorphic PL/pgSQL CASE bug latent for months

**Severity:** critical
**Captured:** 2026-04-28 during M0X.A.5 (migration 0028 smoke test).

**Problem:** `notify_missing_embedding()` from migration `0019_functions_triggers.sql` used `CASE TG_TABLE_NAME WHEN 'lessons' THEN NEW.title || NEW.content WHEN 'decisions' THEN NEW.title || NEW.context || NEW.decision ... END`. PL/pgSQL evaluates `NEW.<column>` references in *every* branch at runtime against the firing table's row type, even branches whose WHEN condition doesn't match. When the trigger fired for `decisions`, PL/pgSQL hit `NEW.content` (lessons branch) and threw `ERROR: record "new" has no field "content"`.

**Why it stayed latent ~6 months:** the trigger was attached to 9 tables but only `lessons` had data. Phase 2 tables (`decisions`, `patterns`, `gotchas`, `contacts`, `ideas`, `projects_indexed`, `conversations_indexed`, `tools_catalog`) were all empty. The bug fired the first time M0.X smoke-tested an INSERT into `decisions`. Same bug would have detonated on first insert into ANY of the 7 other Phase 2 tables.

**Fix:** rewrite using `IF/ELSIF` chain. PL/pgSQL only evaluates the matched branch's expressions in IF/ELSIF — no pre-validation. All 9 table branches preserved with identical semantics. Commit `cb56311` (migration 0028a).

**Lesson:** Polymorphic trigger functions that branch on `TG_TABLE_NAME` with `CASE WHEN ... THEN NEW.<column>` are time bombs against empty tables. Use `IF/ELSIF` for dispatch. Empty tables have not exercised the code path — assume zero coverage until first INSERT happens.

**Tags:** plpgsql, triggers, latent-bug, schema-completeness, m2

---

### LL-INFRA-001 — Migration runner stores `path.stem` while older rows store 4-digit prefix

**Category:** INFRA / **Severity:** 🟡 moderate / **Bucket:** business
**Captured:** 2026-04-30 during M7.B (applying migration 0033).

**Problem:** `infra/db/migrate.py` line 114 records `version = path.stem` (e.g. `'0024_tasks'`) into `schema_migrations`. Pre-existing rows in both `pretel_os` and `pretel_os_test` databases use 4-digit prefixes only (`'0024'` ... `'0031'`), applied by an earlier convention. The runner's existence check `prior = already.get(path.stem)` therefore returns `None` for every migration 0024-0031, prompting re-application. The first non-idempotent migration (`0024_tasks.sql`) fails with `ERROR: trigger "trg_set_updated_at_tasks" for relation "tasks" already exists` and the runner exits with rc=4 before reaching newer files.

**Evidence:** `DATABASE_URL=postgresql://pretel_os@localhost/pretel_os python3 infra/db/migrate.py` output:
```
skip   0023_seed_control_registry
apply  0024_tasks
       FAILED: ... ERROR:  trigger "trg_set_updated_at_tasks" ... already exists
```
`SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 5` returns `0031, 0030, 0029, 0028, 0028a` — all prefix-only.

**Workaround used in M7.B (commit `fbe3a66`):**
```bash
CHK=$(sha256sum migrations/0033_projects_table.sql | awk '{print $1}')
for DB in pretel_os pretel_os_test; do
  psql -v ON_ERROR_STOP=1 -X -1 -q -d "postgresql://pretel_os@localhost/$DB" \
       -f migrations/0033_projects_table.sql
  psql -v ON_ERROR_STOP=1 -X -q -d "postgresql://pretel_os@localhost/$DB" \
       -c "INSERT INTO schema_migrations(version, checksum) VALUES ('0033', '$CHK') ON CONFLICT (version) DO NOTHING;"
done
```

**Root cause:** the runner's version derivation diverged from the convention used to seed the early migrations, and the divergence was never reconciled. The runner has been worked around or the convention has been worked around — both happen now, depending on who applies the migration.

**Fix (deferred per ADR-026):** a one-shot reconciliation migration that backfills full stems into `schema_migrations` for rows 0024-0033, plus a runner change to derive prefix-only `version`. Captured as `M7.A.fu2` in `tasks.md`.

**Next time:** when shipping a migration, do not assume `infra/db/migrate.py` runs cleanly. Use the documented two-line workaround from ADR-026 until the reconciliation lands. Tagged for revisit at next infra-touching session.

**Tags:** migrations, runner, schema_migrations, technical-debt, m7
**Related tools:** `infra/db/migrate.py`
**ADR:** ADR-026

---

### LL-PROC-003 — When MCP session is lost mid-task, ship the durable on-disk form

**Category:** PROC / **Severity:** 🟢 minor / **Bucket:** business
**Captured:** 2026-04-29 during M7.A (registering sdd + vett skills).

**Problem:** Mid-task, `mcp__claude_ai_pretel-os__register_skill` returned `Streamable HTTP error: ... "Session not found"` for both calls. The temptation was to retry, debug the session lifecycle, or open the MCP server logs. But the canonical persistence form for `tools_catalog` rows is **a SQL row**, and the deferred skill registration could be expressed as an idempotent SQL upsert that the operator (or any future caller) can apply at any time.

**Evidence:** Two `register_skill` calls returned the JSON-RPC error simultaneously. Retrying would have produced the same error. The MCP session lifecycle is not the operator's problem at task-shipping time; the durable artifact is.

**Fix:** Wrote `migrations/0032_seed_skills_sdd_vett.sql` with `INSERT INTO tools_catalog (...) VALUES ... ON CONFLICT (name) DO UPDATE SET ...`. Committed alongside the skill files (commit `3a41d7f`). Application of the migration carried forward as `M7.A.fu1` in `tasks.md`.

**Why this is a lesson, not a workaround:** the MCP tool wraps a SQL mutation. When the wrapper fails, the SQL is not lost — it is the canonical form. Producing the SQL as a fallback artifact is **the same outcome** as a successful MCP call; it just happens via a different writer. The principle generalizes: when an MCP tool's purpose is "persist to a known table," the durable backup is "the SQL that persists to that table."

**Anti-pattern this avoids:** rabbit-holing into MCP session debugging when the on-disk form is the answer. Same family as LL-M4-PHASE-A-002 (verbal acknowledgment is not persistence) — both are about distinguishing the durable record from the transient channel.

**Next time:** if an MCP tool fails mid-task and the tool's purpose is data persistence, write the equivalent SQL (or filesystem write) to disk and ship that. Apply the MCP form later when the channel is healthy. The DB cannot tell the difference.

**Tags:** mcp, persistence, fallback, session, m7
**Related tools:** `register_skill`, `tools_catalog`
**Cross-refs:** LL-M4-PHASE-A-002

---

## 10. Pre-flight checklist (master)

Run this before starting any module build. Every check references a lesson that justifies it.

### Planning

- [ ] Spec complete and approved per SDD process (`PROJECT_FOUNDATION §4`)
- [ ] Data flow clear: every input has a source, every output has a consumer
- [ ] Budget set with monitoring plan (LL-COST-001)
- [ ] V1 scope defined — ugliest functional version
- [ ] Edge cases and failure modes documented in spec §7

### Architecture

- [ ] Schemas defined for any new data (spec §4)
- [ ] Integration points identified (`INTEGRATIONS.md`)
- [ ] Model selection documented with fallbacks (if AI) (spec §4)
- [ ] Cost tracking built into every script from day 1 (LL-COST-001)
- [ ] Router, Reflection, Dream Engine boundaries respected (LL-ARCH-001)

### Development

- [ ] Single-item end-to-end test planned BEFORE batch processing
- [ ] File I/O verified for all agents/scripts
- [ ] Deterministic tasks use scripts, not LLMs
- [ ] Structural validators run before quality checks
- [ ] Git commits atomic per task (`CONSTITUTION §6.34`)

### Security

- [ ] Scout bucket content abstracted (LL-AI-001)
- [ ] Secrets in `.env` with mode 0600, never in git (`CONSTITUTION §3`)
- [ ] Pre-commit hook active on any branch that touches `buckets/scout/`

---

## 11. Anti-patterns (live list)

Collected from active lessons. "Never do these." Each anti-pattern traces to a lesson.

### Content and quality
- Never accept stub or placeholder data in outputs — validate all fields have real content.
- Never accept generic descriptions ("Reveals something about X") — require specifics.

### Operations
- Never retry with identical parameters after failure — include failure diagnosis first.
- Never batch-run untested changes — test one item end-to-end first.

### Architecture
- Never put routing logic in a client (LL-ARCH-001).
- Never trigger a periodic job on turn count without measuring the actual distribution (LL-ARCH-002).
- Never dual-home the same asset in git and DB (LL-ARCH-003).
- Never let different phases use different naming for the same entity — normalize IDs.

### Cost
- Never start work without a budget alarm set.
- Never optimize without numbers — the delta has to be measured (LL-COST-001).
- Never assume orchestrator overhead is zero — track it separately.

### Documentation and process
- Never copy content between docs — reference with "See [DOC §section]."
- Never start an AI chat by re-explaining the project — load existing docs as context.
- Never run a review cycle past its diminishing-returns point (LL-PROC-002, LL-PROC-004).

### Security
- Never rely on a single filter layer for security-critical content (LL-AI-001).
- Never commit an `.env` file or a credentials JSON.
- Never store Scout-specific identifiers in any storage.

---

## 12. Escalation chains

Reusable recovery patterns. Each pattern is a sequence of attempts that has worked in the past when a single approach failed.

### Large AI output failure

```
1. Monolithic generation fails
   → split output by domain/section
2. Domain-split fails
   → identify the specific block failing, retry only that block
3. Per-block still fails
   → compact mode: schema + required fields only, no narrative
4. JSON parse failure on any step
   → auto-repair (strip backticks, close unterminated strings) before declaring failure
5. Auto-repair fails
   → escalate to operator with specific section + exact error
```

### Postgres unreachable (degraded mode)

```
1. Connection refused
   → retry with backoff 500ms × 2^attempt up to 3 attempts
2. Still refused
   → Router enters git-only mode, flags `degraded_mode=true`
3. Writes queue to pending-write files in /tmp/pretel-os-pending/
4. Every 60 seconds, attempt reconnect
5. On reconnect, Dream Engine flushes the pending queue, writes a gotcha entry
```

### Cloudflare Tunnel down

```
1. Connection refused from Claude.ai
   → operator receives Telegram alert from health check
2. Check cloudflared systemd status
   → restart if not active
3. Still failing
   → operator accesses via Tailscale directly (100.80.39.23:8787)
4. Claude.ai remains unreachable until tunnel is restored
   → operator uses Telegram bot as temporary primary interface
```

### Anthropic rate limit reached

```
1. 429 received
   → respect retry-after header, backoff
2. Sustained 429
   → Router falls back to rule-based classifier, flags `classification_mode=fallback_rules`
3. Still over limit after 15 minutes
   → Morning Intelligence skipped, operator alerted
4. On recovery
   → Router returns to Haiku classification, flushes any batched reflection work
```

---

## 13. How to write a good lesson

### 13.1 Structure

Start with the Problem in one sentence. Don't bury the lead in context. The Fix should be testable; "be more careful" is not a fix.

### 13.2 Specificity

Name the exact tool, file, function, model, or configuration. "Cowork Dispatch" — not "the dispatch thing." `text-embedding-3-large` — not "the OpenAI embeddings." Line number or commit hash when available.

### 13.3 Preventive rule

One sentence, actionable by a future reader (or a future you) who has forgotten the context. "Use Termius SSH with tmux for long-running LLM commands; Dispatch is for quick status checks only." That sentence is the lesson; everything else is evidence.

### 13.4 Enforcement

Answer the question: "What prevents this from happening again?" Acceptable answers are:
- A script that validates before the failure condition recurs
- A CI check that blocks the merge
- A pre-commit hook
- A DB trigger
- A test that would fail if the rule were violated

Unacceptable answers:
- "Manual discipline"
- "Be more careful next time"
- "Remember to check"

If the only enforcement is memory, the lesson is incomplete. Add a real enforcement mechanism or acknowledge the gap explicitly in the lesson.

### 13.5 Verified

A lesson is `verified: true` when enforcement has been demonstrated — a commit attempted that triggered the guard, a test that caught the regression, a CI run that blocked the bad merge. Until then, `verified: false`. The Dream Engine reports lessons unverified for more than 30 days.

---

## 14. References

- `CONSTITUTION.md §5` — full memory and retrieval rules
- `DATA_MODEL.md §2.1` — `lessons` table schema
- `DATA_MODEL.md §6.3` — `find_duplicate_lesson()` function
- `DATA_MODEL.md §6.5` — `archive_low_utility_lessons()` function
- `DATA_MODEL.md §6.7` — Scout safety trigger
- `PROJECT_FOUNDATION.md §4 Module 8` — `lessons_migration` module
- `INTEGRATIONS.md §3` — OpenAI embeddings (used for lesson embeddings)
- Prior OpenClaw format: `github.com/pr3t3l/openclaw-config/tree/main/lessons-learned`
