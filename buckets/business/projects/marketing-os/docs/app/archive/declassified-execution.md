# Declassified Phase 0 Reset

Date: 2026-06-01

This file records the reset requested for Declassified. The project now starts from the raw idea only, not from website facts, pricing, page copy, or previous offer conclusions.

## Starting Idea

```text
I want to sell detective mystery cases so people can spend quality time with family or friends.
```

## Rules

- Website analysis is optional and only enters evidence if the operator explicitly asks for it.
- Price, case contents, page claims, and Phase 1 offer angles are not initial truth.
- Phase 0 must be built through a guided agent conversation.
- Sandi asks one question at a time and shows a visible Project Foundation Draft.
- No Phase 1 work runs until `Phase 0 Brief` is approved.

## Clean Seed

The clean project state should contain:

- `phase_0_conversation`: seeded with the raw idea and Sandi's first clarifying question.
- `project_foundation`: draft status, low confidence, operator evidence only.

Current generated artifacts, decisions, and lessons from the prior execution are superseded.

## n8n

The `Sandi - Phase 0 Draft Assistant` workflow supports drafting only. It returns a next question or draft support to Sandi. It does not write official artifacts.
