# specs/router/phase_d_close.md — Phase D+E close-out (D.0–D.5)

**Module:** Router
**Status:** Not started — atomic groups D.0–D.5 below.
**Authority:** `specs/router/spec.md` §4 (public interface), §5 (classification), §9 (telemetry contract), §10 (failure modes). `specs/router/plan.md` §6 (Phase D scope), §7 (Phase E scope), §9 (ordering invariant). `layer_loader_contract.md` §10 (bundle shape). `CONSTITUTION.md` §8.43 (degraded mode).
**Scope:** Six atomic groups to close Phase D (and bundled Phase E). After D.5 ships, M4 Phases D+E are done; tag candidates `phase-e-complete` + `phase-d-complete`. Module 4 exit gate tasks (M4.T9.x) are unblocked.

---

## 0. Why this doc exists

### 0.1 What Phase D does — the big picture

Phases A through C built isolated components:

- **Phase A** — a classifier that reads a message and says "this is
  bucket=business, complexity=HIGH, needs_lessons=true."
- **Phase B** — a layer loader that, given classifier signals, assembles
  a `LayerBundle` with L0–L4 context.
- **Phase C** — an invariant detector that scans a `LayerBundle` for
  CONSTITUTION violations and returns a list.

But **nothing connects them yet.** There is no function that takes a raw
user message, runs A→B→C in order, logs everything, handles failures,
and returns a final result to the MCP client.

**Phase D is the wiring phase.** It builds two things:

1. **The Router orchestrator (`router.py`)** — the function `get_context()`
   that is the single entry point for the entire Router. It calls
   classify → assemble_bundle → detect_invariant_violations, handles
   every failure mode from spec §10, and returns a `ContextBundle` dict.

2. **The telemetry system (`telemetry.py`)** — functions that write to
   `routing_logs` and `llm_calls` tables at each step of the pipeline,
   so every `get_context` call leaves an audit trail.

Plus two thin MCP tool wrappers (`get_context.py` replaces the Module 3
stub, `report_satisfaction.py` is new), and the end-to-end tests that
prove everything works together.

### 0.2 Phase E bundled as D.0

`plan.md §9` states: _"Concrete invariant: nobody writes `router.py`
(the orchestrator) until A, B, C, E all have green tests."_

Phase E (fallback classifier) is not done. Without it, the orchestrator
cannot handle the degraded path when LiteLLM is unreachable (spec §10
row 1). Phase E is small (~120 LoC, pure Python, no LLM, no DB, $0
cost), so it is bundled here as D.0 to satisfy the plan §9 invariant
without requiring a separate close-out document.

### 0.3 Relationship to legacy tasks in `tasks.md`

Unlike Phase C (whose legacy tasks were completely wrong post-rescope),
Phase D's legacy tasks (lines 298–362) and Phase E's legacy tasks
(lines 266–296) are **mostly aligned** with the current scope. This doc
**extends** them with post-Phase-B/C adaptations (real type names,
async/sync boundaries, invariant detection integration). The cleanup at
D.5 marks them complete with commit hashes — no "SUPERSEDED" banner
needed.

---

## 1. Decisions taken (Q1–Q9)

### Q1 — Phase E bundled as D.0

**Decision:** Phase E fallback classifier ships as D.0 atomic group
within this Phase D close-out. Plan §7's Phase E gate is verified at
the end of D.0, not as a separate phase.

**Rationale:** Plan §9 invariant requires E tests green before D starts.
E is small (2 implementation tasks + 2 test tasks per `tasks.md` E.x).
Splitting into a separate doc creates overhead (separate briefing,
separate commit chain, separate tasks.md cleanup) that exceeds the work
itself. Bundling is cleaner.

**Trade-off:** Phase E's tag (`phase-e-complete`) must be created before
`phase-d-complete`. Both are created in D.5.

### Q2 — Telemetry write strategy: INSERT early, UPDATE per step

**Decision:** `start_request()` creates the `routing_logs` row
immediately with just `request_id`, `message_excerpt`, `session_id`,
`client_origin`, and `created_at`. Each subsequent `log_*()` function
UPDATEs the same row adding its slice of columns. `log_completion()`
is the final UPDATE (latency_ms, degraded_mode, degraded_reason).

**What this means in practice:**

```
Step 1: start_request() → INSERT INTO routing_logs (request_id, message_excerpt, ...)
Step 2: log_classification() → UPDATE routing_logs SET classification=..., classification_mode=...
Step 3: log_layers() → UPDATE routing_logs SET layers_loaded=..., tokens_per_layer=...
Step 4: log_rag() → UPDATE routing_logs SET rag_expected=..., rag_executed=...
Step 5: log_conflicts() → UPDATE routing_logs SET source_conflicts=...
Step 6 (always, via try/finally): log_completion() → UPDATE routing_logs SET latency_ms=..., degraded_mode=...
```

**Why not accumulate in memory and do a single INSERT at the end?**

If the process crashes at step 3 (e.g., DB error during layer loading),
the single-INSERT approach loses ALL data — no record that the request
ever happened. With INSERT-early, steps 1 and 2 are already committed
to the DB. The partial row (with `degraded_mode=NULL`) is still
valuable for debugging.

Step 6 (`log_completion`) always fires because the orchestrator wraps
steps 2–5 in a try/finally block. Even on crash, the row gets
`degraded_mode=true` and `degraded_reason` explaining what failed.

**Alternatives rejected:**
- Single INSERT at end. Loses data on crash.
- Write-ahead log to a file, then INSERT. Overengineered for
  current scale.

### Q3 — ContextBundle is a plain dict, not a dataclass

**Decision:** `router.get_context()` returns a plain `dict` matching
`spec.md §4.2` exactly. No new dataclass in `types.py`. The `bundle`
key holds `dataclasses.asdict(layer_bundle)`. The MCP tool
(`get_context.py`) returns this dict directly — no re-serialization.

**Why not a dataclass?**

1. **spec §4.2 defines the shape as JSON.** The MCP transport returns
   JSON. A dataclass would be immediately converted to dict at the
   boundary — wasted indirection.
2. **JSON schema validation** (legacy task D.2.2) validates dicts, not
   dataclasses. A `tests/router/context_bundle_schema.json` file
   directly validates the return value.
3. **`types.py` is for contract-level types** (`LayerBundle`,
   `InvariantViolation`). The ContextBundle is Router-internal
   packaging, not a cross-phase contract.

**Trade-off:** No mypy coverage on the dict structure. Mitigated by the
JSON schema test in D.4.

### Q4 — Router `get_context()` is async

**Decision:** `async def get_context(conn, message, session_id,
client_origin, repo_root, cache) -> dict`. Async because
`assemble_bundle()` (Phase B) is async (it calls `embed()` and
`summarize_oversize()`).

The function accepts a sync `psycopg.Connection` (same pattern as
Phase B). Connection lifecycle is the MCP tool's responsibility —
`router.py` does not create or close connections.

**Alternatives rejected:**
- Sync get_context wrapping asyncio.run(). Hostile to the MCP server's
  async event loop.
- Pass an async connection. Phase B loaders are all sync; changing them
  is not worth it.

### Q5 — Degraded mode handling (spec §10)

**Decision:** The orchestrator wraps each major step in a try/except
that catches specific exception classes. On failure, it:
1. Sets `degraded_mode = True`
2. Appends a specific reason string to a `degraded_reasons` list
3. Continues with a fallback or reduced data

The orchestrator **never raises to the MCP tool**. It always returns a
`ContextBundle` dict — possibly degraded.

**Failure cascade (spec §10 rows, mapped to code):**

```
classify() raises ClassifierError
  → catch → call fallback_classify()
  → set classification_mode='fallback_rules'

assemble_bundle() raises Exception (DB down, file missing, etc.)
  → catch → build minimal L0-only bundle from files
  → append 'bundle_assembly_failed: {error}' to degraded_reasons

embed() fails inside assemble_bundle
  → caught internally by assemble_bundle → L4 skipped
  → over_budget_layers or degraded info comes back in BundleMetadata

detect_invariant_violations() raises Exception (should never happen, but defense)
  → catch → violations = []
  → append 'invariant_detection_failed' to degraded_reasons

telemetry log_*() raises Exception (DB write failed)
  → catch → silently continue (telemetry loss is acceptable;
    user-facing response must not fail because of logging)
```

**The try/finally pattern for log_completion:**

```python
async def get_context(conn, message, ...):
    t0 = time.monotonic()
    request_id = start_request(conn, message, session_id, client_origin)
    degraded = False
    reasons = []

    try:
        # steps 2–5 with per-step try/except
        ...
    finally:
        latency_ms = int((time.monotonic() - t0) * 1000)
        try:
            log_completion(conn, request_id, degraded,
                          '; '.join(reasons) or None, latency_ms)
        except Exception:
            pass  # telemetry loss is acceptable
```

### Q6 — LLM call metadata for `llm_calls` table

**Decision:** Claude Code must read
`src/mcp_server/router/litellm_client.py` to discover how `chat_json()`
exposes telemetry metadata (per SESSION_RESTORE: "ChatJsonTelemetry
captures truncation, cache hits, reasoning tokens, finish_reason
classification"). If `chat_json` returns metadata alongside the parsed
dict, use it. If not, modify the call path minimally.

Two acceptable adaptations:
- **(a)** `chat_json()` returns `(result_dict, metadata_dict)` tuple.
  Update `classify()` to destructure. Minimal caller change.
- **(b)** `classify()` captures the raw LiteLLM response internally and
  returns `(classification, llm_call_data)` tuple. Orchestrator
  destructures.

Claude Code picks whichever requires fewer file edits. The goal:
`llm_call_data` reaches `log_classification()` with the fields from
spec §9.2 (provider, model, input_tokens, output_tokens,
cache_read_tokens, cost_usd, latency_ms, success, error).

### Q7 — `recommend_tools` helper

**Decision:** A small helper function `recommend_tools(conn, bucket,
complexity, needs_lessons) -> list[dict]` in `router.py` (or a
separate `_tools.py` if > 30 LoC). Direct SQL query against
`tools_catalog`, ranked by `utility_score`, limited to 5 rows.

```sql
SELECT name, description, utility_score
FROM tools_catalog
WHERE kind = 'tool'
ORDER BY utility_score DESC NULLS LAST
LIMIT 5;
```

Called only when complexity is HIGH, or MEDIUM with
`needs_lessons=true` (spec §7.2). Returns `[]` for LOW complexity.

**Why not call the existing `tool_search` MCP tool?**

spec §11: _"The Router never calls ... any other MCP tool."_ The Router
assembles context; it does not invoke tools. Direct DB query is the
correct pattern.

### Q8 — Session excerpt for classifier

**Decision:** A small helper `get_session_excerpt(conn, session_id)
-> str` that queries `conversation_sessions` for the last 3 turns of
the active session. Returns empty string if `session_id` is None or
table has no matching rows.

Claude Code should verify `conversation_sessions` schema. If the table
does not store per-turn message content (it may only store session
metadata like started_at, last_seen_at), then session_excerpt is empty
for now and this becomes a deferred follow-up for Module 5 (Telegram
bot, which writes actual conversation turns).

### Q9 — Phase A unchecked gate tasks

**Decision:** Legacy tasks A.6.2 (failure-mode tests for classifier),
A.7.1 (gate verification), A.7.2 (tag) remain unchecked. A.6.2 is
effectively covered by D.0's fallback integration tests (E.2.2 in
legacy tasks), which mock LiteLLM failures and verify classifier
falls through to fallback. A.7.1 and A.7.2 are gate formalities —
they complete when Phase D ships (all phases integrated). These are
noted in D.5 cleanup but do not block Phase D start.

---

## 2. Atomic task list

### D.0 — Prerequisite: Fallback classifier (Phase E)

- [ ] **D.0.1** Create `src/mcp_server/router/fallback_keywords.py`.
  Two module-level dicts:
  - `BUCKET_KEYWORDS: dict[str, list[str]]` — 3 buckets × ~6 keywords
    each, derived from `identity.md` content and bucket README files.
    Example: `{"personal": ["personal", "family", "daughter", ...],
    "business": ["business", "freelance", "declassified", "pretel-os",
    ...], "scout": ["scout", "motors", "assembly", ...]}`.
  - `COMPLEXITY_KEYWORDS: dict[str, list[str]]` — `{"HIGH": ["debug",
    "architect", "why does", "recommend", ...], "LOW": ["hi", "hello",
    "thanks", "ok", ...]}`.
  Exact keyword lists are Claude Code's judgment — the test coverage
  (D.0.3) validates correctness.
  - **Done when:** `from mcp_server.router.fallback_keywords import
    BUCKET_KEYWORDS, COMPLEXITY_KEYWORDS` works; each bucket has ≥ 4
    keywords; each complexity level has ≥ 3 keywords.

- [ ] **D.0.2** Create `src/mcp_server/router/fallback_classifier.py
  ::fallback_classify(message: str, l0_content: str) -> dict`. Pure
  Python, no LLM, no DB. Algorithm per `spec.md §10.1`:
  1. Lowercase message.
  2. For each bucket in BUCKET_KEYWORDS: if any keyword in message →
     bucket = that bucket. First match wins.
  3. Scan `l0_content` for a `## Projects` section with bullet list.
     If message mentions a slug → project = slug. Else None.
  4. Complexity: if any HIGH keyword → MEDIUM (never HIGH from rules).
     Else if any LOW keyword → LOW. Else → LOW.
  5. `needs_lessons` = bucket is not None AND project is not None AND
     complexity != LOW.
  6. `skill` = None.
  7. `confidence` = 0.4 (fixed).
  Returns dict matching `spec.md §5.1` schema exactly.
  - **Done when:** function returns valid classification dict for a
    sample message; `confidence` is always 0.4; `complexity` never
    returns "HIGH".

- [ ] **D.0.3** Create `tests/router/test_fallback_classifier.py` with
  7 unit tests per `plan.md §7.4`:
  1. Clear bucket match ("debug my n8n batching" → business).
  2. Unknown bucket ("what's the weather" → None).
  3. Project found in L0 (L0 has `## Projects\n- declassified`,
     message mentions "declassified" → project="declassified").
  4. Project not in L0 (message mentions random slug → project=None).
  5. HIGH-keyword detection ("help me architect" → complexity=MEDIUM,
     not HIGH).
  6. LOW-keyword detection ("hi" → complexity=LOW).
  7. Default-LOW path (no keywords match → LOW).
  All inline fixtures, no conftest.py.
  - **Done when:** `pytest tests/router/test_fallback_classifier.py -v`
    passes 7/7.

- [ ] **D.0.4** Phase E gate: verify `plan.md §7.4 Done when` bullets:
  (a) valid classification dict for all 7 cases; (b) confidence always
  0.4; (c) complexity never HIGH; (d) 7 tests pass.
  - **Done when:** all 4 bullets verified; gate note appended to this
    doc's §3.

### D.1 — Telemetry primitives

- [ ] **D.1.1** Schema verification. Claude Code runs `\d+ routing_logs`
  and `\d+ llm_calls` on the test DB and compares column names / types
  against `spec.md §9.1` and `spec.md §9.2`. Document any drift in a
  comment block at the top of `telemetry.py`. If columns are missing,
  author a migration (next available number after 0031) to add them.
  If columns exist but types differ, flag for operator review.
  - **Done when:** schema matches spec or migration applied; discrepancy
    doc exists if any changes were needed.

- [ ] **D.1.2** Create `src/mcp_server/router/telemetry.py` with six
  functions. All take `conn: psycopg.Connection` and `request_id: str`
  as first two args. All are sync (DB writes are sync via psycopg).
  Each function wraps its SQL in a try/except that silently catches
  DB errors (telemetry must never crash the request). Functions:

  1. `start_request(conn, message, session_id, client_origin) -> str`
     — generates UUID4 `request_id`, INSERTs into `routing_logs` with
     `message_excerpt=message[:200]`, returns request_id.

  2. `log_classification(conn, request_id, classification, mode,
     llm_call_data)` — UPDATEs `routing_logs` with `classification`
     (JSONB), `classification_mode`. If `mode='llm'` and
     `llm_call_data is not None`, INSERTs into `llm_calls` with all
     §9.2 columns.

  3. `log_layers(conn, request_id, bundle: LayerBundle)` — UPDATEs
     `routing_logs` with `layers_loaded` (array of layer names where
     loaded=True), `tokens_assembled_total`, `tokens_per_layer` (JSONB),
     `over_budget_layers`.

  4. `log_rag(conn, request_id, rag_expected, rag_executed,
     lessons_returned, tools_returned)` — UPDATEs routing_logs.

  5. `log_conflicts(conn, request_id, violations:
     list[InvariantViolation])` — UPDATEs `routing_logs.source_conflicts`
     with `json.dumps([asdict(v) for v in violations])`.

  6. `log_completion(conn, request_id, degraded_mode, degraded_reason,
     latency_ms)` — UPDATEs routing_logs with final columns. This is the
     function called in try/finally.

  - **Done when:** mypy clean; `from mcp_server.router.telemetry import
    start_request, log_completion` works.

### D.2 — Router orchestrator

- [ ] **D.2.1** Discover existing interfaces. Claude Code reads these
  files and documents in a comment block at the top of `router.py`:
  - `litellm_client.py` — how does `chat_json()` return metadata? (Q6)
  - `classifier.py` — `classify()` signature and return type.
  - `assemble.py` — `assemble_bundle()` signature.
  - `invariant_detector.py` — `detect_invariant_violations()` signature.
  - `cache.py` — `LayerBundleCache` instantiation pattern.
  - Existing `src/mcp_server/tools/get_context.py` stub — what does
    the current MCP wrapper look like?
  - `conversation_sessions` table schema — does it store per-turn
    content? (Q8)
  If `classify()` does not return LLM call metadata, modify it per Q6
  option (a) or (b) — whichever is fewer file edits.
  - **Done when:** `router.py` comment block documents all discovered
    interfaces. Any required modifications to Phase A files are committed
    in the same commit with clear rationale.

- [ ] **D.2.2** Create `src/mcp_server/router/router.py` with:

  `async def get_context(conn, message, session_id, client_origin,
  repo_root, cache) -> dict`

  Full pipeline per Q4 and Q5:
  1. `t0 = time.monotonic()`
  2. `request_id = start_request(conn, message, session_id,
     client_origin)`
  3. Read `identity.md` from `repo_root` for classifier input.
  4. `session_excerpt = get_session_excerpt(conn, session_id)` — helper
     in router.py or separate file. Returns empty string if unavailable.
  5. `try: (classification, llm_call_data) = classify(message,
     identity_content, session_excerpt, request_id)` with
     `classification_mode = 'llm'`.
     `except ClassifierError: classification =
     fallback_classify(message, identity_content)` with
     `classification_mode = 'fallback_rules'`, `llm_call_data = None`.
  6. `log_classification(conn, request_id, classification,
     classification_mode, llm_call_data)`.
  7. Build `ClassifierSignals` from classification dict.
  8. `try: bundle = await assemble_bundle(conn, ...)` with full args.
     `except: build minimal L0-only bundle; degraded=True`.
  9. `log_layers(conn, request_id, bundle)`.
  10. `violations = detect_invariant_violations(bundle)`.
  11. `log_conflicts(conn, request_id, violations)`.
  12. `tools_recommended = recommend_tools(conn, ...)` per Q7.
  13. Compute RAG signals: `rag_expected` from complexity per spec §5.2,
      `rag_executed` = L4.loaded in bundle, `lessons_returned` = count of
      L4 blocks with source='lessons', `tools_returned = len(tools_recommended)`.
  14. `log_rag(conn, request_id, ...)`.
  15. Build ContextBundle dict per `spec.md §4.2`:
      ```python
      {
          "request_id": request_id,
          "session_id": session_id,
          "classification": classification,
          "classification_mode": classification_mode,
          "bundle": asdict(bundle),
          "tools_recommended": tools_recommended,
          "source_conflicts": [asdict(v) for v in violations],
          "over_budget_layers": list(bundle.metadata.over_budget_layers),
          "degraded_mode": degraded,
          "degraded_reason": '; '.join(reasons) or None,
          "latency_ms": int((time.monotonic() - t0) * 1000),
      }
      ```
  16. `finally: log_completion(...)`.
  17. Return the dict.

  Helper functions (can be private in router.py or separate files):
  - `_read_identity(repo_root) -> str`
  - `_get_session_excerpt(conn, session_id) -> str`
  - `_recommend_tools(conn, complexity, needs_lessons) -> list[dict]`
  - `_compute_rag_expected(classification) -> bool`
  - `_build_degraded_bundle(repo_root) -> LayerBundle` — L0-only bundle
    with loaded=True for L0, loaded=False for L1–L4.

  - **Done when:** mypy clean; `from mcp_server.router.router import
    get_context` works; the function handles all 6 degraded modes from
    spec §10 table without raising.

- [ ] **D.2.3** Create `tests/router/context_bundle_schema.json` — a
  JSON Schema document that validates the ContextBundle dict returned
  by `get_context()`. Matches `spec.md §4.2` key-for-key. Used by D.4
  tests.
  - **Done when:** file exists; a valid ContextBundle passes
    `jsonschema.validate(bundle, schema)`.

### D.3 — MCP tools

- [ ] **D.3.1** Replace `src/mcp_server/tools/get_context.py` stub with
  real Router invocation. Claude Code reads the existing stub to match
  MCP tool registration conventions (decorator pattern, parameter
  schema, return format). The new implementation:
  1. Creates a psycopg connection (or gets one from pool).
  2. Calls `await router.get_context(conn, message, session_id,
     client_origin, repo_root, cache)`.
  3. Returns the dict to the MCP client.
  `client_origin` is derived from the MCP transport context if
  available, else defaults to `'unknown'`.
  - **Done when:** MCP tool registered; calling `get_context` from Claude.ai
    returns a real bundle (not the Module 3 stub response).

- [ ] **D.3.2** Create `src/mcp_server/tools/report_satisfaction.py`.
  MCP tool that takes `request_id: str` and `score: int` (1–5).
  UPDATEs `routing_logs.user_satisfaction` for the matching request_id.
  Returns `{"status": "ok"}` or `{"status": "error", "reason": ...}`.
  Follow existing tool conventions discovered in D.3.1.
  - **Done when:** calling `report_satisfaction(request_id, 4)` updates
    the corresponding routing_logs row.

### D.4 — Tests

- [ ] **D.4.1** Create `tests/router/test_telemetry.py` — unit tests
  for each `log_*` function. These require a real test DB connection.
  Tests:
  1. `test_start_request_creates_row` — call start_request, SELECT the
     row, verify request_id, message_excerpt, client_origin.
  2. `test_log_classification_updates_row` — start_request +
     log_classification, verify classification JSONB and
     classification_mode columns.
  3. `test_log_classification_llm_mode_writes_llm_calls` — with
     mode='llm' and llm_call_data, verify 1 llm_calls row joinable
     on request_id.
  4. `test_log_classification_fallback_no_llm_calls` — with
     mode='fallback_rules', verify 0 llm_calls rows.
  5. `test_log_layers_populates_token_columns` — verify
     tokens_assembled_total, tokens_per_layer JSONB, layers_loaded
     array, over_budget_layers array.
  6. `test_log_conflicts_serializes_violations` — pass a list of
     InvariantViolation, verify source_conflicts JSONB column contains
     the expected JSON array.
  7. `test_log_completion_always_fires` — simulate a crash after
     log_classification, verify log_completion still wrote
     degraded_mode=true and latency_ms.
  8. `test_log_rag_populates_columns` — verify rag_expected,
     rag_executed, lessons_returned, tools_returned.
  All marked `@pytest.mark.slow` (real DB). ~8 tests.
  - **Done when:** `pytest tests/router/test_telemetry.py -v` passes all.

- [ ] **D.4.2** Create `tests/router/test_e2e.py` — end-to-end tests
  that call `router.get_context()` against live infrastructure (LiteLLM
  + DB + embeddings). 6 tests per legacy task D.4:
  1. `test_n8n_debug_query` — "help me debug my n8n batching" →
     bucket=business, complexity ∈ {MEDIUM, HIGH}, L4 loaded,
     1 routing_logs row, 1 llm_calls row, all §4.2 keys present.
     Validate against `context_bundle_schema.json`.
  2. `test_known_bucket_no_project` — "what's the latest pretel-os
     decision?" → bucket=business, project=None or "pretel-os".
  3. `test_ambiguous_message` — "what should I do?" → may fallback or
     produce low confidence; classification_mode in ('llm',
     'fallback_rules').
  4. `test_greeting_low_complexity` — "hi" → complexity=LOW, L4 NOT
     loaded, tools_recommended=[].
  5. `test_high_complexity_recommendation` — "recommend a database
     architecture for my new project" → complexity=HIGH, L4 loaded,
     tools_recommended non-empty.
  6. `test_scout_query_abstract` — "how is my assembly station
     tracking?" → bucket=scout, content abstract only (per CONSTITUTION
     §3 — no identifiable employer data surfaced).
  All marked `@pytest.mark.slow`. Each test also verifies: routing_logs
  row exists, source_conflicts is valid JSON array, latency_ms > 0.
  - **Done when:** all 6 pass. Total cost: ~$0.10–0.30 (6 classifier
    calls + 3–4 embed calls).

- [ ] **D.4.3** Fallback integration tests (legacy E.2.2). 5 tests
  in `tests/router/test_fallback_integration.py` or appended to
  `test_e2e.py`:
  1. Mock LiteLLM as timeout → classify() falls through to
     fallback_classify() → classification_mode='fallback_rules'.
  2. Mock LiteLLM as connection refused → same fallback.
  3. Mock LiteLLM as 5xx → same fallback.
  4. Mock LiteLLM as returning malformed JSON → same fallback.
  5. Mock LiteLLM as returning schema-invalid JSON → same fallback.
  All verify: routing_logs.classification_mode='fallback_rules' AND
  no llm_calls row written for that request.
  These can be fast tests (mocked LiteLLM, real or mocked DB).
  - **Done when:** 5/5 pass.

### D.5 — Gate + cleanup

- [ ] **D.5.1** Run all 3 audit queries from `spec.md §9.3` against
  data accumulated by D.4 test runs:
  1. Classifier uptime (should show both 'llm' and 'fallback_rules').
  2. Per-model classification cost and quality.
  3. RAG mismatch detection.
  Each must execute without error and return ≥ 1 row.
  - **Done when:** all 3 queries return non-zero results.

- [ ] **D.5.2** Save audit queries to
  `runbooks/router_audit_queries.sql` — the 3 spec §9.3 queries plus
  comments explaining each.
  - **Done when:** file exists, queries commented.

- [ ] **D.5.3** Verify `plan.md §6.4 Done when` line by line:
  (a) get_context returns valid ContextBundle for "help me debug my n8n
  batching" (D.4.2 test 1); (b) routing_logs row written with all §9.1
  columns (D.4.1); (c) llm_calls row written joinable on request_id
  (D.4.1 test 3); (d) 3 audit queries execute (D.5.1); (e)
  report_satisfaction updates the row (D.3.2).
  - **Done when:** all 5 bullets verified; gate note appended to §3.

- [ ] **D.5.4** Verify `plan.md §7.4 Done when` (Phase E gate):
  already verified in D.0.4 — cross-reference here for completeness.
  - **Done when:** D.0.4 passed.

- [ ] **D.5.5** Patch `specs/router/tasks.md`:
  - Phase E section (lines 266–296): mark E.1.1, E.1.2, E.2.1, E.3.1
    as `[x]` with commit hashes. E.2.2 (fallback integration tests)
    covered by D.4.3 — mark with that commit hash.
  - Phase D section (lines 298–362): mark D.1.1–D.6.2 as `[x]` with
    commit hashes.
  - Phase A unchecked tasks (A.6.2, A.7.1, A.7.2): mark A.6.2 as
    `[x]` (covered by D.4.3 fallback tests). A.7.1 and A.7.2 — mark
    `[x]` with note "gate verified as part of Phase D integration;
    tag deferred to module-4-complete."
  - **Done when:** all E.x, D.x, and A.6–A.7 rows have `[x]`.

- [ ] **D.5.6** Update `SESSION_RESTORE.md` §2 and §13 (same pattern
  as Phase C close). Phase E + D done. Top-of-stack becomes M4.T9.x
  (runbook + module exit gate + tag).
  - **Done when:** SESSION_RESTORE reflects Phases A–E done, M4.T9.x
    next.

- [ ] **D.5.7** Create tags (operator-driven, same convention as B/C):
  `phase-e-complete` on D.0 final commit, `phase-d-complete` on D.5
  final commit. Do not push — operator reviews first.
  - **Done when:** both tags exist locally.

---

## 3. Status

**Active task:** first unchecked `[ ]` above.

**Suggested commit boundaries:**

1. **D.0** — fallback_keywords.py + fallback_classifier.py + tests
   (single commit, ~150 LoC). Tag `phase-e-complete` here.
2. **D.1** — schema verification + telemetry.py (single commit, ~200
   LoC + possible migration).
3. **D.2** — router.py + context_bundle_schema.json + any Phase A
   interface adaptations for Q6 (single commit, ~350 LoC). This is the
   biggest commit.
4. **D.3** — get_context.py replacement + report_satisfaction.py
   (single commit, ~80 LoC).
5. **D.4** — test_telemetry.py + test_e2e.py + test_fallback_integration
   (single commit, ~400 LoC).
6. **D.5** — gate verification + tasks.md cleanup + audit queries
   runbook + SESSION_RESTORE (single commit, docs only).
   Tag `phase-d-complete` here.

**Cost estimate:** ~$0.10–0.30 total for slow tests (6 e2e classifier
calls + embed calls). D.0 through D.2 are $0 (no LLM). D.3 is $0
(wrappers only). D.4 is the only cost.

**Claude Code session estimate:** 4–6 sessions.
- D.0: 1 session (~3 min)
- D.1: 1 session (~4 min)
- D.2: 1–2 sessions (~5–8 min) — the big one
- D.3 + D.4: 1–2 sessions (~5 min)
- D.5: 1 session (~3 min)

---

## 4. Doc registry

This file is interim. After Phase D closes, fold into
`specs/router/tasks.md` per D.5.5 and keep as historical reference for
Q1–Q9. Convention from `phase_b_close.md` and `phase_c_close.md`.
