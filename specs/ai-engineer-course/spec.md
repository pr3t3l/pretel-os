# Spec — AI Engineer Course knowledge capture

## Problem

Alfredo is taking an AI Engineer course. Raw notes per class become a dead wiki: searchable in theory, never re-read in practice, and invisible to the Router when working on future AI projects (RAG, evals, agents, fine-tuning). The knowledge needs to be **retrievable by concept** (not by class number) and **auto-injected** when relevant work happens.

## Goals

1. Every class produces 2–5 atomic **lessons** in the DB, tagged by source class and by AI domain (rag, evals, agents, fine-tuning, prompting, infra, etc.).
2. A **class index** in git (`specs/ai-engineer-course/classes.md`) gives a one-row pointer per class: number, title, date, key concepts, generated lesson IDs, source link.
3. When a concept stabilizes and recurs (≥3 lessons converging), it gets **promoted to a skill** under `skills/<topic>.md` (L3, loadable on demand).
4. Router lesson recall (L4) surfaces these lessons automatically on `complexity ≥ MEDIUM` turns in personal/business buckets when the topic matches.

## Non-goals

- Transcribing entire classes. Source video / slides / official notes stay external; we link to them.
- Building a course "completion tracker" or homework system.
- Generic AI/ML reference material that already exists elsewhere — we capture **the operator's distilled takeaways**, not textbook content.

## Knowledge model

Three layers, ordered by abstraction:

| Layer | Where | When | Example |
|---|---|---|---|
| **Class entry** | `specs/ai-engineer-course/classes.md` (git) | After every class | `#07 \| RAG eval metrics \| 2026-05-15 \| recall@k, MRR, faithfulness \| lessons: [uuid1, uuid2]` |
| **Lesson** | `lessons` table (DB) | 2–5 per class | `Use Ragas faithfulness score, not BLEU, for retrieval QA evals. next_time: ...` |
| **Skill** | `skills/<name>.md` (git) | When ≥3 lessons converge on a stable topic | `skills/rag_evaluation.md` |

### Lesson taxonomy

Every lesson from this project carries:
- `bucket=personal`
- `project=ai-engineer-course`
- tags: `["ai-engineer-course", "class-NN", "<domain>"]` where `<domain>` ∈ `{rag, evals, agents, fine-tuning, prompting, embeddings, infra, ethics, product}`
- `next_time` clause referencing the technique, not the class number ("when building a retrieval QA system, use X" — not "from class 7, use X")

### Promotion to skill

A lesson cluster qualifies for skill promotion when:
- ≥3 distinct lessons share a domain tag, AND
- the topic has cross-project applicability (would load in 2+ future project contexts), AND
- the operator has applied it at least once in real work (not just theory).

Drafts live in `specs/ai-engineer-course/skill-drafts/` until promotion.

## Workflow per class

1. **During / right after class** — operator writes 2–5 lessons via `save_lesson` MCP tool. Each cites source class in tags.
2. **Class index update** — operator (or Claude on operator's request) appends a row to `classes.md` with the generated lesson IDs.
3. **Periodic review** (monthly) — scan for clusters that qualify for skill promotion; draft under `skill-drafts/`; promote via `register_skill` when ready.

## Retrieval contract

- "I'm building a RAG system" → Router classifies bucket=personal or business, complexity=MEDIUM+, lesson recall finds tagged lessons.
- "Which class covered X?" → grep `classes.md` for the concept.
- "Give me everything on evals" → `search_lessons` with domain tag `evals`.

## Out of scope for v1

- Auto-extraction of lessons from class transcripts (manual capture for now — quality > coverage).
- Spaced-repetition surfacing of class material (the Router does context-driven recall, not study-driven).
- Linking lessons to specific external resources beyond the class index row.
