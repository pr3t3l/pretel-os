# SDD module kickoff

**Status:** Active rule
**Owner:** Alfredo Pretel Vargas
**Created:** 2026-04-28

This runbook documents the procedure for starting a new module. Every module post-Module-3 follows it. Modules 1–3 closed before this rule existed and are exempt; root `tasks.md` carries them as closed milestones only.

## Why this exists

Root `tasks.md` and per-module `specs/<module>/tasks.md` accumulated drift because both held atomic-level checkboxes. Closing a phase required manual sync of two files; missed sync produced misleading state. Lessons LL-M4-PHASE-A-002 (verbal acknowledgment) and LL-M0X-001 (spec drift) describe the same failure mode at the doc level: state captured in one place but referenced in another.

The fix is structural: each level of granularity has exactly one canonical home.

## The rule

For every module that starts after 2026-04-28:

1. **Before first line of implementation code**, create the SDD trinity at `specs/<module-slug>/`:
   - `spec.md` — what to build
   - `plan.md` — how to build it (phases, gates, dependencies)
   - `tasks.md` — atomic checkboxes (one per migration, function, test, doc update)

2. **Root `tasks.md` gets one section per module**, milestone-only:

   ```
   ## Module N — <slug>
   - [x] M<N>.T1 SDD trinity (commits XXX, YYY, ZZZ)
   - [x] M<N>.T2 Phase A — <name> (closed)
   - [ ] M<N>.T3 Phase B — <name>
   - [ ] ...

   Per-module detail: `specs/<slug>/tasks.md`
   ```

3. **When a phase closes**, update both:
   - Per-module `tasks.md` — flip the relevant atomic checkboxes to `[x]`
   - Root `tasks.md` — flip the milestone line to `[x]` and add closure commit hash(es)

4. **When a module phase or whole module completes**, append a closure summary to `tasks.archive.md` under a dated section header. The summary contains: closure commits, schema/code artifacts, atomic task count, and a pointer to the per-module `tasks.md` for line-by-line history. The full atomic content stays in per-module `tasks.md` (with `[x]` markers) — do not duplicate it in the archive.

   Modifications to this convention require a runbook update + commit; CONSTITUTION amendment NOT required unless the rule changes a §-level invariant.

5. **Naming conventions:**
   - Root milestone IDs: `M<N>.T<seq>` (e.g., `M5.T1`, `M5.T2`, ..., `M0X.T4.B`)
   - Per-module atomic IDs: `M<N>.<phase>.<n>.<sub>` (e.g., `M0X.A.4.5`, `M0X.C.5.2a`)

## What goes where, in one table

| Audience | File | Granularity |
|---|---|---|
| Operator: "what's the project state?" | `plan.md` (root) | Project phases, gates, risk register |
| Operator: "what milestone is next?" | `tasks.md` (root) | Module + phase milestones, 1 line each |
| Implementer: "what do I do RIGHT NOW?" | `specs/<module>/tasks.md` | Atomic checkboxes, ~50-150 per module |
| Implementer: "how does this module hang together?" | `specs/<module>/plan.md` | Module phases, deliverables, gates |
| Implementer: "what does this module deliver?" | `specs/<module>/spec.md` | Module schema, contracts, scope |
| LLM-new-to-project: "where do I start?" | `SESSION_RESTORE.md` | Pointer to current state, document map |
| Auditor: "what was the historic atomic detail?" | `tasks.archive.md` | Closed phase closure summaries + pre-rule verbatim snapshot + git log |

## Anti-patterns

- **Duplicating atomic checkboxes in both root and per-module tasks.md** — this is the failure mode this runbook prevents. If you find yourself adding an `M5.A.1.1` line to root tasks.md, stop and put it in `specs/telegram_bot/tasks.md` instead.
- **Modifying constitution to encode this rule** — convention does not warrant constitutional amendment. CONSTITUTION is for invariants ("MCP server is single gateway"). This runbook is for convention.
- **Skipping the per-module trinity for "small" modules** — small modules grow. If a module is so small it doesn't need a spec, it's probably a task in another module's tasks.md, not a module.
- **Pointing root tasks.md at a per-module file that doesn't exist yet** — for modules that haven't kicked off, the root entry says `Per-module detail: TBD (created at M<N> kickoff per runbooks/sdd_module_kickoff.md)`. Don't write paths to files you haven't created.
