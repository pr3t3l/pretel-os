# Build Plan — Producción v3: el Motor de Coherencia

**Status:** v3 propuesto (2026-07-01) — re-scope tras la [investigación de mercado](../docs/research/2026-07-01_market_strategy_scope.md). **Supersede** el alcance UX-only de `build_plan_estudio_produccion.md` (v2): el Estudio deja de ser una superficie de generación y pasa a ser un **motor de coherencia de marca a nivel campaña**. **Trinity:** spec = este doc + la research · plan = §4-5 · tasks = §6 (+ registradas en pretel-os al arrancar).

**Gobierna:** la research 2026-07 (hallazgo maestro: el mercado rechaza lo **no-verificable**, no la IA) + las decisiones del operador (§1) + la doctrina de sandia (data por `lib/api`; DB por `supabase/migrations`; `npm run verify` + `npm run build` son el gate; sin client lock-in).

---

## 1. Decisiones registradas (del operador, 2026-07-01)

- **D1 — Usuario:** el **no-experto primero** (dueño de PyME / solopreneur / creador que vende a mercado US-inglés, no técnico, hoy hace malabares con Jasper+Canva+Buffer+AdCreative sin que los datos fluyan). **Agencias / equipos internos después.**
- **D2 — Producción = MOTOR DE COHERENCIA, no playground.** No competimos con Kling/OpenArt/Canva en amplitud de generación (commodity que fal.ai regala por debajo). Construimos lo que nadie da: **misma marca + voz + personaje a través de N ganchos**, con el prompt exacto y el trail de fuentes.
- **D3 — Nosotros el cerebro, fal.ai/Replicate las manos.** Rentar las manos es barato y validado → se construye **ya**. La integración NO es "la capa cara".
- **D4 — Modelo de precio (híbrido, glass-box):**
  - **Silla / mensualidad = el cerebro:** acceso al sistema + personalización (StyleID) + generación de prompts con nuestra IA + Fundamento + Fase 1 de contenido (lo barato) + métricas de auto-mejora. Incluye un **allowance de generación** para la activación (1ª pieza publicable en la 1ª sesión, sin paywall).
  - **Generación de media = las manos + 20%:** saldo aparte, **costo real de fal.ai × 1.20**, transparente. Nunca perdemos en COGS; esquiva la "jaula de créditos" (queja #1 de UX del mercado).
- **D5 — Build lean + validar en vivo.** El moat-mínimo se construye ya; la **silla ES el test de willingness-to-pay** por el cerebro (no un smoke-test aparte). Se instrumenta desde el día 1.

## 2. Doctrina que gobierna el producto (de la research, citada en el reporte)

1. **Glass-box = el moat, no un detalle.** Cada entregable sale con su trail de fuentes + el prompt/asset exacto que el usuario pega y **posee**. (80% prefiere la versión con fuentes; solo 7% confía más por ver IA visible.)
2. **StyleID inyectado en CADA generación** (modelo Coca-Cola/Adobe "Fizzion", pero democratizado): voz cuantificada 0-100 + design tokens + assets de referencia. Sin esto no hay promesa de coherencia.
3. **Brief de 1 insight antes de generar** (la industria desperdicia 33% del presupuesto en briefs pobres — el diferenciador más apalancado).
4. **Router, no modelo.** Integrar sobre fal.ai (≈985 endpoints, async/webhooks, ~30-50% más barato); tratar cada modelo como intercambiable (Sora 2 pasó de exclusiva a discontinuada en meses). La **tabla de enrutamiento** (§4.1) es la IP defendible.
5. **Nunca cobrar créditos por regeneración dentro del loop** (patrón más odiado). Outputs **editables** (capas/tokens), no PNG plano. Brand kit como **guardrail activo**, no PDF.
6. **HURT** (minutos de corrección humana por pieza) = la métrica de PMF, no volumen de output. El **data flywheel** (cada corrida mejora el contexto del proyecto) es el foso.

## 3. Non-goals (lo que NO construimos)

- ❌ Un playground de generación con 100 modelos (commodity de fal/OpenArt).
- ❌ Amplitud de diseño tipo Canva ni volumen de ads tipo AdCreative.
- ❌ Jaulas de crédito opacas.
- ❌ Traducción automática sin humano (será transcreación con checkpoint, F5).
- ❌ Precio/negocio "cerrado" antes de datos reales — la silla lo valida en vivo (D5).

## 4. Arquitectura (las 3 capas que pidió el operador)

### 4.1 TÉCNICA

**El loop de datos:** `Marca (StyleID)` → `Campaña (Big Idea + Brief)` → `Piezas (set coherente)` → `Aprobar` → `Publicar/Exportar` → `Métricas`.

**Componentes nuevos / que evolucionan (no se tira nada):**

| Componente | Estado hoy | Evoluciona a |
|---|---|---|
| `lib/gateway/` (Replicate + mock) | v2 (P5) | **Gateway v3 — router fal.ai**: tabla intención→modelo + **async/webhooks** (mata timeouts + rate-limit) + **imagen de referencia + start/end frame** |
| `brand_voice` (2.0) + import de identidad (construido, sin desplegar) | parcial | **StyleID por proyecto**: voz cuantificada 0-100 + design tokens (paleta/fuentes) + **assets de referencia** (logo/personaje) en Storage → inyectado en cada prompt |
| Estudio v2 (grid+detalle+develop) | v2 (P2-P4) | **piezas organizadas por Campaña**; el develop hereda StyleID + brief; glass-box reforzado |
| `project_api_calls` (cost ledger) | live | + **markup 1.20** + superficie de saldo (D4) |
| — | — | **Storage** (Supabase) para assets de marca + media; **modelo Campaña** (Big Idea + brief + piezas) |

**La tabla de enrutamiento (intención→modelo, la IP):** imagen con texto legible→GPT Image/FLUX[max]; personaje consistente en carrusel→**FLUX.1 Kontext** (~92% identidad, 1 ref); commodity barato→SDXL ($0.003); anuncio hablado/lipsync→**Veo 3.1** o Seedance; mini-película multi-toma misma mascota multiidioma→**Kling 3.0** (reference locking + Voice Binding); cinematográfico+física+audio→**Seedance 2.x** (hasta 50 refs); movimiento de cámara→**Higgsfield**; 4K alta consistencia→Seedream 4.x. Degradación con gracia si un proveedor cae.

### 4.2 VISUAL (lenguaje de diseño)
- **Papandi dogfood:** nuestra propia identidad visual, ejemplar (somos la prueba viva del StyleID).
- **Outputs editables** (capas + tokens), nunca PNG plano.
- **Panel de StyleID:** paleta + sliders de voz 0-100 + galería de referencias.
- **Biblioteca board-based** (patrón Air): vistas Galería / Tabla / Kanban.
- **Glass-box hermoso:** fuentes, prompt exacto, costo real — visibles sin ser ruido.

### 4.3 EXPERIENCIA (el flujo)
`Marca (una vez) → Campaña (Big Idea + brief de 1 insight) → Piezas (set coherente, misma marca en N ganchos, cada una con prompt + fuentes) → Aprobar (carriles por riesgo, comentar sobre la pieza) → Publicar/Exportar → Métricas (auto-mejora)`. Sin ansiedad de crédito; el usuario siempre es el autor (human-in-the-loop).

## 5. Fases (roadmap)

- **F1 — Fundamentos del motor** *(Incremento 1, EN CURSO)*: **StyleID por proyecto** + **Gateway v3 (router fal.ai + async + referencias/start-end)**. Arregla directamente "no me gusta lo que generamos" (on-brand + confiable) y habilita todo lo demás.
- **F2 — Campaña + Brief:** modelo de Campaña (Big Idea) + brief-gate (1 insight) + piezas que heredan el StyleID + glass-box por entregable + atomización hub-and-spoke (1 core → N spokes por canal).
- **F3 — Biblioteca + Aprobación:** Storage + biblioteca board-based + carriles de aprobación por riesgo + **link de aprobación sin seat** + auto-tag/búsqueda semántica (stack embeddings).
- **F4 — Billing:** Stripe silla + uso (fal×1.20) + allowance de activación + saldo, sobre el cost ledger.
- **F5 — Métricas + auto-mejora + Global:** HURT + métricas de relación (no vanity) + data flywheel; transcreación con checkpoint + disclosures de IA (C2PA/EU AI Act) por plataforma.

## 6. Tareas — F1 (Incremento 1)

### 6.1 StyleID por proyecto
- [ ] Modelo `brand_style_id` (artefacto phase_2 o tabla): `voice{tone_0_100...}`, `palette[{name,hex,role}]`, `fonts[]`, `references[{url,kind}]`, `motifs[]`, `do[]`, `dont[]`, `composition`.
- [ ] Migración + tipos + accesor `lib/api` (sin `.from()` fuera de lib).
- [ ] Fuentes del StyleID: (a) **import** (pegar HTML/CSS de Claude Design → extraer hex+fuentes — *código ya construido, sin desplegar*, se integra aquí), (b) Sandi propone desde voz/oferta/avatar, (c) **subir assets** (Storage) — logo/personaje/fotos.
- [ ] `styleIdSuffix()` — el ancla que se inyecta en CADA prompt de imagen/video (evoluciona `brandSuffix`).
- [ ] Panel de StyleID en la UI (paleta + sliders de voz + galería de refs) — glass-box, co-creación.

### 6.2 Gateway v3 — router fal.ai
- [ ] Adapter fal.ai (`lib/gateway/fal.ts`): `fal.subscribe()` + **webhooks** (async) para video/batches → mata el timeout de 60s y el rate-limit que sufrimos con Replicate síncrono.
- [ ] **Tabla de enrutamiento** `intención→modelo` (§4.1) como dato de producto; `selectProvider` la consume.
- [ ] Soporte de **imagen de referencia** + **start/end frame** en `GenInput` (todos los modelos top los consumen; sin esto no hay coherencia).
- [ ] Storage para media generada (URLs persistentes, no data-URI).
- [ ] Costo por tarea pre-estimado + atribuido por `project_id` **antes** de generar (ya encaja con el ledger + `MEDIA_BUDGET_USD`); dejar listo el markup 1.20 (F4).
- [ ] Degradación con gracia (fallback por capacidad) + mock cuando no hay llave.

### 6.3 Gate
- [ ] `npm run verify` + `npm run build` verdes; commit por sub-incremento a `main` de sandia.

## 7. Riesgos abiertos (de la crítica de la research)

- **¿Se paga por el cerebro?** — la silla lo valida en vivo (D5); instrumentar conversión + retención desde el día 1.
- **Economía unitaria:** verificar que `allowance + costo+20%` deja margen sano con precios reales de fal (video $0.15-0.40/s). Modelar antes de fijar el precio de la silla (F4).
- **Churn > adquisición:** activación a 1 pieza publicable en la 1ª sesión (el allowance) es la palanca de retención.
- **Legal:** EU AI Act exige etiquetado de IA desde ago-2026; FTC + políticas de Meta/TikTok. Convierte el disclosure en requisito no-negociable (F5, pero tenerlo en el radar del MVP).
- **Volatilidad de proveedor:** ningún modelo individual > umbral del valor; la tabla de enrutamiento es un activo vivo con costo de mantenimiento.

---

**Referencias:** [research 2026-07-01](../docs/research/2026-07-01_market_strategy_scope.md) · `build_plan_estudio_produccion.md` (v2, superseded en scope) · `spec_AI_Gateway_Wrapper_PROPOSAL.md` · memorias `papandi-scope-research-2026-07`, `papandi-entregable-accionable`, `sandia-cost-ledger`.
