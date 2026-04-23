# INTEGRATIONS — pretel-os

**Status:** Active
**Last updated:** 2026-04-18
**Owner:** Alfredo Pretel Vargas

This document specifies every external service and internal integration that pretel-os consumes or exposes: endpoints, authentication, rate limits, costs, retry policies, degraded-mode fallbacks, credential management, and health checks. It is the operational reference for Module 3 (`mcp_server_v0`) and every subsequent module that touches a third party.

All figures here are as of 2026-04-18. Prices and limits change; each integration's §Health check step includes a reminder to re-verify quarterly.

---

## 1. Overview and principles

### 1.1 Inventory

Nine integrations, grouped by direction:

**Outbound (pretel-os calls them):**
- Anthropic API (classification, reasoning, reflection)
- OpenAI API (embeddings only)
- Supabase (Phase 4+; local pgvector until then)
- Cloudflare (Tunnel + optional DNS delegation)
- IONOS (DNS zone for alfredopretelvargas.com)
- Telegram Bot API
- LiteLLM proxy (internal multi-provider gateway, reused from prior stack)
- n8n webhooks (for Forge and other workflows)
- Tailscale (VPN control plane)

**Inbound (they reach pretel-os):**
- Claude.ai web / Claude Code / Claude mobile (via MCP over Cloudflare Tunnel)
- Telegram (webhook from bot API)
- Any MCP-compatible client (future: Cursor, Antigravity, Codex)

### 1.2 Principles

1. **Every external call has a declared timeout in `infra/timeouts.yaml`.** No default timeouts. No silent infinite waits.
2. **Retries use exponential backoff with jitter.** Maximum 3 attempts. After the third failure, the call enters degraded-mode handling per `CONSTITUTION §8.43`.
3. **Credentials never live in git.** `.env` files listed in `.gitignore`, systemd environment files at `0600`, or Supabase Vault.
4. **One credential = one purpose.** The Anthropic key used by the Router is not the same key used by Claude Code (operator's subscription). Mixing complicates rotation and obscures cost attribution.
5. **Every call logs to `llm_calls` or `routing_logs`.** Anthropic calls, OpenAI embedding calls, and n8n webhook invocations are audited per `DATA_MODEL §4.1–4.3`.
6. **Health checks are cron'd, not reactive.** The Dream Engine verifies every external dependency's reachability nightly and logs a `gotcha` entry if anything drifts.
7. **Quarterly verification.** Prices, rate limits, and API versions are re-verified every 90 days by the operator. A calendar recurrence (not an agent task) enforces this.

### 1.3 Credential management

All credentials live in one of three locations. No fourth option exists.

| Location | Used for | Access control |
|----------|----------|----------------|
| `/home/operator/.env.pretel_os` (mode 0600) | MCP server, Router, Reflection worker | systemd loads via `EnvironmentFile=` directive |
| `/home/operator/.config/systemd/user/*.service` with `Environment=` lines | Telegram bot token, n8n admin password | Per-service isolation |
| Supabase Vault (Phase 4+) | Production secrets after cloud migration | Row-level security, audit log |

Naming convention for environment variables:

- `{SERVICE}_API_KEY` — primary credential (ex: `ANTHROPIC_API_KEY`)
- `{SERVICE}_URL` — base URL (ex: `LITELLM_URL`)
- `{SERVICE}_TIMEOUT_MS` — call timeout override
- `{SERVICE}_BASE_URL` — when a non-default endpoint is used (ex: staging)

Rotation policy: every credential rotates at least every 180 days. Operator-driven, tracked by an automated reminder: an n8n workflow `key_rotation_reminder` reads `credential_registry.yaml` (a per-credential file in git listing expiry dates) and sends a Telegram alert 7 days before expiry. A rotation invalidates the old key and updates `/home/operator/.env.pretel_os`, followed by `systemctl --user restart pretel-os-mcp` and a smoke test.

### 1.4 Timeouts baseline

Source of truth: `infra/timeouts.yaml`. Values below are the Phase-1 defaults; tune after 30 days of `routing_logs` data.

| Call | Timeout | Rationale |
|------|--------:|-----------|
| Haiku 4.5 classification | 3,000 ms | Classifications are short; anything slower is a signal |
| Opus 4.7 reasoning | 60,000 ms | Operator-facing; longer waits surface through client UI |
| Sonnet 4.6 reflection | 30,000 ms | Background; timeout hits fallback queue |
| OpenAI embedding (single) | 5,000 ms | Fast endpoint, should rarely timeout |
| OpenAI embedding (batch) | 15,000 ms | Up to 2048 items per request |
| n8n webhook (Forge trigger, async) | 10,000 ms | Webhook returns immediately; pipeline async |
| n8n webhook (sync workflow, short) | 120,000 ms | When n8n must return data inline; only for workflows < 2 min |
| n8n sync timeout policy | — | Any workflow expected to exceed 2 min MUST be async. VETT full runs, Forge full pipeline, multi-phase research all async by default. Sync is only for quick lookups and status queries. |
| Supabase query | 5,000 ms | Phase 4+ only |
| Telegram Bot API call | 10,000 ms | |
| Cloudflare Tunnel upstream | 30,000 ms | Upstream to local MCP server |
| LiteLLM second opinion | 15,000 ms | Operator-invoked validation; fast enough to stay tactical |

---

## 2. Anthropic API

### 2.1 Purpose

Three distinct uses, three distinct models:

- **Router classification** (Haiku 4.5) — per `CONSTITUTION §4.8`
- **Reflection worker** (Sonnet 4.6) — per `CONSTITUTION §2.6`
- **Client-side reasoning** (Opus 4.7) — not called by pretel-os directly; the client (Claude.ai, Claude Code) handles this. pretel-os only assembles context.

### 2.2 Endpoint

- Base URL: `https://api.anthropic.com`
- Endpoint: `POST /v1/messages`
- Header: `x-api-key: $ANTHROPIC_API_KEY`
- Header: `anthropic-version: 2023-06-01`
- Content-Type: `application/json`

### 2.3 Authentication

- Environment variable: `ANTHROPIC_API_KEY`
- Format: `sk-ant-api03-...`
- Scope: separate keys per use (router classification key vs reflection worker key) to enable per-purpose cost attribution and independent rotation.
- Credential storage: `/home/operator/.env.pretel_os`

### 2.4 Models used

| Model ID | Role | Typical input | Typical output |
|----------|------|--------------:|---------------:|
| `claude-haiku-4-5-20251001` | Router classifier | ~1,000 tok | ~100 tok |
| `claude-sonnet-4-6-20250929` | Reflection worker | ~4,000 tok | ~800 tok |

Note: Opus 4.7 calls happen client-side (Claude.ai / Claude Code charges the operator's subscription), not through pretel-os's API key.

### 2.5 Rate limits

At Tier 1 (minimum $5 deposit, current operator tier):

| Limit | Haiku 4.5 | Sonnet 4.6 |
|-------|----------:|-----------:|
| Requests per minute | 50 | 50 |
| Input tokens per minute | ~50,000 | ~30,000 |
| Output tokens per minute | ~8,000 | ~8,000 |
| Monthly spend cap | $100 | $100 (shared) |

For pretel-os Phase 1–3 projected volume (~3,000 classifications/month, ~200 reflections/month), Tier 1 is comfortable. Tier advancement is automatic on cumulative spend.

### 2.6 Pricing

| Model | Input $/MTok | Output $/MTok | Cached input $/MTok |
|-------|-------------:|--------------:|--------------------:|
| Haiku 4.5 | $1.00 | $5.00 | $0.10 (est. 90% discount) |
| Sonnet 4.6 | $3.00 | $15.00 | $0.30 |
| Opus 4.7 (client-side) | ~$5.00 | ~$25.00 | ~$0.50 |

Prompt caching is ~90% off cached input tokens with a TTL. The Router's classifier prompt is constant and ideal for caching; expect effective Haiku cost closer to $0.30/MTok input after caching warms up.

### 2.7 Retry policy

```python
# src/mcp_server/anthropic_client.py
MAX_ATTEMPTS = 3
BASE_DELAY_MS = 500
MAX_DELAY_MS = 8000
RETRYABLE_STATUSES = {429, 500, 502, 503, 504, 529}  # 529 = overloaded

def retry_delay(attempt):
    base = min(BASE_DELAY_MS * (2 ** attempt), MAX_DELAY_MS)
    jitter = random.uniform(0, base * 0.3)
    return base + jitter
```

`overloaded_error` (HTTP 529) retries with longer backoff (base × 4). `invalid_request` (HTTP 400) never retries.

### 2.8 Degraded mode

Per `CONSTITUTION §8.43`:
- **Haiku down** → Router falls back to rule-based classifier (keyword + regex match over bucket/project names from L0). Returns with `classification_mode=fallback_rules`. Confidence is lower; L4 RAG fires more conservatively.
- **Sonnet down** → Reflection worker queues its pending work to DB (`reflection_pending` table, not yet modeled — to be added in Phase 1.5 if needed). Next run picks up.

### 2.9 Health check

Nightly via Dream Engine:

```python
response = anthropic_client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=10,
    messages=[{"role": "user", "content": "ping"}]
)
assert response.content[0].text.strip() != ""
```

Failure writes a `gotcha` entry and sends a Telegram alert.

---

## 3. OpenAI API

### 3.1 Purpose

Single purpose: embeddings. `text-embedding-3-large` for every vector in the system per `CONSTITUTION §2.5`. No chat or completion models from OpenAI.

### 3.2 Endpoint

- Base URL: `https://api.openai.com`
- Endpoint: `POST /v1/embeddings`
- Header: `Authorization: Bearer $OPENAI_API_KEY`
- Content-Type: `application/json`

### 3.3 Authentication

- Environment variable: `OPENAI_API_KEY`
- Format: `sk-proj-...` or `sk-...`
- Scope: embeddings only — when creating the key in OpenAI dashboard, restrict to "Model capabilities: Embeddings" to minimize blast radius.

### 3.4 Model

- Model ID: `text-embedding-3-large`
- Dimensions: 3072
- Max input: 8,191 tokens per item
- Batch support: up to 2,048 items per request

### 3.5 Rate limits

At Tier 1:

| Limit | Value |
|-------|------:|
| Requests per minute | 3,000 |
| Tokens per minute | 1,000,000 |
| Requests per day | 10,000 |

pretel-os's projected volume (~500 embeddings/month write + ~3,000/month query = ~3,500/month) is three orders of magnitude below Tier 1 limits.

### 3.6 Pricing

| Tier | $/MTok | Notes |
|------|-------:|-------|
| Standard | $0.13 | Synchronous call, immediate response |
| Batch | $0.065 | Async, 24-hour turnaround, 50% discount |

For pretel-os:
- Real-time writes (on lesson save) → Standard tier
- Initial migration of 89 existing lessons + seed conversations → Batch tier (cheaper, latency irrelevant)

Projected monthly cost: **under $1/month** at current volume.

### 3.7 Retry policy

Same exponential-backoff pattern as Anthropic. OpenAI returns `429` for rate limit exceeded and `500/502/503` for service issues. All retryable.

### 3.8 Degraded mode

Per `CONSTITUTION §8.43`:
- **Embedding writes** queue to `pending_embeddings` table (per `DATA_MODEL §4.4`). Rows are inserted without embeddings; the Auto-index worker flushes when API returns.
- **Embedding queries (RAG)** return `degraded_mode=true` with `lessons=[]`. The client sees an explicit marker and communicates to the operator that retrieval is unavailable — not an empty-but-silent response.

### 3.9 Health check

Nightly:

```python
response = openai_client.embeddings.create(
    model="text-embedding-3-large",
    input="health check"
)
assert len(response.data[0].embedding) == 3072
```

### 3.10 Migration flag (dimension change)

See `DATA_MODEL §11.5`. Any change to the embeddings model triggers a full reindex and a constitutional amendment. Not a routine operation.

---

## 4. LiteLLM proxy

### 4.1 Purpose

Reused component from the prior stack. Acts as a unified gateway in front of multiple LLM providers (Anthropic, OpenAI, Gemini, others), enabling model swapping without changing application code. Used by the Forge pipeline and optionally by pretel-os's MCP server for LLM calls.

### 4.2 Endpoint

- Base URL: `http://127.0.0.1:4000` (local), `http://100.80.39.23:4000` (via Tailscale from other devices)
- Endpoint: `POST /v1/chat/completions` (OpenAI-compatible)
- Optional embeddings endpoint: `POST /v1/embeddings`
- Header: `Authorization: Bearer $LITELLM_API_KEY`

### 4.3 Authentication

- Environment variable: `LITELLM_API_KEY`
- Format: `<your-litellm-api-key>` (operator-set, local-only; not shared externally)
- Config file: `~/.litellm/config.yaml` maps model aliases to upstream providers and passes through the real API keys.

### 4.4 Models exposed via LiteLLM

The Forge pipeline expects these aliases (maintained for compatibility):
- `opus` → routes to Anthropic `claude-opus-4-7-*`
- `sonnet` → routes to Anthropic `claude-sonnet-4-6-20250929`
- `haiku` → routes to Anthropic `claude-haiku-4-5-20251001`
- `gpt-5` → routes to OpenAI `gpt-5.4`
- `gemini` → routes to Google `gemini-3.1-pro`

### 4.5 Role in pretel-os

For the MCP server's own LLM calls (Router classification, Reflection worker), pretel-os calls Anthropic directly, **not** through LiteLLM. Reason: direct calls give cleaner error handling, direct usage metrics via the Anthropic API's usage object, and one less hop on the critical path.

LiteLLM stays for:
- Forge pipeline (existing n8n workflow, unchanged)
- Future workflows that need multi-provider fallback
- Operator's ad-hoc testing via `curl`
- `request_second_opinion` MCP tool — operator-invoked cross-model validation. Uses LiteLLM alias `second_opinion_default` (configured in `~/.litellm/config.yaml` to route to a fixed secondary model, e.g. `gemini-2.5-flash` or `gpt-4.1-mini`). The alias is stable — changing the upstream model does not change the tool contract. Timeout: 15,000 ms (declared in `infra/timeouts.yaml`). Degraded mode: if LiteLLM fails after 3 retries with exponential backoff, the tool returns `{status: 'degraded', analysis: null, degraded_reason: 'litellm_unavailable'}` — no silent failure, no fallback to a direct provider call in Phase 1.

### 4.6 Health check

Nightly:

```bash
curl -sf http://127.0.0.1:4000/health | jq '.healthy_count'
```

Expected: a positive integer. Zero or failure → Telegram alert.

---

## 5. Supabase

### 5.1 Purpose

Phase 4+ target per ADR-007. Managed Postgres + pgvector + object storage. During Phase 1–3, only Supabase Storage is used (for encrypted backup uploads via rclone); the database layer stays on the Vivobook.

### 5.2 Endpoints (Phase 4+)

- Database: `postgresql://postgres:$SUPABASE_DB_PASSWORD@db.$SUPABASE_PROJECT_REF.supabase.co:5432/postgres`
- API (PostgREST auto-generated): `https://$SUPABASE_PROJECT_REF.supabase.co/rest/v1/`
- Storage: `https://$SUPABASE_PROJECT_REF.supabase.co/storage/v1/`
- Realtime: `wss://$SUPABASE_PROJECT_REF.supabase.co/realtime/v1/websocket`

### 5.3 Authentication

Two key classes:

| Key | Used for | Scope |
|-----|----------|-------|
| `anon` key | Client-side read via PostgREST (if ever exposed to browser) | Respects Row-Level Security |
| `service_role` key | Server-side writes from the MCP server | Bypasses RLS — treat as root |

Environment variables:
- `SUPABASE_URL` — project URL
- `SUPABASE_SERVICE_ROLE_KEY` — server-side writes
- `SUPABASE_ANON_KEY` — not used in Phase 1–3
- `SUPABASE_DB_PASSWORD` — direct Postgres connections

### 5.4 Quotas

Free tier (Phase 1–3):
- Database: 500 MB
- Storage: 1 GB
- Bandwidth: 5 GB/month egress
- Compute: shared
- Auth: 50,000 MAU (not used)

Pro tier (Phase 4+, $25/month when revenue-gated):
- Database: 8 GB
- Storage: 100 GB
- Bandwidth: 250 GB/month
- Daily backups
- 7-day point-in-time recovery

Projected consumption at Phase 1 (storage only, for backups): under 200 MB. Free tier sustains the operator for 2+ years per PF §3.1.

### 5.5 Retry and degraded mode

Phase 1–3: backup script fails gracefully. If Supabase Storage is unreachable during `rclone copy`, the encrypted dump stays local and is retried next night. Telegram alert if failures exceed 2 consecutive nights.

Phase 4+: per `CONSTITUTION §8.43`, Postgres unreachable triggers git-only degraded mode. MCP server continues serving L0–L3.

### 5.6 Health check

Phase 1–3:

```bash
rclone lsd supabase-storage:backups/pretel-os/ --max-depth 1 > /dev/null 2>&1
```

Phase 4+:

```python
conn = psycopg.connect(supabase_url, ..., timeout=5)
conn.execute("SELECT 1").fetchone()
```

---

## 6. Cloudflare

### 6.1 Purpose

Two separate uses:

1. **Cloudflare Tunnel** — public exposure of the local MCP server at `mcp.alfredopretelvargas.com` without opening firewall ports.
2. **DNS** — selective subdomain delegation for tunneled endpoints. IONOS remains authoritative for the apex `alfredopretelvargas.com`.

### 6.2 Tunnel

- Tool: `cloudflared` installed via apt
- Config: `/etc/cloudflared/config.yml`
- Credentials: `/etc/cloudflared/<tunnel-uuid>.json` (mode 0600, operator-only)

```yaml
# /etc/cloudflared/config.yml (committed as template; real UUID goes in systemd override)
tunnel: <UUID>
credentials-file: /etc/cloudflared/<UUID>.json

ingress:
  - hostname: mcp.alfredopretelvargas.com
    service: http://localhost:8787
    originRequest:
      connectTimeout: 30s
      noTLSVerify: true
  - hostname: n8n.alfredopretelvargas.com  # future
    service: http://localhost:5678
  - service: http_status:404
```

Runs as systemd service:

```
systemctl start cloudflared
systemctl enable cloudflared
```

### 6.3 DNS

For Option A (ADR-012, confirmed), a single CNAME in IONOS points each subdomain at `<UUID>.cfargotunnel.com`. Cloudflare only sees traffic for the delegated subdomains; the apex domain and website stay fully on IONOS.

Subdomains planned:
- `mcp.alfredopretelvargas.com` — MCP server (Phase 1)
- `n8n.alfredopretelvargas.com` — n8n UI for remote access (Phase 2)
- `forge.alfredopretelvargas.com` — Forge pipeline public webhook endpoint (Phase 3+)

### 6.4 Credentials

- Cloudflare account email + password → password manager
- Tunnel credentials file → local, `0600`, **not** in git
- No API token needed for manual tunnel management; add one only if automation is built.

### 6.5 Rate limits

Free Cloudflare plan includes the Tunnel service with no per-tunnel rate limit. Bandwidth is not metered. Free tier is sufficient for pretel-os's lifetime at current projections.

### 6.6 Degraded mode

If `cloudflared` process dies, the MCP server is unreachable from outside the LAN. Tailscale remains an alternate path for the operator personally, but not for Claude.ai.

Mitigation:
- systemd `Restart=on-failure` with `RestartSec=5s` on `cloudflared` unit
- Nightly health check: resolve `mcp.alfredopretelvargas.com` and curl `/health`
- On sustained failure: Telegram alert + operator fallback to Tailscale-only mode

### 6.7 Health check

Nightly:

```bash
curl -sf -o /dev/null -w "%{http_code}" https://mcp.alfredopretelvargas.com/health
# expect: 200
```

---

## 7. IONOS

### 7.1 Purpose

Authoritative DNS for `alfredopretelvargas.com`, hosting for the personal website, and webmail for `support@declassified.shop`.

### 7.2 Role in pretel-os

Minimal — only the CNAME records for tunneled subdomains (§6.3) are managed in IONOS for pretel-os purposes. The website and webmail remain the operator's personal assets and are out of scope for the pretel-os system itself.

### 7.3 Credentials

- IONOS account login → password manager
- 2FA enabled
- No programmatic access; DNS changes are manual via the IONOS dashboard. Acceptable given the low frequency (every new subdomain = one CNAME).

### 7.4 Health check

Nightly, via the Cloudflare health check in §6.7, which transitively verifies IONOS DNS resolution.

---

## 8. Telegram Bot API

### 8.1 Purpose

Operator interface for capture (voice notes, quick lessons), review (`/review_pending`, `/cross_poll_review`), and daily briefs (Morning Intelligence delivery). Replaces OpenClaw's Telegram layer using `python-telegram-bot` v21.

### 8.2 Endpoint

- Base URL: `https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/`
- All methods are HTTP `POST` or `GET` to `https://api.telegram.org/bot<token>/<method>`
- Webhook (optional, preferred for low-latency updates): pretel-os exposes `https://bot.alfredopretelvargas.com/telegram/webhook` via cloudflared, Telegram POSTs updates there.

### 8.3 Authentication

- Environment variable: `TELEGRAM_BOT_TOKEN`
- Format: `<numeric>:<alphanumeric>` (ex: `12345:ABC-def...`)
- Obtained from BotFather. One bot per role if desired; Phase 1 uses one bot: `@pretel_os_bot` (name TBD during setup).

### 8.4 Bot architecture

Two modes supported:

1. **Long polling** (default Phase 1) — the bot's Python process calls `getUpdates` in a loop. Simple, no public endpoint needed. Works behind Tailscale-only.
2. **Webhook** (Phase 2+ when public subdomain is stable) — Telegram pushes updates to pretel-os's cloudflared tunnel. Lower latency, lower overhead, better Vivobook battery health since the bot doesn't poll continuously.

Either way, `python-telegram-bot` handles both transparently.

**Command inventory (Phase 1):**

| Command | Purpose |
|---------|---------|
| `/start` | Register operator chat_id on first use |
| `/save <text>` | Create a lesson proposal; `save_lesson` MCP tool |
| `/review_pending` | Walk through pending lessons for approve/reject/edit/merge |
| `/cross_poll_review` | Review cross-pollination queue |
| `/morning_brief` | Force the morning intelligence run on demand |
| `/reflect` | Force the Reflection worker on the current session |
| `/idea <text>` | Capture a raw idea to `ideas` table |
| `/status` | Run health checks across all integrations, return a color-coded summary (🟢 all healthy, 🟡 one degraded, 🔴 one down). Triggers the same checks used by the nightly Dream Engine §1.1 principle 6. |
| `/help` | List commands |

The `/status` check is cheap (<5 sec) because it pings each integration in parallel and caches results for 60 seconds. On 🔴 status, the bot includes which integration failed and the last known error from the routing_logs or llm_calls tables.

### 8.5 Rate limits

- Global: 30 messages/second across all chats
- Per chat: 1 message/second
- Per group: 20 messages/minute

pretel-os will never approach these. One operator, occasional messages.

### 8.6 Pricing

Free. No costs.

### 8.7 Retry policy

`python-telegram-bot` retries automatically on HTTP 429 (rate limit) respecting the `retry-after` header. On network errors, the library uses exponential backoff within the bot process.

### 8.8 Degraded mode

If Telegram API is unreachable:
- Outbound messages (Morning Intelligence, alerts) queue to `pending_telegram_messages` (to-be-added table if the need materializes; initially just log to stderr and retry on next cycle).
- Inbound messages cannot be received. Operator uses Claude.ai as fallback interface.

### 8.9 Health check

Nightly:

```python
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
me = await bot.get_me()
assert me.username == "pretel_os_bot"  # replace with actual username once registered
```

---

## 9. n8n

### 9.1 Purpose

Self-hosted workflow engine. Runs the Forge pipeline (existing, 8-phase Product Intelligence workflow) and hosts future async workflows (Morning Intelligence delivery with voice synthesis, scheduled content drops, long-running consolidation tasks, key-rotation reminders per §1.3).

**Morning Intelligence voice synthesis.** The 06:00 voice note delivered via Telegram uses OpenAI TTS (`tts-1`, voice `onyx` or `echo` for Spanish male, operator to choose during Module 8 setup). Reasons: already have an OpenAI API key from embeddings; single-voice quality is sufficient for a daily brief; cost at current length (~3 min audio / ~500 output tokens) is approximately $0.015 per daily brief, or ~$0.45/month. Alternatives evaluated: ElevenLabs ($22/month subscription, overkill); Google Cloud TTS (needs a new API key and billing account); local Piper TTS (quality gap noticeable in Spanish). OpenAI TTS is the baseline; the voice model ID is set in the n8n workflow node and is easy to swap if OpenAI releases a better voice.

### 9.2 Endpoint

- Base URL (local): `http://127.0.0.1:5678`
- Base URL (Tailscale): `http://100.80.39.23:5678`
- Base URL (public, Phase 2+): `https://n8n.alfredopretelvargas.com` via cloudflared

### 9.3 Authentication

- n8n admin credentials: environment variables `N8N_BASIC_AUTH_USER` and `N8N_BASIC_AUTH_PASSWORD` in the Docker Compose file.
- API key for programmatic access: generated via n8n UI (Settings → API), stored as `N8N_API_KEY` in `.env.pretel_os`.
- Webhook URLs use n8n's per-workflow webhook signatures; optional HMAC validation when public.

### 9.4 Integration points

pretel-os's MCP server calls n8n in two ways:

1. **Webhook invocation** (async): MCP tool `run_forge_pipeline(product_url)` POSTs to `http://127.0.0.1:5678/webhook/forge-start`. n8n returns immediately with a run ID; results land in Google Drive and/or a callback.
2. **API query** (status): optional lookup of a run's status via `GET /api/v1/executions/{id}` with the API key.

### 9.5 Rate limits

None at the application level. At infra level, n8n runs in Docker with default resource limits. If a workflow fires heavy LLM calls, those hit LiteLLM's or Anthropic's limits upstream — not n8n.

### 9.6 Pricing

Self-hosted, free (infrastructure costs only — the Vivobook). Phase 4+ migration to n8n Cloud ($20/month starter) or a VPS ($8/month Hetzner self-hosted) is revenue-gated.

### 9.7 Retry policy

n8n workflows have built-in retry settings per node. The MCP server's webhook call uses the standard retry policy (§1.4, §2.7 pattern). On webhook failure, the MCP tool returns `{status: "queued_failed"}` and writes to `pending_forge_runs` (to be added if needed; initially just log).

### 9.8 Degraded mode

- n8n down → `run_forge_pipeline` and related MCP tools return `{status: "unavailable"}`. The Router and core retrieval remain fully operational.
- Morning Intelligence (runs inside n8n) fails silently with a logged incident; no cascading impact.

### 9.9 Health check

Nightly:

```bash
curl -sf http://127.0.0.1:5678/healthz
# expect: 200 OK
```

### 9.10 Backup

n8n workflows are exported via `curl` to the credentials API and saved into the `pretel-os-workflows` git repo. Scheduled weekly:

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "http://127.0.0.1:5678/api/v1/workflows?active=true" > \
     /home/operator/pretel-os-workflows/exports/workflows_$(date +%Y%m%d).json
cd /home/operator/pretel-os-workflows && git add . && git commit -m "Weekly n8n export" && git push
```

---

## 10. Tailscale

### 10.1 Purpose

Private mesh VPN. Gives the operator secure access to the Vivobook server from any personal device (Asus Rock, phone, tablet) without exposing ports to the public internet. Used for direct SSH, Postgres admin, and n8n UI access.

### 10.2 Endpoint

- Operator node (Vivobook): `100.80.39.23` (pretel-laptop)
- Control plane: `login.tailscale.com` (managed by Tailscale)
- Authentication: OAuth via operator's Google account (`prettelv1@gmail.com`)

### 10.3 Authentication

- No credentials in pretel-os config. Tailscale uses device-level auth via OAuth + device authorization.
- On server provisioning: `sudo tailscale up` prompts for device authorization via browser, then persists.

### 10.4 Role in pretel-os

- **Operator access** — SSH to the Vivobook from anywhere, including on the Asus Rock during travel.
- **Mobile Telegram bot long-polling fallback** — if the bot is offline publicly, the operator can still reach n8n UI via Tailscale and manually trigger workflows.
- **Not a pretel-os API surface** — pretel-os's MCP server does not depend on Tailscale for serving; it uses Cloudflare Tunnel for that.

### 10.5 Rate limits

None at the operator's scale. Free tier supports up to 100 devices and is free for personal use.

### 10.6 Pricing

Free (personal tier).

### 10.7 Health check

Weekly (less critical than daily):

```bash
tailscale status --json | jq '.Self.Online'
# expect: true
```

---

## 10.5 UptimeRobot (external monitoring)

### Purpose

External uptime monitoring per GPT audit FINDING-009 and Gemini-adv FINDING-005. The Vivobook's internal health checks cannot detect a hard shutdown (BIOS thermal cutoff, power outage, kernel panic) — the server goes dark silently. UptimeRobot pings from outside the tailnet and emails the operator when the endpoint is unreachable.

### Endpoint

- Account: free tier (50 monitors, 5-min interval)
- Monitor URL: `https://mcp.alfredopretelvargas.com/health`
- Expected response: HTTP 200 with JSON `{"status": "ok"}` (even when `db_healthy=false`, per lazy-init rule in `CONSTITUTION §8.43`)
- Alert channels: email to operator's primary address, Telegram webhook (optional, via n8n)

### Authentication

- UptimeRobot account credential in password manager.
- No programmatic access from pretel-os — monitor is configured once via UptimeRobot's web UI.

### Degraded mode

- **UptimeRobot down**: operator loses one layer of observability. Internal health checks continue. Operator tolerates silent outage risk until the service returns; no workaround needed (single-point monitor is acceptable since it's observing, not serving).

### Review cadence

- Monthly: operator reviews the uptime report as the `control_registry.uptime_review` evidence artifact (cadence 30 days per `DATA_MODEL §5.6`).
- Quarterly: re-verify the monitor URL still matches the current tunnel config.

---

## 11. Inbound integrations (clients reaching pretel-os)

### 11.1 Claude.ai (custom connector)

Configured in operator's Claude.ai settings → Connectors → Add custom MCP → URL: `https://mcp.alfredopretelvargas.com`. OAuth flow is not used.

**Phase 1 auth: Shared Secret Header — REQUIRED from day 1.** Cloudflare Tunnel is transport exposure, not authorization. Any exposed control plane with state-mutation tools (`save_lesson`, `create_project`, `update_project_state`) must authenticate every request. The MCP server fails closed: requests without the correct header return 401 before any routing logic runs.

- Environment variable: `MCP_SHARED_SECRET` (random 48-char string generated at provisioning time, stored in `/home/operator/.env.pretel_os` mode 0600, rotated every 180 days per §1.3)
- Header name: `X-Pretel-Auth`
- Server middleware: FastMCP middleware validates `request.headers['X-Pretel-Auth']` against `MCP_SHARED_SECRET` on every message. Constant-time comparison (`hmac.compare_digest`) to prevent timing attacks.
- Client configuration:
  - **Claude.ai connector**: paste the header in "Custom headers" option when adding the connector
  - **Claude Code**: add `"headers": {"X-Pretel-Auth": "..."}` to the `mcp.json` entry
  - **Claude mobile**: same connector config as Claude.ai web
- Rotation procedure: generate new value → update `.env.pretel_os` → `systemctl --user restart pretel-os-mcp` → update both client configurations. Old value stops working on restart — intentional, no graceful overlap.
- Failure mode: if a client sends the wrong or missing header, it receives 401 with body `{"error": "auth_failed"}`. The MCP server logs the attempt to `routing_logs` with `degraded_mode=false, degraded_reason='auth_failed'` for audit. Sustained 401s from the same origin trigger a Telegram alert.

The MCP server source code implements this from Module 3 onward. There is no Phase 1 without auth — that trade-off was explicitly rejected (see `LESSONS_LEARNED §9` LL-AI-001 pattern: public control plane requires defense-in-depth, not deferred auth).

### 11.2 Claude Code

Configured in `~/.config/claude/mcp.json` on each machine where Claude Code runs:

```json
{
  "mcpServers": {
    "pretel-os": {
      "type": "http",
      "url": "https://mcp.alfredopretelvargas.com"
    }
  }
}
```

Same tunnel, same server. No additional configuration on the pretel-os side.

### 11.3 Claude mobile

Configured identically to Claude.ai web through the app's Connectors settings. Works over cellular or Wi-Fi since the endpoint is publicly reachable via Cloudflare.

### 11.4 Future clients (Cursor, Antigravity, Codex, etc.)

Any MCP-compatible client can be added by pointing its MCP configuration at `https://mcp.alfredopretelvargas.com`. No pretel-os changes needed unless a client requires a specific transport or auth mechanism the MCP server has not exposed.

---

## 12. Integration-level risk register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Anthropic price increase | Medium | Medium | Monthly cost monitoring via `llm_calls` view; budget alert at 80% of cap |
| OpenAI embedding model deprecated | Low | High | `CONSTITUTION §2.5` amendment process + migration template in `DATA_MODEL §11.5` |
| Cloudflare Tunnel outage | Low | High | Tailscale fallback for operator; Claude.ai inaccessible until restored (no workaround) |
| Tier 1 rate limit hit | Low | Medium | Tier advancement is automatic on spend; manual request to Anthropic if needed |
| IONOS webmail breach | Low | Medium (not pretel-os but operator) | 2FA enabled; pretel-os credentials never sent to that inbox |
| Vivobook hardware failure | Medium | Critical | Daily encrypted backups + quarterly restore drill per `DATA_MODEL §10.2` |
| Telegram bot token leaked | Low | Medium | 180-day rotation; revoke via BotFather `/revoke` on suspicion |
| Supabase project deleted (Phase 4+) | Low | Critical | Multi-location backups; operator confirms all destructive actions |

---

## 13. Environment variables reference

Complete `.env.pretel_os` template (committed to repo as `.env.pretel_os.example`; real file in `/home/operator/` with mode 0600):

```bash
# Anthropic
ANTHROPIC_API_KEY=<your-anthropic-api-key>
ANTHROPIC_API_KEY_ROUTER=<your-anthropic-api-key>   # optional: separate key for classification
ANTHROPIC_API_KEY_REFLECTION=<your-anthropic-api-key>   # optional: separate key for reflection

# OpenAI
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# LiteLLM proxy (local)
LITELLM_URL=http://127.0.0.1:4000
LITELLM_API_KEY=<your-litellm-api-key>

# Postgres
DATABASE_URL=postgresql://pretel_os:XXXXXXXX@127.0.0.1:5432/pretel_os
DATABASE_POOL_SIZE=10

# n8n
N8N_URL=http://127.0.0.1:5678
N8N_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXX

# Telegram
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
TELEGRAM_OPERATOR_CHAT_ID=XXXXXXXXX

# Supabase (Phase 4+; empty in Phase 1-3)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_DB_PASSWORD=

# MCP server config
MCP_SERVER_PORT=8787
MCP_SERVER_HOST=0.0.0.0
MCP_LOG_LEVEL=INFO

# Timeouts (milliseconds)
TIMEOUT_HAIKU_MS=3000
TIMEOUT_OPUS_MS=60000
TIMEOUT_SONNET_MS=30000
TIMEOUT_OPENAI_EMBEDDING_MS=5000
TIMEOUT_N8N_WEBHOOK_MS=10000
TIMEOUT_SUPABASE_MS=5000
```

Loaded by systemd via:

```ini
# /etc/systemd/system/pretel-os-mcp.service
[Service]
EnvironmentFile=/home/operator/.env.pretel_os
ExecStart=/home/operator/pretel-os/venv/bin/python -m mcp_server
```
