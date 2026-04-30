# VETT — Scout Motors Context Overlay

**Slug:** `vett_scout_context`
**Kind:** L2 context overlay for the `vett` skill
**Bucket:** `scout`
**Loads when:** bucket = `scout` is active and the `vett` skill is loaded.

This file does **not** redefine the VETT framework. It supplies the concrete Scout Motors values for the variables defined in `skills/vett.md` §17. Read both files together; if anything contradicts the framework logic, the framework wins (`skills/vett.md` is canonical).

---

## 1. Variable bindings

| Generic variable in `skills/vett.md` | Scout-specific value |
|---|---|
| `{the organization}` | **Scout Motors** |
| `{client_governance_team}` | **IT Security + Legal + Procurement** (Scout Motors). Risk acceptance is led by IT Leadership; legal and procurement co-sign contract terms. |
| Operator / evaluator | **Alfredo Pretel** — Workflow Engineering, IT |
| Evaluation ID format | `VETT-[TOOLNAME]-[YYYY-MM]` |

---

## 2. Scout Motors tech stack (`{client_tech_stack}`)

Every D4.1 evaluation must score against this matrix. Every module-G evaluation must consider these layers.

| Layer | System | Notes |
|---|---|---|
| Cloud (Microsoft / OpenAI) | **Azure** | Enterprise agreements in place |
| Cloud (Compound AI) | **AWS** | Primary AI infra — account `data-app-dev` |
| Container orchestration | **Kubernetes / EKS** | Cluster `data-app-eks-dev` — Admin Portal + backend services |
| Security perimeter | **Zscaler** | All traffic routed through — critical for every integration design |
| Orchestration | **N8N** | Alfredo's primary workflow tool |
| Data platform | **Databricks + Mosaic** | Lakehouse — AI processing and recommendation pipelines |
| Operational source of truth | **DynamoDB** | Training manuals, feedback, recommendations, users, defects |
| Vector DB | **Pinecone** | RAG already in production |
| AI models | **Claude (Bedrock), AWS Nova, Meta LLaMA, OpenAI** | Multi-model |
| AI voice / session layer | **LiveKit SaaS** | Real-time audio, sessions, voice detection — also executes agent code |
| Frontend AI | **Open Web UI** | Unified model interface |
| Version control | **GitHub** | Standard pipeline |
| Project tracking | **Jira** | |
| Documentation | **Confluence** | |
| Productivity / docs | **O365 + SharePoint** | |

**Key constraint:** all integrations must pass through or be compatible with **Zscaler**. Never design around it.

**Architecture pattern:** Scout uses a **hybrid SaaS + own cloud** model. Not everything runs on Kubernetes. The agent layer runs on LiveKit SaaS. Data lives in DynamoDB and Databricks. Admin tooling runs on AWS EKS. Evaluators must identify which layer a new tool touches before assessing integration complexity.

### Required D4.1 stack matrix

When filling D4.1 (`TIER1_TIER2_FINDINGS_TEMPLATE` Section 4), include rows for: Azure · AWS+Bedrock · Databricks · N8N · Pinecone · GitHub · Zscaler · Jira · Confluence · O365/SharePoint. Status is one of `Native / API / Custom / Not compatible`, marker is `✅ / ⚠ / ❌`.

---

## 3. Compliance requirements Scout must satisfy

These are the frameworks D1.4 must check against, and the floor for any Advertencia involving compliance.

- **SOC 2 Type II** — required for any vendor handling Scout data.
- **ISO 27001** — preferred; absence is at minimum a MEDIUM Advertencia.
- **IATF 16949** — automotive industry standard. Relevant when the tool touches manufacturing data, quality records, or production parameters.
- **GDPR** — DPA must be available for any tool processing employee or customer personal data.
- **CCPA** — must be confirmed for any tool processing California-resident data.

When a tool falls short of one of the above on data it actually touches, raise an Advertencia at HIGH for SOC 2 / GDPR DPA gaps, MEDIUM for ISO 27001 / CCPA / IATF 16949 gaps unless the use case sits in scope.

---

## 4. Scout data taxonomy (D0.6 / D6.1)

Use this taxonomy to map data the tool will touch. The sensitivity rating drives D2 weighting and Advertencia level.

| Data Type | Sensitivity | Regulatory Risk |
|---|---|---|
| Operator training records | HIGH | Employment law |
| Performance metrics | HIGH | HR / Employment |
| Work instructions / SOPs | MEDIUM | Proprietary |
| Quality control records | MEDIUM | ISO / IATF compliance |
| Production schedules | MEDIUM | Operational |
| Manufacturing parameters | HIGH | Trade secret |
| Supplier data (contracts / pricing) | HIGH | Contract confidentiality |
| Product specifications | HIGH | IP / Pre-launch |
| Financial data | HIGH | Public-company risk |
| Developer prompts / system descriptions | MEDIUM | IP / Architecture exposure |

**Overall data risk** is HIGH if the tool touches any HIGH item; MEDIUM if it touches MEDIUM but no HIGH; LOW only if all touched items are LOW.

> **Reminder — pretel-os CONSTITUTION §3:** the Scout bucket must never store concrete proprietary employer data (supplier names, internal specs, organizational details, financial figures, product roadmaps). Patterns are stored abstractly. The taxonomy above is structural, not data.

---

## 5. Scout-specific scoring adjustments

These are deltas to the generic VETT scoring — not replacements.

- **D1.7 — Zscaler compatibility:** raise to HIGH Advertencia on any incompatibility, regardless of other D1 findings. Zscaler-incompatible tools cannot ship at Scout without an explicit IT Security exception.
- **D2 weight floor:** if the tool touches HIGH-sensitivity data, D2 cannot pass overall (≥60%) without **all** of: (a) US-only residency option enforceable, (b) opt-out from training data on the standard contract, (c) full export and deletion confirmed.
- **D5 hyperscaler-overlap penalty:** under D5.2, if Anthropic / OpenAI / Microsoft / Google offer a competing native product, the vendor's stability score is capped at "Partially met" (2) on D5.4 unless the vendor has clear differentiation evidence.
- **Module G G2.3 — Zscaler integration:** mandatory `Yes` for any infrastructure tool with outbound traffic. Anything else is an Advertencia at HIGH.

---

## 6. Active Scout projects context

Evaluations run for these projects must consider the full system architecture, not just the tech stack matrix.

### Operator Training System (AI Assistant)

**Status:** in active development
**Requested by:** Srridawe — Scout Motors IT
**First evaluation:** Replit — April 2026

**Architecture (hybrid):**

- **LiveKit SaaS** — real-time audio, sessions, voice detection; also executes the agent docker image (Supervisor / Training / Feedback / Defect agents).
- **DynamoDB** (`data-app-dev`) — primary source of truth: tables `lk-training-manuals`, `lk-training-status`, `lk-users`, `lk-feedback`, `lk-recommendation`, `lk-defects`.
- **Databricks (Stage)** — daily-cron pipeline reads raw feedback, generates AI recommendations, writes to `lk-recommendation`.
- **AWS EKS** (`data-app-eks-dev`) — runs the Frontend (LiveKit interface) and the Admin Portal (human approval of recommendations).
- **Feedback loop** — voice → DynamoDB → Databricks → DynamoDB → Admin Portal → human approval → updated training content → next session.

**Common assumption errors to flag in evaluations:**

| Assumption | Reality |
|---|---|
| Everything runs on Kubernetes | Wrong — agent runs on LiveKit SaaS, not EKS |
| LiveKit is just an audio tool | Wrong — LiveKit also executes agent code |
| DynamoDB is a secondary cache | Wrong — DynamoDB is the primary source of truth |
| Databricks is real-time | Wrong — pipeline runs on a daily cron |

When evaluating a tool for this system, the evaluator must identify (a) which of the four layers the tool touches, (b) real-time vs batch profile, (c) where data transits, (d) any new data-residency concern, and (e) any new dependency that could break the feedback loop.

---

## 7. Presentation visual system (Scout brand)

Used for the 10-slide leadership presentation and the 5-slide briefing deck.

| Color | Hex | Use for |
|---|---|---|
| Navy | `#11232F` | Authority, dark panels, confirmed positives |
| Red | `#FF5332` | Risks, warnings, accent |
| Green | `#1E7145` | Strengths, confirmed integrations, pros |
| Amber | `#C55A11` | Cautions, partial items, cons |
| Light Green | `#E2EFDA` | Card backgrounds for pros / positives |
| Light Amber | `#FCE4D6` | Card backgrounds for cautions / costs |
| Light Blue | `#D5E8F0` | Card backgrounds for neutral / strategic |
| Light Red | `#FFDCE0` | Card backgrounds for risks |
| Light Gray | `#F2F2F2` | Alternating table rows |

**Font:** Calibri Light. Titles 24–28pt bold. Body 11–13pt regular.
**Template:** `Non-Confidential_Template.pptx`.

| Layout index | Layout name | Use for |
|---|---|---|
| 0 | Scout Master | Cover, discovery (dark navy full bleed) |
| 4 | Divider Slide Opt.1 | Section breaks |
| 10 | Content Slide Opt.1 | Left white + right dark — risks/positives split |
| 12 | Content Slide Opt.3 | Full white — tables, 2×2 grids, answer slides |
| 13 | Content Slide Opt.4 | Full white, two body columns — pros/cons |

**Title-width constraint:** Content layout title placeholders are ~5.7" wide. Titles ≤6 words or they wrap into the subtitle. Test every title.

**Jargon translation pinned for Scout audience:**

| IT term | Plain language | Keep as-is? |
|---|---|---|
| GCP | "Google's servers" | No |
| MIT license | "Anyone can freely copy this code" | No |
| RBAC | "Role-based access — who can see and do what" | No |
| Effort-based billing | Keep — it is clear and precise | Yes |
| Zscaler | Keep — Scout audience knows it | Yes |
| Databricks | Keep — Scout's own platform | Yes |
| D1, D2, ADV-03 | Never — translate to plain finding | No |
| Option A/B/C/D | Name the path — "Build here, run on our servers" | No |

---

## 8. References

- Generic framework: `skills/vett.md`.
- Scout bucket manifest: `buckets/scout/README.md`.
- pretel-os CONSTITUTION §3 (data sovereignty for the Scout bucket): no concrete proprietary employer data in any commit, database, prompt, log, or backup.
