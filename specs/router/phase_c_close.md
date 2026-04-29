# specs/router/phase_c_close.md — Phase C close-out (C.1–C.5)

**Module:** Router
**Status:** Not started — atomic groups C.1–C.5 below.
**Authority:** `specs/router/spec.md` §8.1 (immutable invariants), `specs/router/plan.md` §5 (post-rescope), `specs/module-0x-knowledge-architecture/layer_loader_contract.md` §10 (Router does NOT pre-resolve), `CONSTITUTION.md` §2.4 + §3 + §9, ADR-025.
**Scope:** Five atomic groups to close Phase C. After C.5 ships, M4 Phase C is done; tag candidate `phase-c-complete`. Phase D (telemetry) is unblocked.

---

## 0. Why this doc exists

`specs/router/tasks.md` lines 214–262 describe the **pre-rescope** Phase C
(topic catalog, `detect_conflicts()`, `apply_priority()`, `Conflict`
dataclass with `winning_source`). All of that was eliminated by
M4.C-rescope (commit `2eb963e`) per `layer_loader_contract.md` §10:
the Router does NOT pre-resolve cross-layer conflicts; the consumer
applies CONSTITUTION §2.7 priority at render time.

Rather than rewrite tasks.md mid-flight, this focused doc tracks the
post-rescope atomic groups and the architectural decisions they rest on.
Same pattern as `phase_b_close.md`. When Phase C closes (C.5), this doc
folds into `tasks.md` (legacy C.x rows marked superseded; new C.x rows
added under a "post-rescope" section) and tag `phase-c-complete` is
created.

**Phase C is a passive detector.** It does not block, modify, or veto
content. It scans the assembled `LayerBundle` for content that breaches
the immutable invariant class (CONSTITUTION §3, §2.3, §2.4, §9), produces
a `list[InvariantViolation]`, and hands it to Phase D for serialization
into `routing_logs.source_conflicts`. Defense-in-depth final-mile only.

---

## 1. Decisions taken (Q1–Q7 from session 2026-04-29)

### Q1 — Location of `InvariantViolation`

**Decision:** Define `InvariantViolation` in `src/mcp_server/router/types.py`,
not in `invariant_detector.py` (despite plan §5.2 listing the latter).

**Rationale:** `types.py` is the canonical location for frozen Router
data shapes (`LayerBundle`, `LayerContent`, `ContextBlock`,
`BundleMetadata`, `ClassifierSignals`). `InvariantViolation` is a value
type on the same plane: a return shape consumed by Phase D telemetry,
later by Module 6 reflection, and by downstream tools. Putting it in
`invariant_detector.py` would force every consumer to import the
detector module (and pull its logic into their import graph) just to
read the shape. Same anti-pattern Phase B already avoided for
`LayerBundle`.

**Plan §5.2 patch:** plan §5.2 currently says `InvariantViolation` lives
in `invariant_detector.py`. C.1.1 patches plan §5.2 in the same commit
that creates the dataclass.

**Trade-off:** None.

**Alternatives rejected:**
- `invariant_detector.py` (plan §5.2 default). Acceptable but couples
  shape-importers to logic.

### Q2 — Per-block vs per-bundle check signatures

**Decision:** Two distinct check signatures, two distinct registries.

```python
# Per-block: most invariants
CheckPerBlock = Callable[[ContextBlock, str], list[InvariantViolation]]
# (block, layer_name) -> list of violations from that block

# Per-bundle: aggregate invariants (budget ceiling)
CheckPerBundle = Callable[[LayerBundle], list[InvariantViolation]]
# (bundle) -> list of violations across the whole bundle
```

**Rationale:** Per-block checks (Scout denylist, agent rules, git/DB
boundary) operate on text content of one `ContextBlock`. Per-bundle
checks (budget ceiling) need the full bundle because a single block
can be under budget while its containing layer overflows. Forcing
budget into a per-block signature would require passing layer-level
state via globals or tuples — uglier than two signatures.

`list[InvariantViolation]` (not `Optional[InvariantViolation]`) lets
one check report multiple violations in one block (e.g., three Scout
tokens in a single lesson).

**Trade-off:** Two registries instead of one. Marginal complexity
increase; pays for itself by keeping each signature minimal.

**Alternatives rejected:**
- Single signature `(block, layer) -> list[Violation]`. Would force
  budget check into the per-block path with hacks.
- Single signature `(bundle) -> list[Violation]`. Forces every
  block-scoped check to re-iterate the bundle internally — boilerplate.

### Q3 — Scout denylist canonical source — DEFERRED

**Decision:** `scout_denylist_check` ships as a stub returning `[]`. A
follow-up task is created in the `tasks` table (`task_create` MCP tool)
with priority `low` and tag `deferred-todo`, scheduled for
post-Module-4 closeout. The stub keeps the registry shape correct and
the test surface complete; the operator does not work on Scout-bucket
content during Phase C, so a stub is operationally safe.

**Title:** `DEFERRED: locate canonical Scout denylist source and wire
into invariants.scout_denylist_check`

**Rationale:** Per session notes, Scout's denylist tokens currently live
in defense-in-depth across pre-commit hook + MCP tool filter + DB
trigger. There is no single Python-importable module today. Locating /
designing one requires research outside Phase C scope. Stub-now,
canonical-later is the correct sequencing.

**Trade-off:** A bundle that contains Scout denylist tokens during
Phase C → Phase D will not be flagged at the invariant-detector layer.
Other layers (pre-commit, MCP filter, DB trigger) still catch it. Final
mile is the only one missing.

**Alternatives rejected:**
- Inline a hand-copied denylist into `invariants.py`. Drift risk: hook
  and detector diverge silently.
- Implement a paritytest with the hook today. Requires Scout-bucket
  testing the operator is currently not doing.

### Q4 — Severity mapping

**Decision:** Severity strings aligned with `layer_loader_contract.md`
§3.2 SQL `CASE` ranking (`critical=0`, `normal=1`, `minor=2`).

| Invariant id | Severity | Justification |
|---|---|---|
| `scout_denylist` | `critical` | Data-sovereignty breach (CONSTITUTION §3) |
| `agent_rule_no_guessing` | `critical` | §9.3 violation, content instructing the agent to bypass tool_search |
| `agent_rule_no_fabrication` | `critical` | §9.2/§9.5 violation |
| `agent_rule_no_simulation` | `critical` | §9.7 violation, "simulate this Python code" content |
| `git_db_boundary` | `critical` | CONSTITUTION §2.4 load-bearing |
| `budget_ceiling` | `normal` | B.7 `summarize_oversize` already mitigates upstream; reaching this layer is drift, not damage |

**Rationale:** Per CONSTITUTION, the first four are non-overridable
invariants that protect data, contract, and agent behavior. Budget
overruns have an upstream mitigation; surfacing them as `normal` lets
Phase D's telemetry highlight true emergencies without drowning the
operator.

**Trade-off:** None.

**Alternatives rejected:**
- All five `critical`. Loses signal: budget overruns are operationally
  routine compared to denylist breaches.

### Q5 — Mention-vs-instruction heuristic

**Decision:** A ±50-character window around each pattern match. If any
of a fixed list of negation tokens appears within the window, the match
is treated as a mention (legitimate explanation of the rule) and **not**
reported as a violation.

```python
NEGATION_TOKENS = (
    # English
    "never", "don't", "do not", "not allowed", "must not",
    "denied", "forbidden", "prohibited", "avoid",
    # Spanish (operator writes lessons in both)
    "nunca", "no debes", "prohibido", "no permitido", "evita",
)

def _is_mention_not_instruction(content: str, match_pos: int) -> bool:
    """Conservative: if a negation appears within ±50 chars of the
    match, treat as a mention. Filters most false positives from
    lessons that explain the rule rather than violate it."""
    start = max(0, match_pos - 50)
    end = min(len(content), match_pos + 50)
    window = content[start:end].lower()
    return any(tok in window for tok in NEGATION_TOKENS)
```

**Rationale:** Phase C is a passive reporter. False positives are
high-cost (operator desensitization, "alarm fatigue"); false negatives
are low-cost (other defense layers catch real violations). Conservative
heuristic favors silent on ambiguity. The remaining false positives
are tracked via lessons and tuned over time per plan §5.5 risk note.

**Trade-off:** False negatives possible (a clever instruction that
includes a negation token nearby). Acceptable per plan §5.5: "false
positives are worse than false negatives."

**Alternatives rejected:**
- LLM-based classifier (cost, latency, plan §5.5 explicit out-of-scope).
- No filter (drowning).
- Sentence-boundary parsing (overkill for seed; revisit if heuristic
  proves noisy in production telemetry).

### Q6 — JSON-serializable shape

**Decision:** Every field of `InvariantViolation` is a primitive `str`
or `int`. No `Enum`, no `datetime`, no nested dataclasses, no `set`,
no `bytes`.

```python
@dataclass(frozen=True)
class InvariantViolation:
    layer: str          # 'L0' | 'L1' | 'L2' | 'L3' | 'L4'
    source: str         # 'lessons:abc-123' | 'CONSTITUTION.md' | ...
    invariant_id: str   # 'scout_denylist' | 'agent_rule_no_guessing' | ...
    evidence: str       # 'matched "guess MCP tool params" at pos 142'
    severity: str       # 'critical' | 'normal' | 'minor'
```

**Rationale:** Phase D will serialize the list with
`json.dumps([asdict(v) for v in violations])` and `INSERT` into
`routing_logs.source_conflicts` (JSONB). Primitive-only fields make
this round-trip work without custom encoders, decoders, or
post-deserialization mapping. No `__post_init__` validation —
constructors are trusted; runtime cost on every detection is avoided.

**Trade-off:** Loses static-type guarantees on enum-like fields
(`severity`, `layer`). Documented in field comments; mypy still flags
typos at the construction site of each check function (because each
check writes literal strings).

**Alternatives rejected:**
- `Enum` for `severity`. Breaks `json.dumps(asdict(...))` without a
  custom encoder.
- Nested dataclass for `evidence` (e.g., `{"pattern": ..., "pos": ...}`).
  Generates nested JSON harder to query in Postgres; flat string is
  enough for telemetry.

### Q7 — Registry structure

**Decision:** Two module-level dicts in `invariants.py`. No decorators,
no plugin system, no auto-discovery.

```python
INVARIANTS_PER_BLOCK: dict[str, CheckPerBlock] = {
    "scout_denylist":              _scout_denylist_check,    # stub
    "agent_rule_no_guessing":      _agent_rule_no_guessing_check,
    "agent_rule_no_fabrication":   _agent_rule_no_fabrication_check,
    "agent_rule_no_simulation":    _agent_rule_no_simulation_check,
    "git_db_boundary":             _git_db_boundary_check,
}

INVARIANTS_PER_BUNDLE: dict[str, CheckPerBundle] = {
    "budget_ceiling": _budget_ceiling_check,
}
```

The detector iterates both dicts and concatenates results. Adding a
new invariant requires (a) implementing the check function and (b)
adding one line to the dict. The detector module is not touched.

**Rationale:** Plain dicts are the simplest data structure that
satisfies the goal (decoupling detector orchestrator from check
implementations). Decorator-based registration introduces
import-order fragility (if `invariants.py` is partially imported, the
dict is partially populated). For 6 seeded checks growing toward maybe
12, that fragility is not earned.

**Trade-off:** Manually keeping the dicts and the function definitions
in sync. Trivial for current scale.

**Alternatives rejected:**
- `@register_invariant("name")` decorator pattern. Magic, import-order
  sensitive, no benefit at this scale.
- Class-based registry (`class InvariantRegistry: ...`). Overengineered.
- Single dict with type-tagged values. Loses static type checking on
  function signatures.

---

## 2. Atomic task list

### C.1 — Types & registry skeleton

- [ ] **C.1.1** Add `InvariantViolation` frozen dataclass to
  `src/mcp_server/router/types.py`. Five `str` fields per Q6: `layer`,
  `source`, `invariant_id`, `evidence`, `severity`. No `__post_init__`
  validation. Docstring references contract §3.2 severity ordering and
  Phase C close-out doc Q1/Q6.
  - **Done when:** `from mcp_server.router.types import InvariantViolation`
    succeeds; mypy clean across `types.py`; `dataclasses.asdict(InvariantViolation(...))`
    is `json.dumps`-compatible (no encoder errors).

- [ ] **C.1.2** Patch `specs/router/plan.md` §5.2 in the same commit as
  C.1.1 to redirect `InvariantViolation` location from
  `invariant_detector.py` to `types.py`. One-line surgical edit.
  - **Done when:** plan §5.2 reads "`InvariantViolation` frozen dataclass
    (in `types.py` per Q1)".

- [ ] **C.1.3** Create `src/mcp_server/router/invariants.py` with two
  empty registry dicts and the `CheckPerBlock` / `CheckPerBundle` type
  aliases. Module docstring documents the dict-add convention from Q7.
  Empty (or stub-only) is acceptable — checks are added in C.2.
  - **Done when:** `from mcp_server.router.invariants import
    INVARIANTS_PER_BLOCK, INVARIANTS_PER_BUNDLE` succeeds; mypy clean;
    both dicts have correct generic type annotations.

### C.2 — Per-invariant check implementations

- [ ] **C.2.1** Implement `_scout_denylist_check(block, layer) ->
  list[InvariantViolation]` in `invariants.py` as a stub returning
  `[]`. Function docstring references Q3 deferral and the deferred-todo
  task id. Register under key `"scout_denylist"` in
  `INVARIANTS_PER_BLOCK`.
  - **Done when:** function exists, registered, and a unit test confirms
    it returns `[]` for any input including a synthetic block
    explicitly containing "ScoutInternalDB".

- [ ] **C.2.2** Implement `_is_mention_not_instruction(content,
  match_pos) -> bool` in `invariants.py` per Q5. `NEGATION_TOKENS`
  module-level constant tuple (English + Spanish). Pure function, no
  I/O, no DB.
  - **Done when:** unit tests cover: negation in left half of window
    (returns True), negation in right half (True), no negation (False),
    negation outside ±50 window (False), Spanish "nunca" detected (True).

- [ ] **C.2.3** Implement `_agent_rule_no_guessing_check(block,
  layer)` for CONSTITUTION §9.3. Detects literal pattern
  `"guess MCP tool params"` (case-insensitive). Applies
  `_is_mention_not_instruction` filter from C.2.2. Returns
  `list[InvariantViolation]` with `severity="critical"`,
  `invariant_id="agent_rule_no_guessing"`, `evidence` string includes
  match position. Register in `INVARIANTS_PER_BLOCK`.
  - **Done when:** synthetic block "you can guess MCP tool params if
    confidence is high" → 1 violation; synthetic block "never guess MCP
    tool params" → 0 violations; both verified by C.4.2 tests.

- [ ] **C.2.4** Implement `_agent_rule_no_fabrication_check(block,
  layer)` for CONSTITUTION §9.2 + §9.5. Pattern list (literal,
  case-insensitive): `"fabricate lesson"`, `"invent a citation"`,
  `"make up a source"`. Same Q5 filter applied. Register in
  `INVARIANTS_PER_BLOCK`.
  - **Done when:** at least one synthetic violation case in C.4.2 fires;
    its negation form (e.g., "never fabricate") does not fire.

- [ ] **C.2.5** Implement `_agent_rule_no_simulation_check(block,
  layer)` for CONSTITUTION §9.7. Pattern list: `"simulate this code"`,
  `"mentally execute"`, `"trace through this script"` (case-insensitive).
  Same Q5 filter applied. Register in `INVARIANTS_PER_BLOCK`.
  - **Done when:** synthetic violation case fires; negation does not.

- [ ] **C.2.6** Implement `_git_db_boundary_check(block, layer)` for
  CONSTITUTION §2.4. Conservative regex looking for explicit dual-homing
  language: `r"(also store|duplicate|mirror|both).{0,40}(git|repo).{0,40}(database|db|postgres|table)"`
  (case-insensitive) or the symmetric pattern with git/db swapped.
  Same Q5 filter applied. Register under
  `"git_db_boundary"`. Documented as the weakest seed check — tunable
  via lessons.
  - **Done when:** synthetic block "we should store this in git AND the
    database for redundancy" → 1 violation; synthetic block "this
    table never needs to live in git" → 0 violations.

- [ ] **C.2.7** Implement `_budget_ceiling_check(bundle) ->
  list[InvariantViolation]` for `layer_loader_contract.md` §7. Per Q2,
  takes the full `LayerBundle`. For each `LayerContent` in
  `bundle.layers`, compares `layer.token_count` to the per-layer ceiling
  (`L0=1200`, `L1=3000`, `L2=5000`, `L3` skip — classifier-determined,
  `L4=4000`) with a 5% slack per contract §11. Overruns produce a
  violation with `severity="normal"`, `invariant_id="budget_ceiling"`,
  `evidence` string includes layer name and actual vs. ceiling counts.
  Register in `INVARIANTS_PER_BUNDLE`.
  - **Done when:** synthetic `LayerBundle` with `L1.token_count=3500`
    triggers 1 violation; the same bundle with `L1.token_count=3100`
    (within 5% slack) triggers 0 violations.

### C.3 — Detector orchestrator

- [ ] **C.3.1** Create `src/mcp_server/router/invariant_detector.py`
  exposing `detect_invariant_violations(bundle: LayerBundle) ->
  list[InvariantViolation]`. Iterates `INVARIANTS_PER_BLOCK` over every
  `(block, layer.layer)` pair across `bundle.layers`, then iterates
  `INVARIANTS_PER_BUNDLE` once over the bundle, then concatenates.
  Result order is deterministic: per-block checks first (in registry
  insertion order, by layer order, by block order within layer), then
  per-bundle checks (in registry insertion order). Pure function, no
  DB, no I/O, no LLM calls.
  - **Done when:** mypy clean across `invariant_detector.py` and
    `invariants.py`; with empty registries the function returns `[]`;
    with one fake check that always fires, the function returns one
    violation per `(layer, block)` pair.

### C.4 — Examples + tests

- [ ] **C.4.1** Author `tests/router/invariant_examples.md`. Format:
  one section per invariant id with two subsections: "Should fire" (1
  positive case) and "Should NOT fire" (1 negation case + brief
  explanation). Plus one "Clean bundle" section showing a
  zero-violation `LayerBundle` example. Markdown only, no code
  execution. Aligns with plan §5.3 deliverables row 4.
  - **Done when:** file exists; covers all 6 registered checks (Scout
    stub gets a "stub returns []" note, not a real example); reviewed
    once for typos.

- [ ] **C.4.2** Write `tests/router/test_invariant_detector.py`. Mirror
  the examples doc. Concrete tests:
  1. `test_clean_bundle_returns_empty` — bundle with safe content, all
     layers under budget → `[]`.
  2. `test_agent_rule_no_guessing_fires` — block content "you can
     guess MCP tool params" in L4 → 1 violation, severity=critical,
     correct invariant_id.
  3. `test_agent_rule_no_guessing_mention_does_not_fire` — block content
     "never guess MCP tool params" in L4 → 0 violations.
  4. `test_agent_rule_no_fabrication_fires` + mention counterpart.
  5. `test_agent_rule_no_simulation_fires` + mention counterpart.
  6. `test_git_db_boundary_fires` + counterpart.
  7. `test_budget_ceiling_fires` — bundle with `L1.token_count=3500` →
     1 violation, severity=normal.
  8. `test_budget_ceiling_within_slack_does_not_fire` — bundle with
     `L1.token_count=3100` → 0 violations.
  9. `test_scout_denylist_stub_returns_empty` — block with
     "ScoutInternalDB" → 0 violations (stub, Q3).
  10. `test_registry_extensibility` — temporarily insert a fake check
     into `INVARIANTS_PER_BLOCK`, run detector, observe it fires;
     teardown removes the fake (use `monkeypatch.setitem`).
  All synthetic `LayerBundle` fixtures defined inline at top of file
  (no shared `conftest.py` per repo convention).
  - **Done when:** `pytest tests/router/test_invariant_detector.py -v`
    exits 0; all 10+ tests green.

- [ ] **C.4.3** Run `mypy src/mcp_server/router/invariant_detector.py
  src/mcp_server/router/invariants.py src/mcp_server/router/types.py`.
  Zero errors, no `# type: ignore`.
  - **Done when:** mypy returns `Success: no issues found`.

### C.5 — Phase C gate + tasks.md cleanup

- [ ] **C.5.1** Verify `plan.md` §5.4 Done-when bullets line by line:
  (a) every invariant in `invariants.py` correctly identifies a
  synthetic violation in any layer (covered by C.4.2); (b) clean bundle
  produces empty list (test 1); (c) the `InvariantViolation` shape is
  serializable to JSONB shape Phase D will consume (verify via a
  one-liner script: `print(json.dumps([asdict(v) for v in
  detect_invariant_violations(test_bundle)]))` — runs clean); (d)
  `pytest tests/router/test_invariant_detector.py -v` exits 0.
  - **Done when:** all four bullets explicitly checked; close-out
    review note appended to this doc's §3.

- [ ] **C.5.2** Patch `specs/router/tasks.md` lines 214–262: prepend a
  "**SUPERSEDED 2026-04-29 by phase_c_close.md (M4.C-rescope)**" banner
  and strikethrough the old C.x rows. Append a new "Phase C —
  post-rescope" section that mirrors C.1–C.5 from this doc, with the
  same checkbox states (all marked complete by this point in the
  sequence).
  - **Done when:** tasks.md visually shows old Phase C as superseded;
    new section reflects actual completion state; commit message
    includes "supersedes legacy Phase C per M4.C-rescope".

- [ ] **C.5.3** Create `task_create` row via `pretel-os` MCP tool for
  the Q3 deferred work: title `DEFERRED: locate canonical Scout
  denylist source and wire into invariants.scout_denylist_check`,
  priority `low`, tag `deferred-todo`, module `M4` (or unassigned if
  M4 closes). Reference this doc's §1 Q3.
  - **Done when:** task row exists; task id captured in this doc's §3
    status.

- [ ] **C.5.4** Operator-driven local tag `phase-c-complete` on the
  closing commit (lightweight, not pushed automatically — same convention
  as `phase-b-complete`). Update `SESSION_RESTORE.md` §2 ("What is done"
  + "Top of stack") and §13 last-known state snapshot. The next-stack
  pointer becomes Phase D — telemetry.
  - **Done when:** `git tag -l 'phase-c-complete'` lists the tag;
    `SESSION_RESTORE.md` reflects Phase C closed and Phase D as
    top-of-stack.

---

## 3. Status

**Active task:** first unchecked `[ ]` above.

**Stop point:** end of C.5 (single pre-push review with 3–4 commits, no
migrations). Suggested commit boundaries:

1. C.1 — types + registry skeleton + plan §5.2 patch
2. C.2 — all six check implementations + the mention-vs-instruction
   helper (single commit, ~300 LoC)
3. C.3 + C.4 — detector orchestrator + examples doc + tests
4. C.5 — gate verification + tasks.md cleanup + deferred-todo task row
   + tag

**Cost estimate:** \$0. Phase C is pure scanning — no LLM calls, no
embedding calls, no slow tests. All checks are regex / string / arithmetic.

**Open follow-ups (file via `task_create` at C.5.3):**
- `DEFERRED: locate canonical Scout denylist source and wire into
  invariants.scout_denylist_check` (Q3)
- (Optional, surface only if telemetry shows noise) `tune git/DB
  boundary regex per production false-positive rate` — track in
  Module 6 lessons review, not as a blocking task.

---

## 4. Doc registry

This file is interim — not registered in `docs/PROJECT_FOUNDATION.md`
§6 Doc registry. After Phase C closes, fold its content into
`specs/router/tasks.md` per C.5.2 and either delete this file or keep
it as a historical reference for the Q1–Q7 architectural decisions.
Convention from `phase_b_close.md` applies.
