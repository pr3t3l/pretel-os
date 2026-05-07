# Module 10 mcp_admin — Phase A close

**Status:** Closed 2026-05-07
**Companion to:** `specs/mcp_admin/{spec.md, plan.md, tasks.md}`.

Phase A delivered the FastAPI scaffolding, the Cloudflare Access middleware, the first MVP view (operator preferences), the systemd unit, and the test infrastructure. Brief because most of Phase A was straight execution against a precise plan.

---

## Q1 — JWT validation in middleware (now or defer)

**Decision:** Defer to Phase B (or later, only if a real risk surfaces).

**Reasoning.** Today's threat model: uvicorn binds to `127.0.0.1` only. The only path for HTTP requests to reach the FastAPI process is through Cloudflare Tunnel, which sits in front of Cloudflare Access. To bypass Access, an attacker needs either (a) the Tunnel credentials or (b) shell access to the Vivobook. Both compromise levels make JWT-bypass a redundant defense — the attacker already owns the kingdom.

JWT signature validation against Cloudflare's JWKs endpoint adds genuine defense in depth (catches misconfiguration of Tunnel routing or Access policies), but at fase 1 scale the cost of getting it wrong (silently rejecting valid sessions during a Cloudflare key rotation) outweighs the benefit. Phase B revisits when the admin gains write surface area beyond the current single mutation (`preference_set`).

**Mitigation pending implementation:** middleware reads the `Cf-Access-Authenticated-User-Email` header and trusts it. If we ever expose the FastAPI process on a non-loopback interface, JWT validation becomes mandatory.

---

## Q7 — systemd `Type=simple` vs `Type=notify`

**Decision:** `Type=simple`.

**Reasoning.** uvicorn is a long-running process; `Type=simple` is the standard pattern for that shape. `Type=notify` requires uvicorn to integrate with systemd's notify socket via `sd_notify(3)`, which it does not ship by default. Adding it would require a wrapper or a switch to a server like Granian (which does support notify). For fase 1 single-operator usage, the `Restart=on-failure` recovery path is sufficient.

Mirrors the convention from `pretel-os-readme.service` (`Type=simple` for the M7.5 awareness consumer). The other sibling, `pretel-os-dream-engine.service`, uses `Type=oneshot` because it's batch-oneshot rather than long-running — a different shape, not a contradiction.

---

## Other Phase A artifacts

### Dependencies installed

`fastapi` and `jinja2` were missing from both interpreters used:

- `/home/pretel/.venvs/pretel-os/bin/python` (production runtime; used by the systemd unit).
- `/usr/bin/python3` user site (used by the system pytest at `/home/pretel/.local/bin/pytest`).

Both got `fastapi==0.136.1` + `jinja2==3.1.6`. `uvicorn==0.46.0` and `httpx==0.28.1` were already present.

### Port

`8088` (env-overridable via `PRETEL_ADMIN_PORT`). Chosen to avoid collisions with existing local listeners: `8787` (MCP server FastMCP), `4000` (LiteLLM), `5432` (Postgres), `5678` (n8n), `631` (CUPS). Single-byte change to 8089 if 8088 ever conflicts.

### DEV_FAKE_USER_EMAIL convention

For local development without Cloudflare Access in front, set `DEV_FAKE_USER_EMAIL=you@example.com` and the middleware injects it as the operator email. Production never sets this var; Cloudflare Access always provides the real header.

### Health-check poller in lifespan

The lifespan opens the DB pool AND starts the `db_mod.start_background_health_check()` poller. Without this, `is_healthy()` stays at `False` and every MCP tool short-circuits to degraded mode — which we discovered when `preference_set` returned `{'status': 'degraded'}` in the first test run. Tests bypass this via the `patched_admin_config` fixture which pins `is_healthy = lambda: True`.

### Test structure

```
tests/mcp_admin/
├── __init__.py
├── conftest.py             — patched_admin_config + admin_client + seed_archive_prefs fixtures
├── test_preferences_handlers.py  — 4 unit tests (middleware paths + app factory)
└── test_e2e_phase_a.py     — 2 slow tests against pretel_os_test
```

The `seed_archive_prefs` fixture is necessary because the autouse `_truncate_between_tests` in the repo-root `conftest.py` wipes `operator_preferences` after every test that requests `patched_db`. Slow tests in mcp_admin re-seed via idempotent INSERT … ON CONFLICT before each run.

---

## Phase A exit gate — verified

- [x] `python -m mcp_admin.main` starts uvicorn cleanly (smoke test on 2026-05-07 14:47:36).
- [x] `GET /health` returns `{"status":"ok"}`.
- [x] `GET /preferences` renders 4579 chars HTML containing all 3 archive thresholds + the operator email pill.
- [x] `POST /preferences/workflow/archive.usage_window_days` mutates via `preference_set` MCP tool (verified by separate-connection SELECT).
- [x] All 6 mcp_admin tests pass (4 unit + 2 slow).
- [x] Full repo suite **283/283 green** (4 fast + 2 slow new from M10 added to the existing 277).
- [x] `mypy src/mcp_admin/` clean (5 source files).
- [x] Manual smoke against production DB shows the 3 archive keys (set to 500 / 0.5 / 90 since migration 0039).

**Next:** Phase B — 4 remaining MVP views (memory browser, dream-engine runs, costs dashboard, pending review queue).
