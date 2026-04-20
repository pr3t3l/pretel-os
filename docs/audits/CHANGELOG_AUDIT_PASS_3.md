# pretel-os Foundation — Audit Pass 3 Changelog

**Date applied:** 2026-04-19
**Audit sources:** GPT-5.4 adversarial (12 findings), Gemini 3.1 Pro adversarial (5 findings), Gemini 3.1 Pro strategic (~15 opportunities), Claude consistency check (8 observations)
**Operator:** Alfredo Pretel Vargas
**Total items applied:** 19 audit fixes + 5 Gemini Strategic ideas promoted + 12 ideas seeded to backlog

This changelog is a reference for what changed, why, and where to find it in the final foundation docs. It sits alongside the 5 foundation documents and does not replace them.

---

## Final document state

| Document | Lines | Status |
|----------|------:|:------:|
| CONSTITUTION.md | 340 | ✅ v4 |
| PROJECT_FOUNDATION.md | 624 | ✅ v3 |
| DATA_MODEL.md | 1,322 | ✅ v3 |
| INTEGRATIONS.md | 809 | ✅ v2 |
| LESSONS_LEARNED.md | 644 | ✅ v1 (unchanged since creation) |
| **Total** | **3,739** | |

Foundation documents are complete. Ready to begin Module 1 (`infra_migration`) per SDD.

---

## Changes applied — by balde (priority bucket)

### 🔴 Balde 1 — Release blockers (6 items)

**Item 1: Lessons lifecycle normalized to single-table model across all docs.**
- Source: GPT FINDING-003 + Claude consistency #1.
- Changes: CONSTITUTION rules 13, 22, 24 rewritten; PROJECT_FOUNDATION Module 5, Module 6, ADR-019 rewritten; DB list on line 76 cleaned up.
- Before: Docs referenced `lessons_pending_review`, `lessons_archive` as separate tables contradicting DATA_MODEL's single-table enum design.
- After: Every reference uses `status='pending_review' | 'active' | 'archived' | 'merged_into' | 'rejected'` on the single `lessons` table.

**Item 2: Table counts aligned across all docs.**
- Source: GPT FINDING-010 + Claude consistency #2.
- Changes: PROJECT_FOUNDATION Module 2 and doc registry now reference "16 Phase-1 tables + 5 Phase-2 tables (21 total)".
- Before: "all 15 tables" references contradicted DATA_MODEL's 18-table count.
- After: Consistent numbers (we later added 3 tables in Balde 2-3, so final count is 21).

**Item 3: `tool_search` added to authoritative inventory + sync table extended.**
- Source: GPT FINDING-004 + Claude consistency #3.
- Changes: PROJECT_FOUNDATION §2.5 context retrieval list + cross-layer sync list now include `tool_search` and `change_stack`. CONSTITUTION §7.36 sync table extended with `register_tool` and `change_stack` rows.
- Before: Rules required `tool_search` but the inventory didn't list it.
- After: Consistent surface — rules point to tools that exist.

**Item 4: Schema aligned with LESSONS_LEARNED process.**
- Source: Claude consistency #4.
- Changes: DATA_MODEL `lessons` table now includes `applicable_buckets TEXT[]` and `metadata JSONB` columns, plus GIN index on `applicable_buckets`.
- Before: LESSONS_LEARNED §2 mentioned `metadata.severity` and `applicable_buckets` but neither existed in the schema.
- After: 1:1 mapping between process doc and real table.

**Item 5: MCP_SHARED_SECRET required from Phase 1 (Option A).**
- Source: GPT FINDING-001.
- Operator decision: Option A chosen after clarifying that Claude.ai web and Claude mobile cannot reach Tailscale (they run on Anthropic servers, not local device).
- Changes: INTEGRATIONS §11.1 now mandates `X-Pretel-Auth` header from day 1, with detailed client config (Claude.ai connector, Claude Code mcp.json), rotation procedure, failure handling (401 with audit logging, Telegram alert on sustained failures).
- Before: Phase 1 trusted tunnel-scoped requests without app-level auth.
- After: Defense in depth from bootstrap — no tunnel-bypass exposure to state-mutation tools.

**Item 6: Auto-approval polarity fantasy eliminated.**
- Source: Gemini-adv FINDING-001.
- Changes: CONSTITUTION rule 13 rewritten. Similarity ≥ 0.92 → always flagged as `merge_candidate` for manual review. The system no longer pretends to detect "opposite advice" via vector similarity — that's a mathematical impossibility.
- Before: "does not contradict an existing lesson (semantic similarity < 0.92 with any existing lesson of opposite advice)" — untestable.
- After: Clean rule, no claimed capabilities the system doesn't have.

---

### 🟡 Balde 2 — Before Module 2: data_layer (6 items)

**Item 7: `reflection_pending` and `conversation_sessions` tables modeled.**
- Source: GPT FINDING-008 + Claude consistency #5.
- Changes: DATA_MODEL §4.5 and §4.6 add both tables with complete schema (session_id, trigger_event, transcript_ref, routing_context, status, close_reason, etc.).
- Before: Reflection worker had no session model; reflection_pending referenced in prose as "not yet modeled."
- After: Sessions are first-class entities. Idle detection, turn-count fallback, and 60-min lifespan fallback all query `conversation_sessions`.

**Item 8: Fallback file contract specified.**
- Source: GPT FINDING-002 + Claude consistency #6.
- Changes: CONSTITUTION §8.43(b) defines path (`/home/operator/pretel-os-data/fallback-journal/YYYYMMDD.jsonl`), format (append-only JSONL with idempotency_key), encryption (LUKS on data volume), replay worker, retention (90 days post-processed), failure escalation (Telegram alert after 5 failed replays).
- Before: "queued write to a local fallback file" in prose — no contract.
- After: Implementable contract with replay idempotency guarantees.

**Item 9: Archive guard uses structured references.**
- Source: GPT FINDING-005.
- Changes: DATA_MODEL `project_state` now has `related_lessons UUID[]` with GIN index. `archive_low_utility_lessons()` rewritten to use `lessons.id = ANY(ps.related_lessons)` instead of `LIKE '%uuid%'`.
- Before: Substring match in free text — false positives and false negatives.
- After: Structured relational check. Clean.

**Item 10: L0 split into immutable invariants + contextual identity.**
- Source: GPT FINDING-006.
- Changes: CONSTITUTION §2.7 rewritten into two regimes. Immutable invariants (security, Scout, token budgets, Git/DB boundary, agent rules) are non-overridable and enforced structurally. Ordered priority (L2 > L3 > L4 > L1 > L0 contextual) applies only to non-invariant content.
- Before: Global meta-rules given weakest priority — could be "correctly" overridden while violating invariants.
- After: Invariants win silently at the system level; contextual L0 participates in ordered arbitration.

**Item 11: Log tables monthly partitioned.**
- Source: Gemini-adv FINDING-002.
- Changes: DATA_MODEL `routing_logs`, `usage_logs`, `llm_calls` all converted to `PARTITION BY RANGE (created_at)` with monthly partitions. Retention enforced by `DROP TABLE partition_YYYY_MM` (O(1), no vacuum overhead) instead of DELETE.
- Before: Standard tables with "retention 90 days, purged by Dream Engine" — DELETE-based, causes bloat.
- After: Instant partition drops, no autovacuum pressure, scales to millions of rows.

**Item 12: Lazy DB initialization.**
- Source: Gemini-adv FINDING-003.
- Changes: CONSTITUTION §8.43(a) mandates MCP server starts and registers tools regardless of Postgres availability. `db_healthy` boolean refreshed every 30s; tool functions check at execution time.
- Before: Startup deadlock if Postgres failed to come up after Vivobook reboot.
- After: Graceful degraded-mode on any startup configuration.

---

### 🟢 Balde 3 — Before 5 freelance clients (4 items)

**Item 13: Multi-tenant `client_id` added to remaining tables.**
- Source: GPT FINDING-007 + Gemini Strategic CONCERN-002.
- Changes: DATA_MODEL adds `client_id UUID` to: `tools_catalog`, `project_state`, `project_versions`, `patterns`, `decisions`, `ideas`, `llm_calls` (previously only `lessons`, `conversations_indexed`, `contacts`). Partial indexes on each for filter performance.
- Before: "multi-tenant-ready" claim contradicted by missing `client_id` on live-state and knowledge-shaping tables.
- After: Every client-relevant mutable table has the column ready for filter-first SQL-level scoping.

**Item 14: L1 sub-buckets pattern.**
- Source: Gemini Strategic CONCERN-001.
- Changes: CONSTITUTION §2.3 documents sub-bucket pattern (`buckets/business/freelance/clients/README.md` paginated). Router loads only relevant sub-bucket per classification. Pre-commit hook signals when bucket README exceeds 80% of 1,500-token budget.
- Before: Single `business/README.md` would exceed L1 budget at ~15 active projects.
- After: Unbounded scalability — any sub-bucket is a separate L1 load.

**Item 15: Write-time token budget enforcement.**
- Source: Gemini-adv FINDING-004.
- Changes: CONSTITUTION §7.36 adds pre-commit hook rule. `infra/hooks/pre-commit-token-budget.sh` counts tokens via `tiktoken cl100k_base` and blocks commits that push a layer over budget.
- Before: Read-time summarization would add 5–15s latency mid-request.
- After: Constraints enforced at commit-time. Read-time summarization remains only as belt-and-suspenders fallback.

**Item 16: `control_registry` table.**
- Source: GPT FINDING-012.
- Changes: DATA_MODEL §5.6 adds `control_registry` table with 6 seed controls (scout_audit, restore_drill, key_rotation_anthropic, key_rotation_openai, pricing_verification, uptime_review). Each with cadence, owner, evidence_required, last_completed_at, next_due_at (computed column), alert_sent_at.
- Before: Manual controls (Scout audit, restore drill, etc.) tracked "in calendar" — invisible to the system.
- After: Dream Engine checks nightly. Overdue controls alert via Telegram. Operator attestation logged.

---

### 🔵 Balde 4 — Sincera claims (3 items)

**Item 17: Uptime 99% → 95% Phase 1-3, with UptimeRobot external monitoring.**
- Source: GPT FINDING-009 + Gemini-adv FINDING-005.
- Changes: PROJECT_FOUNDATION §1.3 uptime criterion rewritten. New INTEGRATIONS §10.5 adds UptimeRobot integration (free tier, 5-min pings, monthly email evidence for control_registry.uptime_review).
- Before: 99% target on single consumer laptop with one ingress path — not structurally supported.
- After: Honest 95% target Phase 1-3, 99% deferred to Phase 4+ with managed hosting. Actual uptime measured externally.

**Item 18: "Multi-tenant-ready" → "migration-aware."**
- Source: GPT FINDING-007.
- Changes: CONSTITUTION §1 rewritten. PROJECT_FOUNDATION §1.4 expanded with explicit scope of migration gap. True multi-tenant isolation (per-client backups, RLS, tenant deployments) explicitly out of scope until Phase 5+.
- Before: "multi-tenant-ready later" overclaimed readiness.
- After: Accurate description — columns exist, full isolation doesn't.

**Item 19: Manual controls accepted via control_registry.**
- Source: Claude consistency pattern + GPT FINDING-012.
- Changes: PROJECT_FOUNDATION §1.4 adds "Weak controls" subsection that explicitly acknowledges Scout audit, restore drill, key rotation, uptime review, pricing verification as manual-with-tracking rather than automated.
- Before: "Manual discipline is NOT enforcement" rule followed by docs that relied on manual discipline.
- After: Acknowledged as weak controls, tracked in `control_registry`.

---

## Gemini Strategic — Opportunities applied (Option C)

### Promoted to roadmap (5 items)

**Skills added to Module 7 (skills_migration), duration extended 3d → 5d:**
- `client_discovery.md` — 5-question intake for new freelance clients (Gemini SKILL-001)
- `sow_generator.md` — drafts Statements of Work (Gemini SKILL-002)
- `mtm_efficiency_audit.md` — industrial-engineering digital audits, $2.5–5k productizable (Gemini SKILL-003)

**Tool added to §2.5 inventory:**
- `log_time_and_cost(project, duration_mins, cost_usd, description, client_id?)` — time + external API cost tracking for freelance margin (Gemini TOOL-003)

**Productized services added to §1.4:**
- AI Governance Starter Pack ($5–10k one-off) (Gemini SERVICE-001)
- Competitor Intel Briefs ($500–1k/month retainer) (Gemini SERVICE-002)
- MTM Digital Efficiency Audit ($2.5–5k per audit) (from SKILL-003)

**Architecture added to §2.3:**
- L1 sub-buckets pattern for scalability (Gemini CONCERN-001, applied as Balde 3 Item 14)

### Seeded to `ideas` table via Module 8 (12 items)

Per PROJECT_FOUNDATION §5.2, these are inserted into `ideas` on Module 8 completion with `status='new'`:

- Context-switching sandbox: `suspend_context` / `/resume` commands
- Academic research ingestion: n8n webhook for PDFs → L4 lessons
- Automated transaction categorization: `log_transaction` tool
- Content repurposer skill: technical logs → LinkedIn/TikTok content (productizable $1.5k/mo retainer)
- `create_client_engagement(client_name, service_tier, target_bucket)` tool
- `generate_client_report(project, report_type)` tool
- White-label Declassified content engine ($3–8k per campaign)
- Stripe integration for automated invoicing
- Google Workspace integration (Gmail ingestion alias + Calendar)
- Toggl Track integration for margin-per-project
- LatAm/Spanish AI market play: translate VETT + AI Governance to Spanish
- Automated failover environment: Ansible/docker-compose 15-min provisioning

### Rejected with rationale (3 items)

- **Local quantized Haiku router (Gemini OPPORTUNITY-002).** API cost is $2–5/month at projected volume; maintaining a local model adds complexity that outweighs savings.
- **Ollama 8B local DLP for Scout (Gemini challenge 1).** Regex denylist + MCP filter + DB trigger is sufficient defense in depth. Running an 8B model 24/7 for every insert is over-engineering at current scope.
- **Redis for queues (Gemini challenge 2).** `pending_embeddings` + `reflection_pending` as DB-native partitioned tables with `pg_notify` for wake-up is simpler and sufficient at operator volume.

---

## Cross-document reference for the 19 items

| Item | Primary doc | Section(s) |
|------|-------------|------------|
| 1 | CONSTITUTION | §5.1 rule 13, §5.5 rules 22/24 |
| 2 | PROJECT_FOUNDATION | Module 2, Doc registry |
| 3 | PROJECT_FOUNDATION / CONSTITUTION | §2.5 inventory, §7.36 sync table |
| 4 | DATA_MODEL | §2.1 lessons table |
| 5 | INTEGRATIONS | §11.1 Claude.ai connector |
| 6 | CONSTITUTION | §5.1 rule 13 |
| 7 | DATA_MODEL | §4.5 reflection_pending, §4.6 conversation_sessions |
| 8 | CONSTITUTION | §8.43(b) fallback file contract |
| 9 | DATA_MODEL | §2.4 project_state + §6.5 archive function |
| 10 | CONSTITUTION | §2.7 source priority |
| 11 | DATA_MODEL | §4.1, §4.2, §4.3 partitioned log tables |
| 12 | CONSTITUTION | §8.43(a) lazy DB init |
| 13 | DATA_MODEL | §2.2, §2.4, §2.5, §5.1, §5.2, §5.5 + §4.3 |
| 14 | CONSTITUTION | §2.3 L1 sub-buckets |
| 15 | CONSTITUTION | §7.36 pre-commit hook |
| 16 | DATA_MODEL | §5.6 control_registry |
| 17 | PROJECT_FOUNDATION / INTEGRATIONS | §1.3 uptime, §10.5 UptimeRobot |
| 18 | CONSTITUTION / PROJECT_FOUNDATION | §1 overview, §1.4 productization |
| 19 | PROJECT_FOUNDATION / DATA_MODEL | §1.4 weak controls, §5.6 registry |

---

## What was NOT changed

Decisions explicitly preserved despite audit pressure:

- **`text-embedding-3-large` (3072 dims)** — challenged three times across reviews. Measured delta: 6 cents/month vs 3-small, +3.7 MTEB retrieval points, ~60 MB storage. Kept; noise ratio favored keeping.
- **Single Vivobook hardware point of failure** — accepted as Phase 1-3 trade-off. Gemini RISK-002 mitigation (failover Ansible script) deferred to ideas backlog.
- **Claude as the only LLM provider for pretel-os internals** — LiteLLM reserved for Forge and future multi-provider workflows, but Router/Reflection call Anthropic directly for cleaner metrics.
- **ADRs 1-18 in PROJECT_FOUNDATION §5** — all original decisions stand. ADR-019 rewritten to reflect single-table lifecycle; no other ADR changed.

---

## Next steps

1. **Commit all 5 foundation docs to `pr3t3l/pretel-os` repo.** This is the canonical foundation set. Tag as `foundation-v1.0`.
2. **Begin Module 1: `infra_migration`.** Per PROJECT_FOUNDATION §4. Write `specs/infra_migration/spec.md` using the SDD template. Four weeks of consolidation work: Ubuntu 24.04 Desktop on Vivobook, move Forge + n8n + Postgres + LiteLLM onto the new server, retire WSL setup.
3. **After Module 1 ships, proceed sequentially:** Module 2 (data_layer), Module 3 (mcp_server_v0), Module 4 (router), etc.
4. **Quarterly review** per `control_registry` — first review Jul 19, 2026.

Foundation is done. Time to build.
