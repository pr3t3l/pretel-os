# specs/router/tasks.md

**Module:** Router
**Status:** Draft (M4.T1.3)
**Last updated:** 2026-04-27
**Authority:** `specs/router/spec.md`, `specs/router/plan.md`, `CONSTITUTION.md §6 rule 31` (every task < 30 min)

> **Task gate (SDD §6 rule 31):** Every unchecked `[ ]` below must be completable in under 30 minutes by an operator with the spec + plan + repo loaded. If a task balloons past 30 min, stop, split it into smaller tasks, and revisit. Per CONSTITUTION §6 rule 32: two consecutive task failures halt implementation and the spec is revisited before any further attempt.

---

## 0. How to read this file

Tasks are grouped by phase (A–F) per `plan.md §2`. Each task has:
- A unique ID: phase letter + sequential number (`A.1`, `B.1`, etc.).
- A short action title.
- A "done when" clause (always testable).
- A cross-reference to the parent `tasks.md` row in the repo root (e.g. `→ M4.T2.2`) when applicable. The parent row is checked when all its sub-tasks here complete.

The first unchecked `[ ]` in this file is the active task. Always.

Tasks within a phase can usually be done in order, but where parallelism exists per `plan.md §9`, it is noted at the phase header.

---

## Phase A — Classifier

**Plan reference:** `plan.md §3`. Parallelizable with B and E. Blocking for C and D.

### A.1 — Skeleton

- [x] **A.1.1** Create directory `src/mcp_server/router/` and `src/mcp_server/router/prompts/`.
  - Done when: both directories exist with `__init__.py` files (empty is fine for `prompts/`).

- [x] **A.1.2** Create `src/mcp_server/router/exceptions.py` with the four typed exceptions: `ClassifierTimeout`, `ClassifierTransportError`, `ClassifierParseError`, `ClassifierSchemaError`. All inherit from a base `ClassifierError`.
  - Done when: `from src.mcp_server.router.exceptions import ClassifierTimeout` works in a Python REPL on the Vivobook.

### A.2 — Prompt authoring

- [x] **A.2.1** Author `src/mcp_server/router/prompts/classify.txt` v1 — system prompt that instructs the model to emit JSON matching `spec.md §5.1`. Include bucket list, complexity rubric, and 3 in-prompt examples (one per complexity level). → M4.T2.1
  - Done when: file exists, ≤ 1,800 tokens, contains explicit JSON schema, contains 3 examples.

- [x] **A.2.2** Validate the prompt loads under 2k tokens via `tiktoken`. → M4.T2.1
  - Done when: `python -c "import tiktoken; enc=tiktoken.get_encoding('cl100k_base'); print(len(enc.encode(open('src/mcp_server/router/prompts/classify.txt').read())))"` returns < 2000.

### A.3 — Test examples

- [x] **A.3.1** Create `tests/router/classification_examples.md` with 10 worked examples covering: 3 buckets × 3 complexity levels + 1 ambiguous edge case. Each example shows input message + expected JSON output.  → M4.T2.1
  - Done when: file has 10 example sections, each with `**Input:**` and `**Expected output:**` blocks, and the schema in every expected output is valid against `spec.md §5.1`.

### A.4 — LiteLLM client

- [x] **A.4.1** Implement `src/mcp_server/router/litellm_client.py` — thin wrapper around the OpenAI SDK pointing at `http://127.0.0.1:4000`. Reads `LITELLM_API_KEY` from env. Single function `chat_json(model_alias, system, user, timeout_ms, max_tokens) -> dict`.
  - Done when: a manual smoke call against `classifier_default` returns a JSON response with `ping → pong` style content.

- [x] **A.4.2** Add a 1-retry policy in `litellm_client.py` for transport errors (connection refused, 5xx). No retry on parse errors.
  - Done when: unit test with mocked failing-then-succeeding transport returns success on second attempt; with persistently failing transport raises `ClassifierTransportError`.

- [x] **A.4.3 — Truncation detection, telemetry, and defensive JSON parsing**
    - [x] Add `ClassifierTruncatedError` and `ClassifierContentFilterError` to `exceptions.py` with telemetry kwarg
    - [x] Add `telemetry` kwarg to existing 5 exception classes (backward compatible default None)
    - [x] Add `ChatJsonTelemetry` dataclass to `litellm_client.py`
    - [x] Refactor `chat_json` to return tuple `(dict, telemetry)` with finish_reason classification, defensive token extraction, markdown fence stripping
    - [x] Raise `ClassifierTruncatedError` on `finish_reason='length'` with `truncation_cause` derived from reasoning vs visible tokens
    - [x] Raise `ClassifierContentFilterError` on `'content_filter'`
    - [x] Raise `ClassifierTransportError` on unexpected finish_reason values (e.g. Gemini RECITATION)
    - [x] Update 3 existing tests to expect tuple return
    - [x] Add 6 new mocked tests covering truncation, content filter, unknown finish_reason, markdown fences, and LiteLLM bug #18896
    - [x] Add 1 integration test against live `classifier_default` (Haiku 4.5)

### F.x — Observational: classifier markdown-fence rate (deferred from A.4.4)

After A.5+ ships and routing_logs accumulate ~1 week of real classifier
calls, query `routing_logs` for the rate at which `provider_metadata`
shows the model emitted markdown fences (defensive stripper kicked in).
If rate < 5%, leave the prompt as-is. If rate > 20%, prompt-engineer
the anti-fences instruction (move to top of prompt, all-caps, repeat).
Note: classify.txt already has the instruction at the bottom; A.4.3
integration test confirmed the stripper handles fences cleanly when
they slip through.

### A.5 — Classifier integration

- [x] **A.5.1** Implement `src/mcp_server/router/classifier.py::classify(message, l0_content, session_excerpt)` — assembles the input, calls `litellm_client.chat_json('classifier_default', ...)`, parses response, validates against schema. → M4.T2.2
  - Done when: function returns a valid dict for the first example in `classification_examples.md` when called against the live LiteLLM proxy.
  - Live integration against the 10 worked examples is deferred to A.6.1; A.5.1 ships with mocked unit tests in `tests/router/test_classifier.py`.

- [x] **A.5.2** Implement strict schema validation in `classifier.py`: `bucket` ∈ {personal, business, scout} or `null`; `complexity` ∈ {LOW, MEDIUM, HIGH}; `confidence` ∈ [0.0, 1.0]; `needs_lessons` is bool. Anything else → `ClassifierSchemaError`. → M4.T2.2
  - Done when: unit test with hand-crafted invalid responses (wrong bucket name, missing field, wrong type) raises `ClassifierSchemaError` for each case.
  - Implemented inline with A.5.1 via `_validate_response` (single source of truth, runs on every classify call). v1 also enforces `project=null` and `skill=null` per spec.md §5.1.

- [x] **A.5.3** Add `request_id` parameter to `classify()` so it can be threaded through to telemetry later (Phase D). For now, it is just accepted and ignored.
  - Done when: signature accepts `request_id: str | None = None` without breaking existing calls.
  - Implemented inline with A.5.1; full Phase D telemetry threading happens when routing_logs writer ships.

### A.6 — Tests

- [x] **A.6.1** Write `tests/router/test_classifier.py` happy-path tests against all 10 examples in `classification_examples.md`. Use the live LiteLLM proxy (integration test, not mocked). → M4.T2.2
  - Done when: `pytest tests/router/test_classifier.py::test_examples -v` passes 10/10.
  - Implemented as `tests/router/test_classifier_eval.py` with `@pytest.mark.eval`. Run via `pytest -m eval`. Report persisted to `tests/router/eval_results/eval_<UTC>.json`. Thresholds: bucket ≥ 0.80, complexity ≥ 0.70, schema_violations = 0.
  - Cost per run: ~$0.003 against Claude Haiku 4.5.

- [ ] **A.6.2** Write `tests/router/test_classifier.py` failure-mode tests: timeout (mocked), transport error (mocked), malformed JSON (mocked), schema-invalid response (mocked).
  - Done when: each failure mode raises the correct typed exception per A.1.2.

### A.7 — Phase A gate

- [ ] **A.7.1** Verify `plan.md §3.4 Done when` line by line. All bullets must hold.
  - Done when: a checklist run against §3.4 returns 4/4 pass.

- [ ] **A.7.2** Tag the codebase locally `phase-a-complete` (lightweight tag, not pushed) so we can `git diff phase-a-complete` later.
  - Done when: `git tag phase-a-complete` succeeds.

---

## Phase B — Layer loader  ✅ COMPLETE 2026-04-29

> ⚠️ **Status: SUPERSEDED ARCHITECTURE.** The atomic B.x tasks below were
> authored 2026-04-27 against a pre-M0.X file-based loader architecture
> (`LayerPayload` dataclass, file reads from `buckets/<bucket>/README.md`
> for L1, etc.). The M4.reconcile commit (`8ac5ff1`, 2026-04-29) realigned
> Phase B with `specs/module-0x-knowledge-architecture/layer_loader_contract.md`:
> loaders read from Postgres tables, the output type is `LayerBundle` /
> `LayerContent` / `ContextBlock`, and the orchestrator is `assemble_bundle`
> (async with sync conn).
>
> Phase B shipped via the post-reconcile atomic tracker at
> `specs/router/phase_b_close.md` (B.1 → B.9, all 14 atomic tasks). Final
> commits: `83190af` (B.1) → `97a67d6` (B.9). Tag candidate
> `phase-b-complete` points at `97a67d6`.
>
> The legacy B.x checkboxes below remain unchecked because their
> *descriptions* (e.g. "Reads `identity.md` from repo root", "Reads
> `buckets/{bucket}/README.md`") no longer describe the shipped code.
> They are kept as historical context. For the actual atomic tasks
> shipped, read `specs/router/phase_b_close.md`.

**Plan reference:** `plan.md §4` (post-reconcile). Parallelizable with A and E. Blocking for C.

### B.1 — Types and shared keywords

- [ ] **B.1.1** Create `src/mcp_server/router/types.py` with `LayerPayload` dataclass: `layer: str, content: str, tokens: int, source_path: str, module: str | None = None, sub_bucket: str | None = None, over_budget: bool = False`.
  - Done when: `from src.mcp_server.router.types import LayerPayload` works.

- [ ] **B.1.2** Create `src/mcp_server/router/fallback_keywords.py` with `BUCKET_KEYWORDS` dict (3 buckets × ~6 keywords each, derived from `identity.md` content) and `COMPLEXITY_KEYWORDS` dict (`HIGH`, `LOW` lists).
  - Done when: file exists, contains both dicts, every value is a list of strings.

- [ ] **B.1.3** Add `count_tokens(text: str) -> int` helper in `src/mcp_server/router/tokens.py` using `tiktoken cl100k_base`.
  - Done when: `count_tokens("hello")` returns a small positive integer.

### B.2 — L0 loader

- [ ] **B.2.1** Implement `load_l0() -> LayerPayload` in `src/mcp_server/router/layer_loader.py`. Reads `identity.md` from repo root, counts tokens, returns payload.
  - Done when: function returns a valid payload with `layer='L0'`, `tokens > 0`, `over_budget=False` (assuming current `identity.md` ≤ 1,200 tok).

- [ ] **B.2.2** Add over-budget detection: if tokens > 1,200, set `over_budget=True` (do not summarize yet — that's B.7).
  - Done when: unit test with a synthetic 2k-token L0 file returns `over_budget=True`.

### B.3 — L1 loader

- [ ] **B.3.1** Implement `load_l1(bucket: str | None) -> LayerPayload | None`. Reads `buckets/{bucket}/README.md`. Returns `None` if `bucket is None`. Raises `FileNotFoundError` if the bucket is named but the file does not exist.
  - Done when: returns valid payload for `bucket='business'` (assuming the file exists); returns `None` for `bucket=None`; raises for unknown bucket.

- [ ] **B.3.2** Add sub-bucket support: if `bucket` contains a slash (e.g., `business/freelance`), load `buckets/business/freelance/README.md` instead. Per `spec.md §6.2`.
  - Done when: unit test with synthetic sub-bucket folder and dotted-path bucket returns the sub-bucket README.

### B.4 — L2 loader

- [ ] **B.4.1** Implement `load_l2(bucket: str | None, project: str | None, module: str | None = None) -> LayerPayload | None`. Reads `buckets/{bucket}/projects/{project}/README.md` always; optionally appends one module file from `modules/{module}.md` when `module` is provided. Per `spec.md §6.3`.
  - Done when: returns project README + 1 module for `(business, declassified, distribution)`; returns project README only for `(business, declassified, None)`; returns `None` if either bucket or project is None.

- [ ] **B.4.2** Reject multi-module loads: if `module` is a list/tuple instead of a string, raise `ValueError`. Per CONSTITUTION §5.6 rule 29.
  - Done when: unit test with `module=['m1', 'm2']` raises ValueError.

### B.5 — L3 loader

- [ ] **B.5.1** Implement `load_l3(skill: str | None) -> LayerPayload | None`. Reads `skills/{skill}.md`. Returns `None` for `skill=None`. Raises if file missing.
  - Done when: returns valid payload for known skill; returns `None` for `skill=None`; raises for unknown skill.

### B.6 — L4 loader (lessons)

- [ ] **B.6.1** Implement `load_l4(query: str, bucket: str | None, tags: list[str], top_k: int) -> LayerPayload | None`. Calls `search_lessons` (existing MCP tool from Module 3) with filter-first semantics.
  - Done when: returns top-K lesson dicts for a known bucket+tag combination; returns empty `lessons=[]` payload (not None) when no matches; returns `None` only when classification did not request lessons.

- [ ] **B.6.2** Verify filter-first execution at SQL level. Run `EXPLAIN ANALYZE` on the underlying query and confirm the bucket/tag filter applies before vector sort. Per CONSTITUTION §5.6 rule 26.
  - Done when: query plan output saved to `tests/router/explain_l4.txt` showing filter as the first reductive step.

### B.7 — Summarization fallback for over-budget content

- [ ] **B.7.1** Author `src/mcp_server/router/prompts/summarize.txt` — compression prompt that takes content + target token count, returns a summary preserving facts and structure.
  - Done when: file exists, ≤ 800 tokens, contains 1 example showing in/out.

- [ ] **B.7.2** Implement `summarize_oversize(content: str, target_tokens: int) -> str` in `layer_loader.py`. Calls `litellm_client.chat_json('classifier_default', ...)` with the summarize prompt.
  - Done when: a synthetic 3k-token input is summarized to ≤ target_tokens for at least 4 of 5 trial runs (some non-determinism is acceptable).

- [ ] **B.7.3** Wire `summarize_oversize` into each loader: when `tokens > budget`, summarize to 80% of budget, set `over_budget=True`, write a `gotcha` row to DB suggesting refactor.
  - Done when: integration test with synthetic over-budget L1 file returns summarized payload + 1 new gotcha row in DB.

### B.8 — Tests

- [ ] **B.8.1** Write `tests/router/test_layer_loader.py` covering all 5 loaders × 4 cases each (happy path, missing file, empty file, over-budget). Total ≥ 20 tests.
  - Done when: `pytest tests/router/test_layer_loader.py -v` passes 20/20.

### B.9 — Phase B gate

- [ ] **B.9.1** Verify `plan.md §4.4 Done when` line by line. All bullets must hold including the query-plan check.
  - Done when: checklist 6/6 pass.

- [ ] **B.9.2** Tag locally `phase-b-complete`.
  - Done when: tag exists.

---

## Phase C — Source priority resolution

**Plan reference:** `plan.md §5`. Blocked by B. Blocking for D.

### C.1 — Topic catalog

- [ ] **C.1.1** Create `src/mcp_server/router/topics.py` with initial topic list of ~10 entries hand-curated from CONSTITUTION + ADRs. Each topic is `{name, keywords, expected_layers}`. Examples: `default-database`, `embeddings-model`, `bucket-classification`, `model-to-task`, `caching-strategy`.
  - Done when: file exists with ≥ 10 topic entries.

### C.2 — Conflict detection

- [ ] **C.2.1** Implement `detect_conflicts(layers: dict[str, LayerPayload]) -> list[Conflict]` in `src/mcp_server/router/conflict_resolver.py`. For each topic in `topics.py`, scan loaded layers for keyword presence. When ≥ 2 layers mention the topic, run a cosine-similarity check on the relevant chunks. If similarity < 0.7, mark as a conflict.
  - Done when: synthetic test with 2 layers carrying contradictory text on `default-database` returns 1 conflict.

- [ ] **C.2.2** Define the `Conflict` dataclass: `{topic, winning_source, winning_text, losing_sources: list[{layer, text}]}`.
  - Done when: dataclass exists in `types.py`.

### C.3 — Invariant enforcement

- [ ] **C.3.1** Implement `enforce_invariants(layers: dict[str, LayerPayload]) -> list[InvariantViolation]`. Checks each layer's content against the immutable invariant class per `spec.md §8.1`:
  - Scout denylist (cross-reference existing pre-commit Scout filter from Module 1).
  - Token-budget ceilings (already enforced by B.7, but defensive recheck).
  - Git/DB boundary (no DB-only entities documented as if they were git-stable).
  - Agent rule mentions in CONSTITUTION §9 must not be contradicted.
  - Done when: synthetic L4 lesson saying "you can guess MCP tool params if confidence is high" triggers an invariant violation.

- [ ] **C.3.2** When invariant violation detected, drop the offending content from the layer (replace with a marker `[content removed: invariant violation — reason X]`) and add to `source_conflicts` with reason `'invariant_violation'`.
  - Done when: integration test confirms the offending text is replaced and the conflict is logged.

### C.4 — Priority application

- [ ] **C.4.1** Implement `apply_priority(conflicts: list[Conflict]) -> list[ResolvedConflict]`. For each conflict, set `winning_source` to the highest-priority layer per `spec.md §8.2` order: L2 > L3 > L4 > L1 > L0.
  - Done when: synthetic conflict between L4 and L1 returns L4 as winner; conflict between L2 and L4 returns L2 as winner.

### C.5 — Tests

- [ ] **C.5.1** Write `tests/router/conflict_examples.md` with 5 hand-written examples covering: L2-vs-L4, L3-vs-L1, L4-vs-L1, invariant violation in L4, invariant violation in L0 contextual section.
  - Done when: file exists with 5 example sections.

- [ ] **C.5.2** Write `tests/router/test_conflict_resolver.py` with at least one test per topic in `topics.py` plus the 5 examples from C.5.1.
  - Done when: `pytest tests/router/test_conflict_resolver.py -v` passes.

### C.6 — Phase C gate

- [ ] **C.6.1** Verify `plan.md §5.4 Done when`.
  - Done when: 4/4 pass.

- [ ] **C.6.2** Tag `phase-c-complete`.
  - Done when: tag exists.

---

## Phase E — Fallback classifier

**Plan reference:** `plan.md §7`. Parallelizable with A and B. Blocking for D's failure-mode tests.

(Listed before D because D consumes E's API.)

### E.1 — Implementation

- [ ] **E.1.1** Implement `src/mcp_server/router/fallback_classifier.py::fallback_classify(message: str, l0_content: str) -> dict`. Pure Python, no LLM, no DB. Algorithm per `spec.md §10.1`. → M4.T6.1
  - Done when: function returns a valid classification dict for a sample message; confidence is hard-coded `0.4`; complexity never returns HIGH.

- [ ] **E.1.2** Project-name extraction: scan `l0_content` for project slugs (assume L0 carries a `## Projects` section with bullet list). When the message mentions a slug, set `project=<slug>`. Otherwise `project=None`.
  - Done when: synthetic L0 with project list + message mentioning one project returns that project.

### E.2 — Tests

- [ ] **E.2.1** Write `tests/router/test_fallback_classifier.py` with 7 cases per `plan.md §7.4`: clear bucket match, unknown bucket, project found in L0, project not in L0, HIGH-keyword detection, LOW-keyword detection, default-LOW path. → M4.T6.1
  - Done when: `pytest tests/router/test_fallback_classifier.py -v` passes 7/7.

- [ ] **E.2.2** Add integration test that mocks LiteLLM as failing (timeout, connection refused, 5xx, malformed JSON, schema-invalid JSON — 5 mocks) and verifies `classify()` falls through to `fallback_classify()` for each. → M4.T6.1
  - Done when: 5 mocked failure scenarios all result in `classification_mode='fallback_rules'`.

### E.3 — Phase E gate

- [ ] **E.3.1** Verify `plan.md §7.4 Done when`.
  - Done when: 4/4 pass.

- [ ] **E.3.2** Tag `phase-e-complete`.
  - Done when: tag exists.

---

## Phase D — Telemetry & orchestration

**Plan reference:** `plan.md §6`. Blocked by A, B, C, E.

### D.1 — Telemetry primitives

- [ ] **D.1.1** Create `src/mcp_server/router/telemetry.py::start_request(message, session_id, client_origin) -> RequestContext`. Generates `request_id`, starts latency timer, returns a context object passed through downstream calls.
  - Done when: function returns a `RequestContext` with valid UUID and `start_time`.

- [ ] **D.1.2** Implement `log_classification(ctx, classification, mode, llm_call_data)`. Writes the classification JSON + mode to `routing_logs`; if `mode='llm'` writes the `llm_calls` row joinable on `request_id`.
  - Done when: integration test runs once, asserts 1 row in `routing_logs` and 1 row in `llm_calls` with matching `request_id`.

- [ ] **D.1.3** Implement `log_layers(ctx, layers_loaded, tokens_per_layer, over_budget_layers)`.
  - Done when: integration test asserts the columns are populated correctly.

- [ ] **D.1.4** Implement `log_rag(ctx, rag_expected, rag_executed, lessons_returned, tools_returned)`.
  - Done when: integration test asserts the columns.

- [ ] **D.1.5** Implement `log_conflicts(ctx, source_conflicts)`.
  - Done when: integration test asserts the JSONB column carries the conflict array.

- [ ] **D.1.6** Implement `log_completion(ctx, degraded_mode, degraded_reason, latency_ms)` wrapped in try/finally semantics so it always fires even on partial failure.
  - Done when: integration test where the orchestrator raises mid-flight still results in a `routing_logs` row with `degraded_mode=true`.

### D.2 — Orchestrator

- [ ] **D.2.1** Implement `src/mcp_server/router/router.py::get_context(message, session_id) -> ContextBundle`. Wires Phases A → B → C and uses E as fallback. Calls D for telemetry. Per `spec.md §4`.
  - Done when: function returns a valid `ContextBundle` for "help me debug my n8n batching".

- [ ] **D.2.2** Build the `ContextBundle` shape per `spec.md §4.2` exactly. Keys ordered as documented; types as documented.
  - Done when: returned bundle passes JSON schema validation against a hand-written schema in `tests/router/context_bundle_schema.json`.

### D.3 — MCP tool wrappers

- [ ] **D.3.1** Replace existing stub `src/mcp_server/tools/get_context.py` with the real Router invocation. Stub from Module 3 wrote `classification_mode='stub'`; new version writes `'llm'` or `'fallback_rules'`.
  - Done when: calling the MCP tool from Claude.ai returns a real bundle, not the stub L0-only response.

- [ ] **D.3.2** Implement `src/mcp_server/tools/report_satisfaction.py`. Updates `routing_logs.user_satisfaction` for the matching `request_id`. → M4.T7.1
  - Done when: calling `report_satisfaction(request_id, 4)` from a Claude.ai chat updates the corresponding row.

### D.4 — End-to-end test

- [ ] **D.4.1** Write `tests/router/test_e2e.py::test_n8n_debug_query`. Calls `get_context("help me debug my n8n batching")` and asserts: bucket=business, complexity ∈ {MEDIUM, HIGH}, L4 lessons contain a tag matching `n8n`, total tokens within budgets. → M4.T8.1
  - Done when: test passes against the live system.

- [ ] **D.4.2** Add 5 additional e2e cases: known bucket with no matching project, ambiguous message (expect fallback), pure greeting (expect LOW + L0 only), HIGH complexity recommendation request, scout-related query (expect bucket=scout with abstract content only).
  - Done when: all 6 e2e tests pass.

### D.5 — Audit queries

- [ ] **D.5.1** Run all 3 audit queries from `spec.md §9.3` against the data accumulated by the e2e test runs. → M4.T5.1
  - Done when: each query executes without error and returns at least one row with non-null aggregates.

- [ ] **D.5.2** Save the queries to `runbooks/router_audit_queries.sql` so the operator can rerun them anytime.
  - Done when: file exists with all 3 queries documented and commented.

### D.6 — Phase D gate

- [ ] **D.6.1** Verify `plan.md §6.4 Done when`.
  - Done when: 5/5 pass.

- [ ] **D.6.2** Tag `phase-d-complete`.
  - Done when: tag exists.

---

## Phase F — Tuning artifacts (Module 4 deliverables only; ongoing work post-exit)

**Plan reference:** `plan.md §8`. No exit gate per plan.md §8.4; this is operational. The tasks below are the *artifacts* Module 4 must ship to enable Phase F work; the *iterations* themselves are ongoing.

### F.1 — Runbook

- [ ] **F.1.1** Write `runbooks/router_tuning.md` with the 3 audit queries from `spec.md §9.3` plus 5 additional tuning queries: per-bucket classification accuracy, per-model latency distribution, sub-bucket detection rate, fallback rate by hour-of-day, low-confidence cluster detection.
  - Done when: file exists with 8 queries, each commented with its purpose and decision criteria.

### F.2 — Open questions

- [ ] **F.2.1** Track all 6 open questions from `spec.md §13` as rows in this file under `## Phase F deferred`. Each row has the question, the resolution criterion, and the data source needed.
  - Done when: section exists with 6 rows.

---

## Phase F deferred (tracking, not gated)

| # | Question | Resolution criterion | Data needed |
|---|---|---|---|
| 1 | Sub-bucket detection signal — dotted path vs second-pass keyword scan | Classifier prompt produces dotted paths reliably across all 5 LiteLLM-aliased providers | A/B test results across providers |
| 2 | Top-K for L4 (HIGH=5, MEDIUM=3) | 30 days of `user_satisfaction` data shows the right K | `routing_logs` + `user_satisfaction` |
| 3 | Session ledger window (3 turns) | A/B test shows window N improves classification accuracy | Synthetic A/B with held-out test set |
| 4 | Summarization prompt for over-budget layers | Prompt handles 5 representative over-budget cases without losing core facts | Sample of over-budget content from production |
| 5 | Sustained low-confidence alerting | Operator decides whether to pursue based on observed pattern | `confidence` distribution from `routing_logs.classification` |
| 6 | Provider drift detection on alias change | If observed in production, becomes a new task | Before/after `user_satisfaction` deltas |

---

## Module 4 exit (parent tasks.md M4.T9.x cross-reference)

These are the parent tasks.md rows that close Module 4. Each completes when the phase work above completes.

- [ ] **M4.T9.1 (parent)** Verify gate from `plan.md §6 Module 4`. → confirmed by all phase gates A.7, B.9, C.6, D.6, E.3 passing.
- [ ] **M4.T9.2 (parent)** Write `runbooks/module_4_router.md` — debugging classifications, LiteLLM/`classifier_default` outage handling, switching providers via config.yaml.
  - Sub-task: F.1.1 (router_tuning runbook) feeds this file.
  - Done when: file exists with 5 sections (overview, classification debugging, LiteLLM outage triage, switching providers, audit queries reference).
- [ ] **M4.T9.3 (parent)** Commit + tag `module-4-complete`.
  - Done when: clean working tree, tag exists, pushed to origin.

---

## Cross-reference table — parent ↔ phase

For tracking against the parent `tasks.md` checklist:

| Parent task | Sub-tasks here |
|---|---|
| M4.T2.1 | A.2.1, A.2.2, A.3.1 |
| M4.T2.2 | A.5.1, A.5.2, A.5.3, A.6.1, A.6.2 |
| M4.T2.3 | (no sub-tasks; deferred per ADR-020 — task is "instrument tokens-in/out per call") covered by D.1.2 + D.5.1 |
| M4.T3.1 | B.2 through B.6 (all loader tasks) |
| M4.T4.1 | C.1 through C.5 (all conflict resolver tasks) |
| M4.T5.1 | D.1.1 through D.1.6, D.5.1, D.5.2 |
| M4.T6.1 | E.1.1, E.1.2, E.2.1, E.2.2 |
| M4.T7.1 | D.3.2 |
| M4.T8.1 | D.4.1, D.4.2 |
| M4.T9.1 | All phase gates (A.7.1, B.9.1, C.6.1, D.6.1, E.3.1) |
| M4.T9.2 | F.1.1 |
| M4.T9.3 | Final tag and commit |

---

## Active task pointer

**The first unchecked `[ ]` above is where the operator is.** As of this draft, that is **A.1.1** (create the `router/` directory).

When implementation starts, the operator updates `SESSION_RESTORE.md §13` with the current task ID after each work session.

---

## Doc registry

This file is registered as `specs/router/tasks.md` in `docs/PROJECT_FOUNDATION.md §6 Doc registry` (added by the M4.T1.3 commit).

**End of tasks.md.**
