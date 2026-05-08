# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Reading order before any work

This project has heavy doctrine. Read these in order — every other source defers to them:

1. `AGENTS.md` — LLM reading order + agent rules summary.
2. `identity.md` + `SOUL.md` — operator identity (facts) and voice (behavior contract). L0 layer.
3. `CONSTITUTION.md` — immutable rules. **§11 is the canonical 39-tool inventory.** Rules only change via amendment with a decision log entry.
4. `tools.md` — narrative description of every tool: what / how-activated / when-to-use.
5. `tasks.md` — milestone-only tracker at repo root. Atomic detail lives at `specs/<module>/tasks.md`.
6. `SESSION_RESTORE.md §2 + §13` — current state and last session snapshot.
7. `runbooks/sdd_module_kickoff.md` — the Trinity rule (spec + plan + tasks before code).

If something contradicts a doc, the doc wins. Do not silently reconcile — surface the conflict.

## Architecture (the parts that take multiple files to understand)

**The MCP server is the single gateway.** All clients (Claude.ai web, Claude Code, Telegram bot, future agents) reach pretel-os through one MCP server (`src/mcp_server/main.py`) over Streamable HTTP at `mcp.alfredopretelvargas.com`. No client talks directly to Postgres. The server exposes 39 tools across 11 functional domains; `tools.md` is the narrative reference, `CONSTITUTION §11` is the canonical row-by-row inventory.

**The Router (inside the MCP server) owns context assembly.** Every turn lands at `get_context()` (`src/mcp_server/router/router.py`), which:
1. Classifies the message into `{bucket, project, skill, complexity, needs_lessons}` via LiteLLM proxy alias `classifier_default` (ADR-020), with a rule-based fallback when the proxy is unreachable.
2. Assembles five context layers (`assemble_bundle()` orchestrates `load_l0`..`load_l4`).
3. Detects invariant violations (`invariant_detector.py`).
4. Logs to `routing_logs` (telemetry INSERT-early per ADR-027).
5. Returns a `ContextBundle` dict (ADR-028 — plain dict, not dataclass) carrying classification, layers, recommended tools, `available_skills` and `active_projects` per bucket (M7.5), source conflicts, and degraded-mode flags.

**Five context layers (L0–L4), each with a token budget enforced at write-time by `infra/hooks/pre-commit-token-budget.sh`:**
- L0 (1,200 tok) — `identity.md` + `SOUL.md` + `operator_preferences` table; always loaded.
- L1 (1,500 tok) — `buckets/{bucket}/README.md`; loaded when classified.
- L2 (2,000 tok) — `buckets/{bucket}/projects/{slug}/README.md` + `project_state` + `projects` registry; loaded when project classified.
- L3 (4,000 tok) — `skills/{name}.md`; loaded on demand via `load_skill()`. Three skills today: `sdd`, `vett`, `skill_discovery`.
- L4 (1,500 tok) — `lessons` table with embeddings; loaded when `complexity ≥ MEDIUM` and lessons exist for the bucket.

**Git/DB strict boundary (CONSTITUTION §2.4).** Stable knowledge (constitution, buckets, projects, skills, code, migrations) lives in git; dynamic memory (lessons, embeddings, queues, logs, live registry) lives in Postgres. Dual-homing is forbidden. Module 7.5 added the **awareness layer** that projects DB state to disk: triggers in migration 0034 fire `pg_notify('readme_dirty', ...)` on writes to lessons/tasks/decisions/projects/tools_catalog; `pretel-os-readme.service` LISTENs, debounces 30 seconds, and dispatches `regenerate_*_readme()` from `src/awareness/readme_renderer.py`. Operator notes between `<!-- pretel:notes:start -->` and `<!-- pretel:notes:end -->` are preserved verbatim across regenerations.

**Five background workers (CONSTITUTION §2.6):** Reflection (M6, code committed but not running), Dream Engine (nightly cron, planned), Morning intelligence (n8n, planned), Auto-index on save (live, listens on `embedding_queue`), README consumer (M7.5, live as `pretel-os-readme.service`). The MCP process also hosts a daemon thread for `LayerBundleCache` LISTEN on `layer_loader_cache` (M4 / 0031) — process-internal, not a separate worker.

**Three fixed buckets + dynamic freelance:** `personal`, `business`, `scout`, `freelance:<client-name>`. Scout bucket is **abstract patterns only** — concrete employer data is forbidden in git, DB, prompts, logs, or backups. Defense in depth: pre-commit hook (`.github/hooks/scout-guard.sh`) + MCP `save_lesson` denylist filter + DB trigger `trg_scout_safety_lessons` from migration 0020.

## The Trinity rule (`runbooks/sdd_module_kickoff.md`)

Every module ships its SDD trinity before any code: `specs/<module>/spec.md` + `plan.md` + `tasks.md`. The root `tasks.md` is milestone-only (one line per module phase); atomic detail (one checkbox per migration / function / test) lives in the per-module file. Modules 1–3 closed before this rule; M4 + M0.X + M5 follow it; M7 + M7.5 ran via per-phase operator briefs (no canonical trinity yet — to be retro-built when the modules close formally).

## Two-layer tool registration

When adding a new MCP tool, **three artifacts move in the same commit**:

1. The function under `src/mcp_server/tools/<file>.py`.
2. `app.tool(<name>)` in `src/mcp_server/main.py` — makes it callable via MCP transport.
3. A row in `tools_catalog` — makes it discoverable via `tool_search`, `list_catalog`, `recommend_skills_for_query`, and the Router's `available_skills` injection. Add via a seed migration or via the `register_tool` MCP tool.

Skipping the catalog row is a real bug: the tool is callable but invisible to the discovery loop in `skills/skill_discovery.md`. Migration 0036 caught up three orphans (`report_satisfaction`, `list_pending_cross_pollination`, `resolve_cross_pollination`) that had drifted; the alignment is now zero. `CONSTITUTION §11` documents the rule explicitly.

Same pattern for skills: write `skills/<name>.md`, then `register_skill` (or seed migration) so the catalog knows about it.

## Migrations

Numbered sequentially under `migrations/` (37 files: 0000–0035 + 0028a). `schema_migrations` table is the applied-migration ledger.

**Known runner bug (LL-INFRA-001 / ADR-030, originally drafted as ADR-026):** `infra/db/migrate.py` stores `path.stem` (e.g. `0024_tasks`) as `version` while older rows use 4-digit prefix only (`0024`). Re-running re-attempts already-applied migrations. Sanctioned workaround from M7.B onward:

```bash
psql "$DATABASE_URL" -1 -f migrations/<NNNN_name>.sql
# migration files now embed `INSERT INTO schema_migrations (version) VALUES ('NNNN') ON CONFLICT DO NOTHING`
```

Apply to **both** `pretel_os` (production) and `pretel_os_test`. The two have drifted in the past — RUN 3 of M7.5 found that test DB needed 0028a + 0030 re-applied because earlier resets reverted `notify_missing_embedding` to a buggy CASE form. If a slow test mysteriously fails on a function-not-found or column-not-found, suspect test-DB drift first and re-apply the relevant function migrations.

`migrations/0032_seed_skills_sdd_vett.sql` is on disk but **NOT YET APPLIED** (M7.A.fu1, tracked in `tasks.md` Module 7).

## Common commands

Tests (system pytest at `/home/pretel/.local/bin/pytest`, not the venv's; venv lacks pytest):

```bash
# Default — runs everything except eval-cost tests, includes slow tests
PYTHONPATH=src pytest tests/

# Fast iteration — skip slow (DB-backed + OpenAI embedding) tests
PYTHONPATH=src pytest tests/ -m "not slow"

# Slow only (DB-backed)
PYTHONPATH=src pytest tests/ -m slow

# Single test
PYTHONPATH=src pytest tests/awareness/test_readme_renderer.py::test_round_trip_preserves_notes_block_byte_for_byte -v

# Live LLM eval (costs real money, opt-in)
PYTHONPATH=src pytest tests/ -m eval
```

Type checking (mypy strict, several legacy modules ignored — see `mypy.ini`):

```bash
mypy src/awareness/ src/mcp_server/tools/awareness.py
mypy src/mcp_server/router/router.py
```

Services (systemd user units):

```bash
systemctl --user status pretel-os-mcp pretel-os-bot pretel-os-readme
systemctl --user restart pretel-os-mcp
journalctl --user -u pretel-os-mcp -n 50 --no-pager
```

Database (DSNs in `~/.env.pretel_os`, mode 0600):

```bash
set -a; source /home/pretel/.env.pretel_os; set +a
psql "$DATABASE_URL"                # production: pretel_os
psql postgresql://pretel_os@localhost/pretel_os_test    # test DB

# Inspect catalog state
psql "$DATABASE_URL" -c "SELECT count(*) FROM tools_catalog WHERE deprecated=false AND archived_at IS NULL;"
```

Health check from outside (Cloudflare Tunnel):

```bash
curl -f https://mcp.alfredopretelvargas.com/health
```

## Conventions worth knowing

- **Async tools, sync renderer.** MCP tool functions are `async def` and use `db_mod.get_pool()` for the async pool. The awareness renderer is sync; MCP wrappers call it via `asyncio.to_thread(_sync_helper, cfg.database_url, ...)` opening a fresh sync `psycopg.connect()`. When a test patches `db_mod`, also patch `config_mod.load_config` to redirect `database_url` to the test DB — otherwise `create_project` and `archive_project` silently regenerate against production state.
- **No client lock-in.** Do not add client-specific assumptions to MCP code. The same server must work for Claude.ai web, Claude Code, Claude mobile, and Telegram.
- **Lesson auto-approval has four conditions** (CONSTITUTION §5.2 rule 13): title + content + concrete-technology reference + `next_time` clause + no duplicate ≥0.92 similarity. Anything that fails one condition queues for `pending_review`.
- **`decisions.project` is `NOT NULL`** — `decision_record` requires a project (the Module 0.X spec drift documented in commit 9a94e93). The legacy text column stays populated; M7.5 added `project_id UUID FK` alongside it.
- **Embeddings are `text-embedding-3-large` (3072 dim).** Switching models requires full reindex + amendment. Never mix dimensions in one column.
- **LiteLLM proxy aliases, not direct provider calls.** `classifier_default` and `second_opinion_default` are configured in `~/.litellm/config.yaml`. Hardwiring `model="claude-..."` in router code is a violation.
- **Pre-commit token budgets.** `infra/hooks/pre-commit-token-budget.sh` blocks commits that push any layer file over budget. The hook advises the corrective action; it never truncates silently.
- **Never edit a bucket README's auto sections by hand.** They will be overwritten on the next regenerate. Operator content goes between the `<!-- pretel:notes -->` markers, which the renderer preserves byte-for-byte.

## When something feels off

- **Slow test fails on a function or column not found** → suspect test-DB drift. Check `psql "$TEST_DSN" -c "\df notify_missing_embedding"` and re-apply 0028a + 0030 if needed.
- **README not updating after a write** → check `pretel-os-readme.service`; the consumer must be running for the projection contract to hold (Postgres does not replay missed NOTIFYs).
- **`tool_search` returns fewer results than expected** → it is filtered + capped at 50. For inventory use `list_catalog()`. The catalog has 42 rows today (39 tools + 3 skills).
- **Classifier picks the wrong bucket** → record via `router_feedback_record` (do not silently work around it). Phase F tuning runbook (`runbooks/router_tuning.md`) consumes these rows.

When in doubt, the **doc wins** over implicit behavior. Surface the conflict; do not reconcile silently.
