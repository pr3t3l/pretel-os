-- 0023_seed_control_registry.sql
-- Source: DATA_MODEL.md §5.6 (seed rows)

INSERT INTO control_registry (control_name, description, cadence_days, owner, evidence_required) VALUES
    ('scout_audit',             'Review Scout bucket for leaked employer data',                                  90, 'operator', 'operator attestation + git log of any corrections'),
    ('restore_drill',           'Restore most recent backup to scratch DB, validate pg_restore',                 90, 'operator', 'log of successful restore'),
    ('key_rotation_anthropic',  'Rotate ANTHROPIC_API_KEY',                                                      180, 'operator', 'env file diff + smoke test log'),
    ('key_rotation_openai',     'Rotate OPENAI_API_KEY',                                                         180, 'operator', 'env file diff + smoke test log'),
    ('pricing_verification',    'Re-verify Anthropic + OpenAI pricing pages vs INTEGRATIONS §2.6 and §3.6',      90, 'operator', 'screenshot or updated doc'),
    ('uptime_review',           'Review 30-day uptime from UptimeRobot, reconcile with SLO target',              30, 'operator', 'dashboard screenshot')
ON CONFLICT (control_name) DO NOTHING;
