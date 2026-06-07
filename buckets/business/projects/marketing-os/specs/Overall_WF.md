# Marketing OS — Overall Workflow

**Project:** business/marketing-os  
**Document type:** lifecycle overview  
**Status:** living document; architecture corrected for Sandi Marketing MVP  
**Last updated:** 2026-06-06 (parallel multi-avatar orchestration + strategies entity + Phases 3/4/5)

## Current Implementation Plan

Marketing OS is now implemented as **Sandi Marketing**, a separate product repo:

```text
C:\Users\prett\Documents\sandia-marketing
```

This `pretel-os` project directory keeps the marketing methodology, specs, historical decisions, and learning context. It is not the runtime app.

## Core Differentiator: Parallel Multi-Avatar Orchestration

This is the architectural thesis of Sandi. Every other feature is downstream of it.

**The job:** a single problem (e.g. "I want to validate / scale my idea") is shared by very different people — a student and a bakery owner have the *same problem* but require *100% different marketing strategies* (different channels, language, awareness level, willingness to pay). A human consultant cannot economically sustain many distinct avatars, each with its own evolving strategy, content, metrics and improvement loop running in parallel. **An AI system can — trivially and cheaply.**

**The thesis:** Sandi's defensible advantage is **not** "AI-powered personas" or "AI content" (both commoditized). It is **maintaining N avatars alive simultaneously, each with its own full Phase 1→5 loop (offer → content → publish → measure → adjust), versioned over time.** This is structural, not cosmetic — competitors are one-shot generators; Sandi is a persistent parallel orchestrator.

**Design consequences (binding on all phase specs):**
- Per-avatar strategy is the **default**, not the exception. Unifying avatars into one offer is an *optimization* that must be justified by evidence — not the goal (see Phase 1 §4).
- There is **no hard cap** on avatars. The operator may prioritize which to activate first, but the system holds N in parallel (supersedes the old "max 5 avatars" rule in Phase 0 §6).
- Strategies are **versioned in time**. The Phase 5 loop does not overwrite a strategy; it emits Strategy #N+1 for that avatar, preserving history for learning (see §"Strategy Lifecycle").

## Canonical Project Hierarchy

The foundation layer (business context, market, segment) is **avatar-agnostic** — it describes the idea, the market and the segment, which are identical regardless of which avatar you later address. Avatar-specific branching begins only at the Buyer Persona / Avatar layer.

```text
Project  ("Mi negocio de X")
│
├── FOUNDATION  (avatar-agnostic — Phase 0.1–0.2.5)
│   ├── Business Context Gate   (0.1)   — La Idea / Contexto (B2B|B2C, etc.)
│   ├── Demand Quantification   (0.2)   — El Mercado (TAM/SAM/SOM + awareness)
│   └── ICP Layer               (0.2.5) — El Segmento (cuenta/cluster)
│
└── Buyer Persona  (0.3 — universal del proyecto: p.ej. "gente que valida/escala ideas")
    ├── Avatar 1  (ej: Estudiante)
    │   ├── Strategy #1 — 2026-06-01 → Resultados · Learnings · Decisions · Best Practices
    │   └── Strategy #2 — 2026-09-01 → Resultados · Learnings · Decisions · Best Practices
    ├── Avatar 2  (ej: Panadero)
    │   └── Strategy #1 — 2026-06-01 → Resultados · Learnings · Decisions · Best Practices
    └── Avatar N  …
```

- **Foundation (0.1–0.2.5):** computed once per project, shared by all avatars. Re-runs only on Phase 0 re-trigger conditions.
- **Buyer Persona (0.3):** one primary persona per project by default (the universal segment description). Additional personas only with evidence.
- **Avatar:** an independent unit of orchestration. Each avatar owns its own strategy stream.
- **Strategy:** one full run of Phase 1→5 for one avatar, dated and versioned. Each strategy produces its own Results, Learnings, Decisions and Best Practices.

## Strategy Lifecycle (the per-avatar loop in time)

For each avatar, Phases 1→5 produce a **Strategy** record:

1. Phase 1 (Oferta) + Phase 2 (Contenido) author the strategy's offer and content plan.
2. Phase 3 (Publicar) + Phase 4 (Medir) execute and collect `results_summary`.
3. Phase 5 (Ajustar) reads results and, instead of editing the active strategy, **emits Strategy #N+1** for that avatar (status `active`), marking the previous one `superseded`. Learnings, decisions and best practices are persisted **per strategy version**, never flattened to the project.

This preserves the full history per avatar — the substrate the system learns from, and what makes parallel avatars cheap to maintain over time.

## Stack Actual

- **Frontend:** Next.js App Router + TypeScript + Tailwind + shadcn/ui-style local components.
- **Data layer:** `lib/api/*.ts`; components, pages, and UI hooks must not call `supabase.from()` directly.
- **State:** TanStack Query for server state; Zustand for local UI state.
- **Backend MVP:** Supabase Cloud Postgres + Auth + RLS + migrations.
- **Edge Functions:** only for secrets, webhooks, and privileged jobs.
- **Deploy:** Vercel for frontend; Supabase Cloud for DB/Auth/Functions.
- **Backend future:** FastAPI only when logic-heavy workflows, long jobs, complex agents, or a public API justify it.
- **Workflow engine:** n8n is not part of the MVP; revisit in Phase 3 if real distribution/publication needs it.

## Superseded Assumptions

The previous plan described Marketing OS as a Python/FastMCP module inside `pretel-os`, with PhaseHandlers, LiteLLM runtime gateway, n8n workflow execution, and pretel-os Postgres as primary app state. That architecture is superseded.

Preserve the **marketing workflow logic** from the phase specs. Do not preserve the old runtime architecture unless the operator explicitly reintroduces it.

## Data Model V1

- `auth.users` — managed by Supabase Auth.
- `projects` — main project/campaign entity. Owns the avatar-agnostic Foundation artifacts (business context, demand, ICP).
- `project_members` — membership and roles; replaces `shared_with_user_ids[]`.
- `buyer_personas` — universal persona(s) per project (Phase 0.3 output A). One primary by default. `project_id` FK.
- `avatars` — independent orchestration unit (Phase 0.3 output B). `project_id` + `buyer_persona_id` FK. No hard cap on rows per project.
- `strategies` — **(new)** one full Phase 1→5 run for one avatar, versioned in time. See schema below.
- `project_phase_artifacts` — outputs by phase, sub-step, artifact name, and JSON content. Gains nullable `avatar_id` + `strategy_id` FKs: Foundation artifacts (Phase 0.1–0.2.5) leave both null (avatar-agnostic); per-avatar artifacts (Phase 1+) set both.
- `project_decisions` — decisions and rationale. Gains nullable `avatar_id` + `strategy_id` FKs so per-strategy decisions hang off their strategy version, not the flat project.
- `project_lessons` — captured learnings. Gains nullable `avatar_id` + `strategy_id` FKs (same rationale).
- `project_audit_log` — sensitive events and important changes.

`strategies` schema (V1):

```text
strategies
─ id                  uuid pk
─ project_id          uuid fk → projects
─ avatar_id           uuid fk → avatars   -- the PRIMARY avatar of this strategy
─ covers_avatar_ids   uuid[]              -- all avatars this strategy serves (see unified vs separate below)
─ multi_avatar_strategy text             -- single_avatar | unified_C_* | separate_strategies (mirrors offer_spec)
─ version_number      int            -- 1, 2, 3 … the time dimension of the hierarchy
─ status              text           -- active | superseded | archived
─ created_at          timestamptz
─ offer_spec_id       uuid           -- Phase 1 output (offer_spec.json)
─ content_plan_id     uuid           -- Phase 2 output (content_plan.json)
─ results_summary     jsonb          -- Phase 4 "Resultados" rollup
─ superseded_by       uuid fk → strategies (self)  -- Phase 5 emits N+1, points back here
```

**Strategy granularity — unified vs separate (resolves the multi-avatar tension):**
- **`separate_strategies` (default):** one strategy per avatar. `avatar_id` set, `covers_avatar_ids = [avatar_id]`. This is the clean per-avatar case from the diagram — N avatars → N parallel strategies.
- **`unified_C_*`:** one strategy serves several near-identical avatars (the Phase 1 unification optimization). `avatar_id` = primary avatar, `covers_avatar_ids` = all covered avatars. The shared strategy still produces per-strategy results/learnings, but content is differentiated per avatar via `language_packs` inside the single plan.
- **`single_avatar`:** trivially one avatar.

**Invariant:** each avatar is served by exactly one `active` strategy at a time (either its own, or a shared unified one). Phase 5 creates the next version and supersedes the previous. Results, learnings, decisions and best practices are queried per `strategy_id`.

RLS protects base access by project membership. Complex product behavior belongs in `lib/api`, Edge Functions, or future FastAPI, not in RLS.

## Lifecycle

The lifecycle remains the product methodology:

1. **Phase 0 — Research + ICP**  
   Output: `product_brief_v2.json`. Establish business context, demand, ICP, buyer persona, avatars, negative personas, competitors, and evidence findings.

2. **Phase 1 — Oferta**  
   Output: `offer_spec.json` + `offer_statement.md`. Convert research into value equation, offer stack, pricing, risk reversal, urgency, and positioning.

3. **Phase 2 — Contenido**  
   Output: `content_plan.json` + `content_assets/`. Convert offer into content pillars, hooks, derivatives, and channel-ready assets.

4. **Phase 3 — Publicar / Distribuir**  
   Output: `publish_plan.json` + `tracking_manifest.json`. Calendar, tracking (UTM/pixel/conversion events), exclusion lists, targeting. Runs per strategy. Carries the economics baseline to Phase 4.

5. **Phase 4 — Medir**  
   Output: `metrics_snapshot.json` + writes `strategies.results_summary`. Unit economics (CAC/LTV vs baseline), funnel by awareness, per-avatar attribution. Produces `phase_5_flags` (the loop's input).

6. **Phase 5 — Ajustar / Optimizar**  
   Output: `optimization_plan.json` + per-strategy lessons/decisions/best-practices. **Per avatar:** Phase 5 does not edit the active strategy — it emits Strategy #N+1 (new `strategies` row, status `active`) and marks the previous `superseded`. A flag→action→re-trigger table routes each Phase 4 flag to the minimal phase that fixes the root cause. See §"Strategy Lifecycle".

**Note on scope of the loop:** Phases 1→5 run **per avatar**, in parallel across all active avatars. The Foundation layer (Phase 0.1–0.2.5) is shared and runs once per project. This is the parallel multi-avatar orchestration described above.

## Phase Specs

- `spec_Phase_0_Research_ICP.md` — research and ICP (Foundation + persona/avatars).
- `spec_Phase_1_Oferta.md` — offer construction (+ strategy birth, D-009/010).
- `spec_Phase_2_Contenido.md` — content planning (anchored to strategy).
- `spec_Phase_3_Distribucion.md` — publish, tracking, targeting (per strategy).
- `spec_Phase_4_Medir.md` — measurement, unit economics, writes `results_summary`.
- `spec_Phase_5_Ajustar.md` — the loop: flag→action→re-trigger, emits Strategy #N+1.

## Phase ↔ Supabase `artifact_phase` mapping

The implementation (`sandia-marketing`) enum `artifact_phase` maps to methodology phases:

| Methodology phase | `artifact_phase` value |
|---|---|
| Phase 0 — Research + ICP | `discovery` |
| Phase 1 — Oferta | `strategy` |
| Phase 2 — Contenido | `production` |
| Phase 3 — Publicar / Distribuir | `distribution` |
| Phase 4 — Medir / Phase 5 — Ajustar | `review` |

## Implementation migrations (`sandia-marketing/supabase/migrations/`)

- `20260531221000_initial_schema.sql` — projects, members, phase_artifacts, decisions, lessons, audit (+ RLS).
- `20260606120000_avatars_strategies.sql` — **buyer_personas, avatars, strategies** (with `covers_avatar_ids`, versioning, `superseded_by`) + `avatar_id`/`strategy_id` FKs on artifacts/decisions/lessons + RLS + audit triggers. Implements D-009/D-010/D-011.

These specs are now **workflow requirements** for Sandi Marketing. They should be translated into app screens, form schemas, API calls, and Supabase artifacts incrementally. References inside those specs to PhaseHandlers, n8n, FastMCP, or pretel-os DB runtime are legacy implementation notes unless explicitly marked current.

## Implementation Status

- Repo scaffolded: `C:\Users\prett\Documents\sandia-marketing`.
- Verification passed: lint, TypeScript, unit tests.
- Production build passed with Next.js 16.2.6.
- Initial Supabase migration exists in `sandia-marketing/supabase/migrations/20260531221000_initial_schema.sql`.
- Local dev runs on port 3001 because port 3000 is occupied by Open WebUI.

## Next Product Steps

1. Connect Supabase Cloud and apply the initial migration.
2. Populate `.env.local` in `sandia-marketing`.
3. Smoke test login and project creation.
4. Turn Phase 0 into the first guided workflow screen set.
5. Persist Phase 0 outputs into `project_phase_artifacts`, with decisions and lessons captured separately.

## Historical Decisions

- D-001 (`e258360a`) — Superseded. Original decision: build Marketing OS as a module inside pretel-os. Current decision: executable product lives in separate repo `sandia-marketing`.
- D-002 (`7f87df56`) — Phase 0 audit accepted into methodology.
- D-003 (`9215573a`) — Phase 1 audit accepted into methodology.
- D-004 (`ef0b2c75`) — Phase 0/1 alignment accepted into methodology.
- D-005 (`fe833af2`) — Phase 2 audit accepted into methodology.
- D-006 (2026-06-01) — Stack MVP locked as Next.js + Supabase Cloud + Vercel.
- D-007 (2026-06-01) — FastAPI and n8n are future insertion points, not MVP dependencies.
- D-008 (2026-06-01) — `project_members` is the membership model.
- D-009 (2026-06-06) — **Parallel multi-avatar orchestration is the core differentiator.** The product maintains N avatars in parallel, each with its own Phase 1→5 loop. Per-avatar strategy is the default; unification is an evidence-justified optimization. Reframes Phase 1 §4 multi-avatar logic.
- D-010 (2026-06-06) — **New `strategies` entity** (versioned per avatar in time). Phase 5 emits Strategy #N+1 rather than overwriting. Results/learnings/decisions/best-practices persist per strategy version. Adds `avatar_id` + `strategy_id` FKs to artifacts/decisions/lessons.
- D-011 (2026-06-06) — **Removed the "max 5 avatars" hard cap** from Phase 0 §6. Cap was an artifact of assuming a human operator; it contradicts the parallel-orchestration thesis. The 2-of-3 distinction test is retained as a *quality criterion for creating a distinct avatar*, not as a ceiling. Foundation layer (0.1–0.2.5) confirmed avatar-agnostic, sitting above the buyer persona.

## How To Start A New Chat

1. Read this file.
2. Open `C:\Users\prett\Documents\sandia-marketing`.
3. Run:

```powershell
$env:Path = "C:\Program Files\nodejs;$env:Path"
& "C:\Program Files\nodejs\npm.cmd" run verify
```

4. Read the relevant phase spec.
5. Implement the next workflow slice in the Sandi app, not inside this `pretel-os` project directory.
