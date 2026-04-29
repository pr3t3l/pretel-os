# Router tuning queries (Phase F deliverable, F.1.1)

**Status:** Ongoing post-Module-4-exit. This file collects the queries
the operator runs against `routing_logs` + `llm_calls` to drive Phase F
tuning decisions per `specs/router/plan.md` §8.

**When to run:** weekly, or when telemetry shows anomalies. The 3
spec §9.3 audit queries (already in `runbooks/router_audit_queries.sql`)
are the baseline; the 5 queries here add tuning-specific signal.

**How to run:** `psql "$DATABASE_URL" -f runbooks/router_tuning.md`
won't work because this file is markdown — copy the SQL blocks below
into psql, or extract them to ad-hoc scripts as needed. Each query is
self-contained.

---

## A. Baseline (cross-reference to spec §9.3)

The 3 audit queries from `runbooks/router_audit_queries.sql`:

1. **Classifier uptime** — share of `llm` vs `fallback_rules` over the
   last 30 days. Healthy when `llm` ≫ `fallback_rules`.
2. **Per-model cost + quality** — `avg(user_satisfaction)` and `cost_usd`
   grouped by resolved model name. Drives provider-cascade tuning.
3. **RAG mismatch** — count of turns where `rag_expected ≠ rag_executed`.
   0 rows is the healthy state.

Run those first. The 5 queries below are additive and surface
patterns the baseline doesn't.

---

## B. Tuning queries (5)

### B.1 Per-bucket classification accuracy

Compare classifier output against operator overrides (`router_feedback`
rows where `feedback_type='wrong_bucket'`). High wrong-bucket rate per
bucket → prompt-engineering target.

```sql
WITH overrides AS (
    SELECT request_id, proposed_correction
    FROM   router_feedback
    WHERE  feedback_type = 'wrong_bucket'
      AND  created_at > now() - interval '30 days'
)
SELECT  rl.classification ->> 'bucket'                 AS predicted_bucket,
        count(*)                                       AS turns,
        count(o.request_id)                            AS overridden,
        round(100.0 * count(o.request_id) / count(*), 2) AS override_pct
FROM    routing_logs rl
LEFT JOIN overrides o USING (request_id)
WHERE   rl.created_at > now() - interval '30 days'
  AND   rl.classification_mode = 'llm'
GROUP BY 1
ORDER BY override_pct DESC NULLS LAST;
```

**Decision criterion:** any bucket with `override_pct > 10%` over 100+
turns is a prompt-iteration target. Update
`src/mcp_server/router/prompts/classify.txt` and re-eval via
`pytest -m eval`.

---

### B.2 Per-model latency distribution

Phase D's bullet 8 (per-turn latency < 2s for HIGH complexity) is
provider-variance dependent. This query surfaces P50/P95/P99 per
concrete model so the operator can pin the LiteLLM cascade head to the
fastest provider.

```sql
SELECT  lc.model,
        rl.classification ->> 'complexity' AS complexity,
        count(*)                            AS turns,
        round(percentile_cont(0.50) WITHIN GROUP (ORDER BY rl.latency_ms)::numeric, 0) AS p50_ms,
        round(percentile_cont(0.95) WITHIN GROUP (ORDER BY rl.latency_ms)::numeric, 0) AS p95_ms,
        round(percentile_cont(0.99) WITHIN GROUP (ORDER BY rl.latency_ms)::numeric, 0) AS p99_ms,
        max(rl.latency_ms)                  AS max_ms
FROM    routing_logs rl
JOIN    llm_calls    lc USING (request_id)
WHERE   rl.created_at > now() - interval '30 days'
  AND   lc.purpose = 'classification'
GROUP BY 1, 2
ORDER BY complexity, p95_ms;
```

**Decision criterion:** if HIGH-complexity P95 > 2000ms for the head
model, swap to a faster model in `~/.litellm/config.yaml` (per the
runbook §4 procedure) and re-measure after a week. If no provider
clears 2s P95 the gate text in `plan.md §10` should be amended via ADR
to reflect provider reality.

---

### B.3 Sub-bucket detection rate

`spec.md §13` defers the sub-bucket detection signal (dotted path vs
keyword scan) to Phase F. This query measures how often the classifier
emits a non-trivial dotted bucket today.

```sql
SELECT  CASE
            WHEN classification ->> 'bucket' LIKE '%/%' THEN 'sub-bucketed'
            WHEN classification ->> 'bucket' IS NULL    THEN 'unbucketed'
            ELSE                                              'top-level'
        END                                            AS bucket_kind,
        count(*)                                       AS turns,
        round(100.0 * count(*) / sum(count(*)) over (), 2) AS pct
FROM    routing_logs
WHERE   created_at > now() - interval '30 days'
GROUP BY 1
ORDER BY 2 DESC;
```

**Decision criterion:** if `sub-bucketed` < 5% across 30 days while the
operator manually corrects bucket-vs-sub-bucket via `router_feedback`,
the prompt isn't getting the dotted path through reliably — switch to
a second-pass keyword scan or amend the prompt with explicit dotted-path
examples. Track via `LL-M4-PHASE-A-002` lesson tags.

---

### B.4 Fallback rate by hour-of-day

LiteLLM provider availability often dips at predictable times
(maintenance windows, peak-load throttling). This query bins the
fallback rate by hour-of-day so the operator can spot patterns.

```sql
SELECT  date_trunc('hour', created_at) AS hour,
        sum(CASE WHEN classification_mode = 'fallback_rules' THEN 1 ELSE 0 END) AS fallback,
        count(*)                                            AS total,
        round(100.0 * sum(CASE WHEN classification_mode = 'fallback_rules' THEN 1 ELSE 0 END)
              / NULLIF(count(*), 0), 2)                     AS fallback_pct
FROM    routing_logs
WHERE   created_at > now() - interval '7 days'
GROUP BY 1
ORDER BY hour DESC;
```

**Decision criterion:** if a specific hour-of-day shows persistent
`fallback_pct > 20%`, drill into `degraded_reason` for that window
(query in `runbooks/module_4_router.md §3`) — usually points to
provider-side rate limits. Mitigation: re-order the LiteLLM cascade so
the first provider isn't the throttled one during that window.

---

### B.5 Low-confidence cluster detection

`confidence < 0.6` is logged but doesn't trigger fallback (per spec
§5.1). Sustained low-confidence clusters by topic suggest the
classifier is uncertain about a recurring class of message that the
prompt doesn't cover well.

```sql
SELECT  classification ->> 'bucket'                AS bucket,
        classification ->> 'complexity'            AS complexity,
        round(avg((classification ->> 'confidence')::numeric)::numeric, 2) AS avg_conf,
        count(*)                                   AS turns,
        count(*) FILTER (WHERE (classification ->> 'confidence')::numeric < 0.6) AS low_conf_turns
FROM    routing_logs
WHERE   created_at > now() - interval '30 days'
  AND   classification_mode = 'llm'
GROUP BY 1, 2
HAVING  count(*) FILTER (WHERE (classification ->> 'confidence')::numeric < 0.6) > 5
ORDER BY low_conf_turns DESC;
```

**Decision criterion:** any (bucket, complexity) cell with > 5 low-
confidence turns in 30 days is a prompt-engineering target. Pull a
sample of 5 message_excerpts from those rows, add as in-prompt
examples in `prompts/classify.txt`, re-eval. Spec §13 tracks this as
"Sustained low-confidence alerting" — Phase F resolves when the
operator decides whether to elevate to a real alert.

---

## C. Decision-record cadence

Each tuning decision driven by these queries should produce one of:

- A **lesson** (`save_lesson` MCP tool) capturing the data + the
  change. Tag with `phase-f-tuning` for Module 6 reflection.
- An **ADR** (`decision_record` MCP tool) when the change supersedes
  an earlier architectural choice (e.g., changing the cascade head
  supersedes ADR-020's implied default).
- A **commit** to `prompts/classify.txt` or `~/.litellm/config.yaml`
  with the data attached in the commit message body.

Don't tune silently — the audit trail is what makes Phase F a
discipline rather than vibes-based knob-twisting.

---

## D. Cross-references

- **Spec:** `specs/router/spec.md` §9.3 (the 3 baseline audit queries),
  §13 (open questions deferred to Phase F).
- **Plan:** `specs/router/plan.md` §8 (Phase F scope).
- **Module runbook:** `runbooks/module_4_router.md` (§3 LiteLLM outage,
  §5 audit queries reference).
- **Baseline SQL:** `runbooks/router_audit_queries.sql`.
