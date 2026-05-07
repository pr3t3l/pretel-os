# Module 10 — mcp_admin — `plan.md`

**Status:** Draft (kickoff 2026-05-07)
**Authority:** companion to `specs/mcp_admin/spec.md`
**Audience:** Claude implementer (per-phase brief)

---

## 1. Architecture overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Browser (operator at mcp-admin.alfredopretelvargas.com)                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS
                                 ▼
                ┌────────────────────────────────────┐
                │ Cloudflare edge                    │
                │  ▶ Access challenge if not auth    │
                │  ▶ One-time PIN to email           │
                │  ▶ JWT cookie (24h)                │
                └────────────────┬───────────────────┘
                                 │ HTTPS via Tunnel
                                 │ + Cf-Access-Jwt-Assertion header
                                 ▼
                ┌────────────────────────────────────┐
                │ Vivobook (localhost only)          │
                │                                    │
                │  cloudflared (existing)            │
                │       │                            │
                │       ▼                            │
                │  uvicorn @ 127.0.0.1:PORT          │
                │       │                            │
                │       ▼                            │
                │  FastAPI (mcp_admin)               │
                │   ├─ middleware: read user email   │
                │   │   from Cf-Access-Authenticated-│
                │   │   User-Email header            │
                │   ├─ GET routes: SELECT → render   │
                │   │   Jinja template               │
                │   └─ POST routes: import + call    │
                │       MCP tool from                │
                │       mcp_server.tools.*           │
                │                                    │
                │  PostgreSQL @ localhost:5432       │
                │   (shared with MCP server, same    │
                │   psycopg pool)                    │
                └────────────────────────────────────┘
```

Cloudflare Access sits at the edge. The FastAPI app only ever sees authenticated requests (assuming Q1's defense-in-depth JWT validation is on; without it, anyone with direct Tunnel-origin access could bypass — mitigated by binding uvicorn to `127.0.0.1`). MCP tools are imported, not called over HTTP, so mutations are direct Python calls into the same codebase.

The admin is **not** an MCP client. It does not speak the MCP protocol. It is a peer process that shares the same Python imports + database.

---

## 2. Phases

### Phase A — Scaffolding + auth + first view

**Scope:**
- `src/mcp_admin/__init__.py` (package marker).
- `src/mcp_admin/main.py` (FastAPI app factory, root mount, lifespan that reuses `mcp_server.db.get_pool()`).
- `src/mcp_admin/middleware.py` — read `Cf-Access-Authenticated-User-Email` header into `request.state.user_email`. Optional: validate JWT against Cloudflare JWKs (Q1 decision).
- `src/mcp_admin/templates/base.html` — sidebar + topbar + main content slot, brand tokens loaded from `tokens.css`.
- `src/mcp_admin/templates/preferences.html` — first concrete view.
- `src/mcp_admin/handlers/preferences.py` — `GET /preferences` reads `operator_preferences`; `POST /preferences/{key}` calls `mcp_server.tools.preferences.preference_set` directly.
- `src/mcp_admin/static/tokens.css` — copied from `alfredo-ai-factory-guide/src/index.css` (HSL variables only).
- `src/mcp_admin/static/admin.css` — layout + components from the mock, parameterized by tokens.css.
- `infra/systemd/pretel-os-admin.service` — Type=simple, ExecStart=uvicorn, EnvironmentFile=$HOME/.env.pretel_os.
- 1 unit test for the preferences handler.
- 1 slow integration test that hits `/preferences` against pretel_os_test.

**Exit gate:**
- `python -m mcp_admin.main` runs uvicorn on a configured port.
- Hitting `http://127.0.0.1:PORT/preferences` returns HTML showing the 3 archive thresholds.
- POST to `/preferences/archive.usage_window_days` with body `{value: "700"}` updates the row in `pretel_os_test` (verified via psql).
- `mypy src/mcp_admin/` clean.
- 18 dream_engine tests + 6 admin unit + 1 admin slow = no regression in the 277-test baseline.

**Q&A to answer in this phase:** Q1, Q7.

**Cost:** $0. No LLM, no external API.

---

### Phase B — Remaining 4 MVP views

**Scope (4 view modules):**

1. **`/memory`** — combined browser for lessons + decisions + best_practices.
   - Tabs at top: Lessons / Decisions / Best Practices
   - Per tab: filter by bucket, tag, status; search box (semantic via existing `search_lessons` / `decision_search` / `best_practice_search` MCP tools); paginated list.
   - Each row clickable → drill-down (Phase C).
2. **`/dream-engine`** — last 14 days of `dream_engine_runs`.
   - Table with started_at, wall_ms, status, jobs_run summary.
   - "Trigger manual run" button → `systemctl --user start pretel-os-dream-engine.service` via subprocess (Q4 confirmation needed) OR direct invocation.
   - Failed/partial rows shown red, success green.
3. **`/costs`** — daily cost dashboard.
   - Last 30 days from `v_daily_cost_by_purpose`.
   - Numeric table for V1 (Q5 decides chart treatment).
   - Total spend MTD + projection.
4. **`/pending`** — combined queue for `lessons WHERE status='pending_review'` + `cross_pollination_queue WHERE status='pending'`.
   - Approve/reject buttons (call `approve_lesson` / `reject_lesson` / `resolve_cross_pollination` MCP tools).
   - Confirmation per click for now (Q4 decision).

**Exit gate:**
- All 4 views render against live DB without 5xx.
- All mutations route through MCP tools (verified by grep).
- Browser walk through each view shows real data.
- mypy clean.

**Q&A to answer:** Q3, Q4, Q5.

**Cost:** $0.

---

### Phase C — Drill-downs

**Scope (6 detail views):**

1. **Table row detail** (`/db/<table>/<id>`) — pretty-print the full row, each column with type + value; foreign keys are clickable links.
2. **Skill render** (`/skills/<name>`) — fetch via `load_skill` MCP tool, render markdown to HTML (Q2 decides library), syntax-highlight code blocks. Sidebar shows metadata (utility_score, trigger_keywords, applicable_buckets, embedding_dim).
3. **Project detail** (`/projects/<bucket>/<slug>`) — fetch via `get_project`, render README markdown, show project_state KV in a table, list recent decisions + tasks scoped to the project.
4. **Dream Engine run detail** (`/dream-engine/<run_id>`) — pretty-print `jobs_run` JSONB and `failures` JSONB; link to journalctl excerpt for the matching time window.
5. **Preference inline edit** — already on `/preferences` page, but each row has an inline form: `value` becomes editable, "Set" button calls `preference_set`. Show old value + new value side by side after submit.
6. **Lesson full card** (`/memory/lessons/<id>`) — full title, content, next_time, tags, applicable_buckets, status, source, evidence JSONB, embedding presence + dim, created_at, reviewed_at. Approve / reject / archive actions.

**Exit gate:**
- All 6 drill-downs reachable from their parent views.
- Markdown rendering produces correct HTML for at least 2 sample skills + 2 sample projects.
- Interactive UX: HTMX swaps in updated content without full page reload for inline edits.

**Q&A to answer:** Q2.

**Cost:** $0.

---

### Phase D — Production deploy

**Scope:**
- DNS A record (or CNAME via existing Tunnel) for `mcp-admin.alfredopretelvargas.com`.
- Cloudflare Tunnel: add public hostname → service `http://localhost:PORT`.
- Cloudflare Access: create application + policy (operator email allowlist).
- Install + enable systemd unit.
- First production access from operator's browser: PIN flow, login, see dashboard.
- Verify `journalctl --user -u pretel-os-admin -p err` shows no errors after one operational session.

**Exit gate:**
- `https://mcp-admin.alfredopretelvargas.com` resolves and shows Cloudflare Access challenge to anyone not in the policy.
- Operator can log in via PIN and see all 5 views.
- All drill-downs work end-to-end against production data.
- SC1–SC7 verified.

**Q&A to answer:** Q6.

**Cost:** $0 incremental (Cloudflare Access free tier).

---

### Phase E — Module exit

**Scope:**
- `runbooks/module_10_mcp_admin.md` — operations runbook:
  - How to add a new Access-allowed email.
  - How to update a CSS token (re-sync from public site).
  - How to add a new view (file pattern + handler + template + nav entry).
  - How to recover from systemd failure.
  - 3 audit queries (Cloudflare Access logs, FastAPI access logs, MCP tool usage logs).
- `tasks.md` (root) — Module 10 row marked complete.
- `SESSION_RESTORE.md §13` — last-session snapshot updated.
- Tag `module-10-complete` on the closing commit (operator authorizes push).

**Exit gate:**
- Runbook in repo.
- Tag created locally; operator chooses when to push.
- 7 days of operator usage with no `journalctl -p err` entries.

---

## 3. Test strategy

| Test type | Location | What it covers | Cost |
|-----------|----------|----------------|------|
| Unit | `tests/mcp_admin/test_handlers.py` | Each handler function in isolation, DB and MCP tools mocked. Verifies template selection, request parsing, header extraction. | $0, fast |
| Slow integration | `tests/mcp_admin/test_e2e.py` (`@pytest.mark.slow`) | Full FastAPI app via `httpx.AsyncClient` against `pretel_os_test`. Verifies each view renders without error and reflects seeded fixtures. | $0, ~1 s per test |
| Manual smoke | Phase D | Production-data walk through every view + drill-down. | $0 |
| Production observation | Phase D | 7-day window, journald errors should be zero. | $0 |

**No browser-driver tests** (Playwright/Selenium) in V1. The visual coherence is verified by side-by-side screenshot, not automated. If the admin grows to >10 views or interactive behaviors, revisit.

---

## 4. Cost forecast

| Item | Forecast |
|------|----------|
| Module build (A–E) | $0. Pure Python + HTML + CSS. |
| Steady-state production | $0/month. Cloudflare Access free tier. |
| Future fase 2 (real-time, ad-hoc SQL, light mode, multi-user) | TBD when chartered. |

---

## 5. Dependencies and load-bearing assumptions

**Hard dependencies (must be true at Phase A start):**
- `mcp_server.db.get_pool()` is importable and returns a working pool against `pretel_os` (or test DB when patched).
- `mcp_server.tools.preferences.preference_set` exists and accepts the canonical signature.
- Cloudflare account with Tunnel already wired and Access available (free tier active).
- DNS for `alfredopretelvargas.com` is managed by Cloudflare (so subdomain creation is via the same dashboard).
- `~/.venvs/pretel-os/bin/python` has `fastapi`, `uvicorn`, `jinja2`, `httpx` installable. (`pip install fastapi uvicorn jinja2 httpx markdown-it-py` — all pure Python, no native deps.)

**Load-bearing assumptions:**
- Cloudflare Access JWT validation logic is correct and the JWKs endpoint is stable. (Mitigated by Q1 defense-in-depth.)
- The MCP tool functions accept being called from outside the MCP server context. (Verified by reading the imports in `src/mcp_server/tools/preferences.py`: tools depend only on `db_mod` which we share.)
- The HSL tokens copied from the public site are stable enough that we don't have to re-sync weekly. (Mitigated by `tokens.css` as single source on the admin side; manual re-sync when public site re-themes.)

---

## 6. Tuning playbook (post-deployment)

| Symptom | Knob | How |
|---------|------|-----|
| Slow page load | DB query optimization | Profile via FastAPI middleware logging, add indexes, paginate |
| Broken visual after public-site re-theme | `static/tokens.css` | Re-copy HSL vars from `alfredo-ai-factory-guide/src/index.css` |
| Cloudflare Access timing out user | Session duration | Cloudflare dashboard → Access → app → Session duration → bump to 168h (7d) |
| Unauthorized access attempt | Access policy | Cloudflare dashboard → Access → app → Policies → audit log |
| Service flapping | journald + systemd Restart= | Check `journalctl --user -u pretel-os-admin` for crash cause; adjust `Restart=on-failure` settings |
| New mutation needed but no MCP tool exists | Add the MCP tool first | Implement in `src/mcp_server/tools/`, register in `app.tool()`, call from admin |

---

## 7. Out-of-scope handling (deferred features, future phases)

| Deferred feature | Re-charter trigger |
|------------------|-------------------|
| Light mode toggle | Operator preference + ~50 lines of CSS variants |
| Real-time live updates (Dream Engine running, ongoing routing_logs) | Genuine need to watch a long-running operation, not just for fun |
| Skill `.md` editor (in-browser) | Operator finds git-edit + register_skill round-trip too painful for >5 edits/week |
| Multi-user / per-user views | A second operator joins (currently N=1 for life) |
| Direct SQL ad-hoc query view | Diagnostics can't be served by drill-downs alone, AND a strict read-only safe path is designed (`SELECT` only with timeout limits) |
| Bulk operations | A queue grows past 50 items the operator wants to action en masse |
| Mobile-responsive | Operator finds themselves wanting to triage from phone (currently Telegram covers that surface) |
| Charts / visualizations on costs / utility | Numeric tables stop being enough to spot trends |

---

## 8. References

- `specs/mcp_admin/spec.md` — what we're building.
- `specs/mcp_admin/tasks.md` — atomic checkboxes.
- `runbooks/sdd_module_kickoff.md` — Trinity rule.
- `infra/systemd/pretel-os-readme.service` — sibling user-unit pattern.
- `infra/systemd/pretel-os-dream-engine.service` — sibling Type=oneshot pattern (admin uses Type=simple instead).
- `src/awareness/readme_renderer.py` — sibling sync-psycopg pattern (not directly applicable but useful reference for connection management).
- `src/mcp_server/db.py` — pool factory we reuse.
- `https://developers.cloudflare.com/cloudflare-one/` — Cloudflare Zero Trust docs.
- `https://github.com/pr3t3l/alfredo-ai-factory-guide` — visual brand source.
