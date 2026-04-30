# Skill: SDD — Spec-Driven Development

**Slug:** `sdd`
**Kind:** procedural skill (L3)
**Applicable buckets:** `personal`, `business`, `scout`
**Source:** distilled from the `sdd-system` repo, generalized for any client/bucket.

---

## 1. Purpose

SDD ("Spec-Driven Development") is a discipline for planning, building, and shipping software-shaped work — apps, workflows, pipelines, data jobs, AI agents — without rebuilding the same thing 10+ times.

The core idea, in one line:

> **Specify before you build. One task at a time. Stop if it breaks twice.**

A skill-aware LLM is expected to:

1. Recognize when SDD applies (see §2).
2. Drive the operator through the SDD lifecycle (§4) using the canonical artifacts (§5) and gates (§6).
3. Refuse to skip steps when a request would short-circuit the discipline ("just write the code first" is an anti-pattern — see §10).
4. Produce the right artifact at the right moment, never freelance template structure.

---

## 2. When to use SDD

Use SDD when **all** of these are true:

- The work will produce code, configuration, or an automation that will run more than once.
- The scope is non-trivial: the result is at least a module, workflow, pipeline, or dataset job — not a one-line patch.
- The work will be revisited: someone (you, future-you, or another LLM) will load context next session and need to know what was decided.
- Cost matters: tokens, infra time, or human hours are non-zero and worth budgeting.

**Do NOT invoke SDD for:**

- One-shot fixes ("rename this var", "fix this typo", "delete this file").
- Pure exploration sessions that produce no artifact (research, brainstorming, reading a paper).
- Work where the user has explicitly opted out: "no spec, just patch it."

When in doubt, ask one question: *"Will this be revisited?"* If yes → SDD. If no → just do the task.

---

## 3. Required inputs before invoking SDD

Before generating the first artifact, gather these inputs from the operator (or confirm they already exist in the project):

| Input | Where it lives | If missing |
|---|---|---|
| Project foundation (vision, stack, roadmap) | `docs/PROJECT_FOUNDATION.md` (or equivalent) | Build it first via §4 Step 0. |
| Lessons from prior work | `docs/LESSONS_LEARNED.md` or similar register | Skim before drafting; cite relevant entries in spec §Pre-Flight. |
| Data model, if the work touches storage | `docs/DATA_MODEL.md` | Add new schemas to spec §Data Model first; promote to canonical doc on close-out. |
| External integrations, if used | `docs/INTEGRATIONS.md` | Same: add to spec, promote on close-out. |
| Constitution / immutable rules | `CONSTITUTION.md` | Read before drafting — every spec must respect it. |

If the project does not yet have a foundation, **start there**. Do not write a module spec into a project with no foundation; the spec will drift.

---

## 4. Lifecycle — the six steps

SDD has six steps. Each step has an output artifact and a validation gate. Do not advance to step N+1 until step N's gate passes.

```
┌──────┐   ┌──────┐   ┌───────┐   ┌───────┐   ┌──────────┐   ┌─────────┐
│ SPEC │ → │ PLAN │ → │ TASKS │ → │ BUILD │ → │ VALIDATE │ → │  CLOSE  │
└──────┘   └──────┘   └───────┘   └───────┘   └──────────┘   └─────────┘
```

### Step 0 (one-time): Project Foundation

If the project has no `PROJECT_FOUNDATION.md`, build it first. The foundation answers "what are we building, on what stack, in what order, by what rules?" It is 3-5 pages, no longer.

Use the `PROJECT_FOUNDATION` template structure: vision, anti-goals, users, tech stack, key decisions, MVP roadmap, post-MVP one-liners, design system, monetization model, cross-cutting concerns, document registry. Do **not** put module-level detail here; that lives in specs.

### Step 1 — SPEC

**What:** A single specification document for **one** module or workflow.

**Pick the right template:**

- **Module spec** — a feature inside an app (UI screens + business rules + data writes).
- **Workflow spec** — a pipeline / automation / orchestrated sequence (input → phases → output).

(Template names: `MODULE_SPEC` and `WORKFLOW_SPEC` in the SDD template set.)

**Process:**

1. Copy the template into `specs/[name]/spec.md`.
2. Drive the operator through iterative Q&A. Fill sections in order; do not skip.
3. Resolve every "Open Questions" entry before generating the plan.

**Module spec sections (summary):**

1. Purpose & scope (problem, success criteria, in/out of scope)
2. User stories (with acceptance criteria — small enough to fit ≤8 criteria each)
3. Business rules (the "gold" — exact behaviors AI/devs get wrong without them)
4. Data model (only what THIS module creates/modifies)
5. Technical decisions (lock before coding)
6. UI screens & navigation
7. Edge cases & error handling (≥5 entries — this prevents 80% of rework)
8. Cost & monitoring (operations, est cost, observability metrics)
9. Open questions (must be empty before plan)
10. Pre-flight checklist (cite relevant Lessons Learned)
11. Testing & Definition of Done

**Workflow spec sections (summary):**

1. Purpose, success criteria, relationship to other workflows
2. Input/output contracts (with JSON schemas + validation rules)
3. Phases & agents (table: phase, executor, model, input, output, est cost, gate)
4. Model selection (only if AI/LLM is used; rules + fallbacks)
5. Failure & recovery (failure mode, detection, recovery, max retries, escalation chain, state persistence)
6. Cost tracking (budget, hard limit, how tracked)
7. Operational playbook (exact commands — copy-paste ready)
8. Open questions
9. Pre-flight checklist
10. Definition of Done

**Gate to advance:** Can you (or another LLM) explain the module/workflow in 2 minutes using only the spec? If no, the spec is incomplete.

### Step 2 — PLAN

**What:** A phased implementation plan, generated from the spec, saved to `specs/[name]/plan.md`.

**Rules:**

- Maximum **5 phases**. If you need more, the spec is too large — split it.
- Every phase has: name, goal (one sentence), estimated time, ordered actions, **and an explicit gate** ("done when …").
- Cost estimate per phase + total at the bottom.

**Typical phase shape:**

1. Foundation / setup (configs, directories, environment)
2. Core logic (the happy path)
3. Integration (wire to other systems, data persistence, external APIs)
4. Error handling / hardening (every edge case from spec §7 has a handler)
5. Testing & polish (full test suite, manual checklist, doc updates, debug-code cleanup)

**Gate to advance:** Every phase has a "done when" that is verifiable in <1 minute.

### Step 3 — TASKS

**What:** Atomic tasks, generated from the plan, saved to `specs/[name]/tasks.md`.

**Rules:**

- Each task is completable in **one AI session (<30 min)**.
- Each task has: id (`TASK-XX`), title, files it touches, dependencies, **a "done when" verifiable in <1 minute**, and a precise prompt for the implementing AI session.
- Tasks are executed in order. Dependencies are sequential.
- Include a progress tracker table at the bottom (`Task | Status | Commit | Notes`).

**Example task shape:**

```
### TASK-03: Persist lesson to Postgres
- Files: src/persistence/lessons.py, tests/test_lessons_persistence.py
- Depends on: TASK-02
- Done when: `pytest tests/test_lessons_persistence.py` exits 0
- Prompt for AI:
  Read specs/lessons/spec.md.
  Implement save_lesson(lesson_dict) writing to Postgres lessons table.
  Use the connection helper in src/db.py. Add a happy-path test
  and an "embedding-missing → degraded mode" test.
  After implementing, run: pytest tests/test_lessons_persistence.py
```

**Gate to advance:** Every "done when" is verifiable in under a minute. No task is >30 min.

### Step 4 — BUILD

**What:** Implement one task at a time. After each task: run tests, commit with `[TASK-XX] description`, advance.

**Build rules:**

1. Load the spec, plan, and tasks file into the AI session before implementation begins. Do **not** start a build session by re-explaining the project from memory — that recreates docs and causes drift.
2. Implement TASK-XX *and only TASK-XX*. Never bundle two tasks "while you're in there."
3. Run the tests defined in the task's "done when" before claiming completion.
4. Commit immediately after the task passes its gate. One task = one commit.
5. **Two-strike rule:** If a task fails twice, **STOP**. Do not force a third attempt with the same approach. The spec is incomplete or wrong. Go back to §Step 1, fix the spec, regenerate the affected tasks, then resume.

**Gate to advance:** All tasks marked complete in the progress tracker.

### Step 5 — VALIDATE

**What:** End-to-end verification before close-out.

Activities:

1. Run the full test suite (not just the per-task tests).
2. Walk through the spec's manual validation checklist (every item ticked or explicitly waived with justification).
3. Compare actual cost vs. spec §Cost estimate. If actual > 2× estimate, write a Lesson Learned (cost surprise).
4. Verify every business rule in spec §3 is exercised by at least one test.

**Gate to advance:** All tests pass + manual checklist complete + cost within (or explicitly reconciled with) estimate.

### Step 5.5 — REVIEW (recommended, not optional in practice)

Before closing, ask four questions and turn each "yes" answer into a written artifact update:

| Question | If yes → update |
|---|---|
| What took longer than expected? | New `LL-*` entry in `LESSONS_LEARNED.md` |
| What did the spec get wrong? | Update the spec template (improve future specs) |
| Did the data model change? | Update `DATA_MODEL.md` |
| Was actual cost off from the estimate? | Update spec §Cost with a "actual" column |

### Step 6 — CLOSE

**What:** Promote the work from "in progress" to "shipped" in canonical state.

Checklist:

- [ ] Spec status → ✅ Complete.
- [ ] `PROJECT_FOUNDATION.md` roadmap row updated to ✅.
- [ ] `PROJECT_FOUNDATION.md` document registry updated (any new doc added).
- [ ] `DATA_MODEL.md` updated if schemas changed.
- [ ] `INTEGRATIONS.md` updated if a new external API was added.
- [ ] `LESSONS_LEARNED.md` has at least the entries from §Step 5.5.
- [ ] Branch merged to `main` (or whichever long-lived branch the project uses).

---

## 5. Canonical artifacts

SDD treats the following files as the single source of truth. Reference them; do not duplicate their content.

| File | Purpose | Update frequency |
|---|---|---|
| `CONSTITUTION.md` | Immutable rules and AI agent rules | Rarely (formal version bump) |
| `docs/PROJECT_FOUNDATION.md` | Vision, stack, roadmap, decisions, doc registry | When a project-wide decision changes |
| `docs/DATA_MODEL.md` | All database/collection schemas, indexes, security rules | Every module that adds or modifies storage |
| `docs/INTEGRATIONS.md` | All external APIs, endpoints, limits, costs | When a new integration is added or limits change |
| `docs/LESSONS_LEARNED.md` | All failures, fixes, anti-patterns, escalation chains | Continuously |
| `specs/[name]/spec.md` | Module or workflow spec | Written once; updated only on rebuild |
| `specs/[name]/plan.md` | Implementation plan, generated from spec | Written once |
| `specs/[name]/tasks.md` | Atomic tasks, generated from plan | Updated as tasks complete |

The directory shape:

```
project-root/
├── CONSTITUTION.md
├── docs/
│   ├── PROJECT_FOUNDATION.md
│   ├── DATA_MODEL.md
│   ├── INTEGRATIONS.md
│   └── LESSONS_LEARNED.md
├── specs/
│   └── [module-or-workflow]/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
└── src/   (or lib/, app/, etc. — code lives here, never in docs)
```

---

## 6. Gates — what each one actually checks

Gates are not vibes. Each is a binary check that produces a yes/no answer:

| Gate | Belongs after | Pass condition |
|---|---|---|
| G-Spec | Step 1 | The spec is explainable in 2 minutes; all open questions resolved. |
| G-Plan | Step 2 | Every phase has a "done when" verifiable in <1 minute. |
| G-Tasks | Step 3 | Every task has a "done when" verifiable in <1 minute and is <30 min. |
| G-Build | Step 4 (per task) | Task's "done when" passes; one commit cut. |
| G-BuildAll | Step 4 (overall) | All tasks complete in tracker. |
| G-Validate | Step 5 | Full test suite green + manual checklist complete + cost reconciled. |
| G-Close | Step 6 | All close-out checkboxes ticked; branch merged. |

If a gate fails, **fall back to the previous step**. Never invent a workaround that makes the gate pass without doing the work. A failed gate means the previous step's artifact is incomplete or wrong.

---

## 7. Session protocols

### 7.1 Starting a BUILD session

```
1. Load into the AI context, in this order:
     CONSTITUTION.md
     specs/[current]/spec.md
     specs/[current]/plan.md
     specs/[current]/tasks.md
2. State the task: "Implement TASK-XX. Run [test command] when done."
3. After task completes:
     - Run tests
     - Commit with [TASK-XX] short description
     - Update tasks.md progress tracker
4. If a task fails twice → STOP. Fix the spec, not the code.
```

### 7.2 Starting a PLANNING session (new module/workflow)

```
1. Load into the AI context:
     PROJECT_FOUNDATION.md
     LESSONS_LEARNED.md (skim for relevant entries)
     DATA_MODEL.md (if storage is touched)
2. Copy the appropriate template:
     MODULE_SPEC for app features
     WORKFLOW_SPEC for pipelines/automations
3. Drive Q&A: "I want to build [description]. Ask me questions
   until the spec is complete."
4. Iterate to spec completeness; gate G-Spec must pass.
5. Generate plan.md from spec; gate G-Plan.
6. Generate tasks.md from plan; gate G-Tasks.
```

### 7.3 Starting an AI chat about an existing project

```
❌ NEVER: "Let me explain everything about my project..."
✅ ALWAYS: "Read these files: [list]. Now help me with [specific thing]."
```

Re-explaining the project from memory recreates docs and causes them to drift.

---

## 8. Working rules

These eight rules are non-negotiable. If a request would violate one, refuse and explain which rule applies.

1. **Spec before code.** No implementation without an approved spec.
2. **One task, one commit.** Atomic progress. Never bundle.
3. **Fails 2× = the spec is incomplete.** Go back to spec, do not push through.
4. **No code in docs.** Specs describe WHAT; code in `src/` implements HOW.
5. **No future specs.** Only spec the module being built NOW. The roadmap holds one-line entries; full specs are written when ready to build.
6. **Reference, never copy.** Use "See `[DOC.md §section]`" instead of duplicating content.
7. **Every doc in the registry.** A doc that is not in `PROJECT_FOUNDATION §Doc Registry` does not exist for the project.
8. **Lessons are mandatory.** Every significant issue gets a `LL-*` entry with evidence — see §9 trigger policy.

---

## 9. When to write a Lesson Learned

A lesson must be written for any of:

- A bug that took >1 hour to fix.
- A task that had to be redone.
- A cost surprise (actual > 2× estimated).
- An architectural assumption that proved wrong.
- An AI/model behavior that was unexpected.
- An incident that affected users or production.

**Lesson schema (minimum fields):**

```
ID: LL-[CATEGORY]-XXX        (PLAN | ARCH | CODE | COST | INFRA | AI | DATA | SEC | OPS | PROC)
Date:
Severity: 🔴 Critical / 🟡 Moderate / 🟢 Minor
Problem:           specific
Evidence:          logs, cost, time lost, error message
Root Cause:
Fix:               what resolved it
Prevention Rule:   one sentence — the actual lesson
Enforced by:       script, validator, test, or process. "Manual discipline" ≠ enforcement.
Time/Cost Lost:
Applies to:        apps / workflows / both
Verified:          ⬜ / ✅ YYYY-MM-DD
```

A lesson without "Enforced by" is incomplete; the operator will hit the same issue again.

---

## 10. Anti-patterns (refuse on sight)

| Anti-pattern | What happens | Apply this rule instead |
|---|---|---|
| Vibe coding (no spec) | Rebuild 10+ times | Spec → Plan → Tasks → Build |
| Monolith doc (everything in one file) | Cannot find anything; AI loses context | One doc per concern (registry in §13 of foundation) |
| Code embedded in docs | Docs desync after first commit | Code in `src/`; docs describe intent |
| Speccing future modules in detail | Wasted effort, false sense of progress | One-line roadmap entry; full spec when ready to build |
| Skipping edge cases (spec §7 incomplete) | Discover them in production | Require ≥5 entries before G-Spec passes |
| Copy-paste between docs | Docs desync within days | Reference: "See `[DOC.md §section]`" |
| Starting AI chat without loading docs | Recreate everything from memory | Load the existing docs first |
| No `LESSONS_LEARNED` entries | Repeat the same mistakes | Mandatory per §9 trigger policy |
| Tasks >30 minutes | Cannot measure progress | Split until each is <30 min |
| Phases with no "done when" | Ship broken things | Every phase has an explicit gate |
| Pushing through a 2× failure | Compound rework | Two-strike rule — back to spec |
| "Just write the code first, spec later" | Drift, untestable scope | SDD does not retrofit. Spec is the source of truth. |

---

## 11. Outputs an SDD-driven session must produce

For a brand-new module or workflow, by the time CLOSE is reached, the operator must have:

1. `specs/[name]/spec.md` — completed, status ✅.
2. `specs/[name]/plan.md` — completed.
3. `specs/[name]/tasks.md` — all tasks ✅, with commit hashes in the tracker.
4. Implementation in `src/` (or equivalent code path).
5. Tests in the project's test directory.
6. `DATA_MODEL.md` updated if schemas changed.
7. `INTEGRATIONS.md` updated if a new external API was added.
8. `LESSONS_LEARNED.md` updated with at least one entry from review (§Step 5.5).
9. `PROJECT_FOUNDATION.md` roadmap and document registry updated.
10. Branch merged to `main`.

If any of those is missing, the work is not closed. Do not say "shipped."

---

## 12. Quick decision flow

```
Request comes in
      │
      ▼
Will this be revisited?
   ├── No  → just do the task, no SDD overhead.
   └── Yes ▼
Is there a PROJECT_FOUNDATION.md?
   ├── No  → build it first (Step 0).
   └── Yes ▼
Is there a spec for this work?
   ├── No  → Step 1 (write spec via Q&A).
   └── Yes ▼
Is there a plan?
   ├── No  → Step 2.
   └── Yes ▼
Is there a tasks file with all tasks complete?
   ├── No  → Step 3 (if missing) → Step 4 (build until all ✅).
   └── Yes ▼
Has Step 5 (validate) passed?
   ├── No  → run full suite + manual checklist.
   └── Yes ▼
Step 5.5 review → Step 6 close-out.
```

---

## 13. References

- Templates referenced by name in this skill (canonical structure, do not copy verbatim into clients):
  - `PROJECT_FOUNDATION` template
  - `MODULE_SPEC` template
  - `WORKFLOW_SPEC` template
  - `plan` template
  - `tasks` template
  - `CONSTITUTION` template
  - `DATA_MODEL` template
  - `INTEGRATIONS` template
  - `LESSONS_LEARNED` template
- Core principle: *specify before you build, one task at a time, stop if it breaks twice.*

---

*SDD skill — generic, reusable across every bucket. Bucket-specific overlays (if any) live in `buckets/{bucket}/skills/`.*
