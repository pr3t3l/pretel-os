# spec_Craft_Reels — La experiencia rediseñada del Estudio de Reels (UX + pipeline de roles)

> **Estado:** PARA FIRMA · **Fecha:** 2026-07-15
> **Fuentes:** `docs/research/2026-07-15_craft_reels_etapas_y_perfiles.md` (craft + etapas + perfiles) · mapa del sistema actual (trace de código 2026-07-15) · investigación UX (Arcads, HeyGen, progressive disclosure, human-in-the-loop checkpoints) · lecciones LIDR (`course:lidr-ai-engineer`) · curso AvatarHype (`specs/AvatarHype Classes/`).
> **Problema:** los reels salen "correctos pero muertos" (sin chispa humana) Y la experiencia está fragmentada: decisiones creativas partidas entre Ángulos y Director ①, tres vocabularios de estilo solapados, 4 superficies para un reel, y la plataforma (IG/TikTok) no cambia nada visible.

---

## 0. El principio rector

**El usuario elige QUIÉN, DÓNDE y PARA QUÉ — con opciones VISUALES y concretas. Papandi decide CÓMO — con el pipeline de roles — y lo muestra en glass-box para corregir.**

Lo que hoy pedimos al usuario (apertura visual entre 16, estilo entre 5, concepto entre 12, ritmo, cámara, loop…) son decisiones de **director de cine** que un dueño de negocio no sabe tomar — por eso se sienten complicadas Y por eso salen reels planos (elige lo seguro). La investigación es unánime: las mejores herramientas (Arcads: pega guion → elige actor DE UNA GALERÍA VISUAL con el ambiente incluido → genera) piden 2-3 decisiones concretas y el resto es default inteligente con override. Progressive disclosure reduce el tiempo-a-primera-acción 30-50% sin perder descubribilidad.

**Regla de diseño:** ninguna opción abstracta ("ritmo con golpe", "zoom punch") en la ruta por defecto. Toda elección del usuario es (a) una persona con cara, (b) un momento/lugar con miniatura, (c) una plataforma con consecuencias visibles, o (d) texto libre suyo. Lo abstracto vive dentro de los roles LLM y en "Ajustes finos" (colapsado).

---

## 1. La experiencia nueva — recorrido completo

### 1.1 Identidad → se convierte en EL CASTING (una vez por marca)

Hoy los avatares nacen de un prompt que ordena literalmente "head-and-shoulders, neutral friendly expression, clean simple background" — el retrato de estudio perfecto que la doctrina identifica como el gatillo del reflejo "esto es un anuncio" (lo-fi vence al pulido el 84% de las veces). Cambios:

1. **Avatar = persona + SU MUNDO, creado en DOS pasos (decisión del operador 2026-07-15):**
   - **Paso A — la persona:** generar/subir el **retrato ancla** (identidad facial — lo que Kling necesita en `frontal_image_url`), editar el prompt glass-box, regenerar hasta convencer, **aprobar la CARA**. Cuesta 1 imagen por intento — nada del paquete se genera antes de esta aprobación (no se pierde plata en mundos de una cara equivocada).
   - **Paso B — su mundo (solo tras aprobar la cara):** botón «Generar su mundo → 6 momentos (~$0.90)». **Un paquete de 6 MOMENTOS** (fotos mid-action, misma cara vía cadena de edición desde el ancla): el usuario **elige CUÁLES 6 de un catálogo** (cama+teléfono, cocina, carro parqueado, espejo del baño, caminando, escritorio, gimnasio, taller, tienda…) — Papandi **sugiere los 6 según el mundo del COMPRADOR** del proyecto (p. ej. vendedora Etsy: empacando pedidos, mesa con laptop). Cada momento: prompt editable antes de gastar, **regenerable individualmente** (5 buenos + 1 malo = repites solo 1), o **reemplazable por foto real subida**. Generadas con 6C + doctrina mid-action (en mitad de la acción, brazo selfie visible cuando aplique, encuadre imperfecto, luz plana natural — NO estudio). **Estos momentos son las fichas visuales que el usuario tocará en el Estudio.**
2. **Los SETS no mueren — se vuelven LUGARES (la mitad "lugar" de la ecuación: momento = persona × lugar × acción).** La biblioteca queda con dos estantes: **Personas** (ancla + momentos) y **Lugares** (los sets de hoy: el taller de la marca, la tienda, la cocina "oficial"). Los lugares sirven para: (a) ser escenario de momentos de las personas (momento = Ana × tu taller × empacando), (b) **b-roll y tomas de producto SIN gente** (doctrina 90% b-roll / 10% cara — los lugares son la materia prima del b-roll), (c) reels animados/voz-en-off sin persona. El `cast_override` de campañas sigue igual (persona + lugar por campaña).
3. **Dial de realismo por avatar:** `Pulida ◄─────► Real` (default: Real). "Real" inyecta la imperfección controlada del curso (textura de piel real, luz de casa, framing casual) en TODAS las generaciones de ese avatar. "Pulida" queda para marcas que lo pidan (B2B formal).
4. **La voz sigue por-personaje** (sin cambio).
5. Se desambigua el vocabulario: **"Audiencias"** (personas de 0.3, a quién le hablas) vs **"Cast"** (quién sale en cámara). Hoy ambos se llaman avatares en la misma página.

### 1.2 Ángulos → SOLO elige qué producir (se adelgaza — SOLO para video)

En Ángulos, para piezas de VIDEO queda únicamente: **ángulo → canal (chips actuales) → campaña/fase si aplica → botón "🎬 Producir →"**. Se **MUDAN al Estudio** (y se funden ahí): 🎬 Apertura visual y 💬 Estilo de apertura. Ángulos vuelve a ser el menú, no un pre-estudio. (Esto elimina la fricción #2 del mapa: dos muros de opciones en dos pantallas.)

**Para NO-video (blog, carrusel, imagen, email, pin…) NADA cambia:** hoy ya se saltan el Director (develop directo → panel de la pieza) y siguen igual. El 💬 Estilo de apertura **se queda en Ángulos solo para no-video** (es su única perilla creativa y ahí funciona). La 🎬 Apertura visual ya era video-only. Un mini-brief para no-video queda fuera de alcance de este spec (spec futuro si hace falta).

### 1.3 El Estudio — 5 pasos, 2 compuertas, 1 brief

**El Estudio es EL MISMO para IG Reel, TikTok y YT Short** — la plataforma es un dato del brief con consecuencias visibles (§1.4).

```
① EL BRIEF (1 pantalla, 3 decisiones visuales + extras colapsados)
   │  «Papandi produce» ──► corre el PIPELINE DE ROLES (§2) — ~30-60s, centavos
   ▼
② GUION + PLAN VISUAL (COMPUERTA 1 — la única de "papel")
   │  aprueba / edita cajas / regenera un beat
   ▼
③ IMÁGENES (COMPUERTA 2 — keyframes mid-action, ya existe)
   ▼
④ CLIPS (genera + cosecha, ya existe, costo visible)
   ▼
⑤ EDICIÓN (editor actual + zoom progresivo auto + check de cadencia)
   ▼
   PUBLICAR → Agenda (como hoy)
```

**① EL BRIEF — la pantalla nueva (reemplaza el Director ① actual y los pickers de Ángulos):**
- **¿Quién?** — chips con FOTO de los personajes aprobados del cast (+ "🎲 Papandi inventa una persona" para UGC libre). Preseleccionado: el default de marca o el cast_override de la campaña.
- **¿Dónde/en qué momento?** — chips con MINIATURA de los momentos del avatar (cama · cocina · carro · espejo · caminando · escritorio · "✨ Papandi elige"). Esto reemplaza a la vez: concepto (12), ambiente (texto libre) y gran parte de la apertura visual — porque el momento ES el ambiente Y el arranque.
- **¿Para qué plataforma?** — chip IG Reel / TikTok / YT Short con sus consecuencias escritas al lado (§1.4).
- **Tu toque (opcional):** un campo de texto libre — "algo que quieras que diga/haga/muestre".
- **▸ Ajustes finos (colapsado — progressive disclosure):** ahí viven G1 (duración/ritmo/cámara/loop/CTA), tipo de reel (presentadora/ugc/animado), estilo de apertura manual, referencia visual 6C, dial de realismo por-pieza. Todo con default "Papandi decide". El usuario que nunca abre este panel obtiene la mejor calidad; el power user tiene todo.
- **Un botón: «Papandi produce el guion y el plan → ~$0.02».**

**② GUION + PLAN VISUAL — una compuerta, no dos muros.** El pipeline de roles (§2) ya corrió. El usuario ve:
- El **guion por beats** (las cajas editables de hoy, agrupadas por beat con su presupuesto de tiempo).
- El **plan visual del director**: qué se ve en cada clip (momento/ambiente), el **money shot** marcado ⭐, y el **gancho de 3 capas** del clip 1 (primer frame + línea hablada + texto overlay) — cada capa editable.
- El **sello del auditor** (glass-box): "✓ Auditado: corregí 2 escenas quietas, recorté el guion de 4.1 a 2.3 palabras/seg" — el usuario VE que hubo control de calidad, sin tener que hacerlo él.
- Acciones: **Aprobar →** / editar cualquier caja / **↻ regenerar solo este beat** (no todo).

**③–⑤** como hoy, con las mejoras de doctrina: keyframes mid-action (§3.2), zoom progresivo automático en el burn, auditoría de cadencia 2-3s en la edición.

### 1.4 La plataforma por fin SE VE (doctrina de 00_CONTEXTO_MAESTRO §3)

En el brief, el chip de plataforma muestra y aplica:
- **TikTok** — "El video dice tus keywords EN VOZ ALTA (el ASR las indexa) · 11-18s ideal · diseñado para completarse".
- **IG Reel** — "Diseñado para que lo REENVÍEN (sends per reach es la señal #1) · 7-15s ideal · momento compartible marcado en el plan".
- **YT Short** — "Construido para el LOOP (el final empata con el inicio) · viewed vs swiped".
El guionista (§2) recibe la doctrina del canal como restricción dura, y el plan visual marca el elemento correspondiente (la frase-keyword / el momento compartible / el empate de loop).

---

## 2. El pipeline de roles (lo que corre entre ① y ②)

**Mapa contra las 8 etapas del research** (`2026-07-15_craft_reels_etapas_y_perfiles.md §5`) — nada se pierde, cada etapa vive en su lugar: etapas **①-④** (estratega, guionista, director, auditor) = los 4 roles LLM de esta sección; etapa **⑤ keyframes** = paso ③ del Estudio (doctrina en §3.2); etapa **⑥ video** = paso ④ del Estudio (§3.1); etapa **⑦ editor de retención** = paso ⑤ del Estudio (§3.3); etapa **⑧ analista** = §7 (F5, el lazo de mejora).

Cadena de llamadas separadas (lecciones LIDR: lost-in-the-middle mata la llamada única; cada rol con system prompt de 4 dimensiones — rol + tarea + uso del contexto + formato — y estructura DISTINTA entre roles, no copias; CAG 3-7 ejemplos en el formato exacto del output; instrucciones al inicio, restricciones al final, query al final; anti-relleno: campo sin evidencia = null, nunca inferir).

Resumen de la cadena (el contrato completo de cada rol está en §2.A–2.D):

| Rol | Modelo | Entrada | Salida (estructurada) |
|---|---|---|---|
| **1. Estratega** (brief destilado) | barato | proyecto+ángulo+campaña+audiencia (todo lo que hoy se vuelca crudo) | brief creativo de ~15 líneas (§2.A) |
| **2. Guionista** | premium + CAG de guiones vivos | brief + momento elegido + toque del usuario | beats + gancho de 3 capas (§2.B) |
| **3. Director (plan visual)** | premium | guion + momentos del avatar + producto | Ficha de Continuidad + plan por clip + capa de actuación (§2.C) |
| **4. Auditor** (crítico) | DISTINTO del generador, barato | guion + plan + Ficha | issues estructurados; boss aplica con tope 2 iteraciones (§2.D) |

La salida del pipeline llena las MISMAS `design_spec.scenes[]` de hoy (más los campos nuevos de actuación) — **compatibilidad total con keyframes/clips/edición existentes.**

### 2.A Rol 1 — EL ESTRATEGA (brief destilado)

Reemplaza el volcado crudo de ~30 bloques por una destilación (lección LIDR: reformular antes de inyectar). **Campos del brief** (schema estructurado, siguiendo la Etapa 1 del curso):
- **Avatar vivo del comprador:** quién es, **3 dolores concretos**, qué ha intentado ya, el miedo profundo, la sensación deseada.
- **El ángulo firmado** (2.5) + el dolor específico de ESTE reel.
- **La venta** (de `offer_spec`/`offer_statement` 1.4, firmado): qué es el producto, la promesa, el **mecanismo** (por qué funciona), la oferta.
- **Formato elegido** entre los 5 probados de la industria: testimonial · problema/solución · demo (hook-demo-CTA) · GRWM/rutina · unboxing.
- **El mundo del comprador:** los ambientes donde vive su problema (alimenta la elección de momentos).
- **Doctrina del canal** (dura, §1.4) + **intent** (dar/pedir) + contexto temporal (radar).
- Regla anti-relleno: sin evidencia → `null`. Nunca inventar datos, estudios ni claims médicos (regla dura del curso).

### 2.B Rol 2 — EL GUIONISTA

Premium, con **CAG de 3-5 guiones VIVOS en el formato exacto del output** (fuentes: la librería de 33 guiones aprobados del curso + los 6 gold-standard de `UGC PROMPT ENGINE.md` — el modelo replica el formato que ve).

**Esqueleto de respuesta directa con presupuesto de tiempo por beat** (30s de referencia; 15s comprime el medio; nunca >35s):
`GANCHO 0-3s → PROBLEMA/AGITACIÓN 3-8s → MECANISMO/SOLUCIÓN (producto POR FUNCIÓN) 8-20s → PRUEBA (beat u overlay) → CTA 3-5s final` — cada beat etiquetado con su **intención emocional**.

**Los 9 patrones obligatorios del curso** (Etapa 4 de `Planificacion.txt`):
1. **HOOK = una verdad MÁS GRANDE que el cliente** — PROHIBIDO abrir con "Estás/Tu/Te/No sabes" (historia, dato biológico con número, creencia colectiva, dato contraintuitivo).
2. Dato técnico con **número concreto** (nunca "mucho"; siempre "20%").
3. Una **pregunta reflexiva** (la que el cliente se hace a sí mismo).
4. **Puntos suspensivos en 3-4 momentos** — el narrador piensa en voz alta (la cadencia humana; el enemigo del "2.5 palabras/seg SOSTENIDO" actual).
5. Frase **puente** al producto ("Por eso creamos…").
6. Producto por **FUNCIÓN**, cero adjetivos vacíos.
7. Beneficios en **3-4 frases telegráficas paralelas**.
8. **BISAGRA REFLEXIVA obligatoria** antes del cierre.
9. Cierre: retorno al gancho transformado / invitación suave.

**Reglas de lenguaje:** hablado grado ≤5 · contracciones · "pero/por eso", nunca "y entonces" · una idea por beat · 2-2.5 palabras/seg (140-170 WPM) · **test leer-en-voz-alta: "si suena a anuncio, está mal; si suena a alguien contándotelo en una cena, está bien"** · talking points, no sobre-guionizado (el asesino #1 de la autenticidad) · en UGC: muletillas ("a ver…", "es que…"), empezar a mitad de pensamiento, CTA de amigo ("yo lo estoy usando y ya"), cada guion entrega un VALOR (observación/verdad incómoda/mini-revelación), nunca "cómpralo ya".

**El gancho de 3 capas** (salida separada del guion, editable por capa en compuerta ②):
(a) **capa visual** — la acción física del primer segundo (vocabulario interno: los 16 `VISUAL_HOOKS` — falling_drop, walk_in, mid_action, object_to_camera, zoom_punch…); (b) **capa hablada** — la línea (con 2 variantes extra para testeo futuro); (c) **capa de texto overlay** — abre un curiosity gap que lo verbal NO resuelve (con power words). Las 3 capas disparan en el primer 1.5s (+35-45% retención a 3s vs una sola capa).

### 2.C Rol 3 — EL DIRECTOR (plan visual + actuación + continuidad)

Premium. Entrada: guion + los momentos del avatar + el producto (referencia de Media). **Piensa EN VOZ ALTA antes de llenar escenas** (el PASO 0 del curso, Etapa 5 — la pasada que produce "cine" en vez de "anuncio"):
1. **Metáfora visual central** (DIBUJABLE — "una columna que se ilumina en rojo donde duele" ✅, "la sensación de cansancio" ❌) y en qué 2-3 escenas se manifiesta.
2. **EL MONEY SHOT** — el momento icónico, diseñado explícitamente, colocado entre la escena 2-4; preferentemente producto-en-manos (§2.1).
3. **Arco visual en una frase** (p. ej. "íntimo → conceptual → real-pero-transformado").
4. **Contraste de planos OBLIGADO**: ≥1 plano abierto, 2 close-ups, 1 macro/detalle, 1 cenital, 1 conceptual — los clips 2-N no pueden ser homogéneos.
5. **Cierre circular**: la última escena = la primera transformada (habilita el loop).

**Por clip, llena las cajas actuales + los campos NUEVOS de actuación** (los 4 bloques de `Prompts VEO3-1.md` — donde vive la chispa):
- `accion`: la acción física **MIENTRAS habla** (manos ocupadas — regla GRWM); micro-evento a mitad en clips >4s; movimiento en el primer segundo (calm/still/sitting = inválido).
- `physics` (NUEVO): "decir natural no vale — hay que definirlo": *slight vertical bounce, subtle side-to-side sway, natural shoulder movement, inconsistent micro-movements, breathing that subtly affects motion and speech*.
- `behaviour` (NUEVO): empieza a mitad de pensamiento, parpadea, desvía la mirada y vuelve, pausas pequeñas, se corrige y sonríe — "no se ve ensayado".
- `tone` (NUEVO): calm/reflective · **not performing, not selling** · energía "amiga al teléfono" +20%.
- `negative` (NUEVO, **CORTO** ≤10 términos — los largos endurecen Kling): *studio lighting, beauty filter, perfect skin, ad-like polish, exaggerated gestures, robotic delivery*.
- `camara`: dirección de ESCENA, no adjetivos ("slowly turns head" > "dynamic"): *handheld micro-shake, slight autofocus breathing, flat indoor lighting (not cinematic)*, punch-in súbito, whip pan; prohibido slow push/pan/drift genérico.
- **Ambiente por beat** desde el catálogo de momentos, emparejado a la función: espejo=demo · carro parqueado=confesión/testimonio · caminando=energía/anuncio · cocina=rutina · cama+teléfono=confesión nocturna · taller/escritorio=producto y autoridad.
- **B-roll**: ≥1-2 insertos SIN cara por reel (producto/manos/lugar) — la cara es condimento, no plato.
- **La FICHA DE CONTINUIDAD** (§2.2), emitida UNA vez.

### 2.D Rol 4 — EL AUDITOR (Actor-Critic-Boss)

Modelo **DISTINTO** del generador (lección LIDR de verificación), prompt estructuralmente distinto: **evalúa contra criterios, no genera**. Schema: `{issues: [{category, severity: critical|major|minor, clip, evidence, fix}]}`.

**Categorías** (cada una con su test):
- `quietud` — sin acción física en el primer segundo; "calm/still/sitting" como dirección.
- `infografia_disfrazada` — el pecado capital del curso: producto aislado sobre fondo neutro.
- `sameness` — clips 2-N homogéneos; el contraste de planos del PASO 0 no se cumple.
- `sobrecarga` — >2.5 palabras/seg en cualquier clip.
- `encadenabilidad` — algún par consecutivo de keyframes no es visualmente encadenable.
- `continuidad` — una escena contradice la Ficha (§2.2).
- `venta` — no responde qué es / qué gano / qué hago, o el producto no aparece en imagen (§2.1).
- `anuncio` — suena a anuncio: aperturas prohibidas, adjetivos vacíos, energía de vendedor (test de la cena).
- `canal` — TikTok sin keywords habladas / IG sin momento compartible / YT sin empate de loop.

**El boss** aplica los fixes con **tope de 2 iteraciones** y entrega la mejor versión disponible (producción > perfección). Test final del curso (Etapa 7): *"¿Es la apertura de un corto de Pixar o un banner de Facebook?"* — "No me des un anuncio. Dame un corto."

### 2.1 El hilo de la VENTA (lo más importante — mandato del operador 2026-07-15)

El reel DEBE definir claramente qué es el producto, cuáles son los beneficios, y vender. Ese hilo se cose en 4 puntos garantizados, no opcionales:

1. **El Estratega** trae la venta FIRMADA de Fase 1 al brief: qué vendes, la promesa, el **mecanismo** (por qué funciona), la oferta estructurada (`offer_spec`/`offer_statement` 1.4). No se inventa nada — se hereda de lo firmado.
2. **El Guionista** escribe sobre esqueleto de respuesta directa: gancho → problema → **mecanismo/producto POR FUNCIÓN** (patrón 6 del curso: qué HACE, cero adjetivos vacíos) → beneficio concreto con número → CTA (por doctrina de intent: directo en presentadora, recomendación-de-amigo en UGC). **El beat de producto es OBLIGATORIO** — la caja `producto ⭐` de hoy sobrevive y el guionista no puede emitir un guion sin llenarla en ≥1 clip.
3. **El Director** pone el producto **EN IMAGEN**: el money shot ⭐ preferentemente ES el momento producto-en-manos (el paquete kraft, la demo, el antes/después); el producto real entra como referencia visual desde Media/brand-assets a los keyframes.
4. **El Auditor** gana la categoría **`venta`** en su schema: verifica que el reel responda *(a) qué es el producto, (b) qué gano yo (beneficio concreto), (c) qué hago ahora (CTA)* — y que el producto aparezca visualmente ≥1 vez. Si falla cualquiera → issue `severity: critical` ANTES de gastar en video.

**En la compuerta ②** el usuario ve la **"línea de venta"** resumida arriba del guion: `Vendes: [producto] → Beneficio: [promesa concreta] → CTA: [acción]` — verificación de un vistazo sin leer todo. (Nota: el balance dar:pedir del proyecto sigue mandando QUÉ piezas venden duro y cuáles dan valor — este spec garantiza que cuando la pieza vende, venda BIEN.)

### 2.2 La Ficha de Continuidad — el continuista (mandato del operador 2026-07-15)

**El problema:** ni Kling ni Veo ni ningún generador tiene memoria entre clips — cada clip es una generación independiente que no sabe nada de las demás. Y la causa #1 de deriva es nuestra: cada prompt RE-DESCRIBE a la persona/lugar con palabras distintas (el LLM parafrasea), y cada paráfrasis es una invitación a cambiar el color de la ropa, el peinado o la luz.

**La regla de oro: la consistencia = repetir la MISMA información, PALABRA POR PALABRA, en cada clip.** Nunca parafrasear entre clips lo que debe permanecer idéntico.

**El mecanismo — 5 anclas, cada una cubre un eje de deriva:**

1. **FICHA DE CONTINUIDAD (nuevo — el rol continuista).** El Director emite UNA VEZ, como salida estructurada aparte, un bloque de texto fijo con: **PERSONA** (rasgos faciales, peinado exacto, outfit con colores y prendas específicas, accesorios), **LUGAR** (set + props presentes, incluido el producto con su descripción exacta), **LUZ** (estilo de iluminación), **VOZ** (el descriptor exacto: "calm warm female voice, early 30s, neutral American accent, unhurried"), **ESTILO** (cámara/grade/realismo del dial). Se persiste en `design_spec.continuity` y se **inyecta VERBATIM** (mismos bytes) en TODOS los prompts de keyframe y de motion de todos los clips. Ningún rol posterior puede reescribirla — se copia, no se genera.
2. **Ancla de identidad facial (ya existe):** el retrato ancla del cast viaja en `frontal_image_url`/`elements` en cada clip, y los keyframes se generan en cadena DESDE el ancla ("same person"). La imagen manda sobre el texto para la cara.
3. **Ancla visual de frontera (ya existe — encadenado):** el último frame del clip N ES el primer frame del clip N+1 (la frontera es LA MISMA imagen) → la transición es continua por construcción. En proveedores sin end-frame (kie-Kling 2.6) la continuidad baja a suave y la Ficha pesa MÁS.
4. **Voz idéntica por contrato:** el descriptor de voz vive en la Ficha (una sola fuente) — se acaba el riesgo de que el guionista lo redacte distinto en el clip 3.
5. **El Auditor verifica la cadena:** (a) la Ficha está presente y VERBATIM en cada escena, (b) cada par consecutivo de keyframes es "visualmente encadenable" (curso, Etapa 7), (c) nada en las cajas de escena contradice la Ficha (p.ej. "chaqueta roja" en el clip 4 cuando la Ficha dice azul) → issue `severity: critical`.

**Regla de presupuesto:** la Ficha es información que se REPITE en cada prompt → debe ser densa y corta (~80-120 palabras), gastada en lo que deriva (ropa, pelo, props, luz), no en prosa. El prompt de cada clip queda: `[FICHA verbatim] + [lo ÚNICO de este clip: acción/encuadre/guion]` — exactamente el patrón STYLE LOCK del curso (Etapa 6: "describir al personaje completo la primera vez, después solo lo que cambia" se INVIERTE aquí: sin memoria entre generaciones, la Ficha va completa SIEMPRE y lo que cambia es lo único que se añade).

## 3. Cambios de doctrina en generación y edición (independientes de la UX)

1. **`composeMotionPrompt` se recompone así:** `[FICHA verbatim] + accion + physics + behaviour + tone + camara + Framing + Audio + "She says exactly: …" + negative + safe zones`. Los campos nuevos vienen del rol Director (§2.C); la Ficha de §2.2. Negative SIEMPRE corto (≤10 términos).
2. **Keyframes mid-action:** el prefijo del encadenado pasa de "Change ONLY the pose" a **"same person/set, NEW moment of the action"**; toda pose es EN MITAD de la acción (mid-gesture, alcanzando, girando — "ready position" genera movimiento natural; pose frontal simétrica = avatar corporativo desde el frame 0); **brazo selfie visible** cuando el concepto es selfie; imperfección horneada (encuadre ligeramente off-center, luz plana de interior, grano de teléfono). **El primer frame del clip 1 ES el gancho visual**: la acción ya iniciada + expresión fuerte + espacio para el texto overlay (safe zone superior).
3. **Edición de retención (⑤, nuestro ffmpeg — puro código, gratis):**
   - **Zoom progresivo** 1.5-2%/s en clips de talking head (60%→85% a lo largo del clip) — el truco de mayor rendimiento; imperceptible por frame.
   - **Auditoría de cadencia**: warning en la línea de tiempo si pasan >3s sin cambio visual (corte, punch-in, overlay, b-roll) — la regla de mayor consenso (cambio significativo cada 2-3s).
   - **Captions karaoke** (ya existe): 4-6 palabras por golpe, aparecen 200-400ms después de la palabra hablada, banda central 45-65%, safe zones Meta (14% arriba / 35% abajo).
   - **Loop check**: si el Director marcó cierre circular, verificar que el último frame empata visualmente con el primero.
4. **Los momentos del Casting (§1.1) se generan con 6C** (C1 Character · C2 Context · C3 Camera "iPhone dump photo" · C4 Clothing · C5 Cinematic Light natural · C6 Clean Output "not AI-generated look") + el dial de realismo del avatar.

## 4. Migración (qué muere, qué se muda)

| Hoy | Mañana |
|---|---|
| Apertura visual (16) en Ángulos | El catálogo pasa a ser vocabulario INTERNO del rol Director; override en Ajustes finos |
| Estilo de apertura (sugerencias) en Ángulos | Lo escribe el Guionista (3 capas); editable en compuerta ② |
| Concepto (12) + Ambiente (texto) en Director ① | Fichas de MOMENTO con miniatura en el brief |
| G1 en Director ① (persistencia rota en `estudio_choices`) | Ajustes finos del brief; persistencia unificada en `design_spec` |
| Tipo de reel + "presentadora" ambiguo | "¿Quién?" (cast/inventar) + dial de realismo; "animado" queda en Ajustes finos |
| Llamada única `estudio_develop@v2.0.0` | Pipeline de 4 roles (§2) |
| Retratos de estudio en el cast | Retrato ancla + paquete de momentos mid-action + dial de realismo |

Compuertas se REDUCEN de ~4 a 2 en el estudio (guion+plan, imágenes). Anti-patrones de la competencia que evitamos (quejas reales de HeyGen): costo opaco (nosotros: precio antes de cada gasto — ya lo tenemos), jobs fallidos que cobran créditos (nuestro ledger loguea $0 en fallo — ya), renders sin expectativa (mostramos ~min por paso — parcial).

## 5. Fases de construcción propuestas

- **F1 — La chispa (sin tocar UX):** capa de actuación en motion prompt (§3.1) + keyframes mid-action (§3.2) + **Ficha de Continuidad** (§2.2, generada por una llamada post-develop) + Auditor (§2.D) como llamada post-develop. *Resultado visible en el siguiente reel.*
- **F2 — El Brief:** pantalla ① nueva (quién/momento/plataforma/ajustes finos), Ángulos adelgazado, momentos del avatar en Identidad (generación del paquete).
- **F3 — El pipeline completo:** partir la llamada única en los 4 roles + compuerta ② con plan visual + sello del auditor + regenerar-por-beat.
- **F4 — Pulido:** zoom progresivo, check de cadencia, dial de realismo, doctrina de plataforma visible.
- **F5 — El Analista (§7):** el lazo de mejora con métricas reales.

## 7. El Analista — la etapa ⑧ (F5, cierra el lazo)

El perfil que la industria llama media buyer/analista: publica, mide y **alimenta de vuelta** la creación. Escalera de métricas: **hook rate** (vistas de 3s / impresiones — 30% sólido, 40% élite) → **hold rate** (sobreviven de 3s→15s — 25-40% sólido) → CTR/acción. **El diagnóstico es POSICIONAL**: mal hook rate = arregla los 3 primeros segundos (las 3 capas del gancho); buen hook + mal hold = arregla el cuerpo. Cadencia industrial: variantes semanales por capas (se testean GANCHOS contra un cuerpo probado, no videos enteros — Arcads: 20 ganchos × 1 cuerpo).

En Papandi: los datos nacen de `piece_events` + (cuando exista conexión de plataforma) las métricas reales de IG/TikTok; el resultado alimenta la **librería de ganchos** del proyecto (qué capa visual/verbal/texto funcionó para ESTE negocio) — el mismo lazo del radar. Sin conexión de plataforma, arranca manual: el operador registra hook/hold desde los insights de la app. Fuera de alcance de F1-F4; se especifica fino al llegar F5.

## 6. Criterios de éxito

1. Un usuario nuevo produce su primer reel tocando ≤4 controles (avatar, momento, plataforma, producir).
2. El reel default pasa el test del curso: "¿suena a alguien contándotelo en una cena?" y "¿algo se mueve en el primer segundo?".
3. Cero opciones abstractas en la ruta por defecto; todas alcanzables en ≤2 clics para el power user.
4. El costo de LLM del pipeline por reel ≤ $0.10 (los roles ahorran video muerto: cada escena cazada por el Auditor = $1-2 no quemados).
5. IG vs TikTok produce guiones y planes DISTINTOS verificables (keywords habladas vs momento compartible).
6. **Todo reel de venta responde de forma verificable: qué es el producto, qué gano, qué hago ahora — y el producto aparece en imagen ≥1 vez** (la línea de venta de la compuerta ② + la categoría `venta` del Auditor lo garantizan).
7. Ninguna imagen del paquete de momentos se genera antes de que la cara del avatar esté aprobada (cero plata perdida en mundos de caras descartadas).
8. **La Ficha de Continuidad aparece byte-por-byte idéntica en el prompt de cada keyframe y cada clip del reel** (verificable con un diff), y el Auditor bloquea cualquier escena que la contradiga — misma persona, misma ropa, mismo lugar, misma luz, misma voz de punta a punta.
