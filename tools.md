# tools.md — pretel-os tool catalog

**Audience:** the operator (Alfredo) and any LLM working through pretel-os.
**Companion to:** `CONSTITUTION §11` (the canonical inventory) and `skills/skill_discovery.md` (the discovery loop).
**Last updated:** 2026-04-30.

This file describes every tool the system exposes — what it does, who reaches for it, and when. It is written in plain language, not as an API spec. For exact signatures and types, read `src/mcp_server/tools/<file>.py`. For the table of contents in numerical form, read `CONSTITUTION §11`.

The catalog ships **39 tools across 11 domains**. The same ground rule applies everywhere: when the system already has a tool that fits, the LLM uses the tool — it does not improvise, it does not ask the operator "which tool should I use", and it does not invent a tool name. If a tool seems missing, the next move is `tool_search` (search by topic) or `list_catalog` (enumerate the full inventory) — never a guess.

---

## How tools get activated

Three pathways trigger a tool. Knowing which one applies helps decide whether the LLM should call it directly, the operator should run a command, or the system will fire it on its own.

**Operator-driven.** The operator types a message into Claude.ai, runs a Telegram command (`/save`, `/review_pending`, `/cross_poll_review`, `/status`), or pastes a prompt into Claude Code. The agent reads the request, picks the right tool, and calls it.

**Agent-driven (discovery loop).** Every turn lands with a `ContextBundle` from the Router that already lists the bucket's available skills and active projects. The agent glances at that list, matches the operator's query to a tool or skill, and calls it. The cycle is described in `skills/skill_discovery.md`. The default is to use a registered tool; calling general knowledge instead is the exception, not the rule.

**System-driven (background workers + DB triggers).** Some tools fire without anyone asking. Migration 0034 attaches Postgres triggers to the five tables that drive bucket and project READMEs; any insert or update on those tables emits a notification, and the README consumer worker picks it up and regenerates the affected file. The reflection worker proposes lessons after a session closes. The Dream Engine recomputes utility scores nightly. The agent does not invoke these — they invoke themselves on the right signal.

---

## 1. Router & contexto (4 tools)

These four are the entry points. Every other tool exists to serve a specific need; these four are how the system decides what need is being served.

### `get_context`

The first call any client makes when the operator types something. It takes the message, classifies it (which bucket, which complexity tier, whether lessons are needed), assembles the relevant context layers (identity, bucket, project, skill, retrieved lessons), checks for invariant violations, and returns a single bundle the agent reads before composing its reply.

The agent does not decide what context to load — `get_context` does. The agent receives what arrives and writes the response from there.

**Activates** at the start of every turn that comes through the MCP server. Claude.ai, Claude Code, and the Telegram bot all wrap their incoming messages in a `get_context` call before the agent reasons.

**Returns** a structured bundle: classification, the five context layers, recommended tools (when complexity warrants), the available skills for the classified bucket, the active projects in that bucket, any source-priority conflicts the invariant detector flagged, and a degraded-mode flag if anything went wrong upstream.

**Use it when** any operator message arrives. There is no scenario where skipping `get_context` is correct — even a one-word "yes" turn flows through it so the Router can log the decision and the agent can see what came back.

### `tool_search`

A topic-driven search across the catalog. The agent gives it a free-text query ("vendor evaluation", "save a lesson", "cost analysis") and gets back the tools whose names or descriptions match the query, ranked by similarity and utility.

This is **search**, not enumeration. If the query is narrow, the result set is narrow. If the query is generic, it returns up to 50 matches.

**Activates** when the agent has a topic in mind but does not remember the exact tool name. "What did we use for vendor checks?" → `tool_search('vendor')`.

**Returns** matching catalog rows with name, kind (skill or tool), short description, applicable buckets, and utility score.

**Use it when** the agent knows the gist of what it needs but not the specific name. Do not use it as an inventory mechanism — for that there is `list_catalog`.

### `list_catalog`

The canonical "what tools exist" endpoint. Unlike `tool_search`, this one is not query-driven — it returns the full catalog, paginated, with a total count so the caller knows whether more pages remain. Optional filters narrow by tool kind (skill / tool / prompt) or by applicable bucket.

This tool was added explicitly to close a discoverability gap: a `tool_search` answer is "the tools that match your query"; a `list_catalog` answer is "every tool in the system". The two complement each other.

**Activates** when the agent (or the operator) wants the inventory. "What can you do?" → `list_catalog()`.

**Returns** every catalog row up to the page limit (default 200), plus the total count.

**Use it when** the agent needs an enumeration: writing a help reply, building an audit, validating that a tool is registered. Use `tool_search` instead when the question is "which tool fits this topic".

### `load_skill`

A skill is a multi-page methodology that lives as a markdown file in `skills/`. `load_skill('vett')` returns the full content of `skills/vett.md`. The agent reads the body once and follows the procedure.

**Activates** after the agent has decided which skill applies (either by glancing at `available_skills` in `get_context`'s response, or by calling `recommend_skills_for_query`). Loading a skill is the step that immediately precedes execution.

**Returns** the markdown body of the skill file plus its registry metadata.

**Use it when** the discovery loop has surfaced a clear match. Do not load skills speculatively — every load consumes context budget. One skill per turn is the rule; if two seem to apply, run the higher-utility one first and reference the second in the reply.

---

## 2. Skills and tools registration (2 tools)

These two tools mutate the catalog. Every reusable methodology or tool the system has must pass through one of them — an unregistered tool is invisible to the discovery loop and cannot be recommended.

### `register_skill`

Adds a methodology (a procedural skill that lives in `skills/<name>.md`) to the catalog. Registration includes the skill's name, short and long descriptions, applicable buckets, the path to the markdown file, and optional trigger keywords used by `recommend_skills_for_query`.

**Activates** during onboarding of a new skill. The operator (or the LLM, with operator confirmation) writes the markdown file first, then calls `register_skill` to make it discoverable.

**Returns** the new catalog row's identifier.

**Use it when** a new skill is being introduced. The most recent example: `skill_discovery` was registered in migration 0035 alongside its markdown file; the LLM now glances at the skill list every turn because the row exists.

### `register_tool`

Adds an executable tool (an MCP-callable function or external operation) to the catalog. Same fields as `register_skill` minus the file path; a `mcp_tool_name` field is added so consumers can invoke it.

**Activates** when a new MCP tool function ships in `main.py` and needs to be discoverable. Three legacy tools (`report_satisfaction`, `list_pending_cross_pollination`, `resolve_cross_pollination`) bypassed registration for months; migration 0036 caught them up so the discovery loop sees them. A new tool added today should run through `register_tool` (or a seed migration) in the same commit that wires `app.tool()` in `main.py`.

**Returns** the new catalog row's identifier.

**Use it when** introducing a new MCP tool. The two-layer rule applies: code path in `main.py` plus catalog row in `tools_catalog`, both in the same commit.

---

## 3. Lessons — capture and review (5 tools)

Lessons are the system's living memory of what worked, what broke, and what to do differently next time. The five tools cover the lifecycle from capture through review.

### `save_lesson`

Persists a new lesson with title, content, bucket, category, and the canonical "next time, do Y" clause. The lesson lands in the database with status `pending_review`. Before insert, the system runs a duplicate check against existing active lessons in the same bucket; if any matches above the 0.92 similarity threshold, the lesson is flagged as a merge candidate and the operator decides what to do. If all four auto-approval conditions hold (title + content + a concrete technology reference + a `next_time` clause), the lesson is promoted to `active` immediately.

**Activates** in three places: the operator typing `/save <text>` in Telegram, the LLM proposing a lesson after a debugging loop closes, or the reflection worker writing one after analyzing a session transcript.

**Returns** the lesson's identifier and whether it was auto-approved or queued for review.

**Use it when** a real loop closes — a problem encountered and resolved, an architectural surprise documented with its fix. Do not save speculative lessons or lessons that paraphrase the constitution; the system filters those out at review time, but writing them in the first place is wasted effort.

### `search_lessons`

Semantic search over the active lessons, with bucket and tag filters applied before the embedding similarity ranking (filter-first, per the constitution). Returns the top matches by cosine similarity.

**Activates** when the agent needs to recall whether a similar issue has been seen before. "Have we hit this Postgres timeout pattern?" → `search_lessons('postgres timeout', bucket='business')`.

**Returns** the top-K lessons with title, the "next time" clause, and similarity score.

**Use it when** the operator's current problem feels familiar, when an architectural decision is being revisited, or when an LLM is checking before proposing a new lesson (so it does not duplicate something already captured).

### `list_pending_lessons`

Returns every lesson currently in `pending_review` status, oldest first. The Telegram bot's `/review_pending` command and Claude.ai review surfaces both call this.

**Activates** during the weekly review ritual or whenever the operator wants to clear the queue. The reflection worker writes lessons faster than the operator approves them; this tool surfaces what is waiting.

**Returns** title, content, bucket, category, tags, and creation date for each pending row.

**Use it when** doing the Sunday review or when the queue feels stale. The morning brief includes a count of pending lessons older than a week as a nudge.

### `approve_lesson`

Flips a `pending_review` lesson to `active`. The transition is gated: if the lesson is in any other state (already approved, rejected, merged), the call is a no-op and reports back that nothing changed. A lesson that turns active becomes eligible for retrieval in `search_lessons` and starts contributing to utility-score recomputation.

**Activates** in the operator's review flow — Telegram inline button, Claude.ai approval action, or a direct MCP call. The reflection worker never approves lessons; that is operator-only.

**Returns** whether the flip happened (`approved: true`) or whether the row was already in a terminal state (`approved: false`).

**Use it when** reviewing a queued lesson and judging it useful. The bar is whether the lesson would help future-you or another LLM reading it cold.

### `reject_lesson`

Flips a `pending_review` lesson to `rejected` and records the rejection reason in the lesson's metadata. Like `approve_lesson`, the transition is one-way and gated on current status.

**Activates** during review when a lesson is duplicate, vague, or wrong. The reason is required because it leaves an audit trail; weeks later the operator can grep rejected lessons by reason and see what kinds of proposals are being filtered out.

**Returns** whether the flip happened.

**Use it when** the lesson does not pass review. Common rejection reasons: "duplicates lesson X", "too vague — no concrete technology reference", "not actually a lesson — paraphrases CONSTITUTION".

---

## 4. Best practices (4 tools)

Where lessons are reactive (a real loop closed), best practices are proactive (a process or convention worth following). Lessons say "we found this bug last Tuesday"; best practices say "always do X before Y". Both have their own table because they answer different questions.

### `best_practice_record`

Inserts or updates a best practice. The same call handles both: if no row with that title exists, it inserts; if one does, it updates and stashes the previous guidance into a `previous_guidance` column so a single rollback step can restore the prior version. The body is embedded so semantic search works.

**Activates** when the operator codifies a convention ("always run mypy before committing", "never push to main without a passing test suite") or when the LLM crystallizes a best practice from accumulated lessons.

**Returns** the row's identifier and whether the operation was an insert or an update.

**Use it when** a pattern emerges across several lessons that justifies a process rule. Do not record best practices that duplicate the constitution; that is what the constitution is for.

### `best_practice_search`

Semantic search over active best practices, filtered by category, applicable buckets, and active flag. Same shape as `search_lessons` but a different table.

**Activates** when the agent needs to recall a known convention. "What's our naming rule for migration files?" → `best_practice_search('naming migration')`.

**Returns** matching practices with title, guidance, category, and similarity score.

**Use it when** about to violate a convention is the worry. Run the search first; if the practice exists, follow it.

### `best_practice_deactivate`

Soft-deletes a best practice — sets its `active` flag to false but keeps the row for audit. Inactive practices do not surface in `best_practice_search` results unless the caller passes `include_inactive=true`.

**Activates** when a convention is retired or superseded.

**Returns** whether the row existed and was flipped.

**Use it when** a process changes and the old guidance would mislead. Do not delete the row — keep it deactivated so the audit trail of "we used to do X, then on date Y we stopped" stays intact.

### `best_practice_rollback`

Restores the `previous_guidance` field into the active guidance, single-step only — there is no chain. Once you roll back, the previous version is overwritten and a second rollback would do nothing useful.

**Activates** when a recent update to a best practice turns out to be wrong and you want the prior wording back without retyping it.

**Returns** whether the row had a prior version to restore and whether it was applied.

**Use it when** the most recent edit was a mistake. For deeper rollbacks (more than one version back), the audit trail in `git log` of the migration files is the source of truth, not this tool.

---

## 5. Tasks (5 tools)

Tasks are pending and in-progress work items. They are deliberately structured (no embeddings, no semantic search) — the question is always "what do I do next" or "what's blocked", and a structured query answers that better than a vector lookup.

### `task_create`

Creates a task with title, bucket, source, and optional fields (description, project, module, priority, blocking dependency, trigger phase, GitHub URL). The task starts in `open` status, or in `blocked` if a `blocked_by` reference is set. When the caller provides both bucket and project, the system resolves `project_id` from the live registry and stores the FK; if the lookup fails, the task is still created with a NULL project_id and the legacy text column captures the slug for forensics — no silent fallback to the wrong project.

**Activates** when the operator says "remind me to X" via Telegram `/idea`, when the agent identifies a follow-up during a turn, or when a phase close-out generates "next phase" tasks programmatically.

**Returns** the task's identifier and its initial status.

**Use it when** something will be done later. A task represents work that has not started; the moment it starts, flip status to `in_progress` via `task_update`. The reflection worker writes tasks that summarize "the operator should look at X" without committing to do them itself.

### `task_list`

Lists tasks with optional filters: bucket, status, module, trigger phase. Default ordering is by priority (urgent → low) then creation time; when filtering by `done` status, the order flips to `done_at DESC` so the freshly-closed work surfaces first.

**Activates** when the operator wants to know what is open, what is blocked, what is happening this phase, or what was finished recently.

**Returns** matching tasks with their core fields.

**Use it when** planning the next move. The Sunday review ritual leans heavily on `task_list(status='blocked')` to find dependencies that have resolved.

### `task_update`

Partial update — only the fields the caller passes get changed. The set of updatable columns is whitelisted at the tool level, so a renamed parameter cannot become a SQL injection vector.

**Activates** when something about a task changes: priority bumps because a deadline moved, status moves to `in_progress`, the description gets sharper after the work starts, the GitHub issue URL is filled in.

**Returns** whether the row was found and the new status.

**Use it when** modifying an existing task. Status transitions to `done` should go through `task_close` instead because that tool also stamps `done_at` and supports a completion note.

### `task_close`

Marks a task as done. Sets the status, fills in `done_at`, and optionally merges a completion note into the task's metadata. Re-closing an already-done task is a no-op — the WHERE clause filters it out.

**Activates** when the work is finished. Telegram `/done <task>` is the operator path; the agent path is direct after a phase close-out.

**Returns** whether the task existed in an open state and was closed.

**Use it when** something actually finished. Do not close speculative tasks that have not been done; a missing close is recoverable, a fake close pollutes the lessons-from-completion review.

### `task_reopen`

Reopens a closed task. Sets status back to `open`, clears `done_at`, and appends an entry to a `metadata.reopened_history` array so the audit trail accumulates: when, why, by whom. The reason is required.

**Activates** when work that was thought finished turns out not to be — a regression surfaced, a follow-up was overlooked, the spec changed.

**Returns** whether the row was found and reopened.

**Use it when** finishing was premature. The history array means a task that has been reopened three times will show its full trajectory; if a task is reopened often, that is a signal to split it into smaller tasks.

---

## 6. Decisions (3 tools)

Decisions are ADR-style records — what we decided, why, and what we considered. The `decisions` table predates the formal ADR process; migration 0028 added the columns to support typed scope (architectural / process / product / operational) and the ADR-number convention.

### `decision_record`

Inserts a decision with bucket, project, title, context, the decision itself, consequences, optional alternatives, and the typed-fields columns (scope, severity, applicable buckets, decided-by, tags, ADR number, derived-from-lessons). The body (title + context + decision) is embedded so semantic search works. Like `task_create`, the (bucket, project) pair resolves to `project_id` when the project is registered.

**Activates** when an architectural choice is made (ADR-027 etc.), when a process decision changes how the team works, or when a product decision is captured for future reference.

**Returns** the decision's identifier and the assigned ADR number when one was provided.

**Use it when** a choice with lasting consequences is being made. Operational decisions ("we'll use port 8787 for the MCP server") get scope `operational` and rarely warrant ADR numbers; architectural decisions ("we use text-embedding-3-large, not 3-small") get scope `architectural` and almost always do.

### `decision_search`

Semantic search over decisions, filtered by bucket, scope, and status. Default status filter is `active`; the caller can pass `include_superseded=true` to see the historical chain.

**Activates** when revisiting an architectural choice ("why are we on Postgres?") or when checking whether a similar decision has been made.

**Returns** matching decisions with title, scope, severity, ADR number, and similarity.

**Use it when** about to make a choice that may have already been made. The system has eight active ADRs as of 2026-04-30; a search saves rediscovering one.

### `decision_supersede`

Atomically replaces an active decision with a new one. In a single transaction: verify the old decision exists and is active, embed the new payload, insert the new decision, mark the old one as `superseded` with a pointer to the new identifier. If the old row is in any state other than `active`, the call returns an error rather than corrupting the chain.

**Activates** when an old decision is being replaced rather than just updated. The supersede chain is the audit trail: ADR-022 was superseded by ADR-024; both rows exist, both are queryable, and the chain reads forward.

**Returns** the new decision's identifier and the old one's identifier.

**Use it when** a prior decision is no longer correct. Do not edit the old decision in place — the supersede pattern preserves the reasoning that led to the change.

---

## 7. Projects (3 tools)

A project is a unit of work with a bucket, a slug, an objective, and (usually) a README. The live `projects` table is distinct from the historical `projects_indexed` table — live projects are what the operator is currently working on; indexed projects are what closed and got archived with embeddings for recall.

### `create_project`

Creates a new live project: validates the bucket, normalizes the slug, inserts a row, writes the initial README to disk under `buckets/<bucket>/projects/<slug>/README.md`, seeds an initial `project_state` row, and snapshots a `project_versions` entry. Module 7.5 added a fourth step: it calls `regenerate_bucket_readme` so the bucket README's "Active projects" section updates immediately. If the (bucket, slug) pair already exists, the call is a no-op and reports the existing identifier.

**Activates** when a new project starts. Operator-driven via Claude.ai or Claude Code: "let's start a project for the Replit VETT evaluation" → the agent calls `create_project`.

**Returns** the project's identifier, normalized slug, README path, and a flag indicating the bucket README was regenerated.

**Use it when** beginning a piece of work that will outlive the current session. Do not use it for one-off scripts or scratch experiments — a project should be something an operator could load context for next month.

### `get_project`

Looks up a project by exact (bucket, slug) match and returns the row plus the README content from disk. The slug is matched verbatim — callers that pass operator input should normalize first using the same rules as `create_project`.

**Activates** when the agent needs the full project context: someone asked about the Scout MTM work, the agent needs the README to answer well.

**Returns** the project row plus the README markdown, or `found: false` if nothing matches.

**Use it when** working inside a known project and needing its current state. The Router does this implicitly during context assembly when the classifier picks a project.

### `list_projects`

Returns active and archived projects, optionally filtered by bucket and status, ordered by creation date (newest first). Limit clamped to 200.

**Activates** when the operator wants to see what is live in a bucket, or when the agent is choosing between projects to associate work with.

**Returns** project rows with name, status, objective, and creation date.

**Use it when** building a project picker or when surveying the landscape. The bucket README's auto-generated "Active projects" section uses this same query under the hood.

---

## 8. Cross-pollination (2 tools)

Cross-pollination is when an insight from one bucket applies to another — a process you discovered for freelance work might apply to Scout work, or a tool you built for personal use might benefit a business project. The reflection worker proposes these; the operator approves or dismisses them.

### `list_pending_cross_pollination`

Returns every cross-pollination proposal currently in `pending` status, ordered by priority (highest first) then creation date. The Telegram bot's `/cross_poll_review` command and Claude.ai review surfaces both call this.

**Activates** during the Sunday review ritual or whenever the operator wants to clear the queue. The reflection worker writes proposals faster than they get reviewed; the morning brief calls out proposals waiting more than 14 days.

**Returns** each proposal with origin bucket, target bucket, the insight, the reasoning, and priority.

**Use it when** doing the weekly sweep. A proposal sitting unhandled for a month is a signal that either the reflection worker is over-eager or the operator's filter is too strict.

### `resolve_cross_pollination`

Approves or dismisses a pending proposal. Approve transitions the row to `applied`; reject transitions it to `dismissed` and records the operator-supplied reason in metadata. Like the lesson approval tools, the transition is one-way.

**Activates** during review. The Telegram inline buttons map to this call directly.

**Returns** whether the row existed in pending state and was transitioned.

**Use it when** judging whether the proposed cross-bucket insight is real. Approval means the operator commits to applying the idea (writing it as a lesson in the target bucket, updating a project, etc.); dismissal records why so the same proposal does not recur.

---

## 9. Preferences (4 tools)

Preferences are operator-controlled facts and overrides — things like "I respond in Spanish by default", "my time zone is America/New_York", "the budget for Anthropic API calls this month is $30". The Layer Loader lifts active preferences into L0 every turn so the agent sees them.

### `preference_get`

Returns a single preference value by category and key. If the preference is unset or inactive, returns null.

**Activates** when the agent needs to read a specific preference that did not surface through L0 — for example, a feature flag that only gates a particular tool.

**Returns** the value (or null) with metadata.

**Use it when** a single look-up is needed. For a survey of preferences, use `preference_list` instead.

### `preference_set`

Upserts a preference: if the (category, key, scope) triple exists, update; otherwise insert. The operation always sets `active=true`, so calling `preference_set` on a previously deactivated preference reactivates it.

**Activates** when the operator declares a preference ("from now on, default voice replies to Spanish"). The Telegram bot's `/prefer` command and Claude.ai's preference-setting flow both route here.

**Returns** the preference's identifier and whether it was an insert or an update.

**Use it when** a preference changes. The atomic upsert means the LLM can call this without first checking whether the row exists.

### `preference_unset`

Soft-deletes a preference — flips its `active` flag to false but keeps the row. Inactive preferences do not surface through `preference_get` or `preference_list` unless the caller passes `include_inactive=true`.

**Activates** when a preference no longer applies and the operator wants the system to forget it without losing the audit trail.

**Returns** whether the row existed and was deactivated.

**Use it when** retiring a preference. Use `preference_set` to update; use `preference_unset` to retire. Hard-deleting a preference is not exposed because the audit trail is more useful than the disk space saved.

### `preference_list`

Returns preferences with optional category and scope filters. Default returns active-only; pass `include_inactive=true` to see retired ones.

**Activates** when the agent or operator wants the full picture of preferences in a category. "What does the operator have set under `communication`?" → `preference_list(category='communication')`.

**Returns** matching preferences with their values and metadata.

**Use it when** auditing preferences or when the agent is about to take an action and wants to confirm there is no relevant preference.

---

## 10. Router feedback and telemetry (3 tools)

Three tools close the feedback loop on Router decisions. The Router logs every classification; these tools let the operator and the agent annotate those logs so the Router can improve.

### `router_feedback_record`

Records a feedback signal — "the bucket classification was wrong", "the project was missed", "the agent should have loaded a different skill". Includes the request identifier (when known) so the feedback associates with the exact `routing_logs` row the agent received. Status defaults to `pending`.

**Activates** when the operator notices a routing mistake or when the agent self-corrects mid-turn ("I think the classifier missed this — let me record the gap").

**Returns** the feedback row's identifier.

**Use it when** the routing decision was suboptimal. Module 4 Phase F's tuning workflow consumes these rows; without them, the Router has no signal to improve on.

### `router_feedback_review`

Transitions a feedback row out of pending — typically to `acknowledged` or `applied` after the operator decides what to do with it. Like the cross-pollination resolver, the transition is gated.

**Activates** during the Router tuning review (Phase F, recurring) or whenever the operator processes the feedback queue.

**Returns** whether the row was found and transitioned.

**Use it when** triaging the feedback queue. Acknowledged means "I see it"; applied means "I changed something based on it" (a classifier prompt update, a fallback rule, a new keyword).

### `report_satisfaction`

Updates the `user_satisfaction` field on a `routing_logs` row, scaled 1 to 5. Keyed by request identifier so the score associates with the exact bundle the agent received.

**Activates** when the operator gives a thumbs-up or thumbs-down at the end of a turn. The Telegram bot does not yet wire this; Claude.ai does. The agent does not call this on its own behalf.

**Returns** whether the row was updated.

**Use it when** the operator explicitly rates a turn. The data feeds the Phase F tuning queries: "show me low-satisfaction turns where the classifier was confident" surfaces classifier blind spots.

---

## 11. Awareness layer (4 tools, Module 7.5)

The awareness layer is the connective tissue that lets the system project its database state to the file system and surface its catalog to the LLM in time for every turn. Three of the four tools here are about projecting DB state to disk; one is the per-query skill recommender.

### `regenerate_bucket_readme`

Reads the live state of a bucket from the database (active projects, archived projects, applicable skills, recent decisions, open task count) and writes the bucket README to disk. The renderer is idempotent: running it twice in a row produces a byte-identical file (the timestamp is reused when nothing else changed). Operator notes between the markers `<!-- pretel:notes:start -->` and `<!-- pretel:notes:end -->` are preserved verbatim, so any hand-written context the operator put under "Operator notes" survives every regeneration.

**Activates** in three places: the `pretel-os-readme.service` worker dispatches it after a 30-second debounce when any of the watched tables changes, `create_project` and `archive_project` call it inline so the operator sees the README updated immediately, and an MCP client can call it directly when forcing a rebuild.

**Returns** the rendered content (preview), the path, and a flag indicating whether the file was actually rewritten or the existing content already matched.

**Use it when** a write to lessons / tasks / decisions / projects / tools_catalog should be reflected in the bucket README and the consumer worker is not running, or when an operator wants to force a refresh after editing the operator-notes block.

### `regenerate_project_readme`

Same shape as `regenerate_bucket_readme`, but for the project README at `buckets/<bucket>/projects/<slug>/README.md`. The auto-generated sections cover summary, objective + stack + applicable skills, open tasks for that project, recent decisions tied to that project (via `project_id`), and recent applicable lessons (also via `project_id`). The same operator-notes-preservation rule applies.

**Activates** the same way as the bucket variant — through the consumer worker, through `create_project`, or directly via MCP.

**Returns** the rendered content, the path, and a regenerated flag. If the project does not exist, returns `project_not_found`.

**Use it when** project-scoped state changes and the project README should reflect it. After M6 reflection_worker ships, this will fire frequently as lessons accumulate against an active project.

### `archive_project`

Marks an active project as archived: sets status, fills in `archived_at` and `archive_reason`, emits a lifecycle notification, and regenerates the bucket README so the project moves from "Active projects" to "Archived projects" immediately. The transition is one-way — re-archiving an already-archived project returns an error rather than no-oping silently. The data stays — lessons, tasks, and decisions linked to the archived project remain queryable, just out of the default "what's active" surface.

**Activates** when a project closes. Operator-driven: "we shipped Replit, archive that project" → the agent calls `archive_project`. The reflection worker does not archive on its own; closing a project is an operator decision.

**Returns** the project's identifier, the archive timestamp, and the bucket-README-regenerated flag.

**Use it when** a project finishes (shipped, dropped, paused indefinitely). The archive reason matters — a year from now, the operator looking at the archived list will appreciate "client paused engagement" or "shipped to production" over a blank field.

### `recommend_skills_for_query`

Scores every skill applicable to a bucket against an operator message and returns the top three with score at or above 1.0. The algorithm is deterministic — no LLM call. Each skill carries a list of `trigger_keywords` (in multiple languages, where appropriate); a keyword match contributes 1.0 to the score, the skill's utility score contributes another 0.3 of itself, and the threshold filters out skills with utility alone (which max at 0.3).

**Activates** when the agent is uncertain which skill applies. The discovery loop says: glance at `available_skills`, and if no clear match, call `recommend_skills_for_query` before falling back to general knowledge.

**Returns** a list of recommendations, each with the skill name, the score, and the reason (which keyword matched). Empty list when nothing crosses the threshold.

**Use it when** the operator's query does not obviously map to a skill name. Cross-language queries are a common case: "evalúa este vendor" matches `vendor` and `evaluar` in vett's keyword list, even though the skill description is in English.

---

## Closing notes

**On counting.** The catalog ships 39 tools (`app.tool` registrations in `main.py`) plus 3 registered skills (`sdd`, `vett`, `skill_discovery`), for 42 total catalog rows. The 11 functional domains in this document mirror `CONSTITUTION §11`. Buckets (`personal`, `business`, `scout`, `freelance:<client>`) are a separate axis — they describe **where** a tool applies, not **what** it does.

**On adding new tools.** Three artifacts move together: the Python function under `src/mcp_server/tools/<file>.py`, the `app.tool(<name>)` line in `main.py`, and the catalog row (either via a seed migration or via `register_tool`). A tool that ships only one of the three is a partial registration — the system will not behave as if the tool exists.

**On rediscovering.** When in doubt, `list_catalog()` is the canonical inventory; `tool_search('<topic>')` is the topic search. `available_skills` and `active_projects` arrive on every `get_context` response so the per-turn glance is free. The agent does not have to remember everything — it has to know how to look.
