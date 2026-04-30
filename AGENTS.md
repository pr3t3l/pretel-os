# AGENTS.md — pretel-os

Read this if you are an LLM entering this repository.

## Reading order

1. `AGENTS.md` (this file)
2. `identity.md` (operator identity, buckets, tools, invariants)
3. `SOUL.md` (operator voice and behavior contract; how to address and work with operator)
4. `CONSTITUTION.md` (immutable rules, including §11 the tool catalog of record)
5. `plan.md §2, §5` (project state, phase gates)
6. `tasks.md` — first unchecked `[ ]` is where you are
7. `SESSION_RESTORE.md` (bridge between chats; §13 carries the latest session snapshot)
8. `runbooks/sdd_module_kickoff.md` — the trinity rule for any module being kicked off

## Agent rules (from CONSTITUTION §9)

1. The agent does not decide whether to consult lessons. The Router decides via complexity classification and pre-loads L4. The agent uses what arrives.
2. The agent never fabricates attributions. If unsure of a source, omit the claim.
3. The agent never guesses parameter names for MCP tools. Call `tool_search` first when uncertain.
4. The agent does not bypass the pre-commit Scout guard by rewriting content until the filter passes. The filter flagging content is a signal to reconsider.
5. The agent writes lessons only when a real loop closed (problem encountered and resolved) or when the Reflection worker proposes one. No fabricated lessons.
6. The agent's memory of past conversations comes only from `conversations_indexed` retrieval or MCP memory tools, never from context-window guessing.
7. The agent does not simulate code execution. Call the corresponding MCP tool. If no tool exists, propose creating one.
8. The agent honors source priority per §2.7. When layers disagree, follow the higher-priority source and surface the conflict.
9. The agent never bypasses cross-layer sync tools per §7.36. Creating a project means calling `create_project`, not writing a README directly.

## Skill discovery loop (Module 7.5)

Every turn produces a `ContextBundle` with two new fields the agent must use:

- `available_skills` — top-10 skills applicable to the classified bucket, ordered by `utility_score`. Read this BEFORE answering any non-trivial question.
- `active_projects` — top-20 active projects in the classified bucket. Same purpose: surface what's available without an extra tool call.

Discovery cycle (also in `skills/skill_discovery.md`):

1. **Receive** the operator query; Router classifies it.
2. **Glance** at `available_skills` in the response.
3. **Match** the query to a skill name/description. If yes → step 5 with that name.
4. If unsure or no obvious match → call `recommend_skills_for_query(message, bucket)`. Top result if `score >= 1.0`, else fall through to general knowledge.
5. **Load + execute**: call `load_skill(name)`, follow the skill's instructions, cite which skill you used in the reply.

Anti-patterns: do not invent tool names, do not ask the operator "what tool should I use" (use `recommend_skills_for_query` instead), do not skip the discovery glance even if you "remember" a skill from last turn.

## Context layers

Not everything lives in this repo. The Router assembles context from multiple sources:

- **L0** — `identity.md` + `SOUL.md` (this repo) + `operator_preferences` (DB) — operator identity (facts), voice (behavior contract), and live preferences. Loaded on every turn.
- **L1** — `buckets/*/README.md` (this repo) — bucket-level context per domain. Auto-projected from DB by the M7.5 readme consumer (operator notes preserved between `<!-- pretel:notes -->` markers).
- **L2** — project state (DB `projects` for live registry, `project_state` for live TODOs, `project_versions` for snapshots; `projects_indexed` for closed projects with embeddings) + `buckets/{bucket}/projects/{slug}/README.md` on disk. Loaded by the Router when a project is detected.
- **L3** — `skills/*.md` (this repo) — procedural memory, reusable methodologies. Loaded on demand when classifier picks a skill OR when the agent calls `load_skill`. Three skills currently registered: `sdd`, `vett`, `skill_discovery`.
- **L4** — lessons (DB `lessons` with embeddings) — loaded by Router when complexity ≥ MEDIUM and lessons exist for (bucket, tags). Filter-first per CONSTITUTION §5.6.

When entering via the repo (Claude Code, git), you only see L0, L1, L3 directly. When entering via MCP (Claude.ai), the Router provides L0–L4 plus `available_skills` + `active_projects` as needed.

## Tool catalog (39 tools across 11 domains)

Canonical reference: `CONSTITUTION §11`. Quick map for orientation:

| Domain | Tools |
|--------|-------|
| Router & contexto (4) | `get_context`, `tool_search`, `list_catalog`, `load_skill` |
| Skills/tools registration (2) | `register_skill`, `register_tool` |
| Lessons — capture & review (5) | `save_lesson`, `search_lessons`, `list_pending_lessons`, `approve_lesson`, `reject_lesson` |
| Best practices (4) | `best_practice_record`, `best_practice_search`, `best_practice_deactivate`, `best_practice_rollback` |
| Tasks (5) | `task_create`, `task_list`, `task_update`, `task_close`, `task_reopen` |
| Decisions (3) | `decision_record`, `decision_search`, `decision_supersede` |
| Projects (3) | `create_project`, `get_project`, `list_projects` |
| Cross-pollination (2) | `list_pending_cross_pollination`, `resolve_cross_pollination` |
| Preferences (4) | `preference_get`, `preference_set`, `preference_unset`, `preference_list` |
| Router feedback & telemetry (3) | `router_feedback_record`, `router_feedback_review`, `report_satisfaction` |
| Awareness layer (4, M7.5) | `regenerate_bucket_readme`, `regenerate_project_readme`, `archive_project`, `recommend_skills_for_query` |

If a tool you expect is not in this map, call `list_catalog()` to enumerate the full inventory or `tool_search('<keyword>')` to query by topic — never invent a name. `tool_search` is filtered by query and capped at 50; `list_catalog` is the canonical "what exists" endpoint.

## Directory map

```
pretel-os/
├── CONSTITUTION.md          # Immutable rules (§11 = tool catalog of record)
├── plan.md                  # Project-wide plan, phase gates
├── tasks.md                 # Milestone tracker
├── tasks.archive.md         # Closed atomic detail (grep convenience)
├── SESSION_RESTORE.md       # Bridge between chats; §13 has session snapshots
├── identity.md              # L0 operator identity (facts)
├── SOUL.md                  # L0 operator voice (behavior contract)
├── DECISIONS.md             # ADR log
├── AGENTS.md                # This file
├── docs/
│   ├── PROJECT_FOUNDATION.md
│   ├── DATA_MODEL.md        # 27 tables + 6 views; trigger functions; views
│   ├── INTEGRATIONS.md
│   └── LESSONS_LEARNED.md
├── specs/                   # Per-module specs (M0.X, M4 router, M5 telegram_bot, ...)
├── buckets/                 # L1 content (personal, business, scout)
├── skills/                  # L3 procedural memory (sdd, vett, skill_discovery)
├── src/
│   ├── awareness/           # M7.5 readme renderer + LISTEN/NOTIFY consumer
│   ├── mcp_server/          # MCP server code (router, tools, telemetry)
│   └── telegram_bot/        # Module 5
├── migrations/              # 37 numbered Postgres migrations (0000-0035 + 0028a)
├── infra/                   # systemd units, hooks, backup
├── runbooks/                # Operational procedures (per-module + sdd_module_kickoff.md)
└── templates/               # SDD templates
```

## Constraints

- Do not suggest alternative architectures.
- Do not propose audits unless explicitly requested.
- Do not estimate time in hours or days.
- Match the operator's language (Spanish or English).
- Give commands first, explain after.
- No flattery, no filler.
