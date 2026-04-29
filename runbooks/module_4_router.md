# Module 4 — Router runbook

**Status:** Module 4 closed 2026-04-29 (Phases A-E shipped; Phase F is
ongoing post-exit). This file is the single operational entry point;
it supersedes the Phase-A-era index that previously lived here.

**Authority:** `specs/router/spec.md` §3 (responsibilities), §9 (telemetry),
§10 (failure modes). `CONSTITUTION.md` §2.2 (Router-as-sole-context-authority).

**Pairs with:**
- `runbooks/router_audit_queries.sql` — the 3 spec §9.3 audit queries
  (D.5.2 deliverable).
- `runbooks/router_tuning.md` — Phase F tuning queries (M4.T9.2 / F.1.1
  deliverable).
- `runbooks/module_4_phase_a_router_classifier.md` — Phase A
  component-level operational doc.

---

## Plan §10 exit gate verification (2026-04-29)

Captured here so a reviewer can audit Module 4 closure without
chasing across files. Each bullet maps to the artifact that proves it.

| # | Bullet | Status | Proof |
|---|---|---|---|
| 1 | Router code implements 6 responsibilities (CONSTITUTION §2.2) | ✓ | File-to-responsibility table below |
| 2 | Classification returns spec §5.1 schema for 10 test inputs | ✓ | `tests/router/test_classifier_eval.py` (Phase A.6.1, opt-in `pytest -m eval`); schema validation enforced by `classifier._validate_response` |
| 3 | Layer loader respects budgets (CONSTITUTION §2.3) | ✓ | Phase B 103 fast + 3 slow tests green; over-budget triggers `summarize_oversize` per contract §7 |
| 4 | Source-priority resolution (CONSTITUTION §2.7) | ✓ | Phase C `invariant_detector.py` + `invariants.py` (12 tests). §2.7 cross-layer priority moved to consumer per `layer_loader_contract.md §10` |
| 5 | `routing_logs` populated per spec §9.1 | ✓ | D.4.1 `test_telemetry.py` (8 tests) + D.4.2 `test_e2e.py` (6 tests); INSERT-early per Q2 |
| 6 | Fallback classifier on LiteLLM unreachable | ✓ | D.0 `fallback_classifier.py` + D.4.3 `test_fallback_integration.py` (5 mocked failure modes) |
| 7 | Smoke tests | ✓ | D.4.2 `test_n8n_debug_query` (= M4.T8.1) + 5 more e2e cases all green in 9.57s |
| 8 | Per-turn latency < 2s for HIGH complexity | **partial** | Steady-state warm latency 948ms; cold-start / provider variance pushes individual turns to ~3.5s (3 sample calls: 2676 / 3558 / 948 ms). The 5s `ClassifierTimeout` cap (`classifier.py::CLASSIFIER_TIMEOUT_MS`) triggers `fallback_classify` on timeout — user-facing budget honored via degraded path. **Phase F follow-up:** tune the LiteLLM cascade for lower P95 |
| 9 | Runbook at `runbooks/module_4_router.md` exists | ✓ | This file (M4.T9.2) |
| 10 | Commit + tag `module-4-complete` | pending | M4.T9.3 — operator-driven tag on this commit |

### Bullet 1: file-to-responsibility map

The 6 responsibilities from CONSTITUTION §2.2 / spec §3.1, mapped
to the files that implement them.

| # | Responsibility | Files |
|---|---|---|
| 1 | **Classify** the turn | `router/classifier.py`, `router/litellm_client.py`, `router/prompts/classify.txt`, `router/exceptions.py`, `router/fallback_classifier.py`, `router/fallback_keywords.py` |
| 2 | **Load layers L0–L4** | `router/assemble.py`, `router/load_l0.py`, `router/load_l1.py`, `router/load_l2.py`, `router/load_l3.py`, `router/load_l4.py`, `router/cache.py`, `router/_tokens.py`, `router/_classifier_hash.py` |
| 3 | **Decide RAG activation** | `router/router.py::_compute_rag_expected`, `router/router.py::_recommend_tools`, classifier signals fan-out via `ClassifierSignals` (`types.py`) |
| 4 | **Enforce token budgets** | `router/summarize.py`, `router/_tokens.py`, `router/assemble.py::_maybe_summarize`, `router/invariants.py::_budget_ceiling_check` (defense-in-depth) |
| 5 | **Resolve source conflicts** | `router/invariant_detector.py`, `router/invariants.py` (Phase C — invariant-violation only; cross-layer priority is consumer-side per contract §10) |
| 6 | **Log** every decision | `router/telemetry.py` (6 functions), `router/router.py` (orchestrator try/finally), `tools/context.py` (MCP wrapper) |

---

## 1. Overview

The Router is the single entry point for context assembly. Every MCP
`get_context` call flows through this pipeline:

```
client → MCP tool wrapper (tools/context.py) → router.get_context() →
  start_request           (telemetry.py — INSERT-early routing_logs row)
  ↓
  classify                (classifier.py via litellm_client.chat_json)
  ↓ (on ClassifierError → fallback_classify, classification_mode='fallback_rules')
  log_classification      (UPDATE routing_logs + INSERT llm_calls if mode='llm')
  ↓
  assemble_bundle         (assemble.py — async; 5 sync loaders + embed + summarize)
  ↓ (on Exception → _build_degraded_bundle, degraded=True)
  log_layers              (UPDATE routing_logs)
  ↓
  detect_invariant_violations  (invariant_detector.py — Phase C)
  ↓
  log_conflicts           (UPDATE routing_logs.source_conflicts JSONB)
  ↓
  recommend_tools + RAG signals
  ↓
  log_rag                 (UPDATE routing_logs)
  ↓
  finally: log_completion (UPDATE routing_logs.degraded_mode + latency_ms)
  ↓
return ContextBundle dict per spec §4.2
```

Per phase_d_close.md Q5, `router.get_context()` NEVER raises to the
MCP transport. Every failure mode degrades to a coherent ContextBundle
with `degraded_mode=True` and a `degraded_reason` string.

**Latency expectations:**
- Warm steady-state HIGH-complexity turn: ~1s.
- Cold-start (first call after idle, or provider variance): up to ~3.5s.
- Hard ceiling: 5s — `ClassifierTimeout` triggers fallback.

---

## 2. Classification debugging

**Question:** What did the classifier return for a specific turn?

```sql
SELECT request_id,
       classification,
       classification_mode,
       degraded_mode,
       degraded_reason,
       latency_ms
FROM   routing_logs
WHERE  request_id = '<uuid>';
```

`classification` is JSONB matching spec §5.1:
`{bucket, project, skill, complexity, needs_lessons, confidence}`.
`classification_mode` is `'llm'` or `'fallback_rules'`.

**Question:** Did the classifier go through LiteLLM or fall through?

If `classification_mode='fallback_rules'` → fallback fired.
`degraded_reason` will start with `classifier_fallback:` and name the
exception class (e.g., `classifier_fallback: ClassifierTimeout`).

**Question:** Did the LLM call cost anything?

```sql
SELECT model,
       provider,
       input_tokens,
       output_tokens,
       cache_read_tokens,
       cost_usd,
       latency_ms,
       success,
       error
FROM   llm_calls
WHERE  request_id = '<uuid>';
```

Note: `cost_usd` is 0.000000 today because the LiteLLM proxy doesn't
surface cost to the SDK response. Accumulating real costs is a Phase F
follow-up.

**Question:** What does the classifier prompt look like?

```bash
cat src/mcp_server/router/prompts/classify.txt
```

The prompt is loaded fresh on every `classify()` call (no caching), so
edits take effect immediately on the next turn — no MCP server restart
required. Re-run `pytest -m eval` after any prompt change.

---

## 3. LiteLLM outage triage

When LiteLLM proxy is unreachable, the Router falls through to
`fallback_classify` (pure Python, no I/O). User-facing impact: turns
return with `classification_mode='fallback_rules'`, `confidence=0.4`,
and `complexity` capped at MEDIUM (never HIGH from rules).

**Verify the proxy is up:**

```bash
curl -fsS http://127.0.0.1:4000/health
# expect: {"healthy_endpoints":[...]}
systemctl --user status litellm
```

**Check fallback rate over the last hour:**

```sql
SELECT classification_mode,
       count(*),
       round(100.0 * count(*) / sum(count(*)) over (), 2) AS pct
FROM   routing_logs
WHERE  created_at > now() - interval '1 hour'
GROUP BY classification_mode;
```

A persistent `fallback_rules` share above ~10% means the LiteLLM
upstream is unhealthy. Drill into `degraded_reason` to see the
specific exception class:

```sql
SELECT degraded_reason, count(*)
FROM   routing_logs
WHERE  classification_mode = 'fallback_rules'
  AND  created_at > now() - interval '1 hour'
GROUP BY degraded_reason
ORDER BY 2 DESC;
```

Common causes:
- `ClassifierTimeout` — provider cold-start or rate-limit.
- `ClassifierTransportError` — connection refused / 5xx.
- `ClassifierParseError` — provider returned non-JSON.
- `ClassifierSchemaError` — provider returned valid JSON but wrong shape.

---

## 4. Switching providers

Per ADR-020, the Router calls `classifier_default` (a LiteLLM alias)
and never references concrete model names. Switching the model behind
the alias is a config edit, not a code change.

**Edit the LiteLLM config:**

```bash
${EDITOR:-nano} ~/.litellm/config.yaml
```

Find the entry for `classifier_default`. Update `model_name`. Common
alternatives: `claude-haiku-4-5`, `gemini/gemini-2.5-flash`,
`openai/gpt-4o-mini`, `kimi/k2-instruct`.

**Restart LiteLLM:**

```bash
systemctl --user restart litellm
```

**Verify the new model is wired:**

```bash
LITELLM_API_KEY=$(grep '^LITELLM_MASTER_KEY=' ~/.env.litellm | cut -d= -f2) \
PYTHONPATH=src DATABASE_URL="postgresql://pretel_os@localhost/pretel_os_test" \
MCP_SHARED_SECRET="smoketest" \
python3 -m pytest tests/router/test_e2e.py::test_n8n_debug_query -v -s
```

The test prints the resolved model in `[D.4.2 violations]` lines
(visible via `-s`). Match it against the new config before declaring
the switch successful.

**No code change needed.** If the new provider returns a subtly
different JSON shape, expect `ClassifierSchemaError` to fire and
fallback to take over. Tune the prompt
(`src/mcp_server/router/prompts/classify.txt`) before the next run
and re-eval (`pytest -m eval`).

**Pre-commit safeguard:**

```bash
grep -rnE "(claude-[0-9]|gpt-[0-9]|gemini-[0-9])" src/mcp_server/router/
# must return nothing — no concrete model names in router source
```

---

## 5. Audit queries reference

The 3 spec §9.3 audit queries live in
`runbooks/router_audit_queries.sql`. Re-run anytime:

```bash
psql "$DATABASE_URL" -f runbooks/router_audit_queries.sql
```

Brief purpose of each:

| Query | Purpose | Healthy state |
|---|---|---|
| Classifier uptime | LLM vs fallback share over 30 days | `llm` >> `fallback_rules` |
| Per-model cost + quality | Cost / satisfaction per concrete model | Models with `avg_satisfaction` data ranked first |
| RAG mismatch | `rag_expected ≠ rag_executed` rate | 0 rows = no mismatches |

For deeper Phase F tuning queries (per-bucket accuracy, latency
distribution, sub-bucket detection rate, fallback by hour, low-
confidence clustering) see `runbooks/router_tuning.md`.

---

## 6. Common operations

**Re-run the M4 test suite end-to-end (~$0.018 actual cost):**

```bash
LITELLM_API_KEY=$(grep '^LITELLM_MASTER_KEY=' ~/.env.litellm | cut -d= -f2) \
PYTHONPATH=src DATABASE_URL="postgresql://pretel_os@localhost/pretel_os_test" \
MCP_SHARED_SECRET="smoketest" \
python3 -m pytest tests/router/ -v
```

**Type-check the entire router module:**

```bash
mypy src/mcp_server/router/
```

**Cache state:** `LayerBundleCache` is a process-lifetime singleton in
`tools/context.py::_get_cache`. Restart the MCP server to clear it.
The LISTEN/NOTIFY listener auto-invalidates on writes to the 4 trigger
tables once wired into the MCP server lifespan — currently a
post-D.3 follow-up; lazy-init works without it but won't auto-invalidate.

---

## 7. Cross-references

- **Spec:** `specs/router/spec.md`
- **Plan:** `specs/router/plan.md` (phases A–F with done-when criteria; §10 exit gate)
- **Tasks:** `specs/router/tasks.md`
- **Phase decision trackers:** `specs/router/phase_b_close.md`,
  `phase_c_close.md`, `phase_d_close.md` (Q1–Q9 architectural decisions)
- **Schema:** `docs/DATA_MODEL.md` §4.1 `routing_logs`, §4.3 `llm_calls`
- **LiteLLM gateway:** `docs/INTEGRATIONS.md` §4.5 + ADR-020 (`DECISIONS.md`)
- **Constitution invariants:** `CONSTITUTION.md` §2.2, §2.3, §2.7, §4 rule 8, §5.1, §8.43, §9 rule 7
- **Lessons:** `LL-M4-PHASE-A-001` through `LL-M4-PHASE-A-003`
  (`docs/LESSONS_LEARNED.md` §9)
- **Phase A component runbook:** `runbooks/module_4_phase_a_router_classifier.md`
- **Module 0.X (gated Phase B):** `runbooks/module_0x_knowledge_architecture.md`

---

## 8. Change log

- **2026-04-29:** Module 4 closed — Phases B–E shipped, gate verified
  (this file). Replaced the Phase-A-era index with this consolidated
  module-level runbook.
- **2026-04-28:** Phase A shipped — earlier version of this file was the
  index pointing at `module_4_phase_a_router_classifier.md`.
