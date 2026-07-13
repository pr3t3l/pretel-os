# spec_Director_de_Video — UN solo flujo guiado (antes spec_Estudio_Video_v2)

> **Estado: ✍️ PARA FIRMA (2026-07-12). NO construir hasta firma.**
> **UN SOLO SPEC:** este documento es el único del Director. Las «Etapas 1-4» de §5 NO son specs ni
> versiones aparte — son el ORDEN DE CONSTRUCCIÓN del mismo documento (como G1/G2a/G2b en su momento),
> cada una shippeable. Nada que recordar fuera de aquí.
> Contexto completo: `docs/research/00_CONTEXTO_MAESTRO.md`. Cambios vs v1 de este spec:
> **UN solo pipeline para TODOS los tipos de reel** (no tres), prompt estructurado en **cajas editables**
> (el usuario edita cada parte), UI de **workflow con indicador de pasos** (se siente un flow), música de
> la **biblioteca propia del operador** (562 pistas royalty-free), y modo D con la misma esencia.

---

## 0 · Diagnóstico (por qué existe este spec)

La prueba real (2026-07-12, 5 clips de «Someone Else's Decision») mostró los dos huecos de v1:
1. **Sin continuidad:** los 5 clips arrancan de la MISMA foto-retrato → tomas sueltas, sin fluidez ni emoción.
2. **Sin control fino barato:** el usuario solo aprueba el guion; todo lo visual se decide dentro de un
   prompt de texto que no ve por partes, y la primera imagen que ve ya costó ~$1/clip.

**La solución:** primero el plan, luego las IMÁGENES ($0.15 c/u), y el video al final — con **el último
frame del clip N como primer frame del clip N+1** (continuidad por construcción). Verificado: Kling v3 Pro
i2v (nuestro endpoint) acepta `start_image_url` + **`end_image_url`** hoy.

---

## 1 · La idea en una frase

**Un ÚNICO flujo guiado — "el Director" — para todo reel.** El "tipo" de reel (presentadora de marca /
UGC / animado / footage propio) **no cambia el flujo: cambia lo que viene pre-llenado en las cajas.**
La estructura del prompt es UNIVERSAL (es la misma para cualquier video): encuadre · sujeto · cámara ·
iluminación · audio · guion con timing · primer frame · último frame.

## 2 · Principios (candados)

1. **No complicarse:** un solo pipeline, un solo esquema de prompt, presets por tipo. Cero código especial
   por modo salvo el motor de video al final.
2. **HÍBRIDO con compuertas baratas:** el usuario edita ANTES de gastar. Compuertas: prompt estructurado →
   keyframes ($0.15) → clips (~$1).
3. **Cajas editables, lectura LIGERA:** cada parte del prompt en su text box con sugerencia pre-llenada;
   tarjetas por clip, colapsables; nunca un muro de texto. Lo que editas ES lo que se manda (glass-box).
4. **Flow visible:** indicador de pasos arriba/al lado (como las fases 0-4 del wizard) — el usuario siempre
   sabe en qué paso está.
5. **La imagen es el ancla** (i2v): las cajas de apariencia alimentan los KEYFRAMES; el prompt de video
   lleva SOLO movimiento/cámara + la narración entre comillas (audio nativo).
6. Doctrinas vigentes intactas: arco que vende, C4/C12/C1, safe zones, captions karaoke en post, EN-first,
   dedupe de slot, gate por-pieza del cast, presupuesto visible antes de gastar.

## 3 · El flujo — pantalla por pantalla

**Qué es «el Director» (aclaración del operador 2026-07-12):** NO es un botón nuevo — es el NOMBRE del
flujo guiado. Se entra por el **mismo botón de siempre**: «Desarrollar para IG Reel →» en la tarjeta del
ángulo en /angulos. La diferencia: hoy ese click dispara el develop a ciegas y abre el drawer; con este
spec, ese click **abre el flujo** empezando por ① Ajustes (la llamada al LLM ocurre DESPUÉS de tus
elecciones, no antes). El indicador de pasos siempre visible te dice dónde estás:
`① Ajustes → ② Guion y prompt → ③ Imágenes → ④ Clips → ⑤ Edición → ⑥ Publicar`

**El canal manda desde el paso cero (pregunta del operador — respuesta: SÍ, ya construido y se conserva):**
la pieza nace ángulo × CANAL, y el develop ya recibe la doctrina POR CANAL (`channelDoctrine`): TikTok ≠
Instagram — en TikTok la caja «Lo que DICE a cámara» debe DECIR las keywords en voz alta (el ASR indexa el
audio), en Instagram el diseño apunta a sends-per-reach, YouTube Shorts pide el final que fluye al inicio
(loop), etc. **La estructura de cajas es la MISMA para todos los canales; el CONTENIDO sugerido llega
pulido por canal** — misma regla que los tipos de reel: presets, no pipelines. (Las duraciones default
también: TikTok viral 11-18s · Reels 7-15s · Shorts 20-45s.)

### ⓪ La fuente: la información de la EMPRESA (lo que alimenta TODO el flujo)

El usuario de Papandi ya le contó su negocio en las fases 0-2; el Director **compila eso** — jamás pide
re-escribirlo. Qué entra y de dónde (auditado contra la BD real del proyecto Papandi, 2026-07-12):

| Qué | De dónde | Estado real |
|---|---|---|
| Qué ES el negocio y por qué ahora | 0.1 `refined_idea` + `why_now` | ✅ existe y está bien escrito |
| Lo único (diferenciadores) | 0.1 `differentiators` | ✅ 4 aceptados |
| QUÉ VENDE y qué recibe el cliente | 1.4 `offer_statement` ("is for you if…" + "what you get") | ✅ existe — ⚠️ pero hoy solo fluyen 300-400 chars al develop (los bullets "what you get" se cortan) |
| Por qué es distinto | 1.4 `distinct_because` | ❌ NULL en la BD — hueco de dato |
| A quién le habla | 0.3 avatar (dolores/miedos/deseos) | ✅ |
| Dolor→ángulo | 2.3 pilares (con `mode`) + 2.5 ganchos | ✅ |

**Fixes de fuente (parte de este spec):** ①fluir el `offer_statement` ESTRUCTURADO (is_for_you_if +
what_you_get como bullets, no un slice de 400 chars) a las piezas que PIDEN; ②exponer/llenar
`distinct_because`; ③**hallazgo de integridad:** TODOS los artefactos están `status='draft'` en la BD y
`getArtifactContent` no exige firma — el contrato "solo lo firmado entra a producción" hoy no se cumple a
nivel de dato (funciona porque lee el draft más reciente). Decidir: persistir la firma en `status` y/o
documentar que draft-vigente es la fuente.

### ① Ajustes (ANTES de cualquier llamada al LLM)
Selecciones rápidas (chips/botones, mismo patrón G1 — que ya existe y se integra aquí):
- **Tipo de reel:** Presentadora de marca (default, usa tu cast) · UGC persona real · Animado (elige estilo:
  Apple realista / Pixar / …) · Traigo mi video (→ modo D, mismas pantallas con ③④ distintas).
- **Cámara** (punch-ins/handheld/fija — G1) · **Ritmo · Duración · Loop · CTA** (G1) · **Ambiente/Set**
  (del cast o describir uno). **Nota de UI: los 5 botones G1 se MUDAN de la tarjeta de /angulos al paso ①**
  (una sola casa; la tarjeta queda solo con gancho visual + estilo de apertura + campaña).
- **Referencia visual opcional [entra en Etapa 3, no en el quick win]:** sube un screenshot
  (TikTok/Pinterest/foto tuya) → se descompone en las 6C (llamada de visión) y pre-llena cajas del paso ②.
- **CONCEPTO (el paso que faltaba — qué TIPO de contenido es): CATÁLOGO DETERMINÍSTICO, sin llamada extra
  al LLM.** (Decisión razonada 2026-07-12 — pregunta abierta del operador, mi recomendación:)
  - **Por qué determinístico:** ①es el patrón de la casa que ya funciona (los 16 ganchos visuales de
    `visual-hooks.ts`, los 5 botones G1, el catálogo de 4.550 formas — MENÚ fijo, el LLM solo RELLENA)
    ②$0 y 0 segundos de latencia extra ③glass-box: un menú estable se aprende; una propuesta generada
    cada vez no ④la personalización NO se pierde: **la misma llamada del develop (que ya hacemos) adapta
    el formato elegido al proyecto** — el micro-momento concreto ("ceramista empacando pedidos") lo escribe
    el develop dentro de las cajas de ②, con la audiencia/ángulo que ya recibe.
  - **El catálogo v1 (12 formatos, de la biblioteca del curso + estándar UGC), cada uno con nombre + 1 línea
    + mini-ejemplo de cómo se vería + para qué sirve (dar/pedir, canal):** presentadora a cámara · street
    interview (entrevistador off-camera) · selfie caminando · confesión en el carro · espejo del baño ·
    micro-momento cocina/mesa de trabajo · escritorio/oficina · producto en manos (unboxing) · podcast 2
    personas · voz en off sobre b-roll · noche/luz de pantalla · actividad (gym/parque/feria). Default =
    «Papandi decide» (elige por ángulo+canal con reglas simples: pedir→presentadora o producto en manos;
    dar+TikTok→micro-momento o street interview).
  - **+ «Otro (descríbelo)»** (pedido del operador 2026-07-12): caja de texto libre — lo que el usuario
    escriba viaja al develop como el concepto Y **se registra** (evento `concept_custom`) para aprender:
    un job semanal agrupa lo que los usuarios piden y propone candidatos a entrar al catálogo. Así el
    catálogo crece de la demanda real, no de nuestra imaginación.
  - **+ pestaña «Tendencias»** (global de Papandi, se actualiza 1×/semana): ver §3.6.
  - (Futuro opcional, NO v1: botón «Sugerir 3 para este ángulo» — una llamada barata que RANKEA el catálogo;
    solo si el menú resulta difícil de elegir en la práctica.)
Todo esto viaja EN la llamada de desarrollo (hoy G1 ya viaja; se suman tipo/concepto/ambiente/referencia).

### ② Guion y prompt estructurado (UNA llamada al develop — la actual, extendida)
El develop devuelve, **por clip**, una tarjeta con CAJAS EDITABLES (cada una un text box con sugerencia):

| Caja | Contenido sugerido según el tipo elegido |
|---|---|
| **Guion** (con timing) | la narración exacta del clip (arco que vende) |
| **Tu producto en esta pieza** ⭐ | CÓMO entra tu empresa/oferta en ESTE reel, según su intención: si la pieza **DA valor** → una puerta suave desde la esencia ("Papandi builds that plan with you"); si **PIDE** → la oferta con tus palabras de 1.4 (what you get + CTA directo + deadline real si hay campaña). Editable — aquí VES exactamente qué se dice de tu negocio |
| **Encuadre visual** | plano/composición del clip |
| **Sujeto** | Presentadora → "tu personaje del cast" (bloqueado a la imagen aprobada) · UGC → persona inventada creíble (edad, imperfecciones) · Animado → personaje del estilo |
| **Cámara** | movimiento/energía (de tus ajustes ①) |
| **Iluminación** | luz con intención |
| **Audio** | voz (descriptor idéntico por clip) + ambiente; UGC añade "raw mic, breathing…" |
| **Primer frame** | descripción de la imagen de arranque del clip |
| **Último frame** | descripción de la imagen final (= primer frame del clip siguiente — el sistema lo empata solo) |

- El usuario **edita cualquier caja** (o ninguna) → «Aprobar guion y prompts →» (compuerta 1).
- El prompt final de cada etapa se COMPONE de las cajas — no hay un segundo prompt oculto.
- **Contador de voz EN VIVO por clip:** la caja «Lo que DICE a cámara» muestra el presupuesto de palabras
  (el guard `over`/`under` que ya existe, ahora mientras editas: "14 palabras / 3s — saldrá acelerado").
  **Esto RESUELVE la tensión del opener sagrado:** la sugerencia llega íntegra (el opener no se mutila por
  defecto), el contador avisa si no cabe, y el USUARIO recorta en la caja — la palabra final es suya.
- **Mapeos que el build no debe perder:** la caja «Lo que DICE a cámara» ES `clip_narrations` (la fuente
  literal del karaoke de ⑤) y el conjunto de cajas reemplaza a `video_prompts` (el prompt de movimiento se
  compone de encuadre+cámara+acción; los frames alimentan ③).
- Los presets por tipo son solo CONTENIDO pre-llenado (el flujo y el esquema no cambian): UGC pre-llena
  cámara/audio con los bloques de realismo (micro-shake, grip fix, raw mic); Animado añade el STYLE LOCK
  y transiciones por estilo; Presentadora fija el sujeto al cast.

### ③ Imágenes de referencia (keyframes) — DESPUÉS del prompt aprobado (como pensaste)
- De las cajas «Primer frame / Último frame» + sujeto + iluminación + estilo → **Nano Banana Pro** ($0.15).
- Presentadora: la primera imagen parte del retrato del cast (edit: "same person, [escena]"). Los siguientes
  keyframes = edición del anterior ("keep identical, change [acción/plano]") → consistencia por cadena.
- **Encadenado automático:** el último frame del clip N ES el primer frame del clip N+1 (misma imagen).
- **Galería** (compuerta 2): ver/regenerar/editar el prompt de cada imagen/subir la tuya. Corregir aquí
  cuesta $0.15, no $1.

### ④ Clips
- **DIÁLOGO NATIVO es el default (no narración):** la persona HABLA a cámara con labios sincronizados —
  el modelo genera voz + labios JUNTOS (Kling `generate_audio` / Sora 2), porque la línea va como diálogo
  entre comillas dentro del prompt, en inglés (EN-first). No hay post-sync de audio: el lip-sync nace en la
  generación (por eso el operador veía "voz de fondo" en ES — no existe lip-sync nativo barato en español).
  La "voz en off" es UN formato del catálogo (b-roll + VO), no el default. En la UI la caja se llama
  **"Lo que DICE a cámara"**, no "narración".
- Por clip: `start_image + end_image` (keyframes aprobados) + prompt de MOVIMIENTO (cajas cámara/acción) +
  narración entre comillas + `elements` (identidad del cast si aplica) → **Kling v3** (default).
- El tipo solo cambia el MOTOR si conviene: UGC one-take corto puede ir a **Sora 2** (un solo clip 12-16s);
  premium a **Veo 3.1 first-last-frame**. ⚠️ Ninguno de los dos está hoy en `VIDEO_MODELS` — **añadirlos al
  catálogo es parte de Etapa 2** (dos endpoints nuevos verificados: `fal-ai/sora-2/image-to-video/pro` y
  `fal-ai/veo3.1/first-last-frame-to-video`). Misma cola, mismo presupuesto, mismas variantes.
- Los clips se generan **en paralelo** (la continuidad ya viene de las imágenes, no del orden).
- **El empaque `multi_prompt` de Kling queda SOLO para el camino legacy** (piezas viejas sin keyframes):
  en modo encadenado cada clip es SU job con su par de imágenes — no hay packing.

### ⑤ Edición — EL STACK COMPLETO (con qué se hace cada cosa)

**Toda la post-edición corre por fal con la MISMA llave y la MISMA cola async** (cero infra nueva, cero
apps externas). La tabla función-por-función:

| Función | Con qué se hace | Estado |
|---|---|---|
| Unir clips en orden (armar el reel) | `fal-ai/ffmpeg-api/compose` — track de video, keyframes secuenciales | ✅ construido (G2) |
| Sincronizar TEXTO con el audio | `fal-ai/whisper` `chunk_level=word` → timestamps POR PALABRA del reel armado (fallback determinista proporcional) | ✅ construido |
| Captions karaoke (palabra a palabra, resaltado) | beats 1-3 palabras (`captions.ts`) → PNGs transparentes client-side canvas ($0) → compose los quema como overlays con timing | ✅ construido |
| Gancho de texto (frame 1) | PNG canvas bajo el 14% superior → overlay | ✅ construido |
| Adjuntar MÚSICA | compose con **track de audio** (la pista entra como input más; `withAudioTrack` ya cableado) — volumen bajo la voz + fade-out final (verificar param `volume` del schema al construir; fallback: pre-procesar el mp3 al volumen deseado) | 🔜 Etapa 3 |
| Elementos nombrados (el folder/el café aparece cuando lo DICE) | overlays de imagen (producto/iconos) posicionados en el timestamp de la PALABRA — compose keyframes `{timestamp, duration, x, y}` | 🔜 Etapa 3 |
| Cortes/trims (modo D) | compose con offsets de entrada/salida por segmento | 🔜 Etapa 4 |
| Transiciones entre clips | v1 = **corte duro** (doctrina 2026: el corte retiene; los punch-ins vienen DENTRO del clip generado). Crossfade solo si el schema de compose lo permite (opacity keyframes — verificar al construir). Transición GENERATIVA (estilo Pixar/Apple del curso) = un clip puente Kling start+end en modo animado | v1 corte · resto 🔜 |
| Efectos/gráficas en movimiento estilo Hyperframe (código→video) | **NO v1** — nuestra vía hoy son PNGs+keyframes; si un caso lo exige, evaluar Remotion self-hosted en fase posterior | ⏳ futuro |
| Export/re-host durable | el reel final se re-sube a brand-assets (mp4) — sobrevive a la expiración de fal | ✅ construido |

**🎵 La biblioteca de música (562 pistas royalty-free, 1.92 GB) — dónde y cómo:**
- **Dónde:** bucket **global** `music-library` en el MISMO Supabase de sandia (no por-proyecto — es un activo
  de Papandi para todos los usuarios). Cabe de sobra: el plan Pro incluye 100 GB ($0.021/GB/mes el exceso);
  1.92 GB ≈ $0 real. Subida una vez por script (resumable TUS). Junto al bucket: `music_tracks` (tabla o
  índice JSON): filename, duración, tags de mood/energía (v1: derivados del nombre del archivo + curación
  manual; v2: análisis de audio), y un README con el ORIGEN/licencia de las pistas (candado legal).
- **Cómo se usa:** en ⑤, selector con preview (`<audio>` del bucket público) + filtro por mood; Papandi
  SUGIERE una pista desde el `mood` del design_spec. Al armar: compose añade el track de audio recortado a
  la duración del reel, volumen de fondo (~20-25% bajo la voz), fade-out en el último segundo. La música
  queda QUEMADA en el mp4 final — legal porque la licencia es nuestra; la doctrina "música del catálogo de
  la plataforma al publicar" queda para quien NO use la biblioteca. Label IA ON no cambia.

### ⑥ Publicar (sin cambios)
Agenda/campaña, música de catálogo si no se quemó una propia, label IA.

## 3.5 · DAR vs PEDIR — la doctrina en cristiano (aclaración pedida por el operador 2026-07-12)

El chip **no clasifica el gancho** (el gancho SIEMPRE abre por el dolor — por eso dos ángulos con chips
distintos se leen igual). Clasifica la **misión del CUERPO** de la pieza:

- **DA VALOR** (pilares `resolve/agitate/educate` — hoy A, B, C): la pieza es ÚTIL por sí misma — enseña,
  nombra el dolor con precisión, da el cómo. Tu producto aparece como la **puerta** al final (CTA suave
  desde la esencia). En video: el arco igual EXPLICA qué es el producto (decisión 2026-07-11), pero NO
  empuja oferta/precio/deadline. **Cómo "da" valor:** el espectador se lleva algo aunque jamás compre
  (un reframe, un error nombrado, un cómo).
- **PIDE** (pilar `reinforce` — hoy D — o estilo con goal `get_sales`, o fase pico/cierre de campaña): la
  pieza PRESENTA la oferta — qué recibe, con las palabras de la Fase 1 (what you get), garantía, y si hay
  campaña su deadline REAL — y cierra pidiendo la acción directa.
- **De dónde sale el chip (glass-box, ya en código):** 1º el `goal` del estilo elegido (táctico); si no,
  el `mode` del pilar (estratégico). La política 3:1 se mide sobre el MES (campañas la reordenan por fase).
- **Fix aplicado hoy (sandia, pusheado):** leyenda visible en la barra del ratio + tooltips concretos en
  cada chip ("el cuerpo de esta pieza presentará tu oferta…" / "enseña y abre la puerta…").
- **Fix de este spec:** el develop recibe el `intent` EXPLÍCITO con sus dos reglas (hoy le llega implícito
  vía `offer_mode`) y la caja "Tu producto en esta pieza" lo materializa editable.

## 3.6 · «Tendencias» — investigación semanal global (propuesta, con mi opinión)

**Veredicto: sí, y encaja barato — con tres condiciones para que no sea humo.**
- **Qué es:** un job semanal (Vercel Cron) a nivel PAPANDI (no por proyecto) que investiga qué está
  funcionando en short-form esa semana (formatos, mecánicas de gancho, estilos de audio/edición) y publica
  un reporte global → pestaña «Tendencias» junto al catálogo de conceptos en ①.
- **Las 3 condiciones:**
  1. **Accionable, no noticia:** cada tendencia se mapea a NUESTRO lenguaje — {qué es, por qué funciona,
     a qué FORMATO del catálogo se parece, ejemplo de cómo se vería con TU ángulo} + botón «Probar este»
     que pre-llena el concepto (o la caja «Otro»). Una tendencia que no se puede ejecutar no se publica.
  2. **Glass-box:** cada ítem con fuente + fecha; el reporte muestra "investigado el {fecha}" (una
     tendencia de hace 3 semanas ya no lo es).
  3. **Filtro de doctrina:** lo que viole candados (engagement bait, urgencia fabricada, testimonios
     falsos) se publica como "tendencia que NO usamos y por qué" — eso también enseña (y es diferenciador).
- **Costo:** una corrida semanal de research (~$0.50-2) — trivial. Storage: tabla `trend_reports`
  (semana, items jsonb con fuentes) o artefacto global.
- **Bonus de aprendizaje:** el mismo job semanal procesa los `concept_custom` de la semana (lo que los
  usuarios pidieron en «Otro») → los candidatos a catálogo salen de tendencia EXTERNA + demanda INTERNA.
- **Conexión con MOMENTOS (`spec_Momentos.md`):** cada card de tendencia lleva «Desarrollar con tu marca»
  → crea un MOMENTO (investigación citada + ángulos efímeros con ventana). Tendencias es una de las TRES
  fuentes de momentos (usuario · tendencias · radar) — misma mecánica, ver ese spec.

## 3.7 · El loop de FEEDBACK — cómo aprendemos del usuario en todo el proceso (propuesta)

**Principio: el mejor feedback es el que el usuario ya da usando el producto — lo explícito se pide POCO
y en momentos de verdad.** Tres capas:

**Capa 1 — IMPLÍCITA (cero fricción, la más rica):** eventos append-only en una tabla `piece_events`
(`event, piece_id, project_id, payload, ts`):
- ②: **el diff entre lo sugerido y lo aprobado en cada caja** (qué corrige la gente = dónde falla el
  develop — la señal #1); qué conceptos se eligen (y qué escriben en «Otro»).
- ③: keyframes regenerados vs aceptados a la primera (qué prompts de imagen fallan); imágenes subidas a
  mano (= el generador no dio lo que quería).
- ④: variante elegida («Usar esta») vs descartadas; Rehacer por pieza; modelo elegido.
- ⑤/⑥: pieza que llega a agendarse/publicarse (= éxito del flujo) vs pieza abandonada (¿en qué paso murió?
  — el funnel del Director); pista de música elegida vs sugerida.
**Capa 2 — EXPLÍCITA (máximo UNA pregunta por pieza):** al terminar el reel (después de «Usar esta»):
👍/👎 + un "¿qué le faltó?" opcional de una línea. Nada de encuestas.
**Capa 3 — RENDIMIENTO REAL (cierra el ciclo con Fase 4/Medir):** "¿cómo le fue?" — v1 manual (el usuario
pega views/saves a los 7 días, la Agenda se lo recuerda); futuro APIs de plataformas. Es el único feedback
que valida DOCTRINA, no solo UX.

**A quién alimenta cada cosa (para que no sea data muerta):** diffs de cajas → mejorar las instrucciones
del develop y los defaults «Papandi decide» · keyframes fallidos → plantillas de prompt de imagen ·
funnel del Director → UX · «Otro» + tendencias → catálogo · piezas 👍 con buen rendimiento → **few-shot
del develop** (ejemplos aprobados del MISMO proyecto en el prompt — el "profiler" que el audit del
ensamblador marcó como faltante) · todo agregado → lecciones globales de Papandi (el data flywheel del
research de mercado). Privacidad: los agregados globales son de PATRONES, jamás contenido identificable
de un cliente.

## 3.8 · Proveedores: fal vs revendedores (kie.ai / apimart.ai — revisados 2026-07-12)

Precios verificados: **kie.ai** vende Veo 3 Fast a **$0.40 por video de 8s (= $0.05/s, ~87% menos que
Veo en fal)** y Veo 3 Quality $2.00/8s (=$0.25/s); Nano Banana ~$0.02/img; créditos desde $5; claims de
30-70% de ahorro. **apimart.ai**: ~20% bajo el precio oficial en todo; Nano Banana Pro $0.107 (vs $0.15
fal); tiene Kling 3.0 Turbo/V3 Omni y Sora 2/Pro (precios exactos requieren cuenta).

**Mi veredicto: fal sigue PRIMARIO; los revendedores entran al bake-off como tier de ahorro, no como base.**
- Por qué fal primario: schemas verificados + cola async + webhooks que YA usamos en prod; 1.000+ modelos;
  es infraestructura oficial-partner, no pool gris de cuotas.
- Por qué SÍ probarlos: si el Veo Fast de kie.ai a $0.05/s da lip-sync usable, **Veo pasa de "premium
  carísimo" a competidor del default** — eso cambia la tabla de enrutamiento. El ahorro real se decide con
  el bake-off ($10-15: mismo brief en fal-Kling vs kie-Veo-Fast vs apimart), midiendo yield/latencia/calidad.
- **Checklist de riesgo ANTES de producción con un revendedor:** leer ToS/privacidad (¿dónde van los prompts
  e imágenes de NUESTROS usuarios? ¿retención?) · medir uptime/latencia 1 semana · confirmar que no es
  pooling de cuotas revocable · fallback a fal cableado (el registry multi-proveedor ya existe) · ningún
  modelo >X% del valor (regla del research de mercado).

## 4 · Modo D — «Traigo mi video» (misma esencia, dos pantallas distintas)

Mismo flow y pantallas ①②⑤⑥; solo cambian ③ y ④:
- **③ Subir y entender:** sube su(s) mp4 (abogado: entrevistas; velera: lo que grabó con nuestro guion de ②)
  → re-host → transcript con **timestamps por palabra** (whisper, ya construido).
- **④ Plan de cortes (cajas, misma filosofía):** el LLM propone sobre el transcript — qué se queda y por qué,
  cortes de muletillas/silencios, gancho de apertura, momentos para elementos nombrados y CTA — el usuario
  edita/aprueba → compose hace los trims + concat. **Nunca destructivo** (el original se conserva).
- ⑤ y ⑥ idénticas (captions karaoke con SU marca, música, publicar). Referencia técnica: video-use (MIT):
  "lee el transcript, no mira frames"; FFmpeg procesa/une/renderiza; Scribe da la palabra exacta.

**Límites, subida y costos del modo D (pensado contra números reales, 2026-07-12):**
- **Límite v1: ≤10 minutos y ≤1 GB por archivo, hasta 3 archivos por pieza.** ¿Un video de 5 min para
  partirlo en clips? **SÍ se acepta y es BARATO de procesar:** whisper ~centavos + plan de edición (1
  llamada LLM sobre el transcript, ~$0.03-0.08) + compose de trims ~$0.10-0.35 → **<$1 por video**. El
  límite no es el costo de proceso: es storage/egress y UX de espera.
- **Subida DIRECTA navegador → Supabase Storage (resumable/TUS), JAMÁS por nuestra API:** Vercel corta el
  body en ~4.5 MB — un mp4 no pasa. TUS soporta hasta 50 GB/archivo en el plan Pro con progreso y reintentos
  (red del usuario inestable = no se pierde la subida). El API solo firma la subida y registra el asset.
- **Storage — la cuenta real:** un 1080p de 5 min ≈ 150-400 MB. Plan Pro: 100 GB incluidos, exceso
  $0.021/GB/mes; egress $0.09/GB sobre cuota (fal descarga el video ~2-3 veces: whisper + compose ≈ <1 GB
  por pieza). Con SOLO el operador: irrelevante. Con 100 usuarios × 3 videos × 300 MB = ~90 GB = el borde
  del plan → **la retención es una política de producto, no un detalle técnico**.
- **Retención (propuesta):** el ORIGINAL se conserva (doctrina: nunca destructivo) mientras la pieza viva;
  los reels FINALES re-hosteados se conservan siempre (livianos); limpieza de originales solo con aviso y
  a decisión del usuario (y a futuro, cuota por plan — hueco para `spec_Admin_Cost_Intelligence`).
- **Un video largo NO es un reel:** el plan de edición propone 1-N reels cortos DESDE el largo (los mejores
  momentos del transcript); cada reel es una pieza normal de Papandi (con su ángulo, sus captions, su CTA).

## 5 · Cambios de código (etapas — cada una shippeable, verify EXIT 0, push inmediato)

| Etapa | Qué entrega | Toca | Criterio de éxito (DONE cuando…) |
|---|---|---|---|
| **Etapa 1 — Cajas + Ajustes** | ① selector tipo/concepto/ambiente (G1 se muda aquí) + ② develop devuelve `scenes[]` (cajas por clip, incl. «Tu producto en esta pieza») + **intent dar/pedir EXPLÍCITO al develop** + **offer_statement ESTRUCTURADO en piezas que piden** + contador de voz en vivo + UI de tarjetas editables + indicador de pasos | `prompts.ts` (instrucción → scenes[] + intent + offer estructurado), `parse.ts` (parsear scenes[] + `clipWordBudget` lee scenes[] Y el formato viejo), `produce/route.ts`, UI del Director | re-desarrollar «Someone Else's Decision» produce cajas editables; editar una caja cambia el prompt compuesto; el contador avisa over/under en vivo |
| **Etapa 2 — Keyframes + encadenado** | ③ galería Nano Banana Pro (generar/regenerar/editar/subir, cadena de consistencia) + ④ `end_image_url` en Kling + **sora-2 i2v y veo3.1 first-last-frame ENTRAN a `VIDEO_MODELS`** + ledger registra costo de imagen | `video-routing.ts` (+endImageUrl +2 modelos), `api/estudio/keyframes` (nuevo), `keyframe-gallery.tsx` (nuevo), `video-generate` (modo encadenado, paralelo, sin packing), `media-ledger` | el reel de prueba sale con **continuidad visible** (el frame de la frontera N/N+1 es la MISMA imagen) y la cara consistente en los 5 clips |
| **Etapa 3 — Edición enriquecida** | ⑤ música de biblioteca (bucket global + selector con preview + compose con audio) + elementos nombrados (overlays en timestamps de palabra) + referencia visual 6C en ① (visión) | `video-compose` (audio track + image overlays), ReelAssembler UI, script de subida de pistas, `api/estudio/reference-decompose` (nuevo) | un reel suena con música de la biblioteca bajo la voz + un overlay aparece en el segundo exacto de su palabra |
| **Etapa 4 — Modo D** | ③④ de footage propio (upload directo TUS + transcript + plan de cortes editable + trims) | upload de video (browser→storage), `api/estudio/edit-plan` (nuevo), compose con trims | un mp4 de 3-5 min del operador sale como reel corto con captions de marca |

**Compatibilidad — SIMPLIFICADA (decisión del operador 2026-07-12: «borramos todas las piezas; solo
tenemos lo que hemos estado jugando»):** NO se mantiene camino legacy. Antes de shippear la Etapa 1 se
borran las piezas de prueba y todo nace con `scenes[]`. Único guard mínimo: si apareciera una pieza sin
`scenes[]`, la UI muestra «Rehacer con el flujo nuevo» en vez de romperse. Esto QUITA trabajo del build
(un solo formato, un solo render).

Cero migraciones de BD en Etapas 1/2 (todo vive en `design_spec`/`asset` JSONB + brand-assets). La única
tabla nueva de todo el spec es `piece_events` (§3.7) — puede esperar a Etapa 3.

## 6 · Costos típicos (ledger registra los reales)

| Tipo | Composición | ~Costo |
|---|---|---|
| Presentadora 28s (5 clips) | 6 keyframes $0.90 + 5 clips Kling $4.70 + compose | **~$5.75** |
| Animado 50-60s (10-12 escenas) | ~13 keyframes $1.95 + 11 clips Kling $9.25 + compose | **~$11.30** |
| UGC one-take 15s (Sora 2) | 1-2 keyframes + $4.50 | **~$4.80** |
| Traigo mi video | whisper ¢ + compose | **<$0.50** |

⚠️ `MEDIA_BUDGET_USD=20/mes` da ~3 reels de presentadora. Decisión pendiente: subirlo/configurable.

## 7 · Decisiones — estado tras el pre-check (2026-07-12)

**✅ Resueltas en conversación (registradas, no re-preguntar):**
- **Etapas 1+2 primero, prueba con «Someone Else's Decision»** — el operador pidió enfocarse en video y pasar
  al build plan.
- **Concepto = catálogo determinístico + «Otro»** — aceptado (pidió añadir «Otro» y Tendencias).
- **Feedback (§3.7) y Tendencias (§3.6)** — aprobados explícitamente ("me parece perfecta" / "buena
  propuesta"). Momentos aprobado conceptualmente (su spec tiene sus propias decisiones).
- **Opener sagrado × duración** — RESUELTA POR DISEÑO: la sugerencia llega íntegra, el contador de voz en
  vivo avisa si no cabe, y el usuario recorta en la caja (la palabra final es suya). Cerrada.
- **Música** — diseño aprobado; licencia EN CURSO (el operador envió correo al curso pidiendo confirmación
  escrita). Mientras llega: quemada solo en proyectos del operador; fallback catálogo de plataforma.

**🔓 Abiertas — SOLO una bloquea el build de Etapa 1:**
1. **[BLOQUEA Etapa 1] El Director: ¿pantalla completa o drawer expandido?** Mi recomendación: **pantalla
   completa** (flow tipo wizard de fases) — la galería de keyframes + cajas por clip no caben cómodas en
   el drawer, y el indicador de pasos pide espacio.
2. Presupuesto: ¿`MEDIA_BUDGET_USD` a $50/mes o configurable por proyecto? (No bloquea Etapa 1; sí conviene
   antes de Etapa 2 — recomiendo $50 fijo ahora, configurable cuando llegue Cost Intelligence.)
3. Modo D: límites v1 (≤10 min, ≤1 GB, 3 archivos) y retención propuesta — confirmar antes de Etapa 4.
4. Firma de datos: ¿persistir `status='signed'` + llenar `distinct_because`? (No bloquea; Etapa 1 lee lo que
   hay. Recomiendo hacerlo como tarea suelta pronto — es el contrato del producto.)
5. Los 2 transcripts de YouTube (folders + café) — para afinar elementos nombrados en Etapa 3.
6. Proveedores: kie.ai/apimart al bake-off con checklist §3.8 — el bake-off es posterior a Etapa 2.

## 8 · Qué NO haremos

- Pipelines distintos por tipo (este spec los mata — un flujo, presets).
- Clonar caras/voces de personas reales sin consentimiento. Testimonios falsos (C4). Música sin licencia.
- Auto-publicar. Cobrar regeneraciones como créditos.
- Construir Etapas 3/4 antes de que Etapas 1+2 prueben el encadenado en un reel real.
