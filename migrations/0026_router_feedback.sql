-- Migration 0026 — router_feedback table
-- Module 0.X — Knowledge Architecture
-- Spec: specs/module-0x-knowledge-architecture/spec.md §5.4 (amended 2026-04-28)
-- Created: 2026-04-28
--
-- Explicit feedback loop signals from operator to Router. Captures
-- "missing context", "wrong bucket", "wrong complexity", etc.
--
-- request_id is `text` (not `uuid`) to match routing_logs.request_id, and
-- has NO foreign key — routing_logs is partitioned by created_at, which
-- prevents a UNIQUE(request_id) constraint. See spec §5.4 amendment for
-- full rationale. Best-effort referential integrity at MCP tool layer.

BEGIN;

CREATE TABLE IF NOT EXISTS router_feedback (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id          text,                                      -- soft reference to routing_logs.request_id (no FK)
    feedback_type       text NOT NULL
                        CHECK (feedback_type IN (
                            'missing_context',
                            'wrong_bucket',
                            'wrong_complexity',
                            'irrelevant_lessons',
                            'too_much_context',
                            'low_quality_response'
                        )),
    operator_note       text,
    proposed_correction jsonb,
    status              text NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','reviewed','applied','dismissed')),
    reviewed_by         text,
    applied_at          timestamptz,
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_router_feedback_status
    ON router_feedback(status);

CREATE INDEX IF NOT EXISTS idx_router_feedback_request
    ON router_feedback(request_id)
    WHERE request_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_router_feedback_type
    ON router_feedback(feedback_type)
    WHERE status = 'pending';

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0026',
    md5('0026_router_feedback_v2_soft_ref')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
