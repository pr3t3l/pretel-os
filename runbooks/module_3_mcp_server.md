# Module 3 Runbook: MCP Server

## Date: 2026-04-27

## Scope

FastMCP-based MCP server (`pretel-os` v3.2.4) exposed to Claude.ai via Cloudflare Tunnel. Seven tools wired to the Postgres data layer from Module 2. Streamable HTTP transport on `127.0.0.1:8787/mcp`. Public hostname: `mcp.alfredopretelvargas.com`.

## Service control

User-scoped systemd unit:

```bash
systemctl --user start pretel-os-mcp
systemctl --user stop pretel-os-mcp
systemctl --user restart pretel-os-mcp
systemctl --user status pretel-os-mcp
systemctl --user is-active pretel-os-mcp
systemctl --user enable pretel-os-mcp     # already done
```

Unit file: `/home/pretel/.config/systemd/user/pretel-os-mcp.service`. Environment loaded from `/home/pretel/.env.pretel_os` (`DATABASE_URL`, `MCP_SHARED_SECRET`, `OPENAI_API_KEY`). Runs `/home/pretel/.venvs/pretel-os/bin/python -m mcp_server.main`. `Restart=on-failure`, 5s backoff.

`loginctl enable-linger pretel` is set, so the unit survives logout / reboot.

## Health check

Public, unauthenticated route:

```bash
curl -s http://127.0.0.1:8787/health
# {"status":"ok","db_healthy":true}

curl -s https://mcp.alfredopretelvargas.com/health
```

`db_healthy` is updated by an in-process poller (`db.start_background_health_check`). When it flips to false, mutating tools return `{"status":"degraded", ...}` and writes are journaled to `~/pretel-os-data/fallback-journal/` per CONSTITUTION §8.43.

## Logs

```bash
# Live tail
journalctl --user -u pretel-os-mcp -f

# Since restart
journalctl --user -u pretel-os-mcp -b --no-pager

# Last 50 lines
journalctl --user -u pretel-os-mcp -n 50 --no-pager

# Around a known incident (UTC time on the system)
journalctl --user -u pretel-os-mcp --since "2026-04-27 13:40:00" --until "2026-04-27 13:45:00"
```

Useful greps:
- `find_duplicate_lesson failed` — duplicate-detection signature mismatch (fixed 2026-04-27).
- `embedding call failed` — OpenAI key/network problem; full traceback present after 9e2b8dd.
- `db_healthy transition` — DB pool flipping up/down.
- `auth_failed` — request sent `X-Pretel-Auth` but secret didn't match.

## Tools

Registered in `src/mcp_server/main.py:64-70`. All return JSON-serializable dicts. Mutating tools obey degraded mode.

| Name | File | Signature |
|---|---|---|
| `get_context` | `tools/context.py` | `(message: str, session_id: Optional[str] = None) -> dict` |
| `save_lesson` | `tools/lessons.py` | `(title, content, bucket, tags, category, severity?, applicable_buckets?, related_tools?, next_time?) -> dict` |
| `search_lessons` | `tools/lessons.py` | `(query: str, bucket?, tags?, limit=5, include_archived=False) -> dict` |
| `register_skill` | `tools/catalog.py` | `(name, description_short, description_full, applicable_buckets, skill_file_path) -> dict` |
| `register_tool` | `tools/catalog.py` | `(name, description_short, description_full, applicable_buckets, mcp_tool_name?) -> dict` |
| `load_skill` | `tools/catalog.py` | `(name: str) -> dict` |
| `tool_search` | `tools/catalog.py` | `(query: str, limit: int = 10) -> dict` |

`save_lesson` auto-promotes to `status='active'` only when all four CONSTITUTION §5.2 rule 13 conditions hold (title + content + technical reference + `next_time`) AND duplicate detection actually ran cleanly. On a missing embedding or any dup-detection error, the row lands as `pending_review` (fail-closed; see commit `9e2b8dd`).

### End-to-end smoke test via the public endpoint

Streamable HTTP requires `initialize` → `notifications/initialized` → tool calls, all sharing the `Mcp-Session-Id` returned by `initialize`.

```bash
# 1. Initialize and capture the session id from response headers
curl -sS -D /tmp/h.txt https://mcp.alfredopretelvargas.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":0,"params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"smoke","version":"0.1"}}}' \
  -o /dev/null
SID=$(grep -i '^mcp-session-id:' /tmp/h.txt | awk '{print $2}' | tr -d '\r\n')

# 2. Initialized notification (HTTP 202)
curl -sS -o /dev/null -w "%{http_code}\n" https://mcp.alfredopretelvargas.com/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# 3. Call a tool
curl -sS https://mcp.alfredopretelvargas.com/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"search_lessons","arguments":{"query":"cloudflare","limit":3}}}'
```

## Auth

`PretelAuthMiddleware` (`src/mcp_server/auth.py`) is in **temporary OPEN MODE**:

- `/health` is unauthenticated (always was).
- All other paths: a missing `X-Pretel-Auth` header **passes through**. A *present* header still must match `MCP_SHARED_SECRET` exactly (`hmac.compare_digest`), otherwise 401 with an audit row written to `routing_logs`.

This was committed as `3617623` to make Claude.ai's custom-connector handshake work — Claude.ai does not currently send the shared-secret header. **TODO**: replace with OAuth per Claude.ai connector requirements; revert the open-mode code path once OAuth is wired.

While in this mode, the public hostname `mcp.alfredopretelvargas.com` is effectively open to anyone who knows the URL. Mitigations: tunnel-side Cloudflare Access policy, plus the lack of public listing.

## Cloudflare Tunnel

Tunnel runs as a **system-level** service (not user-scoped):

```bash
sudo systemctl status cloudflared
sudo systemctl restart cloudflared
sudo journalctl -u cloudflared -f

# Tunnel id is embedded in the token in /etc/systemd/system/cloudflared.service
# (current tunnel id: 14eb11b4-e9cc-4207-8f8b-57e10cc95ec7)
```

Verify the public path round-trips to the local server:

```bash
curl -s https://mcp.alfredopretelvargas.com/health    # → {"status":"ok","db_healthy":true}
curl -sI https://mcp.alfredopretelvargas.com/mcp      # → HTTP/2 (200 or 406 without Accept: text/event-stream)
```

If `/health` works but `/mcp` doesn't, restart `pretel-os-mcp` (the tunnel is fine; the app process is wedged). If `/health` itself fails, restart `cloudflared`.

## Database

Touched objects (already migrated in Module 2):

- `lessons` — written by `save_lesson`, read by `search_lessons` (sequential scan, no HNSW).
- `tools_catalog` — written by `register_skill` / `register_tool`, read by `load_skill` / `tool_search`.
- `routing_logs` — written by `get_context` and by auth failures.
- `usage_logs` — written by every successful tool call (`log_usage` in `tools/_common.py`).
- `find_duplicate_lesson(text, vector(3072), text, real)` — called by `save_lesson`.

Inspect:

```bash
PGPASSWORD=pretel_os_temp_2026 psql -U pretel_os -h 127.0.0.1 -d pretel_os \
  -c "SELECT id, title, status, bucket, vector_dims(embedding) AS dims FROM lessons ORDER BY created_at DESC LIMIT 10;"
```

## Deviations from spec

1. **Auth is temporarily open.** See above. Spec calls for shared-secret on every request; current code lets header-less requests through to support Claude.ai. Tracked as TODO in `auth.py:13` and `auth.py:49`.
2. **HNSW indexing on `lessons.embedding` deferred.** Same root cause as Module 2 §1: pgvector 0.6.0 cannot HNSW-index 3072-dim vectors. `search_lessons` is a sequential scan (acceptable below ~10k vectors; `DATA_MODEL §8`). Re-enable when pgvector ≥0.7 is available or an IVFFlat index is acceptable.
3. **`embedding_queued` flag is misnamed.** `save_lesson` returns `embedding_queued: true` when the embedding could not be fetched, but no actual `pending_embeddings` queue row is inserted by this code path. The flag tells the caller whether retry is needed; a real queue worker is future work.

## Bugs fixed during the module

| Commit | Issue | Fix |
|---|---|---|
| `3206d90` | `search_lessons` SQL crashed: `malformed vector literal: "{active}"` | Bind list now matches placeholder order: SELECT vec, WHERE status, [bucket], [tags], ORDER BY vec, LIMIT. |
| `3206d90` | `embed()` failures only logged the exception message, no traceback | `log.warning` → `log.exception`. |
| `9e2b8dd` | `find_duplicate_lesson` silently failed every save: `function ... (unknown, vector, unknown, double precision) does not exist` | Added explicit `::text / ::vector(3072) / ::real` casts. |
| `9e2b8dd` | `_auto_approval_eligible` was hardcoded `duplicate_hit=False`, so a save with a failed dup-check could still auto-promote | Track `dup_check_clean` and pass `duplicate_hit=not dup_check_clean`. Fail-closed. |

## Current state

- Service: `pretel-os-mcp.service` active, transport `http://127.0.0.1:8787/mcp`.
- Public: `https://mcp.alfredopretelvargas.com` via Cloudflare Tunnel `14eb11b4-e9cc-4207-8f8b-57e10cc95ec7`.
- Tools: 7 registered; all smoke-tested against the public endpoint.
- DB: `db_healthy: true`; `lessons` round-trips with embedding + duplicate detection.
- Connected client: Claude.ai custom connector (open-auth handshake).

## Pending operator actions

1. Implement OAuth per Claude.ai connector requirements; remove the open-mode branch in `auth.py`.
2. Build the `pending_embeddings` retry worker (consume the `embedding_queued: true` signal from `save_lesson`).
3. Re-enable HNSW or IVFFlat once vector volume warrants it (carried from Module 2).
4. Rotate `pretel_os` DB password away from `pretel_os_temp_2026` (carried from Module 2).
