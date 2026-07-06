# Model Selection — el mejor modelo por tarea, no el más caro siempre

**Mandato del operador (2026-06-10):** multi-proveedor (Anthropic + OpenAI + Google + OpenRouter), elegir por caso, benchmarks primero, experimentos propios después.
**Arquitectura:** `lib/api/llm/complete.ts` es el swap-point declarado desde M0. `models.ts` define tarea→modelo; `providerFor()` rutea: `claude-*` → SDK Anthropic directo (prompt caching + web_search server tool); todo lo demás → OpenRouter (una integración, todos los modelos).

## 1. Panorama de benchmarks (junio 2026, fuentes abajo)

| Modelo | Precio $/M (in/out) | Señal clave | Fuente |
|---|---|---|---|
| Claude Opus 4.7/4.8 | 5 / 25 | Líder SWE-Bench Pro (~91); review/razonamiento top | morphllm, ideas2it |
| Claude Sonnet 4.6 | 3 / 15 | Caballo de batalla frontier; web_search nativo en nuestra ruta | vellum/llm-stats |
| Claude Haiku 4.5 | ~1 / 5 | Rápido/barato del stack actual | pricing propio |
| GPT-5.x | ~ frontier | AIME perfecto (math); estructura | lmcouncil |
| Gemini 3 / 3.1 Pro | ~ frontier | Multilingüe top (MGSM+MMLU-ProX ~100%) | benchlm |
| **Kimi K2.5 / K2.6** (Moonshot) | **0.60 / 2.50–2.80** | SWE-Bench Pro 76.8 ≈ GPT-5.5; agentic long-horizon nativo; **5–6× más barato que Sonnet** | coderouter, llmx, usagebox |
| DeepSeek V4 / Flash | **0.14 / 0.28** | El más barato tier-1; volumen/background | akitaonrails, usagebox |
| Qwen3 (235B/14B) | bajo (open) | Español destacado entre open-weights | siliconflow, La Leaderboard (arXiv 2507.00999) |

Lectura transversal de los leaderboards: **ya no hay "mejor modelo" — hay mejor modelo por tarea.** Exactamente la tesis del operador.

## 2. Mapa tarea → modelo (defaults conservadores + candidatos a destronar)

| Tarea Sandi | Default hoy | Candidato (experimento) | Por qué |
|---|---|---|---|
| `market_research` (0.2/0.4, web search + fiel a fuentes) | claude-sonnet-4-6 | gemini-3-pro · kimi-k2.5 | web_search server tool SOLO existe en nuestra ruta Anthropic hoy; factualidad frontier. Riesgo de cambiar: honestidad de citas |
| `conversation_beats` (reformular, voz Sandi es) | claude-haiku-4-5 | **kimi-k2.5** · deepseek-chat | Volumen alto, tono > razonamiento; Kimi a $0.60 es el candidato #1 |
| `extraction` (JSON, flags, merge-patch) | claude-haiku-4-5 | **deepseek-chat** ($0.14) · qwen3 | Tarea mecánica; el más barato que no falle el parse gana |
| `copywriting` (Phase 2) | claude-sonnet-4-6 | kimi-k2.5 · gpt-5 | Calidad de escritura ES; juez ciego decidirá |
| `strategy` (avatares, ERRC, ofertas) | claude-sonnet-4-6 | gpt-5 · kimi-k2.5 | **Techo = Sonnet, nunca Opus** (mandato operador: el medidor de créditos es nuestro costo variable; Opus $5/$25 rompe la economía unitaria). Calidad extra viene de prompts/retrieval |

## 3. Diseño del experimento (siguiente sesión dedicada)

1. **Golden set:** fixtures del run Sandi (pretel-os `run/sandi/`) + el run real de Healthy Families — inputs reales, outputs de referencia firmados por el operador.
2. **Protocolo por tarea:** mismo prompt × N modelos (vía router) × 3 repeticiones. Ciego para el juez.
3. **Métricas:** (a) calidad — juez LLM frontier con rúbrica por tarea (beats: ¿voz SOUL? ¿sin jerga?; extraction: ¿parse zod limpio?; research: ¿fuentes reales? ¿inferencia etiquetada?), (b) **costo real** (ya logueado en `project_llm_calls`), (c) latencia p50/p95, (d) tasa de fallo de contrato (zod).
4. **Decisión:** gana el más barato dentro del 95% de calidad del mejor. Se promueve en `models.ts` con fecha + evidencia (mismo patrón decision-log de pretel-os).
5. **Slugs OpenRouter:** verificar nombres exactos en openrouter.ai/models al montar el harness (cambian con releases).

## Fuentes

[Vellum LLM Leaderboard](https://www.vellum.ai/llm-leaderboard) · [Artificial Analysis](https://artificialanalysis.ai/leaderboards/models) · [LM Council](https://lmcouncil.ai/benchmarks) · [Kimi K2.6 review (CodeRouter)](https://www.coderouter.io/blog/kimi-k2-6-review-coding-benchmarks-2026) · [Kimi vs Sonnet pricing (llmx)](https://llmx.tech/blog/kimi-k2-5-vs-claude-sonnet-4-5-model-comparison-2026) · [Cheapest comparison (UsageBox)](https://usagebox.com/articles/claude-sonnet-vs-kimi-vs-deepseek-billing) · [SWE-bench Pro cost ranking (Morph)](https://www.morphllm.com/best-ai-model-for-coding) · [Multilingual 2026 (BenchLM)](https://benchlm.ai/multilingual) · [Spanish open LLMs (SiliconFlow)](https://www.siliconflow.com/articles/en/best-open-source-llm-for-spanish) · [La Leaderboard español (arXiv)](https://arxiv.org/pdf/2507.00999)
