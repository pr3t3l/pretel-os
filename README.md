# pretel-os

Personal cognitive OS for Alfredo Pretel Vargas — a durable, always-on system that turns scattered context into structured action across personal and business life.

## Status

Module 0.X complete (tag `module-0x-complete`, 2026-04-29). Knowledge architecture shipped: 4 new tables (`tasks`, `operator_preferences`, `router_feedback`, `best_practices`) + `decisions` amended (+7 columns), 18 MCP tools, 47 tests, `layer_loader_contract.md` frozen.

MCP server live at `mcp.alfredopretelvargas.com`. **Modules 4 + 5 complete 2026-04-29.** Module 4 (Router) ships classifier / layer loader L0–L4 / invariant detector / telemetry / orchestrator / MCP wrappers / fallback classifier; runbook `runbooks/module_4_router.md`. Module 5 (Telegram bot) ships 7 commands (`/start /help /save /idea /status /review_pending /cross_poll_review`) + voice handler (Whisper) + session middleware (unblocks M4 D.2 Q8) + idle-close loop. Tools served: 31 (M3 + M0.X + 6 new in M4/M5: `report_satisfaction`, `list_pending_lessons`, `approve_lesson`, `reject_lesson`, `list_pending_cross_pollination`, `resolve_cross_pollination`). Tags: `module-4-complete`, `module-5-complete`. Next: **Module 6 (Reflection worker)** — reads `routing_logs` + `conversations_indexed`, proposes lessons + cross_pollination_queue rows for operator triage via M5's review flows.

## Quick links

- [CONSTITUTION.md](CONSTITUTION.md) — 44 immutable rules
- [identity.md](identity.md) — L0 operator identity and system purpose
- [AGENTS.md](AGENTS.md) — LLM reading order and agent rules
- [plan.md](plan.md) — project roadmap and phase gates
- [tasks.md](tasks.md) — atomic work queue
- [SESSION_RESTORE.md](SESSION_RESTORE.md) — bridge between chats

Start with [CONSTITUTION.md](CONSTITUTION.md) (the 44 immutable rules). The roadmap lives in [plan.md](plan.md), atomic work queue in [tasks.md](tasks.md), and deep references under [docs/](docs/). If you're resuming mid-work, read [SESSION_RESTORE.md](SESSION_RESTORE.md) first.

Private repo. All rights reserved — see [LICENSE](LICENSE).
