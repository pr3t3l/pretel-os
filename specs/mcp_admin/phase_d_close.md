# Module 10 mcp_admin — Phase D close

**Status:** Closed 2026-05-07
**Companion to:** `specs/mcp_admin/{spec.md, plan.md, tasks.md, phase_a/b/c_close.md}`, `runbooks/module_10_mcp_admin_deploy.md`.

Phase D took the admin from "scaffolded + tested locally" to "live in production behind Cloudflare Access at `https://mcp-admin.alfredopretelvargas.com`". Deploy was split: Claude installed the local systemd unit and pre-verified what could be pre-verified (SC4 + health from localhost); operator handled the Cloudflare dashboard work (Tunnel route + Access application + email-allowlist policy) and the first live login.

---

## Q6 — Allowlist composition

**Decision:** Single-email allowlist (operator's primary email). No backup admin email in V1.

**Reasoning.** Single-operator system per `identity.md`. Recovery without Cloudflare Access remains possible via SSH to the Vivobook (`systemctl --user stop pretel-os-admin.service` if needed; direct DB / file edit for irrecoverable lockouts). Cloudflare's PIN flow targets the email field of the request — wrong-email-typed cases return "access denied" cleanly without compromising the allowlist.

A backup email can be added post-launch via Cloudflare dashboard → Access → Applications → pretel-os admin → Policies → operator-only → Include → Emails → add second address. Trivial change, deferrable to need.

---

## Deployment timeline

| Step | Actor | What |
|------|-------|------|
| 2026-05-07 ~15:12 EDT | Claude | `cp` systemd unit to `~/.config/systemd/user/` + `daemon-reload` + `enable --now` |
| 2026-05-07 ~15:12 EDT | Claude | Verified service active (PID 655129, ~57MB memory, Type=simple uvicorn) |
| 2026-05-07 ~15:12 EDT | Claude | `curl http://127.0.0.1:8088/health` → `{"status":"ok"}` from localhost |
| 2026-05-07 ~15:12 EDT | Claude | SC4 grep: zero SQL DML in `src/mcp_admin/` handlers (every mutation routes through MCP tools) |
| 2026-05-07 (operator window) | Operator | Cloudflare Tunnel — added public hostname `mcp-admin.alfredopretelvargas.com` → `localhost:8088`. DNS auto-created. |
| 2026-05-07 (operator window) | Operator | Cloudflare Zero Trust → Access → Applications → Add self-hosted "pretel-os admin", session 24h, identity provider One-time PIN |
| 2026-05-07 (operator window) | Operator | Access policy "operator-only" → Allow → Include Emails: operator's primary email |
| 2026-05-07 (operator window) | Operator | Saved application; ~30 s propagation |
| 2026-05-07 (operator window) | Operator | First live login: PIN flow → dashboard rendered |
| 2026-05-07 (operator window) | Operator | Walked all 5 views + drill-downs; verified SC1/SC2/SC3/SC5/SC7 |

---

## Success criteria status

| SC | Status | Evidence |
|----|--------|----------|
| **SC1** — no traffic reaches FastAPI without auth | ✅ | Operator confirmed Cloudflare Access challenge appears for unauthenticated requests; logged-in journalctl shows only authenticated requests reaching uvicorn. |
| **SC2** — page load < 2 s (95th) | ✅ | Operator browser devtools: cold load < 2 s, warm < 500 ms. |
| **SC3** — all 5 views render against live state | ✅ | Operator clicked through all 5 nav entries; all rendered with live DB content. |
| **SC4** — no SQL DML in admin code | ✅ (Claude pre-verified) | `grep -rEn "^\s*[^#]*\b(INSERT\|UPDATE\|DELETE)\b" src/mcp_admin/` returns 0 lines. Mutation handlers in handlers/preferences.py + handlers/pending.py + handlers/lesson_detail.py all import from `mcp_server.tools.*` and call those functions. |
| **SC5** — drill-downs work | ✅ | Operator clicked from `/memory` lesson rows → lesson detail; from `/dream-engine` rows → run detail; manually navigated to `/projects/personal/pretel-os` and `/skills/class-knowledge-extraction` — all rendered. |
| **SC6** — 7-day observation | ⏳ in progress | Window opened 2026-05-07. Daily journalctl checks until 2026-05-14. |
| **SC7** — visual coherence | ✅ | Side-by-side with `alfredopretelvargas.com`: teal/amber/purple tokens match, Inter font visible, dark mode default, border-radius consistent. |

---

## Production state — what's live now

| Component | State |
|-----------|-------|
| `mcp-admin.alfredopretelvargas.com` | Resolves via Cloudflare; DNS auto-created by Tunnel public hostname |
| Cloudflare Tunnel route | `mcp-admin.alfredopretelvargas.com` → `http://localhost:8088` |
| Cloudflare Access application | "pretel-os admin", self-hosted, session 24h |
| Cloudflare Access policy | "operator-only" — Allow + Include emails: single operator |
| systemd `pretel-os-admin.service` | enabled (default.target.wants) + active (running) |
| FastAPI uvicorn | 127.0.0.1:8088, lifespan opens DB pool + health-check poller |
| Backend CSS tokens | teal `#1D9E75` / amber `#EF9F27` / purple `#7F77DD` from `alfredo-ai-factory-guide` |

---

## Phase D exit gate — verified

- [x] DNS + Tunnel + Access configured.
- [x] First live login flow works (PIN → dashboard).
- [x] All 5 views render against production data.
- [x] All 6 drill-downs reachable + render.
- [x] SC1, SC2, SC3, SC5, SC7 verified by operator at first live access.
- [x] SC4 pre-verified by Claude.
- [ ] SC6 ⏳ in progress (7-day observation, closes 2026-05-14).

**Next: Phase E — 7-day observation + runbook + tag `module-10-complete`.**

Phase E is calendar-driven. One-line check per day:

```bash
journalctl --user -u pretel-os-admin -p err --since yesterday --no-pager
# Expected: empty output (no error-level log lines)
```

If empty for 7 consecutive days → SC6 satisfied → operator authorizes Phase E close (write `runbooks/module_10_mcp_admin.md` operations runbook, flip checkboxes, tag `module-10-complete`).
