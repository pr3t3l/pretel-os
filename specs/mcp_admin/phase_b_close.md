# Module 10 mcp_admin — Phase B close

**Status:** Closed 2026-05-07
**Companion to:** `specs/mcp_admin/{spec.md, plan.md, tasks.md, phase_a_close.md}`.

Phase B added the four remaining MVP views (memory, dream-engine, costs, pending) plus their nav entries and tests. Brief because most of Phase B was straight implementation against the spec.

---

## Q3 — Pagination strategy

**Decision:** Offset/limit. Default `limit=50`, hard cap 200.

**Reasoning.** At current corpus: ~80 lessons + 26 decisions + 31 best_practices = ~140 rows total in the memory tables. Cursor-based pagination is overkill until at least 10k rows. Offset/limit is straightforward, debuggable, and fits naturally with HTML pagination links (`?offset=N&limit=N`). When the lessons table grows past ~5k rows we revisit.

Implementation: `offset` and `limit` are query params validated by FastAPI's `Query(..., ge=0)` / `Query(..., ge=1, le=200)`. The handler runs a `count(*)` for total + the paginated SELECT for rows, then computes `next_offset` / `prev_offset` for the template's prev/next links.

---

## Q4 — Confirmation modal vs one-click + undo

**Decision:** JS `confirm()` dialog for destructive actions (reject lesson, reject cross-pollination, manual Dream Engine trigger). One-click + HTMX-style result for approve.

**Reasoning.** Approve is reversible — a `pending_review → active` flip can be set back to `pending_review` if the operator changes their mind. Reject is harder to undo (the row drops out of the queue and the operator has to remember its content). Treating them asymmetrically respects the actual blast radius.

Manual Dream Engine trigger gets a confirm because it's not an admin-data write but it does spawn a subprocess that records a row in `dream_engine_runs`. Misclick = ugly noise in the run history.

`confirm()` is browser-built-in, requires zero JS framework dependency, and matches the dark-theme aesthetic via the system. A custom modal is fase 2 if the operator finds the native dialog ugly.

---

## Q5 — Charts vs numeric tables for the costs view

**Decision:** Numeric tables only in V1. Three sub-tables on the costs page:
- By purpose (sum across 30 days, sorted by cost descending)
- By day (sum across all purposes/models, last 14 days shown)
- Detail (purpose × model × day, raw rows from `v_daily_cost_by_purpose`)

**Reasoning.** Today the operator's monthly spend is on the order of cents (current 30-day total: $0.000000 — every classifier call is sub-cent). A chart would communicate "approximately zero" no better than the number "$0.00". When there's actual signal in the data — multi-dollar daily fluctuations from an LLM call surge — charts become the right surface. Until then, tables are honest about what's happening.

Re-charter: when monthly spend exceeds $1 / day on average for 7 consecutive days, fase 2 adds a Chart.js trend visualization above the tables.

---

## Implementation notes (non-decision deltas)

### MCP tool location correction

The plan's M10.B.6 / B.14 referenced `mcp_server.tools.review_tools.approve_lesson`. That module does not exist — `approve_lesson` and `reject_lesson` live in `mcp_server.tools.lessons`, alongside `save_lesson` and `search_lessons`. The handlers import from the correct location. No constitutional implication; just a docs delta to track.

### Manual trigger via systemd, not Python entry point

`POST /dream-engine/run` invokes `systemctl --user start pretel-os-dream-engine.service` rather than calling `dream_engine.worker.main(...)` directly. Reasoning:
- Single source of truth for the worker invocation path. Whatever the timer does is what the manual trigger does.
- The worker writes its own `dream_engine_runs` row, so the admin doesn't have to fake telemetry.
- Failures show up in `journalctl --user -u pretel-os-dream-engine.service` consistently.

### Pagination link state preservation

The memory view's prev/next links propagate every filter (`tab`, `bucket`, `tag`, `status`, `q`, `limit`) so the operator's filter state survives navigation. Implemented via Jinja string interpolation into the link href — no JS state needed.

### Confirm dialog passes the prompt result through hidden form fields

For reject actions, the operator-supplied reason / note flows from `prompt()` → hidden `<input>` → form POST. Crude but works without HTMX or a JSON API. HTMX upgrade is fase 2 along with inline edit of preferences (Phase C).

---

## Phase B exit gate — verified

- [x] All 4 new view handlers + 4 templates committed.
- [x] base.html nav lists all 5 MVP views; active state highlights via `active_view` context var.
- [x] main.py `build_app()` includes 5 routers; routes verified via `/openapi.json` introspection.
- [x] **19 mcp_admin tests green** (4 unit + 2 Phase A slow + 13 Phase B slow).
- [x] **296 full repo tests green** (was 283; +13 from Phase B).
- [x] `mypy src/mcp_admin/` clean (9 source files: 1 init, 1 main, 1 middleware, 1 handlers/init, 5 handlers).
- [x] Manual smoke against production DB: all 7 GET routes return 200 (including 3 memory tabs as separate paths). Lifespan opens pool + health check poller transitions False→True cleanly. Clean shutdown on SIGINT.

**Next: Phase C — 6 drill-down detail views.** Markdown library decision (Q2) lives at the top of Phase C; default candidate `markdown-it-py` for GFM + code highlighting.
