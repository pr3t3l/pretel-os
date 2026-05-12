# Plan — AI Engineer Course knowledge capture

## Phases

### Phase 1 — Scaffold (this session)
- Register project (done via `create_project`).
- Trinity files: `spec.md`, `plan.md`, `tasks.md`.
- Create `classes.md` index with header + one example row template.
- Create `skill-drafts/.gitkeep` so the directory exists.

### Phase 2 — First class capture
- Take the first real class (whichever is current / next in the course).
- Use `save_lesson` for 2–5 atomic insights with the taxonomy from `spec.md`.
- Append the row to `classes.md`.
- Verify lessons appear in `search_lessons` with the expected tags.

### Phase 3 — Iterate
- Repeat Phase 2 per class.
- No tooling changes until ≥5 classes are in (measure friction before optimizing).

### Phase 4 — First skill promotion (trigger-based, not date-based)
- When a domain tag accumulates ≥3 lessons + cross-project relevance + real application: draft skill in `skill-drafts/`, then promote via `register_skill` and move to `skills/<name>.md`.

### Phase 5 — Review cadence (optional, after 10+ classes)
- Monthly: scan `classes.md` + `search_lessons` for clusters; consider promotions; archive lessons that turned out wrong (`reject_lesson` flow).

## Open questions

- **Class source format?** Is it video, live cohort, async? Affects whether we link to timestamps. → Resolve when first class lands.
- **Course name + provider?** Affects whether we add a `course:<name>` tag for multi-course futures. → Operator to confirm.
- **Should we add a `class-NN` field to lessons schema, or keep it in tags?** Current call: tags-only, no schema change. Revisit if querying gets awkward.

## Risks

- **Discipline drift.** If operator skips the lesson-write step, the project degrades to a wiki. Mitigation: keep per-class cost low (2–5 lessons, ~10 min).
- **Over-tagging early.** Premature taxonomy invents domains that never recur. Mitigation: use the fixed 9-domain list in spec; only expand after pattern proves.
- **Skill promotion too eager.** Promoting a 1-class concept to a skill bloats L3 search. Mitigation: 3-lesson + cross-project + applied-once gate.
