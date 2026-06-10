# Corpus Audit & Retrieval Design (Quality at Depth — paso 1)

**Status:** auditoría de primer pase v1 (2026-06-07).
**Por qué:** "auditar el corpus ANTES de vectorizar" (lesson LIDR). Raw PDFs ≠ conocimiento recuperable. Este doc inventaria el corpus, lo mapea a las fases, y propone el pipeline + la estructura de recuperación. Sin esto, garbage-in = garbage-out.

**Ubicación del corpus (glass-box):** `C:\Users\prett\Pretel-OS\...\marketing-os\docs\Marketing Documentacion Teorica\` (copia worktree). **NO** está en la copia `Documents\pretel-os` donde viven los specs. Probablemente binarios sin commitear. → Decisión pendiente: dónde vive el corpus canónico y qué entra a git (ver Findings).

---

## 1. Inventario (4 cursos, ~65 archivos)

| Carpeta | # archivos | Contenido | Idioma |
|---|---|---|---|
| **1. Fundamentos de Marketing con IA** | ~10 | C1 intro, C2 análisis mercado, C3 SEO, C4 SEM, C5 RRSS, C6 Email + **Diccionario de términos** + guía completa | ES |
| **2. Análisis de mercado con IA** | ~12 | C1–C9: demanda, **buyer persona, propuesta de valor, activadores de compra, punto de dolor, competencia** + prompts + recursos + workflow | ES |
| **3. SEO con IA** | ~19 | C1–C11: conceptos, GPTs SEO, keyword research, datos estructurados, redirecciones, Google AIO, autoridad, contenido enriquecido + JSON prompting | ES |
| **7. Redes sociales con IA** | ~24 | Contenido (fundamentos, pilares, bases de marca, creación video, scraping, automatización funnel/comentarios/scripts) + **Prompt-*** + **.zip blueprints** | ES |

---

## 2. Mapeo corpus → fases / Módulos (el valor real)

| Curso | Alimenta | Especialista |
|---|---|---|
| 1. Fundamentos | overview cross-fase + **glosario → capa de educación** (movimiento 5, jerga-en-simple) | Setup Agent (educación) |
| 2. Análisis de mercado | **Phase 0** casi 1:1 (0.2 demanda · 0.3 persona/valor/activadores=forces/dolor=pain · 0.4 competencia) | especialistas Phase 0 |
| 3. SEO con IA | **Phase 2** (contenido SEO) + **Phase 3** (distribución) | especialista SEO |
| 7. Redes sociales | **Phase 2** (pilares, marca) + **Phase 3** (RRSS, automatización) | especialista RRSS |
| (4,5,6 — faltan) | probablemente SEM/Ads/Email a profundidad | 🔴 conseguir después |
| BMC (285+75+4, en Drive) | **Módulo A** (9 bloques) | especialistas Business Case |

---

## 3. Taxonomía de assets (3 tipos, manejo distinto)

- **Conocimiento** (capítulos `C*.pdf`, guías `*.docx`) → extraer texto → chunk por concepto → recuperación (RAG/CAG). El núcleo de la KB.
- **Operacional** (`Prompt-*.pdf`, `*.zip` blueprints, prompts de ejemplo) → **NO es conocimiento**; son **prompts/automatizaciones** → se vuelven **tools / sub-workflows / prompt-library**, separados de la KB.
- **Glosario** (`Diccionario-de-terminos-Marketing`) → alimenta directo la **capa de educación** (traducir jerga al nivel del `user_knowledge_profile`). Alto valor, bajo esfuerzo.

---

## 4. Findings / riesgos

1. 🔴 **Gap de completitud:** cursos 1, 2, 3, 7 presentes; **4, 5, 6 ausentes** (SEM/Email/Ads profundos). Conseguir o marcar el hueco.
2. 🔴 **BMC no está local** (285+75+4 págs en Drive, link inaccesible para el crawler). Hay que traerlo al corpus para el Módulo A.
3. 🟡 **Binarios:** mayoría PDFs (requieren extracción de texto) + .docx + .zip. No vectorizar el PDF crudo; extraer → markdown estructurado primero (lesson LIDR: JSON/PDF crudo genera embeddings ruidosos).
4. 🟡 **Ubicación + git:** el corpus vive en la copia worktree, no en la de specs, probablemente sin commitear. Decisión: corpus canónico en storage (no git para binarios) + **solo el texto procesado/estructurado** entra a la KB.
5. 🟡 **Idioma ES:** config Presidio `es_core_news_md` para PII; decidir embeddings multilingües; recordar prompt-inglés/salida-español.

---

## 5. Pipeline propuesto (audit → … → retrieval)

```
1. AUDITAR      (este doc) — qué hay, qué falta, qué tipo
2. EXTRAER      PDF/docx → texto/markdown estructurado (no crudo)
3. ESTRUCTURAR  chunk por CONCEPTO (no por página), con metadata:
                { course, chapter, phase/block, asset_type, lang, source_path }
4. VALIDAR      dedup, contradicciones, calidad (pandera/validadores)
5. INDEXAR      CAG (esenciales destilados) hoy → RAG cuando dispare trigger
```

**Recuperación por especialista:** cada especialista (Phase 0, SEO, RRSS, BMC-block) consulta SOLO su rebanada de KB filtrada por `phase/block` — así su contexto se mantiene afilado (no carga todo el corpus).

---

## 6. Próximos pasos

- [ ] Decidir ubicación canónica del corpus + qué entra a git (texto procesado, no binarios).
- [ ] Conseguir cursos 4/5/6 + traer los docs de BMC desde Drive.
- [ ] Pase de extracción (PDF/docx → markdown estructurado) — empezar por Curso 2 (alimenta Phase 0, donde está la simulación).
- [ ] Extraer el glosario a la capa de educación (quick win).
- [ ] Separar los assets operacionales (prompts/zips) a una prompt-library/tools, fuera de la KB.
- [ ] Definir el contrato `get_relevant_examples(input, phase)` (la costura CAG→RAG, lesson LIDR).
