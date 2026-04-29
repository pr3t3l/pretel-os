# specs/router/phase_b_close.md — Phase B close-out (B.7 + B.8 + B.9)

**Module:** Router
**Status:** Complete 2026-04-29 — all atomic tasks shipped, ready for `phase-b-complete` tag.
**Authority:** `specs/router/spec.md`, `specs/router/plan.md` §4, `specs/module-0x-knowledge-architecture/layer_loader_contract.md` §6 + §10
**Scope:** Three remaining atomic groups to close Phase B. After this doc's tasks complete, M4 Phase B is done; tag candidate `phase-b-complete`.

---

## 0. Why this doc exists

`specs/router/tasks.md` was authored 2026-04-27 against the pre-M0.X
file-based architecture. After M4.reconcile (commit `8ac5ff1`) and B.1–B.6
shipped, the legacy B.x tasks in that file are stale (LayerPayload
naming, file-based loader assumptions, etc.). Rather than rewrite the
whole tasks.md mid-flight, this focused doc tracks the three remaining
atomic groups and the architectural decisions they rest on.

When Phase B closes, this doc is folded into `tasks.md` (mark legacy
B.x rows superseded; add B.7+B.8+B.9 status under a "post-reconcile"
section) and a `phase-b-complete` tag is created.

---

## 1. Decisions taken (Q1–Q4 from session 2026-04-29)

### Q1 — `summarize_oversize` transport

**Decision:** Reuse `chat_json` from Phase A's `litellm_client.py`. The
summarize prompt asks the model for `{"summary": "<compressed text>"}`
and the helper extracts `["summary"]`. No new transport primitive.

**Trade-off:** ~3–5 token overhead per call from JSON wrapper, vs. the
robustness of inheriting Phase A's timeout / retry / telemetry / fence-
stripping pattern. The robustness wins.

**Alternatives rejected:**
- Build a non-JSON `chat_text` helper paralleling `chat_json`. More code,
  duplicates retry/timeout/telemetry logic.

### Q2 — Cache invalidation mechanism

**Decision:** Add migration `0031_layer_cache_invalidation_triggers.sql`
with one shared trigger function `notify_cache_invalidate()` attached
AFTER INSERT OR UPDATE OR DELETE on the four contract §6 tables:
`operator_preferences`, `decisions`, `best_practices`, `lessons`. The
function emits `pg_notify('layer_loader_cache', '<table>:<event>')`.

The cache module LISTENs on that channel from a background thread and
clears the in-memory dict on receipt.

**Trade-off:** One DB schema change in Phase B (we have not added schema
changes since 0030). But the alternatives are worse: scattering NOTIFY
calls across every MCP tool that mutates these tables (option b) is more
invasive and easy to forget; TTL-based invalidation (option c) violates
the plan §4.4 done-when ("write to one of the 4 trigger tables, observe
next assemble_bundle returns cache_hit=False").

**Alternatives rejected:**
- Per-tool `cur.execute("NOTIFY ...")` in each `tools/*.py` after writes.
  Six+ files to touch; easy to miss future tools.
- TTL-based cache without DB triggers. Simple, but caller cannot prove
  invalidation works in tests.

### Q3 — `ClassifierSignals` dataclass timing

**Decision:** Define `ClassifierSignals` in `types.py` as a frozen
dataclass during B.9, NOT during B.5. B.5 (`load_l3`) does not consume
the dataclass — it takes `skill_ids: list[str] | None` directly. B.9
(`assemble_bundle`) is the first caller that benefits from a typed
classifier signals shape.

**Fields** (per plan §4.5 cache-key derivation + B.6 forward-looking
classifier_domain):

```python
@dataclass(frozen=True)
class ClassifierSignals:
    bucket: str | None
    project: str | None
    complexity: str             # 'LOW' | 'MEDIUM' | 'HIGH'
    needs_lessons: bool
    needs_skills: bool
    skill_ids: tuple[str, ...] | None
    classifier_domain: str | None = None
```

`skill_ids` is a tuple (not list) so the dataclass is hashable for cache
key derivation.

**Trade-off:** Adds a small dataclass to `types.py`. None.

### Q4 — `assemble_bundle` async/sync boundary

**Decision:** `async def assemble_bundle(conn, ...)` — async function
that accepts a sync `psycopg.Connection` from the caller. The function
calls `embed()` (async), the 5 sync loaders, and `summarize_oversize`
(async via chat_json). Connection lifecycle is the caller's
responsibility (Phase D `router.py` orchestrator owns it).

**Signature:**

```python
async def assemble_bundle(
    conn: psycopg.Connection,
    bucket: str | None,
    project: str | None,
    classifier_signals: ClassifierSignals,
    repo_root: Path,
    query_text: str,
    current_time: datetime,
    cache: LayerBundleCache,
) -> LayerBundle: ...
```

**Trade-off:** Mixes async (transport) with sync (DB). The bridge sits
in `assemble_bundle`, not in every loader. Loaders stay simple sync
functions (consistent with B.2–B.6).

**Alternatives rejected:**
- Make all 5 loaders async. Massive refactor; no benefit since
  `psycopg.Connection` is sync.
- Make `assemble_bundle` sync and call `asyncio.run()` for `embed()` /
  `summarize_oversize`. Hostile to the eventual Phase D async caller.

---

## 2. Atomic task list

### B.7 — summarize_oversize helper

- [x] **B.7.1** Create `src/mcp_server/router/prompts/summarize.txt` —
  system prompt instructing the model to compress to ≤target_tokens
  while preserving facts/structure, returning `{"summary": "<text>"}`.
  - Done when: file exists, ≤500 tokens (cl100k_base).

- [x] **B.7.2** Implement `src/mcp_server/router/summarize.py` with
  `summarize_oversize(content: str, target_tokens: int) -> str`. Calls
  `chat_json('classifier_default', system=summarize_prompt, user=content+target)`,
  extracts `result["summary"]`. Surfaces `Classifier*` exceptions
  unchanged (caller decides how to react).
  - Done when: mypy clean; manual smoke against live LiteLLM compresses
    a 500-token paragraph to ≤300 tokens.

- [x] **B.7.3** Write `tests/router/test_summarize.py` — unit test with
  mocked `chat_json` for happy path + transport error pass-through; ONE
  `@pytest.mark.slow` integration test that calls real classifier_default
  on a synthetic 500-token paragraph and asserts result is shorter and
  contains a meaningful subset of the input.
  - Done when: fast tests pass; slow test passes once with real call.

### B.8 — Cache + LISTEN/NOTIFY

- [x] **B.8.1** Author `migrations/0031_layer_cache_invalidation_triggers.sql`
  with one shared `notify_cache_invalidate()` function emitting
  `pg_notify('layer_loader_cache', TG_TABLE_NAME || ':' || TG_OP)` on
  AFTER INSERT/UPDATE/DELETE for the four contract §6 tables. Idempotent
  (`DROP TRIGGER IF EXISTS`, `CREATE OR REPLACE FUNCTION`).
  - Done when: SQL parses; applies cleanly to both prod and test DBs.

- [x] **B.8.2** Apply migration to `pretel_os` and `pretel_os_test`.
  - Done when: `psql -c "SELECT trigger_name FROM information_schema.triggers
    WHERE trigger_name LIKE 'trg_%cache_invalidate%'"` returns 4 rows on
    both DBs.

- [x] **B.8.3** Implement `src/mcp_server/router/_classifier_hash.py`
  with `classifier_hash(signals: ClassifierSignals) -> str`. Uses
  `hashlib.sha256(json.dumps(asdict(signals), sort_keys=True).encode()).hexdigest()[:16]`.
  Pure function; no I/O.
  - Done when: deterministic across runs; identical signals → identical
    hash; different signals → different hash.

- [x] **B.8.4** Implement `src/mcp_server/router/cache.py` with
  `LayerBundleCache` class: thread-safe dict cache keyed by
  `(bucket, project, classifier_hash)`, with `get`, `put`,
  `invalidate_all`, and `start_listener(conn) -> None` that spawns a
  daemon thread running `LISTEN layer_loader_cache` and clearing the
  cache on each notification.
  - Done when: mypy clean; instantiation works; sequential put/get
    returns the stored bundle.

- [x] **B.8.5** Write `tests/router/test_cache.py` — unit tests for
  classifier_hash determinism + collision behavior, cache get/put/
  invalidate, plus ONE integration test that: starts the listener,
  inserts a row into one of the four trigger tables in a separate
  connection, waits up to 2 seconds, asserts cache was cleared.
  - Done when: all tests pass.

### B.9 — assemble_bundle orchestrator

- [x] **B.9.1** Add `ClassifierSignals` frozen dataclass to
  `src/mcp_server/router/types.py` per Q3 fields (skill_ids as tuple
  for hashability). No `__post_init__` validation — caller (Phase A
  classifier output adapter) is responsible for type integrity.
  - Done when: mypy clean; from `mcp_server.router.types import
    ClassifierSignals` works.

- [x] **B.9.2** Implement `src/mcp_server/router/assemble.py::assemble_bundle`
  per Q4 signature. Logic:
  1. Compute `classifier_hash` from `classifier_signals`.
  2. Cache lookup with `(bucket, project, hash)`. If hit, return cached
     bundle with `metadata.cache_hit=True` swapped in.
  3. If miss: call `embed(query_text)` only when
     `signals.needs_lessons` (otherwise pass `query_embedding=None` to
     `load_l4`).
  4. Call all 5 loaders sync — L0 always, L1/L2/L3/L4 conditional on
     signals.
  5. For each loaded layer with `token_count > budget`, call
     `summarize_oversize` on its content, replace blocks with a single
     summarized block, and write a `gotcha` row to DB.
  6. Construct `BundleMetadata` (bucket, project, classifier_hash,
     total_tokens, assembly_latency_ms = (now - current_time).ms,
     cache_hit=False).
  7. Construct `LayerBundle`, cache it, return.
  - Done when: mypy clean; happy-path integration test returns valid
    bundle.

- [x] **B.9.3** Write `tests/router/test_assemble_bundle.py` — full
  integration covering:
  - happy path (cache miss → 5 LayerContent, 4 with `loaded=True`
    if signals demand all)
  - cache hit (second call returns same bundle with `cache_hit=True`)
  - cache invalidation (insert into `decisions`, observe next call is
    `cache_hit=False`)
  - over-budget L1 triggers `summarize_oversize` + writes a `gotcha`
    row (verified via SELECT on gotchas table)
  - degraded mode: closed connection → file-backed L0 loads,
    DB-backed layers `loaded=False`
  - 1 `@pytest.mark.slow` end-to-end with real `embed()` + real
    `chat_json`-driven summarize over a synthetic 5K-token L1 fixture
  - Done when: 6 fast + 1 slow tests pass.

---

## 3. Status

**Active task:** first unchecked `[ ]` above. Update this doc as tasks
ship.

**Stop point:** end of B.9 (single pre-push review with 3 commits and
1 migration).

**Cost estimate:** B.7 slow ≈ \$0.001 (1 chat_json call); B.9 slow ≈
\$0.002 (1 embed + 1 chat_json for summarize). Total ≤ \$0.005.

---

## 4. Doc registry

This file is interim — not registered in `docs/PROJECT_FOUNDATION.md
§6 Doc registry`. After Phase B closes, fold its content into
`specs/router/tasks.md` and delete this file (or keep as historical
reference if the decisions are useful).
