# DECISIONS — pretel-os

**Status:** Active ADR log
**Last updated:** 2026-04-28
**Owner:** Alfredo Pretel Vargas

This file is the canonical record of architectural and process decisions for pretel-os. Every entry is an ADR (Architectural Decision Record) with explicit context, decision, consequences, and alternatives. Decisions here are immutable; if a decision needs to change, a new ADR supersedes it (status flips to `superseded`, `superseded_by` points to the new ADR).

When `decisions` table comes online (M0.X Phase A migration 0029), the rows here seed that table. Until then, this file is authoritative.

## Conventions

Each ADR has the format:

```
## ADR-NNN — Short title

**Status:** active | superseded
**Scope:** architectural | process | product | operational
**Severity:** critical | normal | minor
**Decided:** YYYY-MM-DD
**Decided by:** operator | claude+operator
**Applicable buckets:** [list or "all"]
**Tags:** [list]
**Superseded by:** ADR-NNN (only if status=superseded)
**Derived from lessons:** [list of lesson IDs] (optional)

### Context
What problem prompted this decision.

### Decision
What was decided.

### Consequences
What this enables, what this costs, what's now load-bearing.

### Alternatives considered
What else was on the table and why it was rejected.
```

ADRs 001-019 are recorded in `docs/PROJECT_FOUNDATION.md §5` (legacy location, not migrated). ADR-020 onward live here.

---

## ADR-020 — Router classifier and second_opinion route through LiteLLM proxy aliases

**Status:** active
**Scope:** architectural
**Severity:** critical
**Decided:** 2026-04-27
**Decided by:** operator
**Applicable buckets:** all
**Tags:** [router, litellm, model-routing, vendor-neutrality]

### Context
The Router needs LLM access for classification (every turn) and second-opinion fallback (rare). Hardcoding `model="claude-..."` or `model="gpt-..."` strings in Router code couples pretel-os to a specific vendor and forces code changes whenever the operator wants to swap models for cost or quality reasons.

### Decision
All Router LLM calls route through LiteLLM proxy aliases: `classifier_default` and `second_opinion_default`. Underlying model selection is config-only via `~/.litellm/config.yaml`. Router code never references concrete model identifiers.

### Consequences
- Model swaps become a YAML edit, not a code change
- Cascade fallback (primary→fallback1→fallback2) handled at proxy level, transparent to Router
- Routing logs show alias not concrete model — concrete model identity must be extracted from `provider_metadata` jsonb (see ADR-024 follow-up — LL-M4-PHASE-A-003)
- Constitutional rule: Router code MUST NOT contain string literals matching `claude-`, `gpt-`, `gemini-`, etc.

### Alternatives considered
- Direct vendor SDKs (Anthropic / OpenAI) → rejected: vendor lock-in
- LangChain ChatModel abstraction → rejected: heavyweight, opinionated, adds dependency surface
- Custom router class in code → rejected: duplicates what LiteLLM already does

---

## ADR-021 — Split lessons into typed knowledge stores (Module 0.X)

**Status:** active
**Scope:** architectural
**Severity:** critical
**Decided:** 2026-04-28
**Decided by:** operator+claude
**Applicable buckets:** all
**Tags:** [knowledge-architecture, lessons, schema, module-0x]

### Context
The single `lessons` table accumulated semantically distinct content types: post-hoc patterns (the original purpose), pending tasks, architectural decisions, best-practice guidance, and operator preferences. Each type has different mutability rules (tasks close, decisions get superseded, best practices update in place, preferences toggle), different load triggers (preferences load every session, lessons only when classifier says so), and different write provenance. Forcing all into one schema produced schema-violations-by-tag and confused retrieval semantics.

### Decision
Split into typed stores: `tasks`, `operator_preferences`, `router_feedback`, `best_practices` (new tables) plus amendment of existing `decisions` table (M0.X spec §5.2). `lessons` retains its original scope: post-hoc reflection patterns only.

### Consequences
- Each table has correct lifecycle, CHECK constraints, and load contract
- Module 4 Phase B layer loader can map L0–L4 to specific tables (M0.X spec §8)
- 4 misclassified `lessons` rows migrated in `0029_data_migration_lessons_split.sql`
- 16 new MCP tools required (M0.X spec §6)

### Alternatives considered
- Add columns to `lessons` to discriminate types → rejected (Appendix A of spec): different semantics, lowest-common-denominator design
- Single typed-document collection with discriminator field → equivalent to above, same rejection

### Derived from lessons
- LL-M4-PHASE-A-002 (verbal acknowledgment is not persistence)

---

## ADR-022 — SOUL.md as L0 voice file

**Status:** active
**Scope:** architectural
**Severity:** normal
**Decided:** 2026-04-28
**Decided by:** operator+claude
**Applicable buckets:** all
**Tags:** [l0, identity, soul, voice]

### Context
Operator's communication style and behavioral preferences (direct, actionable, Spanish/English mix, no flattery, deferral discipline) need to load into every session via L0. CONSTITUTION.md is for system rules; IDENTITY.md is for operator facts; AGENTS.md is for LLM read order. None is the right home for "voice."

### Decision
Add `SOUL.md` at repo root, loaded into L0 alongside CONSTITUTION/IDENTITY/AGENTS. Note: Claude.ai web/app does NOT load SOUL.md (Anthropic uses operator's userPreferences). SOUL.md applies to Claude Code, Telegram bot via OpenClaw, and any MCP session caller that loads it.

### Consequences
- Per CONSTITUTION §2.3, the 1,200-token L0 budget applies to `identity.md` specifically. SOUL.md follows the pattern of `AGENTS.md` and `CONSTITUTION.md`: loaded in L0 without per-file numerical cap, kept lean by convention (target ~150-200 tokens). Pre-commit hook (§7.36) enforces only the `identity.md` cap.
- Operator voice persists across sessions and clients (except Anthropic web/app)
- Future scope: sync between SOUL.md and Anthropic userPreferences (deferred)

### Alternatives considered
- Inline voice in IDENTITY.md → rejected: pollutes operator-facts file with style guidance
- Persist in `operator_preferences` table → rejected: voice is too rich for key/value rows
- userPreferences only → rejected: doesn't apply to Claude Code or Telegram

---

## ADR-023 — best_practices is a new table, not an extension of patterns

**Status:** active
**Scope:** architectural
**Severity:** normal
**Decided:** 2026-04-28
**Decided by:** operator+claude
**Applicable buckets:** all
**Tags:** [knowledge-architecture, best-practices, patterns, module-0x]

### Context
M0.X needs to capture reusable PROCESS guidance ("always X when Y", narrative). Existing `patterns` table (DATA_MODEL §5.1) holds CODE snippets with required `code TEXT NOT NULL` and `language` columns. Question (OQ-6 in spec): extend `patterns` with `kind` column or create new `best_practices` table.

### Decision
Create new `best_practices` table (M0.X spec §5.5) with prose `guidance` field, `rationale`, `domain`, `scope`, `derived_from_lessons` for reflection-worker provenance, and single-step rollback fields (`previous_guidance`, `previous_rationale`). Patterns table retained unchanged for code.

### Consequences
- Two tables for two distinct concepts (code vs prose); clean retrieval
- L4 layer load includes both `lessons` and `best_practices`; L2 includes both `decisions` and `best_practices` filtered by scope
- 3 new MCP tools: `best_practice_record`, `best_practice_search`, `best_practice_deactivate`

### Alternatives considered
- Extend `patterns` with `kind text CHECK (kind IN ('code','process','convention'))` → rejected: `code TEXT NOT NULL` incompatible with prose; L2/L4 want different result shapes; LL-DATA-001 ("single table beats parallel") applies to lifecycle states of one type, not ontologically distinct types
- Add to `lessons` with tag → rejected: same anti-pattern that motivated M0.X

---

## ADR-024 — HNSW indexes deferred until pgvector ≥ 0.7 or volume justifies

**Status:** active
**Scope:** architectural
**Severity:** critical
**Decided:** 2026-04-24
**Captured retroactively:** 2026-04-28 (lost during 4-day verbal-acknowledgment gap; recovered by operator)
**Decided by:** operator+claude
**Applicable buckets:** all
**Tags:** [pgvector, hnsw, embeddings, retrieval, scaling]

### Context
pgvector 0.6.0 (the version available in Ubuntu 24.04 noble repos) limits HNSW indexes to vectors of ≤2,000 dimensions. pretel-os uses `text-embedding-3-large` at 3,072 dimensions across all embedding columns (`lessons`, `tools_catalog`, `projects_indexed`, `conversations_indexed`, `patterns`, `decisions`, `gotchas`, `contacts`, `ideas`, and the M0.X-new `best_practices`). Therefore HNSW indexes cannot be created with the current pgvector version on the chosen embedding model.

### Decision
Omit all `CREATE INDEX ... USING hnsw` statements from migrations until either:
1. pgvector is upgraded to ≥0.7.0 (which raises the HNSW dimension cap), OR
2. Vector volume crosses the threshold where sequential scan latency exceeds 100ms (empirically ~50K rows for vector(3072) at current hardware)

Until then, queries use sequential scan with `ORDER BY embedding <=> query LIMIT k`. At <5K vectors (Phase 1-3 projection), this completes in 10-50ms — imperceptible.

### Consequences
- All migrations (including M0.X 0024-0029) must NOT include HNSW CREATE INDEX statements
- Spec.md §5.5 best_practices must be amended: HNSW line replaced with deferred comment
- Tasks.md M0X.A.4.5 must be amended: from "Add HNSW index" to "Skip HNSW index per ADR-024"
- A future migration will re-add HNSW indexes once condition 1 or 2 is met
- text-embedding-3-large at 3,072 dims is preserved (CONSTITUTION §2.5 + DATA_MODEL §11.5 invariant); reducing to 2,000 dims to enable HNSW on pgvector 0.6.0 was rejected (alternative below)

### Alternatives considered
- **Reduce embeddings to vector(2000) using OpenAI dimensions=2000 parameter** → rejected: requires constitutional amendment to §2.5 (text-embedding-3-large at 3,072 dims is declared immutable). Quality loss in MTEB benchmarks is ~1-2%, indistinguishable at our corpus scale, but the constitutional change introduces risk and is not justified by current need
- **Use IVFFlat instead of HNSW** → rejected: IVFFlat requires populated tables to build lists; with empty tables the index is degenerate. Also lower recall quality than HNSW
- **Build pgvector ≥0.7 from source** → considered, deferred: tracking gap (no apt updates for source-installed packages); revisit if HNSW becomes urgent before Ubuntu provides a newer build
- **Add PostgreSQL Apt PPA for pgvector 0.7+** → considered, deferred: introduces apt-source drift across Postgres ecosystem packages; revisit if templated approach (template1 pre-load) proves insufficient

### Derived from lessons
None directly. This ADR exists because the original decision (2026-04-24) was made conversationally and never persisted — a textbook instance of LL-M4-PHASE-A-002 (verbal acknowledgment is not persistence). The 4-day gap between decision and capture exposed the failure mode that Module 0.X is designed to prevent.

---

## ADR-025 — Layer Loader Contract frozen at `module-0x-complete`

- **Status:** active
- **Scope:** architectural
- **Bucket:** business
- **Project:** pretel-os
- **Date:** 2026-04-29
- **Severity:** critical
- **Decided by:** operator

### Context
Module 0.X delivered the schemas (`tasks`, `operator_preferences`, `router_feedback`, `best_practices`) and the amended `decisions` table that Module 4 Phase B (Layer Loader) will consume to assemble L0–L4 context bundles per CONSTITUTION §2.3. Phase B can only start once the input surface is stable: Phase B planners need a deterministic mapping from `(bucket, project, classifier_signals)` to "which tables, which filters, which orderings, which output shape, which token-counting method." Without that, Phase B keeps coming back to ask, and the whole point of separating M0.X from M4 collapses.

### Decision
Treat `specs/module-0x-knowledge-architecture/layer_loader_contract.md` as a frozen architectural commitment as of the `module-0x-complete` tag (commit `49edc0c`, 2026-04-29). The contract specifies, in §1–§11:

- §1–§2 — purpose and runtime inputs
- §3 — layer-by-layer source tables, SQL filters, and orderings (L0–L4)
- §4 — tables explicitly NOT loaded into context
- §5 — performance contract (sequential scan per ADR-024 until 50K rows or pgvector ≥ 0.7)
- §6 — cache invalidation triggers (LISTEN/NOTIFY on `operator_preferences`, `decisions`, `best_practices`, `lessons`)
- §7 — token budgets per layer (hard 1.2K identity.md per CONSTITUTION §2.3; soft 3K/5K/4K elsewhere)
- §8 — observability requirements
- §9 — frozen-interface clause: any new layer, removed table, filter shape change, or token-budget change requires a new ADR superseding this one
- §10 — output bundle shape (`LayerBundle` typed dataclass with `LayerContent` / `ContextBlock` / `BundleMetadata`); L0 intra-layer ordering pinned (CONSTITUTION → IDENTITY → AGENTS → SOUL → preferences); conflict resolution deferred to consumer per CONSTITUTION §2.7
- §11 — token counting method (`tiktoken.get_encoding("cl100k_base")`, aligned with `infra/hooks/token_budget.py`)

The contract is the input spec for M4 Phase B. Phase B writes its own spec/plan/tasks against this contract (no further round-trip with M0.X authors).

### Consequences
- M4 Phase B is unblocked. Phase B planners read the contract, produce SDD trinity, ship.
- Adding a new layer (L5), removing a table from a layer, changing a filter's shape, or changing a token budget requires a new ADR superseding this one. Adding new content sources within an existing layer (e.g., a new prefs scope variant) does not — Phase B can adapt at runtime per §9.
- The token-budget arithmetic in §7 is anchored to `cl100k_base`. Future divergence between the contract and `infra/hooks/token_budget.py` requires an ADR, not a unilateral hook change.
- Severity ordering for `decisions` is mandated DB-side via SQL `CASE` (`critical=0, normal=1, minor=2, ELSE 99`) per §3.2 — pull-then-sort-in-Python is non-conformant for testability and determinism.
- The frozen output bundle shape (§10) means the consumer (Router/dispatcher) is the sole authority for prompt assembly; Phase B never pre-renders a single markdown blob.

### Alternatives considered
- **No formal contract — let Phase B planners derive intent from spec.md §8** → rejected: spec.md §8 is a sketch, not a contract, and authoring a new module against a sketch produces ambiguity (operator review of the contract draft caught three concrete gaps: missing output shape, missing tokenizer choice, ambiguous severity ordering). The contract makes those decisions explicit.
- **Contract embedded inside spec.md §8 instead of a standalone file** → rejected: the contract is the durable interface that survives spec.md edits. A standalone file makes "supersede" unambiguous and lets Phase B reference a fixed artifact (`layer_loader_contract.md@module-0x-complete`) without grepping a long spec.
- **Defer the freeze; let Phase B and M0.X co-evolve** → rejected: the whole reason M0.X was carved out was to give M4 a stable input surface. Co-evolution is the failure mode this avoids.

### Derived from lessons
- `LL-M0X-001` — Spec drift caught at scratch test time. Phase E's drift fixes (tool count 16 → 18, `decisions.project` NOT NULL clarification) are the same family. The contract is intentionally fully-specified to avoid being the source of similar drift downstream.
- `LL-M4-PHASE-A-002` — Verbal acknowledgment is not persistence. The contract is a written, version-pinned artifact (`module-0x-complete` tag), not a verbal handoff.
