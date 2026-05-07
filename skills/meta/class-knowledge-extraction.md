# Skill: class-knowledge-extraction — Distill course content into the knowledge base

**Slug:** `class-knowledge-extraction`
**Kind:** procedural skill (L3, meta)
**Applicable buckets:** `personal`, `business`
**Loaded by default:** no (utility-driven; activates on course/lesson signals)

---

## 1. Purpose

This skill teaches an LLM running on pretel-os how to take **course/lesson content** the operator pastes into a session and **distill it into the correct pretel-os knowledge structures** — without saving noise.

The operator is taking AI Engineering courses (and other ones over time). When a class is shared into a session, the system must consistently transform it into:

- 0–N rows in `best_practices` (decision criteria — "use X when Y")
- 0–N rows in `lessons` (gotchas with `next_time` clauses)
- 0–N new skill `.md` files (procedural / syntax-dense reference material)

Without this skill, an LLM tends to either (a) save a verbose summary as one giant lesson — polluting search; or (b) skip saving entirely — losing the value of the course. This skill encodes the canonical heuristic, the quality bar, and the operator-in-the-loop workflow that prevents both failure modes.

The contract, in one line:

> **For each conceptual block in a class, ask three questions in order. Save only what passes one of them. Always present the proposal to the operator for approval before writing.**

---

## 2. When this skill activates

The Router does **not** load this skill by default — it's loaded when the user's message contains course/lesson signals or when `recommend_skills_for_query` ranks it above threshold for the current turn.

Trigger phrases (operator says something like):

- Spanish: *"te paso la clase de hoy"*, *"vamos a analizar esta lección"*, *"guarda lo importante de esto"*, *"acabo de ver esta clase"*, *"transcripción del curso"*, *"módulo del curso"*, *"voy a pegarte una clase"*
- English: *"here's today's class"*, *"let's analyze this lecture"*, *"save what's important from this"*, *"distill this lesson"*, *"course transcript"*, *"lecture notes"*

Trigger contexts (no explicit phrase, but obvious from shape):

- A long pasted block of structured text that looks like a class transcript or lecture notes (multiple sections, code blocks, definitions, examples).
- A URL pointing to an educational platform (Maven, DeepLearning.AI, Coursera, YouTube edu channel, etc.) followed by content the operator wants analyzed.
- A heading like "Class N", "Lesson N", "Module N" followed by content.

This skill does **not** activate for:

- Operational lessons from the operator's own work (use `save_lesson` directly with the appropriate bucket and tags).
- Architectural decisions made during active development (use `decision_record` directly).
- Consolidation of already-saved knowledge (that's a separate process — Dream Engine + manual review).
- Personal notes / journaling (use `save_lesson` with `bucket=personal` directly).
- Project-specific debugging insights (use `save_lesson` with the specific project tag).

The discipline lives in the **classification**: this skill is for *external* learning material being absorbed into the system, not for capturing the operator's own insights.

---

## 3. Core heuristic — the three questions

For each conceptual block in the class (a definition, a comparison, a code example, a numbered list of trade-offs), ask these three questions **in order**. Save under the structure of the first YES.

If all three answers are NO for that block → **don't save it**. Noise in the knowledge base is worse than missing information: it degrades the precision of every future semantic search.

### 3.1 Question 1 — Is there an actionable decision criterion?

A decision criterion has the shape: *"Use X when Y; otherwise use Z"*, or *"Choose A over B if condition C holds"*. It survives outside the class context — the operator could apply it months later to a brand-new project.

If YES:

- **Target table:** `best_practices`
- **MCP tool:** `best_practice_record`
- **Required fields:**
  - `title`: short headline naming the decision (≤ 80 chars). Format: "*Decision*: X over Y when Z".
  - `guidance`: distilled rule (NOT class summary). 2–4 sentences. Reads as imperative advice.
  - `rationale`: one sentence — the *why* behind the rule (cite the principle, not the lecturer).
  - `domain`: one of the existing domain literals (`process`, `architecture`, `prompting`, etc.) — pick the closest fit, do not invent.
  - `scope`: usually `'global'` for course material; `'project'` only if scoped to a specific in-flight project.

- **Real example (Caso A — CAG vs RAG):**

  ```
  title    = "CAG when context fits the model window; RAG when corpus exceeds it"
  guidance = "Use Cache-Augmented Generation (CAG) when the entire knowledge base
              fits in the model's effective context window. Switch to
              Retrieval-Augmented Generation (RAG) when the corpus exceeds the
              window or grows over time. CAG is simpler operationally — no
              vector DB, no chunk-size tuning — but pays per-token at every call."
  rationale = "Effective context window <= ~70% of advertised window due to
               recall degradation in the middle of long contexts ('lost in the
               middle' phenomenon)."
  domain   = "architecture"
  scope    = "global"
  ```

### 3.2 Question 2 — Is there a gotcha that prevents a future error?

A gotcha is a discovered surprise: *"X looks like it should work but doesn't because Y"*. The operator must be able to recognize the situation in the future and act differently because of this lesson.

If YES:

- **Target table:** `lessons`
- **MCP tool:** `save_lesson`
- **Required fields (per CONSTITUTION §5.2 rule 13 — auto-approval requires all four):**
  - `title`: surprising claim (≤ 80 chars). Format: "*Symptom*: actual cause" or "X breaks when Y".
  - `content`: 2–5 sentences. What looked right, what actually happened, root cause.
  - `next_time`: imperative clause — what to do when this situation recurs. **Without `next_time`, the lesson does NOT auto-approve and lands in `pending_review`**.
  - At least one tag identifying the technology/pattern (`embeddings`, `prompt-engineering`, `rag`, `cag`, etc.).

- **Real example (Caso A — context window):**

  ```
  title     = "Effective context window != advertised window in long-context models"
  content   = "Long-context models (200k+) advertise their max window but show
               accuracy degradation in the middle of long contexts ('lost in the
               middle' / Liu et al. 2023). A 200k-token model retrieves with high
               accuracy in the first ~50k and last ~10k; the middle 140k is
               degraded. Treat advertised window as upper bound, not effective
               capacity."
  next_time = "When sizing context for CAG/RAG decisions, plan for ~50–70% of the
               advertised window as effective. Place high-priority content at
               start or end, not middle. Test recall before committing."
  bucket    = "personal"
  tags      = ["ai-engineering", "context-window", "long-context", "lost-in-middle"]
  ```

### 3.3 Question 3 — Is there procedural / syntax-dense content worth a skill file?

A skill file is justified when the material is **referenced repeatedly during execution** — code APIs, multi-step procedures, framework lifecycles. The test: would the operator copy-paste this back into a session whenever they hit the same task? If yes → skill. If no → it's a one-time decision (Q1) or a gotcha (Q2).

If YES:

- **Target:** new file `skills/<domain>/<slug>.md`, then registered in `tools_catalog` via `register_skill`.
- **MCP tool:** `register_skill` (and a SQL UPDATE on `trigger_keywords` afterwards — `register_skill` does not currently accept it as a parameter).
- **Structure of the new skill (mirror the conventions of `sdd.md`, `vett.md`, this file):**
  - Title + slug + applicable buckets + loaded-by-default flag.
  - "When to use this skill" — explicit triggers.
  - Lifecycle / steps / API reference (the procedural body).
  - Anti-patterns specific to the domain.
  - Cross-references.
- **Required fields for `register_skill`:**
  - `name`: kebab-case slug, unique across the catalog.
  - `description_short`: ≤ 80 chars. One-line propósito.
  - `description_full`: ≥ 500 chars, rich in keywords, bilingual where appropriate, includes WHEN-USE / KEYWORDS / NO-USE-FOR / DEPENDENCIES blocks.
  - `skill_file_path`: path relative to repo root.
  - `applicable_buckets`: array — typically `['personal', 'business']` for course material.

- **Real example (Caso B — OpenAI Responses API):**

  Class B explains the full syntax of `client.responses.create`, parameter semantics, error handling, response structure. That's procedural and the operator will copy-paste it whenever they touch the API → **skill file is justified**.

  ```
  Output:
    file = "skills/ai-engineering/openai-responses-api.md"
    register_skill(
        name="openai-responses-api",
        description_short="OpenAI Responses API: syntax, params, error handling",
        description_full="...",  # rich keywords + when/no-use/deps
        skill_file_path="skills/ai-engineering/openai-responses-api.md",
        applicable_buckets=["personal", "business"]
    )
  ```

  Possibly also 1–2 best_practices distilled from the class (e.g., *"always verify response.status before parsing content"*) — those are Q1 hits inside the same class, separate from the procedural skill.

### 3.4 If all three answers are NO

The block is general background, motivational framing, lecturer narrative, or already-known material. **Do not save it.** A class that produces zero entries is a clean outcome — the brief explicitly allows this.

---

## 4. Quality rules — anti-noise discipline

Five rules. Violating any of them produces noise that harms future search precision more than it helps recall.

1. **Never save the literal text of the class as a single entry.** Distill — extract the rule, the gotcha, or the procedure. If you find yourself copy-pasting more than 3 sentences from the class into a `content` or `guidance` field, you are summarizing, not distilling. Re-read Q1/Q2/Q3 and try again.

2. **Every entry must carry at least one domain tag.** Without a domain tag, the entry is unreachable via filtered search and pollutes broader queries. Domain tags follow §8 (Domain tagging convention). The course slug (e.g., `ai-engineering`) is the base tag; sub-tags come from the topic of the specific class (e.g., `rag`, `cag`, `prompt-engineering`, `agents`, `evals`, `responses-api`).

3. **Lessons must have a `next_time` clause.** Without it, CONSTITUTION §5.2 rule 13 auto-approval fails and the lesson rots in `pending_review` until the operator triages manually. The clause is imperative and concrete — "use X" not "consider Y". If you cannot produce an imperative `next_time`, the block is not a lesson; reconsider Q1 or skip.

4. **Best practices must have a clear `rationale`.** The rationale is one sentence answering *why* the rule holds — cite the principle, the trade-off, or the empirical observation. A best practice without rationale is dogma; a best practice with rationale is a tool the operator can re-evaluate when conditions change.

5. **Always search for duplicates before proposing.** Before listing a new entry in the operator-review summary (§5), call:

   - `best_practice_search(query=<the proposed title>, top_k=5)` for Q1 hits
   - `search_lessons(query=<the proposed title>, tags=[domain_tag], limit=5)` for Q2 hits

   If a result with similarity ≥ 0.90 is returned, do not propose the new entry as fresh. Either propose it as an *update* / *supersession* (with explicit reference to the existing row's UUID) or skip it. Vector duplicates are silent destroyers of search precision.

A class that produces zero entries because nothing crosses the bar is a **healthy outcome**, not a failure. Force-saving to "have something to show" is exactly the failure mode this skill prevents.

---

## 5. Operator-in-the-loop workflow

The LLM **never writes directly** to `best_practices`, `lessons`, or `register_skill` from this skill. The flow is strictly:

1. **Ingest** — read the full class content the operator pasted (or referenced).
2. **Identify candidates** — apply the three questions to each conceptual block. Run §4 rule 5 duplicate searches inline.
3. **Present a structured proposal** — write a single markdown summary in chat (format below). Each proposed entry gets a checkbox the operator can read at a glance.
4. **Wait for explicit approval** — the operator may say "go", may edit individual items ("change the title of #2"), may delete items ("skip #3"), or may reject the whole batch.
5. **Execute** — for each approved item, call the corresponding MCP tool (`best_practice_record`, `save_lesson`, `register_skill` + UPDATE).
6. **Report results** — emit a final block listing each created entry's UUID and a one-line summary, plus any operator-rejected items as a record of choices made.

### 5.1 Proposal summary format (mandatory)

```markdown
## Class knowledge extraction — proposal

**Class:** <one-line description: title or topic + course>
**Domain tag:** `<base-tag>` (sub-tags below per item)
**Duplicates checked:** yes — <N best_practice queries + N lesson queries ran>

---

### Best practices (Q1 hits)

- [ ] **#1 — `best_practice_record`**
  - **title:** "..."
  - **guidance:** "..."  (2–4 sentences)
  - **rationale:** "..."  (1 sentence)
  - **domain:** `process` | `architecture` | ...
  - **scope:** `global` | `project`
  - **tags:** [`<base>`, `<sub>`, ...]
  - **dup-check:** "no match ≥0.90 in best_practice_search(<query>, top_k=5)"

### Lessons (Q2 hits)

- [ ] **#2 — `save_lesson`**
  - **title:** "..."
  - **content:** "..."  (2–5 sentences)
  - **next_time:** "..."  (imperative — required for auto-approve)
  - **bucket:** `personal` | `business`
  - **tags:** [`<base>`, `<sub>`, ...]
  - **dup-check:** "no match ≥0.90 in search_lessons(<query>, tags=[<base>])"

### Skills (Q3 hits)

- [ ] **#3 — new skill `.md` + `register_skill`**
  - **path:** `skills/<domain>/<slug>.md`
  - **slug:** `<kebab-case-name>`
  - **description_short:** "..."  (≤ 80 chars)
  - **description_full plan:** "..."  (1–2 sentences describing what will be in it)
  - **applicable_buckets:** `[personal, business]`
  - **proposed sections:** 1. Purpose ... 2. When to use ... 3. ... (the outline)
  - **trigger_keywords (post-register UPDATE):** [...]

### Skipped blocks

- "<block topic>" — all 3 questions answered NO.
- "<block topic>" — duplicate of <existing UUID> with sim 0.94; superseding instead.

---

**Awaiting your explicit approval.** Reply with:
- `go` to execute everything
- `go but skip #N` to omit specific items
- `edit #N: <new value for field>` to adjust before executing
- `cancel` to drop the batch
```

### 5.2 Execution + report format

After approval, execute the tools serially and emit:

```markdown
## Extraction complete

- ✅ #1 best_practice `<uuid>` — "<title>"
- ✅ #2 lesson `<uuid>` — "<title>" (status: `active` if auto-approved, else `pending_review`)
- ✅ #3 skill registered `<uuid>` — `skills/.../<slug>.md` written + UPDATE on trigger_keywords

**Skipped:** #4 per operator request.
**Failed:** none. (or — list failures with error messages.)

**Commit:** none made — this skill never commits the markdown changes itself. Run `git add skills/<domain>/<slug>.md && git commit` separately when ready.
```

---

## 6. Anti-patterns (DO NOT do these)

The seven failure modes that make this skill produce noise instead of signal:

1. **❌ Saving the class summary as one giant lesson.** A class is multiple blocks; force the heuristic on each block, not on the class as a whole. One 1000-word `content` field is a violation of §4 rule 1 by definition.

2. **❌ Creating a skill `.md` "just in case" / "this might be useful".** Q3 has a strict test: would the operator copy-paste this back into a future session? If you cannot point to that recurring use-case, it's not a skill — it's a one-shot reference, which means it's either Q1, Q2, or skipped.

3. **❌ Saving a lesson without a `next_time` clause.** Lands in `pending_review` per CONSTITUTION §5.2 rule 13. If you cannot produce a concrete imperative for what to do next time, the block is not a lesson — it is information without action, which by definition does not earn a row in `lessons`.

4. **❌ Generic best practices without domain tags.** "Always test before deploying" with no tags is unfindable and unranked. Without `domain` + at least one content tag, the row pollutes broader queries and helps no one.

5. **❌ Skipping the operator approval step.** Direct writes from this skill bypass the trust contract. The operator's role is the quality gate; the LLM's role is to surface candidates with maximum information density. Writing without approval makes the LLM the editor — that's not the contract.

6. **❌ Mixing knowledge from different courses into the same entry.** An entry that says "from CAG vs RAG class AND from the agents class" is doing the work of two entries badly. Each conceptual block belongs to one source class and one set of tags.

7. **❌ Treating a multi-class PDF as one class.** If the operator pastes a course module containing 5 lectures, each lecture is its own pass through the heuristic. Run the 3 questions on each lecture's blocks, present one consolidated proposal at the end. Do not collapse 5 lectures into 5 entries — that's also rule 1 violation, just at higher granularity.

---

## 7. Cross-references

Tools and skills this one calls or references:

- **`best_practice_search(query, top_k=5)`** — duplicate detection before proposing a Q1 hit. Always run before listing the entry in the proposal.
- **`search_lessons(query, tags=[domain_tag], limit=5)`** — duplicate detection before proposing a Q2 hit. Filter by domain tag to keep the search tight.
- **`best_practice_record`** — write path for Q1 hits after operator approval.
- **`save_lesson`** — write path for Q2 hits after operator approval. Auto-approval requires title + content + tech reference + `next_time` clause + no duplicate ≥0.92 (CONSTITUTION §5.2 rule 13).
- **`register_skill`** — registration path for Q3 hits. The new `.md` must be written to disk first; `register_skill` reads `description_full` to compute the embedding.
- **`load_skill('skill_discovery')`** — the meta-skill that brought this one into context. This skill does not call it directly but follows its discipline (check `available_skills` first, never invent).

When a Q3 hit produces a new skill `.md` in a domain directory (e.g., `skills/ai-engineering/`), check whether an `INDEX.md` exists in that directory and propose adding an entry to it as part of the operator approval step. Domain INDEX files keep the directory navigable as it grows.

---

## 8. Domain tagging convention

All entries — best_practices, lessons, registered skills — must carry at least one domain tag. The tag is the primary filter for future retrieval.

### 8.1 Base tags by course

| Course / source | Base tag | Typical sub-tags |
|-----------------|----------|------------------|
| AI Engineering course | `ai-engineering` | `prompt-engineering`, `rag`, `cag`, `embeddings`, `agents`, `evals`, `responses-api`, `context-window`, `tool-use`, `function-calling` |
| Future course (slug TBD) | `<course-slug>` | derived from class topics |

The base tag is the **course slug** in kebab-case. When a new course starts, the operator names the slug — this skill does not invent base tags on the fly.

### 8.2 Sub-tag rules

- Sub-tags come from the **topic of the specific class** (not the whole course).
- Use existing sub-tags when applicable. Before introducing a new sub-tag, query:
  ```sql
  SELECT DISTINCT unnest(tags) AS tag, count(*) AS cnt
  FROM lessons WHERE %s = ANY(tags) GROUP BY 1 ORDER BY cnt DESC LIMIT 30;
  ```
  (replace `%s` with the base tag) — to surface existing sub-tags in that domain.
- Sub-tags should be lowercase, hyphenated, ≤ 30 chars.
- 2–5 sub-tags per entry is the sweet spot. More than 5 dilutes meaning.

### 8.3 Cross-cutting tags

Some tags apply across multiple courses (e.g., `prompt-engineering`, `evals`). These are fine as sub-tags but should not become base tags — the base tag identifies the source, not the topic.

---

## 9. End-to-end examples

### 9.1 Example A — Conceptual class (CAG vs RAG)

**Operator input:**

> *"Te paso la clase de hoy del curso de AI engineering — la de CAG vs RAG. Aquí está la transcripción:* [...long pasted block explaining when to use CAG, when to use RAG, the long-context degradation issue, cost considerations, and a comparison table...]"

**LLM internal pass:**

- Block 1 (definitions of CAG and RAG): pure background. Q1 NO, Q2 NO, Q3 NO → **skip**.
- Block 2 (decision criterion: when to use CAG vs RAG): Q1 YES → `best_practice_record`.
- Block 3 (gotcha: effective context window << advertised window): Q2 YES → `save_lesson` with `next_time`.
- Block 4 (gotcha: lost-in-the-middle): Q2 YES → potentially merge with #3 or save as a separate lesson; check for duplicate first.
- Block 5 (cost trade-off CAG = per-token, RAG = infrastructure): part of the rationale of #2; do not save separately.

**Duplicate searches ran:**

- `best_practice_search(query='CAG when context fits ... RAG when corpus exceeds', top_k=5)` → no match ≥ 0.90.
- `search_lessons(query='effective context window long context degradation', tags=['ai-engineering'], limit=5)` → no match ≥ 0.90.
- `search_lessons(query='lost in the middle long context recall', tags=['ai-engineering'], limit=5)` → no match ≥ 0.90.

**Proposal posted to operator** (per §5.1 format) — 1 best_practice + 2 lessons + 1 explicit skip.

**After operator says `go`:**

- ✅ best_practice `<uuid>` — "CAG when context fits the model window; RAG when corpus exceeds it"
- ✅ lesson `<uuid>` — "Effective context window != advertised window in long-context models" (status: `active`, auto-approved)
- ✅ lesson `<uuid>` — "Lost-in-the-middle: long-context recall degrades in middle of window" (status: `active`, auto-approved)
- 0 skill files (this class is conceptual, not procedural).

### 9.2 Example B — Procedural class (OpenAI Responses API)

**Operator input:**

> *"te paso la clase del responses API de OpenAI — la sintaxis completa, manejo de errores y todo eso"* [...long block with code samples for `client.responses.create`, parameter list with types and defaults, response object structure, error class hierarchy, retry pattern...]

**LLM internal pass:**

- Block 1 (full API surface — `client.responses.create` signature, every parameter, response shape, error handling): Q3 YES → new skill file. The operator will copy-paste this back into every session that touches the Responses API.
- Block 2 (decision: "always check `response.status` before parsing `response.output`"): Q1 YES → `best_practice_record`. Survives outside the class context.
- Block 3 (gotcha: the API silently truncates outputs above N tokens without raising): Q2 YES → `save_lesson` with `next_time`.

**Proposal posted:**

```markdown
## Class knowledge extraction — proposal

**Class:** OpenAI Responses API — full syntax + error handling (AI Engineering course)
**Domain tag:** `ai-engineering` (sub-tags per item)
**Duplicates checked:** yes — 1 best_practice query + 1 lesson query + skill name availability check ran

### Best practices (Q1 hits)
- [ ] **#1 — `best_practice_record`**
  - title: "Always verify `response.status` before parsing `response.output` (OpenAI Responses API)"
  - guidance: "When using `client.responses.create`, the `response` object can return with status='incomplete' or status='failed' even on a 200 HTTP response. Always check `response.status == 'completed'` before reading `response.output`. Skipping this check causes silent partial results to flow into downstream code."
  - rationale: "The Responses API decouples HTTP success from logical completion; status reflects model-side outcome, not transport."
  - domain: "process"
  - scope: "global"
  - tags: ["ai-engineering", "responses-api", "openai", "error-handling"]
  - dup-check: "no match ≥0.90 in best_practice_search('verify response.status before parsing OpenAI Responses API', top_k=5)"

### Lessons (Q2 hits)
- [ ] **#2 — `save_lesson`**
  - title: "Responses API silently truncates output beyond max_output_tokens"
  - content: "Setting max_output_tokens too low and exceeding it returns a response with status='completed' (not 'incomplete') but a truncated output field. There is no exception raised and no warning. Caller code that doesn't validate output length proceeds with partial data."
  - next_time: "Always set max_output_tokens generously and check actual output token count via response.usage.output_tokens; if equal to max_output_tokens, treat as a truncation signal and re-call with higher cap."
  - bucket: "personal"
  - tags: ["ai-engineering", "responses-api", "openai", "truncation", "tokens"]
  - dup-check: "no match ≥0.90 in search_lessons('Responses API silent truncation max_output_tokens', tags=['ai-engineering'])"

### Skills (Q3 hits)
- [ ] **#3 — new skill `.md` + `register_skill`**
  - path: `skills/ai-engineering/openai-responses-api.md`
  - slug: `openai-responses-api`
  - description_short: "OpenAI Responses API: syntax, params, error handling"
  - description_full plan: "Full reference for `client.responses.create`: signature, all parameters with types/defaults/effect, response object shape, error class hierarchy, retry pattern. Bilingual keywords."
  - applicable_buckets: ["personal", "business"]
  - proposed sections: 1. Purpose · 2. When to use · 3. API signature · 4. Parameters reference · 5. Response object · 6. Errors · 7. Retry pattern · 8. Anti-patterns · 9. References
  - trigger_keywords (post-register UPDATE): ["responses api", "client.responses", "openai api", "response.create", "structured output", "response status", "responses sdk"]

### Skipped blocks
- (none — every block produced output)
```

**After operator says `go`:**

- ✅ best_practice `<uuid>` — verify response.status...
- ✅ lesson `<uuid>` — silent truncation... (status: `active`, auto-approved)
- ✅ skill registered `<uuid>` — `skills/ai-engineering/openai-responses-api.md` written; `trigger_keywords` UPDATE applied.
- **Note to operator:** "Run `git add skills/ai-engineering/openai-responses-api.md && git commit` when ready — I do not commit from this skill per CONSTITUTION §2.4."

---

## 10. References

- `CONSTITUTION.md §2.4` — git/DB boundary (skill `.md` files live in git, catalog rows live in DB; this skill writes both, never duplicates).
- `CONSTITUTION.md §5.2 rule 13` — lesson auto-approval requires title + content + tech reference + `next_time` clause + no duplicate ≥ 0.92.
- `CONSTITUTION.md §5.5 rule 24` — duplicate detection threshold ≥ 0.95 in nightly Dream Engine; rule 14 pre-save threshold ≥ 0.92. This skill uses ≥ 0.90 as a more cautious filter for course material specifically.
- `skills/skill_discovery.md` — the discovery cycle that should have brought this skill into context.
- `src/mcp_server/tools/best_practices.py` — `best_practice_record` + `best_practice_search` implementation.
- `src/mcp_server/tools/lessons.py` — `save_lesson` + `search_lessons` implementation.
- `src/mcp_server/tools/catalog.py` — `register_skill` and `load_skill` implementation.
- `tools_catalog.trigger_keywords` — populated via direct SQL UPDATE post-register (no parameter on current `register_skill` signature).
