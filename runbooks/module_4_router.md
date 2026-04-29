# Module 4 — Router (runbook index)

**Status:** Phase A complete; Phases B–F pending.
**Owner:** Alfredo Pretel Vargas
**Created:** 2026-04-28
**Last updated:** 2026-04-28

This file is the entry point for Module 4 operational documentation. Module 4 is large enough that each phase has its own runbook covering that phase's component-specific operational surface (failure modes, cost, latency, configuration). This index lists those runbooks and captures cross-phase concerns that don't belong inside any single phase.

---

## 1. What Module 4 is

The Router turns one operator message into a fully-assembled context bundle ready for the client-side reasoning model. Per CONSTITUTION §2.2 it owns six responsibilities: classification, layer loading, RAG activation, token budget enforcement, source priority resolution, and decision logging.

The Router is built across six functionally distinct phases, each shipping as its own component with its own public API. They compose into a pipeline at runtime but live as separate ops surfaces — debugging "the classifier" is a different exercise than debugging "the layer loader."

---

## 2. Phases — status table

| Phase | Status | Runbook |
|---|---|---|
| A — Classifier | ✅ closed 2026-04-28 (commit `e59b943` then docs at `28fec7b`) | [`module_4_phase_a_router_classifier.md`](module_4_phase_a_router_classifier.md) |
| B — Layer loader | ⏸️ blocked on Module 0.X close (needs `layer_loader_contract.md` from M0.X Phase E) | — |
| C — Source priority resolution | ⏸️ blocked on B | — |
| D — Telemetry | ⏸️ blocked on C | — |
| E — Fallback classifier | ⏸️ blocked on D | — |
| F — Tuning | ⏸️ post-30-day post-Module-4-exit (observational, no new code) | — |

When a phase ships, create its runbook at `module_4_phase_<letter>_<slug>.md` following the structure of Phase A's runbook (architecture diagram → files → operational checks → known signals → failure modes → cost → exit gate → handoff → quick reference → change log).

---

## 3. Cross-phase concerns

These cut across multiple Phase runbooks. Capture them here once rather than duplicating per phase.

### 3.1 LiteLLM aliases (ADR-020) — applies to A and E

Every LLM call in Module 4 routes through a LiteLLM proxy alias, never a hardcoded provider model identifier:

- Phase A classifier: `classifier_default` (cascade: Haiku 4.5 → Sonnet 4.6 → gpt-4o-mini)
- Phase E fallback: pure Python keyword matching, no LLM at all

Model swaps are config edits in `~/.litellm/config.yaml`, not code changes. Pre-commit safeguard: `grep -rnE "(claude-[0-9]|gpt-[0-9]|gemini-[0-9])" src/mcp_server/router/` must return nothing.

### 3.2 Telemetry shape (Phase A → Phase D)

`ChatJsonTelemetry` is the dataclass produced by the LiteLLM client wrapper in Phase A. Phase D (Telemetry) reads its fields when writing rows to `routing_logs` and `llm_calls`. Field set at end of Phase A:

```
finish_reason, raw_finish_reason, truncated, truncation_cause,
prompt_tokens, completion_tokens, reasoning_tokens, visible_output_tokens,
total_tokens, max_tokens_requested, headroom_used_ratio, near_truncation,
cache_creation_tokens, cache_read_tokens, cache_hit,
model, response_id, provider_metadata
```

If Phase D writes against a stale field name, Phase A's client wrapper is the source of truth. Don't fork the dataclass.

### 3.3 Classification output shape (Phase A → all downstream)

The contract between Phase A and Phases B/C/D/E is the JSON dict returned by `classifier.classify()`:

```
{
  bucket: 'personal' | 'business' | 'scout' | null,
  project: null,                    // reserved for v2
  skill: null,                      // reserved for v2
  complexity: 'LOW' | 'MEDIUM' | 'HIGH',
  needs_lessons: bool,
  confidence: float [0.0, 1.0]
}
```

This is frozen by `specs/router/spec.md §5.1`. Layer Loader (B), Source priority (C), Telemetry writer (D), and Fallback (E) all read this shape. Changes require a constitutional amendment because §5.1 of the spec is the contract.

### 3.4 Module 0.X dependency (gates Phase B)

Phase B (Layer loader) needs to know which tables map to which layer L0–L4. That mapping is established in Module 0.X spec §8 and frozen in `specs/module-0x-knowledge-architecture/layer_loader_contract.md` at end of M0.X Phase E.

Until M0.X completes Phase E, Phase B cannot start — the contract isn't frozen yet, so any layer loader written today would have to be rewritten when the contract finalizes.

### 3.5 Degraded mode contract (CONSTITUTION §8.43)

Every Phase that touches a downstream dependency (DB, OpenAI, LiteLLM, embeddings) must respect degraded mode: return an explicit `{status: 'degraded', degraded_reason: ...}` payload rather than throwing or returning false success. Phase A already does this for LiteLLM (raises typed exceptions caught by orchestrator). Phases B–E must follow the same pattern.

### 3.6 Eval discipline (Phase A → continuous)

`pytest -m eval` runs the live classifier eval against the 10 hand-labeled examples in `tests/router/classification_examples.md`. It costs ~$0.01 per run and is opt-in (skipped on default `pytest` runs). Thresholds: bucket ≥ 0.80, complexity ≥ 0.70, schema_violations = 0.

Run weekly. If any phase modifies the classifier prompt, re-eval before commit. See Phase A runbook §5.2 + §6.3 for full procedure.

---

## 4. Module 4 high-level dependencies

```
M4 Phase A (Classifier)
       │
       ├─ depends on: LiteLLM proxy (config in ~/.litellm/config.yaml)
       ├─ depends on: src/mcp_server/router/prompts/classify.txt
       └─ produces:   tuple[dict, ChatJsonTelemetry]
                              │
                              ▼
M0.X Phase E (Layer loader contract) — gates the next step
                              │
                              ▼
M4 Phase B (Layer loader)
       │
       ├─ depends on: classifier output dict
       ├─ depends on: M0.X tables (decisions, best_practices, lessons, operator_preferences)
       └─ produces:   layer payload per L0–L4
                              │
                              ▼
M4 Phase C (Source priority resolution)
                              │
                              ▼
M4 Phase D (Telemetry — writes routing_logs + llm_calls)
                              │
                              ▼
M4 Phase E (Fallback classifier — pure keyword rules, no LLM)
                              │
                              ▼
M4 Phase F (Tuning — observational, post-30-day)
```

---

## 5. Cross-references

- **Spec:** `specs/router/spec.md`
- **Plan:** `specs/router/plan.md` (phases A–F with done-when criteria)
- **Tasks:** `specs/router/tasks.md` (atomic task list; A.* checkboxes all `[x]`)
- **Schema:** `docs/DATA_MODEL.md` §4.1 `routing_logs`, §4.3 `llm_calls`
- **LiteLLM gateway:** `docs/INTEGRATIONS.md` §4.5 + ADR-020 (`DECISIONS.md`)
- **Constitution invariants:** `CONSTITUTION.md` §2.2, §2.3, §2.7, §4 rule 8, §5.1, §8.43, §9 rule 7
- **Lessons:** `LL-M4-PHASE-A-001` through `LL-M4-PHASE-A-003` (`docs/LESSONS_LEARNED.md` §9)
- **Module 0.X (gates Phase B):** `runbooks/module_0x_knowledge_architecture.md`
- **SDD trinity rule:** `runbooks/sdd_module_kickoff.md`
