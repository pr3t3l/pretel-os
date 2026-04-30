# Skill: skill_discovery — How to find and use registered skills

**Slug:** `skill_discovery`
**Kind:** procedural skill (L3)
**Applicable buckets:** `personal`, `business`, `scout`
**Loaded by default:** yes (utility_score = 1.0)

---

## 1. Purpose

This skill teaches an LLM running on pretel-os how to **discover** the skills available to it on any given turn, **decide** which one applies (if any), and **load** its full content before answering.

The pretel-os system carries a growing catalog of registered skills — `vett`, `sdd`, and others added over time. Each skill is a focused methodology: how to evaluate vendors, how to drive a spec-driven build, how to triage a budget question. They live as markdown files under `skills/` and as rows in the `tools_catalog` table.

Without this skill, an LLM will tend to default to general knowledge for every question — even when a **registered, validated, operator-trusted skill exists for that exact case**. That defeats the purpose of having a skill catalog. This skill exists to make discovery automatic.

The contract, in one line:

> **Every turn, after classification, glance at `available_skills` before answering. If a skill matches the query, load it. If unsure, ask the catalog — never the operator.**

---

## 2. When to use this skill

This skill is loaded into L3 by default for every bucket. **You never need to "trigger" it explicitly** — its rules apply to every turn the LLM handles via the pretel-os Router.

The behaviors below are unconditional:

1. After the Router has classified a turn (you receive the `ContextBundle`), look at the `available_skills` field before composing your answer.
2. When `available_skills` contains a skill whose name or description maps to the user's query, load it via `load_skill(name)` and follow its instructions.
3. When no skill in `available_skills` is an obvious match but the query is non-trivial, call `recommend_skills_for_query(message, bucket)` to ask the catalog for ranked candidates.
4. When neither path turns up a skill (or the top recommendation is below threshold), answer from general knowledge — but only after the discovery glance.

The discipline lives in the **glance**: the half-second of attention spent reading `available_skills`. Skipping it is the most common failure mode.

---

## 3. How to read `available_skills` from `get_context` output

Every call to `get_context(message, ...)` returns a `ContextBundle` dict. One of its keys is `available_skills`:

```json
{
  "request_id": "...",
  "classification": {"bucket": "business", "complexity": "MEDIUM", ...},
  "bundle": {...},
  "available_skills": [
    {"name": "vett", "description_short": "Vendor Evaluation & Technology Triage framework", "utility_score": 0.85},
    {"name": "sdd",  "description_short": "Spec-Driven Development process",                  "utility_score": 0.90}
  ],
  "active_projects": [...],
  ...
}
```

The list is **already filtered** to the classified bucket and **already sorted** by `utility_score DESC`. It is capped at 10 entries — that is small enough to scan in one glance.

The mapping rule is simple:

- Read each `name` and `description_short`.
- Ask: "would this skill's framework directly apply to the user's query?"
- If yes for one entry → that's your skill. Load it.
- If yes for multiple → load the highest-utility one first; mention the alternatives if they remain relevant after the primary completes.
- If no for all → fall through to §4.

Do **not** load every skill listed. Loading one skill that doesn't apply pollutes context with hundreds of irrelevant tokens; loading the right one focuses you.

---

## 4. When to call `recommend_skills_for_query`

When `available_skills` exists but no entry's name/description obviously maps to the user's query, do not give up and answer from general knowledge yet. Ask the catalog:

```
recommend_skills_for_query(message: <the user's exact message>, bucket: <classified bucket>)
```

This tool runs a deterministic keyword + utility scoring pass over every skill applicable to that bucket and returns the top 3 with `score >= 1.0`. The shape:

```json
{
  "status": "ok",
  "recommendations": [
    {"name": "vett", "score": 1.255, "reason": "matched keyword: 'evaluar'", ...}
  ]
}
```

Three reasons to lean on `recommend_skills_for_query` instead of just scanning `available_skills`:

1. **Cross-language queries.** The user writes in Spanish ("evalúa este vendor"); the skill description is in English ("Vendor Evaluation"). The `vett` skill registers Spanish keywords (`evaluar`, `vendedor`, `proveedor`) so the recommender catches the match even when a literal name-scan misses it.
2. **Synonyms.** "Tool review", "platform review", "vett" all point at the same skill. The recommender's keyword list captures them; the description_short shows only one phrasing.
3. **You're not sure.** If the glance turned up two plausible skills, let the recommender break the tie with utility-weighted scoring.

If `recommendations` is empty, no skill matched above threshold. **That is a clean answer**: skip skill loading and proceed with general knowledge.

---

## 5. How to call `load_skill(name)`

Once you have a skill name (from the glance or from `recommend_skills_for_query`), fetch the full content:

```
load_skill(name='vett')
```

Returns the full markdown body of `skills/vett.md`. Read it once, then follow its instructions to drive the rest of the turn.

Notes:

- `load_skill` returns content, not metadata. The metadata (utility_score, applicable_buckets) is what `available_skills` and the tools_catalog already gave you.
- A skill file may reference a bucket-specific overlay (like `buckets/scout/skills/vett_scout_context.md`). The overlay is loaded into L2 separately by the Layer Loader when the bucket matches; you do not need to load it manually.
- Skills should be loaded **at most once per turn**. If you've already loaded a skill in this turn, treat the second load as redundant.

---

## 6. The discovery cycle

Every turn that involves real work follows the same five steps:

```
1. RECEIVE        — operator query lands; Router classifies it.
2. GLANCE         — read available_skills from the ContextBundle.
3. MATCH          — does any skill's name/description_short map to the query?
                    If yes → step 5 with that name.
                    If unsure → step 4.
                    If no → answer from general knowledge.
4. RECOMMEND      — call recommend_skills_for_query(message, bucket).
                    If recommendations non-empty → step 5 with top-1 name.
                    If recommendations empty → answer from general knowledge.
5. LOAD + EXECUTE — call load_skill(name); follow the skill's lifecycle.
                    Cite which skill you used in the reply.
```

The whole cycle is meant to be **fast** — a glance plus at most one tool call before you start composing the answer. If the cycle takes more than a few hundred milliseconds of LLM-side reasoning, you're overthinking it; pick the most plausible match and move on.

---

## 7. Anti-patterns

These behaviors break the discovery contract. Treat each as a soft "do not do" — recoverable in the same turn if you catch yourself, but never default to them.

**Do not invent tools or skills that are not in the catalog.**
If you find yourself thinking "I bet there's a `vendor_eval` tool", stop and check `available_skills` or the registered tools list. Pretel-os registers tools explicitly via `register_skill` / `register_tool`; nothing exists outside that registry.

**Do not ask the operator "what tool should I use".**
That question is a discovery failure. The operator has already told the system what's available — that's exactly what `available_skills` and `recommend_skills_for_query` exist for. Ask the catalog, not the operator.

**Do not skip the discovery glance because you "remember" a skill from a prior turn.**
The catalog can change between turns: a skill can be added, deprecated, or have its utility_score adjusted by the operator. Each turn's `available_skills` is the source of truth for that turn. Memory of last turn is a hint, not a substitute for the glance.

**Do not call `load_skill` on a name you have not seen in `available_skills` or `recommendations` first.**
The name might not exist, or might not apply to the current bucket, or might be deprecated. Loading content blindly wastes tokens at best and surfaces wrong instructions at worst.

**Do not load multiple skills "just in case".**
Skills are large. Loading three when one applies pollutes the context window; the LLM then has to triage three competing methodologies in the same turn. Pick one, follow it, mention the others briefly if relevant.

**Do not treat `available_skills: []` as a degraded state.**
An empty list means the catalog has no applicable skill for the classified bucket — it does not mean the system is broken. Answer from general knowledge with confidence; the catalog will be expanded by the operator when patterns emerge.

---

## 8. Worked examples

### Example A — Clear skill match

> User (Telegram, bucket=scout): *"evalúa este vendor para Scout: $TOOL"*

- **Classification:** bucket=scout, complexity=MEDIUM.
- **Glance at `available_skills`:** `[{name: 'vett', description_short: 'Vendor Evaluation & Technology Triage framework', ...}, {name: 'sdd', ...}]`.
- **Match:** "evaluate" / "vendor" map directly to `vett`. No need for `recommend_skills_for_query` — the glance already resolves it.
- **Action:** `load_skill('vett')`. Follow its lifecycle (`§4 → §5 → §6` of vett.md). The Scout overlay is in L2 already because bucket=scout; consult its variable bindings as the framework directs.
- **Reply opens with:** "Voy a usar el skill `vett` para esta evaluación, con el overlay de Scout cargado..."

### Example B — Ambiguous case (use the recommender)

> User (Telegram, bucket=business): *"ayúdame a planear esto bien"*

- **Classification:** bucket=business, complexity=MEDIUM.
- **Glance at `available_skills`:** `[{name: 'sdd', ...}, {name: 'vett', ...}, ...]`.
- **Match:** "planear" doesn't directly map to any name; "plan" is in `sdd` description but the user might also mean a budget plan or a marketing plan. Genuinely ambiguous.
- **Action:** `recommend_skills_for_query(message='ayúdame a planear esto bien', bucket='business')`.
- **Recommender returns:** `[{name: 'sdd', score: 1.27, reason: "matched keyword: 'plan'"}]`.
- **Decision:** load `sdd`.
- **Action:** `load_skill('sdd')`, then follow §2 ("When to use SDD") to confirm scope before driving the lifecycle.
- **Reply opens with:** "Suena a SDD — voy a verificar primero si aplica el ciclo completo..."

### Example C — No skill needed

> User (Telegram, bucket=personal): *"qué hora es"*

- **Classification:** bucket=personal, complexity=LOW.
- **Glance at `available_skills`:** `[]` or whatever the personal bucket carries; nothing matches "tiempo / hora / fecha" semantically.
- **Match:** none. Don't bother with `recommend_skills_for_query` for a LOW-complexity factual query — the bar isn't met.
- **Action:** answer from general knowledge directly. "Son las 15:42 EDT (zona horaria del operador, identity.md §1)."
- **No `load_skill` call. No tool call.** A LOW-complexity factual question does not earn a discovery cycle past the glance.

---

## 9. Cost and latency notes

The discovery cycle is cheap by design:

- The glance is **free** — `available_skills` is already in the bundle returned by `get_context`. Reading it costs you only the tokens already paid for.
- `recommend_skills_for_query` is a **single SQL query** + a Python sort. No LLM call. Sub-millisecond on typical hardware.
- `load_skill` is a **filesystem read** plus a small DB lookup. Cheap.

The expensive part — running the loaded skill's lifecycle — is what justifies the discipline. A 200-line skill that takes 30 seconds to follow is wildly cheaper than a 30-minute LLM session producing a custom plan from scratch every time.

---

## 10. References

- `get_context` — Router orchestrator that produces the ContextBundle (`src/mcp_server/router/router.py`).
- `recommend_skills_for_query` — keyword + utility scoring (`src/mcp_server/tools/awareness.py`).
- `load_skill` — fetch full skill content from `skills/<name>.md` (`src/mcp_server/tools/catalog.py`).
- `tool_search` — broader catalog search across kind=tool|skill (`src/mcp_server/tools/catalog.py`).
- `tools_catalog` — DB-side registry of every skill and tool (DATA_MODEL §5.10).
- `register_skill` / `register_tool` — how to add new entries to the catalog.
- pretel-os CONSTITUTION §2.2 — Router gateway as the single discovery surface.
- pretel-os CONSTITUTION §5 — context layering (L0–L4) and how skills flow into L3.
