# AUDIT PROMPT — GPT-5.4 Adversarial Architecture Review

**Target model:** GPT-5.4 (recommended) or GPT-5.1+
**Interface:** ChatGPT web, or direct API via LiteLLM
**Estimated cost:** ~$0.50
**Expected output length:** 15–25 findings, ~5,000–8,000 words
**Duration:** 3–5 min for model, 30 min for you to read

---

## Instructions (paste below this line)

---

You are a senior systems architect performing an adversarial audit on a personal cognitive operating system called **pretel-os**. The operator (Alfredo Pretel Vargas) is a solo developer transitioning from W2 employment to freelance. The system is designed to give any LLM client (Claude.ai web, Claude Code, Claude mobile, future MCP-compatible clients) hierarchical context, persistent memory, cross-bucket awareness, and portable access to three life domains: personal, business, and Scout (W2 employment with data-sensitivity requirements).

Your job is to find problems — specifically:

1. **Architectural flaws** — decisions that will cause pain at scale or in failure modes
2. **Unmitigated systemic risks** — single points of failure, cascade failure paths, unbounded growth
3. **Unjustified assumptions** — claims in the docs that aren't backed by reasoning or evidence
4. **Cross-document inconsistencies** — CONSTITUTION says X, DATA_MODEL implies Y, they conflict
5. **Edge cases / failure modes not covered** — what happens when [unexpected thing]?
6. **Undocumented trade-offs** — decisions presented as obvious when they're actually contested
7. **Testability and verifiability gaps** — rules stated that can't be operationally tested

You are **not** performing a consistency check against a prior conversation. You are performing an adversarial architecture review using the documents as your only source.

## Ground rules for your review

1. **Read all five documents completely before writing any finding.** Cross-references matter.
2. **Each finding must be specific and actionable.** "Scalability is a concern" is noise. "The `routing_logs` table has no retention policy enforced in code — only mentioned in prose in §4.1 — so it will grow unboundedly at ~3,000 rows/day once deployed" is a real finding.
3. **Cite the exact section and line.** Every finding must say which document, which section, which specific claim.
4. **Prioritize real problems over style preferences.** Naming conventions and prose style are not findings. Architectural load-bearing decisions are.
5. **When you claim something is missing, verify it is actually missing.** Use Ctrl-F mentally. If the doc covers it somewhere, that's not a gap.
6. **Severity rating on every finding.** CRITICAL / MODERATE / MINOR with defined criteria:
   - **CRITICAL**: will cause system-wide failure, data loss, cost explosion, or security breach
   - **MODERATE**: will cause significant rework or user-facing degradation
   - **MINOR**: improvement opportunity, not a bug
7. **If a decision seems wrong, propose an alternative.** Don't just say "consider X." Say "use approach Y because [evidence] [trade-off]."
8. **Distinguish between bugs and trade-offs.** A deliberate decision you disagree with is a trade-off; document why you'd decide differently. A decision that clearly breaks something is a bug.

## Specific areas to scrutinize

Apply extra skepticism to these load-bearing decisions:

- **The Router as single gateway** (`CONSTITUTION §2.2`) — what happens at scale, under partial failure, with contradictory input?
- **The five fixed context layers L0–L4** (`CONSTITUTION §2.3`) — are the budgets realistic? What content doesn't fit the taxonomy?
- **Git/DB strict boundary** (`CONSTITUTION §2.4`) — are there assets that are harmfully forced into one side?
- **Event-triggered Reflection** (`CONSTITUTION §2.6`, §5.1 rule 12) — are the triggers complete? What sessions will never fire reflection?
- **Source priority resolution** (`CONSTITUTION §2.7`) — does this handle all real conflict scenarios?
- **Four fixed background workers** (`CONSTITUTION §2.6`) — what legitimate work doesn't fit?
- **Complexity classification LOW/MEDIUM/HIGH** (`CONSTITUTION §5.1`) — testable? Operationally distinct?
- **Lifecycle rules for lessons** (`CONSTITUTION §5.5`) — do they actually prevent knowledge-base bloat, or just delay it?
- **Degraded mode** (`CONSTITUTION §8.43`) — is every degradation path actually implementable?
- **Cross-layer sync via tools** (`CONSTITUTION §7.36`) — does this actually prevent drift, or just document that it shouldn't happen?
- **The choice of `text-embedding-3-large`** (`ADR-006`) — is the justification sound? What breaks if wrong?
- **Single-tenant now, multi-tenant-ready later** (`§1.1`) — what does "ready" cost and does the schema actually enable it?
- **Revenue-gated cloud migration 3x margin** (`ADR-014`) — what happens if revenue comes from multiple sources?
- **Single hardware failure point (Vivobook)** (`PROJECT_FOUNDATION §3.4`) — mitigation sufficient?
- **Scout compliance with abstract patterns only** (`§3`) — what's the failure mode when an abstract pattern leaks identifying context through its specificity?

## Also look for

- Any metric that's stated but has no measurement mechanism defined
- Any "the operator will do X" that depends on manual discipline the system doesn't enforce
- Any tool listed in `PROJECT_FOUNDATION §2.5` whose behavior isn't specified elsewhere
- Any enum value (status, complexity, severity, category) whose transition rules are incomplete
- Any foreign-key relationship in `DATA_MODEL.md` whose cascade behavior isn't defined
- Any integration in `INTEGRATIONS.md` whose rate limits × expected volume leaves less than 10x headroom
- Any circular dependency between modules in the roadmap

## Output format

Produce a single document with this structure:

```
# pretel-os Adversarial Audit — Findings

**Auditor:** GPT-5.4
**Date:** [date]
**Documents reviewed:** CONSTITUTION.md, PROJECT_FOUNDATION.md, DATA_MODEL.md, INTEGRATIONS.md, LESSONS_LEARNED.md
**Total findings:** N (C critical, M moderate, m minor)

## Summary
[3–5 sentences: the most important architectural concerns]

## Findings

### FINDING-001 — [short title]
- **Severity:** CRITICAL | MODERATE | MINOR
- **Location:** [doc] §[section]
- **Claim under review:** "[exact quote or close paraphrase from doc]"
- **The problem:** [1–3 sentences explaining the issue]
- **Why this matters:** [concrete failure scenario or impact]
- **Proposed fix:** [specific change — new rule, new column, new process]
- **Alternative approach (if trade-off):** [if this is a decision you'd make differently, the alternative with reasoning]

### FINDING-002 — [...]
[repeat for each finding]

## Patterns across findings
[3–5 cross-cutting themes that emerge — e.g., "most failure-mode gaps are in the background worker layer", "several rules depend on un-enforced manual discipline"]

## Areas where the architecture is strong
[5–10 bullets on what you'd keep as-is. This calibrates your criticism — an auditor who only criticizes isn't credible.]

## Questions for the operator
[3–5 questions whose answers would change your assessment. Use these where you couldn't tell from the docs alone whether something is a gap or a deliberate choice.]
```

## Five documents to review

The five documents are pasted below in order. Read all of them before writing findings.

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

Now produce the audit findings. Do not summarize the documents. Do not restate what they say. Produce only findings per the output format above.
