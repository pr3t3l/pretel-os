# Module 3 (Part 1): MCP Server v0 — local

## What
Stand up the MCP server described in `CONSTITUTION §2.1/§2.2` and `PROJECT_FOUNDATION §2.5` — a FastMCP Python app that exposes pretel-os tools over Streamable HTTP. Part 1 covers everything local: scaffold, auth, DB pool, embeddings, fallback journal, 7 tools, `/health`, and a systemd user unit. Cloudflare Tunnel exposure and client onboarding land in Part 2.

## Inputs
- `pretel_os` Postgres 16 database from Module 2 (21 tables + seeds) reachable via `~/.env.pretel_os`
- OpenAI key for `text-embedding-3-large` (3072 dims) per `CONSTITUTION §2.5`
- `fastmcp>=2.0` framework (Streamable HTTP transport)
- Existing `identity.md` at repo root for the L0 stub

## Outputs
- `src/mcp_server/` package, installed runnable as `python -m mcp_server.main`
- Tools: `get_context` (L0 stub), `save_lesson`, `search_lessons`, `register_skill`, `register_tool`, `load_skill`, `tool_search`
- Plain HTTP `GET /health` (no auth) used by systemd and future uptime monitoring
- Lazy DB connection pool with a 30 s background health poller
- ASGI middleware enforcing `X-Pretel-Auth` on every request except `/health`
- Fallback journal at `/home/pretel/pretel-os-data/fallback-journal/YYYYMMDD.jsonl` for mutations during DB outages
- `~/.config/systemd/user/pretel-os-mcp.service` (enabled, not started)
- `MCP_SHARED_SECRET` populated in `~/.env.pretel_os`

## Constraints
- No HNSW search — pgvector 0.6.0 limit. Use `ORDER BY embedding <=> query_embedding LIMIT k` with filter-first predicates per `CONSTITUTION §5.6` rule 26.
- Every tool must honor `db_healthy`: reads return `{status:'degraded', degraded_reason:'db_unavailable'}`; mutations persist to the fallback journal and return `{status:'degraded', journal_id:...}` per `CONSTITUTION §8.43 (b)`.
- Lazy DB init per `CONSTITUTION §8.43 (a)` — server starts even if Postgres is down.
- Constant-time secret comparison per `INTEGRATIONS §11.1`.
- Secrets via env only (`CONSTITUTION §3.4`); no hardcoding.
- `save_lesson` runs pre-save duplicate detection (threshold 0.92) per `CONSTITUTION §5.2` rule 14; auto-promotes to `active` when the four auto-approval conditions in rule 13 are met.
- Every tool invocation logs to `usage_logs`; `get_context` also logs to `routing_logs` with `classification_mode='stub'` for Part 1.
- `/health` never requires auth; always returns HTTP 200 even when DB is unhealthy.

## Out of scope (Part 2 and later)
- Cloudflare Tunnel + public subdomain
- Claude.ai / Claude Code / Claude mobile connector onboarding
- Router classification (Haiku 4.5) — Part 1 ships a stub L0 responder
- L1–L4 context loading
- Reflection worker, Dream Engine, Forge pipeline
- Additional tools listed in `PROJECT_FOUNDATION §2.5` (`create_project`, `snapshot_project`, `request_second_opinion`, etc.)
