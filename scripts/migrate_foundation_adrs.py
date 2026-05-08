"""Migrate the foundation-era ADRs into the `decisions` table.

Scope (21 ADRs total):

  • 19 ADRs from `docs/PROJECT_FOUNDATION.md §5` (ADR-001 through ADR-019).
    ADR-020 and ADR-021 were already inserted by Module 0.X / M4 work and
    are skipped here.

  • 2 ADRs from `DECISIONS.md` that conflict with ADR-026 / ADR-027 already
    in the DB (different topics, same numbers). The conflict was resolved
    on 2026-05-07 by renumbering the file ADRs:
        DECISIONS.md ADR-026 (migrate.py reconciliation deferred) → ADR-030
        DECISIONS.md ADR-027 (projects vs projects_indexed)        → ADR-031

Why a script and not raw SQL: writes go through `decision_record` per
CONSTITUTION §2.1, which embeds title+context+decision via OpenAI on
write and queues to pending_embeddings on failure.

Idempotent: re-running detects existing adr_numbers and skips.

Usage:
    PYTHONPATH=src python scripts/migrate_foundation_adrs.py [--dry-run] [--test-db]
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Any

# ---------------------------------------------------------------- ADR data
#
# Each row is the canonical operator-curated content. Free-form prose was
# normalised into the four ADR fields the table expects. Dates in the
# source documents are preserved in `decided_by` ("operator+claude /
# 2026-04-18") to keep provenance.

ALL_BUCKETS = ["personal", "business", "scout"]


def _adr(
    n: int,
    title: str,
    context: str,
    decision: str,
    consequences: str,
    *,
    alternatives: str | None = None,
    severity: str = "critical",
    applicable_buckets: list[str] | None = None,
    tags: list[str] | None = None,
    decided_by: str = "operator+claude",
    scope: str = "architectural",
) -> dict[str, Any]:
    return {
        "adr_number": n,
        "title": title,
        "context": context,
        "decision": decision,
        "consequences": consequences,
        "alternatives": alternatives,
        "severity": severity,
        "applicable_buckets": applicable_buckets if applicable_buckets is not None else ALL_BUCKETS,
        "tags": tags or [],
        "decided_by": decided_by,
        "scope": scope,
    }


ADRS: list[dict[str, Any]] = [
    _adr(
        1, "Separate repository from OpenClaw",
        context=(
            "OpenClaw accumulated configuration debt and architectural decisions that were "
            "never documented. Debugging routinely exceeds the cost of rebuild."
        ),
        decision=(
            "pretel-os is a new repository (`pr3t3l/pretel-os`) built from scratch using the "
            "SDD process. OpenClaw is deprecated and will be retired once pretel-os reaches "
            "feature parity for daily workflows."
        ),
        consequences=(
            "Short-term effort cost (rebuild). Long-term gain: known architecture, explicit "
            "decisions, tested modules. Three existing assets (SDD System repo, VETT, Forge "
            "n8n workflow) are preserved unchanged and reused."
        ),
        tags=["repository", "openclaw", "sdd", "foundation"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        2, "MCP server as the single gateway",
        context=(
            "Clients (Claude.ai, Claude Code, Claude mobile, future agents) need a portable "
            "contract. Direct database access from a client would lock pretel-os to specific "
            "clients and leak schema details."
        ),
        decision=(
            "Every client reaches pretel-os exclusively through the MCP server over Streamable "
            "HTTP. The MCP server exposes tools, resources, and prompts. Postgres, n8n, the "
            "Telegram bot, and the git repo are never addressed directly by clients."
        ),
        consequences=(
            "Portability is guaranteed by construction. Schema changes only require MCP tool "
            "signature stability. One deployment surface to secure and monitor."
        ),
        tags=["mcp", "gateway", "architecture", "portability"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        3, "The Router lives in the MCP server, not in any client and not in OpenClaw",
        context=(
            "Context assembly (which layers to load, when to run RAG, how to respect token "
            "budgets) is a first-class responsibility that previously lived ambiguously across "
            "OpenClaw, skills, and ad-hoc prompts. That ambiguity was the root cause of token "
            "waste and inconsistent behavior."
        ),
        decision=(
            "The Router is a named component inside the MCP server per CONSTITUTION §2.2. "
            "Clients call one tool, `get_context(message)`, and receive pre-assembled context. "
            "No client-side routing, no client-side RAG, no client-side classification."
        ),
        consequences=(
            "Switching clients does not change behavior. Router logic is testable in isolation. "
            "Cost control is enforceable at one point. Rule 36 of the CONSTITUTION depends on "
            "this decision."
        ),
        tags=["router", "context", "mcp", "architecture"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        4, "Stack D chosen over OpenClaw reconfiguration and over fully custom stack",
        context=(
            "Three options evaluated:\n"
            "- A: fully custom (build everything)\n"
            "- B: OpenClaw reconfigured carefully\n"
            "- C: hybrid (custom router + OpenClaw UI)\n"
            "- D: mature-components stack (`python-telegram-bot` + n8n + FastMCP + systemd)"
        ),
        decision=(
            "Option D. Each component is independently battle-tested. No wrapper hides "
            "architectural decisions. Replaceability is preserved (any component can swap "
            "without touching the others)."
        ),
        consequences=(
            "Loses OpenClaw's community and update cadence. Gains stability, testability, "
            "explicit ownership of every choice. Requires operator to manage Telegram bot "
            "updates and n8n upgrades directly (acceptable — all of these have mature "
            "ecosystems)."
        ),
        alternatives=(
            "A (fully custom — too much rebuild), B (OpenClaw reconfigured — keeps the debt), "
            "C (hybrid — leaks OpenClaw choices into Router)."
        ),
        tags=["stack", "architecture", "components", "foundation"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        5, "Ubuntu 24.04 Desktop replaces Windows 11 on the Vivobook",
        context=(
            "Windows 11 on the Vivobook consumes more than 70% of RAM at idle, leaving "
            "insufficient headroom for Postgres + n8n + MCP server + bot concurrently. Dual "
            "boot adds GRUB complexity and risks leaving the machine at a boot menu after a "
            "power event. Windows Server is overpriced for this use."
        ),
        decision=(
            "Clean install Ubuntu 24.04 LTS Desktop on the Vivobook S15 OLED, single boot. GUI "
            "available on demand; services run as systemd units regardless of login state."
        ),
        consequences=(
            "All RAM (16–32 GB) available for workloads. Native Linux tooling (apt, Docker, "
            "systemd, Python). Operator loses Windows on the Vivobook — acceptable because the "
            "Asus Rock remains the personal laptop and carries Windows if needed."
        ),
        severity="normal",
        tags=["infra", "os", "ubuntu", "vivobook"],
        decided_by="operator / 2026-04-18",
    ),
    _adr(
        6, "OpenAI text-embedding-3-large as the embeddings model",
        context=(
            "Three candidates considered: OpenAI `text-embedding-3-small` (cheap, 1536 dim), "
            "OpenAI `text-embedding-3-large` (3072 dim, industry standard), Voyage-3-large "
            "(best benchmark but less portable). Local sentence-transformers rejected due to "
            "dependency on machine availability."
        ),
        decision=(
            "`text-embedding-3-large`, 3072 dimensions. Cost at expected volume is negligible "
            "(~$1/month). Supported by every major tutorial, framework, and vector DB "
            "provider. Portable by construction."
        ),
        consequences=(
            "Switching to Voyage or local requires full reindex (cheap at current scale, more "
            "expensive later — acceptable trade). Pinned in CONSTITUTION §2.5 to prevent "
            "silent drift."
        ),
        alternatives=(
            "`text-embedding-3-small` (cheaper but lower quality), Voyage-3-large (best "
            "benchmark, less ecosystem support), local sentence-transformers (rejected — needs "
            "machine availability)."
        ),
        tags=["embeddings", "openai", "vector", "foundation"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        7, "Postgres + pgvector locally, migrate to Supabase when schema stable",
        context=(
            "Vector database options evaluated: pgvector local, Supabase (Postgres + pgvector "
            "managed), Pinecone, Turbopuffer, Qdrant Cloud, Neon. Scale estimates show "
            "Postgres + pgvector comfortable at 10M+ vectors; projected dataset is under 100k "
            "vectors in 5 years."
        ),
        decision=(
            "Phase 2 builds on pgvector locally on the Vivobook. Phase 4–5 migrates to Supabase "
            "managed Postgres when the schema has stabilized. Pinecone and others are held in "
            "reserve but not adopted."
        ),
        consequences=(
            "Schema iteration cost is zero during build (local dev). Migration to Supabase is "
            "a one-hour `pg_dump`/`psql` operation when triggered. Forge's existing Postgres "
            "remains separate and untouched until its own revenue-gated migration."
        ),
        alternatives="Pinecone, Turbopuffer, Qdrant Cloud, Neon (held in reserve, not adopted).",
        tags=["postgres", "pgvector", "supabase", "data"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        8, "Five context layers L0–L4, fixed",
        context=(
            "An arbitrary layer count is a source of drift: adding layers whenever a new need "
            "appears leads to bloat. A fixed, small set forces design discipline."
        ),
        decision=(
            "Exactly five context layers — L0 Identity, L1 Bucket, L2 Project, L3 Skill, L4 "
            "Retrieved lessons — as defined in CONSTITUTION §2.3. Adding a sixth requires "
            "constitutional amendment."
        ),
        consequences=(
            "Every new feature must fit into one of the five. Multi-module projects split "
            "within L2 (project README + module file), they do not create a new layer. "
            "Tool-catalog detail lives in L3, not L0."
        ),
        tags=["context-layers", "router", "architecture", "constitutional"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        9, "Four background workers, fixed",
        context=(
            "Cron jobs proliferate. Without a named charter, every new automation becomes a "
            "cron entry nobody remembers maintaining."
        ),
        decision=(
            "Exactly four background workers — Reflection, Dream Engine, Morning Intelligence, "
            "Auto-index — as defined in CONSTITUTION §2.6. Each has a named charter and a "
            "single home. Adding a fifth requires constitutional amendment. (Amended 2026-05 "
            "by ADR-029 to drop Reflection; current count is 4 with the addition of the "
            "README consumer in M7.5.)"
        ),
        consequences=(
            "Operational surface is bounded and documentable. Failure modes are enumerable. "
            "Every scheduled behavior traces to one of four owners."
        ),
        tags=["workers", "constitutional", "operations"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        10, "Reflection triggered by event, never by turn count",
        context=(
            "Earlier proposal used 'every N messages' (N=100 suggested). Analysis showed most "
            "sessions never reach 100 messages, so reflection would rarely fire. Event-driven "
            "triggers (task completion, session close, or fallback) fire reliably."
        ),
        decision=(
            "Reflection fires on `task_complete` tool call, on `close_session` (10 minutes "
            "idle or explicit close), or on a fallback every 20 turns — whichever arrives "
            "first. Never on arbitrary message-count windows. (Status: Reflection worker was "
            "later cancelled — see ADR-029 / decision row 9e8bacad.)"
        ),
        consequences=(
            "Lessons capture happens when loops actually close. The fallback catches long "
            "exploratory sessions that never formally close. Rule 12 of CONSTITUTION §5.1 "
            "depends on this."
        ),
        severity="normal",
        tags=["reflection", "triggers", "workers"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        11, "Dedicated tools_catalog table, not mixed into lessons",
        context=(
            "Alternatives were: (a) dedicated table with embeddings and utility score, "
            "(b) mix into `lessons` with a `tool_metadata` tag, (c) YAML in git with no "
            "embeddings. Option (b) mixes semantically different entities and complicates "
            "queries. Option (c) has no ranking or retrieval."
        ),
        decision=(
            "Dedicated `tools_catalog` table in Postgres with its own columns (usage_count, "
            "utility_score, applicable_buckets, skill_file_path) and its own embedding column."
        ),
        consequences=(
            "Tool recommendations run against a small, purpose-shaped table. Utility score "
            "formula (CONSTITUTION §5.2) has a clean home. No semantic pollution in lessons."
        ),
        alternatives=(
            "(b) tag inside `lessons` — rejected: mixes ontologies. (c) YAML in git — "
            "rejected: no ranking or retrieval."
        ),
        tags=["tools-catalog", "schema", "data"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        12, "Subdomain of alfredopretelvargas.com via Cloudflare Tunnel (Option A)",
        context=(
            "Operator already owns `alfredopretelvargas.com` on IONOS hosting. Two options: "
            "(A) keep DNS at IONOS, delegate a subdomain to Cloudflare for tunnel use, or "
            "(B) move entire DNS zone to Cloudflare."
        ),
        decision=(
            "Option A. `mcp.alfredopretelvargas.com` (and future subdomains) are routed "
            "through Cloudflare Tunnel via CNAME from IONOS. Main website and webmail "
            "continue at IONOS unchanged."
        ),
        consequences=(
            "Zero disruption to existing website or `support@declassified.shop` email. "
            "Cloudflare-managed subdomains have TLS, DDoS protection, and tunnel routing for "
            "free. Adding new public subdomains requires one CNAME record each in IONOS."
        ),
        alternatives="Move full DNS zone to Cloudflare — rejected: too disruptive to website/email.",
        severity="normal",
        tags=["dns", "cloudflare", "ionos", "infra"],
        decided_by="operator / 2026-04-18",
    ),
    _adr(
        13, "Asus Rock as personal laptop, Vivobook S15 OLED as always-on server",
        context=(
            "Operator has two Asus laptops. Only one can be the always-on server (thermal, "
            "location, reliability profile differ). The Vivobook S15 OLED has higher specs "
            "(Intel Ultra 9, up to 32 GB RAM, NVMe Gen4). The Asus Rock is older and portable."
        ),
        decision=(
            "The Vivobook S15 OLED is reinstalled with Ubuntu 24.04 Desktop and becomes the "
            "pretel-os server, always on, at home. The Asus Rock remains on Windows and "
            "serves as the operator's daily portable laptop for travel and in-office work."
        ),
        consequences=(
            "Clean role separation. The Asus Rock can reach the server via Tailscale from "
            "anywhere. Failover plan: if the Vivobook fails, the Asus Rock can temporarily "
            "host the stack (reduced uptime but functional)."
        ),
        severity="normal",
        tags=["hardware", "infra", "vivobook", "asus-rock"],
        decided_by="operator / 2026-04-18",
    ),
    _adr(
        14, "Cloud migration is revenue-gated with 3x margin",
        context=(
            "Running fully in the cloud costs $50–100/month at minimum. Running locally costs "
            "near-zero in cash but requires the Vivobook to remain healthy."
        ),
        decision=(
            "Cloud migration happens per product: the associated product's revenue (Forge, "
            "Declassified, freelance) must cover 3x the new monthly spend before migration. "
            "Until then, local wins."
        ),
        consequences=(
            "The system's cash floor stays low during build. Cloud migration, when it "
            "happens, is economically safe. CONSTITUTION §4.11 encodes this rule."
        ),
        tags=["cost", "cloud", "revenue-gated", "constitutional"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        15, "Preserve SDD System, VETT, and Forge from prior stack",
        context=(
            "Not every asset from the OpenClaw era is waste. Three things work well and "
            "would cost more to rebuild than to port."
        ),
        decision=(
            "`github.com/pr3t3l/sdd-system` remains the canonical SDD template source. VETT "
            "migrates to `skills/vett.md` unchanged. Forge's 8-phase n8n pipeline migrates "
            "with Postgres dump to the Vivobook and remains on its current design."
        ),
        consequences=(
            "Faster ramp. The three preserved assets become early `tools_catalog` entries "
            "and early content for `skills/`."
        ),
        severity="normal",
        tags=["sdd", "vett", "forge", "migration", "skills"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        16, "Complexity classification drives retrieval (LOW/MEDIUM/HIGH)",
        context=(
            "Rule 16 of an earlier draft referenced 'complex problems' without an operational "
            "definition. Agents were left to decide when to consult lessons, which is exactly "
            "what the Router is supposed to own."
        ),
        decision=(
            "Router classifies every turn as LOW, MEDIUM, or HIGH per CONSTITUTION §5.1. "
            "HIGH always loads L4 and queries tool-catalog. MEDIUM conditionally loads "
            "(filter-first existence check). LOW never loads L4. The definition is "
            "operational (not subjective): factual queries and casual conversation are LOW; "
            "structured known-workflow tasks are MEDIUM; debugging, architecture, and "
            "recommendation requests are HIGH."
        ),
        consequences=(
            "Predictable cost per turn by category. No agent-side guessing. Operator can "
            "review `routing_logs` to see classification history and tune rules if needed."
        ),
        tags=["router", "complexity", "classification", "retrieval"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        17, "Degraded mode for MCP dependency failures",
        context=(
            "The MCP server is the single gateway (ADR-002). A naive implementation would "
            "make every dependency outage a full system outage. Postgres unreachable → no "
            "context. OpenAI down → no embeddings. Classifier LLM down → no classification. "
            "Unacceptable."
        ),
        decision=(
            "Degraded mode is a first-class operating state per CONSTITUTION §8.43. Git-only "
            "mode serves L0–L3 without the DB. Embedding writes queue to `pending_embeddings` "
            "when OpenAI is down. Classifier LLM (via LiteLLM `classifier_default`) falls "
            "back to keyword/regex rules. Morning Intelligence skips with logged incident. "
            "Every degraded response carries an explicit flag so the agent surfaces reduced "
            "functionality instead of pretending everything works."
        ),
        consequences=(
            "System stays usable during partial outages. Failure modes are enumerable and "
            "testable. Cost of implementation is one additional code path per external "
            "dependency — acceptable."
        ),
        tags=["degraded-mode", "resilience", "constitutional"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        18, "Project snapshots separate from skill versions",
        context=(
            "`skill_versions` preserves the evolution of methodology files. But projects also "
            "evolve (Declassified changes its stack, Healthy Families adds modules), and "
            "'how did we do it before this change' is a common recall need."
        ),
        decision=(
            "Add `project_versions` table (separate from `skill_versions`). Snapshots are "
            "written automatically by structural tools (`add_module`, `change_stack`, etc.) "
            "and can be invoked manually via `snapshot_project(project, reason)`. Each "
            "snapshot stores the full L2 content at that point in time with reason and "
            "timestamp."
        ),
        consequences=(
            "'How did we do this 6 months ago' returns actual historical state, not inferred "
            "from git log. Storage cost is trivial (project files are small, snapshots rare). "
            "Rule 25 of CONSTITUTION §5.5 depends on this decision."
        ),
        severity="normal",
        tags=["project-versions", "snapshots", "schema"],
        decided_by="operator+claude / 2026-04-18",
    ),
    _adr(
        19, "Knowledge lifecycle (archive, summarize, nightly dedup)",
        context=(
            "Without lifecycle rules, the system accumulates noise. Old lessons nobody uses "
            "still match retrieval queries. Six-month-old conversations clog "
            "`conversations_indexed`. Near-duplicates missed at insert time proliferate."
        ),
        decision=(
            "Three lifecycle rules encoded in CONSTITUTION §5.5: (1) lessons with zero usage "
            "+ low utility after 180 days have their `status` set to `archived` (same row, "
            "excluded from default retrieval); (2) conversations older than 90 days are "
            "replaced with 200-token summaries (embedding preserved); (3) nightly dedup pass "
            "at similarity ≥ 0.95 generates merge proposals in `cross_pollination_queue` "
            "with `proposal_type='merge_candidate'`. All three run in the Dream Engine."
        ),
        consequences=(
            "Retrieval precision holds as the corpus grows. Archived lessons remain "
            "queryable with explicit flag. Operator retains final say on merges — no "
            "automatic deletion."
        ),
        tags=["lifecycle", "archive", "dedup", "dream-engine", "constitutional"],
        decided_by="operator+claude / 2026-04-18",
    ),
    # ADR-020 and ADR-021 are already in the DB (rows b616e850, 97a91903).
    # They are skipped here.
    #
    # Renumbered ADRs from DECISIONS.md to resolve the 026/027 conflict
    # (resolved 2026-05-07 — see Hallazgo 1 in M9.fu3 session).
    _adr(
        30, "infra/db/migrate.py version-format reconciliation deferred",
        context=(
            "`infra/db/migrate.py` records `path.stem` (e.g. `0024_tasks`) as the `version` "
            "column in `schema_migrations`. Pre-existing rows in both `pretel_os` and "
            "`pretel_os_test` use 4-digit prefixes only (`0024`, `0025`, ..., `0031`) — "
            "applied via an earlier convention. The runner's existence check `prior = "
            "already.get(path.stem)` therefore always returns `None` for migrations "
            "0024–0031, prompting re-application; non-idempotent migrations then fail with "
            "`ERROR: trigger already exists` and abort the run on the first non-idempotent "
            "file (currently `0024_tasks.sql`).\n\n"
            "This blocks the runner from being used to apply any new migration without first "
            "either reconciling the schema_migrations rows or fixing the runner's version "
            "derivation. Discovered while applying `0033_projects_table.sql` for Module 7 "
            "Phase B.\n\n"
            "Originally documented as ADR-026 in DECISIONS.md; renumbered to ADR-030 on "
            "2026-05-07 because the `adr_number=26` slot was already taken in the DB by the "
            "Router invariant detector decision."
        ),
        decision=(
            "Defer the runner fix. For new migrations, use the documented workaround:\n"
            "1. Apply the migration directly via `psql -v ON_ERROR_STOP=1 -X -1 -q -d "
            "\"$DB_URL\" -f migrations/NNNN_*.sql`.\n"
            "2. Compute the SHA256 with `sha256sum migrations/NNNN_*.sql | awk '{print $1}'`.\n"
            "3. Insert into schema_migrations using prefix-only version: "
            "`INSERT INTO schema_migrations(version, checksum) VALUES ('NNNN', '<sha>') ON "
            "CONFLICT (version) DO NOTHING`.\n\n"
            "Apply to both `pretel_os` and `pretel_os_test`.\n\n"
            "The proper fix (a one-shot reconciliation migration that backfills full stems "
            "into schema_migrations for rows 0024–0033, plus a runner change to derive "
            "prefix-only `version`) is captured as M7.A.fu2 in `tasks.md` and revisited at "
            "next infra-touching session."
        ),
        consequences=(
            "Every new migration carries an extra two-line ritual until reconciled. The "
            "`migrate.py` runner cannot be used as a single command for fresh applies; "
            "cognitive overhead falls on the operator (or whoever is shipping the migration). "
            "Test database stays in lockstep with prod because both get the same direct-apply "
            "treatment. The reconciliation migration itself, when it lands, is a data-only "
            "change to schema_migrations (rewriting existing rows + inserting any missing); "
            "it carries no schema risk."
        ),
        alternatives=(
            "Fix the runner immediately — rejected: minor scope creep at a phase boundary; "
            "the new migration (0033) needed to land cleanly. Backfill schema_migrations rows "
            "now to match the runner's expected format — rejected: 8 rows × 2 databases = 16 "
            "manual updates with no test coverage on the result. Make every future migration "
            "idempotent enough to survive double-apply — equivalent to keeping the bug."
        ),
        scope="operational",
        severity="normal",
        applicable_buckets=ALL_BUCKETS,
        tags=["migrations", "runner", "schema_migrations", "technical-debt", "renumbered-from-026"],
        decided_by="operator+claude / 2026-04-30",
    ),
    _adr(
        31, "projects (live) and projects_indexed (closed) are intentionally two tables",
        context=(
            "Module 2 shipped `projects_indexed` (DATA_MODEL §2.3) as a historical/closed-"
            "project table with `embedding vector(3072)`, narrative columns (`outcome`, "
            "`closure_reason`, `final_readme`), and `key_decisions JSONB`. It was designed "
            "for semantic recall of finished work, not for active-project state.\n\n"
            "Module 7 Phase B (`create_project` MCP tool) needs a live registry where "
            "(bucket, slug) is unique, where the row carries an active `status='active'` "
            "default, and where the writer is a tool — not a closure ritual. Reusing "
            "`projects_indexed` would have meant either: (a) overloading the table with a "
            "status discriminator and weakening its semantic-recall mission, or (b) "
            "requiring active projects to populate the closure-only columns at insert time.\n\n"
            "Originally documented as ADR-027 in DECISIONS.md; renumbered to ADR-031 on "
            "2026-05-07 because the `adr_number=27` slot was already taken in the DB by the "
            "telemetry INSERT-early decision."
        ),
        decision=(
            "Migration 0033 introduces a separate `projects` table for live, active projects, "
            "distinct from `projects_indexed`. Identity for `projects` is `(bucket, slug)` "
            "unique with default `status='active'`; `projects_indexed` keeps the closure "
            "narrative + embedding column. When a project closes, a future tool (or manual "
            "workflow) copies the row from `projects` → `projects_indexed`, populates the "
            "closure narrative, generates the embedding, and (optionally) deletes from "
            "`projects`. That tool is out of scope for M7.B."
        ),
        consequences=(
            "Queries against 'live projects' go to `projects`; queries against 'what did we "
            "ship before' go to `projects_indexed`. No status filter required to disambiguate. "
            "The router's `_check_project_exists()` checks only `projects` (plus on-disk "
            "README). The `projects` table is small and write-light (one row per active "
            "project); the absence of an embedding column saves a 24KB vector per row. Future "
            "tool: `close_project(bucket, slug, outcome, closure_reason)` copies → indexes → "
            "optionally deletes. Captured as a backlog item; not blocking."
        ),
        alternatives=(
            "Single `projects` table with `status` enum and embedding column — rejected: "
            "forces every active project to either carry NULL embedding (wasted column) or "
            "get embedded prematurely (doesn't capture final state). Add `status` column to "
            "`projects_indexed` and use it for both — same anti-pattern as the lessons-table "
            "consolidation that ADR-021 split apart. Different lifecycle, different writer, "
            "different read pattern → different tables."
        ),
        scope="architectural",
        severity="normal",
        applicable_buckets=ALL_BUCKETS,
        tags=["data-model", "projects", "lifecycle", "m7", "renumbered-from-027"],
        decided_by="operator+claude / 2026-04-30",
    ),
]


# ---------------------------------------------------------------- driver

async def _run(*, dry_run: bool, use_test_db: bool) -> int:
    if use_test_db:
        from dataclasses import replace as dc_replace
        from mcp_server import config as cfg_mod
        original = cfg_mod.load_config

        def _override() -> Any:
            return dc_replace(
                original(),
                database_url="postgresql://pretel_os@localhost/pretel_os_test",
            )

        cfg_mod.load_config = _override  # type: ignore[assignment]

    if not dry_run:
        from mcp_server import db as db_mod
        pool = db_mod.get_pool()
        await pool.open(wait=True)
        await db_mod.start_background_health_check()
        for _ in range(20):
            if db_mod.is_healthy():
                break
            await asyncio.sleep(0.5)
        if not db_mod.is_healthy():
            print("ERROR: db_mod.is_healthy() never became True", file=sys.stderr)
            return 1

    print(f"Migrating {len(ADRS)} foundation ADRs (target: bucket=business, project=pretel-os)")

    if dry_run:
        for a in ADRS:
            print(f"  ADR-{a['adr_number']:03d} [{a['scope']}/{a['severity']}] {a['title']}")
            print(f"    decided_by={a['decided_by']}")
            print(f"    tags={a['tags']}")
        return 0

    # Pre-flight: skip ADRs whose number already exists.
    from mcp_server import db as db_mod
    pool = db_mod.get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT adr_number FROM decisions WHERE adr_number IS NOT NULL")
            existing = {int(r[0]) for r in await cur.fetchall()}

    from mcp_server.tools.decisions import decision_record

    inserted = 0
    skipped = 0
    errors = 0
    for a in ADRS:
        n = int(a["adr_number"])
        if n in existing:
            skipped += 1
            print(f"  ◇ ADR-{n:03d} already in DB — skipped")
            continue

        try:
            r = await decision_record(
                bucket="business",
                project="pretel-os",
                title=a["title"],
                context=a["context"],
                decision=a["decision"],
                consequences=a["consequences"],
                alternatives=a.get("alternatives"),
                scope=a["scope"],
                applicable_buckets=a["applicable_buckets"],
                decided_by=a["decided_by"],
                severity=a["severity"],
                adr_number=n,
                tags=a["tags"],
            )
        except Exception as exc:  # pragma: no cover
            print(f"  ✗ ADR-{n:03d}: {type(exc).__name__}: {exc}")
            errors += 1
            continue

        status = r.get("status")
        if status == "ok":
            inserted += 1
            queued = " (embedding queued)" if r.get("embedding_queued") else ""
            print(f"  ✓ ADR-{n:03d} → {r.get('id')}{queued}")
        else:
            errors += 1
            print(f"  ✗ ADR-{n:03d} → {r}")

    print(f"\nDone: {inserted} inserted, {skipped} skipped, {errors} errors")
    return 0 if errors == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-db", action="store_true")
    args = parser.parse_args()
    return asyncio.run(_run(dry_run=args.dry_run, use_test_db=args.test_db))


if __name__ == "__main__":
    sys.exit(main())
