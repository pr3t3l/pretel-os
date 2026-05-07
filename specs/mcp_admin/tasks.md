# Module 10 — mcp_admin — `tasks.md`

**Status:** Draft (kickoff 2026-05-07)
**Convention:** Atomic — one checkbox per file / handler / migration / test. < 30 minutes per item.
**Phases match `specs/mcp_admin/plan.md` §2.**

---

## Phase A — Scaffolding + auth + first view (preferences)

- [x] **M10.A.1** — Decide Q1 (JWT validation in middleware now or defer). Document in `phase_a_close.md`.
- [x] **M10.A.2** — Decide Q7 (systemd Type=simple vs notify). Document in `phase_a_close.md`.
- [x] **M10.A.3** — Verify venv has FastAPI + uvicorn + jinja2 + httpx. If missing, `pip install` and document in `phase_a_close.md`.
- [x] **M10.A.4** — Create `src/mcp_admin/__init__.py` (empty package marker with one-line docstring).
- [x] **M10.A.5** — Write `src/mcp_admin/static/tokens.css` — copy HSL variables from `alfredo-ai-factory-guide/src/index.css` (`:root` and `.dark` blocks). One-line comment at top noting the source URL + commit SHA at copy time.
- [x] **M10.A.6** — Write `src/mcp_admin/static/admin.css` — layout + components adapted from the mock, using `var(--primary)` etc. from tokens.css.
- [x] **M10.A.7** — Write `src/mcp_admin/templates/base.html` — sidebar + topbar + main slot, Inter + JetBrains Mono fonts, dark-mode body class.
- [x] **M10.A.8** — Write `src/mcp_admin/main.py` — FastAPI app factory, mounts static + templates, lifespan that opens DB pool, lists 5 view nav entries.
- [x] **M10.A.9** — Write `src/mcp_admin/middleware.py` — `attach_user` reads `Cf-Access-Authenticated-User-Email`. Conditional JWT validation per Q1 outcome.
- [x] **M10.A.10** — Write `src/mcp_admin/handlers/preferences.py` — `GET /preferences` (reads via psycopg), `POST /preferences/{category}/{key}` (calls `mcp_server.tools.preferences.preference_set`).
- [x] **M10.A.11** — Write `src/mcp_admin/templates/preferences.html` — table of all prefs grouped by category, inline form per row.
- [x] **M10.A.12** — Add nav entry "Operator preferences" to base.html.
- [x] **M10.A.13** — Write `infra/systemd/pretel-os-admin.service` per Q7 outcome. Type=simple, EnvironmentFile=$HOME/.env.pretel_os, ExecStart uvicorn main:app on `127.0.0.1:PORT`.
- [x] **M10.A.14** — Write `tests/mcp_admin/__init__.py` + `tests/mcp_admin/conftest.py` (fixture: FastAPI test client patched against pretel_os_test).
- [x] **M10.A.15** — Write `tests/mcp_admin/test_preferences_handlers.py` — 4 unit tests (GET happy path, POST happy path, POST with invalid key, header extraction).
- [x] **M10.A.16** — Write `tests/mcp_admin/test_e2e_phase_a.py` (@pytest.mark.slow) — 2 integration tests against pretel_os_test (full request → DB round-trip).
- [x] **M10.A.17** — Run `PYTHONPATH=src pytest tests/mcp_admin/` — all green. Run `pytest tests/` (full suite) — no regression on 277 baseline.
- [x] **M10.A.18** — Run `mypy src/mcp_admin/` — clean.
- [x] **M10.A.19** — Manual smoke: `PYTHONPATH=src python -m mcp_admin.main` → curl `http://127.0.0.1:PORT/preferences` shows the 3 archive thresholds.
- [x] **M10.A.20** — Phase A close: write `specs/mcp_admin/phase_a_close.md` answering Q1/Q7 + any deltas.
- [x] **M10.A.21** — Commit Phase A: `[M10.A] mcp_admin scaffolding + Cloudflare Access middleware + first view (preferences)`.

## Phase B — Remaining 4 MVP views

- [x] **M10.B.1** — Decide Q3 (pagination strategy). Document in `phase_b_close.md`.
- [x] **M10.B.2** — Decide Q4 (confirmation modal vs one-click + undo). Document in `phase_b_close.md`.
- [x] **M10.B.3** — Decide Q5 (charts vs numeric tables for costs view in V1). Document in `phase_b_close.md`.
- [x] **M10.B.4** — Write `src/mcp_admin/handlers/memory.py` — `GET /memory` with tabs (Lessons | Decisions | Best Practices), filters (bucket, tag, status), search box.
- [x] **M10.B.5** — Write `src/mcp_admin/templates/memory.html`.
- [x] **M10.B.6** — Hook semantic search to `mcp_server.tools.lessons.search_lessons` / `decision_search` / `best_practice_search`.
- [x] **M10.B.7** — Write `src/mcp_admin/handlers/dream_engine.py` — `GET /dream-engine` lists last 14 runs from `dream_engine_runs`. Sort by started_at DESC.
- [x] **M10.B.8** — Write `src/mcp_admin/templates/dream_engine.html`.
- [x] **M10.B.9** — Add "Trigger manual run" button → POST `/dream-engine/run` → `subprocess.run(['systemctl', '--user', 'start', 'pretel-os-dream-engine.service'])`.
- [x] **M10.B.10** — Write `src/mcp_admin/handlers/costs.py` — `GET /costs` reads `v_daily_cost_by_purpose` for last 30 days.
- [x] **M10.B.11** — Write `src/mcp_admin/templates/costs.html` (numeric table V1 per Q5).
- [x] **M10.B.12** — Write `src/mcp_admin/handlers/pending.py` — `GET /pending` lists `lessons WHERE status='pending_review'` + `cross_pollination_queue WHERE status='pending'`.
- [x] **M10.B.13** — Write `src/mcp_admin/templates/pending.html` with approve / reject buttons per row.
- [x] **M10.B.14** — Wire approve/reject to `mcp_server.tools.review_tools.approve_lesson` / `reject_lesson` / `resolve_cross_pollination`.
- [x] **M10.B.15** — Add nav entries to base.html for the 4 new views.
- [x] **M10.B.16** — Write unit tests for the 4 handlers (4 modules × ~3 tests = 12 tests).
- [x] **M10.B.17** — Write integration tests `tests/mcp_admin/test_e2e_phase_b.py` (@pytest.mark.slow) — 1 test per view.
- [x] **M10.B.18** — Run full test suite — green. mypy clean.
- [x] **M10.B.19** — Manual smoke walk through 5 views (preferences + 4 new).
- [x] **M10.B.20** — Phase B close: `specs/mcp_admin/phase_b_close.md` answering Q3/Q4/Q5.
- [x] **M10.B.21** — Commit Phase B: `[M10.B] mcp_admin: 4 MVP views (memory, dream-engine, costs, pending)`.

## Phase C — Drill-downs

- [ ] **M10.C.1** — Decide Q2 (markdown library — markdown-it-py vs mistune vs python-markdown). Document in `phase_c_close.md`. Default candidate: `markdown-it-py` (GFM support, code highlighting via `mdit-py-plugins`).
- [ ] **M10.C.2** — `pip install` the chosen library; commit dependency.
- [ ] **M10.C.3** — Write `src/mcp_admin/handlers/db_browser.py` — `GET /db/{table}/{id}` shows full row pretty-printed; foreign keys are clickable links.
- [ ] **M10.C.4** — Template `db_row.html`.
- [ ] **M10.C.5** — Write `src/mcp_admin/handlers/skills_detail.py` — `GET /skills/{name}` calls `mcp_server.tools.catalog.load_skill`, renders markdown to HTML, sidebar shows metadata.
- [ ] **M10.C.6** — Template `skill_detail.html`.
- [ ] **M10.C.7** — Write `src/mcp_admin/handlers/projects_detail.py` — `GET /projects/{bucket}/{slug}` calls `get_project`, reads README, renders markdown, lists project_state KV + recent decisions/tasks.
- [ ] **M10.C.8** — Template `project_detail.html`.
- [ ] **M10.C.9** — Write `src/mcp_admin/handlers/dream_run_detail.py` — `GET /dream-engine/{run_id}` shows jobs_run + failures pretty-printed JSONB; embeds `journalctl` excerpt for that time window.
- [ ] **M10.C.10** — Template `dream_run_detail.html`.
- [ ] **M10.C.11** — Hook inline preference edit (HTMX swap) on `/preferences` — POST returns the row HTML, HTMX swaps in place.
- [ ] **M10.C.12** — Write `src/mcp_admin/handlers/lesson_detail.py` — `GET /memory/lessons/{id}` shows full lesson card; approve/reject/archive actions wire to MCP tools.
- [ ] **M10.C.13** — Template `lesson_detail.html`.
- [ ] **M10.C.14** — Add clickable links from list views to drill-down pages (memory list → lesson detail; dream-engine list → run detail; tools_catalog list → skill detail; projects list → project detail).
- [ ] **M10.C.15** — Unit tests for the 6 drill-down handlers.
- [ ] **M10.C.16** — Integration tests `tests/mcp_admin/test_e2e_phase_c.py` (@pytest.mark.slow) — 1 per drill-down with a fixture row.
- [ ] **M10.C.17** — Run full test suite — green. mypy clean.
- [ ] **M10.C.18** — Manual walk: every drill-down reachable from its parent view, no 5xx.
- [ ] **M10.C.19** — Phase C close: `specs/mcp_admin/phase_c_close.md`.
- [ ] **M10.C.20** — Commit Phase C: `[M10.C] mcp_admin: 6 drill-down detail views`.

## Phase D — Production deploy + Cloudflare Access

- [ ] **M10.D.1** — Decide Q6 (single-email allowlist or backup admin email). Document in `phase_d_close.md`.
- [ ] **M10.D.2** — Cloudflare dashboard → DNS → add CNAME `mcp-admin` → Tunnel ID (or use existing Tunnel UI).
- [ ] **M10.D.3** — Cloudflare Tunnel: add public hostname `mcp-admin.alfredopretelvargas.com` → service `http://localhost:PORT`. Verify via cloudflared logs.
- [ ] **M10.D.4** — Cloudflare Zero Trust → Access → Applications → Add application → Self-hosted. Domain `mcp-admin.alfredopretelvargas.com`. Session duration 24h.
- [ ] **M10.D.5** — Add policy "operator-only" → Action: Allow → Include: Emails → `prettelv1@gmail.com` (+ backup per Q6).
- [ ] **M10.D.6** — Identity providers: confirm One-time PIN enabled. Optional: add Google.
- [ ] **M10.D.7** — Save application. Wait ~30s for propagation.
- [ ] **M10.D.8** — `cp infra/systemd/pretel-os-admin.service ~/.config/systemd/user/`.
- [ ] **M10.D.9** — `systemctl --user daemon-reload && systemctl --user enable --now pretel-os-admin.service`.
- [ ] **M10.D.10** — `systemctl --user status pretel-os-admin.service` — Active (running).
- [ ] **M10.D.11** — Open `https://mcp-admin.alfredopretelvargas.com` in browser. Verify Cloudflare Access challenge appears.
- [ ] **M10.D.12** — Login via PIN flow with operator email. Verify dashboard loads.
- [ ] **M10.D.13** — Walk all 5 views + 6 drill-downs against production data. Each must render without error.
- [ ] **M10.D.14** — Verify SC1 (no traffic reaches FastAPI without auth): test by curling the Tunnel hostname without an Access cookie — should get the Access HTML challenge, not the app.
- [ ] **M10.D.15** — Verify SC2 (page load < 2s) via browser devtools.
- [ ] **M10.D.16** — Verify SC4 (no SQL DML in admin code): `grep -rEn "INSERT|UPDATE|DELETE" src/mcp_admin/ | grep -v "^\s*#" | grep -v "test_"` → 0 lines.
- [ ] **M10.D.17** — Verify SC7 (visual coherence): side-by-side screenshot vs `alfredopretelvargas.com`.
- [ ] **M10.D.18** — Phase D close: `specs/mcp_admin/phase_d_close.md` with deployment timeline + SC1-7 verification.
- [ ] **M10.D.19** — Commit Phase D: `[M10.D] mcp_admin: production deploy + Cloudflare Access (live)`.

## Phase E — Observation + module exit

- [ ] **M10.E.1** — Day 1–7 observation: each day check `journalctl --user -u pretel-os-admin -p err --since yesterday` — should be empty.
- [ ] **M10.E.2** — Day 7: verify Cloudflare Access logs show only operator's email; no failed bypass attempts.
- [ ] **M10.E.3** — Day 7: SC6 satisfied → proceed to runbook.
- [ ] **M10.E.4** — Author `runbooks/module_10_mcp_admin.md`:
  - How to add a new Access-allowed email.
  - How to update a CSS token (re-sync from public site).
  - How to add a new view (file pattern + handler + template + nav entry).
  - How to recover from systemd failure.
  - 3 audit queries.
- [ ] **M10.E.5** — Update `tasks.md` (root) — Module 10 row marked complete with link to runbook.
- [ ] **M10.E.6** — Update `SESSION_RESTORE.md §13` (last session snapshot reflects M10 closed).
- [ ] **M10.E.7** — Update `tools.md` if any new MCP tool was added during M10 (none planned in fase 1; flag if any).
- [ ] **M10.E.8** — Tag `module-10-complete` on the closing commit (operator authorizes push).
- [ ] **M10.E.9** — Final commit: `[M10.E] Module 10 (mcp_admin fase 1) complete — runbook + tag`.

---

## Out-of-band items (track here, do later)

- [ ] **M10.fu1** — Light mode toggle (operator preference + ~50 lines CSS).
- [ ] **M10.fu2** — Real-time updates via WebSocket / SSE for `dream_engine_runs` mid-execution and `routing_logs` live tailing.
- [ ] **M10.fu3** — Skill `.md` editor in-browser with diff preview before commit.
- [ ] **M10.fu4** — Direct SQL ad-hoc query view (read-only, with timeout limits) for diagnostics that drill-downs can't serve.
- [ ] **M10.fu5** — Bulk operations (e.g., archive 50 lessons matching a query in one click).
- [ ] **M10.fu6** — Mobile-responsive layout pass.
- [ ] **M10.fu7** — Charts on costs / utility (vega-lite or Chart.js if a real trend-spotting need emerges).
- [ ] **M10.fu8** — Cloudflare uptime monitor on `mcp-admin.alfredopretelvargas.com` (free tier, page in dashboard).

---

**For atomic completion tracking:** check the box and commit per the SDD convention "one task = one commit, prefix `[M10.X.Y]`." The phase-close commits (`M10.A.21`, `M10.B.21`, `M10.C.20`, `M10.D.19`, `M10.E.9`) collect the phase-close documents.
