# specs/router/spec.md

**Module:** Router
**Status:** Draft (M4.T1.1)
**Last updated:** 2026-04-27
**Authority:** `CONSTITUTION.md §2.2, §2.3, §2.7, §5`, `docs/PROJECT_FOUNDATION.md ADR-002, ADR-003, ADR-008, ADR-016, ADR-017, ADR-020`

> **2-minute read gate (SDD §6 rule 31):** Sections 1–4 are the spec. Everything else is contract detail. If a reviewer cannot describe what the Router does after reading §1–§4, this spec has failed and must be revisited before plan/tasks.

---

## 1. Purpose

The Router is the component inside the MCP server that turns a single user message into a fully-assembled context bundle, ready for the client-side reasoning model (Opus 4.7 or equivalent) to act on.

It exists because without it, the MCP server is a passthrough: every client request would either get nothing useful or get everything (token explosion, cost blow-up, irrelevant retrieval). The Router is what makes pretel-os *pretel-os* — the active layer that classifies the turn, loads only the layers that matter, decides whether to fire RAG, enforces token budgets, and logs the full decision trail.

The Router never reasons about the operator's problem. That is the client model's job. The Router only decides what to feed it.

---

## 2. Authority

| Source | Constraint |
|---|---|
| `CONSTITUTION §2.2` | Six responsibilities (immutable). Router is the sole context-assembly authority. |
| `CONSTITUTION §2.3` | Five layers L0–L4 with fixed budgets. No layer added/split/merged without amendment. |
| `CONSTITUTION §2.7` | Source priority resolution: immutable invariants > L2 > L3 > L4 > L1 > L0 (contextual). |
| `CONSTITUTION §4 rule 8` | Classification routes through LiteLLM alias `classifier_default`, not direct Anthropic. |
| `CONSTITUTION §5.1` | Complexity classification (LOW/MEDIUM/HIGH) drives RAG behavior. |
| `CONSTITUTION §8.43` | Degraded mode is a first-class operating state. |
| `ADR-020` | Router classification + Second Opinion route through LiteLLM proxy. |
| `docs/INTEGRATIONS.md §4.5` | LiteLLM is the gateway for Router calls. |
| `docs/DATA_MODEL.md §4.1, §4.3` | `routing_logs` and `llm_calls` schemas are the telemetry contract. |

Anything in this spec that contradicts the sources above is wrong. Update this spec, never the constitutional source, in that case.

---

## 3. Scope

### 3.1 In scope

The Router does exactly these six things, per CONSTITUTION §2.2:

1. **Classify** the incoming turn into `{bucket, project, skill, complexity, needs_lessons, confidence}` via LiteLLM alias `classifier_default`.
2. **Load layers L0–L4** per §2.3, loading only what classification demands.
3. **Decide RAG activation**: lessons retrieval, tool-catalog retrieval, project retrieval.
4. **Enforce token budgets** per §2.3 before returning context to the client.
5. **Resolve source conflicts** per §2.7 when multiple layers contradict each other.
6. **Log** every decision to `routing_logs` and every LLM call to `llm_calls` (joinable by `request_id`).

### 3.2 Out of scope

The Router never:

- Reasons about the operator's problem (that is the client model's job).
- Executes tools (the client decides which tools to call).
- Writes lessons (the Reflection worker does that, Module 6).
- Decides which skill to *use* — only which skill to *load*. Use is a client decision.
- Modifies any L0–L3 file (those are git, read-only at runtime).
- Calls Anthropic, OpenAI, or Gemini directly. All LLM calls go through LiteLLM proxy at `http://127.0.0.1:4000`.

### 3.3 Boundaries with adjacent modules

| Adjacent | Relationship |
|---|---|
| MCP server transport (Module 3) | Router is invoked when a client calls `get_context`. The transport layer hands message + session_id to the Router and returns the Router's `ContextBundle` to the client. |
| Reflection worker (Module 6) | Router writes `routing_logs` rows the worker later reads to detect patterns. No direct call between them. |
| Dream Engine (nightly) | Recomputes `utility_score` on `tools_catalog` and `lessons`. Router consumes these scores during ranking but never writes them. |
| Telegram bot (Module 5) | Calls `get_context` via the same MCP transport. The Router sees no difference between Claude.ai web, Claude Code, and Telegram. |

---

## 4. Public interface

### 4.1 Tool signature

```python
get_context(
    message: str,                    # user's raw turn text
    session_id: str | None = None,   # client-provided; used to thread routing_logs
) -> ContextBundle
```

This is the only public entry point. It is exposed via the MCP server as a tool. Internal helpers (`classify`, `load_l0`, `load_l1`, etc.) are not part of the public contract.

### 4.2 ContextBundle return shape

```python
{
    "request_id": str,                          # uuid generated server-side, joins to llm_calls
    "session_id": str | None,                   # echoed back from input
    "classification": {
        "bucket": str | None,                   # 'personal' | 'business' | 'scout' | None
        "project": str | None,                  # e.g. 'declassified' | None
        "skill": str | None,                    # e.g. 'vett' | None
        "complexity": "LOW" | "MEDIUM" | "HIGH",
        "needs_lessons": bool,
        "confidence": float                     # 0.0 – 1.0
    },
    "classification_mode": "llm" | "fallback_rules",
    "layers": {
        "L0": { "content": str, "tokens": int },
        "L1": { "content": str, "tokens": int } | None,
        "L2": { "content": str, "tokens": int, "module": str | None } | None,
        "L3": { "skill": str, "content": str, "tokens": int } | None,
        "L4": { "lessons": list[dict], "tokens": int } | None
    },
    "tools_recommended": list[dict],            # name + one-line description, ranked by utility_score
    "source_conflicts": list[dict],             # see §8
    "tokens_total": int,                        # sum across loaded layers + tools
    "tokens_per_layer": dict,                   # {'L0': 480, 'L1': 1200, ...}
    "over_budget_layers": list[str],            # layers that required summarization
    "degraded_mode": bool,
    "degraded_reason": str | None,
    "latency_ms": int                           # server-side processing time
}
```

The bundle is JSON-serializable. Order of keys is documented but not enforced by the protocol.

### 4.3 Companion tool: `report_satisfaction`

```python
report_satisfaction(
    request_id: str,    # the request_id returned from a prior get_context call
    score: int          # 1–5
) -> {"status": "ok"} | {"status": "error", "reason": str}
```

Updates `routing_logs.user_satisfaction` for the matching `request_id`. Used by the client (or operator manually) to feed back retrieval-quality signal. Per §5.1 and §9.1 below.

---

## 5. Classification contract

### 5.1 Classifier prompt — provider-agnostic

The system prompt lives in `src/mcp_server/router/prompts/classify.txt` and must produce valid JSON across all providers reachable via LiteLLM aliases (Gemini, Anthropic, OpenAI, Kimi, etc.).

**Inputs to the classifier:**
- The raw user message.
- L0 content (always loaded, max 1,200 tokens per §2.3).
- An abbreviated session ledger (last 3 turns of `conversation_sessions` for the active `session_id`, if present).

**Output JSON schema (strict):**

```json
{
  "bucket": "personal" | "business" | "scout" | null,
  "project": "<project-slug-from-L0-index>" | null,
  "skill": "<skill-name-from-L0-tools-list>" | null,
  "complexity": "LOW" | "MEDIUM" | "HIGH",
  "needs_lessons": true | false,
  "confidence": 0.0 – 1.0
}
```

**Validation rules:**
- `bucket` must be one of the three or `null`. Anything else → parse failure → fallback.
- `project` must match a slug present in the loaded L1 index, or be `null`. Hallucinated project names are a parse failure.
- `complexity` must be uppercase exact match.
- `confidence` is the model's self-reported confidence. Low confidence (< 0.6) is logged but does not by itself trigger fallback.

### 5.2 Complexity rules (CONSTITUTION §5.1)

| Level | When | RAG behavior |
|---|---|---|
| **LOW** | Greetings, factual lookups with a single answer, single-step requests with no ambiguity, acknowledgments | L4 never loads. Tool catalog never queried. |
| **MEDIUM** | Structured tasks following a known workflow, minor problem solving with obvious scope | L4 loads conditionally: cheap count query first, top-3 if ≥ 1 match, skip if 0. Tool catalog queried only if `needs_lessons=true`. |
| **HIGH** | Debugging, architectural decisions, multi-step reasoning over unfamiliar territory, recommendations | L4 always loads (top-K by similarity). Tool catalog always queried. |

The agent never overrides this. The Router decides; the agent uses what arrives.

### 5.3 Calling `classifier_default` via LiteLLM

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4000",
    api_key=os.environ["LITELLM_API_KEY"],
)

response = client.chat.completions.create(
    model="classifier_default",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message_with_l0_context},
    ],
    response_format={"type": "json_object"},
    temperature=0.0,
    max_tokens=300,
    timeout=3.0,
)
```

- Timeout per `INTEGRATIONS §1.4`: 3,000 ms.
- Retries: 1 retry with 500 ms delay on transport error, none on parse error.
- On any of (timeout, transport error, malformed JSON, schema-invalid JSON): fall back to rule-based classifier per §10.

---

## 6. Layer loading rules

### 6.1 Layer table (CONSTITUTION §2.3)

| Layer | Source | Loaded when | Budget |
|---|---|---|---|
| **L0** | Git: `identity.md` | Always | 1,200 tok |
| **L1** | Git: `buckets/{bucket}/README.md` (or sub-bucket per §2.3 pattern) | `classification.bucket` is not null | 1,500 tok |
| **L2** | Git: `buckets/{b}/projects/{p}/README.md` + relevant module file | `classification.project` is not null | 2,000 tok |
| **L3** | Git: `skills/{skill}.md` | `classification.skill` is not null | 4,000 tok |
| **L4** | Postgres + pgvector: `lessons` filtered by bucket/tags | `classification.needs_lessons=true` AND complexity allows it (§5.2) | 1,500 tok |

### 6.2 Sub-bucket selection (L1)

When the bucket README points to sub-buckets (per CONSTITUTION §2.3 sub-bucket pattern), the Router loads the sub-bucket whose name is matched by:
- A second-pass keyword scan against the user message, OR
- An explicit hint embedded in the classification (`bucket="business/freelance/clients"`).

If no sub-bucket matches, the bucket README itself is loaded (containing pointers + recent index).

### 6.3 Module selection (L2)

For multi-module projects (CONSTITUTION §5.6 rule 28), the Router loads:
- `buckets/{b}/projects/{p}/README.md` always.
- Plus exactly **one** module file per turn — the module whose name appears in the message or whose tags match the most-similar lesson in L4.

Loading multiple modules per turn is forbidden by §5.6 rule 29. If the agent later needs another module, it explicitly calls `list_modules(project)` and re-requests via a follow-up turn.

### 6.4 Budget enforcement

Write-time enforcement (pre-commit hook, §7.36 of the constitution) blocks commits that push any layer's content over budget. This means at read-time, layers should already fit. Read-time summarization is fallback-only — for content that existed before the hook was installed.

When a layer exceeds budget at read-time:
1. The Router logs the layer name in `routing_logs.over_budget_layers`.
2. The Router calls a summarization helper (LiteLLM alias `classifier_default` with a summarize prompt) to compress the over-budget layer to 80% of its budget ceiling.
3. The summarized content is served. The original is not modified on disk.
4. A `gotcha` row is written suggesting the operator refactor the source file.

The Router never silently truncates.

---

## 7. RAG activation

### 7.1 Lessons retrieval (L4)

```python
# Filter-first per CONSTITUTION §5.6 rule 26
lessons = search_lessons(
    query_embedding=embed(user_message),
    bucket=classification.bucket,
    tags=derive_tags(classification),
    limit=top_k_for_complexity(classification.complexity),  # HIGH=5, MEDIUM=3
    include_archived=False,
)
```

- For HIGH complexity: top-5 lessons.
- For MEDIUM complexity with ≥ 1 hit on filter-only count: top-3 lessons.
- For LOW: never queried.
- Never returns archived lessons unless the operator explicitly requests via a different tool (`search_lessons(include_archive=true)`).

### 7.2 Tool catalog retrieval

When complexity is HIGH, or when MEDIUM with `needs_lessons=true`:

```python
tools = recommend_tools(
    context=classification,
    limit=5,
)
```

Ranked by `utility_score` per CONSTITUTION §5.3 rule 18, ties broken toward higher `cross_bucket_count`. Tools surfaced in the bundle as `{name, one_line_description, utility_score}`. Full schemas are loaded on-demand by the agent via `tool_search`.

### 7.3 Project retrieval (historical)

The Router does NOT query `projects_indexed` by default. That is reserved for the agent to call explicitly via `search_projects_indexed(query, bucket?)` when investigating prior work. Per CONSTITUTION §5.6 rule 27: only the active project's L2 is loaded per turn.

---

## 8. Source priority resolution (CONSTITUTION §2.7)

### 8.1 Immutable invariants (non-overridable)

The Router enforces these at assembly time. If any layer's content tries to override them, the layer's content is rewritten (or that section dropped) and a `source_conflicts` entry is logged with reason `'invariant_violation'`:

- Security/data-sovereignty rules (`CONSTITUTION §3`): Scout denylist, credential handling.
- Token-budget ceilings (`§2.3`).
- Git/DB boundary (`§2.4`).
- Agent rules in `§9` (no guessing tool params, no executing code by reading, etc.).

These are enforced structurally — pre-commit hooks block them at write-time, DB triggers block at insert-time, MCP middleware blocks at request-time. The Router's role is final-mile: surface the conflict in the bundle so the agent sees it.

### 8.2 Contextual ordered priority

For non-invariant content, when two layers say different things on the same topic (e.g., L4 lesson says "use Postgres" but L1 bucket README says "use SQLite"):

```
L2 current project state    >  L3 skill  >  L4 lesson  >  L1 bucket  >  L0 contextual identity
```

The Router does not silently reconcile. It surfaces the conflict in `source_conflicts` like:

```json
{
  "topic": "default-database",
  "winning_source": "L4:lesson:c7f2-...",
  "winning_text": "Postgres + pgvector for embeddings work",
  "losing_sources": [
    {"layer": "L1", "text": "SQLite is fine for prototypes"}
  ]
}
```

The agent reads the bundle, follows the winning source, and surfaces the conflict in its reasoning so the operator sees it. If the higher-priority source is wrong, the operator corrects the source — not the agent's behavior on that turn.

---

## 9. Telemetry contract

Every `get_context` call writes one row to `routing_logs` and zero or one row to `llm_calls`. They join on `request_id`.

### 9.1 `routing_logs` columns populated per call

Per `DATA_MODEL §4.1`:

| Column | Source |
|---|---|
| `request_id` | Generated server-side at start of `get_context`. |
| `client_origin` | Provided by transport layer (`'claude.ai'`, `'claude_code'`, `'telegram'`). |
| `message_excerpt` | First 200 chars of `message`. |
| `classification` | The full JSON from the classifier (or fallback). |
| `classification_mode` | `'llm'` or `'fallback_rules'`. |
| `layers_loaded` | Array of layer names actually loaded, e.g. `['L0', 'L1', 'L4']`. |
| `tokens_assembled_total` | Sum of `tokens_per_layer.values()`. |
| `tokens_per_layer` | JSONB `{'L0': 480, 'L1': 1200, ...}`. |
| `over_budget_layers` | Array of layer names that triggered summarization. |
| `rag_expected` | Computed from complexity: HIGH→true, LOW→false, MEDIUM→depends on filter-count. |
| `rag_executed` | Did L4 actually fire? |
| `lessons_returned` | Count from L4. |
| `tools_returned` | Count from tool catalog. |
| `source_conflicts` | Array per §8.2. |
| `degraded_mode` | True if any dependency was unavailable. |
| `degraded_reason` | Human-readable reason. |
| `latency_ms` | End-to-end Router processing time. |
| `user_satisfaction` | NULL on insert; updated later via `report_satisfaction`. |

### 9.2 `llm_calls` row when classification used `classifier_default`

Per `DATA_MODEL §4.3`:

| Column | Value |
|---|---|
| `request_id` | Same as `routing_logs.request_id`. |
| `purpose` | `'classification'`. |
| `provider` | Whatever LiteLLM reports (`'gemini'`, `'anthropic'`, etc.). |
| `model` | Concrete model name from response (`'gemini/gemini-2.5-flash'`, etc.). |
| `input_tokens` | From LiteLLM response. |
| `output_tokens` | From LiteLLM response. |
| `cache_read_tokens` | From LiteLLM response when provider reports it; 0 otherwise. |
| `cost_usd` | Computed by LiteLLM; pass through. |
| `latency_ms` | Time from request start to response complete. |
| `success` | True unless an exception was caught. |
| `error` | Error message on failure; NULL otherwise. |
| `client_id` | NULL for now (Phase 4+ for billing attribution). |
| `project` | `bucket/project` from classification when known. |

When fallback rules are used, no `llm_calls` row is written. `routing_logs.classification_mode='fallback_rules'` is the only signal.

### 9.3 Audit queries (must be supported by the schema as written)

These queries must run cleanly against the resulting data:

```sql
-- Classifier uptime (last 30 days)
SELECT classification_mode, count(*),
       round(100.0 * count(*) / sum(count(*)) over (), 2) AS pct
FROM routing_logs
WHERE created_at > now() - interval '30 days'
GROUP BY classification_mode;

-- Per-model classification cost and quality
SELECT lc.model,
       count(*) AS classifications,
       avg(rl.user_satisfaction) AS avg_satisfaction,
       avg(lc.cost_usd) AS avg_cost,
       sum(lc.cost_usd) AS total_cost
FROM routing_logs rl
JOIN llm_calls lc USING (request_id)
WHERE lc.purpose = 'classification'
  AND rl.created_at > now() - interval '30 days'
GROUP BY lc.model
ORDER BY avg_satisfaction DESC NULLS LAST;

-- RAG mismatch detection (rag_expected ≠ rag_executed)
SELECT date_trunc('day', created_at) AS day, count(*)
FROM routing_logs
WHERE rag_expected <> rag_executed
GROUP BY day
ORDER BY day DESC;
```

If any of these queries cannot run against the implementation, the implementation is wrong — not the spec.

---

## 10. Failure modes & degraded behavior

Per CONSTITUTION §8.43. The Router never returns 500 because a downstream is unavailable.

| Dependency | Failure mode | Router behavior |
|---|---|---|
| LiteLLM proxy unreachable for `classifier_default` | timeout, connection refused, 5xx after 1 retry | Switch to `fallback_classifier.py`. Set `classification_mode='fallback_rules'`, `confidence=0.4`. Continue with layer loading using fallback's classification. |
| Classifier response malformed (not JSON, missing fields, hallucinated bucket/project) | Parse failure | Same as above — fallback rules. |
| Postgres unreachable | DB queries error | L0–L3 continue (git-only). L4 returns `{lessons: [], tokens: 0}` with explicit marker `degraded_reason='db_unavailable'`. Tool catalog returns only L0-embedded names. `routing_logs` write queues to fallback journal per §8.43(b). |
| OpenAI embeddings API unreachable | Embed call errors | New embeddings queue to `pending_embeddings`. L4 retrieval against existing embeddings continues. If the user message itself cannot be embedded, L4 is skipped with `degraded_reason='embedding_unavailable'`. |
| Layer file missing on disk (deleted, renamed, permission error) | I/O error | That single layer is omitted from the bundle. `degraded_reason` enumerates which layer. Other layers proceed normally. |
| Layer over budget after summarization attempt | Summarizer also failed | Layer omitted from bundle. `degraded_reason='layer_X_oversize'`. Bundle returned without that layer. |

Every degraded response sets `degraded_mode=true` and a human-readable `degraded_reason`. The agent surfaces reduced functionality to the operator rather than pretending everything works.

### 10.1 Fallback classifier (`fallback_classifier.py`) — algorithm sketch

```
1. Lowercase the message.
2. For each bucket in BUCKET_KEYWORDS, if any keyword appears in message → bucket = that bucket. First match wins; break.
3. Scan L0 for project names (extracted from the L0 project index). If the message contains a project slug or its display name → project = that slug.
4. Complexity:
   - If any keyword from COMPLEXITY_KEYWORDS['HIGH'] appears → MEDIUM (never HIGH from rules).
   - Else if any keyword from COMPLEXITY_KEYWORDS['LOW'] appears → LOW.
   - Else → LOW.
5. needs_lessons = (bucket is not None AND project is not None AND complexity != LOW).
6. skill = None (rules cannot reliably infer skills).
7. confidence = 0.4 (fixed).
```

Bucket and complexity keyword lists are defined in `src/mcp_server/router/fallback_keywords.py` and version-controlled. Adding a keyword is a code change with a test.

---

## 11. Non-goals

The following are explicitly NOT what the Router does. Confusion on these is what makes routers turn into monoliths.

- **Reasoning about the user's problem.** The Router does not generate explanations, code, advice, or any user-facing content beyond the bundle. The client model owns that.
- **Tool execution.** The Router never calls `save_lesson`, `register_skill`, `request_second_opinion`, or any other MCP tool. It assembles context for the agent that will.
- **Lesson writing.** The Reflection worker (Module 6) writes lessons. The Router only reads them via L4.
- **Skill execution.** The Router can load a skill into L3 ("here is how VETT works"). It does not run a phase of VETT.
- **Cross-pollination flagging.** The Reflection worker writes `cross_pollination_queue` rows. The Router does not.
- **Embedding writes.** The Router queries existing embeddings. New writes happen via `auto_index_on_save` worker per CONSTITUTION §2.6.
- **Client-side rendering.** The Router returns JSON. The client decides how to display it.
- **Multi-turn conversation memory.** The Router uses the most recent 3 turns from the session ledger as classification input. It does not maintain a longer working-memory store. Long-term recall is `conversations_indexed` queried by the agent.

---

## 12. Success criteria (entry to implementation)

This spec passes its gate when a reviewer (operator + an outside LLM running this spec cold) can answer all of the following from §1–§11 without consulting other docs:

1. What is the input and output of the Router? (§4)
2. What are the six things it does? (§3.1)
3. What are the three complexity levels and what changes for each? (§5.2)
4. Which layers exist and when does each load? (§6.1)
5. What happens when LiteLLM is unreachable? (§10)
6. Where is the LLM-call detail logged separately from the routing decision? (§9)
7. What is the source-priority order for non-invariant content? (§8.2)
8. What is explicitly out of scope for the Router? (§11)

If any of these requires reading the constitution to answer, the spec is incomplete and must be revised before plan/tasks.

### 12.1 Implementation gate (from `plan.md §6 Module 4 Done when`)

When the code lands, these must hold (verified at M4.T9.1):

- Router code in `src/mcp_server/router/` implements the 6 responsibilities.
- Classification via `classifier_default` returns the schema in §5.1 for all 10 test examples.
- Layer loader respects budgets per §6.1.
- Source priority resolution implemented per §8 (both regimes).
- `routing_logs` populated on every call with all telemetry per §9.1.
- Fallback to rule-based classifier when LiteLLM unreachable, sets `classification_mode='fallback_rules'`.
- Smoke tests pass (M4.T8.1).
- Per-turn latency under 2 seconds for HIGH complexity.
- Runbook at `runbooks/module_4_router.md` exists.

---

## 13. Open questions (to resolve during plan/tasks)

Questions deliberately left open here, to be answered in `specs/router/plan.md` (M4.T1.2) or during implementation:

1. **Sub-bucket detection signal.** §6.2 lists two options (keyword scan vs explicit classification hint). The plan must pick one. Likely answer: classifier emits `bucket="business/freelance/clients"` directly; we update the classifier prompt to support the dotted path. But this needs a prompt-engineering pass.
2. **Top-K for L4.** §7.1 says HIGH=5, MEDIUM=3. These are starting numbers. Tuning happens after 30 days of `user_satisfaction` data.
3. **Session ledger window.** §5.1 says "last 3 turns". Is 3 right? Could be 2 or 5. Cheap to tune later.
4. **Summarization prompt.** §6.4 invokes a summarizer for over-budget layers. The exact prompt is a Module 4 implementation detail, not spec content. The spec only mandates that one exists.
5. **Confidence threshold for triggering fallback.** §5.1 says low confidence is logged but does not trigger fallback. Should sustained low-confidence (e.g., 5 turns in a row with confidence < 0.5) trigger an alert? Defer to operations.
6. **Provider drift detection.** When the operator changes `classifier_default` from one provider to another, classification quality may drift. Should the Router flag this in the bundle? Defer to Module 4 implementation review.

These are recorded so they don't get rediscovered later. Each becomes a task in `tasks.md` or a follow-up lesson, never a silent decision.

---

## 14. Doc registry

This spec is registered in `docs/PROJECT_FOUNDATION.md §6 Doc registry` under `specs/router/spec.md` (to be added by M4.T1.3 commit).

**End of spec.md.**
