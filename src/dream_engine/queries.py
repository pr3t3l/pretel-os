"""SQL strings used by the Dream Engine worker.

Kept separate from worker.py so the queries are testable + readable in
isolation. Each constant is prefixed with the job name (`UTILITY_*`,
`DEDUP_*`, `ARCHIVE_*`) and ordered by execution within the job.

Conventions used here:
  - psycopg %s placeholders, never f-string interpolation of values.
  - cosine distance via pgvector `<=>` operator (similarity = 1 - distance).
  - cross_pollination_queue inserts use the UNIQUE constraint
    `cross_pollination_queue_pair_unique` (origin_lesson, target_lesson_id,
    proposed_by) for idempotency via ON CONFLICT DO NOTHING.

Phase B Q4/Q5/Q6 resolutions (see plan.md §2 Phase B):
  Q4: top-K = 5 per (origin, target_bucket). Tunable via constant below.
  Q5: cosine via `<=>`. Threshold 0.05 distance == 0.95 similarity.
  Q6: archival UPDATE fires existing readme_dirty triggers (migration
      0034) so the bucket README regenerates without explicit NOTIFY.
"""
from __future__ import annotations

# ---------------------------------------------------------------------
# Job 1 — utility_recompute
# ---------------------------------------------------------------------

UTILITY_RECOMPUTE = "SELECT recompute_utility_scores();"

UTILITY_AFFECTED_COUNTS = """
SELECT
    (SELECT count(*) FROM tools_catalog WHERE deprecated = false) AS tools_count,
    (SELECT count(*) FROM lessons WHERE status = 'active')        AS lessons_count
"""


# ---------------------------------------------------------------------
# Job 2 — dedup_pass
# ---------------------------------------------------------------------
#
# For each pair of active lessons in DIFFERENT buckets where cosine
# distance <= 0.05 (similarity >= 0.95), insert a cross_pollination_queue
# row with proposed_by='dream_engine_dedup'.
#
# `a.id < b.id` enforces canonical pair ordering (avoids both (A,B) and
# (B,A)). PARTITION BY (a.id, b.bucket) gives top-K candidates per source
# lesson per target bucket — limits queue noise when one lesson has many
# neighbors in the same bucket.
#
# ON CONFLICT (cross_pollination_queue_pair_unique) DO NOTHING means a
# second nightly run for the same pair is a no-op.

DEDUP_TOP_K = 5
DEDUP_DISTANCE_THRESHOLD = 0.05  # cosine: 1 - similarity (so >= 0.95 sim)

DEDUP_INSERT_CANDIDATES = """
WITH candidates AS (
    SELECT
        a.id          AS origin_lesson,
        a.bucket      AS origin_bucket,
        a.project     AS origin_project,
        a.title       AS origin_title,
        b.id          AS target_lesson_id,
        b.bucket      AS target_bucket,
        b.title       AS target_title,
        (a.embedding <=> b.embedding) AS distance,
        ROW_NUMBER() OVER (
            PARTITION BY a.id, b.bucket
            ORDER BY a.embedding <=> b.embedding ASC
        ) AS rank_in_target_bucket
    FROM   lessons a
    JOIN   lessons b
      ON   a.id < b.id
      AND  a.bucket <> b.bucket
      AND  a.status = 'active'
      AND  b.status = 'active'
      AND  a.embedding IS NOT NULL
      AND  b.embedding IS NOT NULL
      AND  (a.embedding <=> b.embedding) <= %(distance_threshold)s
)
INSERT INTO cross_pollination_queue (
    origin_bucket, origin_project, origin_lesson,
    target_bucket, target_lesson_id,
    idea, reasoning,
    proposed_by, confidence_score
)
SELECT
    origin_bucket,
    origin_project,
    origin_lesson,
    target_bucket,
    target_lesson_id,
    'Possible merge candidate: cross-bucket lessons appear semantically equivalent',
    format(
        'Cosine similarity %%s between origin lesson "%%s" (%%s) and target lesson "%%s" (%%s). Detected by Dream Engine nightly dedup pass; review for merge or dismiss.',
        round((1 - distance)::numeric, 4),
        origin_title, origin_bucket,
        target_title, target_bucket
    ),
    'dream_engine_dedup',
    (1 - distance)::real
FROM candidates
WHERE rank_in_target_bucket <= %(top_k)s
ON CONFLICT ON CONSTRAINT cross_pollination_queue_pair_unique DO NOTHING
RETURNING id;
"""


# ---------------------------------------------------------------------
# Job 3 — archive_low_utility
# ---------------------------------------------------------------------
#
# Predicates per CONSTITUTION §5.5 rule 22 v5.2:
#   1. status = 'active'
#   2. usage_count = 0
#   3. utility_score < %(utility_threshold)s
#   4. created_at < now() - %(window_days)s * interval '1 day'
#   5. Not referenced by any active project_state row
#      (Implementation gap fase 1: predicate 5 is a placeholder. The
#       project_state schema does not have a typed FK to lessons.id.
#       Documented in phase_b_close.md as a known constitutional-rule
#       drift — risk is microscopic at 500-day window + zero usage +
#       utility < 0.5; revisit when project_state acquires lesson refs
#       or when archive count exceeds expectations.)
#
# `RETURNING id` lets the worker count affected rows for the
# dream_engine_runs.jobs_run JSONB telemetry.
#
# UPDATE fires the existing trg_lessons_readme_dirty_* triggers
# (migration 0034) so the bucket README regenerates and the now-archived
# lessons disappear from default views automatically.

ARCHIVE_LOW_UTILITY = """
UPDATE lessons
SET    status = 'archived',
       updated_at = now()
WHERE  status = 'active'
  AND  usage_count = 0
  AND  utility_score < %(utility_threshold)s
  AND  created_at < now() - %(window_days)s * interval '1 day'
RETURNING id;
"""


# ---------------------------------------------------------------------
# Telemetry — dream_engine_runs lifecycle
# ---------------------------------------------------------------------

INSERT_RUN_START = """
INSERT INTO dream_engine_runs (status, worker_pid)
VALUES ('running', %(worker_pid)s)
RETURNING id;
"""

UPDATE_RUN_FINISH = """
UPDATE dream_engine_runs
SET    completed_at = now(),
       status       = %(status)s,
       jobs_run     = %(jobs_run)s::jsonb,
       failures     = %(failures)s::jsonb
WHERE  id = %(run_id)s;
"""
