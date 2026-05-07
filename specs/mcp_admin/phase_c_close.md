# Module 10 mcp_admin — Phase C close

**Status:** Closed 2026-05-07
**Companion to:** `specs/mcp_admin/{spec.md, plan.md, tasks.md, phase_a_close.md, phase_b_close.md}`.

Phase C added the six drill-down detail views the spec promised (table row, skill `.md` render, project README + state, dream_engine_run JSONB, lesson full card) plus hyperlinks from the list views to those drill-downs. The "preference inline edit via HTMX swap" sub-item was deferred to a follow-up — the existing redirect-303 path already works; HTMX is a UX enhancement, not a blocker.

---

## Q2 — Markdown rendering library

**Decision:** `markdown-it-py` + `mdit-py-plugins` (specifically the `tasklists` plugin; built-in `table` and `strikethrough` enabled).

**Reasoning.** Three candidates considered:

| Lib | GFM tables | Code highlighting | Footnotes / Tasklists | Maintenance |
|-----|-----------|-------------------|----------------------|-------------|
| markdown-it-py | ✓ (built-in via .enable) | via plugins | via plugins | Active, ESM-style API mirroring markdown-it (JS) |
| mistune | ✓ | via Pygments hook | mostly | Maintained but smaller ecosystem |
| python-markdown | ✓ via Tables ext. | via codehilite ext. | via plugins | Stable but verbose plugin model |

Picked markdown-it-py for plugin breadth + matching the `markdown-it` mental model (the operator's `alfredo-ai-factory-guide` site uses `react-markdown` which wraps the JS markdown-it). Same renderer behavior across both surfaces.

Implementation lives at `src/mcp_admin/markdown.py` — 1 module-level `MarkdownIt` instance with `commonmark + linkify + typographer + table + strikethrough + tasklists`. `render(content)` returns HTML string (or empty string for empty input).

---

## Drill-downs delivered

| Path | Source | Implementation note |
|------|--------|---------------------|
| `GET /db/{table}/{row_id}` | raw psycopg + `information_schema` | Allowlist of 16 browsable tables. Renders shell + "row not found" panel even when id is bogus — friendlier for diagnostics than a hard 404. |
| `GET /skills/{name}` | `mcp_server.tools.catalog.load_skill` + `tools_catalog` SELECT for sidebar metadata | Markdown rendered server-side. Sidebar shows utility / usage / trigger_keywords / applicable_buckets. |
| `GET /projects/{bucket}/{slug}` | `mcp_server.tools.projects.get_project` + scoped decision/task SELECTs | README parsed from disk via `Path(readme_path).read_text()`. Recent decisions + tasks linked via `project_id` FK. |
| `GET /dream-engine/run/{run_id}` | raw psycopg, dream_engine_runs by id | Pretty-printed `jobs_run` + `failures` JSONB. journalctl excerpt deferred to fase 2 (adds subprocess + escaping; not blocking). |
| `GET /memory/lessons/{lesson_id}` | raw psycopg, lessons by id | Full card with title / content / next_time / metadata + tags + applicable_buckets. Approve / reject buttons routed through `approve_lesson` / `reject_lesson` MCP tools when status='pending_review'. |

**Hyperlinks added** in `memory.html` (lessons → lesson detail; decisions → /db/decisions; best_practices → /db/best_practices) and `dream_engine.html` (run row started_at → run detail). Click-through tested manually.

---

## Deferred from Phase C → follow-ups

### M10.fu9 — HTMX inline preference edit

The spec's M10.C.11 called for HTMX-driven swap of the preferences row after edit (no page reload). Phase C ships the drill-downs but keeps the redirect-303 path. Reasoning: the redirect path works correctly, the visual difference is a sub-second flicker, and the HTMX wiring would have added another partial template + handler branching for `HX-Request: true`. Defer until the operator finds the page reload annoying enough to ask for the upgrade.

### M10.fu10 — journalctl excerpt in dream_run_detail

Plan M10.C.9 promised an embedded journalctl snippet for the run's time window. Implementing that requires `subprocess.run(['journalctl', ...])` with careful argument escaping and timeout handling, plus deciding which lines are "the relevant ones" (full-text? error-only?). The spec template includes the manual `journalctl --since X --until Y` invocation operator can copy. fu10 wires it inline when there's signal that operators are using it.

### M10.fu11 — `archive_lesson` MCP tool + lesson detail archive button

The lesson detail page currently exposes approve / reject actions. Archive is documented as a follow-up because no `archive_lesson` MCP tool exists (Dream Engine archives via direct UPDATE per M8). Adding the tool + the button is a small addition once the operator wants the manual archive path.

---

## Phase C exit gate — verified

- [x] 5 new drill-down handlers + 5 templates committed.
- [x] List views (memory, dream_engine) link to their drill-downs.
- [x] `markdown-it-py` + `mdit-py-plugins` installed in both Pythons.
- [x] **30 mcp_admin tests green** (4 unit + 2 Phase A slow + 13 Phase B slow + 11 Phase C slow).
- [x] **307 full repo tests green** (was 296; +11 from Phase C).
- [x] `mypy src/mcp_admin/` clean (15 source files: 1 init, 1 main, 1 middleware, 1 markdown, 1 handlers/init, 10 handlers).
- [x] Manual smoke against production DB: 5 drill-downs return 200 against real rows
  - `/skills/class-knowledge-extraction` (the meta skill committed earlier this session)
  - `/memory/lessons/{id}` (real lesson row)
  - `/dream-engine/run/0f552c95` (the first live Dream Engine run)
  - `/db/decisions/{id}` (real decision row)
  - `/projects/personal/pretel-os` (the meta-project registry row)

**Next: Phase D — production deploy + Cloudflare Access policy + first live access from operator's browser.** Phase D is operator-driven (DNS + Tunnel + Access policy in Cloudflare dashboard) — Claude can write the runbook entries but the actual go-live click is operator's call.
