# Build Plan — Producción del Estudio (texto primero) en `sandia-marketing`

**Status:** v1.0 propuesto (2026-07) — **Trinity:** spec ✅ (`spec_Estudio_Produccion_Publicacion.md §2-3`) · plan = este doc · tasks = registradas en pretel-os.
**Gate de arranque:** Fase 2 FIRMADA al 100% (los 4 avatares, 2.0→2.6) + el calendario vivo (los slots esperan piezas; el drawer dice "el copy llega con producción" — esto lo cumple).
**Doctrina que gobierna:** `spec_Estudio §2` (el plan firmado **ES el brief** — el lever #1 anti-genérico) + `§3` (pipeline de 5 pasos + plantillas del corpus + **la DOCTRINA filtra el craft**) + **C4/C12/C1** (sin prueba social · sin urgencia fabricada · valor por funcionalidad) + **BP-001** (manual antes de automático) + reglas duras de sandia (data vía `lib/api`; DB por `supabase/migrations`; `npm run verify` es el gate).
**Alcance v1:** **TEXTO primero** (artículo SEO / guion de carrusel-reel / email / copy) — de un pilar firmado a una **pieza aprobada que llena un slot del calendario**. **Imagen/video = track aparte** (el AI Gateway, `spec_AI_Gateway_Wrapper_PROPOSAL.md`, tarea `babfe7a0`). Automatización SOLO tras ≥3 corridas manuales (BP-001).

---

## 0. Estado real (lo que ya existe)
- **El brief vive en lo firmado:** por avatar — voz 2.0 · pilares 2.3 · atomización 2.4 (1 ancla + N derivados, cada uno con su `kind` canal×formato) · ganchos 2.5 (con temporalidad M5) · + la oferta (Fase 1) + las keywords del estudio 0.2. **Eso ES la cola de producción + el brief.**
- **El calendario (M4)** ya tiene los slots (cadencias 2.2) + las fechas (radar M3). El drawer es placeholder hasta que haya piezas — este módulo lo llena.
- **El corpus** (`docs/Marketing Documentacion Teorica/`): las plantillas de calidad por canal (SEO · RRSS/ADAS · email PAS/AIDA · ads). El **CRAFT**.
- **Sandia:** la generación ya vive en `app/api/phase2/*` + `lib/api/llm/complete.ts` — el patrón a reusar.

## 1. LA decisión de diseño
1. **El plan firmado ES el brief** (§2): NO re-inferir. Ensamblar mensaje del pilar + gancho (2.5) + voz (2.0) + **keywords REALES** + palabras de la oferta + dolores del avatar → el brief más rico posible (= RAG). *Brief genérico → output genérico.*
2. **Pipeline de 5 pasos, no "un prompt"** (§3.2): Brief → **Estructura** (plantilla del corpus, no se inventa) → **Borrador** (outline-first) → **QA SEPARADO** (candados de voz + DOCTRINA + estructura + keywords) → **Aprobar** (tarjeta del operador). El QA separado es el salto de calidad vs one-shot.
3. **La doctrina filtra el craft** (§3.4): el QA **quita** lo que el corpus sugiere pero la doctrina prohíbe (testimonios → mecanismo, C4; precio tachado/urgencia → fuera, C12/C1). Glass-box: reporta qué quitó y por qué.
4. **Manual antes de automático (BP-001):** el operador corre el pipeline a mano por pieza; se automatiza tras ≥3 corridas reales con ≥1 best_practice destilada.
5. **Texto primero:** imagen/video (el wrapper de endpoints) es un track aparte; no bloquea el texto.

## 2. Milestones (cada uno cierra verde: `npm run verify` + e2e del slice)

### M1 — El brief + el modelo de pieza (la foundation)
1. Esquema `pieza` (§3.1): `id, avatar_key, pillar_id, anchor_ref, kind{channel,format}, production_mode, brief, outline, draft, qa_flags, temporality, status, cost`. Tabla `project_pieces` (o JSONB) en Supabase + accesores `lib/api`.
2. **Ensamblador del brief** (`buildBrief`, puro/testeable): desde el plan firmado (2.3 + 2.4 + 2.0 + 2.5 + oferta + keywords) → el objeto `brief` **channel-aware** (§2).
**Done:** dado un derivado de la cola (2.4) + su avatar, `buildBrief` produce el brief estructurado con grounding real; tests del ensamblado; tabla + accesores verdes.

### M2 — El pipeline de texto (brief → pieza aprobada), manual-asistido
1. Ruta `app/api/estudio/produce` (server): Brief → elige la **plantilla del corpus** por canal (§3.3) → **Borrador** (LLM, outline-first) → **QA** (paso separado: candados voz/doctrina/estructura/keywords; reporta qué quitó).
2. UI: una pieza de la cola → ver el borrador → el **QA visible** (qué revisó / qué quitó y por qué) → tarjeta **Aprobar / Ajustar / Regenerar** (autoría del operador).
**Done:** producir **1 pieza real** de punta a punta (un artículo SEO o un guion de carrusel desde un pilar firmado), con el QA aplicando C4/C12/C1; el operador la aprueba; `verify` verde.

### M3 — Pieza aprobada → biblioteca → llena el calendario
1. Pieza `aprobada` → entra a la **biblioteca de assets** (§5) → aparece como el **copy listo** en su slot del calendario.
**Done:** una pieza aprobada se ve en el calendario como publicación con su copy real; el drawer deja de ser placeholder.

## 3. Orden y dependencias
**M1** (brief + pieza) bloquea **M2** (el pipeline lo consume). **M2 → M3** (la pieza aprobada llena el calendario). Imagen/video (AI Gateway) = paralelo, después del texto.

## 4. Pendientes / decisiones
- **AI Gateway** (imagen/video) → spec aparte (`spec_AI_Gateway_Wrapper_PROPOSAL`, tarea `babfe7a0`) + costos en **Módulo C** (`c027d954`). Track separado.
- **Keyword research por avatar** (`cdf66e45`): aterriza el brief en búsquedas REALES (mejora el lever #1). **Recomendado antes de M2** — necesita OK del operador + presupuesto DataForSEO.
- **Storage de assets** (§5/§11): retención + versionado — se decide al llegar a media.
- **Perfil de producibilidad** (§3.7): trivial para texto v1 (todos pueden texto); importa con media.

## 5. V1 cuts (lo que NO entra)
- Solo **texto** (imagen/video = track aparte).
- **Manual-asistido** (sin automatización hasta ≥3 corridas — BP-001).
- 1 canal/formato para la primera corrida (artículo SEO o carrusel); ampliar tras validar.
