# AGENTS.md — pretel-os

Read this if you are an LLM entering this repository.

## Reading order

1. `AGENTS.md` (this file)
2. `identity.md` (operator identity, buckets, tools, invariants)
3. `CONSTITUTION.md` (immutable rules)
4. `plan.md §2, §5` (project state, phase gates)
5. `tasks.md` — first unchecked `[ ]` is where you are
6. `SESSION_RESTORE.md` (bridge between chats)

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

## Context layers

Not everything lives in this repo. The Router assembles context from multiple sources:

- **L0** — `identity.md` (this repo) — operator identity, purpose, invariants
- **L1** — `buckets/*/README.md` (this repo) — bucket-level context per domain
- **L2** — project state (DB: `projects_indexed`, `project_state`) — loaded by Router when a project is detected. No file to read here.
- **L3** — `skills/*.md` (this repo) — procedural memory, reusable methodologies
- **L4** — lessons (DB: `lessons`) — loaded by Router based on complexity and relevance. No file to read here.

When entering via the repo (Claude Code, git), you only see L0, L1, L3. When entering via MCP (Claude.ai), the Router provides L0–L4 as needed.

## Directory map

```
pretel-os/
├── CONSTITUTION.md          # Immutable rules
├── plan.md                  # Project-wide plan, phase gates
├── tasks.md                 # Atomic tasks (source of truth)
├── SESSION_RESTORE.md       # Bridge between chats
├── identity.md              # L0 operator identity
├── AGENTS.md                # This file
├── docs/
│   ├── PROJECT_FOUNDATION.md
│   ├── DATA_MODEL.md
│   ├── INTEGRATIONS.md
│   └── LESSONS_LEARNED.md
├── specs/                   # Per-module specs
├── buckets/                 # L1 content
├── skills/                  # L3 procedural memory
├── src/mcp_server/          # MCP server code
├── migrations/              # Postgres schema
├── infra/                   # systemd, hooks, backup
├── runbooks/                # Operational procedures
└── templates/               # SDD templates
```

## Constraints

- Do not suggest alternative architectures.
- Do not propose audits unless explicitly requested.
- Do not estimate time in hours or days.
- Match the operator's language (Spanish or English).
- Give commands first, explain after.
- No flattery, no filler.
