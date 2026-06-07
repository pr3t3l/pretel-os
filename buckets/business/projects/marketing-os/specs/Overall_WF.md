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

## Flag Registry (living contract between Phase 4 and Phase 5)

The loop's contract is a set of **flags**: Phase 4 (the measurer) raises them; Phase 5 (the optimizer) reads them and acts. **This is NOT a hardcoded enum.** Hardcoding a fixed list would train the system to only react to failure modes someone already imagined — and to force novel problems into the wrong bucket. For an AI-first product that is a self-inflicted blind spot (it is exactly what produced advisor issue M3: a flag listed but with no producer).

Instead, flags are a **living registry with three tiers** — the same shape as the `signal_rules` lifecycle already used in Phase 0:

1. **Seed heuristics (the known) — fast deterministic path.** For well-understood failure modes, Phase 4 raises a known flag and Phase 5 applies the mapped action without invoking an LLM. Cheap, auditable, covers the common case.
2. **Open diagnosis (the unknown) — forced reasoning.** When metrics move materially but **no known flag fires**, that absence is itself the meta-flag `unexplained_anomaly`. It triggers a reasoning step (Phase 5 §5.1.b): an analyst/LLM reads the raw data + the strategy's history + lessons and **hypothesizes a novel root cause**, instead of searching a list. This is how the system "thinks" when the catalog doesn't explain reality.
3. **Promotion (the bridge) — reasoning becomes structure.** When a novel root cause is validated (its action worked, or the pattern recurs), it is **promoted into the registry as a new flag** with its own producer rule. The seed list grows from observed reality; it is never the ceiling.

**Storage:** flags live inside `strategies.results_summary` (jsonb) — an **open set**, not a DB enum. Adding a new flag needs **no migration**.

**Producer-binding rule (kills M3 orphans):** every flag in the registry MUST declare a producer. A flag with no producer is invalid and cannot be referenced by Phase 5. Each flag declares four fields: `name | producer | action | re-trigger scope`.

### Seed registry (v1)

| flag | producer | action | re-trigger scope | new strategy version? |
|---|---|---|---|---|
| `ctr_falling_30pct_14d` | Phase 4 metric (FATIGUE-001) | refresh hooks/content | Phase 2 (that avatar) | yes |
| `conversion_falling_30pct` | Phase 4 metric (CONVERSION-001) | revise offer | Phase 1 (that avatar) | yes |
| `ltv_cac_below_3` | Phase 4 metric (ECONOMICS-LIVE-001) | reprice / retention / organic-only | Phase 1 or decision | yes |
| `cac_up_40pct` | Phase 4 metric (CAC-TREND-001) | fix targeting first | Phase 3, **same active version**; escalate to Phase 1 only if it persists (LOOP-004) | no (Phase 3); yes only on escalation |
| `avatar_underperforming` | Phase 4 metric (AVATAR-PERF-001) | pause avatar, reallocate budget | archive that strategy | no (archived) |
| `avatar_changed_qualitatively` | **operator** (manual observation) | re-research that avatar | **Phase 0.3↓ for that avatar only** (Foundation untouched) | yes |
| `foundation_drift` | Phase 4 metric (FOUNDATION-DRIFT-001: cross-avatar simultaneous decay / market-data shift / competitive shift) | re-research the shared base | **Phase 0.1–0.2.5, project-wide** (affects all avatars) | yes (all avatars) |
| `unexplained_anomaly` | Phase 4 metric (ANOMALY-001: material move, no known flag) | **open diagnosis** (reason → hypothesize) | depends on diagnosis; may promote a new flag | depends |

Notes:
- There is **no calendar-based flag** (no `12_months_elapsed`). Foundation is rebuilt on **evidence of drift**, never on a schedule — see Phase 0 §11.
- `cac_up_40pct` does **not** edit a strategy in place; a Phase 3 re-trigger produces a new `publish_plan` *within the same active strategy version* (the strategy entity is untouched, so D-010 holds). Only escalation to Phase 1 mints a new version.
- Phase 4 and Phase 5 both reference THIS table — neither maintains its own copy (prevents the drift that caused M3).

## Two extension patterns (so we don't hardcode the open world)

Closed enums are safe only for **states of a closed system** (semáforo `green|yellow|red`, máquina de estados `scheduled|published|failed`, `value|cta|hybrid`). For **categories of an open world** and for **thresholds whose right value depends on context**, every phase spec uses one of these two reusable patterns *by name* instead of freezing a list. The test for which applies:

> **¿Esto enumera los estados de un sistema cerrado, o las categorías de un mundo abierto?** Cerrado → enum fijo. Abierto → Pattern A. Número con valor dependiente del contexto → Pattern B.

### Pattern A — Extensible Vocabulary (for open-world categories)
Use when a field classifies something that could have members nobody enumerated (trigger types, bonus types, KPI types).

- **Seed** — a short list of the common, well-understood members (the 80%).
- **Escape** — a literal `other` value + a required `*_custom_description` free-text field. A case that doesn't fit is captured, never forced into the wrong bucket, never orphaned (this is what would have prevented M3).
- **Promotion** — when the same `other` description recurs **≥3 times across the project AND passes a review** (operator or automated dedup), it is promoted to a named member of the seed. Same lifecycle as Phase-0 `signal_rules` and the Flag Registry above.

Governance (so registries don't bloat — "muerte por mil campos abiertos"):
- Promotion is **not** automatic on first sight; it costs ≥3 repetitions + a review. Otherwise every one-off becomes a permanent category and the vocabulary rots.
- **Sequencing:** openness pays off most *once there is data to promote from*. Pre-PMF, `seed + other` (capture only) is enough; promotion runs later when volume exists. Don't ask the LLM to invent categories with no grounding early.

### Pattern B — Context-Adjusted Threshold (for numbers whose right value depends on context)
Use when a cutoff (a ratio, a percentage) is a reasonable default but the correct value varies by business model / market / channel (ratio_target, LTV:CAC, Vaynerchuk ratio).

- **Default by segment** — the threshold is a *table keyed by the dimension that actually moves it* (business_type, delivery_format, channel), not one global constant.
- **Evidence adjustment** — the default is adjusted by evidence the system already has (`competitive_landscape` from Phase 0, measured fatigue from Phase 4). If the default contradicts the evidence, that conflict triggers reasoning (the open-diagnosis layer) — it is not applied blind.
- **Alarm stays on** — near or past the threshold the system *reasons the context with hard evidence* (margin, recurrence, stage) before a verdict, but the alert is never silently switched off. **Softening the verdict ≠ removing the detector.** (Guards against the `EVIDENCE-001` confirmation-bias trap: "let's reason away the red" is exactly what self-deception looks like.)

### Pattern C — Evolving Schema (the artifact JSON shape itself is a seed, not a frozen contract)
Use for the **structure** of every phase artifact (`business_context.json`, `buyer_persona.json`, `offer_spec.json`, …). Pattern A opens enum *values* and Pattern B opens *thresholds*; Pattern C opens **which fields exist at all**.

Why: the JSON this reference build produces is **v1 of one team's worldview**. Other clients, other models, and the operator's own future learning will bring different focus and improvements. Freezing the schema locks the product to today's blind spots. The schema must improve from real usage — **across all phases**, not just Phase 0.

- **Seed + version** — every artifact carries `schema_version` (already on `project_phase_artifacts` from M0) and a `metadata` jsonb (also from M0) where not-yet-promoted fields live. The documented JSON is the *seed* (v1).
- **Capture before promote** — a field/question nobody anticipated is captured in `metadata` first (the "other" of schemas). When it recurs **≥N times across projects/users AND passes review**, it is promoted to a first-class field and `schema_version` bumps. Same lifecycle as the Flag Registry and `signal_rules`.
- **Outcome-driven evolution (the learning loop)** — every interaction in every phase writes lessons; downstream results (Phase 4 `results_summary`) reveal which questions/fields actually predict good strategies. Predictive fields get reinforced/added; dead fields get deprecated. The schema *learns what matters*.
- **Tenancy** — distinguish a client's **local schema extensions** (their `metadata` fields) from **globally promoted core** fields. Versioned and reconciled, never one frozen shape imposed on everyone.
- **Governance** — promotion has a cost (≥N + review), sequencing (capture pre-data, promote post-data), and deprecation of unused fields — so the schema grows from reality without bloating.

This makes every artifact JSON a **living contract that improves with usage**, which is the operator's explicit requirement: the system *and* the JSON get better with every user interaction, in every phase.

Phase specs tag each extensible field as **[Extensible Vocabulary]** or **[Context-Adjusted Threshold]**, and every artifact JSON is governed by **[Evolving Schema]** (seed + `schema_version` + learning loop), so the patterns are explicit at the point of use.

## Data Privacy & the Learning Boundary

The learning loop above (Patterns A/B/C, flag promotion, signal-rule promotion) **requires** a privacy boundary — without it, "the system learns from interactions" is a data leak. This section is load-bearing for everything that promotes knowledge, in every phase.

**The rule:** *only abstracted patterns cross the boundary into global learning. Raw client data never does.*

**Three tiers by sensitivity:**

| Tier | Contents | Rule |
|---|---|---|
| **T1 — Raw client data** | the client's idea, *their* customers, numbers, PII, their copy | Tenant-scoped, encrypted, RLS. **Never leaves** the tenant boundary. |
| **T2 — Tenant artifacts** | their `business_context.json`, avatars, strategies, results | Private to the tenant, typed. Does **not** feed the global model directly. |
| **T3 — Global learning** | only **de-identified, aggregated** patterns | The only thing that improves the system for everyone. |

- **What rises to T3 (abstract, non-identifying):** "a custom `trigger_type` 'social proof' recurred across N tenants → promote", "for B2C reflexive + subscription, refreshing hooks every 14d worked". **What never rises:** client name, their real customers, their numbers, their copy.
- **Promotion-to-global rule:** promotion to T3 requires **de-identification + cross-tenant aggregation (≥N distinct tenants)** — NOT ≥N within a single tenant. This stops one client's pattern from leaking as "global learning". (Distinct from the within-project promotion that Patterns A/B/C use for a *tenant's own* schema/vocabulary, which stays in T2.)

**Mechanisms (all already prototyped in pretel-os / present in the stack):**
- **RLS per tenant** — the Supabase schema already enforces it (`is_project_member`, `project_role_for_user`).
- **PII pseudonymization** before anything is eligible for T3 — pseudonymize > generic tokens (preserves signal). Spanish needs explicit config (Presidio `es_core_news_md`).
- **Defense in depth** — a guard that blocks raw client specifics from entering the global store, mirroring the Scout guard (pre-commit hook + MCP denylist + DB trigger).
- **Consent / opt-in** per tenant for contributing their abstractions to T3.
- **Data residency / compliance** — international scope (US/Europe/LatAm) ⇒ GDPR applies to Europe; vet provider server locations.

**Why this is reassuring, not novel:** pretel-os already lives this pattern. The **Scout bucket** = "abstract patterns only, never concrete employer data" with defense in depth; **cross-pollination** = abstracted lessons flow across buckets while raw data does not. Sandi's multi-tenant privacy is that same pattern applied to SaaS — define the principle now, implement (encryption, Presidio pipeline, consent UI) at build time.

## Portable Human Connection & Per-Project Agent Memory

**Loyalty thesis:** method *is* connection — *how* Sandi helps (Socratic, one-step, decides-with-reasons, celebrates) is what creates the bond. The moat is the **relationship/memory**, not features. The engine is **Self-Determination Theory** (Deci & Ryan): hit **autonomy** (the user decides), **competence** (they learn and win), and **relatedness** (they feel understood) on every interaction.

### A. Portable Human Connection (model-agnostic)
Anthropic bakes character *into the model* (Constitutional AI / character work). Sandi can't rely on that across OpenAI / DeepSeek / Kimi / etc. — so the humanity lives in the **system layer**, making the model interchangeable plumbing. Four portable layers:
1. **Character spec (a SOUL)** — explicit persona: archetype (Sage/Mentor), values, voice, never-dos. In the system prompt + few-shot exemplars, *any* model performs it. Mirrors pretel-os `SOUL.md` (ADR-22). → `specs/SOUL_setup_agent.md`.
2. **Interaction patterns** — the 5 movements, reflective listening, normalize, celebrate, autonomy-support. Pure orchestration, model-independent.
3. **Memory** — the model forgets between calls; the *system* remembers. The felt relationship **is** the memory layer (§D).
4. **Character evals** — calibrated LLM-as-judge (LIDR); run on every model swap so the persona survives the migration.

Named techniques (for the spec): SDT; Motivational Interviewing / Rogerian reflective listening; **rupture-and-repair** (a repaired mistake builds *more* trust than never erring); peak-end rule (end each session on a win); cognitive-load (one thing at a time); glass-box honesty.

### B. Glass-Box (no black box)
Every conclusion shows **source/method → reasoning → jargon-in-plain-language**; inferences are labeled as inferences; the system states what it could *not* verify. Builds trust. Reconciles with the internal plan in §D: *hidden-by-default ≠ secret* — anything is available on demand.

### C. Adaptive Education + `user_knowledge_profile`
Profile the user's level per concept (novice/intermediate/expert); teach **just-in-time** (1-line micro-lessons in context); **level up across projects/campaigns**. Education is both the market wedge (46% of SMBs lack a strategy) and a retention engine (the user becomes a better marketer *because of* Sandi).

### D. Per-Project Agent Memory (mirror of pretel-os)
Each project/run gets a **brain like the one pretel-os gives Claude**:

| Layer | Holds | pretel-os analog | User-visible? |
|---|---|---|---|
| Project doc | what this project is | README + CLAUDE.md | yes |
| **Action plan** (internal, **mutable**) | where we are / what's next / what changed | tasks.md / SESSION_RESTORE / plan.md | **not by default** (progressive disclosure); on demand |
| Lessons | what we learned | `lessons` | on demand |
| Best practices | what works (promoted) | `best_practices` | on demand |
| Decisions | what we decided + why | `decisions` | on demand (glass-box) |
| Working state | typed brief + history | `ProjectFoundationBrief` | yes (panel) |
| User profile | knowledge level | (new) | implicit |

Rules (operator-defined): the **action plan is internal** (not pushed at the user — that's what progressive disclosure protects), **mutable** (revised as reality unfolds — ties to the Phase 5 loop, `foundation_drift`, and Pattern C), and **not secret** (glass-box: shown if asked). Everything **typed and persisted**, never a free-text blob the model "remembers" (LIDR memory anti-patterns). This per-project memory feeds the global T3 learning **only** through the privacy boundary (de-identified + cross-tenant).

**Recursive elegance:** Sandi gives every user-project the same memory architecture the operator built for pretel-os. Proven pattern, re-applied.

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
- `spec_Phase_0_Setup_Agent.md` — the conversational guided delivery of Phase 0 for non-expert users (4 movements, 0.1 script, [Evolving Schema]).
- `spec_Phase_1_Oferta.md` — offer construction (+ strategy birth, D-009/010).
- `spec_Phase_2_Contenido.md` — content planning (anchored to strategy).
- `spec_Phase_3_Distribucion.md` — publish, tracking, targeting (per strategy).
- `spec_Phase_4_Medir.md` — measurement, unit economics, writes `results_summary`.
- `spec_Phase_5_Ajustar.md` — the loop: flag→action→re-trigger, emits Strategy #N+1.

## Phase ↔ Supabase `artifact_phase` mapping

The implementation (`sandia-marketing`) enum `artifact_phase` maps to methodology phases. The **M0 AI-first rebuild** (`20260602000000_ai_first_extension.sql`) introduced the canonical values below; the legacy values (`discovery`, `strategy`, `production`, `distribution`, `review`) remain valid as **deprecated aliases** — the runtime uses only the canonical ones.

| Methodology phase | canonical `artifact_phase` | legacy alias |
|---|---|---|
| (pre-Phase-0 conversational brief — Setup Agent) | `setup` | — |
| Phase 0 — Research + ICP | `phase_0` | `discovery` |
| Phase 1 — Oferta | `phase_1` | `strategy` |
| Phase 2 — Contenido | `phase_2` | `production` |
| Phase 3 — Publicar / Distribuir | `phase_3` | `distribution` |
| Phase 4 — Medir | `phase_4` | `review` |
| Phase 5 — Ajustar | `phase_5` | `review` |

## Implementation migrations (`sandia-marketing/supabase/migrations/`)

- `20260531221000_initial_schema.sql` — projects, members, phase_artifacts, decisions, lessons, audit (+ RLS).
- `20260601011000_repair_initial_schema_idempotent.sql` — idempotency repair of the initial schema.
- `20260602000000_ai_first_extension.sql` — **M0 AI-first rebuild**: canonical `artifact_phase` (`setup`, `phase_0..phase_5`), `artifact_status` + `metadata`/`schema_version`/`supersedes` on `project_phase_artifacts`, and new tables `profiles`, `project_conversations`, `project_llm_calls`, `project_prompt_versions` (conversational Setup Agent plumbing).
- `20260606120000_avatars_strategies.sql` — **buyer_personas, avatars, strategies** (with `covers_avatar_ids`, versioning, `superseded_by`, `results_summary`) + `avatar_id`/`strategy_id` FKs on artifacts/decisions/lessons + RLS + audit triggers. Runs on top of the AI-first base; additive and reconciled (distinct enum values + columns). Implements D-009/D-010/D-011.

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
- D-012 (2026-06-06) — **Living Flag Registry** (replaces hardcoded flag enum). Seed heuristics (fast path) + open-diagnosis branch (`unexplained_anomaly` → reason the root cause) + promotion (validated novel causes become new flags). Producer-binding rule kills orphan flags (advisor M3). Added CONVERSION-001 (advisor critical), CAC-TREND-001 (M3), fixed in-place ambiguity (M1), Foundation re-trigger scope avatar-vs-project (M4), phase_4/phase_5 labels (M2). **Removed all calendar-based refresh** (no `12_months_elapsed`/6-month); Foundation rebuilds on `foundation_drift` evidence only (Coca-Cola principle: review constantly, rebuild on evidence).
- D-013 (2026-06-06) — **Two extension patterns** to avoid hardcoding the open world: **Extensible Vocabulary** (seed + `other`+description + promotion ≥3×+review) and **Context-Adjusted Threshold** (default-by-segment + evidence adjustment + alarm-stays-on). Unifying test: closed-system states → fixed enum; open-world categories → Pattern A; context-dependent numbers → Pattern B. Governance: promotion has a cost (no bloat); openness sequenced after data exists.
- D-017 (2026-06-07) — **Portable Human Connection & Per-Project Agent Memory**. Sandi's humanity lives in the system layer (character SOUL + interaction patterns + memory + character evals), not the model — portable across any LLM provider. SDT is the loyalty engine; glass-box + adaptive education (`user_knowledge_profile`) folded in. Each project/run gets a pretel-os-style brain: project doc + **internal mutable action plan** + lessons + best-practices + decisions + typed working state + user profile. Action plan is internal (progressive disclosure), mutable (Phase 5 loop / foundation_drift / Pattern C), not secret (glass-box). New artifact `specs/SOUL_setup_agent.md`. Mirrors pretel-os SOUL.md + memory architecture.
- D-016 (2026-06-07) — **Data Privacy & the Learning Boundary**. Three tiers (T1 raw client data: tenant-scoped/encrypted/RLS, never leaves; T2 tenant artifacts: private; T3 global learning: de-identified + aggregated only). Promotion to global requires cross-tenant aggregation (≥N distinct tenants) + de-identification — raw data never crosses. Load-bearing for the Pattern A/B/C learning loop. Mechanisms (RLS, PII pseudonymization, defense-in-depth guard, consent, residency) already prototyped in pretel-os (Scout bucket + cross-pollination). Principle now, implementation at build.
- D-015 (2026-06-07) — **Setup Agent** (conversational guided Phase 0 for non-experts) + **Pattern C — Evolving Schema**. Validated wizard-guided interface against the full LIDR corpus (best practices "Espectro de interfaces", "prompt es artefacto de software", "pre-flight + Step N of M"; lessons transaccional-vs-conversacional, memoria tipada, CAG, costos). 4-movement behavior contract; jargon hidden from user; flag calibration. Per operator: artifact JSON schemas are seeds, not frozen — they evolve via `schema_version` + capture-in-`metadata` + outcome-driven learning loop across ALL phases. New spec `spec_Phase_0_Setup_Agent.md` with the 0.1 script formalized.
- D-014 (2026-06-06) — Applied D-013 to 7 rigidity zones: trigger `type` (R-1), `hormozi_category` (R-2), `ratio_target` (R-3), LTV:CAC threshold (R-4, table by business model, alarm preserved), Vaynerchuk ratio (R-5, per-channel adjustable by measured fatigue), pillar `kpi_primary` (R-6), brand `archetype` (R-7, primary+secondary hybrids; stays closed — 12 Jungian archetypes are exhaustive). Did NOT touch healthy closed enums (semáforo, machine states, `value|cta|hybrid`, evaluator types, structural minimums).

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
