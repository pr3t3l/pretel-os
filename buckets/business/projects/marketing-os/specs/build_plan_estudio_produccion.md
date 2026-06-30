# Build Plan — Producción del Estudio (texto primero) en `sandia-marketing`

**Status:** v2 **EJECUTADO** (2026-06-30) — UI v2 (grid + detalle + "Desarrollar idea" + AI Gateway scaffold) construida, verificada (179 tests) y desplegada; ver §6.4 para los SHAs. **Trinity:** spec ✅ (`spec_Estudio_Produccion_Publicacion.md §2-3`) · plan = este doc · tasks = registradas en pretel-os.
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
6. **El Estudio es PERPETUO, no one-shot (spec §1):** el plan firmado es una **RECETA** (pilares + ganchos + cadencias = motor generativo), NO una lista fija de N piezas. La cola 2.4 es el **PRIMER LOTE**; v1 lo produce manual. El motor que genera piezas nuevas semana tras semana + el **LOOP** (producir → publicar → medir → refrescar/ajustar, Fase 4/5 re-disparan) es la **evolución** — se construye tras validar el pipeline manual (BP-001). Este plan **arranca** ese sistema, no un one-shot que se vacía.
7. **Glass-box por pieza (spec §0 anti-promesa + §8):** cada pieza muestra su **ORIGEN** (de qué pilar/gancho/voz nació) + su **MODO** + su **COSTO** antes de producir. Nunca prometemos "todo te llega hecho" si una parte la pones tú.

## 1. LA decisión de diseño

### M1 — El brief + el modelo de pieza (la foundation)
1. Esquema `pieza` (§3.1): `id, avatar_key, pillar_id, anchor_ref, kind{channel,format}, production_mode, brief, outline, draft, qa_flags, temporality, status, cost`. Tabla `project_pieces` (o JSONB) en Supabase + accesores `lib/api`.
2. **Ensamblador del brief** (`buildBrief`, puro/testeable) — el contrato de datos **COMPLETO** (§2), nada del plan se desperdicia: **2.4** ancla+kind · **2.3** pilar (fuerza+modo) · **2.5** gancho · **2.0** voz (léxico+prohibidos) · **2.2** canal (función+cadencia+formato) · **2.1** reparto (momento de conciencia → registro) · **Fase 1** oferta (palabras exactas si REFORZAR) · **Fase 0** (keywords reales + idioma del avatar) · **perfil de producción** (→ el modo). El brief es **channel-aware** (SEO: entidades + gap de la SERP · social: ADAS · email: posición en la secuencia · ads: límites) y un **artefacto estructurado** (JSON-Prompt), no solo prosa.
**Done:** dado un derivado de la cola (2.4) + su avatar, `buildBrief` produce el brief estructurado con grounding real; tests del ensamblado; tabla + accesores verdes.

### M2 — El pipeline de texto (brief → pieza aprobada), manual-asistido
1. Ruta `app/api/estudio/produce` (server): Brief → elige la **plantilla del corpus** por canal (§3.3) → **Borrador** (LLM, outline-first) → **QA** (paso separado: candados voz/doctrina/estructura/keywords; reporta qué quitó).
2. UI — la superficie **"Producir"** del Estudio (§8.1), por avatar: una pieza de la cola (mostrando **de qué pilar/gancho nació + su modo + costo** — glass-box) → ver el borrador → el **QA visible** (qué revisó / qué quitó y por qué) → tarjeta **Aprobar / Ajustar / Regenerar** (autoría del operador). *(Publicar = la superficie siguiente, §7 / §8.4.)*
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

## 6. UX v2 — el grid unificado + el detalle (2026-06-30, mandato del operador)
Tras probar la sim: el "Producir" de lista delgada se reemplaza por una **superficie tipo Library de GPT** + un cambio de flujo. Funda la investigación de generación de imagen/video (ver `spec_AI_Gateway_Wrapper_PROPOSAL §0-3`).

### 6.1 El flujo (renombre)
**"Producir" → "Desarrollar idea"**: la primera acción crea el **PAQUETE** (texto + `design_spec` + prompts + tips), NO la media. Generar la imagen/video real es el paso **ÚLTIMO** (el AI Gateway), disponible **tras aprobar**.
Estados: **por desarrollar → desarrollada → aprobada → producida (media) → publicada**. El texto puro queda publicable al aprobar; solo la media pasa por "Producir media".

### 6.2 El grid (la superficie del Estudio)
Una sola superficie: cada derivado del plan = una **card**. Filtros por **avatar** + **canal**; orden por **fecha sugerida** (del calendario M4). Producida → miniatura/preview + título; por desarrollar → título + descripción + CTA "Desarrollar idea". (Reemplaza la lista cola+biblioteca.)

### 6.3 El detalle (al abrir una pieza) — glass-box
**Encabezado común** (toda pieza): origen (pilar · gancho · voz · keywords · avatar) · el prompt exacto · QA (qué quitó y por qué) · tips de publicación · modo + costo · acciones (Aprobar / Regenerar / Editar).
**El entregable, por tipo** (del `kind` = canal×formato de la atomización 2.4):
- **Blog/SEO:** título SEO + meta · cuerpo (H2/H3, outline-first) · keywords + enlaces internos · **prompts + `design_spec`** de las imágenes.
- **LinkedIn:** el post (gancho + cuerpo + CTA, formato LinkedIn) · el gancho (primer renglón) · hashtags · **prompt + `design_spec`** del visual.
- **Imagen** (pin/post): el **`design_spec`** (cámara·iluminación·estilo·composición·output) · texto superpuesto · el prompt de generación · título/descripción (SEO).
- **Carrusel:** por diapositiva: texto + dirección visual + **prompt + `design_spec`** · gancho (slide 1) + CTA (final) · caption + hashtags.
- **Reel/Video:** **guion por intervalos** (0-3s gancho/cuerpo/cierre) + texto en pantalla · `design_spec` de video (movimiento de cámara · motion · audio · diálogo) · audio/trend.
- **Email:** asunto + preheader · cuerpo (PAS/AIDA según secuencia) · CTA · tips de envío.

El **`design_spec`** de toda pieza visual usa el **esquema canónico** (`spec_AI_Gateway §1-2`): sujeto · escena · cámara{ángulo, plano, lente, [video: movimiento]} · iluminación · estilo · composición · output [+video: motion, pacing, duration, audio, dialogue]. **Prosa, no JSON** (hallazgo verificado).

### 6.4 Milestones v2 — EJECUTADO (renumeran el alcance de la UI; el brief M1 + el pipeline M2 se reusan)
Estado: **P1–P5 construidos, verificados (179 tests) y desplegados** (Vercel auto-deploy desde `main`). SHAs en `sandia-marketing`.
- **P1** ✅ `1d9caee` — modelo de pieza enriquecido: `prompt_used`, `design_spec` (jsonb), `image_prompts`/`video_prompt`, `publish_tips`, `suggested_date`. Migración + tipos + accesores.
- **P2** ✅ `41a3996` — el grid (cards · filtros avatar/canal · estado por badge). Match derivado↔pieza por `(avatar_key, pillar_id, channel===kind)` — sin columna nueva; colisiones same-kind/same-pillar raras y aceptables v1 (fix futuro = `derivative_index`).
- **P3** ✅ `41a3996` — el detalle (modal glass-box: origen · la pieza · `design_spec` · tips · QA · el prompt exacto · acciones), por tipo de §6.3.
- **P4** ✅ `387c5da` — el pipeline "Desarrollar idea": UNA llamada LLM → el paquete completo por tipo (texto/guion + `design_spec` + tips + QA), `parseDevelop` robusto.
- **P5** ✅ `de0512a` — AI Gateway scaffold: el **serializer canónico→prosa** (`lib/gateway/serialize.ts`, el "router propio") + interfaz `MediaProvider` + **proveedor mock** (placeholder SVG, cero costo) + route `produce-media` + botón "Producir media" en piezas aprobadas. **Generación real env-gated**: entra al conectar las llaves del operador (Replicate/fal/Veo/…) + presupuesto — no se gasta su dinero sin permiso.

**Pendiente para "media real" (cuando el operador decida):** conectar ≥1 adapter real en `selectProvider()` tras poner la llave en `.env.local`/Vercel (`REPLICATE_API_TOKEN`/`FAL_KEY`/…) y definir presupuesto. Opcional: columna `derivative_index` si aparecen colisiones de match; `suggested_date` real desde el calendario (hoy null → orden natural de la cola).
