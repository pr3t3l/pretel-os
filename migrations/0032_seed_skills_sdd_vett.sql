-- 0032_seed_skills_sdd_vett.sql
-- Module 7 Phase A — register sdd + vett skills in tools_catalog.
-- Source: skills/sdd.md, skills/vett.md (this commit).
--
-- MCP register_skill was unavailable at registration time (session error);
-- this migration is the SQL fallback. Idempotent on conflict.

INSERT INTO tools_catalog (
    name,
    kind,
    description_short,
    description_full,
    applicable_buckets,
    skill_file_path
) VALUES
(
    'sdd',
    'skill',
    'Spec-Driven Development process',
    'SDD — Spec-Driven Development. Discipline for planning, building, and shipping software-shaped work (apps, workflows, pipelines, agents) without rebuilding the same thing 10+ times. Core principle: specify before you build, one task at a time, stop if it breaks twice. Six-step lifecycle (SPEC → PLAN → TASKS → BUILD → VALIDATE → CLOSE) with explicit gates. Module specs cover purpose, user stories, business rules, data model, technical decisions, UI, edge cases, cost/observability, open questions, pre-flight checklist, testing/DoD. Workflow specs cover input/output contracts, phases & agents, model selection, failure & recovery, cost tracking, operational playbook. Eight working rules, lessons-learned trigger policy, anti-pattern catalog. Generic across personal, business, scout buckets.',
    ARRAY['personal','business','scout'],
    'skills/sdd.md'
),
(
    'vett',
    'skill',
    'Vendor Evaluation & Technology Triage framework',
    'VETT — Vendor Evaluation & Technology Triage. 233-question, 7-dimension, 7-module framework for evaluating whether a vendor tool/platform should be adopted by an organization. Six-phase lifecycle: Intake → Tier 1 → Tier 2 → Tier 3 → Communication → Lessons Learned. Tier 1 universal core: D0 Tool Profile (narrative, three-part overlap analysis); D1 Security & Compliance (25%); D2 Data Ownership & Residency (20%); D3 Cost & TCO (15%); D4 Integration with Existing Stack (20%); D5 Vendor Stability & Exit Risk (20%); D6 Data Classification (informs D2); D7 Operational Impact (informs D1). Tier 2 specialist modules A–G activated by tool type. 0–3 scoring scale with N/A; Relevance Gate excludes category errors. Final score = (Tier 1 × 0.70) + (Tier 2 × 0.30). Recommendation bands 80+/60–79/40–59/<40. Twelve immutable rules. Mandatory Strategic Opportunity Assessment §3.5. 10-slide leadership presentation per Pyramid Principle and SCQA. Generic and organization-agnostic; bucket overlays supply tech stack, governance team, compliance, and data taxonomy.',
    ARRAY['business','scout'],
    'skills/vett.md'
)
ON CONFLICT (name) DO UPDATE SET
    kind                = EXCLUDED.kind,
    description_short   = EXCLUDED.description_short,
    description_full    = EXCLUDED.description_full,
    applicable_buckets  = EXCLUDED.applicable_buckets,
    skill_file_path     = EXCLUDED.skill_file_path,
    updated_at          = now();
