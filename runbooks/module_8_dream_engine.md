# Module 8 — Dream Engine — operations runbook

**Status:** Active (worker deployed 2026-05-07, observation gate in progress)
**Service:** `pretel-os-dream-engine.service` (Type=oneshot)
**Timer:** `pretel-os-dream-engine.timer` (OnCalendar `*-*-* 02:00 America/New_York`, `Persistent=true`)
**Source code:** `src/dream_engine/`
**Authority:** `CONSTITUTION §2.6 v5.2` (worker charter), `§5.3 rule 18` (utility formula), `§5.4 rule 20` (queue writer), `§5.5 rules 22+24` (archive + dedup), `decisions` table ADR-029.
**Owner:** Alfredo Pretel Vargas

This runbook is the operator's reference for the Dream Engine in steady state. For module rationale and design, see `specs/dream_engine/{spec,plan}.md`. For the implementation history, see the four phase-close documents and the `decisions` row chain (M6 cancellation `9e8bacad` → ADR-029 amendment `a39bc9b9`).

---

## 1. What it does

Three jobs run sequentially nightly in independent transactions (failure of one does not roll back the others):

| # | Job | What | Cost |
|---|-----|------|------|
| 1 | `utility_recompute` | Calls SQL function `recompute_utility_scores()` (migration 0019). Updates `tools_catalog.utility_score` and `lessons.utility_score` per the §5.3 rule 18 formula. | $0, ~10 ms |
| 2 | `dedup_pass` | Finds cross-bucket lesson pairs with cosine similarity ≥ 0.95, inserts into `cross_pollination_queue` with `proposed_by='dream_engine_dedup'`. Idempotent via UNIQUE constraint on `(origin_lesson, target_lesson_id, proposed_by)` — re-running a night for the same pair is a no-op. | $0, ~5–50 ms |
| 3 | `archive_low_utility` | Flips `status='active' → 'archived'` on lessons matching all 3 predicates: `usage_count = 0`, `utility_score < archive.utility_threshold`, `created_at < now() - archive.usage_window_days * interval '1 day'`. Thresholds read from `operator_preferences`; worker hard-fails on missing key. | $0, ~few ms |

The worker is fire-and-exit (`Type=oneshot`). One row in `dream_engine_runs` per invocation captures start_at, completed_at, status, jobs_run JSONB, failures JSONB, worker_pid.

**No LLM calls. No external API calls. Embeddings are pre-existing.**

---

## 2. Daily verification (Phase D + ongoing)

After 02:00 ET each night:

### Quick check via DB

```sql
SELECT id, started_at::time AS started, completed_at::time AS finished,
       round(EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000) AS wall_ms,
       status,
       jobs_run::jsonb #>> '{utility_recompute,rows_affected}' AS utility_rows,
       jobs_run::jsonb #>> '{dedup_pass,rows_affected}'        AS dedup_rows,
       jobs_run::jsonb #>> '{archive_low_utility,rows_affected}' AS archive_rows
FROM dream_engine_runs
WHERE started_at > now() - interval '24 hours'
ORDER BY started_at DESC;
```

Expected: 1 row, `status='success'`, all 3 *_rows present, `wall_ms` < 200 at current corpus.

### Quick check via journalctl

```bash
journalctl --user -u pretel-os-dream-engine.service \
  --since "today 01:00" --until "today 03:00" --no-pager
```

You should see the lifecycle log lines:
```
Dream Engine starting (dry_run=False, pid=NNNN)
Dream Engine run_id=...
Archive thresholds: window_days=500, utility_threshold=0.500, lookback_days=90
  utility_recompute      OK  rows=N    duration=Xms
  dedup_pass             OK  rows=N    duration=Xms
  archive_low_utility    OK  rows=N    duration=Xms
Dream Engine finished status=success
```

If the section above is missing for a given night, see §5 below.

---

## 3. Manual trigger (out-of-cycle)

```bash
systemctl --user start pretel-os-dream-engine.service
```

The service runs once and exits. Check the new row in `dream_engine_runs` afterwards.

### Dry-run (no writes)

For testing changes against prod data without committing:

```bash
PYTHONPATH=/home/pretel/dev/pretel-os/src \
  /home/pretel/.venvs/pretel-os/bin/python -m dream_engine.worker --dry-run
```

Telemetry rows are still inserted (the worker commits `_start_run` and `_finish_run` so observability survives). The 3 job transactions ROLLBACK so no data mutations persist.

---

## 4. Tuning archive thresholds

Three keys live in `operator_preferences` with `category='workflow'`, `scope='global'`, `source='migration'` (seeded by 0039).

| Key | Default | Effect of raising | Effect of lowering |
|-----|---------|-------------------|--------------------|
| `archive.usage_window_days` | **500** | More lenient — lessons survive longer before becoming archive-eligible | More aggressive — older lessons archived sooner |
| `archive.utility_threshold` | **0.5** | More aggressive — more lessons fall below the floor | More lenient |
| `archive.utility_lookback_days` | **90** | Wider lookback (currently informational; utility is recomputed nightly per §5.3 rule 18 — the lookback shows up indirectly through the recency_weight component) | Narrower lookback |

### Tuning via MCP (preferred)

```
preference_set("workflow", "archive.usage_window_days", "700")
```

### Tuning via SQL (fallback)

```sql
UPDATE operator_preferences
SET    value = '700', updated_at = now()
WHERE  category = 'workflow'
  AND  key      = 'archive.usage_window_days'
  AND  scope    = 'global';
```

Next nightly run uses the new value. **No constitutional amendment needed** — that's the whole point of parametrizing per ADR-029.

If you `preference_unset` (sets `active=false`), the worker hard-fails on next run with a clear error message naming the missing key.

---

## 5. Recovering from a missed run

`Persistent=true` on the timer means systemd auto-runs the missed invocation on next boot. No manual action needed in the typical case.

### When auto-recovery kicks in

- Laptop suspended at 02:00 → systemd fires the missed run at next wake.
- Server rebooted between 01:00 and 02:00 → fires soon after boot.
- Service crashed at 02:00 → next fire is the following 02:00 (no auto-retry within the same calendar slot).

### When you want to force a run

```bash
systemctl --user start pretel-os-dream-engine.service
```

The worker is idempotent — running multiple times the same day produces the same outcome:
- `utility_recompute` overwrites scores (target state, not delta).
- `dedup_pass` second run inserts 0 rows via UNIQUE + ON CONFLICT DO NOTHING.
- `archive_low_utility` second run finds 0 candidates because the first run already flipped them to `status='archived'` (predicate filters `status='active'`).

### Verifying the timer is healthy

```bash
systemctl --user list-timers --all | grep dream-engine
```

Expected output:
```
NEXT                       LEFT  ...  UNIT                              ACTIVATES
Fri 2026-MM-DD 02:00:NN ...  ...  ...  pretel-os-dream-engine.timer      pretel-os-dream-engine.service
```

If `NEXT` is missing or far in the past, the timer is broken — run:

```bash
systemctl --user daemon-reload
systemctl --user restart pretel-os-dream-engine.timer
systemctl --user list-timers | grep dream-engine
```

---

## 6. Common failure modes

### `dream_engine_runs.status='failed'` for one night

All three jobs raised. Inspect `failures` JSONB:

```sql
SELECT id, failures FROM dream_engine_runs
WHERE status='failed'
ORDER BY started_at DESC LIMIT 1;
```

`failures` is an array of `{job, error_class, error_message, traceback}`. Most likely root causes:
- **DB unreachable mid-run** — check Postgres status. The worker exits non-zero; systemd logs a failed unit.
- **Schema drift** — a column referenced by the worker no longer exists. Check recent migrations.
- **Permissions** — `pretel_os` role lost a privilege. Check `ALTER TABLE … OWNER` history.

### `dream_engine_runs.status='partial'`

≥1 job raised but ≥1 succeeded. The other jobs persisted normally — partial is operationally fine. If a specific job repeatedly fails:

```sql
SELECT started_at::date,
       failures::jsonb -> 0 ->> 'job'           AS failing_job,
       failures::jsonb -> 0 ->> 'error_class'   AS error_class,
       failures::jsonb -> 0 ->> 'error_message' AS msg
FROM dream_engine_runs
WHERE status='partial'
ORDER BY started_at DESC
LIMIT 14;
```

Patterns suggest the root cause: same `dedup_pass` / `OperationalError` for multiple nights → likely vector index issue or pgvector version mismatch.

### "Archive thresholds missing from operator_preferences" error

One of the 3 keys was deactivated or deleted. Re-seed:

```sql
INSERT INTO operator_preferences (category, key, value, scope, source)
VALUES
    ('workflow', 'archive.usage_window_days',     '500', 'global', 'migration'),
    ('workflow', 'archive.utility_threshold',     '0.5', 'global', 'migration'),
    ('workflow', 'archive.utility_lookback_days', '90',  'global', 'migration')
ON CONFLICT (category, key, scope) DO UPDATE SET active = true, updated_at = now();
```

This is what migration 0039 does — same statement, idempotent.

### Dedup pass producing too many proposals

Symptom: `cross_pollination_queue` grows by tens of rows per night.

Cause: similarity threshold too lenient or corpus has many genuine near-duplicates.

Fix:
- **Code change:** edit `DEDUP_DISTANCE_THRESHOLD` in `src/dream_engine/queries.py` from `0.05` (≥0.95 sim) to `0.03` (≥0.97 sim). Redeploy via systemd reload (no restart needed for one-shot services).
- **Data change:** triage the queue via Telegram `/cross_poll_review` to get the count down; the underlying threshold can stay.

CONSTITUTION §5.5 rule 24 says ≥0.95 as the floor — running tighter is allowed, looser is a constitutional change.

### Worker timing out / running long

Plan §1 budget says < 60 s at current corpus, < 5 min at 1000 lessons. If wall_ms > 5000 at current scale, something is wrong — likely a missing pgvector index after a major schema change. Diagnostics:

```sql
EXPLAIN ANALYZE
SELECT a.id, b.id, a.embedding <=> b.embedding AS dist
FROM lessons a JOIN lessons b
  ON a.id < b.id AND a.bucket <> b.bucket
  AND a.status='active' AND b.status='active'
  AND a.embedding IS NOT NULL AND b.embedding IS NOT NULL
WHERE (a.embedding <=> b.embedding) <= 0.05;
```

Expected: sequential scan over ~70 rows is fast. If row count grows past ~5000, ADR-024 HNSW index becomes the answer.

---

## 7. Audit queries (3)

### 7.1 — Last 14 nights health

```sql
SELECT date_trunc('day', started_at AT TIME ZONE 'America/New_York')::date AS night,
       count(*)                                AS runs,
       count(*) FILTER (WHERE status='success')AS ok,
       count(*) FILTER (WHERE status='partial')AS partial,
       count(*) FILTER (WHERE status='failed') AS failed,
       round(avg(EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000)) AS avg_wall_ms
FROM dream_engine_runs
WHERE started_at > now() - interval '14 days'
GROUP BY 1
ORDER BY 1 DESC;
```

### 7.2 — Cross-pollination queue accumulation by source

```sql
SELECT proposed_by, status,
       count(*) AS rows,
       min(created_at)::date AS oldest,
       max(created_at)::date AS newest
FROM cross_pollination_queue
GROUP BY proposed_by, status
ORDER BY proposed_by, status;
```

Helps spot if the queue is growing unbounded (operator behind on triage) or if a particular source is over-producing.

### 7.3 — Archive activity over the past 90 days

```sql
SELECT date_trunc('week', updated_at AT TIME ZONE 'America/New_York')::date AS week,
       count(*) AS lessons_archived
FROM lessons
WHERE status='archived'
  AND updated_at > now() - interval '90 days'
GROUP BY 1
ORDER BY 1 DESC;
```

Helps spot threshold mis-tuning: zero archives over many weeks → thresholds too lenient; many archives in one week → thresholds tightened too much or batch-cleanup happened.

---

## 8. Known constitutional drift

`CONSTITUTION §5.5 rule 22 v5.2` predicate (5) "Not referenced by any active project in `project_state`" is **NOT** implemented in fase 1 — `project_state` has no typed lesson-reference column, so the worker cannot honor this safety check.

Risk is microscopic: the other predicates (zero usage + low utility + > 500 days) already guarantee an unused lesson, and a project actively referencing a lesson would have raised its `usage_count` through normal retrieval.

Tracked as `M8.fu4` in `specs/dream_engine/tasks.md`. If observation reveals incidents where the worker archived something the operator wanted alive, that's the trigger to implement the predicate.

---

## 9. Cross-references

| Doc | Purpose |
|-----|---------|
| `specs/dream_engine/spec.md` | What we're building (success criteria, open Q's, risks) |
| `specs/dream_engine/plan.md` | How we built it (phases, architecture, tuning playbook) |
| `specs/dream_engine/tasks.md` | Atomic task tree |
| `specs/dream_engine/phase_a_close.md` | Q1/Q2/Q3/Q7 schema decisions |
| `specs/dream_engine/phase_b_close.md` | Q4/Q5/Q6 worker decisions + drift note |
| `specs/dream_engine/phase_c_close.md` | systemd installation + first live run record |
| ADR-029 (`decisions` row `a39bc9b9`) | Constitutional amendment v5.2 chartering this scope |
| M6 cancellation (`decisions` row `9e8bacad`) | Why reflection_worker is not the queue writer |
| Migration 0019 | `recompute_utility_scores()` SQL function |
| Migration 0010 | `cross_pollination_queue` table |
| Migration 0037 | Embedding invalidation triggers (UPDATE-side coverage) |
| Migration 0038 | Embedding invalidation app-override fix |
| Migration 0039 | Dream Engine schema (UNIQUE constraint, dream_engine_runs, seed prefs) |
