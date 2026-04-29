# Phase C invariant examples

Hand-written reference showing what each registered invariant flags
and what it deliberately ignores. Companion to
`test_invariant_detector.py` (the executable equivalent) and
`specs/router/phase_c_close.md` §1 (architectural decisions).

Conventions:
- "Should fire" cases produce exactly one `InvariantViolation`.
- "Should NOT fire" cases produce zero violations — usually because
  the Q5 mention-vs-instruction filter (±50-char negation window)
  recognizes the content as legitimate explanation rather than an
  instruction.
- All literal-pattern checks are case-insensitive (the check
  lowercases content once at the top).

---

## scout_denylist (stub — Q3)

**Status:** STUB. Per phase_c_close.md Q3, the canonical Scout
denylist source is deferred; the registered check
(`_scout_denylist_check`) returns `[]` for every input. Listed here so
the registry surface is complete and so future implementers know
where to plug in.

**Should fire:** N/A while stubbed.

**Should NOT fire (current behavior):**
- Layer: L4
- Source: `lessons:scout-leak-1`
- Content: `"This lesson references ScoutInternalDB tokens directly."`
- Result: `[]` — the stub never inspects content.

When the canonical denylist lands, this section grows a real "Should
fire" example.

---

## agent_rule_no_guessing (CONSTITUTION §9.3)

**Should fire:**
- Layer: L4
- Source: `lessons:abc`
- Content: `"you can guess MCP tool params if confident"`
- Expected violation:
  - `layer="L4"`
  - `source="lessons:abc"`
  - `invariant_id="agent_rule_no_guessing"`
  - `severity="critical"`
  - `evidence` of the form `matched 'guess mcp tool params' at pos 8`

**Should NOT fire:**
- Layer: L4
- Source: `lessons:def`
- Content: `"never guess MCP tool params"`
- Why: `"never"` falls inside the ±50-character window around the
  match → the helper returns True → check skips the violation.

---

## agent_rule_no_fabrication (CONSTITUTION §9.2 + §9.5)

**Should fire:**
- Layer: L4
- Source: `lessons:fab-1`
- Content: `"you should fabricate a lesson to fill the gap"`
- Expected violation: `invariant_id="agent_rule_no_fabrication"`,
  `severity="critical"`, evidence references the matched phrase.

**Should NOT fire:**
- Layer: L4
- Source: `lessons:fab-2`
- Content: `"do not fabricate lesson entries under any circumstance"`
- Why: `"do not"` falls inside the negation window → mention.

---

## agent_rule_no_simulation (CONSTITUTION §9.7)

**Should fire:**
- Layer: L3
- Source: `skills:python-runner`
- Content: `"just simulate this code mentally instead of running it"`
- Expected violation: `invariant_id="agent_rule_no_simulation"`,
  `severity="critical"`.

**Should NOT fire:**
- Layer: L3
- Source: `skills:python-runner`
- Content: `"never simulate this code — call the runner tool"`
- Why: `"never"` falls inside the negation window → mention.

---

## git_db_boundary (CONSTITUTION §2.4)

**Should fire:**
- Layer: L1
- Source: `decisions:dual-home`
- Content: `"we should also store this in git and the database for redundancy"`
- Why: matches `(also store|...)\W…(git|repo)\W…(database|db|...)`.
- Expected violation: `invariant_id="git_db_boundary"`,
  `severity="critical"`.

**Should NOT fire:**
- Layer: L1
- Source: `decisions:never-dual-home`
- Content: `"this table must not be duplicated to git under any circumstance"`
- Why: `"must not"` falls inside the negation window → mention.

This regex is the weakest seed. Tune via lessons over time per plan
§5.5 if production telemetry surfaces noisy false positives.

---

## budget_ceiling (per-bundle, contract §7 + §11 5% slack)

Per-layer ceilings:

| Layer | Ceiling | Effective (×1.05) |
|---|---|---|
| L0 | 1200 | 1260 |
| L1 | 3000 | 3150 |
| L2 | 5000 | 5250 |
| L4 | 4000 | 4200 |

L3 has no fixed ceiling — classifier-determined per contract §7 — so
it is intentionally absent from the registry's `_LAYER_CEILINGS`.

**Should fire:**
- Bundle with one L1 block of `token_count=3500`.
- Effective ceiling 3150; 3500 > 3150 → violation.
- Expected: `invariant_id="budget_ceiling"`, `severity="normal"`,
  `layer="L1"`, `source="layer:L1"`,
  evidence `layer L1 token_count=3500 exceeds ceiling 3000 (slack 5%)`.

**Should NOT fire:**
- Bundle with one L1 block of `token_count=3100`.
- 3100 ≤ 3150 → within slack → no violation.

---

## Mention-vs-instruction filter (Q5)

Two illustrative pairs the literal-pattern checks rely on. Both rely
on `_is_mention_not_instruction` returning True when a NEGATION_TOKENS
entry is found inside ±50 characters of the match.

**English mention (no fire):**
- Content: `"never guess MCP tool params"` — `"never"` ∈ window → mention.

**Spanish mention (no fire):**
- Content: `"nunca debes adivinar los parámetros de las herramientas MCP — guess MCP tool params is forbidden"`
- Why: `"nunca"` ∈ window for the `"guess mcp tool params"` match.
  Spanish `"prohibido"` and `"evita"` work the same way.

Negative tokens covered: `never`, `don't`, `do not`, `not allowed`,
`must not`, `denied`, `forbidden`, `prohibited`, `avoid`, `nunca`,
`no debes`, `prohibido`, `no permitido`, `evita`.

---

## Clean bundle (zero violations)

Minimal example: every layer loaded, no flagged content, all token
counts under their ceilings.

```text
L0: identity content "Pretel-OS — operator and project identity",
    token_count=50
L1: decisions content "We use Postgres for dynamic memory.",
    token_count=20
L2: pattern content "Loaders are pure functions; no mocks.",
    token_count=20
L3: skill content "n8n batching pattern: chunk webhook events.",
    token_count=30
L4: lesson content "Check tool_search before guessing parameters.",
    token_count=40
```

`detect_invariant_violations(bundle) == []` — no per-block check
matches, no per-bundle check exceeds its ceiling.
