# El Ensamblador de Prompts — inventario + diseño

> Rescatado del workflow `papandi-prompt-assembly-audit` (run `wf_6f254292-5e0`, 2026-07-02T08:44:06.165Z, status: completed).
> Inventario campo-por-campo de lo que crean las fases 0/1/2 vs lo que consume el ensamblador de prompts (develop) — gaps: creado-sin-usar, usado-débil, faltante, innecesario — y el diseño del ENSAMBLADOR como compilador.

---

# EL ENSAMBLADOR DE PROMPTS (el compilador de Papandi)

**Estado:** spec de arquitectura · **Fecha:** 2026-07-02 · **Fuentes:** inventario de artefactos F0–F2, auditoría de consumo del pipeline `produce` y mapa de gaps (2026-07-01/02), verificados contra `lib/estudio/brief.ts`, `lib/estudio/prompts.ts`, `app/api/estudio/produce/route.ts`, `lib/estudio/visual-hooks.ts`, `lib/estudio/visual-identity.ts`, `lib/gateway/serialize.ts`, `lib/gateway/video-routing.ts` en `C:\Users\prett\Documents\sandia-marketing`.

---

## 1. El modelo mental: un compilador de dos etapas con una fuente de verdad

Papandi es, técnicamente, un **compilador de decisiones firmadas a media publicable**. La analogía no es decorativa — mapea 1:1 sobre el código existente:

```
FASES FIRMADAS  ──buildBrief()──▶  BRIEF (IR-1)  ──buildDevelopSystem()──▶  LLM develop
(código fuente)                                                                 │
                                                              PIEZA + design_spec (IR-2) + TIPS + QA
                                                                                │
                                                   serialize.ts / video-routing.ts (dialectos)
                                                                                │
                                                        FLUX / Kling / Seedance / Veo → media
```

**Capa 0 — Fases firmadas = código fuente.** Los artefactos de `project_phase_artifacts` (0.1–2.6) son la única verdad. La firma (`status=signed` + gate) es el *type-check*: nada draft compila. `produce/route.ts` lo hace cumplir con un 409 duro sobre los 4 obligatorios (2.0 voz, 2.3 pilares, 2.4 atomización, 2.5 ganchos) y carga otros 6 en modo tolerante (oferta, statement, demanda, personas, 0.1, matriz 2.2). Regla: **si un dato no viene de un artefacto firmado o de un catálogo curado, no entra al prompt.**

**Capa 1 — El BRIEF = representación intermedia (IR-1).** `buildBrief()` (`lib/estudio/brief.ts`) es pura y testeable: cruza artefactos y produce el objeto `Brief` de UNA pieza — pilar seleccionado, derivado seleccionado, gancho rotado (`derivativeIndex % n`), voz, keywords top-8, oferta con su **modo** (`reforzar`/`contexto`), esencia 0.1. Aquí vive la **selección**: de todo lo firmado, qué le toca a esta pieza. El brief se persiste con la pieza (`insertPiece`) — es el registro glass-box de qué sabía el compilador.

**Capa 2 — Renderer por formato (backend de destino #1).** `buildDevelopSystem(brief, type, extras)` + `developTypeInstruction(type)` traducen la IR a un system prompt específico del entregable: `blog | linkedin | email | carousel | video | image | text` (clasificado por regex desde el `kind` de 2.4 vía `channelToContentType`). Esta capa decide la **forma**: estructura del guion por clips, tope 15–35s, carrusel 4–6 slides, PAS/AIDA en email. Su salida es doble: la PIEZA (texto) y el **design_spec (IR-2)** — el esquema canónico visual (sujeto/escena/cámara/luz/estilo/paleta/output + `image_prompts[]`/`video_prompts[]` + `hook_text_overlay`).

**Capa 3 — Renderer por modelo (dialectos).** La IR-2 se compila al motor concreto:
- **Imagen:** `serializeForGateway` (prefiere `image_prompts[0]`, cae a `composeImagePrompt` con orden fijo sujeto→escena→composición→cámara→luz→estilo→mood→paleta) + `brandSuffix` (paleta estricta + Avoid) + enrutado a **FLUX Kontext** si hay `reference_image_url` (~92% fidelidad de identidad).
- **Video:** `video-routing.ts` — `planClips` (segundos parseados de la prosa), `packClips` greedy ≤15s **solo Kling** (`multi_prompt`, misma voz/cara por grupo), `snapSeconds` a 4/6/8 **solo Veo**, y `falVideoBody` que emite el body EXACTO de cada dialecto (Kling: `multi_prompt[]` + `shot_type:"customize"`; Seedance: prompt único 4–15s; Veo: `duration:"Ns"` + 1:1→9:16). Precio visible antes de generar (D-V4).

**Qué capa decide qué (la regla de oro):**

| Decisión | Capa dueña | Dónde |
|---|---|---|
| Qué es verdad (mensaje, voz, audiencia, oferta, doctrina de negocio) | Fases firmadas | artefactos + gates |
| Qué entra a ESTA pieza (selección, rotación, modo de oferta) | IR-1 | `buildBrief` |
| Contexto runtime no-firmado (radar, journey, elecciones del operador) | Ensamblador de extras | `produce/route.ts` |
| Cómo se estructura por entregable (guion, slides, PAS) | Renderer de formato | `developTypeInstruction` |
| Qué se ve (escena, cámara, paleta, clips) | IR-2 | `design_spec` del develop |
| Sintaxis del motor (bodies, packing, snapping, clamps de ratio) | Dialecto | `serialize.ts`, `falVideoBody` |
| Doctrina (C1/C4/C12), precios, duraciones facturables | **NUNCA el LLM** | candados en prompt + código |

Un dato decidido en la capa equivocada es un bug de arquitectura. Ejemplo vivo: la **duración del clip** (decisión de dialecto/facturación) hoy la decide la prosa del LLM redactor vía regex `"N seconds"` — por eso está en los fixes (§4.10). Otro: `hook_text_overlay` **por diseño** nunca cruza a la capa 3 — el texto es capa overlay del editor, la IA no renderiza tipografía. Esa es una decisión de capa correcta y hay que protegerla.

Hay **dos ensamblajes de prompt**, no uno: (a) el system del develop (fases→IR-1→prompt de redacción, `estudio_develop@v2.0.0`, maxTokens 4200, temp 0.55) y (b) el prompt de media (IR-2→dialecto). El primero decide *qué se dice*; el segundo *qué se ve*. El moat vive en que ambos beben de lo firmado y dejan rastro.

---

## 2. El orden y la jerarquía del ensamblaje

El presupuesto de atención del modelo es finito y no es plano: pesa más el **inicio** (primacía: define la misión), pesa más el **final** (recencia: gobierna la emisión), y el **medio se degrada** ("lost in the middle" — ahí solo sobrevive lo resumible). El ensamblador ordena por esa curva, no por orden de fase.

### 2.1 Las cuatro clases de información y su porqué

**A. SIEMPRE (invariantes del proyecto).** Rol/misión, VOZ (arquetipo+tono+léxico), DOCTRINA (C1/C4/C12), ESENCIA 0.1, IDENTIDAD VISUAL 2.0.5 (si la pieza es visual), y el CONTRATO DE SALIDA (separadores `===SPEC===`/`===TIPS===`/`===QA===`). Porqué: definen de quién es cada token de salida y su legalidad. Sin ellas la pieza es de otra empresa u otra ética. El léxico prohibido y la doctrina son **filtros de emisión**: además de declararse, se re-auditan en `===QA===`.

**B. POR PIEZA (la selección del plan).** PILAR (mensaje+fuerza+modo), GANCHO 2.5 rotado, IDEA del derivado (nota 2.4 — hoy perdida, fix §4.2), PIEZA ANCLA, KEYWORDS. Va **primero tras el rol** (posición 2–4): es el QUÉ decir; el modelo debe leer la misión antes que el contexto. El gancho viaja casi-verbatim ("úsalo o adáptalo") — lo verbatim jamás se resume.

**C. POR FORMATO (contratos de emisión).** `developTypeInstruction(type)` + reglas visuales (espejo del público, texto-nunca-en-imagen, zona limpia, coherencia de personaje, variedad de planos) + schema del SPEC. Va **al final** (recencia): es lo que el modelo ejecuta al emitir, y es lo más largo — ponerlo al inicio ahogaría la misión.

**D. POR MODO DEL PILAR (el dial de venta).** `pillar.mode` decide `offer_mode`: `reforzar` → "LA OFERTA (cítala explícitamente, con sus palabras)" con más presupuesto (400 chars hoy); cualquier otro (agitar/resolve) → "LA SOLUCIÓN (contexto — este pilar NO vende… SOLO el CIERRE apunta a esta puerta)" con menos (300). Porqué: la coherencia oferta↔contenido es doctrinal — un pilar REINFORCE repite las palabras exactas de la oferta; uno RESOLVE agita sin vender y solo el cierre abre la puerta. El modo también sesga la selección de formas retóricas (E1: `MODE_AFFINITY` en hooks-brain).

**E. ELECCIÓN DEL OPERADOR (personalización runtime).** Dos diales por pieza: el **gancho visual** (catálogo `visual-hooks.ts` — moldea el CLIP 1) y la **forma retórica** (catálogo `hooks_catalog` vía suggest-hooks E0→E1→re-rank). Se insertan junto al gancho/formato porque **visten** la apertura. Regla E3 (impresa en el prompt): *la plantilla aporta solo la FORMA; la sustancia — el dolor, los términos, la verdad investigada — viene ÚNICAMENTE del proyecto; los [corchetes] se llenan con ESTE proyecto, nada inventado.* Es la jerarquía DOLOR × FORMA × ESCENA del Cerebro de Ganchos: tres capas que se componen, nunca compiten.

### 2.2 El orden canónico (v2.0.0 actual, con su lógica)

| # | Bloque | Clase | Presupuesto | Porqué esta posición |
|---|---|---|---|---|
| 1 | Rol + misión + "idioma del mercado" | A | fijo | primacía absoluta: quién eres y qué produces |
| 2 | PILAR (mensaje·fuerza·modo) | B | completo | la misión editorial de la pieza |
| 3 | GANCHO 2.5 | B | verbatim | el primer segundo — no se parafrasea la selección |
| 4 | FORMA RETÓRICA elegida + regla E3 | E | completo | viste al gancho; debe leerse pegada a él |
| 5 | AUDIENCIA (avatar) | B/A | resumido (hoy JSON crudo 1600) | el espejo: a quién muestran texto e imagen |
| 6 | PERSONAJE DE MARCA (D-V2) | A | completo | identidad visual persistente; ancla de casting |
| 7 | JOURNEY (matriz 2.2) | B | 1 línea, omisible | temperatura del lector (frío/tibio/caliente) |
| 8 | CONTEXTO TEMPORAL (radar) | B | 1 línea, omisible | ventanas reales; con candado anti-C12 explícito |
| 9 | VOZ (arquetipo·tono·léxico·prohibidos) | A | completo | invariante; (mejora: + promesa pública, §4.4) |
| 10 | KEYWORDS top-8 | B | resumido | anclas léxicas anti-invención |
| 11 | ESENCIA 0.1 (qué es · lo único · why now) | A | truncado 500/200 | el ADN; "el CIERRE nace de aquí" |
| 12 | OFERTA/SOLUCIÓN según modo | D | 400/300 | dosificada por el dial de venta |
| 13 | DIFERENCIADOR (pov_mecanismo) | A | completo | anti-genérico, anti-C4: se ataca por mecanismo |
| 14 | DOCTRINA C4/C12/C1 | A | fijo | filtro previo al contrato de emisión |
| 15 | TIPO (developTypeInstruction) | C | fijo, largo | contrato del entregable — cerca del final |
| 16 | GANCHO VISUAL elegido | E | completo | moldea el CLIP 1; pegado al contrato de video |
| 17 | IDENTIDAD VISUAL (línea 2.0.5) | A | 1 línea densa | paleta/estilo/mood para los image_prompts |
| 18 | Reglas visuales globales (7 bloques) | C | fijo | gobiernan la emisión del SPEC |
| 19 | FORMATO DE SALIDA (separadores) | A/C | fijo | recencia máxima: lo último que lee es cómo emitir |

**Reglas de presupuesto del ensamblador** (normativas): (1) lo **verbatim** (gancho, garantía, léxico, hex de paleta) nunca se resume ni trunca; (2) lo **narrativo** (esencia, oferta, audiencia) se presupuesta con truncado **en frontera de oración y en UN solo punto** (hoy hay doble truncado 600→500 / 300→200 — bug); (3) lo **best-effort** (radar, journey) se omite entero antes que llegar vacío o roto (`filter(null)` — correcto hoy); (4) ningún bloque condicional imprime "n/d" salvo el tono. El problema real del ensamblador hoy **no es falta de ventana** (el statement completo cabe de sobra en el presupuesto) — es que trunca por paranoia heredada y **tira señal ya cargada** (ver §4).

---

## 3. Ejemplo completo armado, campo por campo

**Fixture [EJEMPLO — proyecto ficticio con artefactos "firmados" plausibles]:** producto **"Glaze & Grow"** — sistema de marketing semanal para ceramistas que venden en Etsy. Mercado US (inglés). Pre-lanzamiento.

Entradas de esta pieza:

| Parámetro | Valor | Origen |
|---|---|---|
| avatar_key | `etsy_ceramist` ("Mara", 34) | 0.3 personas |
| pillar_id | `PILLAR_B` — "El ciclo roto: ventas que suben y caen sin que tú lo controles" · `force_attacked=ongoing_pains` · `mode=agitar` | 2.3 pillars |
| derivative_index | 2 → `kind="Reel de Instagram (video)"`, `note="La montaña rusa contada desde la mesa de empaque: mes lleno vs mes vacío"` | 2.4 atomization_map |
| gancho rotado | `hooks[2 % 10] = hooks[2]` (template `problem_agitate`) | 2.5 hook_library |
| hookTemplateId (operador) | «Nobody in [niche] talks about [uncomfortable truth] — and that silence is costing you» · categoría `curiosity_open_loops` · psicología "Curiosity Gap + Loss Aversion" · goal `get_views` | hooks_catalog |
| visualHook (operador) | `falling_drop` — "Caída / algo se derrama" | visual-hooks.ts |
| type | `channelToContentType("Reel de Instagram (video)")` → `video` | prompts.ts |
| offer_mode | "agitar" ∉ {reforzar, reinforce} → **contexto** | brief.ts |

### 3.1 El system prompt ensamblado (como lo recibe el LLM)

Las líneas `⟵` son **anotaciones de este spec** (no viajan en el payload). `[…]` marca texto estático largo comprimido aquí; en producción viaja completo. `⚠` marca pérdidas de señal reales del ensamblador actual.

```text
Eres el redactor + director creativo del Estudio de Papandi. DESARROLLA la idea de una
pieza en su PAQUETE completo desde el brief, en el IDIOMA del mercado (el del gancho/keywords).
⟵ estático (prompts.ts:166). El idioma se INFIERE del gancho — no hay locale canónico (§4.10)

PILAR: La tienda sube y se desploma sin patrón visible; la montaña rusa no es falta de
talento sino falta de sistema — nombramos el ciclo y lo hacemos visible. · fuerza=ongoing_pains · modo=agitar.
⟵ 2.3 pillars.what_it_says + force_attacked + mode (avatar etsy_ceramist) — consumo FUERTE

GANCHO de apertura: "Your best month on Etsy wasn't luck — and your worst month wasn't either."
⟵ 2.5 hook_library.hooks[2].text (rotación derivativeIndex % 10) — FUERTE
⚠ hooks[2].template ("problem_agitate") entra al Brief pero NO se imprime; expires_at/temporality NO se filtran

FORMA RETÓRICA ELEGIDA (del catálogo — el operador la escogió para la APERTURA): «Nobody in
[niche] talks about [uncomfortable truth] — and that silence is costing you» · psicología:
Curiosity Gap + Loss Aversion. RELLÉNALA con EL DOLOR del proyecto (el gancho/pilar de arriba):
la plantilla aporta solo la FORMA; la sustancia (el dolor, los términos, la verdad investigada)
viene ÚNICAMENTE del proyecto. Los [corchetes] se llenan con ESTE proyecto — nada inventado.
⟵ hooks_catalog vía getHooksByIds(hookTemplateId): template + psychology — FUERTE
⚠ goal=get_views existe en el catálogo y guía el re-rank, pero no llega al develop

AUDIENCIA (a QUIÉN le hablas — la imagen debe MOSTRARLA a ella, en su situación real):
{"key":"etsy_ceramist","name":"Mara","age":34,"essence":"Mara, 34, lleva 3 años vendiendo
tazas y vajilla esmaltada en Etsy desde el garaje convertido en taller. Noviembre fue su
mejor mes; febrero casi la hace rendirse…","distinct_because":"…","journey_stage":"consciencia",
"where_we_meet":"Instagram Reels de noche, después de empacar pedidos","forces_of_progress":
{"ongoing_pains":["ventas impredecibles mes a mes","el algoritmo cambia y nadie avisa"],
"triggers":[…],"pull":[…],"anxiety":["que profesionalizar el marketing le robe las horas de tor
⟵ 0.3 personas.avatars[etsy_ceramist] — JSON.stringify().slice(0,1600), DÉBIL
⚠ JSON crudo cortado a mitad de palabra; si avatarKey no matchea cae a avatars[0] EN SILENCIO (§4.3)

PERSONAJE DE MARCA (FIJO del proyecto — es LA protagonista de TODO el contenido visual; úsala
IDÉNTICA en cada clip/imagen Y en cada pieza; NO inventes otra persona): a woman in her mid-30s,
shoulder-length dark wavy hair, clay-dusted denim apron over a cream linen shirt, small ceramic
stud earrings. VOZ del personaje (idéntica siempre): calm warm female voice, early 30s, neutral
American accent, unhurried.
⟵ 2.0.5 brand_visual_identity.character (D-V2) — FUERTE

ETAPA DEL JOURNEY (matriz 2.2, canal «Instagram»): momentos del viaje=despierta → compara ·
qué se publica aquí: Reels de dolor/identidad y carruseles educativos; nada de venta dura.
Habla al lector EN ese momento del viaje (frío=despertar sin vender · tibio=profundizar
confianza · caliente=convertir).
⟵ 2.2 channel_journey_matrix — match por HEURÍSTICA de tokens ("instagram" ⊂ kind); aquí matchea,
   pero "Blog/SEO" vs "artículo" NO matchearía y la línea desaparecería sin aviso (§4.9)

CONTEXTO TEMPORAL (hoy es 2026-07-02, mercado US): ventanas que se acercan — Independence Day
(2026-07-04) · Christmas in July (2026-07-25) · Back-to-school (2026-08-15). Ancla la pieza a
UNA ventana SOLO si conecta natural con el pilar/mensaje; si no, ignóralas por completo.
PROHIBIDO fabricar urgencia con ellas (C12).
⟵ radar (geo 0.1 + project_events), best-effort — DÉBIL
⚠ sin eventos en 60 días esta línea entera desaparece Y CON ELLA LA FECHA (bug "February en junio", §4.1)

VOZ: arquetipo everyman; tono directa, cálida, concreta, sin humo, de taller. Léxico: kiln,
glaze, made-to-order, slow craft, studio day. PROHIBIDO: passive income, hustle, scale,
6-figures, hack, girlboss, empire.
⟵ 2.0 brand_voice (archetype/tone/lexicon) — FUERTE
⚠ brand_promise_public y consistency_rules_plain NO se imprimen (§4.4)

KEYWORDS REALES (ancla, NO inventes términos): etsy sales dropped suddenly · why are my etsy
sales so slow · etsy sales down 2026 · how to get consistent sales on etsy · etsy algorithm
changes · handmade business slow season · etsy shop views but no sales · pottery business tips.
⟵ 0.2 demand_quantification.keyword_intents ordenadas measured-first, slice(0,8), SOLO .keyword
⚠ volumen/mes, KD e intent (lo pagado a DataForSEO) se descartan antes del prompt (§4.8)

ESENCIA DE LA EMPRESA (el ADN — la pieza debe respirarlo y el CIERRE nace de aquí, jamás de un
genérico): QUÉ ES: Glaze & Grow — sistema de marketing semanal para ceramistas que venden en
Etsy: cada lunes, tres movimientos concretos leídos de las señales de TU tienda, sin volverte
marketer full-time — LO ÚNICO: Hecho para cerámica: habla kiln, glaze y made-to-order, no
dropshipping · Semana a semana: 3 acciones, no un curso de 40 horas — POR QUÉ AHORA: El
algoritmo 2026 de Etsy premia señales constantes; las tiendas que publican en ciclos aleatorio
⟵ 0.1 business_context (refined_idea/differentiators accepted/why_now) — DÉBIL
⚠ doble truncado 600→500 / 300→200: el why_now se corta a mitad de frase (§4.6/§2.2 regla 2)

LA SOLUCIÓN (contexto — este pilar NO vende: el cuerpo agita/educa SIN mencionar el producto;
SOLO el CIERRE apunta a esta puerta en una frase específica de la ESENCIA — nunca "follow for
more" ni un CTA genérico): **Glaze & Grow Weekly** — for ceramic artists on Etsy who are done
with feast-or-famine months. Every Monday: three moves built from YOUR shop's signals (views,
favorites, conversion): what to post, what to fix, what to let g
⟵ 1.4 offer_statement.markdown, modo CONTEXTO → slice(0,300) — DÉBIL
⚠ la página de oferta mide ~2.000 chars: garantía, why-now y CTA quedan fuera SIEMPRE (§4.6);
   displacement_framing 1.3 ("deja de X" + costo de seguir igual) — el ángulo natural del modo
   agitar — no existe para el develop

DIFERENCIADOR (POV/mecanismo, anti-genérico): No es otro curso: es un ritmo semanal que lee
las señales de TU tienda y te dice qué publicar — el sistema, no la inspiración.
⟵ 1.4 offer_spec.distinct_because — FUERTE

DOCTRINA (producto PRE-LANZAMIENTO, sin clientes): C4 PROHIBIDO testimonios/casos/prueba
social/cifras inventadas → ataca por MECANISMO. C12 sin urgencia/escasez fabricada. C1 valor
por FUNCIONALIDAD, no comparación.
⟵ estático (prompts.ts:195)

TIPO = REEL/VIDEO corto de 15-35 SEGUNDOS TOTALES (techo duro…). La PIEZA = el GUION por
CLIPS: 3-5 clips numerados con su rango de tiempo… […texto íntegro de
developTypeInstruction("video"), ~350 palabras estáticas: tope ≈2.5 palabras/segundo hablado ·
mismo protagonista descrito IDÉNTICO por clip ("The SAME woman…") · narración como VO entre
comillas dentro del prompt (audio nativo) · voz descrita idéntica por clip · MOVIMIENTO
OBLIGATORIO (acción física en CADA clip, prohibido sujeto quieto) · cámara con golpe, no paseo
· la cara comunica antes de hablar · CLIP 1 = acción que interrumpe en el PRIMER segundo ·
primer frame apilado (máx 3 elementos) · overlay gráfico lo añade el editor, no la IA · misma
paleta/luz; 9:16; zona limpia…]
⟵ estático por formato (prompts.ts:developTypeInstruction) — la plantilla del canal 2.4
   (channel_template) se calcula en el Brief pero NO se fusiona aquí (§4.2)
⚠ la duración por clip queda a merced de que el LLM escriba "N seconds" en la prosa (§4.10)

GANCHO VISUAL ELEGIDO POR EL OPERADOR — «Caída / algo se derrama (falling hook)»: En el primer
segundo algo CAE o se derrama frente a cámara — un objeto del mundo de la protagonista se
resbala de sus manos, una pila se desploma, un líquido se vuelca. Ella reacciona; la escena
continúa desde esa interrupción. MOLDEA EL CLIP 1 con esta mecánica EXACTA, adaptada al mundo
real de la AUDIENCIA (sus objetos, su espacio, su oficio), con la acción ocurriendo en el
PRIMER segundo. El hook_text_overlay y la primera línea hablada se montan SOBRE esta acción.
⟵ catálogo visual-hooks.ts[falling_drop].name + mechanic — FUERTE (best_for no viaja, correcto:
   ya sirvió para elegir)

IDENTIDAD VISUAL (usa SIEMPRE esta paleta/estilo/mood en los image_prompts; NO inventes otra):
estilo=editorial documentary photography, soft natural window light, subtle film grain ·
paleta=warm terracotta #C4573A, glaze cream #F2E9DC, kiln charcoal #2E2B28, sage celadon
#9DB5A0 · mood=honest, warm, grounded, quietly confident · composición=negative space, subject
off-center, clean upper third for overlays · motivos=hands at work, raw clay texture, glazed surfaces.
⟵ 2.0.5 vía visualIdentityBriefLine — FUERTE
⚠ do[]/dont[]/typography NO llegan al develop (dont solo se pega DESPUÉS en brandSuffix de
   generación): el redactor escribe image_prompts sin conocer los vetos (§4 nota)

REGLA: en piezas VISUALES la PIEZA es BREVE… Los image_prompts / video_prompt son EL
ENTREGABLE… CRÍTICO — EL TEXTO NO VA EN LA IMAGEN… PRINCIPIO #1 DE LA IMAGEN — ES UN ESPEJO
DEL PÚBLICO, NO DECORACIÓN NI EL LOGO… COHERENCIA DE PERSONAJE… VARIEDAD DE PLANOS…
SUPERFICIES CON TEXTO… Los prompts son PROSA descriptiva (no JSON)…
⟵ 8 bloques estáticos de doctrina visual (prompts.ts:201-208), íntegros en producción

FORMATO DE SALIDA (separadores EXACTOS, en este orden):
[la PIEZA en markdown]
===SPEC===
[SOLO un JSON con el design_spec; {} si no lleva visual]: {"subject":"","scene":"","camera":
{"angle":"","shot":"","lens_dof":"","movement":""},"lighting":"","style":"","composition":"",
"mood":"","palette":"","output":{"aspect_ratio":""},"image_prompts":["..."],"video_prompts":
["<un prompt por clip>"],"hook_text_overlay":""}
===TIPS===
[tips de publicación: mejor ventana + cómo/dónde, 1-2 frases]
===QA===
[SOLO un JSON]: {"removed":[{"what":"","why":"C4|C12|C1|voz|estructura"}],"notes":"<1 frase>"}
⟵ estático — el contrato de emisión, en posición de recencia máxima
```

**Mensaje user:** `Desarrolla la idea ahora: Reel de Instagram (video) (tipo video) del pilar "El ciclo roto: ventas que suben y caen sin que tú lo controles".`
⚠ La `note` del derivado ("la montaña rusa desde la mesa de empaque…") — LA idea planificada en 2.4 — no está ni en el system ni en el user: el modelo improvisa la idea desde pilar+kind (§4.2).

### 3.2 La segunda compilación: IR-2 → dialecto de motor

El develop emite (entre otros) `video_prompts` — un prompt por clip, con la duración en prosa. Clip 1 [EJEMPLO de salida esperada]:

> *"A woman in her mid-30s, shoulder-length dark wavy hair, clay-dusted denim apron over a cream linen shirt, at a wooden packing table in her home pottery studio. In the very first second a stack of cardboard shipping boxes TOPPLES off the table and a glazed terracotta mug slips from her hands — she catches it against her apron, eyes wide, sharp intake of breath, then looks straight into the lens with a knowing, frustrated half-smile. Handheld punch-in to her face as she says: "Nobody in pottery talks about this." Calm warm female voice, early 30s, neutral American accent, unhurried. Soft natural window light, editorial documentary photography, subtle film grain, warm terracotta and glaze cream palette, charcoal shadows. Clean upper third for overlay text. Vertical 9:16, 5 seconds."*

⟵ obsérvese la composición de capas en un solo párrafo: personaje D-V2 (2.0.5) + gancho visual `falling_drop` (catálogo) + forma retórica rellenada con el dolor (E3) + voz del personaje + identidad visual + zona limpia + "5 seconds" (la regex de `clipSeconds` depende de esa mención).

Con 3 clips de 5s, `planGeneration("kling-3.0", …)` empaqueta greedy ≤15s → **UN job** (misma voz/cara), y `falVideoBody` emite el dialecto Kling:

```json
{ "multi_prompt": [ {"prompt":"<clip 1>","duration":"5"}, {"prompt":"<clip 2>","duration":"5"},
    {"prompt":"<clip 3>","duration":"5"} ],
  "aspect_ratio": "9:16", "generate_audio": true, "shot_type": "customize" }
```
Costo visible antes de generar: 15s × $0.168 = **$2.52**. El mismo IR-2 en **Veo 3.1** compila distinto: 5s no es duración válida → `snapSeconds` a 6s, **tres jobs** separados (`duration:"6s"`, 720p), 18s × $0.40 = $7.20, y 1:1 se convertiría a 9:16. En **Seedance**: tres jobs de 5s, prompt único cada uno. `hook_text_overlay` ("Nobody in pottery talks about this") **no viaja** a ningún dialecto: es capa del editor.

---

## 4. Los 10 fixes priorizados del ensamblador

Criterio de orden: (bugs que rompen confianza del usuario) > (señal ya cargada que se tira — costo casi cero) > (identidad/calidad) > (determinismo de la capa media). Rutas relativas a `C:\Users\prett\Documents\sandia-marketing`.

1. **Integridad temporal de punta a punta.** Filtrar `expires_at < hoy` y priorizar seasonal con ventana abierta en la rotación de ganchos (`lib/estudio/brief.ts:62`); emitir SIEMPRE "hoy es {ISO}" con rama else en `produce/route.ts:163` (como ya hace step-proposal); aceptar `publish_date` del slot del calendario como ancla en vez de `todayISO`; backfill de `temporality` en bibliotecas pre-M5 + jubilación/regeneración de vencidos (`buildHookRegenSystem` ya existe). **Impacto:** mata la familia completa del bug "February en junio" — el error más visible y el que más confianza destruye (una pieza fuera de temporada delata al robot).
2. **Imprimir los huérfanos que el Brief ya carga.** Cuatro líneas en `lib/estudio/prompts.ts`: `IDEA DE LA PIEZA: {derivative.note}` · `GANCHO (molde {hook.template})` · `PIEZA ANCLA: {anchor_title}` · fusionar `channel_template.structure/rules` dentro de `developTypeInstruction(type, template)`. **Impacto:** la pieza desarrolla LA idea planificada en 2.4 (hoy improvisa desde pilar+kind), honra el molde retórico del gancho y cruza CTA con su pieza madre. El fix más barato de toda la lista: los datos ya viajan hasta un milímetro del prompt.
3. **AUDIENCIA estructurada + guard de avatar.** Reemplazar `JSON.stringify(avatar).slice(0,1600)` (`produce/route.ts:130`) por proyección de campos (essence, where_we_meet, 3 ongoing_pains, 2 anxiety, habit — como la `forcesLine` de step-proposal); 409/warn cuando `avatarKey` no matchea en vez de caer a `avatars[0]` en silencio. **Impacto:** el "espejo del público" (principio #1 de la imagen) recibe señal limpia sin llaves ni cortes a mitad de objeto; elimina piezas generadas para el avatar equivocado sin aviso.
4. **VOZ completa: promesa + reglas testeables.** Añadir `brand_promise_public` a la línea VOZ y `consistency_rules_plain` a la sección `===QA===`. **Impacto:** los cierres rematan en la promesa firmada (hoy salen genéricos) y el QA audita contra reglas verificables por máquina (máx un "!", titulares ≤12 palabras, números con fuente) en vez de solo C4/C12/C1.
5. **La orden de trabajo de Fase 1 llega a Producción.** Línea nueva: `SUEÑO DEL COMPRADOR: {dream_statement} · OBJECIÓN #1 A ATACAR: {weakestAxisOf} — {rationale}` desde `value_equations` (1.1). **Impacto:** cada pieza conoce su apertura aspiracional y la objeción que la ecuación identificó como cuello de botella — hoy la Fase 1 analítica es casi invisible para el develop; esto la vuelve ejecutable pieza a pieza.
6. **Oferta sin slice ciego + desplazamiento.** Extraer secciones estructuradas del `offer_statement` (para quién / qué hace / garantía / why-now / CTA) y dosificarlas por modo — garantía VERBATIM solo en `reforzar`; en modo agitar/contexto inyectar `displacement_framing.replacement_narrative + cost_of_continuing_current_path` (1.3) como línea propia; un solo punto de truncado con corte en frontera de oración (elimina el doble corte 600/500–300/200). **Impacto:** el modo contexto gana su ángulo natural ("deja de X" + costo de no actuar — exactamente lo que pide un pilar de agitación) y el modo reforzar deja de perder garantía y CTA por un `slice(0,400)`.
7. **Números con fuente.** Rotar 2–3 `verified_points` (claim+value+source_name) y los `refuted_assumptions` de 0.2 al develop. **Impacto:** las plantillas `stat_lead`/`contrarian`/`myth_bust` dejan de elegir entre inventar cifras (violación glass-box y de la regla "números con fuente") u omitirlas; contrarianismo con base investigada real.
8. **Keywords con su medición.** Serializar `"kw" [vol/mes real · KD · intent]` (como ya hace step-proposal en `route.ts:117-125`) y filtrar por afinidad al journey/awareness de la pieza. **Impacto:** lo pagado a DataForSEO por fin llega al redactor; títulos y SEO anclados a demanda medida, no a 8 strings desnudos.
9. **Plan ejecutable por clave, no por heurística.** Guardar `channel_key` y `awareness_target` en cada derivado al generar 2.4 (validando el reparto contra `content_mix.target_mix` al firmar); matchear la matriz 2.2 por key (loggear cuando no hay match); `channels[].cta_destination` (URL/handle real, consumiendo el dominio elegido en 0.1) inyectado en el cierre. **Impacto:** el journey deja de perderse cuando "Blog/SEO" no comparte token con "artículo"; el mix firmado se vuelve ejecutable pieza a pieza; el CTA pasa de retóricamente específico a operativamente real.
10. **Determinismo de la capa media.** `duration_seconds` estructurado por clip en `===SPEC===` (regex de prosa solo como fallback); iterar TODOS los `image_prompts` en la ruta de carrusel (hoy `serializeForGateway` toma solo el primero — los slides 2..6 no se generan por esa vía); derivar `aspect_ratio` del canal del derivado (reel/story=9:16, feed=1:1/4:5) y validarlo en `parseDevelop`; parametrizar `marketIsEnglish` (desde locale canónico del proyecto, fijado al firmar launch_focus/1.4) y `preLaunch` (flag de estado) en hooks-brain; imprimir `psychology` por candidato en el re-rank y rellenar hasta 5 picks. **Impacto:** duración, ratio, idioma y selección de formas dejan de ser suposiciones hardcodeadas del dialecto; el presupuesto D-V4 se vuelve exacto y el sistema sobrevive al primer proyecto hispano o post-lanzamiento sin tocar código.

**Y quitar (higiene del IR):** dejar de generar y marcar deprecated `perceived_value_usd`+`comparable` (doctrina anti-comparación — que ningún prompt futuro los recoja por accidente), `derivatives_count`/`derivatives_summary` y `channels_declared` (derivables — dual-homing interno), `scarcity.type` (campo persuasivo muerto sin candado ético), y las copias embebidas `step_thread.pre.price_research`/`cost_breakdown` (referenciar `product_economics`). Un compilador con campos muertos en la fuente termina compilándolos.

---

## 5. Opinión honesta: ¿el ensamblador ES el producto?

**Sí en lo esencial — con cuatro matices que importan.**

**Donde la tesis acierta.** El moat de Papandi no puede ser la llamada al LLM (commodity), ni los modelos de media (fal.ai por debajo, intercambiables — el propio código admite que precios y endpoints "caducan rápido"), ni las plantillas (copiables en una tarde). Lo único que un competidor no puede replicar prompteando ChatGPT es la **cadena de suministro de contexto firmado**: semanas de decisiones co-creadas, corregidas por humano, con evidencia citada y gates éticos, compiladas en cada pieza. El ensamblador es el punto exacto donde el glass-box deja de ser filosofía y se vuelve ejecutable — donde "esta pieza dice esto PORQUE firmaste aquello" es literalmente trazable (`insertPiece` persiste brief + system + spec). Eso conecta con el hallazgo maestro del research de mercado: lo que el mercado rechaza es lo no-verificable. El ensamblador es el mecanismo de verificabilidad. Como doctrina de inversión, la tesis es correcta: **ninguna otra hora de trabajo rinde más calidad por pieza que una hora en esta capa** — la auditoría lo demuestra: los artefactos capturan oro y el prompt tira cerca de la mitad (la nota de la idea, la promesa de marca, las estadísticas con fuente, la ecuación de valor entera).

**Matiz 1 — el compilador vale lo que su fuente.** Un ensamblador perfecto sobre fases vacías produce basura elegante; las fases firmadas sin ensamblador son un PDF bonito. El producto es el **par inseparable** (fuente firmada ↔ compilador). La formulación precisa sería: *el producto es el sistema cuya fuente de verdad son decisiones humanas firmadas y cuyo output es media; el ensamblador es su compilador.* Venderlo como "ensamblador de prompts" a secas invita a compararlo con prompt-tools de $9/mes; lo defendible es la cadena completa.

**Matiz 2 — hoy es la capa más floja de su propia tesis.** La auditoría muestra que el eslabón supuestamente central es el que más señal pierde (huérfanos del Brief, truncados ciegos, JSON crudo, heurísticas de tokens, fecha condicional). Es decir: la tesis es direccionalmente correcta y **operativamente aspiracional**. Eso no la debilita — la confirma: si el ensamblador no fuera el producto, sus gaps no dolerían tanto en la calidad final. La lista del §4 es, en la práctica, el backlog de producto.

**Matiz 3 — el ensamblador invisible no se puede cobrar.** El usuario no experimenta el compilador; experimenta la pieza y el porqué. La anotación del §3 ("de dónde sale cada bloque") debería ser **feature de UI**, no solo spec interno: mostrar la procedencia de cada bloque del prompt convierte el moat en algo legible, auditable y demo-able — y es el único claim que ningún wrapper puede imitar. La procedencia es el artefacto vendible del ensamblador.

**Matiz 4 — compilador sin profiler no aprende.** Falta el loop de rendimiento (gap "faltante" #3): sin métricas por pieza/gancho, el ensamblador no puede saber qué ensamblaje convierte, y "los ganadores se quedan, los que no convierten se jubilan con datos" es una promesa sin datos. Igual que los few-shot de piezas aprobadas (el mecanismo más barato de fidelidad de voz), el loop es parte del compilador, no un añadido de Fase 4. El producto se completa cuando el ciclo cierra: firmar → compilar → publicar → medir → recompilar mejor.

**Veredicto:** el ensamblador es el corazón del producto y el lugar correcto donde concentrar el esfuerzo — pero es el corazón, no el cuerpo. El producto completo es: fuente firmada + compilador de dos etapas + procedencia visible + loop de medición. De esas cuatro, hoy la más rezagada es precisamente la que el operador señala como el producto real; los 10 fixes del §4 son el camino más corto para que la tesis sea verdad en producción, no solo en arquitectura.


---

# Anexo A — Consumo del ensamblador (qué usa hoy el develop)

| # | Fuente (artefacto.campo) | Cómo entra | Fuerza |
|---|---|---|---|
| 1 | brand_voice (2.0).archetype_primary | produce/route.ts safeParse obligatorio (409 si falta) → brief.voice.archetype → línea VOZ del develop, entero | fuerte |
| 2 | brand_voice (2.0).tone_descriptors | join(', ') completo en línea VOZ; si vacío imprime 'n/d' | fuerte |
| 3 | brand_voice (2.0).lexicon.preferred_terms | join completo, SOLO si length>0 (línea 'Léxico:') | fuerte |
| 4 | brand_voice (2.0).lexicon.prohibited_terms | join completo, SOLO si length>0 (línea 'PROHIBIDO:') | fuerte |
| 5 | pillars (2.3).pillar{what_it_says|name, force_attacked, mode} | SOLO el pilar con id==pillarId (find); message=what_it_says con fallback a name; línea PILAR completa; mode además decide offer_mode (reforzar vs contexto) vía set {reforzar,reinforce} | fuerte |
| 6 | atomization_map (2.4).derivatives[derivativeIndex].kind | SOLO ese derivado; kind → channelToContentType(regex) → developTypeInstruction estática + mensaje user ('Desarrolla la idea ahora: {kind}'); también decide el match del journey | fuerte |
| 7 | atomization_map (2.4).derivatives[derivativeIndex].note | va al objeto brief.derivative.note pero buildDevelopSystem NUNCA lo imprime — la nota de la idea NO llega al prompt del develop (sí llega a suggest-hooks como 'LA PIEZA') | débil |
| 8 | atomization_map (2.4).long_form.title_working|asset_id | solo como anchor_ref al persistir la pieza (insertPiece); NO se inyecta en el system del develop | débil |
| 9 | hook_library (2.5).hooks[pillar].text | filtra por pillar y rota UNO solo: hooks[derivativeIndex % n] → línea 'GANCHO de apertura' completa; también es el 'pain' primario en suggest-hooks | fuerte |
| 10 | hook_library (2.5).hooks[pillar].template | entra al brief (hook.template) pero buildDevelopSystem no lo imprime — solo lo usan buildDraft/buildProduce legacy; información perdida en develop | débil |
| 11 | offer_statement (1.4).markdown | prioridad sobre offer_spec.name como offer_words; truncado a slice(0,400) en modo reforzar o slice(0,300) en modo contexto | débil |
| 12 | offer_spec (1.4).name | solo fallback si no hay statement_md; mismo truncado 400/300 | débil |
| 13 | offer_spec (1.4).distinct_because | → pov_mecanismo, línea DIFERENCIADOR entera sin truncar, condicional a existir | fuerte |
| 14 | demand_quantification (0.2).keyword_intents | condicional a safeParse OK (si el schema falla → [] silencioso); ordena measured-first + monthly_searches desc, slice(0,8), y SOLO conserva .keyword — intent y volumen se descartan del prompt | débil |
| 15 | business_context (0.1).refined_idea|idea | doble truncado: slice(0,600) en route + slice(0,500) al imprimir 'QUÉ ES' en la línea ESENCIA; sin 0.1 firmado essence=null y la línea desaparece | débil |
| 16 | business_context (0.1).why_now | doble truncado: slice(0,300) en route + slice(0,200) en 'POR QUÉ AHORA' | débil |
| 17 | business_context (0.1).differentiators | solo state==='accepted' (o sin state), label+description concatenados, slice(0,4), join completo en 'LO ÚNICO' | débil |
| 18 | personas (0.3).avatars[avatarKey] | find por key con fallback al PRIMERO de la lista; el objeto entero JSON.stringify().slice(0,1600) → línea AUDIENCIA (JSON crudo truncado a 1600 chars) | débil |
| 19 | channel_journey_matrix (2.2).channels[match].journey_moments + what_gets_published | condicional triple: safeParse OK + canal enabled + heurística de match (tokens del label >2 chars contenidos en kind.toLowerCase()) — si el label no comparte token con el kind, el journey se pierde en silencio | débil |
| 20 | radar (geo + project_events) | best-effort try/catch (falla → null sin avisar); upcomingEvents(60 días).slice(0,4), solo name+date por evento → línea CONTEXTO TEMPORAL | débil |
| 21 | brand_visual_identity (2.0.5).style/palette/mood/composition/motifs | visualIdentityBriefLine: línea única completa (paleta con name+hex), condicional a que exista style o palette; do/dont/typography/reference_image_url NO entran al develop (dont solo vive en brandSuffix de generación) | fuerte |
| 22 | brand_visual_identity (2.0.5).character.description + .voice | línea PERSONAJE DE MARCA completa sin truncar, condicional a description no vacía (coerceVisualIdentity) | fuerte |
| 23 | visual-hooks.ts catálogo estático[visualHookId].name + mechanic | solo si el operador eligió id válido (getVisualHook, si no null); inyecta name+mechanic completos; best_for NO se inyecta | fuerte |
| 24 | hooks_catalog[hookTemplateId].template + psychology | solo el PRIMERO de getHooksByIds([id]) y solo si el operador lo eligió; línea FORMA RETÓRICA completa (psychology condicional) | fuerte |
| 25 | suggest-hooks: pain = hook2.5.text ?? pillar.what_it_says ?? pillar.name | cadena de fallbacks; UN solo gancho por rotación derivativeIndex % n; entero en 'EL DOLOR' | fuerte |
| 26 | suggest-hooks: pillar.mode + force_attacked | E1 determinista: MODE_AFFINITY (fallback DEFAULT si modo desconocido) + máx 1 categoría extra por fuerza; E0 SQL cap 40 candidatos (queryHookCandidates) | fuerte |
| 27 | suggest-hooks: candidates[].psychology | RerankCandidate lo tipa pero buildHookRerankSystem NO lo imprime en la lista (solo id+category+goal+template) — el LLM re-rankea sin la psicología | débil |
| 28 | hooks-brain: excludeLanguageBound / preLaunch | la ruta nunca pasa preLaunch ni marketIsEnglish → defaults duros: siempre excluye social-proof/urgencia y NUNCA excluye language_bound (asume mercado inglés, no lo deriva del proyecto) | débil |
| 29 | suggest-hooks: parseHookSuggestions | extrae primer '{'..último '}', slice(0,5), y filtra ids que no existan en DB (picks inválidos se caen en silencio, puede devolver <5) | débil |
| 30 | design_spec.image_prompts (generación imagen) | serializeForGateway toma SOLO el primer prompt no vacío ((spec.image_prompts??[]).map(clean).find(Boolean)); los demás slides no pasan por esta vía; fallback a composeImagePrompt determinista (subject→scene→composition→camera→lighting→style→mood→palette) | débil |
| 31 | design_spec.video_prompts (generación video) | videoClipPrompts usa TODOS los clips (trim+filter vacíos); fallback legacy a video_prompt único o al compositor; fuerte para multi-clip | fuerte |
| 32 | design_spec.output.aspect_ratio | default '1:1' si falta/vacío; falVideoBody lo clampa a {16:9,9:16,1:1} → si no, 9:16; Veo convierte 1:1→9:16 | débil |
| 33 | video_prompts[i] → segundos del clip | clipSeconds: regex '(\d+) seconds|segundos' DENTRO de la prosa del prompt; si el prompt no lo dice → 6s fijo; clamp 2-15; snap a 4/6/8 solo en Veo; packing greedy ≤15s solo Kling (multi_prompt) | débil |
| 34 | design_spec.hook_text_overlay | NO viaja al gateway (por diseño: es capa overlay del editor, nunca renderizado por la IA); solo persiste en el spec | débil |
| 35 | design_spec.camera.movement + subject/scene/... (video fallback) | solo se usan si falta video_prompt/video_prompts (composeVideoPrompt); con prompts ricos del LLM los campos canónicos quedan sin leer | débil |

**Notas de pipeline:**

- Hallazgo mayor: buildDevelopSystem NO imprime brief.derivative.note ni brief.channel_template (label/structure/rules) ni brief.anchor_title ni hook.template — todos entran al objeto Brief pero solo los prompts legacy (buildDraftSystem/buildProduceSystem) los usan. El develop sustituye el formato por developTypeInstruction(type) estática; la nota de la idea (2.4) y la plantilla del canal se pierden del prompt.
- Doble truncado de la esencia 0.1: route.ts corta idea a 600 / why_now a 300 y buildDevelopSystem vuelve a cortar a 500 / 200 — el segundo corte es el efectivo.
- AUDIENCIA es el avatar completo como JSON.stringify crudo cortado a 1600 chars — sin selección de campos; si avatarKey no matchea usa avatars[0] en silencio.
- Journey (2.2) depende de una heurística de tokens label↔kind: si el label del canal no comparte ningún token >2 chars con el kind del derivado, la etapa del journey no se inyecta y nadie lo reporta.
- Keywords 0.2: solo sobreviven 8 strings; intent y monthly_searches (lo medido con DataForSEO) se descartan antes del prompt.
- suggest-hooks: excludeLanguageBound siempre false y preLaunch siempre true por defaults no parametrizados desde el proyecto; psychology existe en los candidatos pero no se imprime en el system del re-rank.
- Gateway imagen: serializeForGateway solo toma el primer image_prompt no vacío — la generación por-slide de un carrusel debe iterar por fuera de esta función o los slides 2..6 no se generan.
- Video: los segundos de cada clip se parsean con regex de la prosa del prompt ('N seconds'); prompt sin duración explícita = 6s asumidos; el radar temporal y el journey son best-effort (nunca bloquean, fallan en silencio).
- Cadena completa verificada: produce/route.ts carga 10 artefactos (4 obligatorios: 2.0/2.3/2.4/2.5 con 409) → buildBrief (puro) → buildDevelopSystem + extras → 1 llamada LLM (estudio_develop@v2.0.0, maxTokens 4200, temp 0.55) → parseDevelop separa PIEZA/===SPEC===/===TIPS===/===QA=== → insertPiece persiste brief+system+design_spec; la media real va después por serialize.ts/video-routing.ts.

---

# Anexo B — Gaps (cruce creado × consumido)

## Creado sin usar (18)

- **hook_library (2.5).hooks[].temporality / valid_window / expires_at / event_ref** _(prioridad: alta)_ — Es LA causa del bug 'February en junio': step-proposal M5 (app/api/phase2/step-proposal/route.ts:180-198) ya escribe estos campos al crear los ganchos, pero la rotación en buildBrief (C:\Users\prett\Documents\sandia-marketing\lib\estudio\brief.ts:62-63) filtra SOLO por pillar — un gancho seasonal vencido sigue entrando al develop. Filtrar expires_at < hoy y priorizar seasonal con ventana abierta elimina piezas fuera de temporada sin tocar la captura.
- **value_equations (1.1).equations[].dream_statement + weakestAxisOf + rationales de los 4 ejes** _(prioridad: alta)_ — El 'hook maestro' (la promesa en el punto de vista del cliente) y la ORDEN DE TRABAJO (el eje débil = la objeción #1 que todo contenido debe atacar) nunca llegan al develop. Una línea 'SUEÑO: ... / EJE DÉBIL A ATACAR: likelihood — {rationale}' daría a cada pieza su apertura aspiracional y su objeción a cerrar.
- **brand_voice (2.0).brand_promise_public** _(prioridad: alta)_ — La columna vertebral del copy (headline, bio, cierres). buildDevelopSystem imprime arquetipo/tono/léxico (prompts.ts:178) pero NO la promesa — los cierres salen genéricos en vez de rematar siempre en la promesa firmada.
- **brand_voice (2.0).consistency_rules_plain** _(prioridad: alta)_ — El develop tiene sección ===QA=== (prompts.ts:215-216) pero audita solo contra C4/C12/C1: las 5 reglas testeables (máx un '!', titulares ≤12 palabras, números con fuente, ≥1 término preferido) no se inyectan. Es el fix más barato con impacto directo en calidad publicable.
- **risk_urgency (1.3).displacement_framing.replacement_narrative + cost_of_continuing_current_path** _(prioridad: alta)_ — Un ángulo de contenido completo ('deja de hacer X' + costo de no actuar = hooks de dolor y secciones why-now). Hoy solo sobrevive si casualmente cupo en los primeros 400 chars del offer_statement truncado.
- **demand_quantification (0.2).verified_points[] (claim, value, source_name)** _(prioridad: alta)_ — El catálogo tiene plantilla stat_lead pero NINGUNA estadística citable con fuente llega al prompt → el modelo omite datos o los inventa (violando glass-box y la regla 'números con fuente'). 2-3 verified_points por pieza darían hooks con números reales.
- **offer_stack (1.2).bonuses[].specific_target (+ name/description accepted)** _(prioridad: alta)_ — El mapa objeción→respuesta ('un post por freno'): cada pieza sabría qué freno concreto desactiva y con qué bonus se responde. Hoy los bonuses no existen para el develop salvo lo que quepa en el slice del statement.
- **demand_quantification (0.2).refuted_assumptions[]** _(prioridad: media)_ — Combustible directo de las plantillas contrarian y myth_bust con base investigada real ('creíamos X, los datos dicen Y') en vez de contrarianismo inventado.
- **icp (0.2.5).must_have_filters + deal_breakers (accepted)** _(prioridad: media)_ — Material literal para direct_callout ('esto es para ti si… / NO es para ti si…') y para redactar piezas que repelen al cliente equivocado sin ofender.
- **personas (0.3).persona.self_image + persona.jtbd + persona.pains[]** _(prioridad: media)_ — Llegan al planning (step-proposal:147) pero NO al develop; el JSON del avatar truncado a 1600 chars puede cortarlos. El espejo de autoimagen convierte más que describir el producto — merece línea propia estructurada.
- **risk_urgency (1.3).risk_reversal.statement (garantía verbatim)** _(prioridad: media)_ — En piezas de cierre (most_aware/reforzar) la garantía es el ataque al eje probabilidad y debe ir VERBATIM; casi nunca sobrevive el slice(0,400) del statement.
- **cancha (0.4).rivals[].angle + errc (eliminar/reducir/incrementar/crear)** _(prioridad: media)_ — angle dice qué mensaje ya está ocupado (no repetir al rival); ERRC son 4 ángulos contrarian listos ('por qué eliminamos X que todos cobran'). El develop hoy compite a ciegas del mapa competitivo.
- **business_context (0.1).sales_cycle + marketing_objective.primary/primary_kpi** _(prioridad: media)_ — Impulsivo pide claridad y momento; reflexivo pide prueba y educación — cambia el tipo de pieza. El objetivo (ventas/leads/awareness) calibra la agresividad del CTA. Nada de esto llega al prompt de media.
- **content_mix (2.1).target_mix** _(prioridad: media)_ — La pieza no sabe a qué momento de conciencia sirve; el único proxy es el journey por heurística de tokens (frágil). Declarar 'esta pieza es problem_aware' alinearía tono, profundidad y CTA con el presupuesto editorial firmado.
- **brand_visual_identity (2.0.5).do[] / dont[] / typography** _(prioridad: media)_ — El develop ESCRIBE los image_prompts sin conocer los vetos (dont solo se añade después en brandSuffix de generación) → prompts que chocan con el Avoid. typography nunca llega al editor de overlay pese a que el gancho ES texto-overlay (doctrina §2.7).
- **strategies (1.x).strategies[].demand_type** _(prioridad: media)_ — capture vs generate cambia el tipo de gancho (SEO/comparativa vs interrupción/educación). Lo consume el planning 2.x pero el develop no lo ve; una línea lo alinearía con la estrategia firmada.
- **offer_spec (1.4).pricing.price_anchor.anchor_statement** _(prioridad: baja)_ — Si la pieza menciona precio, el framing firmado del número no está en el prompt — cada pieza reinventa cómo enmarcar la única cifra permitida.
- **business_context (0.1).deep_questions[].answer** _(prioridad: baja)_ — Matices del negocio en palabras del fundador (por qué, para quién, cómo) que no viven en ningún otro campo; cantera de frases auténticas para storytelling de origen.

## Usado débil (15)

- **atomization_map (2.4).derivatives[].note** — problema: Entra al Brief (lib/estudio/brief.ts:76) pero buildDevelopSystem NUNCA la imprime — LA IDEA concreta de la pieza se pierde y el modelo desarrolla solo desde kind+pilar (sí llega a suggest-hooks, no al develop).
  - fix: Añadir en C:\Users\prett\Documents\sandia-marketing\lib\estudio\prompts.ts (junto a la línea PILAR) `IDEA DE LA PIEZA: ${brief.derivative.note}` cuando exista.
- **produce: radar → CONTEXTO TEMPORAL** — problema: La fecha de hoy solo se inyecta si hay eventos en 60 días (produce/route.ts:163 `if (next.length)`); sin eventos o con error del radar el prompt queda SIN fecha → segunda mitad del bug 'February en junio'. step-proposal sí tiene rama else con 'HOY ES' (route.ts:98); produce no.
  - fix: Emitir SIEMPRE `hoy es ${todayISO}` (rama else como step-proposal:98) y loggear el catch en vez de silenciar.
- **brief.channel_template (pickTemplate(kind))** — problema: Se calcula (brief.ts:77) y jamás se imprime; el develop usa developTypeInstruction(type) estática → un reel de IG y un email reciben la misma instrucción de formato.
  - fix: Imprimir label/structure/rules de la plantilla en buildDevelopSystem, o fusionarlas dentro de developTypeInstruction(type, template).
- **offer_statement (1.4).markdown** — problema: slice(0,400) reforzar / slice(0,300) contexto (prompts.ts:191-192) sobre una página de ~350 palabras (~2.000+ chars): garantía verbatim, por-qué-ahora y el CTA quedan fuera casi siempre.
  - fix: Pasar el markdown completo (cabe de sobra en 4200 maxTokens) o extraer secciones estructuradas (para quién / garantía / CTA) en vez de slice ciego.
- **demand_quantification (0.2).keyword_intents** — problema: Solo sobreviven 8 strings .keyword (brief.ts:68-71); intent, monthly_searches y keyword_difficulty — lo pagado a DataForSEO — se descartan antes del prompt.
  - fix: Serializar `"kw" [vol/mes real · KD · intent]` como ya hace step-proposal (route.ts:117-125) y filtrar por afinidad al journey/awareness de la pieza.
- **personas (0.3).avatars[avatarKey] → AUDIENCIA** — problema: JSON.stringify crudo cortado a 1600 chars (produce/route.ts:130) — corta forces_of_progress a mitad de objeto y mete llaves/ruido; si avatarKey no matchea cae a avatars[0] EN SILENCIO (pieza del avatar equivocado).
  - fix: Proyección estructurada (essence, where_we_meet, 3 ongoing_pains, 2 anxiety, habit) como la forcesLine de step-proposal:136, y 409/warn cuando el avatar no existe.
- **hook_library (2.5).hooks[].template** — problema: Entra al Brief (brief.ts:78) pero no se imprime — el modelo no sabe qué molde retórico honra el gancho al continuar la pieza.
  - fix: Extender la línea GANCHO en prompts.ts:168 a `GANCHO de apertura (molde ${brief.hook.template}): "..."`.
- **channel_journey_matrix (2.2).journey_moments** — problema: Match por heurística de tokens label↔kind (produce/route.ts:140-142): 'Blog/SEO' vs kind 'artículo' no comparten token >2 chars → la etapa del journey se pierde en silencio.
  - fix: Guardar channel_key en cada derivative al generar 2.4 y matchear por key; loggear cuando no hay match en vez de omitir.
- **business_context (0.1).refined_idea / why_now** — problema: Doble truncado (route 600/300 → prompt 500/200, prompts.ts:182-184): el segundo corte es el efectivo y parte frases a la mitad.
  - fix: Un solo punto de truncado (el del prompt), con corte en límite de oración y presupuesto explícito.
- **atomization_map (2.4).long_form.title_working** — problema: Solo se usa como anchor_ref al persistir la pieza; el develop no sabe de qué pieza madre deriva → derivados sin coherencia temática ni CTA cruzado al contenido largo.
  - fix: Línea `PIEZA ANCLA: ${brief.anchor_title}` en buildDevelopSystem (el dato ya está en el Brief).
- **design_spec.image_prompts (gateway)** — problema: serializeForGateway toma SOLO el primer prompt no vacío → los slides 2..6 de un carrusel no se generan por esta vía.
  - fix: Iterar todos los image_prompts (como ya hace videoClipPrompts con los clips) o exponer una variante serializeForGatewayAll y usarla en la ruta de carrusel.
- **design_spec.video_prompts → duración de clip** — problema: clipSeconds parsea con regex 'N seconds|segundos' la PROSA del prompt; sin mención explícita = 6s fijos — la duración depende de que el LLM redactor mencione el número.
  - fix: Pedir campo estructurado duration_seconds por clip en el JSON de ===SPEC=== (prompts.ts:212) y usar la regex solo como fallback.
- **hooks-brain: excludeLanguageBound / preLaunch** — problema: Defaults duros no parametrizados: siempre asume mercado inglés y pre-launch — cuando el proyecto lance o sea hispano, seguirá excluyendo/incluyendo categorías equivocadas.
  - fix: Derivar marketIsEnglish de offer_statement.language / launch_focus y preLaunch de un flag de estado del proyecto, pasados desde la ruta.
- **suggest-hooks: candidates[].psychology + parseHookSuggestions** — problema: psychology está tipado en RerankCandidate pero no se imprime en el system del re-rank (el LLM ordena a ciegas del mecanismo); además los picks con id inválido se caen en silencio y puede devolver <5.
  - fix: Imprimir psychology por candidato en buildHookRerankSystem y rellenar hasta 5 con el top determinista de E1 cuando haya drops.
- **design_spec.output.aspect_ratio** — problema: Default '1:1' si falta + clamps divergentes por proveedor (Kling {16:9,9:16,1:1}, Veo 1:1→9:16) — el ratio real depende del proveedor, no del canal de la pieza.
  - fix: Derivar el ratio del canal del derivado (kind→ratio map: reel/story=9:16, feed=1:1/4:5) al generar el spec y validarlo en parseDevelop.

## Faltante (8)

- **Fecha de publicación objetivo de la pieza (el slot del calendario)** — El develop ancla al 'hoy' del momento de generación (y solo si el radar devuelve eventos); una pieza generada hoy pero publicada en 3 semanas puede quedar fuera de temporada — es la generalización del bug 'February'. _(capturar en: Pasar publish_date del slot del calendario como parámetro de produce/route.ts y usarla (no todayISO) como ancla del CONTEXTO TEMPORAL.)_
- **Refresco/jubilación de ganchos vencidos + backfill de temporality** — M5 ya escribe expires_at pero nada retira ni regenera ganchos caducados, y las bibliotecas generadas ANTES de M5 no tienen temporality (los ganchos 'February' legacy siguen en rotación para siempre). _(capturar en: Sweep al cargar hook_library en produce (excluir vencidos) + migración/backfill withDefaultTemporality sobre bibliotecas viejas + regeneración quirúrgica de caducados con buildHookRegenSystem (ya existe).)_
- **Loop de rendimiento por pieza/gancho (métricas reales)** — hooks[].in_use y channels[].how_measured existen, pero ninguna fase captura impresiones/CTR/ventas por pieza — 'los ganadores se quedan, los que no convierten se jubilan con datos' no tiene datos con los que operar. _(capturar en: Fase 3/4: ingesta de métricas por piece_id/hook_id (manual o API) en una tabla de resultados; inyectar 'ganchos ganadores/retirados' en suggest-hooks y en la regeneración 2.5.)_
- **Ejemplos few-shot de piezas aprobadas/editadas por el operador** — La doctrina 'la corrección humana manda' vive en tarjetas de Fase 0-1 pero ninguna fase guarda piezas finales aprobadas como ejemplares de voz — el develop redacta sin ningún 'así sonamos' real, el mecanismo más barato de fidelidad de voz. _(capturar en: Al aprobar/editar una pieza en El Estudio, flag is_exemplar; produce inyecta 1-2 ejemplares del mismo canal como few-shot.)_
- **Locale/idioma canónico del proyecto** — El idioma se infiere en cadena frágil (offer_statement.language='auto' → 'el idioma del gancho/keywords') y hooks-brain lo asume inglés por default duro — no existe un campo único de verdad para el mercado hispano o multi-territorio. _(capturar en: Campo market_locale fijado al firmar launch_focus en 0.1 (o al firmar 1.4), leído por produce, hooks-brain y el gateway.)_
- **CTA destino real por canal (URL/handle/link-in-bio)** — El develop exige cierre específico 'nunca follow-for-more' pero no puede apuntar a un destino concreto: domain_checks se capturan en 0.1 y el dominio elegido nunca se consume — el CTA queda retóricamente específico pero operativamente vacío. _(capturar en: channels[].cta_destination en la matriz 2.2 (o registro project-level de links) inyectado en la línea de OFERTA/cierre.)_
- **awareness_target por derivado** — content_mix.target_mix reparte el presupuesto editorial por momento de conciencia, pero ningún derivado declara a cuál sirve — el mix firmado no es ejecutable pieza a pieza y el proxy (journey por tokens) es frágil. _(capturar en: derivatives[].awareness_target en 2.4 (validado contra target_mix al firmar), impreso en el develop e informando la selección de plantilla de gancho.)_
- **Biblioteca de prueba social post-lanzamiento** — C4 prohíbe testimonios pre-launch (correcto), pero no existe artefacto donde capturarlos cuando lleguen — el día que haya clientes, el prompt seguirá atacando solo por mecanismo y el eje 'probabilidad' quedará sub-atacado. _(capturar en: Artefacto phase_3 proof_library (quote, resultado, fuente, permiso) que al existir levante la restricción C4 en el develop.)_

## Innecesario (6)

- **offer_stack.core_deliverable.perceived_value_usd + comparable** — Legacy retirado el 2026-06-25: la doctrina prohíbe vender por comparación/value-stack; siguen en el schema solo por compatibilidad. Dejar de generarlos y marcarlos deprecated para que ningún prompt futuro los recoja por accidente.
- **atomization_map.derivatives_count + derivatives_summary** — Redundantes con derivatives[] (el gate ya usa count ?? derivatives.length): dos representaciones de la misma verdad que pueden divergir; con derivatives[] estructurado, el resumen y el conteo son derivables en lectura.
- **channel_journey_matrix.channels_declared** — Lista derivada de channels[].enabled recalculable al vuelo (la genera parseP2Proposal); persistirla es dual-homing dentro del propio artefacto y nadie la consume para contenido (solo step-proposal la imprime como JSON, donde podría derivarse).
- **risk_urgency.scarcity.type** — Default 'none', el propio inventario lo marca 'hoy sin uso activo' y ninguna ruta lo consume: o se implementa con su candado ético (como urgency.genuine_reason) o se quita del schema — un campo persuasivo muerto invita a llenarlo sin gobernanza.
- **step_thread.pre.price_research + step_thread.pre.cost_breakdown** — Copias embebidas byte-a-byte de product_economics.price_research/cost_breakdown: dos fuentes de verdad para el mismo estudio; el hilo puede referenciar el artefacto project-level en vez de duplicarlo.
- **channel_journey_matrix.notifications_commitment** — Frase de contrato UX del producto ('cada slot te avisará con el copy listo') guardada por avatar dentro de un artefacto de contenido: no informa ninguna pieza ni el calendario — ese compromiso vive en el producto, no en los datos del proyecto.

---

# Anexo C — Inventario campo por campo (fases 0/1/2)

## phase_0 (Fundación) — 5 artefactos en project_phase_artifacts, clave única (project_id, phase, sub_step, artifact_name, avatar_key). Nota: lib/schemas/foundation-brief.ts es un schema legacy del Setup Agent v1 (renderDraft/prompts) que NO se persiste como artefacto en los flujos phase0 actuales.

### 0.1 — Terreno — `business_context`  
_creado por: components/phase0/terreno-wizard.tsx (upsertArtifact en cada respuesta) + app/api/phase0/idea-cowork/route.ts (co-work de idea: deep_questions/differentiators/refined_idea) + app/api/phase0/name-check/route.ts (devuelve domain_checks/name_conflicts que el wizard persiste). Schema: lib/schemas/business-context.ts; guion determinista en lib/wizard/terreno-script.ts_

- **schema_version / sub_step** — Literales de versionado ('v1', '0.1-business-context') para parseo seguro del JSON.  
  _valor marketing:_ Bajo — plomería, no contenido.
- **idea** — La idea de negocio en las palabras crudas del usuario (lo primero que Papandi pregunta, 'como a un amigo').  
  _valor marketing:_ Alto — es la voz auténtica del fundador; fuente de lenguaje real para copy y storytelling de origen.
- **idea_mode** — Si el proyecto es 'nueva' o 'en_marcha' (D-018 co-crear vs extraer).  
  _valor marketing:_ Medio — cambia el ángulo narrativo: historia de lanzamiento vs historia de tracción.
- **idea_material** — Material pegado por el usuario (docs, notas) cuando el proyecto ya camina.  
  _valor marketing:_ Medio — cantera de hechos y frases del propio negocio para reutilizar en piezas.
- **deep_questions[] (id, question, hint, answer)** — Preguntas profundas adaptativas generadas por Papandi + las respuestas del usuario durante el co-work de idea.  
  _valor marketing:_ Alto — las respuestas contienen matices del negocio (por qué, para quién, cómo) que no están en ningún otro campo; oro para ángulos de contenido.
- **differentiators[] (key, label, description, original_description, state)** — Diferenciadores co-creados en tarjetas: Papandi propone, el usuario acepta/descarta/edita; original_description guarda el texto de Papandi cuando el usuario lo corrigió (la corrección humana manda downstream).  
  _valor marketing:_ Alto — los aceptados son LA materia prima de propuestas de valor, hooks y ángulos de diferenciación; description editada = palabras del fundador.
- **idea_solid** — Juicio del modelo: la idea ya es suficientemente sólida para evaluar (cierra el loop de extracción).  
  _valor marketing:_ Bajo — control de flujo del wizard.
- **extraction_rounds** — Rondas de co-work corridas (tope duro en el route = control de costos).  
  _valor marketing:_ Bajo — telemetría de costos.
- **refined_idea** — La idea afinada tras el co-work; alimenta el research 0.2 y la puerta 0.2.5.  
  _valor marketing:_ Alto — es el pitch destilado del negocio; base directa para bios, descripciones y elevator pitch en contenido.
- **why_now** — Por qué este negocio tiene sentido AHORA (generado en el co-work junto a refined_idea).  
  _valor marketing:_ Alto — el argumento de urgencia/timing; combustible para ganchos de 'por qué hoy' y contenido de tendencia.
- **business_type** — Quién paga: B2C, B2B o hybrid.  
  _valor marketing:_ Alto — decide tono, canales y ciclo de todo el contenido (persona vs empresa).
- **lead_segment / parked_segment** — En híbridos: qué segmento (B2C/B2B) lidera el lanzamiento y cuál queda anotado para después.  
  _valor marketing:_ Alto — evita contenido difuso: toda la Fase 0-2 se escribe para el segmento líder.
- **sales_cycle** — Cómo decide el cliente: impulsivo, reflexivo o mixto.  
  _valor marketing:_ Alto — impulsivo pide claridad y momento exacto; reflexivo pide confianza, pruebas y educación — cambia el tipo de pieza a producir.
- **monetization_model** — Cómo cobra: subscription, one_shot, freemium, usage o unsure.  
  _valor marketing:_ Medio — suscripción orienta contenido a retención, pago único a flujo constante de nuevos; define el 'juego' del funnel.
- **monetization_pattern** — Patrón de modelo de negocio reconocido, vocabulario extensible (ej. bait_hook_credits derivado de subscription+consumible).  
  _valor marketing:_ Medio — permite hablar del modelo con precisión (ej. narrativa cebo-y-anzuelo) al diseñar la oferta y su comunicación.
- **has_usage_consumable** — Hay consumible por uso (créditos/IA/materiales) — distingue bait_hook_credits y abre la dependencia de modelo de costos en Fase 1.  
  _valor marketing:_ Bajo para contenido — alto para pricing/oferta (Fase 1).
- **market_scope** — Dónde están los clientes: local, nacional, internacional.  
  _valor marketing:_ Alto — define idioma, canales y si el contenido es de proximidad (mapas/reseñas) o de alcance país/global.
- **launch_focus_accepted (+ metadata.launch_focus)** — El usuario aceptó la propuesta de 'lanzar enfocado' (un país/idioma primero) cuando marcó internacional; el territorio elegido va en metadata.launch_focus.  
  _valor marketing:_ Alto — fija el territorio e idioma reales del arranque, o sea dónde y en qué lengua se crea el contenido.
- **marketing_objective (primary, primary_kpi)** — Resultado de negocio buscado primero (sales/recurring/leads/awareness) + meta concreta opcional en lenguaje llano ('10 ventas/mes'); calibra el math gate de 0.2.  
  _valor marketing:_ Alto — es el norte de cada campaña: decide si el contenido optimiza venta, retención, captura de leads o alcance, y contra qué KPI se mide.
- **working_name / name_status** — Nombre de trabajo del negocio + estado (undecided/working/final); nunca bloquea el gate, se firma en 1.4.  
  _valor marketing:_ Alto — el nombre aparece en cada pieza; su estado avisa si la marca aún puede cambiar.
- **domain_checks[] (domain, available, price_usd, source)** — Chequeo real de dominios (Verisign RDAP para .com/.net, Vercel API si hay token): disponible/tomado/no-confirmado + precio.  
  _valor marketing:_ Medio — decide el dominio/URL que llevará todo el contenido y los CTA.
- **name_conflicts[] (name, what, source)** — Marcas/empresas/apps existentes con el mismo nombre o similar, detectadas por web search (best-effort, máx 3, nunca inventadas).  
  _valor marketing:_ Medio — riesgo de confusión de marca; informa si conviene diferenciar el naming en el contenido.
- **name_check_ran** — Flag de que el chequeo de nombre ya corrió (distingue 'sin conflictos' de 'no revisado').  
  _valor marketing:_ Bajo — control de flujo.
- **implications_acknowledged[]** — Implicaciones derivadas en lenguaje llano (generadas por terrenoImplications()) que el usuario reconoció al firmar; el gate exige ≥2.  
  _valor marketing:_ Medio — cada implicación es una regla estratégica ya aceptada ('compra pensada ⇒ contenido de confianza, no presión') que el contenido debe honrar.
- **flags_raised[]** — Flags rule-based levantados en la conversación (hybrid_two_terrains, pricing_pattern, impulse_check, international_focus) — rastro glass-box.  
  _valor marketing:_ Bajo — trazabilidad de decisiones, no insumo directo de piezas.
- **status / gate_G_Phase_0_1 / signed_at** — Estado del artefacto (draft/signed), gate (pending/passed) y timestamp de firma; editar un artefacto firmado lo re-abre (regla de enmienda).  
  _valor marketing:_ Bajo — gobernanza; garantiza que el contenido se construye sobre decisiones firmadas.
- **metadata** — Bolsa de campos no anticipados (Evolving Schema): solid_reason, extraction_capped, launch_focus, etc.  
  _valor marketing:_ Bajo-medio — launch_focus sí es útil (territorio del arranque).

### 0.2 — Mercado — `demand_quantification`  
_creado por: app/api/phase0/market-research/route.ts (LLM research + enriquecimiento DataForSEO Labs + auditoría AI Overview; persist único al final con metadata.pipeline_complete=true) + components/phase0/mercado-step.tsx (ediciones del usuario). Schema: lib/schemas/demand-quantification.ts_

- **schema_version / sub_step** — Literales 'v1' y '0.2-demand'.  
  _valor marketing:_ Bajo — plomería.
- **verified_points[] (claim, value, source_name, source_url)** — Datos duros del mercado, cada punto con su fuente — nunca presentados como inferencia (regla glass-box); el gate exige ≥3.  
  _valor marketing:_ Alto — estadísticas citables para contenido de autoridad ('el X% de...'), hooks con números reales y credibilidad verificable.
- **inferred_readings[] (claim, basis)** — Lecturas de Papandi SIEMPRE etiquetadas como inferencia, con su base; el usuario puede corregirlas.  
  _valor marketing:_ Medio — hipótesis de mercado utilizables como ángulos, pero sin citarlas como dato duro.
- **keyword_intents[] (intent, keyword, volume_note, zero_click_risk, monthly_searches, competition, keyword_difficulty, measured)** — Keywords clasificadas por intención de búsqueda (transaccional=listo para comprar / comparativa=comparando / informacional=investigando el problema), con volumen mensual real y competencia y dificultad SEO 0-100 de DataForSEO cuando measured=true (si no, volume_note es la estimación LLM), y flag de riesgo zero-click por AI Overview de Google.  
  _valor marketing:_ Alto — ES el mapa de contenido SEO de Fase 2: qué buscan, con qué palabras exactas, cuánta gente, qué tan difícil rankear, y qué keywords Google se come con AI Overview (evitar apostarles el tráfico).
- **refuted_assumptions[] (assumption, what_research_found)** — Corazonadas del operador que la investigación REFUTÓ (EVIDENCE-001: el research honesto refuta ≥1 cosa).  
  _valor marketing:_ Alto — ángulos contraintuitivos listos ('creíamos X, los datos dicen Y') y vacunas contra contenido basado en supuestos falsos.
- **market_size (tam_note, sam_note, som_note)** — Tamaño de mercado en lenguaje llano: total / alcanzable / capturable.  
  _valor marketing:_ Medio — cifras de contexto para contenido de oportunidad y pitch; más estratégico que pieza a pieza.
- **economic_reading** — Capa económica: señal de willingness-to-pay / sensibilidad al precio del mercado.  
  _valor marketing:_ Alto — informa cómo hablar de precio en el contenido (valor vs costo) y qué objeción económica anticipar.
- **awareness (problem_aware_note, solution_aware_note, unaware_note)** — Notas cualitativas de cuán consciente está el mercado del problema y de las soluciones.  
  _valor marketing:_ Alto — dicta el punto de partida del mensaje: educar el problema vs comparar soluciones vs cerrar.
- **awareness_distribution (unaware_pct, problem_aware_pct, solution_aware_pct, most_aware_pct)** — La foto del mercado como distribución de 4 niveles (~100 total), MISMAS claves que content_mix.target_mix de Fase 2 — cruza la frontera de fase sin traducción (CONTENT-004 la espeja ±10%).  
  _valor marketing:_ Alto — determina directamente el MIX de contenido: qué % de piezas para dormidos vs conscientes del dolor vs comparadores vs listos para comprar.
- **offer_strategy / offer_strategy_note** — Veredicto create_demand vs capture_demand (¿hay que crear la demanda o solo capturarla?) + nota explicativa; derivado del conteo de keywords por intención.  
  _valor marketing:_ Alto — la decisión madre del contenido: educación/evangelización (crear demanda) vs SEO/comparativas/captura (demanda existente).
- **math_gate (target_users, price_monthly_usd, annual_revenue_usd, passes, note)** — La matemática en abierto: usuarios objetivo × precio = ingreso anual, ¿la meta cabe en el mercado? passes true/false + nota.  
  _valor marketing:_ Medio — realismo para la meta de campañas; poco uso directo en piezas, mucho en planificación.
- **verdict / verdict_note** — Semáforo del mercado: verde/amarillo/rojo + razón.  
  _valor marketing:_ Medio — go/no-go estratégico; el note resume la lectura del mercado en una frase reutilizable.
- **research_method** — Cómo se investigó (transparencia glass-box del método).  
  _valor marketing:_ Bajo — trazabilidad.
- **status / gate_G_Phase_0_2 / signed_at** — Draft/signed + gate + firma (gate: ≥3 verified_points, verdict emitido, math_gate calculado).  
  _valor marketing:_ Bajo — gobernanza.
- **metadata (dataforseo_enriched, dataforseo_keyword_source, dataforseo_pool_size, curated_keywords, curation_cost_usd, ai_overview_audited, ai_overview_flagged, pipeline_complete, dataforseo_note/error)** — Telemetría del pipeline de enriquecimiento: si hubo datos medidos reales, tamaño del pool, costo de curación LLM, cuántas keywords se auditaron/flagearon por AI Overview, y si el pipeline terminó.  
  _valor marketing:_ Bajo-medio — dice cuánta confianza dar a los números de keywords (medidos vs estimados).

### 0.2.5 — Puerta (ICP) — `icp`  
_creado por: app/api/phase0/icp-proposal/route.ts (propuesta LLM desde business_context+demand firmados, prompt puerta_proposal@v1.0.0) + components/phase0/puerta-step.tsx (aceptar/descartar tarjetas). Schema: lib/schemas/icp.ts_

- **schema_version / sub_step** — Literales 'v1' y '0.2.5-icp'.  
  _valor marketing:_ Bajo — plomería.
- **beachhead_label** — Etiqueta del segmento cabeza de playa: el nicho concreto por el que se entra al mercado.  
  _valor marketing:_ Alto — el 'para quién' explícito de cada pieza; nombra a la audiencia en titulares y targeting.
- **must_have_filters[] (key, label, description, state)** — Filtros imprescindibles del cliente ideal, en tarjetas co-creadas (pending/accepted/discarded); el gate exige ≥3 aceptados.  
  _valor marketing:_ Alto — criterios de calificación que se convierten en lenguaje de auto-selección ('esto es para ti si...') y en targeting de ads.
- **deal_breakers[] (key, label, description, state)** — Descalificadores: señales de que alguien NO es el cliente; gate exige ≥2 aceptados.  
  _valor marketing:_ Alto — permite contenido que repele al cliente equivocado ('esto NO es para ti si...') y ahorra presupuesto de adquisición.
- **cluster_notes (demographic, psychographic)** — Notas del clúster: quiénes son demográficamente y cómo piensan/sienten.  
  _valor marketing:_ Alto — la base de tono, referencias culturales y estética del contenido.
- **evidence_basis** — Declaración de en qué evidencia se basa esta puerta (requerido por el gate).  
  _valor marketing:_ Medio — respaldo de credibilidad; útil si el contenido cita 'según lo que vimos en el research'.
- **status / gate_G_Phase_0_2_5 / signed_at** — Draft/signed + gate (≥3 must-haves, ≥2 deal-breakers, evidencia declarada) + firma.  
  _valor marketing:_ Bajo — gobernanza.
- **metadata (model, cost_usd, latency_ms)** — Telemetría de la llamada LLM que generó la propuesta.  
  _valor marketing:_ Bajo — costos/observabilidad.

### 0.3 — Personas — `personas`  
_creado por: app/api/phase0/personas-proposal/route.ts (propuesta LLM desde 0.1+0.2+0.2.5 firmados, prompt personas_proposal@v1.0.0, soporta focus) + components/phase0/personas-step.tsx (aceptar/editar tarjetas, elegir first_cycle). Schema: lib/schemas/personas.ts_

- **schema_version / sub_step** — Literales 'v1' y '0.3-personas'.  
  _valor marketing:_ Bajo — plomería.
- **persona.label** — Nombre de LA persona primaria (pre-PMF hay una sola).  
  _valor marketing:_ Alto — el arquetipo central al que se le escribe todo.
- **persona.self_image** — Cómo se ve a sí misma la persona (autoimagen).  
  _valor marketing:_ Alto — el espejo: el contenido que refleja la identidad deseada del lector convierte mejor que el que describe el producto.
- **persona.jtbd** — Job-to-be-done funcional + emocional en 1-2 frases (resumen).  
  _valor marketing:_ Alto — el 'para qué me contratan' es la promesa central de cualquier pieza.
- **persona.pains[]** — Lista de dolores de la persona primaria.  
  _valor marketing:_ Alto — la capa DOLOR del Cerebro de Ganchos: cada dolor es un hook potencial.
- **persona.data_layers (demographic, psychographic, behavioral, economic)** — Las 4 capas de datos del corpus §0.3 en lenguaje llano: quién es, cómo piensa, cómo se comporta, cuánto/cómo gasta.  
  _valor marketing:_ Alto — behavioral dice dónde/cuándo consume contenido; economic cómo hablarle de precio; psychographic el tono; demographic el casting visual.
- **avatars[].key / name / age** — Identificador, nombre propio y edad de cada avatar (2-4 variantes contextuales de la persona).  
  _valor marketing:_ Medio — humaniza: nombre y edad concretan el casting de imágenes y ejemplos.
- **avatars[].essence** — La historia de 60 segundos: quién es, su situación, su pregunta.  
  _valor marketing:_ Alto — mini-brief narrativo listo para guiones, escenas y storytelling de cada pieza.
- **avatars[].distinct_because** — Por qué este avatar es genuinamente distinto (regla 2-de-3: trigger/canal/lenguaje).  
  _valor marketing:_ Alto — garantiza que el contenido por-avatar no sea el mismo mensaje repetido; señala QUÉ cambiar entre versiones.
- **avatars[].journey_stage** — Dónde vive la estrategia de este avatar en el journey (consciencia→consideración→decisión→retención→advocacy).  
  _valor marketing:_ Alto — decide el tipo de pieza para este avatar (educativa vs comparativa vs cierre vs fidelización).
- **avatars[].where_we_meet** — El lugar/momento concreto donde encontramos al avatar (canal + contexto).  
  _valor marketing:_ Alto — mapea directo a canales de distribución y al contexto de consumo (formato, duración, tono) de cada pieza.
- **avatars[].forces_of_progress.ongoing_pains[]** — Dolores crónicos del avatar (JTBD Forces): lo que duele siempre.  
  _valor marketing:_ Alto — alimenta SEO y contenido evergreen (el dolor crónico se busca todo el año).
- **avatars[].forces_of_progress.triggers[] (event, type: estacional/situacional/emocional/financiero/otro)** — Eventos disparadores que mueven al avatar a actuar, tipificados.  
  _valor marketing:_ Alto — insumo táctico de ads y urgencia: los estacionales dan calendario, los situacionales dan hooks de momento exacto.
- **avatars[].forces_of_progress.pull[]** — Atracción de la solución nueva: qué le tira hacia el cambio.  
  _valor marketing:_ Alto — los beneficios que sí mueven, en el orden que importan al avatar; base de promesas y CTAs.
- **avatars[].forces_of_progress.anxiety[]** — Miedos sobre cambiar/adoptar la solución.  
  _valor marketing:_ Alto — objeciones a desactivar en el contenido (pruebas, garantías, FAQs); semilla de la garantía en Fase 1.
- **avatars[].forces_of_progress.habit[]** — La manera actual de resolver (el hábito a desplazar).  
  _valor marketing:_ Alto — el enemigo narrativo: contenido de desplazamiento 'deja de hacer X' contra la alternativa actual.
- **avatars[].original_essence / state** — Texto original de Papandi si el usuario editó la essence + estado de tarjeta (pending/accepted/discarded).  
  _valor marketing:_ Bajo-medio — la edición humana indica las palabras preferidas del operador.
- **negative_personas[] (key, label, description, exclusion_basis: etico/economico/ltv_bajo/alto_costo_soporte/otro, action: descalificar/revision_manual/redirigir, state)** — Anti-personas estructuradas: a quién NO servir, por qué se excluye y qué hacer al detectarla; drives la exclusion list de Fase 3.  
  _valor marketing:_ Alto — define qué contenido NO hacer, qué audiencias excluir en ads y cómo redactar para repeler sin ofender.
- **first_cycle_avatar_key** — Decisión HUMANA (nunca algorítmica): qué avatar dispara el primer ciclo de contenido.  
  _valor marketing:_ Alto — el foco del primer sprint: toda la producción inicial se escribe para ESTE avatar.
- **evidence_basis** — En qué evidencia se basan estas personas.  
  _valor marketing:_ Medio — credibilidad del retrato; distingue persona investigada de persona imaginada.
- **status / gate_G_Phase_0_3 / signed_at** — Draft/signed + gate (persona nombrada, ≥2 avatares aceptados, ≥1 negativa aceptada, pick humano sobre avatar aceptado) + firma.  
  _valor marketing:_ Bajo — gobernanza.
- **metadata (model, cost_usd, latency_ms)** — Telemetría de la llamada LLM.  
  _valor marketing:_ Bajo.

### 0.4 — Cancha — `cancha`  
_creado por: app/api/phase0/cancha-research/route.ts (LLM + web_search hasta 8 usos, desde 0.1-0.3 firmados, prompt cancha_research@v1.0.0) + components/phase0/cancha-step.tsx (aceptar gaps, elegir chosen_gap_key). Schema: lib/schemas/cancha.ts_

- **schema_version / sub_step** — Literales 'v1' y '0.4-cancha'.  
  _valor marketing:_ Bajo — plomería.
- **rivals[] (key, name, channel, price_note, angle, source_name, source_url)** — Competidores directos mapeados por canal (seo/redes/ads — string extensible), con nota de precio (show-and-confirm), su posicionamiento en una frase + qué modelar/evitar, y fuente; gate exige ≥3.  
  _valor marketing:_ Alto — el angle dice qué mensaje ya está ocupado (no repetirlo) y qué imitar; price_note ancla el framing de precio; channel revela dónde compite cada rival (dónde diferenciarse o evitar).
- **substitutes[] (mismo shape RivalCard)** — Sustitutos: soluciones no-directas con las que el cliente resuelve hoy (channel='sustituto').  
  _valor marketing:_ Alto — la competencia real del contenido de desplazamiento: 'vs hacerlo en Excel / vs no hacer nada'.
- **gaps[] (key, label, description, state)** — Huecos accionables del mercado en tarjetas propuesta (pending/accepted/discarded): lo que nadie está atendiendo.  
  _valor marketing:_ Alto — cada gap aceptado es un territorio de mensaje sin dueño; el elegido se vuelve el eje del posicionamiento.
- **verdict / verdict_note** — Veredicto de posicionamiento: océano 'rojo' (mercado saturado) o 'azul' (espacio abierto) + razón.  
  _valor marketing:_ Alto — cambia la estrategia de contenido: en rojo se compite por diferenciación agresiva; en azul se educa una categoría nueva.
- **errc (eliminar, reducir, incrementar, crear)** — Lente ERRC (spec §7, FLAG-9): qué da por sentado el sector que ESTE negocio puede Eliminar/Reducir/Incrementar/Crear — el razonamiento detrás del verdict; nullable para artefactos previos.  
  _valor marketing:_ Alto — cuatro ángulos de contenido contrarian listos: 'por qué eliminamos X que todos cobran', 'lo que nadie ofrece y nosotros creamos'.
- **chosen_gap_key** — Decisión humana: EL hueco que este negocio ataca — semilla del posicionamiento de Fase 1; gate exige que apunte a un gap aceptado.  
  _valor marketing:_ Alto — la elección de posicionamiento: el mensaje madre del que cuelga todo el contenido posterior.
- **evidence_basis** — Base de evidencia del mapa competitivo.  
  _valor marketing:_ Medio — credibilidad del análisis.
- **status / gate_G_Phase_0_4 / signed_at** — Draft/signed + gate (≥3 rivales, verdict emitido, ≥1 gap aceptado y elegido) + firma.  
  _valor marketing:_ Bajo — gobernanza.
- **metadata (model, cost_usd, latency_ms)** — Telemetría de la llamada LLM con web search.  
  _valor marketing:_ Bajo.

## FASE 1 — Oferta (Papandi): 1.0 economía del producto · 1.1 ecuación de valor · 1.x estrategia de demanda · 1.2 paquete/stack · 1.3 garantía-urgencia-desplazamiento · 1.4 precio/nombre/statement

### 1.0 — `product_economics (persistido; project-level, avatar-agnóstico)`  
_creado por: lib/schemas/product-economics.ts (shape); escrito por components/phase1/paquete-thread.tsx vía upsertArtifact; alimentado por /api/phase1/pricing-research y /api/phase1/cost-estimate_

- **cost_to_serve_usd** — Costo marginal de servir a UN cliente/unidad al mes, fijado al producto (no al avatar).  
  _valor marketing:_ medio — sostiene claims de precio honesto y define cuánto margen hay para promos/descuentos sin quebrar el candado
- **cost_breakdown** — El desglose línea-por-línea (shape CostBreakdown) que produjo ese costo, guardado para reuso 'ya desglosado'.  
  _valor marketing:_ bajo — es interno/glass-box; útil solo para narrativa de transparencia si la marca la usa
- **base_price_usd** — Precio base/objetivo del producto que los candados del paquete consumen por defecto.  
  _valor marketing:_ alto — es EL número de precio que enmarca todo el copy (única cifra permitida en la página de oferta)
- **price_research** — El estudio de precio con competencia real (shape PricingResearch) guardado para reuso.  
  _valor marketing:_ alto — contiene competidores reales con precios/fuentes y el porqué del posicionamiento de precio
- **metadata** — Bolsa libre de metadatos (record).  
  _valor marketing:_ bajo — trazabilidad

### 1.1 — `value_equations (persistido; una ecuación Hormozi por avatar, puntuada por el OPERADOR)`  
_creado por: lib/schemas/value-equation.ts (shape); app/api/phase1/value-equation-suggest/route.ts escribe la sugerencia LLM; el cliente escribe los scores reales y firma_

- **equations[].avatar_key / avatar_name / first_cycle** — A qué avatar pertenece la ecuación y si es el del primer ciclo (avatar de entrada).  
  _valor marketing:_ medio — permite segmentar contenido por avatar/canal
- **equations[].dream_statement** — El sueño del cliente en UNA frase, en SU punto de vista (anclado a su meta, no al producto).  
  _valor marketing:_ ALTO — es el hook maestro: la promesa/aspiración exacta para titulares, ganchos y aperturas
- **equations[].dream.score + rationale** — Eje 'resultado soñado' 1–10 con su porqué (10=óptimo).  
  _valor marketing:_ alto — el rationale verbaliza por qué el sueño importa; materia prima de copy aspiracional
- **equations[].likelihood.score + rationale** — Eje 'probabilidad percibida de lograrlo' 1–10 con porqué.  
  _valor marketing:_ alto — si es bajo, el contenido debe atacar escepticismo (mecanismo, no testimonios); el rationale nombra la duda exacta
- **equations[].time.score + rationale** — Eje 'demora hasta el resultado' 1–10 con porqué.  
  _valor marketing:_ alto — dicta si el copy enfatiza rapidez/primeros resultados
- **equations[].effort.score + rationale** — Eje 'esfuerzo y sacrificio' 1–10 con porqué.  
  _valor marketing:_ alto — dicta claims de facilidad ('sin que tengas que…')
- **equations[].weak_plan_note** — Plan escrito de mejora obligatorio cuando el composite cae en banda débil (100–999).  
  _valor marketing:_ medio — anticipa el ángulo que el paquete/contenido debe reforzar
- **equations[].suggestion** — Propuesta de arranque de Papandi (dream_statement + 4 ejes con score/rationale + weak_plan_note), guardada JUNTO a los scores reales, nunca como default (anti-anclaje).  
  _valor marketing:_ medio — segunda lectura del mismo comprador; alternativas de framing
- **status / gate_G_Phase_1_1 / signed_at** — Estado draft|signed, gate pending|passed y fecha de firma.  
  _valor marketing:_ bajo — gobernanza: solo lo firmado alimenta contenido
- **(derivados en código) compositeOf / weakestAxisOf / categoryOf** — Composite = producto de los 4 ejes (1–10.000); eje más débil; categoría (inaceptable/débil/estándar/sólida/excepcional).  
  _valor marketing:_ ALTO — el eje débil es la ORDEN DE TRABAJO: define qué objeción ataca el paquete y luego todo el contenido

### 1.x — `multi_avatar_decision (persistido; contenido = shape StrategyDecision de offer.ts)`  
_creado por: components/phase1/offer-steps.tsx (usePersist '1.x'/'multi_avatar_decision'); lectura LLM previa de /api/phase1/strategy-proposal_

- **decision** — Decisión de estrategia con un solo avatar activo: 'own_strategy' (trivial, D-039).  
  _valor marketing:_ bajo — estructural
- **rationale** — Porqué narrado de la decisión (un solo público encendido → su propia estrategia v1).  
  _valor marketing:_ bajo — contexto interno
- **avatar_key / avatar_name** — El avatar al que pertenece la estrategia.  
  _valor marketing:_ medio — ancla el contenido al público activo
- **demand_type** — Cómo llega la demanda de ese avatar: capture (ya busca con palabras exactas) | generate (dormido, hay que despertarlo) | mixed.  
  _valor marketing:_ ALTO — decide el TIPO de contenido: SEO/captura de búsqueda vs. contenido que despierta (hooks de interrupción) vs. mixto
- **demand_type_rationale** — El porqué glass-box de esa elección, citando el estudio 0.2 firmado / la esencia del avatar.  
  _valor marketing:_ alto — explica el comportamiento de búsqueda del cliente; guía canales y formatos
- **status / signed_at / metadata** — draft|signed, fecha de firma, metadatos.  
  _valor marketing:_ bajo — gobernanza

### 1.x — `strategies (persistido; registro de estrategias por avatar)`  
_creado por: components/phase1/offer-steps.tsx (usePersist '1.x'/'strategies'); leído por Phase 2 (app/api/phase2/step-proposal/route.ts)_

- **strategies[].strategy_id** — Id de la estrategia (p.ej. strat_<avatarKey>_v1).  
  _valor marketing:_ bajo — referencia
- **strategies[].avatar_name** — Avatar dueño de la estrategia.  
  _valor marketing:_ medio — segmentación de contenido
- **strategies[].demand_type** — capture|generate|mixed heredado de la decisión firmada.  
  _valor marketing:_ ALTO — es lo que Fase 2 consume para orientar el plan de contenido
- **strategies[].status / version_number** — active|… y versión de la estrategia.  
  _valor marketing:_ bajo — versionado

### 1.x (efímero) — `StrategyRead — lectura razonada de Papandi sobre el tipo de demanda (NO se persiste; se devuelve al cliente y su porqué acaba en demand_type_rationale)`  
_creado por: lib/wizard/phase1/strategy-proposal.ts + app/api/phase1/strategy-proposal/route.ts (con fallback determinista en código desde el estudio 0.2)_

- **recommended** — capture|generate|mixed recomendado por Papandi.  
  _valor marketing:_ alto — se cristaliza en demand_type
- **why** — 2-3 frases citando los datos FIRMADOS del usuario (estudio 0.2, esencia del avatar, canales de rivales).  
  _valor marketing:_ alto — argumento reutilizable sobre cómo compra/busca el cliente
- **example_search** — Las palabras EXACTAS que su cliente escribiría en Google (o null si no busca).  
  _valor marketing:_ ALTO — keyword semilla literal para SEO/ads/títulos
- **option_reads.capture / generate / mixed** — Una línea sobre qué significaría cada opción para ESTE avatar (no genérica).  
  _valor marketing:_ medio — micro-lecturas de canal por avatar
- **basis** — measured (derivado del estudio firmado) vs inferred (juicio de Papandi).  
  _valor marketing:_ medio — confiabilidad del dato al citarlo en contenido

### 1.2 — `offer_stack (persistido server-side por stack-proposal; el usuario dispone/edita/firma) — doctrina: venta por FUNCIONALIDAD, no comparación`  
_creado por: lib/schemas/offer.ts (OfferStack); lib/wizard/stack-proposal.ts; app/api/phase1/stack-proposal/route.ts (upsertArtifactContent phase_1/1.2/offer_stack)_

- **core_deliverable.name** — Nombre del entregable central — el producto enmarcado como el camino del buyer persona a su sueño.  
  _valor marketing:_ ALTO — el 'qué es' que encabeza toda página/pieza de venta
- **core_deliverable.description** — 1-2 frases de qué puede HACER/lograr el cliente con él.  
  _valor marketing:_ ALTO — copy de beneficio directo listo para reutilizar
- **core_deliverable.why** — Porqué narrado (canon): cómo este centro es el camino al sueño del comprador, anclado a datos firmados.  
  _valor marketing:_ alto — la narrativa/ángulo del producto en voz de igual de confianza
- **core_deliverable.state** — pending|accepted|discarded (disposición del usuario).  
  _valor marketing:_ bajo — solo lo accepted entra al statement
- **core_deliverable.perceived_value_usd / comparable** — LEGACY (retirados 2026-06-25): valor percibido en USD y comparable de mercado; nullable por compatibilidad.  
  _valor marketing:_ bajo — NO usar: la doctrina prohíbe vender por comparación
- **bonuses[].name / description / specific_target / why / state / key** — 4-5 refuerzos: qué le PERMITE al cliente (description), el freno/objeción concreta que quita (specific_target), el porqué narrado (why), y su disposición.  
  _valor marketing:_ ALTO — cada bonus = un par objeción→respuesta: mapa directo de ángulos de contenido (un post por freno)
- **price_point_usd / delivery_cost_usd** — Precio del paquete y costo de servir a un cliente (los del usuario MANDAN sobre la sugerencia LLM).  
  _valor marketing:_ alto — el precio único que aparece en el copy; el costo es interno
- **delivery_format** — digital|service|physical|hybrid — cómo se entrega; fija el umbral del candado de margen (70/50/30/40%).  
  _valor marketing:_ medio — condiciona claims logísticos (envío, acceso inmediato, sesiones)
- **stack_economics (price, cost, gross_margin_pct, margin_target_pct, margin_gate_passed)** — El único candado económico: margen bruto vs umbral por formato de entrega.  
  _valor marketing:_ bajo — salud del negocio, no copy; limita descuentos/promos
- **suggestions.guarantee_statement / urgency_statement / urgency_reason / displacement_replacement / displacement_cost** — Semillas para 1.3 (de la misma propuesta LLM): garantía, urgencia honesta + su razón real, y el encuadre de desplazamiento (qué hábito reemplaza + costo de seguir igual).  
  _valor marketing:_ ALTO — borradores de los elementos persuasivos clave; el desplazamiento es un ángulo de contenido completo ('deja de X')
- **uncovered[] (item, destino)** — 'Lo que dejo honestamente descubierto': 1-3 objeciones que este paquete NO resuelve, cada una con su fase dueña.  
  _valor marketing:_ alto — backlog explícito de objeciones para el contenido de fases posteriores; evita claims que el paquete no cubre
- **proposed_rescore (axis, from, to, why)** — LA prueba de que el paquete vale: cuánto sube el eje débil de la ecuación (propuesta; se firma en 1.3 con la garantía).  
  _valor marketing:_ alto — el 'antes/después' del argumento central: por qué esta oferta cambia la probabilidad/tiempo/esfuerzo del comprador
- **status / signed_at** — draft|signed y fecha.  
  _valor marketing:_ bajo — solo firmado alimenta 1.4 y Fase 2
- **metadata (price_basis, delivery_cost_basis, model, cost_usd, latency_ms)** — Base declarada del precio/costo sugeridos + telemetría LLM del run.  
  _valor marketing:_ bajo — trazabilidad glass-box

### 1.2 — `step_thread (persistido; el HILO conversacional del paso 1.2 + pre-decisiones del usuario)`  
_creado por: lib/schemas/step-thread.ts (PaqueteThreadState/PaquetePre); escrito por components/phase1/paquete-thread.tsx vía upsertArtifact_

- **stage** — Etapa del hilo: pre | armando | dispose | signed.  
  _valor marketing:_ bajo — estado de flujo
- **pre.central (name, description, why, state)** — El entregable central pre-decidido por el usuario ANTES de ver el paquete (ley 5 — la propuesta se diseña alrededor).  
  _valor marketing:_ alto — la definición del producto en palabras validadas por el operador
- **pre.price_usd / pre.cost_usd** — Precio objetivo y costo de servir confirmados por el usuario en etapa A.  
  _valor marketing:_ medio — números de partida que gobiernan el candado
- **pre.price_research** — Copia del estudio de precio real (PricingResearch) embebida en el hilo.  
  _valor marketing:_ alto — mismo valor que en product_economics: competencia real con fuentes
- **pre.cost_breakdown** — Copia del desglose de costo de servir (CostBreakdown) embebida en el hilo.  
  _valor marketing:_ bajo — interno
- **messages[] (id, role sandi|user, md, block, at)** — La conversación completa del paso en markdown ligero; block = descriptor de bloque interactivo (pre_decisiones|stack_cards|locks|client_view|signature).  
  _valor marketing:_ medio — memoria de CÓMO se llegó a la oferta; las objeciones/preguntas del operador ahí son insight de voz-de-cliente
- **cowork_rounds** — Rondas de conversación libre consumidas (tope duro server-side).  
  _valor marketing:_ bajo — control de costos

### 1.2-pre (efímero → embebido) — `PricingResearch — estudio de precio REAL (respuesta de API; se persiste dentro de product_economics.price_research y step_thread.pre.price_research)`  
_creado por: lib/wizard/phase1/pricing-research.ts + app/api/phase1/pricing-research/route.ts (web_search sobre competidores firmados en 0.4; solo LEE, el usuario decide)_

- **competitors[] (name, monthly_usd, raw_price, note, source_url)** — Competidores reales normalizados a $/mes (o por unidad si venta única), con precio crudo y URL fuente.  
  _valor marketing:_ ALTO — tabla de mercado verificable: alimenta páginas de pricing, FAQs de precio y decisiones de posicionamiento (aunque el copy nunca compara marcas)
- **floor_usd / suggested_usd / ceiling_usd** — Rango defendible: piso, sugerido (cruce valor×mercado) y techo.  
  _valor marketing:_ alto — marco para promos/anclas sin salirse de lo que el cliente compara
- **market_position** — below_market | at_market | above_market — posición elegida vs el mercado.  
  _valor marketing:_ alto — define el tono del framing de precio (accesible vs premium)
- **rationale** — Justificación glass-box citando los 3 pilares (ecuación · oferta · competencia), razonada sobre el buyer persona completo.  
  _valor marketing:_ alto — el argumento de 'por qué este precio' en lenguaje reutilizable
- **evidence_basis** — 1 frase honesta: qué confirmó la web vs qué queda estimado.  
  _valor marketing:_ medio — control de qué cifras son citables en público

### 1.2-pre (efímero → embebido) — `CostBreakdown — desglose del costo de servir (respuesta de API; se persiste dentro de product_economics.cost_breakdown y step_thread.pre.cost_breakdown)`  
_creado por: lib/wizard/phase1/cost-estimate.ts + app/api/phase1/cost-estimate/route.ts (dinámico por patrón de negocio; pasarela Stripe 2.9%+$0.30 calculada en código)_

- **lines[] (label, monthly_usd, basis)** — Cada componente del costo marginal por cliente/unidad (materiales, amortización de molde, merma, comisiones de marketplace, IA/infra…) con el supuesto del que sale.  
  _valor marketing:_ bajo — interno; útil solo para contenido de transparencia radical o storytelling de 'cómo se hace'
- **payment_mode** — direct (el sistema añade Stripe) | marketplace (las comisiones van como líneas) | none — quién pone la comisión de pago.  
  _valor marketing:_ bajo — evita doble contabilidad; revela el canal de venta
- **note** — 1 frase de lectura del total.  
  _valor marketing:_ bajo
- **evidence_basis** — Qué es estimado vs medido.  
  _valor marketing:_ bajo — honestidad interna
- **(derivados en código) gatewayCost / costTotal** — Comisión de pasarela sobre el precio y total mensual por cliente (líneas + pasarela si aplica).  
  _valor marketing:_ bajo — alimenta el candado de margen

### 1.3 — `risk_urgency (persistido client-side; decisión ÉTICA del usuario sobre garantía/urgencia/desplazamiento)`  
_creado por: lib/schemas/offer.ts (RiskUrgency); editado/firmado en components/phase1/offer-steps.tsx; semillas vienen de offer_stack.suggestions_

- **risk_reversal.choice** — unconditional | conditional | none — tipo de garantía elegido.  
  _valor marketing:_ alto — define si el copy puede llevar reversión de riesgo y de qué tipo
- **risk_reversal.statement** — El texto de la garantía (condiciones y números exactos).  
  _valor marketing:_ ALTO — se renderiza VERBATIM en la página de oferta y en todo copy de cierre; es el ataque al eje 'probabilidad'
- **risk_reversal.honor_confirmed** — Confirmación explícita de que el operador honrará la garantía (gate ético).  
  _valor marketing:_ medio — licencia para usar la garantía en público
- **urgency.choice / statement / genuine_reason** — window|none, el texto de urgencia y la razón GENUINA (ventana real del comprador) que la sostiene.  
  _valor marketing:_ ALTO — urgencia honesta lista para CTAs y campañas de lanzamiento; genuine_reason blinda contra humo
- **scarcity.type** — Tipo de escasez (default 'none').  
  _valor marketing:_ bajo — hoy sin uso activo
- **displacement_framing.replacement_narrative** — Qué hábito/solución actual REEMPLAZA la oferta (reemplaza, no añade).  
  _valor marketing:_ ALTO — ángulo de contenido completo: 'deja de hacer X, haz esto en su lugar'
- **displacement_framing.cost_of_continuing_current_path** — El costo (en llano) de seguir por el camino actual.  
  _valor marketing:_ ALTO — el 'costo de no actuar': materia prima de hooks de dolor y secciones why-now
- **status / signed_at / metadata** — draft|signed, fecha, metadatos.  
  _valor marketing:_ bajo — gobernanza

### 1.4 — `offer_spec (persistido client-side; consolidación: nombre + precio final)`  
_creado por: lib/schemas/offer.ts (OfferFinal); editado/firmado en components/phase1/offer-steps.tsx; leído por Fase 2 y por pricing/cost como fuente del productName_

- **name** — El nombre del producto/oferta.  
  _valor marketing:_ ALTO — la marca del producto: aparece en cada pieza de contenido
- **name_status** — working | final — madurez del nombre.  
  _valor marketing:_ medio — avisa si el nombre aún puede cambiar antes de producir contenido masivo
- **pricing.price_point_usd** — El precio final justificado que sella la oferta.  
  _valor marketing:_ ALTO — la única cifra de costo permitida en el copy
- **pricing.price_anchor.anchor_statement** — Frase de anclaje del precio (cómo se enmarca el número).  
  _valor marketing:_ alto — el framing del precio para páginas y objeciones de costo
- **status / signed_at / metadata** — draft|signed, fecha, metadatos.  
  _valor marketing:_ bajo — gobernanza

### 1.4 — `offer_statement (persistido server-side; LA página de oferta ≤350 palabras — alimenta TODO el copy de Fase 2)`  
_creado por: lib/wizard/statement-proposal.ts + app/api/phase1/offer-statement/route.ts (upsertArtifactContent phase_1/1.4/offer_statement); requiere 1.2 y 1.3 firmados_

- **markdown** — La página única de oferta en markdown: para quién / qué recibes (por funcionalidad) / reemplaza-no-añade / sin riesgo (garantía verbatim) / por qué ahora / UN CTA — en UN solo idioma (el del mercado).  
  _valor marketing:_ ALTO — es el artefacto de marketing por excelencia: la fuente canónica de la que Fase 2 deriva hooks, posts, anuncios y páginas
- **language** — Idioma de la página ('auto' al generarse; implícito del launch focus — US→inglés).  
  _valor marketing:_ alto — gobierna el locale de todo el copy derivado
- **format / schema_version** — 'markdown' y versión del shape.  
  _valor marketing:_ bajo — técnico
- **metadata (model, cost_usd)** — Modelo LLM y costo de la generación.  
  _valor marketing:_ bajo — trazabilidad de costos

## phase_2 (Contenido) — 8 artefactos guardados vía upsertArtifact en project_phase_artifacts: 2.0 brand_voice y 2.1 content_mix son COMPARTIDOS del comprador (avatar_key=''); 2.0.5 brand_visual_identity es compartido y se escribe desde El Estudio; 2.2–2.5 son POR AVATAR (avatar_key=key del avatar activo); 2.6 content_plan es la consolidación/firma del gate por avatar. Escritores: components/phase2/phase2-thread.tsx + app/api/phase2/step-proposal/route.ts (pasos 2.0–2.5, mapeo P2_ARTIFACT en lib/wizard/phase2/canon.ts), app/api/estudio/visual-identity/route.ts (2.0.5), app/projects/[projectId]/phase-2/page.tsx (2.6). Todos los schemas 2.0–2.5 en lib/schemas/content-plan.ts son .loose() (admiten campos extra del run fundacional) y comparten el trío status/signed_at/metadata.

### 2.0 — `brand_voice`  
_creado por: lib/schemas/content-plan.ts (BrandVoice) · propuesto por app/api/phase2/step-proposal/route.ts · guardado por components/phase2/phase2-thread.tsx (compartido, avatar_key='')_

- **schema_version** — Versión del schema del artefacto (default 'v1').  
  _valor marketing:_ bajo — plomería de compatibilidad, no informa contenido
- **archetype_primary** — Arquetipo de marca principal (uno de los 12 junguianos: sage, caregiver, hero, creator, ruler, magician, explorer, rebel, innocent, everyman, lover, jester).  
  _valor marketing:_ alto — define la personalidad de TODA pieza; es el molde que hace que cientos de posts suenen a una sola voz
- **archetype_secondary** — Arquetipo secundario opcional que matiza al primario (nullable).  
  _valor marketing:_ medio — añade matiz al tono cuando el primario solo se queda plano
- **archetype_rationale** — Por qué ese arquetipo: cita los trabajos emocional Y social de la persona firmada de Fase 0.  
  _valor marketing:_ medio — justifica la voz ante el operador y ancla decisiones futuras de tono
- **brand_promise_public** — La promesa de marca en UNA frase de cara al cliente; idealmente una quote literal del research.  
  _valor marketing:_ alto — es la columna vertebral del copy: headline, bio, cierre de piezas
- **brand_promise** — La promesa en formato interno completo (versión larga para uso interno, nullable).  
  _valor marketing:_ medio — contexto interno para redactar sin diluir la promesa pública
- **tone_descriptors** — Array de ~5 descriptores del tono (ej: directo, cálido, sin jerga).  
  _valor marketing:_ alto — se inyectan en cada prompt de generación de copy para mantener el sonido
- **lexicon.preferred_terms** — 6-10 términos que la marca SIEMPRE usa (diccionario positivo).  
  _valor marketing:_ alto — vocabulario obligatorio que hace reconocible el copy pieza a pieza
- **lexicon.prohibited_terms** — 8-12 términos vetados, incluyendo el vocabulario que quemó al avatar (jerga de gurús, etc.).  
  _valor marketing:_ alto — filtro duro: cada gancho y pieza se chequea contra esta lista antes de salir
- **consistency_rules_plain** — 5 reglas TESTEABLES de consistencia (cero prohibidos, ≥1 preferido, máx un '!', números con fuente, titulares ≤12 palabras).  
  _valor marketing:_ alto — QA automático del copy: reglas verificables por máquina antes de publicar
- **status** — Estado del artefacto ('draft' → 'signed...'); voiceGateReady exige arquetipo + promesa + ≥3 tonos.  
  _valor marketing:_ bajo — control de flujo del wizard, no contenido
- **signed_at** — Timestamp ISO de la firma del operador (nullable).  
  _valor marketing:_ bajo — auditoría de cuándo quedó en piedra
- **metadata** — Bolsa libre clave→valor para datos extra.  
  _valor marketing:_ bajo — extensión sin schema, contenido impredecible

### 2.0.5 — `brand_visual_identity`  
_creado por: lib/estudio/visual-identity.ts (tipo VisualIdentity) · propuesto/importado/editado y guardado por app/api/estudio/visual-identity/route.ts (compartido, avatar_key='')_

- **palette[]** — 4-5 colores de marca, cada uno {name: nombre descriptivo en inglés que un generador de imágenes entiende, hex: color exacto, role: fondo/primario/acento/texto}.  
  _valor marketing:_ alto — se pega como 'Strict color palette' a CADA prompt de imagen: es lo que hace que todas las piezas se vean de la misma marca
- **style** — El medio + look visual concreto y repetible (ej: 'editorial documentary photography, natural warm light, film grain').  
  _valor marketing:_ alto — define el acabado de toda imagen generada; sin él cada foto sale de un universo distinto
- **mood** — 3-4 palabras del sentimiento visual, alineadas a la voz (array).  
  _valor marketing:_ alto — traduce el arquetipo verbal a emoción visual en cada prompt
- **composition** — Reglas recurrentes de encuadre/espacio (ej: espacio negativo, sujeto descentrado).  
  _valor marketing:_ medio — da consistencia de layout entre piezas; útil sobre todo en carruseles
- **motifs** — 2-4 elementos visuales que se repiten y hacen reconocible la marca (manos, texturas, un objeto ancla).  
  _valor marketing:_ alto — la firma visual repetida: lo que hace que el scroll reconozca la marca sin leer
- **typography** — El feel tipográfico para textos superpuestos en imágenes.  
  _valor marketing:_ medio — clave para text-overlays (el gancho como texto sobre la imagen, doctrina §2.7)
- **do[]** — Lista de prácticas visuales permitidas/deseadas.  
  _valor marketing:_ medio — guía positiva para el generador y para el operador al aprobar
- **dont[]** — Lista de vetos visuales (degradados arcoíris, sonrisas stock…); viaja como 'Avoid:' en el prompt.  
  _valor marketing:_ alto — evita el look genérico de stock que mata la coherencia de marca
- **reference_image_url** — URL del logo/personaje de referencia; enruta la generación a FLUX Kontext (~92% de fidelidad de identidad).  
  _valor marketing:_ alto — permite personaje/logo consistente entre imágenes, imposible solo con texto
- **character** — BrandCharacter: {description: descripción fija de la protagonista de marca, voice?: su voz}; el personaje persistente (D-V2) inyectado en cada develop.  
  _valor marketing:_ alto — la misma protagonista en TODAS las piezas crea narrativa serial y reconocimiento

### 2.1 — `content_mix`  
_creado por: lib/schemas/content-plan.ts (ContentMix) · app/api/phase2/step-proposal/route.ts + components/phase2/phase2-thread.tsx (compartido, avatar_key='')_

- **schema_version** — Versión del schema (default 'v1').  
  _valor marketing:_ bajo — plomería
- **market_photo_pct** — La foto MEDIDA del mercado desde el estudio 0.2: % de audiencia en cada momento de conciencia {most_aware_pct, solution_aware_pct, problem_aware_pct, unaware_pct} (nullable).  
  _valor marketing:_ alto — el dato real de dónde está la gente; base contra la que se justifica toda desviación estratégica
- **target_mix** — El reparto DECIDIDO del esfuerzo de contenido por momento mental (los mismos 4 %; debe sumar 100).  
  _valor marketing:_ alto — dicta literalmente cuántas de cada 10 piezas van a cada momento de conciencia: es el presupuesto editorial
- **per_row_why** — Una frase corta de razón por momento (most_aware/solution_aware/problem_aware/unaware): qué tan rápido/barato convierte cada uno.  
  _valor marketing:_ medio — el porqué llano de cada fila; educa al operador y guía ajustes futuros
- **deviation_justification** — Justificación escrita obligatoria cuando target_mix se aleja >30 puntos de la foto medida (candado mixGateReady).  
  _valor marketing:_ medio — evidencia de decisión estratégica consciente vs error; no genera copy
- **rationale** — Máx 3 frases llanas de por qué el reparto se aleja de la foto (mover peso del dormido al que ya siente el dolor).  
  _valor marketing:_ medio — la narrativa estratégica del mix, reutilizable al explicar el plan
- **status** — draft/signed; candados: suma=100, desviación>30 exige justificación, unaware>0 si la estrategia crea demanda.  
  _valor marketing:_ bajo — control de flujo
- **signed_at** — Timestamp ISO de firma (nullable).  
  _valor marketing:_ bajo — auditoría
- **metadata** — Bolsa libre clave→valor.  
  _valor marketing:_ bajo — extensión

### 2.2 — `channel_journey_matrix`  
_creado por: lib/schemas/content-plan.ts (ChannelMatrix + MatrixChannel) · app/api/phase2/step-proposal/route.ts + components/phase2/phase2-thread.tsx (POR AVATAR, anclado en su where_we_meet)_

- **schema_version** — Versión del schema (default 'v1').  
  _valor marketing:_ bajo — plomería
- **channels[].key** — Identificador estable del canal (ej: 'blog_seo').  
  _valor marketing:_ bajo — clave técnica para cruces con pilares/calendario
- **channels[].label** — Nombre en llano del canal ('Blog/SEO', 'Instagram', 'TikTok'…).  
  _valor marketing:_ medio — el nombre operativo que aparece en calendario y piezas
- **channels[].big_surface** — Marca de gran superficie (Instagram/TikTok): entran por defecto por ley del operador; excluirlas exige caso escrito.  
  _valor marketing:_ medio — codifica la regla de distribución de máximo alcance
- **channels[].enabled** — Si el canal está encendido en el plan (candado: mínimo 3 encendidos).  
  _valor marketing:_ alto — determina DÓNDE se publica de verdad; el calendario solo alimenta canales encendidos
- **channels[].off_reason** — El caso escrito obligatorio para apagar una gran superficie (nullable).  
  _valor marketing:_ bajo — trazabilidad de la decisión, no produce contenido
- **channels[].journey_moments** — Qué momento(s) del viaje del cliente cubre el canal ('despierta → compara → decide').  
  _valor marketing:_ alto — evita el error clásico de que el canal de despertar pida la venta: cada pieza sabe su función en el funnel
- **channels[].what_gets_published** — 2-3 frases concretas de qué tipo de piezas salen en ese canal.  
  _valor marketing:_ alto — el brief editorial por canal: define el formato y sustancia de cada pieza a producir
- **channels[].cadence_floor** — Cadencia mínima comprometida, SIEMPRE en formato 'N por semana' (regla del operador).  
  _valor marketing:_ alto — el piso de producción que dimensiona el calendario y la carga semanal
- **channels[].cadence_target** — Cadencia meta a la que se aspira ('1-2 por semana').  
  _valor marketing:_ medio — la ambición de escala cuando la producción lo permita
- **channels[].best_windows** — Mejores ventanas horarias/días para publicar en ese canal (de estudios con fuentes).  
  _valor marketing:_ alto — cuándo soltar cada pieza para maximizar alcance; alimenta las notificaciones del calendario
- **channels[].how_measured** — La métrica concreta de éxito del canal (obligatoria y no vacía en cada canal encendido — Fase 4 la necesita).  
  _valor marketing:_ alto — cierra el loop: define qué dato decide si el canal funciona (ventas, no likes)
- **channels_declared** — Lista derivada de labels de canales encendidos (la calcula parseP2Proposal).  
  _valor marketing:_ bajo — vista rápida redundante con channels[].enabled
- **notifications_commitment** — El compromiso del producto: 'cada slot del calendario te avisará con el copy listo adentro'.  
  _valor marketing:_ medio — contrato de UX de entrega, no informa piezas
- **status / signed_at / metadata** — Trío estándar: estado draft/signed, timestamp de firma, bolsa extra.  
  _valor marketing:_ bajo — control de flujo y auditoría

### 2.3 — `pillars`  
_creado por: lib/schemas/content-plan.ts (PillarSet + Pillar) · app/api/phase2/step-proposal/route.ts + components/phase2/phase2-thread.tsx (POR AVATAR, construido desde sus forces_of_progress)_

- **schema_version** — Versión del schema (default 'v1').  
  _valor marketing:_ bajo — plomería
- **pillars[].id** — Identificador estable del pilar (PILLAR_A..D); lo referencian atomizaciones y ganchos.  
  _valor marketing:_ bajo — clave técnica de cruce entre artefactos
- **pillars[].name** — Nombre evocador del territorio de contenido, en el idioma del usuario.  
  _valor marketing:_ alto — el título del territorio temático que organiza todo el volumen de contenido
- **pillars[].force_attacked** — La fuerza psicológica del avatar que ataca: ongoing_pains (dolores crónicos) | triggers (momentos de rabia) | anxiety (miedos) | habit (hábitos). Candado: las 4 cubiertas, una por pilar.  
  _valor marketing:_ alto — cada pieza sabe exactamente qué músculo del cliente empuja; garantiza que ninguna palanca de compra quede sin contenido
- **pillars[].mode** — REINFORCE (la fuerza ya la cubre la oferta → el contenido repite sus palabras exactas) | RESOLVE (la oferta la delegó al copy → el contenido es el único que la ataca) | mixed.  
  _valor marketing:_ alto — evita disonancia oferta↔contenido y piezas duplicadas: define si el pilar amplifica o resuelve
- **pillars[].what_it_says** — De qué habla el pilar, en 1-2 líneas.  
  _valor marketing:_ alto — el brief temático del que salen anclas, derivados y ganchos
- **pillars[].channels** — Keys de los canales de la matriz donde vive este pilar.  
  _valor marketing:_ medio — mapea territorio→distribución; útil al armar el calendario
- **status / signed_at / metadata** — Trío estándar draft/signed + timestamp + bolsa extra.  
  _valor marketing:_ bajo — control de flujo

### 2.4 — `atomization_map`  
_creado por: lib/schemas/content-plan.ts (AtomizationMap + Atomization) · app/api/phase2/step-proposal/route.ts + components/phase2/phase2-thread.tsx (POR AVATAR)_

- **schema_version** — Versión del schema (default 'v1').  
  _valor marketing:_ bajo — plomería
- **ratio_policy_plain** — La política dar:pedir en llano (Vaynerchuk): de cada N piezas cuántas DAN valor vs cuántas PIDEN la venta; default 3:1, 5:1 si el avatar viene quemado de gurús.  
  _valor marketing:_ alto — regula la proporción venta/valor de todo el calendario; protege la confianza de la audiencia
- **atomizations[].pillar_id** — El pilar al que pertenece esta atomización (uno por pilar firmado, los 4).  
  _valor marketing:_ bajo — clave de cruce con pillars
- **atomizations[].long_form.title_working** — Título de trabajo de la pieza ANCLA (artículo/video largo), en el idioma del avatar y anclado en keywords reales.  
  _valor marketing:_ alto — es la pieza madre de la semana: su título define el SEO y la sustancia de todos los derivados
- **atomizations[].long_form.asset_id** — Referencia al asset producido de la ancla cuando ya existe (nullable).  
  _valor marketing:_ bajo — enlace de producción, no informa contenido nuevo
- **atomizations[].derivatives[]** — Las piezas chicas derivadas de la ancla: {kind: '<canal> (<formato>)' ej. 'Reel de Instagram (video)' / 'email' / 'respuesta de foro', note: 1 frase concreta}. Cada derivado se ADAPTA al formato real de su canal×avatar (candado: ≥5 por pilar).  
  _valor marketing:_ alto — la lista literal de entregables de la semana por pilar, cada uno ya con canal y formato decididos
- **atomizations[].derivatives_summary** — Resumen en texto de los derivados (forma alternativa compatible con el run fundacional, nullable).  
  _valor marketing:_ medio — fallback legible cuando no hay lista estructurada
- **atomizations[].derivatives_count** — Conteo de derivados (forma alternativa; el candado usa count ?? derivatives.length).  
  _valor marketing:_ bajo — número para el gate, redundante con la lista
- **status / signed_at / metadata** — Trío estándar draft/signed + timestamp + bolsa extra.  
  _valor marketing:_ bajo — control de flujo

### 2.5 — `hook_library`  
_creado por: lib/schemas/content-plan.ts (HookLibrary + Hook) · app/api/phase2/step-proposal/route.ts + components/phase2/phase2-thread.tsx (POR AVATAR; regeneración quirúrgica por gancho vía buildHookRegenSystem)_

- **schema_version** — Versión del schema (default 'v1').  
  _valor marketing:_ bajo — plomería
- **hooks[].hook_id** — Identificador estable del gancho (ej: H_A_01).  
  _valor marketing:_ bajo — clave para editar/regenerar/medir un gancho puntual
- **hooks[].template** — La plantilla de copywriting del gancho: contrarian, problem_agitate, curiosity_gap, stat_lead, question, myth_bust, story_open, direct_callout (candado: ≥4 plantillas distintas en la biblioteca; glosas en HOOK_TEMPLATES).  
  _valor marketing:_ alto — garantiza variedad estructural para no sonar a disco rayado y permite auditar qué moldes convierten
- **hooks[].text** — El gancho literal: las primeras 1-2 frases de la pieza, EN EL IDIOMA DEL MERCADO, filtrado contra la voz (cero prohibidos) y las anti-personas (cero promesas de enriquecerse).  
  _valor marketing:_ alto — copy publicable tal cual: el primer segundo que decide la mayoría de las impresiones; también sirve de texto-overlay
- **hooks[].pillar** — El pilar al que pertenece (candado: ≥10 ganchos por pilar, biblioteca de ~40).  
  _valor marketing:_ medio — asegura que cada territorio tiene arsenal de aperturas propio
- **hooks[].in_use** — Flag de si el gancho ya está asignado a una pieza (default false); base de la memoria de rendimiento ('los ganadores se quedan, los que no convierten se jubilan con datos').  
  _valor marketing:_ alto — evita repetir ganchos y habilita el loop de aprendizaje por rendimiento (lo consume la migración de inteligencia temporal)
- **status / signed_at / metadata** — Trío estándar draft/signed + timestamp + bolsa extra.  
  _valor marketing:_ bajo — control de flujo

### 2.6 — `content_plan`  
_creado por: app/projects/[projectId]/phase-2/page.tsx (GateSignature G-Phase-2, POR AVATAR) — no tiene schema en content-plan.ts: es un sello, no un contenedor_

- **schema_version** — Versión ('v1').  
  _valor marketing:_ bajo — plomería
- **avatar_key** — El avatar cuyo plan de contenido se consolida y firma.  
  _valor marketing:_ bajo — llave de segmentación, redundante con avatar_key de la fila
- **consolidates** — Lista de los 6 artefactos que este plan consolida: brand_voice, content_mix, channel_journey_matrix, pillars, atomization_map, hook_library.  
  _valor marketing:_ bajo — manifiesto de qué quedó en piedra; no contiene los datos (viven en cada artefacto)
- **status** — 'signed' — la firma del gate de fase que desbloquea la publicación (Fase 3).  
  _valor marketing:_ medio — es el interruptor que dice que ESTE avatar ya puede entrar a producción/calendario
- **signed_at** — Timestamp ISO del cierre de la fase para ese avatar.  
  _valor marketing:_ bajo — auditoría

