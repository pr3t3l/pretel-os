# Build Plan — Producción v3: el Motor de Coherencia

**Status:** v3 (2026-07-01) — **F1 construido y validado en vivo** (StyleID + Gateway v3/fal+Kontext → 8 imágenes coherentes con la marca real). **Actualizado tras el test:** el motor da coherencia pero **NO atención** → se añade la doctrina §2.7 (coherencia ≠ atención; gancho = texto-overlay que la IA no renderiza) y se afila **F2 = Brief + Texto-overlay** (§6.4). Re-scope original tras la [investigación de mercado](../docs/research/2026-07-01_market_strategy_scope.md); **supersede** el alcance UX-only de v2. **Trinity:** spec = este doc + la research · plan = §4-5 · tasks = §6.

**Gobierna:** la research 2026-07 (hallazgo maestro: el mercado rechaza lo **no-verificable**, no la IA) + las decisiones del operador (§1) + la doctrina de sandia (data por `lib/api`; DB por `supabase/migrations`; `npm run verify` + `npm run build` son el gate; sin client lock-in).

> **⚠️ C17 (2026-07-09):** el **motor de coherencia** (StyleID + Gateway v3 + brief + glass-box + §2.7
> coherencia≠atención) **sobrevive intacto** — es el corazón del producto. Cambió el modelo de contenido:
> la **«atomización hub-and-spoke» (1 core → N spokes) murió** → hoy `pieza = ángulo × canal` (generativo). El
> grid **«Estudio v2»** lo reemplazaron **Ángulos** (`/angulos`) + **Media** (`/media`) en el swap 2026-07-08.
> El **Modelo de Campaña (Big Idea)** vive en `spec_Campanas.md`. El **gancho por derivado/rotación** murió:
> el operador ELIGE el ángulo. Autoridad: `spec_Superficies_Produccion.md` + `spec_Modelo_Contenido.md`.

---

## 1. Decisiones registradas (del operador, 2026-07-01)

- **D1 — Usuario:** el **no-experto primero** (dueño de PyME / solopreneur / creador que vende a mercado US-inglés, no técnico, hoy hace malabares con Jasper+Canva+Buffer+AdCreative sin que los datos fluyan). **Agencias / equipos internos después.**
- **D2 — Producción = MOTOR DE COHERENCIA, no playground.** No competimos con Kling/OpenArt/Canva en amplitud de generación (commodity que fal.ai regala por debajo). Construimos lo que nadie da: **misma marca + voz + personaje a través de N ganchos**, con el prompt exacto y el trail de fuentes.
- **D3 — Nosotros el cerebro, fal.ai/Replicate las manos.** Rentar las manos es barato y validado → se construye **ya**. La integración NO es "la capa cara".
- **D4 — Modelo de precio (híbrido, glass-box):**
  - **Silla / mensualidad = el cerebro:** acceso al sistema + personalización (StyleID) + generación de prompts con nuestra IA + Fundamento + Fase 1 de contenido (lo barato) + métricas de auto-mejora. Incluye un **allowance de generación** para la activación (1ª pieza publicable en la 1ª sesión, sin paywall).
  - **Generación de media = las manos + 20%:** saldo aparte, **costo real de fal.ai × 1.20**, transparente. Nunca perdemos en COGS; esquiva la "jaula de créditos" (queja #1 de UX del mercado).
- **D5 — Build lean + validar en vivo.** El moat-mínimo se construye ya; la **silla ES el test de willingness-to-pay** por el cerebro (no un smoke-test aparte). Se instrumenta desde el día 1.

**Decisiones de VIDEO (operador, 2026-07-01 — tras la [research de video](../docs/research/2026-07-01_video_field_of_action.md)):**
- **D-V1 — Audio:** SIN música en el archivo (se añade al publicar desde el catálogo de la plataforma — restricción legal). **Narración, diálogo y SFX nativos del modelo SÍ** (Kling/Seedance/Veo los generan). ElevenLabs fuera de V1 (innecesario con audio nativo; queda como fallback para VO en español, donde no hay lipsync nativo barato).
- **D-V2 — Personaje de marca (lane avatar): SÍ se ofrece.** Personaje sintético consistente mantenido por **referencias** (fotos + voz anclada: Kling elements/Voice Binding · Wan reference-to-video · Seedance refs — mismo patrón que la referencia Kontext ya construida). Candados: **label IA siempre**, consentimiento explícito si clona a una persona real, y la evidencia visible al usuario (glass-box: 36% de castigo de marca al detectar IA — él decide informado). Nota: AvatarHype ≠ plataforma (es curso/recetario); la tecnología real es reference-based consistency.
- **D-V3 — Entregable: TERMINADO por default** ("como sale de Kling/OpenArt": el/los clips generados listos para ver, con audio nativo; multi-shot en una generación — Seedance — preferido). **El PAQUETE va SIEMPRE incluido** (glass-box: guion + prompts + assets) y es el modo para usuarios expertos. Ensamble multi-clip server-side (captions quemados + concat, sin música ya es legal) = V1.5 opt-in.
- **D-V4 — Modelos: SELECTOR visible, no default sellado.** El usuario elige el modelo (precio por clip visible ANTES de generar), genera las variantes que quiera; **las variantes se ALMACENAN (append, nunca reemplazan)** y el usuario decide cuál queda. Cada generación se registra (modelo · costo · kept/discarded) → **yield-ledger = el bake-off continuo con uso real** (data flywheel §2.6) que va enseñando qué modelo rinde por tipo de video. Sustituye al bake-off sintético.
- **P0 legal vigente:** leer ToS comerciales de Kling/Wan/Seedance/fal (reventa del output a clientes del SaaS + likeness real) antes de vender la generación.

## 2. Doctrina que gobierna el producto (de la research, citada en el reporte)

1. **Glass-box = el moat, no un detalle.** Cada entregable sale con su trail de fuentes + el prompt/asset exacto que el usuario pega y **posee**. (80% prefiere la versión con fuentes; solo 7% confía más por ver IA visible.)
2. **StyleID inyectado en CADA generación** (modelo Coca-Cola/Adobe "Fizzion", pero democratizado): voz cuantificada 0-100 + design tokens + assets de referencia. Sin esto no hay promesa de coherencia.
3. **Brief de 1 insight antes de generar** (la industria desperdicia 33% del presupuesto en briefs pobres — el diferenciador más apalancado).
4. **Router, no modelo.** Integrar sobre fal.ai (≈985 endpoints, async/webhooks, ~30-50% más barato); tratar cada modelo como intercambiable (Sora 2 pasó de exclusiva a discontinuada en meses). La **tabla de enrutamiento** (§4.1) es la IP defendible.
5. **Nunca cobrar créditos por regeneración dentro del loop** (patrón más odiado). Outputs **editables** (capas/tokens), no PNG plano. Brand kit como **guardrail activo**, no PDF.
6. **HURT** (minutos de corrección humana por pieza) = la métrica de PMF, no volumen de output. El **data flywheel** (cada corrida mejora el contexto del proyecto) es el foso.
7. **Coherencia ≠ atención** *(hallazgo del test en vivo 2026-07-01)*. La coherencia (StyleID + referencia) mantiene la MARCA, pero **lo que PARA el scroll es el GANCHO**, no que se vea bonito. Y el gancho que para es **TEXTO grande y legible** — que **la IA de imagen NO puede renderizar** (sale garabato: "papagnda pleosodyd"). Por eso:
   - El gancho va como **capa de TEXTO-OVERLAY editable sobre un fondo IA limpio**, NUNCA "quemado" en la generación.
   - La **portada (slide 1) es el scroll-stopper**: hook de texto + un visual con **tensión/pattern-interrupt**, no una foto tranquila.
   - Slides tipo **diagrama / UI / texto** → **fondo limpio + overlay**, no IA renderizando texto.
   - Regla dura: una pieza **coherente pero sin gancho legible = nadie la mira**. La atención es un objetivo de primera clase, no un subproducto de la coherencia.

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
| **Ángulos + Media** (ex «Estudio v2 grid») | v2 (P2-P4) | piezas por **ángulo** (agrupables por Campaña → `spec_Campanas`); el develop hereda StyleID + brief; glass-box reforzado |
| `project_api_calls` (cost ledger) | live | + **markup 1.20** + superficie de saldo (D4) |
| — | — | **Storage** (Supabase) para assets de marca + media; **modelo Campaña** (Big Idea + brief + piezas) |

**La tabla de enrutamiento (intención→modelo, la IP):** imagen de fondo **SIN texto quemado** (el gancho va en overlay, §2.7)→FLUX/GPT Image; personaje consistente en carrusel→**FLUX.1 Kontext** (~92% identidad, 1 ref); commodity barato→SDXL ($0.003); anuncio hablado/lipsync→**Veo 3.1** o Seedance; mini-película multi-toma misma mascota multiidioma→**Kling 3.0** (reference locking + Voice Binding); cinematográfico+física+audio→**Seedance 2.x** (hasta 50 refs); movimiento de cámara→**Higgsfield**; 4K alta consistencia→Seedream 4.x. Degradación con gracia si un proveedor cae.

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
- **F2 — Brief afilado + Texto-overlay (la capa de ATENCIÓN)** *(SIGUIENTE — el hueco que el test reveló: el motor da coherencia, no atención)*:
  - **Brief-gate de 1 insight** que venda el valor ÚNICO de Papandi (no una metáfora genérica del problema) — el diferenciador #1.
  - **Capa de texto-overlay** (§2.7): fondo IA limpio + **gancho de texto grande, legible y editable** sobre la portada; por-slide clasifica **foto vs diagrama/UI/texto** (los de texto → fondo limpio + overlay, matan los garabatos).
  - **Portada primero**: la slide 1 se diseña como scroll-stopper (hook + tensión visual).
  - Modelo de **Campaña** (Big Idea → `spec_Campanas`) + piezas que heredan el StyleID + glass-box; **C17:** `pieza = ángulo × canal` (la «atomización hub-and-spoke 1 core → N spokes» murió).
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

> **Estado F1 (2026-07-01):** StyleID (editar a mano + import URL/CSS/PDF + proponer, anti-clobber) + Gateway v3 (fal + Kontext + referencia + presupuesto multi-proveedor) **construidos y validados en vivo** — 8 imágenes coherentes con la marca real. El test reveló el hueco de F2 (§2.7).

## 6.4 Tareas — F2 (Incremento 2, SIGUIENTE): Brief afilado + Texto-overlay
- [ ] **Brief-gate:** Sandi propone **1 insight que venda el valor ÚNICO de Papandi** (no la metáfora genérica del problema) antes de generar; el operador lo firma (glass-box).
- [ ] **Clasificador por-slide:** foto/escena (IA genera el visual) vs **diagrama / UI / texto** (fondo limpio + overlay; nunca IA renderizando texto).
- [ ] **Capa de texto-overlay:** componer el **gancho** (texto grande, legible, tipografía del StyleID) sobre el fondo IA — **editable, no quemado**; export con el texto encima.
- [ ] **Portada = scroll-stopper:** la slide 1 se diseña con hook + visual con tensión; el prompt del fondo deja **zona segura** para el texto.
- [ ] **Prompts SIN pedir texto en la imagen** (evita los garabatos "papagnda pleosodyd"); el texto vive SOLO en la capa overlay.
- [ ] Modelo de **Campaña** (Big Idea → `spec_Campanas`); pieza = ángulo × canal [C17: sin atomización hub-and-spoke].
- [ ] Gate verde + commit.

## 6.5 Tareas — F-Video V1 (tras la research de video + decisiones D-V1..V4)

**0 — Fix de ESENCIA (prerequisito de TODO el contenido, no solo video):**
- [ ] Cargar `business_context` (0.1: idea + diferenciadores firmados + why_now) al brief como bloque **ESENCIA**; la pieza debe respirarlo y el CTA nace de ahí (no genérico).
- [ ] La **oferta SIEMPRE presente** en el brief, dosificada por modo del pilar (agitar = implícita/puerta al final; reforzar = explícita). Hoy solo entra en "reforzar" → por eso los CTAs genéricos.
- [x] ~~Gancho por derivado (rotación sobre la biblioteca 2.5)~~ → **C17:** el operador ELIGE el ángulo (gancho 2.5); sin rotación por índice.

**1 — El guion de reel enriquecido (sin costo de generación):**
- [ ] Campos nuevos: `hook_text_overlay` (≤8 palabras, frame 1), narración/diálogo por intervalo (marcado para audio nativo), duración objetivo 15–35s, CTA única, densidad 5–10 palabras/s.
- [ ] Prompts de video **por clip y por modelo** (dialectos: comillas para diálogo en Seedance · ingredients ≤3 en Veo · start-frame en Kling · ≤2k chars en Wan) — entregable glass-box aunque el usuario genere fuera.

**2 — Generación real de video (el selector):**
- [ ] `routeVideoModel()` + catálogo de modelos de video en el gateway (Wan 2.6 · Kling 3.0 · Seedance 2.0 · Veo 3.1/Fast vía fal) con **precio/s visible antes de generar**.
- [ ] **Selector de modelo** en la UI + generación **asíncrona** (cola + polling; Kling concurrencia 1 en fal).
- [ ] **Variantes acumulativas**: cada generación se agrega (modelo · costo · prompt), nunca reemplaza; el usuario marca la que queda.
- [ ] **Yield-ledger**: registrar intentos vs elegidas por modelo (el bake-off continuo, D-V4).
- [ ] **Multi-shot packing** (verificado en fal 2026-07-01, `fal-ai/kling-video/v3/pro/*`): el guion canónico queda POR CLIP (agnóstico); el adapter de Kling agrupa clips en generaciones multi-shot de ≤15s vía `multi_prompt` ([{prompt, duration}], `shot_type: customize|intelligent`) → **misma voz y personaje dentro de cada generación** (resuelve el voice-drift), menos costuras; grupos encadenados con start/end frame. Precios: $0.112/s sin audio · $0.168/s audio nativo (EN/ZH) · $0.196/s voice control; 9:16 nativo; `generate_audio`. Seedance multi-shot equivalente; Seedance 2.5 (30s nativos) colapsará el reel a 1 generación cuando llegue a fal.
- [ ] Start-frames 9:16 desde el StyleID (FLUX/Kontext, ~$0.10–0.24/reel) — fija el aspect en i2v y ancla la marca; producto = foto real como start frame (anti-alucinación).

**3 — Personaje de marca (D-V2):**
- [ ] Entidad "Personaje" en el StyleID (set de fotos de referencia + voz opcional) → se inyecta como referencias en la generación (Kling elements / Wan ref-to-video / Seedance refs).
- [ ] Candados: label IA + flujo de consentimiento para likeness real + evidencia visible (glass-box).

**V1.5 (después):** ensamble server-side opt-in (captions quemados + concat multi-clip, sin música) + zonas seguras como config versionada (`platform_rules`) + checklist de publicación por plataforma.

## 7. Riesgos abiertos (de la crítica de la research)

- **¿Se paga por el cerebro?** — la silla lo valida en vivo (D5); instrumentar conversión + retención desde el día 1.
- **Economía unitaria:** verificar que `allowance + costo+20%` deja margen sano con precios reales de fal (video $0.15-0.40/s). Modelar antes de fijar el precio de la silla (F4).
- **Churn > adquisición:** activación a 1 pieza publicable en la 1ª sesión (el allowance) es la palanca de retención.
- **Legal:** EU AI Act exige etiquetado de IA desde ago-2026; FTC + políticas de Meta/TikTok. Convierte el disclosure en requisito no-negociable (F5, pero tenerlo en el radar del MVP).
- **Volatilidad de proveedor:** ningún modelo individual > umbral del valor; la tabla de enrutamiento es un activo vivo con costo de mantenimiento.

---

**Referencias:** [research 2026-07-01](../docs/research/2026-07-01_market_strategy_scope.md) · `build_plan_estudio_produccion.md` (v2, superseded en scope) · `spec_AI_Gateway_Wrapper_PROPOSAL.md` · memorias `papandi-scope-research-2026-07`, `papandi-entregable-accionable`, `sandia-cost-ledger`.
