# Session handoff — 2026-05-10 (R4 completed, pre first manual cycle)

**For**: next Claude Code session opened in `buckets/business/projects/marketing-os/`
**From**: session that drafted Phase 2 + integrated audit R4 + promoted specs from operator's Desktop into this repo
**Status at close**: 4 specs + audit trail persisted; 0 manual cycles executed yet.

---

## What this file is

Continuity context. CLAUDE.md gives you the architecture baseline; this file gives you the **delta of the previous session** so you don't re-read 1000 conversation messages to pick up. It is **not** a lesson or decision (those go to pretel-os). It is operational scratch — replace or archive when the next handoff is written.

---

## Where the work stands

### Specs
All four spec files in `specs/` are post-audit and persisted:
- `Overall_WF.md` — v2, includes audit history R1–R4 + decision IDs D-001 to D-005
- `spec_Phase_0_Research_ICP.md` — v1.5 + R3 alignment patches (target_cac_usd persisted, pricing_tiers structured)
- `spec_Phase_1_Oferta.md` — v1.5 + R3 alignment patches (forces in ALL avatars, sub-step 1.4.0 language_packs, comparable in core_deliverable, urgency.aligned_with_trigger)
- `spec_Phase_2_Contenido.md` — **v1.1** post-R4 (force_coverage per pillar, JTBD anchor, Vaynerchuk ratio, displacement_inheritance, V1/V2 disambiguation in sub-step table, Pinterest in channel_function lookup)

### Pretel-os state (queryable, do not re-create)

**5 decisions** in `business/marketing-os`:
| ID | UUID | What |
|---|---|---|
| D-001 | `e258360a` | Marketing OS as module inside pretel-os |
| D-002 | `7f87df56` | Audit R1 — Categoría A integrated into Phase 0 v1.5 |
| D-003 | `9215573a` | Phase 1 spec v1.5 |
| D-004 | `ef0b2c75` | Audit R3 — Phase 0↔1 alignment |
| D-005 | `fe833af2` | Phase 2 spec v1.0 + R4 integrated v1.1 |

**25 best_practices** with `scope: project:business/marketing-os`, `domain: workflow`:
- 11 prior signal rules (Phase 0 + Phase 1: DEMAND-001/002/003/004, EVIDENCE-001/002, ECONOMICS-001, VALUE-001/002, STACK-001/002, OFFER-001, PRICING-001) + 2 lookup tables (`ratio_target`, `margin_target_pct`) — registered before this session
- 14 Phase 2 signal rules (VOICE-001, CONTENT-001/002/003/004/005, ATOMIZATION-001, FORCES-001, NEGATIVE-001, COVERAGE-001, TRIGGER-ALIGN-001, HANDOFF-001, REINFORCE-001, VAYNER-001) — registered this session
- 2 Phase 2 lookup tables (`channel_function`, `atomization_ratio_minimum_per_anchor_format`) — this session
- 9 hook templates (problem_agitate_solve, before_after_bridge, aida, curiosity_gap, pattern_interrupt, contrarian, most_people_think, identity_callout, specific_number) — this session
- 1 prior best_practice BP-001 (`fea3dbd8`) — manual-before-automatic gate

**1 lesson** with tag `marketing-os`:
- `17112600` — pretel-os `domain` enum constraint (`workflow|process|convention|communication` only, NOT `signal-rule`). Always honored: signal rules persisted as `domain: workflow` with `SIGNAL-RULE` prefix in title.

To rehydrate: `decision_search(query='marketing-os', bucket='business')`, `best_practice_search(scope='project:business/marketing-os')`, `search_lessons(tags=['marketing-os'])`.

---

## Where we are in the lifecycle

```
Phase 0 spec ✅  Phase 1 spec ✅  Phase 2 spec ✅  Phase 3-5 specs ⏳
Manual cycles run: 0 (Declassified primero per Overall_WF §9 priority)
```

Per BP-001 (`fea3dbd8`), next step is **manual execution of Phase 0 with a real product**, not drafting Phase 3–5 specs. The spec drafting outpaces the manual practice; rebalance toward execution.

---

## Concrete next step (when this session opens)

**Arrancar el primer ciclo manual de Phase 0 con Declassified Cases**.

Concrete first action: drafting `runs/declassified/cycle_1_2026-05-10/phase_0/product_brief.json` (the v1.5 input contract that wakes up Phase 0). Operator interview style — the next Claude session asks the operator the questions to fill the brief: product description, expected_ltv_usd, expected_repeat_rate, marketing_objective, operator_hypotheses (audience + problem with critical flags), constraints (languages, geographies, research budget hours/USD), and the new R3 fields `target_cac_usd` (or null for autocalc) + `target_cac_basis`.

Then walk sub-step 0.1 (Business Context Gate, manual operator declaration), then 0.2, etc., per the spec. Each sub-step closes with `decision_record` calls into pretel-os when warranted, plus filesystem writes to `runs/declassified/cycle_1_2026-05-10/phase_0/`.

---

## Conventions established this session (worth preserving)

These are how we've been operating; they are not codified in pretel-os but should be honored in subsequent sessions for coherence:

1. **Audit rounds are versioned R1, R2, R3, R4...** — header `Audit references` block in each spec lists them with date + decision UUID. Never overwrite, always append.
2. **Spec versions bump** when an audit changes them: Phase 0 was v1.5 after R3, Phase 2 was v1.0 then v1.1 after R4. Keep `Status:` line in header current.
3. **Decisions follow D-NNN naming** in `Overall_WF §10` table, with the `decision_record` UUID in parens. New decisions append; never renumber.
4. **Signal rules live as `domain: workflow` best_practices** with prefix in title (`SIGNAL-RULE NAME-NNN: ...`), `applicable_phase: phase-X.Y` in tags. Lookup tables = same pattern with prefix `LOOKUP-TABLE name: ...`. Hook templates = `HOOK-TEMPLATE name: ...`. (Per lesson `17112600`.)
5. **Pre-gate checks are numbered, never reorder** — adding a check appends with a new number; existing numbers stay stable so other docs that reference "G-Phase-2-PRE check 7" don't break.
6. **"reinforce vs resolve" pattern** (R4 A1-ISSUE-1, decision D-005): when downstream phase consumes upstream output, distinguish between "what upstream already covered (reuse phrasing)" vs "what upstream explicitly delegated to downstream (attack with own copy)". Apply this pattern when drafting Phase 3–5 specs.
7. **Doble persistencia** (filesystem + pretel-os): structured artifacts that need cross-product/cross-cycle querying live in both — full JSON in filesystem, key fields in Postgres via MCP. `brand_voice.json` is the reference example (R4 A2-ISSUE-3).
8. **No "(pendiente registrar)" prose** in spec docs. If a decision exists, persist it in pretel-os and reference its UUID. The Overall_WF doc lied through R1, R2, R3 with stale "(pendiente registrar)" lines until R4 cleanup — anti-pattern, do not reintroduce.
9. **README.md never hand-edited** — it's auto-generated by `regenerate_project_readme(bucket=business, slug=marketing-os)`. After substantive spec/decision changes, regenerate.

---

## Things deferred (intentionally not done this session)

| Item | Why deferred | When to revisit |
|---|---|---|
| A1-ISSUE-9 voice versioning per asset | Capture as lesson during cycle 1 | First Phase 2 cycle |
| A1-ISSUE-10 ICP in B2B copy | Capture as lesson when Alfredo-as-freelance starts | When B2B product enters |
| A1-ISSUE-5 email sequences | V2 when email becomes a real channel | Post Declassified cycle 2+ |
| A1-ISSUE-6 pre-PMF rule combined with `validation_status` | Refinement at second product | When velas hija or freelance enters |
| Phase 3 / 4 / 5 specs | BP-001 blocks: do manual cycles first, then spec the agent from observed practice | After 1+ Declassified cycle through Phase 2 |
| Sub-workflow skills (`content-pillars-builder`, `content-atomizer`, `hook-library-generator`, `awareness-mix-suggester`, `value-equation-optimizer`, `offer-stack-builder`, `keyword-research-pipeline`) registered as MCP tools | V2 milestone, after ≥3 manual cycles each phase | Per BP-001 |
| n8n workflow for sub-step 0.2 Capa 2 (Google autocomplete + PAA + Reddit scraping) | Built when first cycle reaches sub-step 0.2 | During first Phase 0 manual cycle |
| Object storage for binary creative assets | Not needed yet — Declassified cycle 1 is text-heavy | When Phase 2 produces quote graphics or Phase 3 publishes media |
| Limpiar `C:\Users\prett\Desktop\Marketing-os\` (carpeta vacía huérfana) | Bash tenía cwd ahí, falló rmdir | Cualquier sesión nueva puede borrarla |

---

## Open infra context (relevant for next session)

- Repo cloned at `C:\Users\prett\Documents\pretel-os\` on operator laptop, working tree clean as of commit `4cff74c`.
- Server has the same repo with hourly auto git-sync (commit `ab782c6` "[Git-sync] Hourly pretel-os-gitsync.{service,timer}"), so files written here propagate to server within ~1h. Pretel-os MCP runs on server and reads filesystem from there.
- Git identity configured globally on Windows side: `prettel1@hotmail.com / pr3t3l`. Commits from PowerShell or Bash tool work without per-repo setup.
- WSL has its own separate git config (`/home/prettel_wsl/.gitconfig`) — they do NOT share. If operator commits from WSL it'll be `prettel_wsl@PretelMachine.(none)` unless WSL is configured separately.

---

## What to read first when this session opens (5 min)

1. `CLAUDE.md` (auto-loaded by Claude Code) — architecture baseline
2. This file — session continuity
3. `specs/Overall_WF.md` — full lifecycle map if you need it (else skip; CLAUDE.md summarizes)
4. The relevant phase spec when the operator picks one to execute

You don't need to re-read Phase 1/2 specs unless the operator says "we're working on Phase N today". Pretel-os queries are cheaper than re-reading specs in full.
