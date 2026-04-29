# specs/router/plan.md

**Module:** Router
**Status:** Draft (M4.T1.2)
**Last updated:** 2026-04-27
**Authority:** `specs/router/spec.md` (M4.T1.1), `CONSTITUTION.md §6 rule 31` (every phase has "done when")

> **Phase gate (SDD §6 rule 31):** Each phase below ends with an explicit "done when" line. No phase advances without the prior gate met. No code merges without the phase's deliverables complete.

---

## 1. Purpose

This plan decomposes Router implementation into six phases (A–F). Each phase is independently shippable, testable, and gated. The plan is the bridge between `spec.md` (what the Router is) and `tasks.md` (atomic work items <30 min each).

The phases are ordered by dependency, not by perceived complexity. Phases A and B can run in parallel; E develops in parallel with A; C waits on B; D integrates at the end of A+B+C+E; F is operational and lives beyond Module 4 exit.

---

## 2. Phase dependency graph

```
                ┌────────────────────────┐
                │ Phase A — Classifier   │
                │ (LiteLLM client +      │
                │  prompt + parse)       │
                └─────────┬──────────────┘
                          │
       ┌──────────────────┼─────────────────────┐
       │                  │                     │
       ▼                  ▼                     ▼
┌────────────┐   ┌────────────────┐   ┌──────────────────┐
│ Phase B    │   │ Phase E        │   │ Phase D          │
│ Layer      │   │ Fallback       │   │ Telemetry        │
│ loader     │   │ classifier     │   │ (after A+B+C+E)  │
└─────┬──────┘   └────────────────┘   └──────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Phase C — Source         │
│ priority resolution      │
└──────────────────────────┘

                                   ┌──────────────────────┐
                                   │ Phase F — Tuning     │
                                   │ (post-30-day ops)    │
                                   └──────────────────────┘
```

Parallelism: A ‖ B ‖ E. C blocks on B. D blocks on A+B+C+E. F is post-Module 4 exit.

---

## 3. Phase A — Classifier

### 3.1 Goal

A working `classify(message, l0_content, session_excerpt) -> dict` that calls `classifier_default` via LiteLLM, parses the JSON response, validates against the schema in `spec.md §5.1`, and returns either a valid classification or raises a typed exception that Phase E can catch.

### 3.2 Scope

**In:**
- `src/mcp_server/router/classifier.py` — main module.
- `src/mcp_server/router/prompts/classify.txt` — provider-agnostic system prompt.
- `src/mcp_server/router/exceptions.py` — `ClassifierTimeout`, `ClassifierTransportError`, `ClassifierParseError`, `ClassifierSchemaError`.
- LiteLLM client wrapper using OpenAI-compatible SDK (`base_url='http://127.0.0.1:4000'`, alias `classifier_default`).
- 10 test classification examples in `tests/router/classification_examples.md`, each with expected output.
- Unit tests in `tests/router/test_classifier.py`: success path, timeout, malformed JSON, schema-invalid JSON, unknown bucket, unknown project.

**Out:**
- Provider-specific prompt-caching code (deferred per ADR-020, see `tasks.md M4.T2.3`).
- Fallback classifier (Phase E).
- Telemetry writes (Phase D).

### 3.3 Deliverables

| Path | Content |
|---|---|
| `src/mcp_server/router/__init__.py` | Module init. |
| `src/mcp_server/router/classifier.py` | `classify()` function + LiteLLM client. |
| `src/mcp_server/router/prompts/classify.txt` | System prompt. |
| `src/mcp_server/router/exceptions.py` | Typed exceptions. |
| `tests/router/classification_examples.md` | 10 examples covering all 3 buckets + 3 complexity levels + edge cases (empty message, ambiguous bucket, unknown project). |
| `tests/router/test_classifier.py` | Unit tests against examples + failure modes. |

### 3.4 Done when

- `classify()` returns a dict matching `spec.md §5.1` schema for all 10 examples in `classification_examples.md`.
- All 4 typed exceptions raise correctly under their respective failure modes (verified by mocked tests).
- One real integration test (no mock) classifies one real message through the live LiteLLM proxy and returns a valid response.
- `pytest tests/router/test_classifier.py -v` exits 0.

### 3.5 Risk notes

- **Prompt quality is the dominant risk.** Provider-agnostic prompts are harder than provider-specific ones because Gemini/Claude/GPT/Kimi disagree on JSON-mode behavior. Mitigation: invest disproportionate time in prompt iteration; keep examples in version control; A/B test across at least 2 LiteLLM aliases pointing to different providers before declaring done.
- **JSON mode** is supported by Gemini and OpenAI but with subtly different syntax. Use OpenAI-compatible `response_format={"type": "json_object"}` (LiteLLM normalizes).
- **Timeout cliff at 3,000 ms.** Some providers cold-start above this on first call after idle. Mitigation: a single warm-up ping when the MCP server starts.

---

## 4. Phase B — Layer loader

### 4.1 Goal

Five loader functions, one per layer, each respecting its budget per `spec.md §6.1` and emitting a structured layer payload that Phase C can consume.

### 4.2 Scope

> **Reconciled 2026-04-29 with `layer_loader_contract.md` §3.** Loaders now read from Postgres tables (and a small fixed set of repo files for L0). Function signatures changed accordingly. Output type changed from `LayerPayload` (loose dict-like) to `LayerContent` / `LayerBundle` (frozen dataclasses, contract §10).

**In:**
- `src/mcp_server/router/layer_loader.py` with:
  - `load_l0() -> LayerContent` — reads CONSTITUTION/IDENTITY/AGENTS/SOUL files in pinned order (contract §10) AND queries `operator_preferences` for `scope='global'`. Returns one `LayerContent` with up to 5 `ContextBlock`s.
  - `load_l1(bucket: str) -> LayerContent` — queries `decisions` (active, bucket+applicable_buckets, severity-ordered via SQL CASE) and `operator_preferences` (scope LIKE 'bucket:...'). Returns `LayerContent` with `loaded=False` if classifier signals indicate no L1 needed.
  - `load_l2(bucket: str, project: str) -> LayerContent` — queries `decisions` (bucket+project), `best_practices` (project scope), `patterns` (bucket-applicable). No `module` parameter — module-level filtering moved into classifier-supplied tags.
  - `load_l3(skill_ids: list[str]) -> LayerContent` — queries `tools_catalog` WHERE `kind='skill'` AND `name = ANY(skill_ids)`. Skill file content is loaded from `skill_file_path` per row.
  - `load_l4(query_embedding, bucket, top_k) -> LayerContent` — filter-first sequential pgvector scan against `lessons` AND `best_practices` (cross-cutting via applicable_buckets). Per ADR-024, no HNSW.
  - `assemble_bundle(...) -> LayerBundle` — orchestrator that calls the 5 loaders, computes `BundleMetadata`, and returns the frozen dataclass. THIS function is what the Router calls.
- `src/mcp_server/router/types.py` — `ContextBlock`, `LayerContent`, `BundleMetadata`, `LayerBundle` exactly per contract §10.
- Token-counting helper using `tiktoken.get_encoding("cl100k_base")` per contract §11.
- `summarize_oversize(content, target_tokens) -> str` helper calling `classifier_default` for over-budget compression. Behavior unchanged from earlier draft.
- Unit tests for each loader: happy path, table empty, table query error (degraded mode), file missing (L0 only), over-budget triggers summarization.
- Integration test: full `assemble_bundle` round-trip with a seeded test DB.
- Cache invalidation: implement LISTEN/NOTIFY on the 4 trigger tables per contract §6.

**Out:**
- Source priority resolution / conflict resolution (consumer's job per contract §10 — was Phase C, now reduced; see Patch F note for Phase C).
- Decision logic about which layers to load (lives in `router.py` orchestrator, written at end of Phase D integration).
- Embedding generation (already exists from Module 3; loaders consume it).
- Reflection-worker writes to `lessons` / `best_practices` (Module 6).

### 4.3 Deliverables

> **Reconciled 2026-04-29.** `LayerPayload` is superseded by `LayerBundle`/`LayerContent`/`ContextBlock` from contract §10. Old name appears in some early task descriptions; treat as legacy alias when reading tasks.md.

| Path | Content |
|---|---|
| `src/mcp_server/router/layer_loader.py` | 5 loaders + `assemble_bundle` orchestrator + summarize helper. |
| `src/mcp_server/router/types.py` | `ContextBlock`, `LayerContent`, `BundleMetadata`, `LayerBundle` — frozen dataclasses per contract §10. |
| `src/mcp_server/router/prompts/summarize.txt` | Compression prompt for over-budget layers. |
| `src/mcp_server/router/fallback_keywords.py` | Bucket and complexity keyword lists used by fallback classifier (Phase E). Sub-bucket dotted-path selection moves into the classifier signals (out of layer-loader scope). |
| `src/mcp_server/router/cache.py` | `(bucket, project, classifier_hash)` cache + LISTEN/NOTIFY invalidation on `operator_preferences`, `decisions`, `best_practices`, `lessons` per contract §6. |
| `tests/router/test_layer_loader.py` | ≥30 tests covering: per-loader happy path, per-loader DB-empty path, degraded-mode (DB unhealthy), over-budget summarization, intra-L0 ordering invariant, severity SQL CASE ordering verified at SQL level, filter-first verified by EXPLAIN inspection. |
| `tests/router/test_assemble_bundle.py` | Integration: full round-trip with seeded `pretel_os_test`, asserts `LayerBundle` shape, `cache_hit=False` then `cache_hit=True` on second call, LISTEN/NOTIFY invalidation actually fires. |

### 4.4 Done when

- `assemble_bundle(bucket, project, classifier_signals, current_time) -> LayerBundle` returns a valid `LayerBundle` with all 5 `LayerContent` entries (some may have `loaded=False`).
- L0 always has `loaded=True` and emits ≥4 file blocks + ≤1 prefs block in the pinned order from contract §10.
- L1/L2/L3/L4 emit `loaded=True` only when classifier signals + inputs require them.
- Severity-ordered DB queries verified at the SQL plan level (test inspects `EXPLAIN` to confirm the CASE expression participates in the sort).
- Filter-first verified at the SQL plan level (test inspects `EXPLAIN` for `lessons` and `best_practices` queries — `bucket` filter must precede vector op).
- Over-budget content triggers `summarize_oversize` and returns content ≤ 80% of layer budget, plus an `over_budget=True` marker on the bundle's `over_budget_layers` list.
- A `gotcha` row is written to DB when summarization fires (verified by integration test).
- Cache invalidation verified: write to one of the 4 trigger tables, observe next `assemble_bundle` returns `cache_hit=False`.
- Degraded mode: DB unhealthy → loader returns `LayerContent(loaded=False)` for DB-backed layers, file-backed L0 still works.
- All token counts use `tiktoken.get_encoding("cl100k_base")` per contract §11.
- `pytest tests/router/test_layer_loader.py tests/router/test_assemble_bundle.py -v` exits 0.

### 4.5 Risk notes

- **Token counting drift.** Resolved by contract §11: `cl100k_base` is the canonical encoding. The pre-commit token-budget hook (`infra/hooks/token_budget.py`) was confirmed 2026-04-28 to use the same encoding. If a future hook change diverges, an ADR must reconcile both — not Phase B's concern.
- **L4 filter-first is mandatory.** Per CONSTITUTION §5.6 rule 26 and contract §3.5, never do a global vector scan. The loader must apply `bucket` + `applicable_buckets` filters at SQL level *before* the vector sort. Verified by `EXPLAIN` inspection in test.
- **Phase C scope shrank.** Original Phase C built `resolve_conflicts()` inside the Router. Per contract §10, conflict resolution now lives in the consumer. Phase C of this plan should be re-scoped to: (a) `source_conflicts` array population only, (b) invariant violation detection only (the Scout/budget/agent-rule checks). The conflict-priority logic moves to the consumer (likely Phase D or a follow-up). Tracked as a Phase C re-scope task — not blocking Phase B start.
- **Cache key derivation.** `classifier_hash` per contract §6 must be deterministic over `(bucket, project, complexity, needs_lessons, needs_skills, skill_ids tuple)`. Use `hashlib.sha256(json.dumps(..., sort_keys=True).encode()).hexdigest()[:16]`.

---

## 5. Phase C — Invariant violation detection

> **Reconciled 2026-04-29 (M4.C-rescope):** Per `module-0x-knowledge-architecture/layer_loader_contract.md §10`, Phase B does NOT pre-resolve cross-layer conflicts; the consumer applies CONSTITUTION §2.7 source priority at render time. Phase C is therefore reduced to invariant-violation detection only. Source-priority resolution is no longer a Router responsibility.

### 5.1 Goal

A `detect_invariant_violations(bundle: LayerBundle) -> list[InvariantViolation]` function that scans an assembled `LayerBundle` for content that breaches the immutable invariant class (Scout denylist, budget ceilings, git/DB boundary, agent rules from CONSTITUTION §9) and populates `routing_logs.source_conflicts` with a structured entry per violation.

This is a defense-in-depth check that no layer's content sneaks past CONSTITUTION's hard invariants — not a topical-conflict resolver.

### 5.2 Scope

**In:**
- `src/mcp_server/router/invariant_detector.py` with:
  - `detect_invariant_violations(bundle: LayerBundle) -> list[InvariantViolation]` — iterates every `ContextBlock` in every `LayerContent` in `bundle.layers`, runs each block through every registered invariant check.
  - `InvariantViolation` frozen dataclass: `layer: str`, `source: str`, `invariant_id: str`, `evidence: str`, `severity: str`.
- `src/mcp_server/router/invariants.py` — registry of invariant check callables keyed by `invariant_id`. Initial set seeded from CONSTITUTION + scout policy (scout-denylist match, budget-ceiling overrun, git/DB boundary breach, CONSTITUTION §9 agent-rule breach).
- Unit tests with synthetic violations embedded across layers: scout-denylist string in an L4 lesson, budget-ceiling violation in an L1 bucket README, agent-rule breach in an L3 skill, clean bundle produces empty list.

**Out:**
- Source priority resolution across layers (consumer's job per contract §10).
- Topical conflict detection between non-invariant content (deferred; reopen post-Module-4 only if telemetry shows operator confusion from contradictory layers).
- The decision to *modify* a source when wrong (operator-only).
- Cross-pollination flag writing (Reflection worker, Module 6).

### 5.3 Deliverables

| Path | Content |
|---|---|
| `src/mcp_server/router/invariant_detector.py` | Bundle scanner + `InvariantViolation` dataclass. |
| `src/mcp_server/router/invariants.py` | Registry of invariant check callables. |
| `tests/router/test_invariant_detector.py` | Synthetic violation tests across the 4 seeded invariant types + clean-bundle case. |
| `tests/router/invariant_examples.md` | Hand-written examples documenting expected detections. |

### 5.4 Done when

- For each invariant in `invariants.py`, the detector correctly identifies a synthetic violation embedded in any layer of a `LayerBundle`.
- A bundle with zero violations produces an empty list and no `source_conflicts` row.
- `routing_logs.source_conflicts` JSONB receives a structured `InvariantViolation` entry per detected violation.
- `pytest tests/router/test_invariant_detector.py -v` exits 0.

### 5.5 Risk notes

- **False positives are worse than false negatives.** A noisy detector that flags benign mentions of denylist tokens (e.g., a lesson explaining *why* a token is denied) drowns the operator. Mitigation: invariant checks must distinguish content-as-mention from content-as-instruction; start with conservative rules and tune via lessons.
- **Invariant registry seeds the system.** Initial registry is ~4 checks, one per major invariant class. Growth happens via lessons (operator notices a missed violation, adds a check). This is fine.
- **Consumer owns priority resolution.** Phase C intentionally does NOT replace the priority logic that used to live here. If telemetry later shows the consumer is fumbling priority resolution at scale, file it as a Module 5+ task — do not re-expand Phase C.

---

## 6. Phase D — Telemetry

### 6.1 Goal

Every `get_context` call writes one `routing_logs` row, and zero or one `llm_calls` row (one if the classifier ran via LiteLLM, zero if it hit fallback rules), all joinable by `request_id`. The 3 audit queries from `spec.md §9.3` execute cleanly against the resulting data.

### 6.2 Scope

**In:**
- `src/mcp_server/router/telemetry.py` with:
  - `start_request(message, session_id, client_origin) -> request_id` — creates the request, returns the UUID, starts the latency clock.
  - `log_classification(request_id, classification, mode, llm_call_data | None)` — inserts into `routing_logs` (always) and `llm_calls` (when `mode='llm'`).
  - `log_layers(request_id, layers_loaded, tokens_per_layer, over_budget_layers)`.
  - `log_rag(request_id, rag_expected, rag_executed, lessons_returned, tools_returned)`.
  - `log_conflicts(request_id, source_conflicts)`.
  - `log_completion(request_id, degraded_mode, degraded_reason, latency_ms)` — finalizes the row.
- Integration with the Router orchestrator so each phase writes its own slice.
- `report_satisfaction(request_id, score)` MCP tool implementation.
- Integration tests that run `get_context` end-to-end and assert 1 `routing_logs` row + 1 `llm_calls` row are written, joinable.

**Out:**
- Dashboard / visualization (operator runs SQL by hand or via Telegram `/status`).
- Retention policy (Dream Engine handles via partition drops, already in DATA_MODEL §4.1).

### 6.3 Deliverables

| Path | Content |
|---|---|
| `src/mcp_server/router/telemetry.py` | All logging helpers. |
| `src/mcp_server/router/router.py` | Orchestrator that wires Phases A+B+C+E+D together. This is where `get_context` actually lives. |
| `src/mcp_server/tools/get_context.py` | MCP tool wrapper that calls `router.get_context()` and returns the bundle. |
| `src/mcp_server/tools/report_satisfaction.py` | MCP tool. |
| `tests/router/test_telemetry.py` | Unit + integration: assert column population, join, audit-query correctness. |
| `tests/router/test_e2e.py` | The single end-to-end test required by `tasks.md M4.T8.1`. |

### 6.4 Done when

- `get_context("help me debug my n8n batching")` returns a valid `ContextBundle` with bucket=`business`, complexity ∈ {MEDIUM, HIGH}, L4 lessons containing the tag `n8n`, total tokens within the per-layer budgets.
- One `routing_logs` row written with all columns from `spec.md §9.1` populated.
- One `llm_calls` row written with `purpose='classification'`, `model=<concrete>`, joinable on `request_id`.
- All 3 audit queries from `spec.md §9.3` execute without error and return non-zero rows after the e2e test runs 5 times with varied messages.
- `report_satisfaction(request_id, 4)` updates `routing_logs.user_satisfaction` for the matching row.

### 6.5 Risk notes

- **Partial write hazard.** If the request fails midway (e.g., LiteLLM timeout after 2 layers loaded), the partial state must still result in a coherent `routing_logs` row with `degraded_mode=true`. Mitigation: telemetry writes are idempotent per request_id; final `log_completion` is wrapped in a try/finally so it always fires.
- **Latency measurement honesty.** `latency_ms` measures Router work, not the round-trip to the client. Clearly documented so dashboards don't misread it.

---

## 7. Phase E — Fallback classifier

### 7.1 Goal

A pure-Python `fallback_classify(message, l0_content) -> dict` that returns a conservative classification (per `spec.md §10.1`) when LiteLLM is unreachable, the call times out, or the response is unparseable.

### 7.2 Scope

**In:**
- `src/mcp_server/router/fallback_classifier.py` — pure-Python regex/keyword classifier, no LLM, no DB.
- Reuse of `fallback_keywords.py` from Phase B.
- Unit tests covering: clear bucket match, unknown bucket, project found in L0, project not in L0, HIGH-keyword detection, LOW-keyword detection, default-LOW path.
- Integration test: mock LiteLLM as failing; assert `classify()` falls through to `fallback_classify()`; assert `routing_logs.classification_mode='fallback_rules'`; assert no `llm_calls` row written for that request.

**Out:**
- ML-based fallback (out of scope for Phase 1; would be a future ADR).

### 7.3 Deliverables

| Path | Content |
|---|---|
| `src/mcp_server/router/fallback_classifier.py` | Pure-Python classifier. |
| `tests/router/test_fallback_classifier.py` | All 7 cases above + failure-mode integration. |

### 7.4 Done when

- `fallback_classify()` returns a valid classification dict (matching `spec.md §5.1` schema) for all 7 unit-test cases.
- Confidence is always `0.4` (per spec).
- Complexity never returns `HIGH` — capped at `MEDIUM` per `spec.md §10.1`.
- Integration test verifies the fallback path triggers correctly under each of: LiteLLM timeout, LiteLLM connection refused, LiteLLM 5xx, malformed JSON response, schema-invalid JSON response.
- `pytest tests/router/test_fallback_classifier.py -v` exits 0.

### 7.5 Risk notes

- **Keyword list drift.** As new buckets/projects/skills are added, the keyword list must update. This is acceptable cost: when the operator adds a new project, they update L0, run the L0 budget check, and if relevant add a keyword. This is documented in the runbook (Phase D deliverable).

---

## 8. Phase F — Tuning (post-30-day, post-Module-4-exit)

### 8.1 Goal

Empirical tuning of complexity thresholds, top-K values, sub-bucket detection, and confidence floors based on 30+ days of `routing_logs` and `user_satisfaction` data. This phase is operational, not a build phase. It does not block Module 4 exit.

### 8.2 Scope

**In:**
- A weekly query suite (the 3 audit queries from `spec.md §9.3` plus 5 additional tuning queries) run by the operator or via Dream Engine summary.
- A backlog item to revisit each open question from `spec.md §13` after 30 days.
- A criterion: when any open question has clear empirical signal (e.g., HIGH top-K should be 7 not 5 because top-5 gets `user_satisfaction < 3` consistently), open a code change PR with the data attached.

**Out:**
- Automatic auto-tuning. The operator decides; the system surfaces evidence.

### 8.3 Deliverables

| Path | Content |
|---|---|
| `runbooks/router_tuning.md` | The 8 tuning queries + decision criteria for each. |
| Lessons | Each tuning decision becomes a lesson logging the data + the change. |

### 8.4 Done when

This phase has no exit gate. It is ongoing. Module 4 ships with `runbooks/router_tuning.md` written but the tuning iterations happen for the life of the project.

---

## 9. Phase ordering & parallelism

| Calendar slot | Work in flight |
|---|---|
| Slot 1 | A (Classifier) ‖ B (Layer loader) ‖ E (Fallback). All three start together. |
| Slot 2 | A finishes → C (Source priority) starts. B continues. E finishes. |
| Slot 3 | B finishes → C wraps up. A+B+C+E all done. |
| Slot 4 | D (Telemetry) integrates everything. e2e test. |
| Slot 5 | M4.T9.x — runbook + tag + commit. |
| (Post-exit) | F starts and never finishes. |

Concrete invariant: nobody writes `router.py` (the orchestrator) until A, B, C, E all have green tests. The orchestrator is integration code, not feature code.

---

## 10. Module 4 exit gate (re-stating `plan.md §6 Module 4 Done when`)

When all six phases above have their gates met (F is exempt — it's ongoing), Module 4 is done iff:

- Router code in `src/mcp_server/router/` implements the 6 responsibilities per `CONSTITUTION §2.2`.
- Classification via `classifier_default` returns the schema for all 10 test inputs.
- Layer loader respects budgets per `CONSTITUTION §2.3`.
- Source priority resolution implemented per `CONSTITUTION §2.7`.
- `routing_logs` populated on every call with all telemetry fields.
- Fallback to rule-based classifier when LiteLLM unreachable; sets `classification_mode='fallback_rules'`.
- Smoke tests: known-bucket query returns that bucket's L1 + relevant L2 + L4 lessons; unknown topic returns L0 + L1 only.
- Per-turn latency under 2 seconds for HIGH complexity.
- Runbook at `runbooks/module_4_router.md` covers LiteLLM/classifier outages, classification debugging, budget overruns, switching providers via config.yaml.
- Commit + tag `module-4-complete` per `tasks.md M4.T9.3`.

---

## 11. Open questions deferred from `spec.md §13`

Each tracked here so they get a task in `tasks.md` rather than vanishing.

| # | Question | Deferred to | Resolved when |
|---|---|---|---|
| 1 | Sub-bucket detection signal: dotted path in classification vs second-pass keyword scan | Phase A prompt-engineering iteration | Classifier prompt produces dotted paths reliably across all 5 LiteLLM-aliased providers |
| 2 | Top-K values for L4 (HIGH=5, MEDIUM=3) | Phase F | 30 days of `user_satisfaction` data shows the right K |
| 3 | Session ledger window (3 turns) | Phase F | A/B test shows window N improves classification accuracy |
| 4 | Summarization prompt for over-budget layers | Phase B | Prompt handles 5 representative over-budget cases without losing core facts |
| 5 | Sustained low-confidence alerting | Phase F | Operator decides whether to pursue based on observed pattern |
| 6 | Provider drift detection on alias change | Phase F | If observed in production, becomes a new task |

These six items become rows in `tasks.md` (M4.T1.3 deliverable) tagged `defer-to-phase-F` or `defer-within-phase-X`.

---

## 12. Doc registry

This file is registered as `specs/router/plan.md` in `docs/PROJECT_FOUNDATION.md §6 Doc registry` (added by M4.T1.3 commit).

**End of plan.md.**
