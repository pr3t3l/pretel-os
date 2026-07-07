# Build Plan — Modelo de contenido (PILAR → ÁNGULO → PIEZA)

**Estado:** v1.1 — para EJECUTAR tras la firma de `spec_Modelo_Contenido.md` (ratifica C17 en `_audit_change_ledger.md`). **NO construir hasta firma.**
**Decide:** el orden de ejecución, tests por fase, la migración, y **cómo el cambio se relaciona con la producción de video** (input-side vs output-side).
**Fuentes:** `spec_Modelo_Contenido.md` (autoridad) · `_audit_change_ledger.md` C17 · **`docs/app/ensamblador-de-prompts.md`** (el compilador de dos etapas — autoridad de la Capa 2/develop) · `docs/research/doctrina-video-2026.md` (qué espera el modelo de video) · mapa de producción (explorador, esta sesión) · `spec_Estudio_Produccion_Publicacion.md`.

---

## 0. Dónde vive "la idea" — CORRECCIÓN (el operador cazó un error de diseño)

Mi propuesta previa (un campo `angle` en el gancho) **re-introducía el `note`** — justo lo que este plan mata. Verificado contra `docs/app/ensamblador-de-prompts.md` (Anexo fila 7 + fix #2): **el `note` HOY NI SE IMPRIME al prompt de develop** — es un campo cargado-sin-usar; el develop ya arma la idea desde pilar + gancho + kind. No hay especificidad que "rescatar" con un campo nuevo.

**La idea vive en el TEXTO del gancho.** El modelo de 3 capas del Cerebro de Ganchos (ya escrito en el ensamblador §2.1.E: *"DOLOR × FORMA × ESCENA — tres capas que se componen, nunca compiten"*) es el correcto:

| Capa | Qué es | De dónde sale | Ejemplo (del operador) |
|---|---|---|---|
| **DOLOR** (la idea/sustancia) | el **texto del gancho** (2.5) + el pilar | 2.5 — sagrado | *"You had a good month. Then a quiet one… That's someone else's decision about your income."* |
| **FORMA** (cómo se dice) | `template` + `psychology` + `goal` del catálogo de 4.550 | `hooks_catalog`, E3 al desarrollar | *"I spent [time] figuring out why [X] wasn't working…"* · Open Loop · Engagement |
| **ESCENA** (la apertura visual) | el gancho visual | `visual-hooks.ts`, al desarrollar | *"caída / algo se derrama"* |

**Consecuencia (SIN campo `angle`):** el único cambio a 2.5 es que el prompt genera ganchos **RICOS** — el texto carga la idea completa (como tu ejemplo: 3 frases con reframe), no un teaser de 4 palabras. El develop desarrolla ESE gancho + pilar. El `note` se elimina sin pérdida (no se usaba). El `anchor` se muda al pilar (2.3). **Nada de `angle`, nada de `note`.**

*Sobre los 4.550:* NO es overengineering — es la capa FORMA, y funciona por **retrieval** (E0 SQL → ≤40 candidatos → E1 re-rank → 5 picks), no "vadear 4.550". Su `psychology`+`goal` guían el desarrollo. Caveat real: hoy están **sub-cableados** — el `psychology`/`goal` no llegan del todo al develop (ensamblador fix #10); hay que wire-arlos. *(Licencia: OK — el operador confirmó que los compró para uso libre, 2026-07-06; sin restricción para el SaaS.)*

---

## 1. El árbol de prompts (antes → después)

**Antes (3 llamadas):** 2.3 pilares · 2.4 atomización (ancla + derivados + ratio) · 2.5 ganchos.
**Después (2 llamadas):** 2.3 pilares (+ ancla + ratio) · ~~2.4~~ · 2.5 ganchos (texto RICO).

```json
// 2.3 enriquecido — absorbe el ancla y el ratio del difunto 2.4
{ "ratio_policy_plain":"3:1 — de cada 4, 3 dan y 1 pide (5:1 si viene quemado)",
  "pillars":[{ "id":"PILLAR_A","name":"...","force_attacked":"ongoing_pains","mode":"resolve",
    "message":"...","anchor":{"title_working":"..."},"channels":["blog_seo","social"] }, ...×4 ] }

// 2.5 — MISMO schema {hook_id, template, text, pillar}; cambia la CALIDAD del texto:
// el `text` es la idea completa (rico), no un teaser. Sin campo `angle`.
{ "hooks":[{ "hook_id":"H_A_01","template":"curiosity_open_loops",
    "text":"You had a good month. Then a quiet one. Then another good month — and you still don't know why either happened. That's someone else's decision about your income.",
    "pillar":"PILLAR_A" }, ...10/pilar ] }
```

---

## 2. Fases de ejecución (ordenadas, con tests)

### P1 — Schema + prompts (la raíz)
- `content-plan.ts`: `Pillar` gana `anchor`; `PillarSet` gana `ratio_policy_plain`; **borrar** `Atomization`/`AtomizationMap`/`atomGateReady`. `Hook` NO cambia de schema (`{hook_id, template, text, pillar}`). `pillarsGateReady` (4 fuerzas) se queda.
- `canon.ts`: quitar `"2.4"` de `P2Step`/`P2_STEP_IDS`/`P2_GUION`/`P2_ARTIFACT`; borrar `shapes["2.4"]`, su caso en `parseP2Proposal`, `composeAtomMsg`; **enriquecer** `shapes["2.3"]` (anchor + ratio); **subir la calidad** de `shapes["2.5"]` (el `text` = la idea completa, no 1-2 frases sueltas).
- `config.ts`: quitar la fila del paso 2.4.
- **Tests:** `phase2-canon.test.ts` (shapes nuevas, sin 2.4); gate = 4 fuerzas.
- **Verif:** `npm run verify`; el wizard corre 2.0→2.1→2.2→2.3→2.5.

### P2 — El contrato de develop (Capa 1 / `buildBrief`)
- `brief.ts`: `Target` pasa de `{pillar_id, derivative_index}` → **`{pillar_id, hook_id, channel}`**; `buildBrief` lee el gancho por id (borrar `rotateHook`), `kind` desde `channel`, la IDEA desde `hook.text` (rico), `anchor` desde `pillar.anchor`.
- `produce/route.ts`: body `{projectId, avatarKey, pillarId, hookId, channel, visualHook?, hookTemplateId?, publishDate?}`; cargar el gancho por id; **validar** `hookId ∈ pilar` y `channel` habilitado en la matriz 2.2; `type = channelToContentType(channel)`.
- `prompts.ts`: la línea del gancho ya es la idea (sube en prominencia); *"PIEZA ANCLA"* desde `pillar.anchor`. (Oportunidad: aplicar de paso los fixes #2/#4 del ensamblador — imprimir `hook.template`, `psychology`/`goal` del catálogo, `brand_promise` — pero eso es backlog de calidad, no bloquea el modelo.)
- **Tests:** `brief.test.ts` (nuevo Target, sin rotateHook); integridad en produce.
- **Verif:** desarrollar UNA pieza (gancho×canal) end-to-end en prod; el cuerpo abre con SU gancho (coherencia).

### P3 — El sorteo del set inicial (`plan.ts`, la reescritura grande)
- `buildPublicationPlan`: iterar **pilares × canales habilitados**; elegir ganchos (mayormente distintos) pesados por **rol de canal** (carrusel=educar, Reel=alcance) + **journey** (2.2) + **ratio** (`pieceIntent`/`ratioStatus`, ya en Etapa E); respetar cadencias/ventanas/topes; emitir **slots ○ VACÍOS**.
- **Tests:** `plan.test.ts` (slots ○; ratio; mezcla por rol; generativo, no se agota).
- **Verif:** el calendario se llena con slots ○ desde el pozo de ganchos.

### P4 — UI (biblioteca de ángulos + calendario)
- `estudio/page.tsx`: "ideas (derivados)" → **"biblioteca de ganchos por pilar, desarrollable a cualquier canal"**; *Desarrollar* abre selector de canal (habilitados en 2.2).
- `calendar/page.tsx`: estados ○◐●✓; desarrollar desde el slot (ancla la fecha); vencidos se reprograman con aviso.
- **«Desarrollar mi semana»** (lote) + una-por-una (default en debug).
- **Verif visual** en papandi.com.

### P5 — Migración de datos
- Proyectos con `atomization_map` firmado → copiar `long_form.title_working` a `pillars[].anchor`; los derivados se **descartan**. Los ganchos (2.5) **no migran** (mismo schema; el texto rico aplica a los nuevos). Sin pérdida.

---

## 3. La relación con la producción de video (la pregunta del operador)

**El cambio de modelo toca el INPUT de develop (Capa 1); la producción de video cuelga del OUTPUT (Capas 2-3).** Son ortogonales y se encuentran en el paso develop.

### 3.a El compilador de dos etapas (autoridad: `ensamblador-de-prompts.md`)

```
FASES FIRMADAS ──Capa 1: buildBrief()──▶ BRIEF ──Capa 2: developTypeInstruction(type)──▶ LLM
   (código fuente)     ▲ ESTO re-cablea                    │ (DETERMINISTA por canal×formato)
                       (input hook×canal)     PIEZA (texto) + design_spec (IR-2) + TIPS + QA
                                                            │
                                        Capa 3: serialize.ts / video-routing.ts (dialectos)
                                                            │
                                              FLUX / Kling / Seedance / Veo → media
```

- **Capa 1 (`buildBrief`) = lo ÚNICO que este plan re-cablea.** De `{pilar, derivado}` a `{pilar, gancho, canal}`.
- **Capa 2 (`developTypeInstruction`) = DETERMINISTA por canal×formato, y YA existe.** No es un prompt genérico: `channelToContentType(kind)` → una receta específica por tipo (`video | image | carousel | blog | linkedin | email | text`). El cambio de modelo NO la toca — solo cambia de dónde saca su input.
- **Capa 3 (dialectos) = intacta.** Consume el `design_spec` que produce la Capa 2.

**La regla de oro (ensamblador §1):** doctrina, precios y **duraciones** las fija el CÓDIGO, nunca el LLM; el LLM solo redacta dentro de esa receta. Un dato decidido en la capa equivocada es un bug de arquitectura.

### 3.b Qué espera cada punto final — y por qué "no es lo mismo para reels que para imágenes"

La receta de Capa 2 YA codifica lo que el modelo final espera, distinto por tipo:

| Tipo | Qué exige el punto final (lo que el LLM debe emitir en el `design_spec`) |
|---|---|
| **VIDEO (reel)** | 1 prompt POR CLIP (3-5), autocontenido, con: **descripción del personaje COMPLETA + descripción del SET COMPLETA (idénticas en cada clip)** · narración (VO entre comillas, audio nativo) · descriptor de voz · **acción física obligatoria** · **movimiento de cámara obligatorio** · expresión fuerte en frame 1 · micro-evento si el clip >4s · duración · zona limpia (safe zones 14%/35%) |
| **IMAGEN (pin/carrusel/post)** | `image_prompts[]` (prosa): sujeto + escena + composición + paleta + mood. **SIN cámara, SIN movimiento, SIN transiciones, SIN narración.** Otra receta. |
| **TEXTO (LinkedIn/blog/email/Reddit)** | `===SPEC=== = {}` — **sin design_spec**. Solo estructura del canal (primera línea, largo, CTA nativo). Cero media por default. |

**Tus preguntas del reel, respondidas con la doctrina (`doctrina-video-2026.md` línea 128 + ensamblador §3.1):**

1. **¿Describir el personaje si ya tenemos su imagen?** — **SÍ, ambos, porque hacen cosas distintas.** La **imagen** (kit, `start_image_url`+`elements.frontal_image_url`) ancla la **identidad/cara** (Kling mantiene la consistencia ahí, ~92% fidelidad). La **descripción** aporta lo que una foto estática NO codifica: **acción, expresión, movimiento, cámara**, y el hecho de que el clip se MUEVE. La doctrina lo confirma: *"repetir personaje/set/voz completos por clip"* (mitigación al no-recuerdo del modelo entre clips). **No se omite la descripción** — se complementa con la imagen. **Además: al SUBIR un personaje/set, se auto-genera su descripción desde la imagen (modelo de visión) — así el texto que recibe Kling es coherente con lo que la foto muestra** (decisión del operador 2026-07-06; vive en la biblioteca de personajes, Etapa B / `spec_Phase_Identidad §2.2`).
2. **El set muestra solo un frame — ¿describimos el resto?** — **SÍ.** La imagen del set siembra el arranque; el clip se mueve, así que el prompt describe el **espacio, la luz y la acción** más allá de ese frame. Mismo razonamiento que el personaje.
3. **¿Transiciones clip 1→2→3→4?** — Realidad del empaque: los prompts RICOS (personaje+set+acción+cámara completos) superan los 512 chars de `multi_prompt` → caemos a **singles** (cada clip = una generación separada). Y está bien: **un reel son CORTES entre planos, no una toma continua** — el corte ES el lenguaje del formato. La identidad entre cortes la sostiene la **imagen del personaje** (referencia en cada clip); el estilo/paleta, la descripción repetida. El **frame chaining** (último frame → `start_image` del siguiente, FLUX Kontext) solo hace falta para el caso especial de *toma continua sin cortes* → Etapa G, **no bloquea** el modelo.

### 3.c Estado de la personalización de video (del explorador + doctrina)

| Pieza | Estado |
|---|---|
| Apertura visual (16 ganchos), audio nativo + voz del kit, multi-shot packing, personaje persistente (image-to-video), cálculo de costo | ✅ **construido** |
| Movimiento de cámara, CTA de cierre | ⚠️ **parcial** (en el prompt, sin botón UI) |
| Captions karaoke (WhisperX/FFmpeg/Creatomate), safe zones + overlay en VIDEO, botones ritmo/loop/duración, frame chaining, concat automático de clips | ❌ **planeado** (Etapa G) |

**Lo que debes saber:** el cambio de modelo **NO rompe la generación de video** — el video consume el `design_spec` + personaje + clips que la Capa 2 sigue produciendo. Los 8 botones de personalización + la post-producción son **Etapa G (output-side)**, un backlog aparte. Y los **10 fixes del ensamblador** (imprimir el `note`→ahora el gancho rico, `psychology`/`goal`, promesa de marca, keywords con volumen, etc.) son el **backlog de CALIDAD del develop** — también aparte, pero varios se pueden colar en P2.

**Preguntas del operador (extracción de frame + post-producción):** sacar el último frame de un clip = **canvas client-side ($0)**, trivial. El caso "clip 1 termina y no está listo para cortar" tiene dos salidas: **(a) barata/ya** — que el develop escriba cada clip para CERRAR en un beat limpio ("posición de entrega") → el corte siempre funciona, sin cadena; **(b) Etapa G** — frame chaining real (último frame → `start_image` del siguiente) para movimiento continuo, con orquestación secuencial + deriva generacional. Para "mantener el mismo set" en cortes basta la imagen del set + su descripción repetida. La **post-producción** (concat FFmpeg → **WhisperX ALINEA la narración YA conocida del guion** → captions karaoke → overlay en safe zones → export; ~5% del costo de generar; render Creatomate/Shotstack o worker FFmpeg propio) es output-side y mayormente **determinista** → se especifica en el **build plan de Etapa G**.

---

## 4. ¿Está alineado el módulo de contenido? — el mapa honesto

| Capa | Estado |
|---|---|
| Generación (2.3 pilares + 2.5 ganchos ricos) | Diseño LISTO → build **P1** |
| Contrato de develop (Capa 1, input gancho×canal) | Re-cablear → **P2** |
| Sorteo / calendario generativo | Reescribir → **P3** |
| UI biblioteca de ganchos + slots | Construir → **P4** (Etapa D vuelta grano) |
| Develop compiler (Capa 2, receta por formato) | **YA existe, endpoint-aware; NO se toca** (solo cambia su input) |
| Generación de video (Capa 3) | COMPATIBLE, no se rompe |
| Personalización de video (8 botones + post-producción) | **Etapa G** — 1 construido, 2 parciales, 5+ planeados (output-side) |
| Calidad del develop (10 fixes del ensamblador) | Backlog aparte; varios colables en P2 |

**Respuesta corta:** el módulo de contenido queda alineado *como diseño* con este plan; falta DESARROLLAR (a) este rework input-side (P1-P5), (b) la biblioteca de ganchos (Etapa D = UI de P4), (c) la personalización de video output-side (Etapa G), y (d) los fixes de calidad del develop (ensamblador §4). (a) es prerrequisito de (b), (c) y (d).

---

## 5. Verificación global
- `npm run verify` verde por fase; deploy continuo.
- **End-to-end:** firmar 2.x → calendario con slots ○ (vacíos) → desarrollar un slot (gancho×canal) → pieza coherente (el cuerpo abre con SU gancho) → si es video: `design_spec` (personaje+set descritos por clip) → Kling (imagen del personaje como ancla) → variante.
- Métrica del modelo: la misma combinación no duplica llamadas; el `hook_id` viaja a la pieza (atribución del loop de automejora).
