# AI Engineer Course — Class Index

Curso: **LIDR — AI Engineer** (Antonio Pérez, training.lidr.co). Tag base: `course:lidr-ai-engineer`.

Quick lookup: concepto → clase → lessons. Append una fila por artículo/clase.

| # | Sesión | Título | Conceptos clave | Domain tags | Lessons (UUIDs cortos) |
|---|--------|--------|-----------------|-------------|------------------------|
| 01 | S1 | Estructura de una llamada al API de Anthropic | Messages API, max_tokens obligatorio, alternancia user/assistant, SDK auto-retry, no total_tokens | prompting, infra, anthropic-sdk | `908b2d90`, `ee81b0d2`, `b76076bb`, `a59937b7` |
| 02 | S1 | Estructura de una llamada al API de OpenAI | Responses API vs Chat Completions, previous_response_id + store, snapshot vs alias, reasoning_tokens cost | prompting, infra, openai-sdk | `4763ad94`, `293faa35`, `436681c6`, `3b90dd17` |
| 03 | S1 | Estructura de una llamada al API de Gemini | google-genai SDK, role="model", count_tokens gratis, safety filters silenciosos, thinking default | prompting, gemini-sdk, cost | `541528bd`, `bb81bde8`, `3364ca65`, `28a8951f` |
| 04 | S1 | Parámetros en modelos de razonamiento | Bloqueo temperature/top_p/penalty, reasoning_effort + verbosity, Claude 4.5+ no temp+top_p, o-series system→developer | prompting, anthropic-sdk, openai-sdk | `84262e81`, `9f9b77c4`, `cb0fe489` |
| 05 | S1 | Tokenización: conceptos avanzados | BPE, español 20-40% más tokens, output 3-6x más caro, compact JSON, LLMs no hacen aritmética, coste cuadrático en multi-turn | embeddings, cost, prompting, i18n | `ea145413`, `7f83caeb`, `97d50968`, `01a5a0a3`, `7451b582` |
| 06 | S2 | Comparación de modelos 2026 | Multi-modelo router (cost), Batch API 50% off, DeepSeek compliance (servers China), OpenRouter vs LiteLLM | arch, cost, ethics, infra | `9364e272`, `5f23950d`, `ec0293d1`, `fd06ba88` |
| 07 | S2 | Arquitectura escalable en proyectos IA generativa | FastAPI/ASGI async para LLM, capa context/ como punto sustitución CAG→RAG, routers thin / services fat | arch, infra | `8ac337af`, `1ba8d74d`, `daeb04a7` |
| 08 | S2 | Arquitectura de conversaciones con modelos | Transaccional vs conversacional (decisión de producto), sliding window + turnos ancla, servicio stateless | arch, product, prompting | `100dfb92`, `46396856`, `4435cc9e` |
| 09 | S2 | Qué es CAG (Cache Augmented Generation) | CAG vs RAG criterios, lost in the middle, context útil 60-80% del anunciado, CAG primero RAG después | arch, rag, cag | `0ad9e8da`, `545b08d6`, `ec5d0b86`, `aa315077` |
| 10 | S2 | Don't do RAG when CAG is all you need (paper) | Paper Chan et al. ACM 2025, KV-cache precomputado, beats RAG en SQuAD/HotPotQA | arch, cag, rag, paper | `e025290d` |
| 11 | S2 | Gestión efectiva de contexto en arquitectura CAG | 2-3/5-7/>10 ejemplos en CAG, orden deliberado del prompt, 4-dim system prompt, formato ejemplos = formato output | prompting, cag, rag | `08061d08`, `8c1261d2`, `1ef113b2`, `56991e09` |

**Total lessons capturadas:** 39 (todas auto-aprobadas).

## Cómo usar este índice

- **Buscar clase por concepto** — Ctrl-F en "Conceptos clave" o "Domain tags".
- **Lesson → clase fuente** — cada lesson carga tag `class-NN`; busca esa fila aquí para fuente original.
- **Lessons completas** — usa `search_lessons(tags=["ai-engineer-course"])` o por UUID corto en DB.
- **Progreso del curso** — cuenta filas; hoy son 11 (S1 completa + S2 completa).

## Domain tag vocabulary (de spec.md)

`rag` · `evals` · `agents` · `fine-tuning` · `prompting` · `embeddings` · `infra` · `ethics` · `product`

Tags extra emergentes durante captura (subsidiarios, no requieren amend de spec): `anthropic-sdk`, `openai-sdk`, `gemini-sdk`, `cost`, `arch`, `cag`, `migration`, `compliance`, `i18n`, `observability`, `privacy`, `paper`, `reference`.

## Source

Antonio Pérez, training.lidr.co/members/32741395 — sin link directo a clases individuales (se accede vía plataforma LIDR).
