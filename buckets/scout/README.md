# Bucket: scout

<!-- pretel:auto:start summary -->
**Active projects:** 0  
**Archived projects:** 0  
**Open tasks:** 0  
**Last regenerated:** 2026-04-30T19:56:16Z
<!-- pretel:auto:end summary -->

<!-- pretel:auto:start active_projects -->
## Active projects

_(none)_
<!-- pretel:auto:end active_projects -->

<!-- pretel:auto:start archived_projects -->
## Archived projects

_(none)_
<!-- pretel:auto:end archived_projects -->

<!-- pretel:auto:start applicable_skills -->
## Available skills

- **skill_discovery** — How to discover and use registered skills
- **sdd** — Spec-Driven Development process
- **vett** — Vendor Evaluation & Technology Triage framework
<!-- pretel:auto:end applicable_skills -->

<!-- pretel:auto:start recent_decisions -->
## Recent decisions (5 most recent)

_(none)_
<!-- pretel:auto:end recent_decisions -->

<!-- pretel:notes:start -->
# Scout Bucket

**Purpose.** This bucket holds the operator's W2 work at **Scout Motors** — Workflow Engineering, IT. It is the L1 context loaded by the Router when a turn is classified into `bucket=scout`.

The Scout bucket is **abstract patterns and process only**. Concrete proprietary employer data (supplier names, internal specs, organizational details, financial figures, product roadmaps) is forbidden in any location: git, database, prompts, logs, or backups. See pretel-os `CONSTITUTION §3` for the full rule and `migrations/0016_scout_denylist.sql` / `migrations/0020_scout_safety_trigger.sql` for the enforcement.

---

## Active skills in this bucket

| Skill | File | Bucket overlay (L2 context) | Purpose |
|---|---|---|---|
| `vett` | `skills/vett.md` (generic) | `buckets/scout/skills/vett_scout_context.md` | Vendor Evaluation & Technology Triage. Generic framework + Scout-specific tech stack, governance teams, compliance, data taxonomy, and presentation system. |
| `sdd` | `skills/sdd.md` (generic) | — | Spec-Driven Development — applies to all buckets. |

When the Router classifies a turn into `bucket=scout` AND the `vett` skill is loaded, the Scout overlay is loaded as L2 context alongside the generic `skills/vett.md`. The overlay supplies the values for the variables the framework leaves abstract (`{the organization}`, `{client_tech_stack}`, `{client_governance_team}`, compliance frameworks, data taxonomy, scoring deltas, presentation visuals).

---

## Key projects

| Project | Status | Notes |
|---|---|---|
| **VETT evaluations** | Active | First evaluation: Replit — April 2026, for the Operator Training System. Subsequent evaluations follow `skills/vett.md` lifecycle, scored against the Scout overlay. |
| **MTM (Manufacturing Training Module) work** | Ongoing | Voice-driven training-content workflows; consumes the Operator Training System's hybrid LiveKit + DynamoDB + Databricks + EKS architecture. |
| **Operator Training System support** | Ongoing | Architecture documented in the Scout VETT overlay §6. Evaluators must consider all four layers — LiveKit / EKS / DynamoDB / Databricks — for any tool touching this system. |

Project-level state, when it exists, lives at `buckets/scout/projects/[name]/` (lazy-loaded per `CONSTITUTION §5.6` — only the active project's L2 is loaded per turn).

---

## Data handling note (CONSTITUTION §3)

> The Scout bucket never stores proprietary employer data. Patterns are abstract and reusable. Concrete employer data is forbidden in git, database, prompts, logs, or backups.

**Operational implication for skills loaded into this bucket:**

- VETT evaluations stored under `buckets/scout/evaluations/` (when present) must contain only structural and process content. Findings about Scout's stack are allowed (the stack itself is documented in the overlay); findings that include supplier names, supplier pricing, internal specs, financials, or unannounced product details are not.
- Any commit touching `buckets/scout/` runs `.github/hooks/scout-guard.sh`. A flagged commit blocks pending operator review.
- MCP `save_lesson` calls with `bucket=scout` run the denylist check before insert; flagged content returns an error and the LLM must reformulate abstractly or cancel.

When in doubt: store the **shape of the problem and the approach**, not the specific data.

---

## References

- Generic VETT skill: `skills/vett.md`
- Scout VETT overlay: `buckets/scout/skills/vett_scout_context.md`
- Generic SDD skill: `skills/sdd.md`
- pretel-os CONSTITUTION §3 — data sovereignty rules.
- pretel-os CONSTITUTION §5 — context layering and Router behavior (L0–L4).
<!-- pretel:notes:end -->
