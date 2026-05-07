# Module 10 — mcp_admin (admin console) — `spec.md`

**Status:** Draft (kickoff 2026-05-07)
**Module:** M10 / mcp_admin — fase 1 (MVP)
**Authority:** `CONSTITUTION.md §2.1` (MCP server is sole gateway), `§2.4` (git/DB boundary), `§8.43` (degraded mode), `decisions` row `5f1aa52a` (`personal:pretel-os` meta-project)
**Owner:** Alfredo Pretel Vargas
**Audience:** Operator + Claude implementer

---

## 1. Two-minute summary

A password-protected admin console for pretel-os hosted at `mcp-admin.alfredopretelvargas.com`. Built as a separate FastAPI application that renders HTML server-side (Jinja templates + HTMX for interactivity), authenticates via **Cloudflare Access** (zero-trust, no auth code in the app itself), and **calls the existing MCP tools internally for every mutation** instead of writing SQL directly. The console is read-heavy: 5 views to start (operator preferences, memory browser, Dream Engine runs, costs dashboard, pending review queue) plus 6 drill-down detail views (table rows, skill `.md`, project README + state, run JSONB pretty-print, preference inline-edit, lesson full card).

Stack: FastAPI + Jinja2 + HTMX + vanilla CSS (using the same HSL design tokens as `alfredo-ai-factory-guide` — teal `#1D9E75` / amber `#EF9F27` / purple `#7F77DD` — for visual coherence with the operator's brand). systemd `--user` unit. Cloudflare Tunnel adds a public hostname, Cloudflare Access enforces auth at the edge so the FastAPI process never sees unauthenticated requests.

**The one-line contract:**

> Admin never writes SQL DML. Every mutation routes through an existing MCP tool (`preference_set`, `save_lesson`, `archive_project`, `decision_record`, `resolve_cross_pollination`, etc.). If a needed mutation has no MCP tool, write the tool first.

This preserves the `CONSTITUTION §2.1` invariant that the MCP server is the only write surface — the admin is just another consumer, peer to Claude clients and the Telegram bot.

---

## 2. Why now (motivation)

Three operational pains that keep recurring:

1. **Tuning thresholds requires SQL or MCP-tool calls.** The operator wants to bump `archive.usage_window_days` from 500 to 700 and currently has to either run `psql` manually or remember to invoke `preference_set` from a session. A form input is the right surface.

2. **Reviewing memory has no UI.** Pending lessons in `pending_review`, cross-pollination proposals in `cross_pollination_queue`, dream_engine_runs telemetry — these all live in DB tables. The Telegram bot covers two of them via `/review_pending` and `/cross_poll_review`, but a screen-sized dashboard is much more useful for batch review than per-message Telegram cards.

3. **Costs are invisible.** `v_daily_cost_by_purpose` exists as a view; nobody looks at it because there's no surface. A simple chart on a recurring URL would close that loop.

The admin is the missing **operator surface** for the system. Every other surface (Claude.ai, Claude Code, Telegram, future external agents) is for *executing work*. The admin is for *operating the system itself*: tuning, reviewing, observing, governing.

---

## 3. Success criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| **SC1** | `https://mcp-admin.alfredopretelvargas.com` resolves and shows the Cloudflare Access login page; no traffic reaches the FastAPI backend without a valid `Cf-Access-Jwt-Assertion` header. | curl from outside Cloudflare Access returns the Access challenge HTML, never the app's HTML. journalctl shows zero unauthenticated requests reached the FastAPI process. |
| **SC2** | Logged-in operator sees the overview dashboard in < 2 s page load (95th percentile). | Browser devtools Network panel timing on first load + 5 reloads. |
| **SC3** | All 5 MVP views render without errors against live DB state and reflect changes within one page reload (no caching artifacts). | Manual smoke walk: preferences shows the 3 archive thresholds + their current values; memory browser lists lessons / decisions / best_practices counts matching `SELECT count(*)` from psql; dream_engine_runs shows last N rows; costs view shows non-zero `v_daily_cost_by_purpose` for at least one day; pending review queue shows whatever's in `cross_pollination_queue` and `lessons WHERE status='pending_review'`. |
| **SC4** | All write operations from the admin go through an MCP tool (no direct INSERT/UPDATE/DELETE in admin code). | Code review: grep for `INSERT`, `UPDATE`, `DELETE` in `src/mcp_admin/` returns zero hits in non-comment lines (raw SELECT for read views is allowed). Mutation handlers all import from `mcp_server.tools`. |
| **SC5** | Six drill-down levels work end-to-end: click a table row → row detail; click a skill name → rendered `.md` content; click a project → README + `project_state`; click a `dream_engine_runs` row → expanded `jobs_run` JSONB pretty-printed; click a preference → inline form to set new value; click a lesson → full card with title, content, next_time, tags, status, embedding-info. | Manual walk through each. |
| **SC6** | After 7 days in production: Cloudflare Access logs show only the operator's email (no unauthorized attempts succeeded); FastAPI journalctl logs zero 5xx errors; no manual interventions required to keep the service running. | Cloudflare Zero Trust logs export + `journalctl --user -u pretel-os-admin -p err`. |
| **SC7** | Visual coherent with `alfredo-ai-factory-guide`: teal `#1D9E75` primary, amber `#EF9F27` secondary, purple `#7F77DD` accent, Inter font, JetBrains Mono for code/data, default dark mode, border-radius `0.75rem`. | Side-by-side screenshot vs the operator's public site; tokens identical at the CSS-variable level. |

---

## 4. Out of scope (for fase 1)

- **Direct SQL ad-hoc query view.** Tempting for diagnostics but bypasses the MCP-tool invariant. Defer; if needed, add a strictly read-only psql-equivalent in fase 2 with operator-only confirmations.
- **Light mode toggle.** Default dark only in V1; light mode is a styling pass for fase 2.
- **Mobile-responsive layout.** V1 desktop-first. The mock degrades gracefully via the `@media (max-width: ...)` rules but mobile is not a tested surface.
- **Real-time updates (WebSocket / SSE).** All views are refresh-driven in V1; "live" is a Phase 2 concern, gated by a real need (e.g., watching a Dream Engine run mid-execution).
- **Multi-user support.** Single operator only; Cloudflare Access policy enforces single-email allowlist.
- **Audit log of admin actions.** Every mutation goes through MCP tools which already log via `usage_logs` — that's our audit trail. No separate admin-side log.
- **Editor for skill `.md` files.** The drill-down for skills is *render only*. Editing happens via git + `register_skill` re-call. Inline editing is fase 2 if a real need emerges.
- **Bulk operations** (e.g., "archive 50 lessons at once"). Phase 2.

---

## 5. Non-functional requirements

| Requirement | Target |
|-------------|--------|
| **Auth** | Cloudflare Access at the edge. The FastAPI process never sees unauthenticated requests. Optional defense-in-depth: validate the JWT against Cloudflare's JWKs in middleware (Phase B nice-to-have). |
| **Performance** | < 2 s page load (cold), < 500 ms (warm cache). Most views run a handful of SQL queries; no N+1. |
| **Cost per month** | $0. Cloudflare Access free tier (50 users), Cloudflare Tunnel, FastAPI on Vivobook — all $0. |
| **Database connection** | Reuses the existing `psycopg` async pool pattern from `src/mcp_server/db.py`. No new pool — share `mcp_server.db.get_pool()` at runtime. |
| **MCP tool reuse** | Mutations import from `mcp_server.tools.*` directly. The admin runs in the same Python interpreter family — calling a tool is a function call, not an HTTP MCP request. |
| **Style** | CSS variables identical to `alfredo-ai-factory-guide`'s `--primary/--secondary/--accent/--background/...`. Inter + JetBrains Mono via Google Fonts CDN. Vanilla CSS — no framework. |
| **Code budget** | Worker fits in ~600 lines Python (FastAPI app + handlers) + ~400 lines templates + ~200 lines CSS. |
| **Observability** | Every request logs via standard FastAPI middleware to journald. Cloudflare Access logs all auth events. No admin-side telemetry table; rely on `usage_logs` from MCP tool invocations. |

---

## 6. Open questions

These get answered at phase kickoff, not now:

| ID | Question | Phase to resolve |
|----|----------|------------------|
| Q1 | JWT validation in middleware (defense in depth) — implement now or defer? | Phase A |
| Q2 | Markdown rendering library — `markdown-it-py`, `mistune`, or `python-markdown`? Need GFM tables + code highlighting. | Phase C (drill-downs) |
| Q3 | Pagination strategy — server-side cursor vs offset/limit? At 100+ lessons offset is fine; at 10k+ it's not. | Phase B |
| Q4 | Pending review approve/reject — confirmation modal or one-click + undo window? | Phase B |
| Q5 | Costs dashboard — server-rendered SVG charts (vega-lite via JS) or just numeric tables for V1? | Phase B |
| Q6 | Cloudflare Access app name + policy — does the operator want to be the only allowed email or also a backup admin email? | Phase D (deploy time) |
| Q7 | systemd Type=simple (long-running uvicorn) vs Type=notify (newer) — convention check against existing units. | Phase A |

---

## 7. Risks and mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cloudflare Access bypass via direct Tunnel access | Low | High — exposes whole DB read surface to the internet | Validate JWT in middleware (Q1); restrict the FastAPI app to listen only on `127.0.0.1` so the only path to it is via Tunnel. |
| Mutation bypasses MCP tool and hits SQL directly | Medium during development | Medium — breaks invariant § 2.1 | Code review for `INSERT/UPDATE/DELETE` strings in `src/mcp_admin/` (SC4 verification step). Pre-commit grep. |
| Admin shows stale data because of layer cache (M4 cache invalidation triggers fire on writes) | Low | Low — refresh fixes it | Most views read directly from DB, not from cache. The few cached layers (L0, L1, L2) are read by the Router for context assembly, not by the admin. |
| FastAPI process crashes silently and operator doesn't notice | Medium | Low — service is operator-discretionary, not load-bearing | systemd `Restart=on-failure`. Cloudflare uptime check (free) ping every 5 min. |
| Style drift from `alfredo-ai-factory-guide` over time | Medium | Low | Single source of truth: copy the HSL CSS variables once into a `tokens.css`. If the public site re-themes, propagate in one edit. |
| Operator forgets the email PIN flow and gets locked out | Low | Medium | Cloudflare Access supports add-on Google login as fallback identity provider. |

---

## 8. Definition of done

Module 10 fase 1 is complete when:

1. All 7 success criteria above pass (SC1–SC7).
2. `runbooks/module_10_mcp_admin.md` shipped (operations runbook: how to add an Access-allowed user, how to update a CSS token, how to add a new view, how to recover from systemd failure).
3. Tag `module-10-complete` created on the closing commit (operator-driven push).
4. `tasks.md` (root) row marked `[x]`.

---

## 9. Cross-references

- `specs/mcp_admin/plan.md` — phased architecture and Q&A.
- `specs/mcp_admin/tasks.md` — atomic checkboxes per phase.
- ADR-029 (`decisions` row a39bc9b9) — constitutional amendment v5.2 (this module's existence does not require an amendment but its mutations must not violate §2.1).
- `personal:pretel-os` (`projects` row 5f1aa52a) — meta-project home for any decisions made during this module.
- `infra/systemd/pretel-os-readme.service` and `pretel-os-dream-engine.service` — existing user-unit patterns to mirror.
- `src/mcp_server/db.py` — async connection pool to reuse.
- `src/mcp_server/tools/` — MCP tools to import for mutations.
- External: `https://github.com/pr3t3l/alfredo-ai-factory-guide` — visual brand reference (teal/amber/purple HSL tokens, Inter + JetBrains Mono).
- External: Cloudflare Zero Trust dashboard — where Access policies live.
