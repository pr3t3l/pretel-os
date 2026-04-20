# AUDIT PROMPT — Gemini 3.1 Pro Strategic & Use-Case Review

**Target model:** Gemini 3.1 Pro (recommended) or Gemini 2.5 Pro
**Interface:** Google AI Studio, Gemini web, or direct API via LiteLLM
**Estimated cost:** ~$0.40
**Expected output length:** 10–18 opportunities + gap list, ~4,000–6,000 words
**Duration:** 3–5 min for model, 30 min for you to read

---

## Instructions (paste below this line)

---

You are a senior product architect and strategist performing a **forward-looking review** on a personal cognitive operating system called **pretel-os**. The operator (Alfredo Pretel Vargas) is a solo developer in Columbia, SC, transitioning from a W2 role at Scout Motors toward full-time freelance work. He builds and operates a self-hosted AI agent platform and is designing pretel-os as the unified cognitive infrastructure behind both his personal life, his current employment (Scout, with strict data-sensitivity requirements), and his emerging freelance business (target: dozens to hundreds of clients over 2–5 years).

Your job is **not** to find architectural bugs. A separate adversarial auditor is handling that. Your job is to think forward:

1. **Use cases the system should support that aren't explicitly covered**
2. **New skills, tools, or MCP features the system should include**
3. **Freelance productization opportunities** beyond the five already listed (VETT-as-a-Service, SDD-on-Demand, Forge, Finance AI-parsing, Marketing System)
4. **Cross-pollination opportunities** the design enables but the docs don't name
5. **Scalability scenarios** specific to the "100 clients" ambition — what breaks, what needs earlier investment?
6. **Strategic risks and opportunities** the operator would regret missing
7. **Complementary tools and integrations** that would compound the system's value

Your orientation: assume everything in the documents is already decided and implemented. Start from "given this system exists, what's next?" and "given the operator's stated direction, what's missing that they'll need in 6–24 months?"

## Ground rules

1. **Read all five documents before writing any opportunity.** You need the full picture to identify non-obvious connections.
2. **Every opportunity must be concrete and actionable.** Not "consider AI for better workflows" — instead, "add a skill `client_discovery.md` that runs a 5-question diagnostic when a new freelance client is added via `create_project`, capturing budget, timeline, technical constraints, and preferred communication cadence; store in `project_state` and surface in Morning Intelligence."
3. **Ground every opportunity in the operator's stated context.** Use the details in the docs (Declassified Cases, Vietnam trip planning, rental property income, TikTok Spanish content, daughter's Kindergarten enrollment, the 8-phase Forge pipeline, etc.). Generic "you could add CRM features" is weaker than "given the operator runs Declassified Cases digital mystery products, a `customer_lifecycle` skill could track post-purchase engagement patterns applicable to any future product launch."
4. **Classify each opportunity:**
   - **IMMEDIATE** — should be a Phase-1 module or added to the roadmap before first build
   - **NEAR-TERM** — add within 3–6 months, after foundation modules ship
   - **LONG-TERM** — worth documenting now so it's not forgotten; build in 6+ months
5. **Be specific about freelance revenue potential.** If an opportunity is a productizable service, say "small operator could charge $X per engagement" with evidence or analog pricing.
6. **Identify cross-bucket value.** If something for Scout also helps Business, call it out — cross-pollination is a first-class feature of this system.
7. **Challenge the Productized Services list.** Is it complete? Too ambitious? Missing obvious wins?

## Specific areas to probe

### Scalability to 100 clients

`PROJECT_FOUNDATION §1.3` lists "freelance proof of concept" as a 12-month success criterion. The system is designed to scale to "hundreds of clients over 2–5 years." What specific capabilities does that trajectory require that aren't named in the current design?

Consider: client onboarding flow, per-client isolation beyond the `client_id` column, client-facing deliverable formats, billing integration, contract management, recurring revenue vs one-off project tracking, cross-client learnings that respect confidentiality, project templating for common engagement types, client communication cadence tracking, scope-creep detection.

### Productized services — beyond the five

The docs name five offerings. What other skills or workflows, already built or planned, could become productized services?

Consider: Morning Intelligence-as-a-service for small businesses, cross-pollination consulting (applying a methodology from one domain to another), Scout Motors-style assembly-line tracker templates, the SDD planner workflow as a methodology-consulting engagement, CRM + memory hybrid for solo consultants, personal financial analysis for other solopreneurs, Spanish-content automation for LatAm markets (leveraging the operator's Spanish TikTok experience).

### Skills not yet in the roadmap

`PROJECT_FOUNDATION §4 Module 7` lists seven skills to migrate. What skills are missing that the operator will need within 12 months?

Consider: client proposal generation, scope-estimation skill, pricing skill for freelance offerings, content-series planning (for TikTok/YouTube), tax-preparation skill (given rental income + self-employment + upcoming LLC/S-Corp decisions), travel-planning skill (Vietnam is an example; every freelance trip is another), school-decision skill (Kindergarten selection is a recurring life event type, not a one-off).

### Tools not yet proposed for the MCP server

`PROJECT_FOUNDATION §2.5` lists the tool inventory. What tools would compound the system's value?

Consider: calendar integration beyond read (draft + schedule based on context), email draft generation grounded in `contacts` and recent project context, contract / invoice generation, receipt parsing for rental income, social-media post drafting, voice-memo transcription + auto-routing to correct bucket, "explain this to a friend at a coffee shop" simplification tool (leveraging the operator's mentioned use case), daily reflection prompt generation.

### Morning Intelligence — what else could it do?

It currently delivers a Spanish voice brief at 06:00. What higher-value uses of that channel are there?

Consider: weekly strategic review (Sundays), monthly financial check-in, quarterly Scout-compliance audit reminder, "you haven't logged a lesson from bucket X in 30 days" nudges, "project Y has a TODO older than 14 days" prompts, content-calendar prompts for TikTok, end-of-day reflection prompt (evening counterpart).

### Data the system should be capturing but isn't

The schema has 18 tables. What's missing that the operator will regret not tracking?

Consider: time spent per bucket (for ROI on attention), API cost attribution per project (for freelance billing / personal budget), revenue per offering (for productization decisions), operator mood / energy (if desired — affects when to review pending lessons vs ship code), travel log (for tax purposes on business trips), relationship-touchpoint cadence (last contact with key collaborators).

### Freelance operator lifecycle

The system focuses on knowledge and context. It's silent on the business operations of being a freelancer.

Consider: lead capture → qualified prospect → proposal → signed client → active engagement → delivery → post-engagement → referral / case study, with the data model and MCP tools supporting each stage.

## Output format

Produce a single document with this structure:

```
# pretel-os Strategic & Use-Case Review

**Reviewer:** Gemini 3.1 Pro
**Date:** [date]
**Documents reviewed:** [list]
**Focus:** forward-looking opportunities, use cases, productization, scalability

## Executive summary
[3–5 sentences: the highest-leverage opportunities]

## Use cases the design enables but doesn't name

### USE-CASE-001 — [short title]
- **What:** [1–2 sentence description]
- **Why valuable:** [concrete scenario showing operator benefit]
- **Implementation sketch:** [which existing entities — tools, tables, workers, skills — enable this; what new surface, if any, is needed]
- **When:** IMMEDIATE | NEAR-TERM | LONG-TERM
- **Cross-bucket potential:** [which buckets benefit]

[repeat 4–8 use cases]

## New skills to add to the `skills/` directory

### SKILL-001 — [name]
- **What it does:**
- **Why the operator needs it:**
- **Inputs:** [...]
- **Outputs:** [...]
- **Productizable?** [yes, with target market and rough pricing] | [no, internal only]
- **When:** IMMEDIATE | NEAR-TERM | LONG-TERM

[repeat 4–8 skills]

## New MCP tools to add

### TOOL-001 — `function_name(...)`
- **Purpose:**
- **Category:** context | capture | sync | execution | prompt
- **Signature:** [params → return]
- **Rationale:** [why not existing tools + what changes for operator]
- **When:**

[repeat 3–6 tools]

## Productized freelance services (additions to the existing 5)

### SERVICE-001 — [name]
- **What the client receives:**
- **Underlying pretel-os asset:** [skill, workflow, or tool]
- **Estimated pricing range:** [with analog benchmark if possible]
- **Target client profile:**
- **Delivery mechanism:** [async report, live consult, monthly retainer, etc.]
- **Dependencies:** [other modules or skills required first]

[repeat 3–5 services]

## Scalability concerns for the 100-client target

### CONCERN-001 — [title]
- **Observation:** [what the current design does]
- **What breaks at 10 clients:** [or 50, or 100 — be specific about the threshold]
- **Recommendation:**
- **Priority:** IMMEDIATE | NEAR-TERM | LONG-TERM

[repeat 3–5 concerns]

## Cross-pollination opportunities not named in the docs

### CROSS-POLL-001 — [source bucket] → [target bucket]
- **What crosses:** [pattern, skill, or data]
- **Current state:** [why it isn't captured today]
- **Value if captured:** [operator benefit]

[repeat 3–6]

## Complementary integrations worth adding

[3–5 external services or APIs that would compound value, with use case and estimated cost]

## Challenges to current decisions

[Only the top 3–5 decisions you'd make differently, with specific rationale. This is your chance to push back on the operator's plan from a strategic (not architectural) angle.]

## Strategic risks and opportunities

### RISK-001 — [short title]
- **Risk:** [specific scenario]
- **Likelihood / Impact:**
- **Mitigation:** [actionable step the operator can take now]

### OPPORTUNITY-001 — [short title]
- **Opportunity:** [specific scenario]
- **Time sensitivity:** [why acting now matters]
- **First step:**

[repeat 2–4 of each]

## Questions for the operator
[3–5 questions whose answers would change priorities]
```

## Five documents to review

The five documents are pasted below in order. Read all of them before writing opportunities.

---

### Document 1 of 5: CONSTITUTION.md

[PASTE FULL CONSTITUTION.md HERE]

---

### Document 2 of 5: PROJECT_FOUNDATION.md

[PASTE FULL PROJECT_FOUNDATION.md HERE]

---

### Document 3 of 5: DATA_MODEL.md

[PASTE FULL DATA_MODEL.md HERE]

---

### Document 4 of 5: INTEGRATIONS.md

[PASTE FULL INTEGRATIONS.md HERE]

---

### Document 5 of 5: LESSONS_LEARNED.md

[PASTE FULL LESSONS_LEARNED.md HERE]

---

Now produce the strategic review. Do not summarize the documents. Focus on opportunities and use cases the design enables or misses.
