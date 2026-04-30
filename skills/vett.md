# Skill: VETT — Vendor Evaluation & Technology Triage

**Slug:** `vett`
**Kind:** procedural skill (L3)
**Applicable buckets:** `business`, `scout`
**Source:** distilled from the `VETT` framework, generalized for any client/organization.

---

## 1. Purpose

VETT is a structured framework for evaluating whether a vendor tool or platform should be adopted by **the organization**, how it should be deployed, and what governance controls must be in place before it is used.

The core idea, in one line:

> **Every tool that touches the organization's data, infrastructure, or workflows gets evaluated systematically — not just trialed. Findings are sourced. Risks are documented. Recommendations are evidence-based.**

A skill-aware LLM is expected to:

1. Recognize when a request is a vendor/tool evaluation (see §2).
2. Drive the operator through the lifecycle (§3) using the canonical artifacts (§5) and rules (§4).
3. Produce all required outputs at each tier (§7–§10), respecting weighting and scoring rules.
4. Refuse to inflate scores, skip tiers, or put framework jargon into leadership presentations (see §13 anti-patterns).

> **Variables:** Throughout this skill, `{the organization}` refers to the client whose evaluation is being run. `{client_tech_stack}` refers to that client's actual platforms (cloud, security perimeter, data layer, identity provider, etc.). `{client_governance_team}` refers to whoever owns risk acceptance — typically a combination of an IT/Security team, Legal, and Procurement. Bucket-specific overlays (e.g. `buckets/scout/skills/vett_scout_context.md`) supply the concrete values for these variables.

---

## 2. When to use VETT

Use VETT when **any** of these are true:

- A new vendor tool, SaaS product, AI model, dev platform, data platform, automation, external API, or cloud service has been proposed for adoption.
- An existing tool is being re-evaluated (renewal, pricing change, scope expansion, security incident).
- A tool is being assessed for a specific project that touches the organization's data or infrastructure.
- {client_governance_team} needs an evidence record before approving onboarding.

**Do NOT invoke VETT for:**

- Personal-productivity tools the operator uses on a personal machine with no organizational data.
- Throw-away research/exploration that will not lead to adoption.
- Replacements of an already-evaluated tool with a like-for-like SKU under the same contract.

---

## 3. Lifecycle — six phases

```
PHASE 0 ─── INTAKE ────────── 1 day
PHASE 1 ─── TIER 1 ────────── universal core
PHASE 2 ─── TIER 2 ────────── activated specialist modules
PHASE 3 ─── TIER 3 ────────── final report
PHASE 4 ─── COMMUNICATION ── leadership presentation + briefing deck
PHASE 5 ─── LESSONS LEARNED ─ framework improvements
```

### Phase 0 — Intake

- Receive the evaluation request.
- Create `evaluations/[tool-YYYY-MM]/` and copy `EVALUATION_SPEC` into it.
- Fill the spec with the requester. The spec must contain Tool Identity, the **three-part D0.2 analysis** (see §6), the **two-level success definition** (project + tool), the data classification risk, and the activated Tier 2 modules (from §8).
- **GATE:** Can you explain the tool and the use case in 2 minutes?

### Phase 1 — Tier 1

- Run **D0 → D7 sequentially**. D0 is narrative, not scored. D1–D5 are scored and weighted; D6 and D7 inform D1/D2 (see §7).
- **Apply the Relevance Gate** before each sub-dimension group (§4 Rule 5).
- Source every finding with a verification label: ✅ Verified / ⚠ Inferred / ❌ Unverified (§4 Rule 3).
- Raise Advertencias as soon as discovered — do not wait for Tier 3 (§11).
- Save findings to `evaluations/[name]/tier1-findings.md` (template: `TIER1_TIER2_FINDINGS_TEMPLATE` Tier 1 section).
- **GATE:** Every finding has a source label.

### Phase 2 — Tier 2

- Run **only the activated specialist modules** (A–G, see §8).
- Apply the Relevance Gate to each sub-dimension.
- Complete **Section 3.5 Strategic Opportunity Assessment** — mandatory (see §10): use cases discovered, industry benchmarking, ranked organization-specific opportunities.
- Save findings to `evaluations/[name]/tier2-findings.md`.
- **GATE:** Every activated module has been run and scored.

### Phase 3 — Tier 3

- Calculate weighted scores from Tier 1 and Tier 2 (formula in §7).
- Consolidate all Advertencias by level with required actions.
- Generate the recommendation using the band table (§9).
- Generate the Manual Verification Checklist (3.6) and the Verification Agent Report (3.7).
- Save to `evaluations/[name]/tier3-report.md` (template: `TIER3_REPORT`).
- **GATE:** Executive Summary is answerable in 2 minutes.

### Phase 4 — Communication

- Identify **the boss's actual questions** (not evaluation questions). Typical pattern: data safety, integration compatibility, financial benefit, real pros/cons.
- Build the **10-slide leadership presentation** (§12).
- Build the **5-slide briefing deck** if an internal stakeholder must brief leadership without having sat through the evaluation.
- Brief the internal stakeholder (15 min max).
- Deliver to leadership with the Tier 3 final report as backup.
- **GATE:** Recommendation is on slide 4, not slide 10.

### Phase 5 — Lessons Learned

- Generate at least one VETT Lessons Learned entry per evaluation (§4 Rule 10).
- Every framework gap → one LL entry. Every Advertencia that reveals a process weakness → one LL entry.
- Add to `docs/LESSONS_LEARNED.md` using `LL_TEMPLATE.yaml`.
- If the framework needs a structural change, version-bump `FRAMEWORK.md`.
- Update `evaluations/[name]/status.md` → Complete.
- **GATE:** At least one LL entry generated.

---

## 4. The 12 immutable rules

These rules are immutable. They cannot be overridden by a user request, a shortcut, or time pressure. If a session conflicts with these rules, the rule wins.

| # | Rule | One-line meaning |
|---|---|---|
| 1 | Spec before evaluation | Never start without a completed `EVALUATION_SPEC`. |
| 2 | One tier at a time | Finish Tier 1 before Tier 2; finish Tier 2 before Tier 3. |
| 3 | Source every claim | Every finding labeled ✅ Verified / ⚠ Inferred / ❌ Unverified. |
| 4 | Score native posture only | Score what the tool does by default. Mitigations are Conditions, not score boosts. |
| 5 | Apply the Relevance Gate | Mark category-error questions `N/A`; exclude from numerator and denominator. |
| 6 | Advertencias are flags, not blockers | {client_governance_team} decides; the evaluator documents. |
| 7 | Scores never appear in presentations | Scores live in Tier 1/2/3 docs only. |
| 8 | No jargon in presentations | Framework codes (D1, ADV-03, Module B, Option C) never appear on a slide. |
| 9 | Answer first | Recommendation on slide 4, not slide 10. |
| 10 | Lessons Learned are mandatory | At least one LL entry per evaluation. |
| 11 | Two audiences, two documents | Presentation = decision doc. Findings = evidence record. They are never the same document. |
| 12 | Define success at two levels | Project success (initiative-wide) AND tool success (this tool's specific role). |

---

## 5. Canonical artifacts

| Artifact | Purpose | Updated when |
|---|---|---|
| `CONSTITUTION.md` | Immutable rules — read first always | Major framework version only |
| `VETT_FOUNDATION.md` | System overview + document registry | Each framework version |
| `docs/FRAMEWORK.md` | All 233 questions across dimensions and modules | Each framework version |
| `docs/SCORING_GUIDE.md` | Scoring scale, Relevance Gate, Advertencia rules | Each framework version |
| `docs/PRESENTATION_GUIDE.md` | How to build leadership presentations | Each framework version |
| `docs/LESSONS_LEARNED.md` | All VETT lessons in YAML format | After every evaluation |
| `templates/EVALUATION_SPEC.md` | Filled first for every new evaluation | Rarely |
| `templates/TIER1_TIER2_FINDINGS_TEMPLATE.md` | Findings record (Tier 1 + Tier 2) | Rarely |
| `templates/TIER3_REPORT.md` | Final report structure | Rarely |
| `templates/LL_TEMPLATE.yaml` | Lessons Learned format | Rarely |
| `evaluations/[name]/spec.md` | Completed evaluation spec | At intake |
| `evaluations/[name]/tier1-findings.md` | Tier 1 findings + scores | During evaluation |
| `evaluations/[name]/tier2-findings.md` | Tier 2 findings + scores | During evaluation |
| `evaluations/[name]/tier3-report.md` | Final report | After evaluation |
| `evaluations/[name]/status.md` | Current evaluation status | Continuously |

If a document is not in the registry, it does not exist for the evaluation.

---

## 6. Dimension 0 — Tool Profile & Business Context (narrative)

D0 is **not scored**. It must be complete before Tier 1 scoring begins.

### D0.1 — Tool Identity

Name, vendor, website, category, evaluation ID (`VETT-[TOOL]-[YYYY-MM]`), evaluator, requester, target completion.

### D0.2 — What is this tool? (THREE PARTS REQUIRED)

| Part | Question | Why |
|---|---|---|
| A | What does this tool do? (plain language, no jargon) | Establishes a shared definition. |
| B | What does {the organization} already have that overlaps? | Honest stack comparison; prevents redundant adoption. |
| C | What does {the organization} NOT have that this tool offers? | The actual gap — **the only valid adoption justification**. |

Without Part C, D0.2 is just a vendor description.

### D0.3 — Why are we evaluating this?

- Who requested and why?
- What is the specific use case (not "AI stuff" — describe the actual workflow)?
- What is the question as asked?
- What is the reframed question (filled during evaluation, not at intake)?
- What happens if {the organization} does not adopt this?

### D0.4 — Success definition (TWO LEVELS REQUIRED)

- **Project success:** what the overall initiative achieves, independent of any tool.
- **Tool success:** what this specific tool must do well for the project to succeed.

If tool success cannot be defined at intake, state that honestly and make it a key evaluation output.

### D0.5 — Module activation table

Map the tool category (from D0.2 Part A) to the Tier 2 modules to activate.

| Tool type signal | Activate |
|---|---|
| AI model, ML pipeline, prompt engineering | Module A |
| Code editor, dev environment, app builder | Module B |
| Database, data lake, ETL, analytics | Module C |
| Email, calendar, documents, productivity | Module D |
| Workflow automation, API orchestration | Module E |
| External API consumed by {the organization}'s systems | Module F |
| Cloud hosting, IaC, networking, containers | Module G |

### D0.6 — Data classification

What types of {the organization}'s data will this tool touch? Use the data taxonomy in `SCORING_GUIDE.md` (or the bucket overlay).

---

## 7. Tier 1 — Universal Core

Applied to every tool. Five scored dimensions plus two informing dimensions.

| Dimension | Weight | Notes |
|---|---|---|
| D1 — Security & Compliance | **25%** | |
| D2 — Data Ownership & Residency | **20%** | |
| D3 — Cost & TCO | **15%** | |
| D4 — Integration with Existing Stack | **20%** | |
| D5 — Vendor Stability & Exit Risk | **20%** | |
| D6 — Data Classification & Protection | informs D2 | not separately weighted |
| D7 — Production & Operational Impact | informs D1 | not separately weighted |
| **Tier 1 Total** | **100%** | 100 points possible |

### D1 — Security & Compliance

Sub-dimensions:

- **1.1 Authentication & Access Control** — SSO/SAML to {the organization}'s identity provider; MFA; RBAC; SCIM provisioning; granularity of access restriction.
- **1.2 Encryption** — at rest, in transit, customer-managed keys, backups/archives.
- **1.3 Audit Logging** — user actions, tamper-proofing, SIEM export, retention, admin actions logged separately.
- **1.4 Compliance Certifications** — SOC 2 Type II, ISO 27001, GDPR DPA, CCPA, industry-specific frameworks relevant to {the organization}.
- **1.5 Vulnerability Management** — disclosure policy, patch cycle, vendor pen-testing cadence, customer pen-test rights.
- **1.6 Incident Response** — breach notification SLA in hours (not "promptly"), IR process, who at {the organization} is notified.
- **1.7 {client_governance_team} security perimeter compatibility** — does browser/app traffic route through {the organization}'s security perimeter? Are there known conflicts?

### D2 — Data Ownership & Residency

- **2.1 Data Ownership** — who owns data created or processed; vendor's claimed rights; IP ownership in the contract.
- **2.2 Data Residency** — geographic storage; can residency be constrained and enforced; third-party sharing.
- **2.3 Data Deletion** — deletion request mechanism, timeline, verification, post-termination handling.
- **2.4 Training Data Risk** — can {the organization}'s data train vendor models? Opt-out mechanism standard or negotiated? Are developer prompts excluded by default?
- **2.5 Data Portability** — export at any time, formats supported, bulk export API.

### D3 — Cost & TCO

- **3.1 Pricing Model** — per seat / usage-based / effort-based / flat; predictability; spending ceiling; overages.
- **3.2 Implementation Cost** — internal engineering hours, professional services, training.
- **3.3 Integration Cost** — integration with {client_tech_stack}; API call costs; egress fees.
- **3.4 Scaling Cost** — cost at 2× and 10× current volume; tier-change triggers; spike triggers.
- **3.5 Exit Cost** — migration cost; lock-in clauses; data and IP retention upon exit.

### D4 — Integration with Existing Stack

- **4.1 Core Stack Integration** — for each system in {client_tech_stack}, evaluate integration as **native / API / custom / not compatible**.
- **4.2 API Design** — standard API (REST, GraphQL, OpenAI-compatible); current docs; rate limits; sandbox.
- **4.3 Authentication Integration** — OAuth 2.0 / SAML 2.0; works with {the organization}'s identity provider.
- **4.4 Data Flow Design** — how data moves; whether it leaves {the organization}'s perimeter in transit; auditable.
- **4.5 Deployment Architecture** — runs inside {the organization}'s cloud; required external hosting; container support.

### D5 — Vendor Stability & Exit Risk

- **5.1 Financial Health** — funding, valuation, ARR, growth, runway.
- **5.2 Market Position** — operating tenure, competitors, consolidation signals, hyperscaler-competing-product risk.
- **5.3 Customer Concentration** — major customers, churn, single-customer dependence.
- **5.4 Exit Risk** — vendor-shutdown plan; data accessibility; IP recoverability; migration cost and timeline.
- **5.5 Contractual Protection** — SLA with financial penalties; source/data escrow; termination clause.

### D6 — Data Classification & Protection (informs D2)

- **6.1 Data Taxonomy** — map {the organization}'s data this tool will touch to sensitivity level + regulatory risk. Use the taxonomy from `SCORING_GUIDE.md` or the bucket overlay.
- **6.2 Classification Controls** — labels supported; per-data-type access control; field-level encryption.
- **6.3 Data Minimization** — does the tool need more access than the use case requires; can access be limited.
- **6.4 Third-Party Sharing** — sub-processors; locations; ability to restrict.

### D7 — Production & Operational Impact (informs D1)

- **7.1 Reliability** — uptime SLA, historical record, status page, maintenance window policy.
- **7.2 Performance** — latency SLAs, scale degradation, rate-limit production impact.
- **7.3 Business Continuity** — RTO, RPO, DR plan, geographic redundancy.
- **7.4 Support** — SLA tiers, 24/7 availability, dedicated AM, escalation path.
- **7.5 Change Management** — breaking-change comms, deprecation notice, LTS track.

### Scoring scale (every scored question)

| Score | Meaning | When to use |
|---|---|---|
| 3 | Fully met | Confirmed from primary source. No gaps. |
| 2 | Partially met | Met with caveats, only under conditions, or inferred. |
| 1 | Minimally met | Present but inadequate, undocumented, or requires significant work. |
| 0 | Not met | Confirmed gap, unavailable, or a direct risk. |
| N/A | Not applicable | Relevance Gate applied — category error for this tool type. |

**N/A is excluded from BOTH numerator and denominator.** It does not inflate or deflate scores.

### The Relevance Gate

Before scoring **every** sub-dimension group, ask:

> "Given what this tool IS and the role it plays for {the organization} — is this sub-dimension testing a real capability gap, or a category error?"

A **category error** assumes the tool is a type of thing it is not. Examples:

- Asking a development platform about fine-tuning an LLM → N/A.
- Asking an internal-only tool about a global CDN → N/A.
- Asking a managed dev environment about chaos engineering → N/A.
- Asking a SaaS productivity tool about IaC → N/A.

How to apply:

```
1. Read the sub-dimension group.
2. Ask: "Is this tool the type of thing this question is designed for?"
3. YES → score normally.
4. NO  → mark N/A, write one line explaining why, exclude from score.
```

Do **not** mark N/A because a tool fails a question. N/A is for category errors only. A real gap scores 0 or 1.

### Final score formula

```
Final Score = (Tier 1 Score × 0.70) + (Tier 2 Score × 0.30)
```

Tier 1 score is the weighted sum of D1–D5 percentages mapped to point totals. Tier 2 score is the combined percentage across activated modules.

---

## 8. Tier 2 — Specialist Modules

Activated by tool type identified in D0. Apply the Relevance Gate before every sub-dimension.

### Module A — AI/ML Platform
*Activate when:* the tool IS an AI model, provides AI capabilities as its core function, or hosts AI models {the organization} will use.

Sub-dimensions: A1 Model Governance · A2 Data Training Risk · A3 Inference Cost & Performance · A4 Integration & Deployment · A5 Responsible AI & Compliance.

### Module B — Dev/Code Platform
*Activate when:* the tool is a development environment, code editor, or application builder.

Sub-dimensions: B1 Code & IP Ownership · B2 Security & Access Control · B3 Deployment & Environment Control · B4 Collaboration & Governance · B5 AI Features Within the Platform.

### Module C — Data Platform
*Activate when:* the tool processes, stores, transforms, or analyzes data.

Sub-dimensions: C1 Data Architecture · C2 Data Quality & Governance · C3 Performance & Scale · C4 Integration.

### Module D — SaaS Productivity
*Activate when:* the tool is a productivity application (communication, documents, project management).

Sub-dimensions: D1 Data Handling · D2 Integration · D3 Administration.

### Module E — Automation/Integration
*Activate when:* the tool orchestrates workflows, connects systems, or automates processes.

Sub-dimensions: E1 Capability · E2 Security · E3 Reliability · E4 Scale.

### Module F — External API/Service
*Activate when:* {the organization}'s systems will call this tool as an external API or web service.

Sub-dimensions: F1 API Quality · F2 Reliability & Performance · F3 Security · F4 Cost Model.

### Module G — Infrastructure/Cloud
*Activate when:* the tool hosts, runs, or manages infrastructure that {the organization}'s systems depend on.

Sub-dimensions: G1 Cloud Architecture & Control · G2 Security & Network · G3 Identity & Access · G4 Scalability & Performance · G5 Reliability & Business Continuity · G6 Cost & FinOps · G7 Compliance & Auditability.

> The full 233-question list lives in `docs/FRAMEWORK.md`. Sub-dimensions marked `[GATE]` are most prone to category errors and require an explicit Relevance Gate decision.

---

## 9. Recommendation bands

| Score | Band | Meaning |
|---|---|---|
| 80–100 | ✅ Approved | Adopt with standard onboarding |
| 60–79 | ⚠ Approved with Conditions | Adopt with specific governance controls in place first |
| 40–59 | 🔶 High Risk | Significant concerns — leadership decision required with full risk acknowledgment |
| 0–39 | ❌ Not Recommended | Do not adopt in current form |

The recommendation goes to the Tier 3 report **and** to slide 4 of the leadership presentation. Nowhere else.

---

## 10. Strategic Opportunity Assessment (3.5) — MANDATORY

Every evaluation must complete this section. It answers: *what else can this tool do for {the organization} beyond the original request?*

### A. Use cases discovered during investigation

For each use case found beyond the original request:

- Description in plain language.
- Which {the organization} team or process benefits.
- Estimated complexity (Low / Medium / High).
- Dependency on other {the organization} systems.

### B. Industry benchmarking

How is this tool used in:

- {the organization}'s primary industry.
- Adjacent industries.
- General enterprise — best practices.

### C. Organization-specific opportunities (ranked)

| Opportunity | Feasibility (1-5) | Business Impact (1-5) | Priority Score (F × I) |
|---|---|---|---|
| Opportunity 1 | | | |
| Opportunity 2 | | | |
| Opportunity 3 | | | |

Present the top 3 with a 2-sentence implementation outline each.

---

## 11. Advertencias — risk flags

An Advertencia is a formally documented risk flag. It is **not** an automatic blocker. {client_governance_team} determines how each is addressed; the evaluator's job is to document completely.

| Level | When | Implication |
|---|---|---|
| HIGH | Immediate risk to data, IP, finance, or operations | Resolve or formally accept before development begins |
| MEDIUM | Real risk that is manageable with controls | Address before production |
| LOW | Awareness item — worth monitoring | Document and review at next evaluation cycle |

**Format:**

```
ID: ADV-XX                     (sequential per evaluation; restart at ADV-01 each evaluation)
Level: HIGH / MEDIUM / LOW
Source: dimension or module where found
Title: plain language — what is the risk
Finding: what was found and why it matters for {the organization} specifically
Required Action: what must happen before this risk is acceptable
```

Verification labels apply to every finding:

- ✅ Verified — confirmed from primary source.
- ⚠ Inferred — reasonable conclusion from available evidence.
- ❌ Unverified — could not be confirmed; goes to the Manual Verification Checklist (3.6).

---

## 12. Communication — the leadership presentation

### The Pyramid Principle

> *You think from the bottom up. You present from the top down.*

1. Lead with the recommendation (slide 4, not slide 10).
2. Support with 3–4 key arguments — one per slide.
3. Each argument is backed by evidence inside the slide.

### SCQA opening (slide 2)

| Element | Definition |
|---|---|
| Situation | The undisputed current state |
| Complication | What created the decision point |
| Question | The business question to be answered |
| Answer | Your recommendation — stated immediately |

### Five non-negotiable rules

1. **Answer first.** Recommendation on slide 4.
2. **No internal codes.** D1, ADV-03, Module B, Option C never appear on a slide.
3. **One message per slide.** The slide title IS the conclusion; the body proves it.
4. **Business language only.** Translate IT terms; keep terms the audience already uses.
5. **No scores.** Scores live in evidence documents. {the organization} has no established benchmark; a number without context confuses more than it informs.

### The 10-slide structure

| # | Slide | Title formula | Must include |
|---|---|---|---|
| 1 | Cover | `[Tool Name]` | Four boss-question preview at bottom |
| 2 | Why we evaluated | `WHY WE EVALUATED [TOOL]` | SCQA — 4 cards |
| 3 | What is the tool | `WHAT IS [TOOL]?` | Three-part D0.2 analysis + reframed question + vendor facts |
| 4 | The short answer | `THE SHORT ANSWER` | Recommendation + conditions + named architecture paths |
| 5 | Q1 — Data safety | `01 — IS OUR DATA SAFE?` | Risks + fixes left, verified protections right |
| 6 | Q2 — Integration | `02 — DOES IT INTEGRATE WITH OUR STACK?` | Integration table — System / Type / Status / Notes |
| 7 | Q3 — Financial | `03 — CAN WE BENEFIT FINANCIALLY?` | Cost drivers left, savings + contract requirements right |
| 8 | Q4 — Pros & cons | `04 — PROS AND CONS` | ≤5 per side; titles ≤8 words |
| 9 | The discovery | `THE DISCOVERY THAT CHANGES THE RISK PICTURE` | Named discovery + 5 impact points + status + call to action |
| 10 | Next steps | `WHAT NEEDS TO HAPPEN BEFORE WE START` | Numbered conditions + owners + explanations |

### The 5-slide briefing deck (when an internal stakeholder must brief leadership)

| # | Slide | Purpose | Time |
|---|---|---|---|
| 1 | The Answer | Recommendation + named paths | 1 min |
| 2 | Three Questions Answered | Pre-loaded answers to the questions {client_governance_team} will ask | 4 min |
| 3 | The Discovery | The finding that changes the risk picture | 3 min |
| 4 | What the Meeting Must Produce | Two decisions + three contract requirements | 3 min |
| 5 | Your Meeting Toolkit | The 10-slide deck, evidence package, four one-sentence answers | 2 min |

### QA checklist before delivery

- Content: zero placeholder/TODO strings.
- Jargon: every slide title understandable to a senior non-IT operator.
- Answer-first: slides 1–4 alone make the recommendation clear.
- Visual render: PDF check — no truncation, no overlap, no orphaned elements.

---

## 13. Anti-patterns (refuse on sight)

| Anti-pattern | What happens | Rule violated |
|---|---|---|
| Start evaluating without a spec | Scope drifts, findings incomplete | Rule 1 |
| Score mitigations as positives | Scores mislead — tool appears safer than it is | Rule 4 |
| Apply irrelevant questions | Scores distorted in both directions | Rule 5 |
| Put scores in the presentation | Leadership asks about methodology instead of deciding | Rule 7 |
| Use framework codes on slides | Audience decodes instead of deciding | Rule 8 |
| Skip Lessons Learned | Same mistakes repeat in the next evaluation | Rule 10 |
| Show evidence before recommendation | Executive attention lost before the answer arrives | Rule 9 |
| Conflate findings doc and presentation | Two audiences served badly by one document | Rule 11 |
| Define only project success OR only tool success | Misalignment between initiative and tool | Rule 12 |

---

## 14. Session protocols

### 14.1 New evaluation session

```
Load in this order:
1. CONSTITUTION.md
2. VETT_FOUNDATION.md
3. docs/FRAMEWORK.md
4. docs/SCORING_GUIDE.md
5. templates/EVALUATION_SPEC.md
   + bucket-specific overlay (e.g. buckets/scout/skills/vett_scout_context.md)

Then: "I want to evaluate [Tool Name]. Ask me questions until the
spec is complete."
```

### 14.2 Tier 1 evaluation session

```
Load:
1. CONSTITUTION.md
2. docs/FRAMEWORK.md (focus D0–D7)
3. docs/SCORING_GUIDE.md
4. evaluations/[name]/spec.md
   + bucket overlay

Then: "Run Tier 1 evaluation for [Tool Name]. Start with D0,
work through D7."
```

### 14.3 Tier 2 evaluation session

```
Load:
1. CONSTITUTION.md
2. docs/FRAMEWORK.md (focus on activated modules)
3. docs/SCORING_GUIDE.md
4. evaluations/[name]/spec.md
5. evaluations/[name]/tier1-findings.md
   + bucket overlay

Then: "Run Tier 2 evaluation for [Tool Name]. Activated modules: [list]."
```

### 14.4 Tier 3 / report session

```
Load:
1. CONSTITUTION.md
2. templates/TIER3_REPORT.md
3. evaluations/[name]/spec.md
4. evaluations/[name]/tier1-findings.md
5. evaluations/[name]/tier2-findings.md

Then: "Generate the Tier 3 final report for [Tool Name]."
```

### 14.5 Presentation build session

```
Load:
1. CONSTITUTION.md
2. docs/PRESENTATION_GUIDE.md
3. evaluations/[name]/tier3-report.md
   + bucket overlay (color system, layout templates)

Then: "Build the leadership presentation for [Tool Name].
Follow the Pyramid Principle. Apply all five rules."
```

---

## 15. Outputs every evaluation must produce

By the end of Phase 5, the operator must have:

1. `evaluations/[name]/spec.md` — completed, status COMPLETE.
2. `evaluations/[name]/tier1-findings.md` — D0–D7 with weighted scores, every finding labeled.
3. `evaluations/[name]/tier2-findings.md` — every activated module scored; Strategic Opportunity Assessment §3.5 complete.
4. `evaluations/[name]/tier3-report.md` — sections 3.1–3.7 complete; recommendation band assigned.
5. Leadership presentation — 10 slides, recommendation on slide 4, no scores, no codes.
6. Briefing deck (5 slides) if an internal stakeholder will brief leadership.
7. ≥1 LL entry in `docs/LESSONS_LEARNED.md`.
8. `evaluations/[name]/status.md` → Complete.

If any of those is missing, the evaluation is not closed.

---

## 16. Quick decision flow

```
Evaluation request comes in
      │
      ▼
Is the EVALUATION_SPEC complete? (D0.2 three parts, D0.4 two-level success)
   ├── No  → Phase 0 intake (drive Q&A until gate passes).
   └── Yes ▼
Is Tier 1 (D0–D7) scored with every finding labeled?
   ├── No  → Phase 1; apply Relevance Gate; raise Advertencias as discovered.
   └── Yes ▼
Are all activated Tier 2 modules scored AND §3.5 complete?
   ├── No  → Phase 2.
   └── Yes ▼
Is the Tier 3 report generated with a recommendation band?
   ├── No  → Phase 3.
   └── Yes ▼
Is the 10-slide leadership presentation built (and briefing deck if needed)?
   ├── No  → Phase 4.
   └── Yes ▼
Phase 5: write Lessons Learned + close-out.
```

---

## 17. Variables this skill expects to have resolved

When this skill is loaded with a bucket overlay, the overlay must supply concrete values for:

- `{the organization}` — the client name.
- `{client_tech_stack}` — the actual list of platforms (cloud, security perimeter, data, identity, orchestration, AI, etc.) used in D4.1 / D7 / Module G.
- `{client_governance_team}` — who owns risk acceptance (typically IT/Security + Legal + Procurement).
- Compliance frameworks the client must satisfy (e.g. SOC 2, ISO 27001, GDPR/CCPA, industry-specific).
- Data classification taxonomy — the actual data types and sensitivity ratings.
- Any client-specific scoring adjustments or extra dimensions.
- Presentation visual system (colors, fonts, layout indices) if the client has a brand template.

If the overlay is missing values, ask the operator before scoring.

---

*VETT skill — generic, organization-agnostic. Concrete client values live in the bucket-specific overlay (e.g. `buckets/{bucket}/skills/vett_{bucket}_context.md`).*
