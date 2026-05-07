"""Dream Engine — nightly consolidation worker (Module 8 fase 1).

Cron 02:00 America/New_York via systemd timer
`pretel-os-dream-engine.timer`. Three jobs run sequentially in
independent transactions:

  1. utility_recompute() — invokes recompute_utility_scores() SQL function
  2. dedup_pass() — writes cross_pollination_queue rows for cross-bucket
     lesson pairs with cosine similarity >= 0.95 (idempotent via UNIQUE
     constraint cross_pollination_queue_pair_unique)
  3. archive_low_utility() — flips status='archived' on lessons matching
     thresholds read from operator_preferences

See specs/dream_engine/{spec,plan,tasks,phase_a_close}.md for context.
Authority: CONSTITUTION §2.6 v5.2 + §5.4 rule 20 + §5.5 rules 22+24.
"""
