# Layer Loader Contract (Module 0.X → Module 4 Phase B)

**Status:** FROZEN as of `module-0x-complete` tag.
**Contract for:** Module 4 Phase B (Layer Loader implementation).
**Authority:** spec.md §8, CONSTITUTION §2.3 (layer budgets), CONSTITUTION §2.7 (source priority), DATA_MODEL.md §5.

---

## 1. Purpose

Phase B implements a loader that, given (bucket, project, classifier signals), produces an L0–L4 context bundle within the budgets defined in CONSTITUTION §2.3. This document specifies WHICH tables/files Phase B reads for each layer, WHAT filters apply, HOW results are ordered, and WHEN each layer is loaded.

## 2. Inputs Phase B receives at runtime

- `bucket`: 'personal' | 'business' | 'scout' | 'freelance:<client>'
- `project`: optional, project slug within bucket
- `classifier_signals`: dict with at least `needs_lessons: bool`, `needs_skills: bool`
- `current_time`: timestamp for recency ranking

## 3. Layer-by-layer contract

### 3.1 L0 — Identity (always loaded, ~1.2K token budget on identity.md per CONSTITUTION §2.3)

| Source | Filter | Order | Notes |
|---|---|---|---|
| `CONSTITUTION.md` | full file | as-written | infrastructure, no per-file cap |
| `IDENTITY.md` | full file | as-written | hard ≤1,200 tokens (pre-commit hook §7.36) |
| `AGENTS.md` | full file | as-written | infrastructure, no per-file cap |
| `SOUL.md` | full file | as-written | convention ~150-200 tokens, no enforced cap |
| `operator_preferences` | `WHERE active = true AND scope = 'global'` | `ORDER BY category, key` | format as inline `<key>: <value>` lines |

**SQL — L0 preferences:**
```sql
SELECT category, key, value
FROM operator_preferences
WHERE active = true AND scope = 'global'
ORDER BY category, key;
```

**What is NOT in L0:**
- Bucket-scoped preferences (those go in L1)
- Any embedding-search results
- Any task/feedback content

### 3.2 L1 — Bucket context (loaded when bucket is known)

| Source | Filter | Order |
|---|---|---|
| `decisions` | `WHERE status = 'active' AND (bucket = $bucket OR $bucket = ANY(applicable_buckets))` | `ORDER BY severity_rank, created_at DESC` |
| `operator_preferences` | `WHERE active = true AND scope LIKE 'bucket:' || $bucket || '%'` | `ORDER BY category, key` |

**SQL — L1 decisions:**
```sql
SELECT id, title, scope, severity, adr_number,
       LEFT(decision, 500) AS summary
FROM decisions
WHERE status = 'active'
  AND (bucket = $1 OR $1 = ANY(applicable_buckets));
-- Phase B applies recency + severity ordering in app code.
```

**Severity ranking** (CONSTITUTION §5.4 alignment): `critical` > `normal` > `minor`. Phase B materializes this as a CASE expression or sorts in Python.

**What is NOT in L1:**
- Decision `context`, `consequences`, `alternatives` (too verbose for L1; available in L2 if needed)
- Inactive (`status='superseded'`) decisions

### 3.3 L2 — Project context (loaded when project is known within bucket)

| Source | Filter | Order |
|---|---|---|
| `decisions` | `WHERE status = 'active' AND bucket = $bucket AND project = $project` | full content; recency DESC |
| `best_practices` | `WHERE active = true AND scope = 'project:' || $bucket || '/' || $project` | `ORDER BY domain, updated_at DESC` |
| `patterns` | `WHERE $bucket = ANY(applicable_buckets)` | `ORDER BY language, updated_at DESC` |

**SQL — L2 best_practices:**
```sql
SELECT id, title, guidance, rationale, domain
FROM best_practices
WHERE active = true
  AND scope = 'project:' || $1 || '/' || $2;
```

**What is NOT in L2:**
- Cross-bucket best_practices (those load only in L4 when applicable_buckets matches)
- Lessons (those load only in L4 with classifier permission)

### 3.4 L3 — Skills (loaded when classifier_signals.needs_skills = true)

| Source | Filter | Order |
|---|---|---|
| `tools_catalog` | `WHERE kind = 'skill'` | classifier-filtered (Phase B receives a skill_ids list from Router) |

No change from M3. Documented here for completeness.

### 3.5 L4 — Lessons + cross-cutting best practices (loaded when classifier_signals.needs_lessons = true)

| Source | Filter | Order |
|---|---|---|
| `lessons` | `WHERE status IN ('active') AND deleted_at IS NULL AND embedding IS NOT NULL` | vector similarity sequential scan, top-K |
| `best_practices` | `WHERE active = true AND (domain = $classifier_domain OR $bucket = ANY(applicable_buckets))` | vector similarity, top-K |

**SQL — L4 lessons (sequential scan per ADR-024):**
```sql
SELECT id, title, next_time, similarity
FROM (
  SELECT id, title, next_time,
         (1 - (embedding <=> $1::vector)) AS similarity
  FROM lessons
  WHERE status = 'active'
    AND deleted_at IS NULL
    AND embedding IS NOT NULL
    AND ($2::text IS NULL OR bucket = $2 OR $2 = ANY(applicable_buckets))
) sub
ORDER BY similarity DESC
LIMIT $3;
```

Phase B should default `top_k = 5` per layer and adjust based on remaining budget.

## 4. Tables explicitly NOT loaded into context

These tables exist but Phase B never reads them as part of the bundle:
- `tasks` — operational; surfaced only via `task_list` tool when operator asks
- `router_feedback` — operational; consumed by Module 6 reflection worker
- `pending_embeddings` — internal queue; managed by auto-index worker
- `routing_logs` — analytics partition; queried via Router-internal tools only
- `tools_catalog` — except for L3 skill rows; tool registry not bundle content

## 5. Performance contract

Per ADR-024:
- All vector searches use **sequential scan** (no HNSW indexes exist). At <5K vectors per table, latency is 10–50ms per layer.
- L4 query in production today touches ~30 lessons + ~0 best_practices = trivial cost.
- When `lessons` or `best_practices` cross 50K rows, ADR-024 mandates HNSW re-introduction. That's a future migration, not Phase B's concern.

## 6. Cache invalidation triggers

Phase B SHOULD cache layer bundles per `(bucket, project, classifier_hash)` for the duration of one turn. Cache MUST invalidate on:
- `operator_preferences` UPDATE/INSERT/DELETE (L0)
- `decisions` INSERT or `status` change (L1, L2)
- `best_practices` INSERT/UPDATE/deactivate (L2, L4)
- `lessons` INSERT or `status` change (L4)

A simple LISTEN/NOTIFY on these tables is sufficient. Implementation is Phase B's choice.

## 7. Token budgets per layer

Per CONSTITUTION §2.3:

| Layer | Budget | Behavior on overflow |
|---|---|---|
| L0 | identity.md ≤1,200 toks (hard); rest no per-file cap | pre-commit hook blocks if identity.md exceeds |
| L1 | ~3,000 tokens (soft) | Phase B truncates lowest-severity decisions first |
| L2 | ~5,000 tokens (soft) | Phase B truncates oldest patterns/best_practices first |
| L3 | classifier-determined | Phase B respects skill_ids list verbatim |
| L4 | ~4,000 tokens (soft) | Phase B uses smaller top_k or excerpt-not-full content |

Soft budgets are advisory. Hard budgets (identity.md) are enforced by infrastructure outside Phase B.

## 8. Observability requirements for Phase B

Phase B SHOULD log per turn:
- Which layers loaded (L0 always, L1-L4 conditional)
- Per-layer row counts and token counts
- Cache hit/miss
- Total bundle assembly latency

Schema for `layer_load_logs` table is OUT OF SCOPE for this contract. Phase B owns that table.

## 9. Frozen interface — what changes need a new ADR

Any of the following requires a new ADR superseding this contract:
- Adding a new layer (L5)
- Removing a table from a layer
- Changing the SQL filter shape (e.g., adding new WHERE conditions Phase B must respect)
- Changing token budgets

Adding new content sources within an existing layer (e.g., a new prefs scope variant) does NOT require an ADR — Phase B can adapt at runtime.

---

**Last updated:** 2026-04-28
**Next review:** When Phase B implementation begins.
