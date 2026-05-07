# Module 8 Dream Engine — Phase C close

**Status:** Closed 2026-05-07 (go-live authorized by operator)
**Companion to:** `specs/dream_engine/{spec,plan,tasks,phase_a_close,phase_b_close}.md`

Phase C delivered the systemd timer + first live production run. Brief because there are no open Q's specific to this phase — the work was operational installation.

---

## Files added

```
infra/systemd/pretel-os-dream-engine.service   (Type=oneshot worker)
infra/systemd/pretel-os-dream-engine.timer     (OnCalendar 02:00 ET, Persistent=true)
```

Both copied to `~/.config/systemd/user/` (user-level, not system-level).

---

## Deployment timeline

1. **Production dry-run** at `2026-05-07 13:13:58 EDT` via direct python invocation.
   - run_id `6ae68beb-2216-437a-8709-5cf648b141cf`
   - 13ms wall, status=success
   - 112 rows touched by utility_recompute (70 active lessons + 42 catalog)
   - 0 dedup proposals (closest cross-bucket pair: similarity 0.467, well below 0.95 threshold)
   - 0 archives (no lessons match the 500-day predicates today)

2. **Operator dry-run review** — authorized go-live based on the above zero-mutation outcome at current corpus state.

3. **systemd installation** at `2026-05-07 13:23 EDT`:
   - `cp infra/systemd/pretel-os-dream-engine.* ~/.config/systemd/user/`
   - `systemctl --user daemon-reload`
   - `systemctl --user enable --now pretel-os-dream-engine.timer`
   - Verification: `systemctl --user list-timers | grep dream-engine` shows `Fri 2026-05-08 02:00:57 EDT`

4. **First live run** at `2026-05-07 13:25:12 EDT` via `systemctl --user start pretel-os-dream-engine.service`:
   - run_id `0f552c95-b834-4040-9c8a-037c1ef30ede`
   - 22ms wall, status=success
   - exit code 0/SUCCESS
   - jobs_run JSONB shows all 3 jobs with proper duration + rows_affected fields
   - failures = []

---

## Success criteria status against production

| SC | Status | Evidence (verified post-live-run) |
|----|--------|-----------------------------------|
| SC1 dream_engine_runs telemetry | ✅ | row `0f552c95`, jobs_run + failures + worker_pid all populated |
| SC2 utility_recompute updates score | ✅ | 112 rows touched; tools without usage_count score 0.0 per formula (`ln(1+0) + recency(NULL)=0 + 0 + 0 = 0` — mathematically correct) |
| SC3 dedup writes pair / idempotent | ✅ contract verified | 0 rows today (corpus has no near-duplicates), but `test_dedup_idempotent_second_run_inserts_zero` slow test proves the UNIQUE constraint behavior |
| SC4 archive flips low-utility | ✅ contract verified | 0 rows today, but `test_archive_flips_old_low_utility_lesson` slow test proves predicate behavior |
| SC5 partial status on fault | ✅ via unit test | `_finish_run` computes 'partial' when ≥1 job failed and ≥1 succeeded |
| SC6 preference_set tunes thresholds | ✅ | `test_archive_thresholds_loaded_from_seed` reads via the same code path; values are tunable without code change |
| SC7 7-day production observation | open | Phase D — 7 nightly runs starting 2026-05-08 02:00 ET |

SC3 and SC4 contract-verification is the strongest possible against current data (where the predicates do not naturally fire). When they do fire in production, the slow tests' assertions also hold by construction.

---

## What's running now in production

- `pretel-os-dream-engine.timer` enabled at user level. Next fire: **Fri 2026-05-08 02:00:57 EDT** (with RandomizedDelaySec=60 jitter applied).
- `Persistent=true` means missed runs (laptop suspended at 02:00) recover on next boot.
- `pretel-os-dream-engine.service` is fired by the timer; it runs once and exits.
- `dream_engine_runs` table accumulates one row per nightly invocation.

---

## Phase C exit gate

- [x] Both unit files in repo (`infra/systemd/pretel-os-dream-engine.{service,timer}`)
- [x] Installed at user level
- [x] Timer enabled and visible in `list-timers`
- [x] Production dry-run reviewed and approved
- [x] First live run completed with status=success
- [x] SC1-SC4 verified against post-run state
- [x] Phase C committed (this commit)

**Next: Phase D — 7-day production observation gate (operator-driven, ~1 verification per day).**
