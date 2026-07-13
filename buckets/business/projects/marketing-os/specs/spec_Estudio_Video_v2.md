# spec_Estudio_Video_v2 — El Director de Video: UN solo flujo guiado

> **Estado: ✍️ PARA FIRMA · v2 (2026-07-12, reescrito tras revisión del operador). NO construir hasta firma.**
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

**Entrada:** /angulos → click en la tarjeta del canal (IG Reel, TikTok…) → se abre **el Director**
(la ventana actual, expandida a flow). Indicador de pasos:
`① Ajustes → ② Guion y prompt → ③ Imágenes → ④ Clips → ⑤ Edición → ⑥ Publicar`

### ① Ajustes (ANTES de cualquier llamada al LLM)
Selecciones rápidas (chips/botones, mismo patrón G1 — que ya existe y se integra aquí):
- **Tipo de reel:** Presentadora de marca (default, usa tu cast) · UGC persona real · Animado (elige estilo:
  Apple realista / Pixar / …) · Traigo mi video (→ modo D, mismas pantallas con ③④ distintas).
- **Cámara** (punch-ins/handheld/fija — G1) · **Ritmo · Duración · Loop · CTA** (G1) · **Ambiente/Set**
  (del cast o describir uno).
- **Referencia visual opcional:** sube un screenshot (TikTok/Pinterest/foto tuya) → se descompone en las
  6C y pre-llena cajas del paso ②.
Todo esto viaja EN la llamada de desarrollo (hoy G1 ya viaja; se suman tipo/ambiente/referencia).

### ② Guion y prompt estructurado (UNA llamada al develop — la actual, extendida)
El develop devuelve, **por clip**, una tarjeta con CAJAS EDITABLES (cada una un text box con sugerencia):

| Caja | Contenido sugerido según el tipo elegido |
|---|---|
| **Guion** (con timing) | la narración exacta del clip (arco que vende) |
| **Encuadre visual** | plano/composición del clip |
| **Sujeto** | Presentadora → "tu personaje del cast" (bloqueado a la imagen aprobada) · UGC → persona inventada creíble (edad, imperfecciones) · Animado → personaje del estilo |
| **Cámara** | movimiento/energía (de tus ajustes ①) |
| **Iluminación** | luz con intención |
| **Audio** | voz (descriptor idéntico por clip) + ambiente; UGC añade "raw mic, breathing…" |
| **Primer frame** | descripción de la imagen de arranque del clip |
| **Último frame** | descripción de la imagen final (= primer frame del clip siguiente — el sistema lo empata solo) |

- El usuario **edita cualquier caja** (o ninguna) → «Aprobar guion y prompts →» (compuerta 1).
- El prompt final de cada etapa se COMPONE de las cajas — no hay un segundo prompt oculto.
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
- Por clip: `start_image + end_image` (keyframes aprobados) + prompt de MOVIMIENTO (cajas cámara/acción) +
  narración entre comillas + `elements` (identidad del cast si aplica) → **Kling v3** (default).
- El tipo solo cambia el MOTOR si conviene: UGC one-take corto puede ir a **Sora 2** (un solo clip 12-16s);
  premium a **Veo 3.1 first-last-frame**. Misma cola, mismo presupuesto, mismas variantes (todo ya existe).
- Los clips se generan **en paralelo** (la continuidad ya viene de las imágenes, no del orden).

### ⑤ Edición (lo ya construido + 2 extras)
- Armar (concat) + captions karaoke + gancho (G2 vigente).
- **Elementos nombrados** (nuevo, barato): overlays (producto/iconos/gráficos) que aparecen EXACTO cuando la
  narración los dice — ya tenemos timestamps por palabra + compose con keyframes. (Patrón video-use /
  los videos de YouTube: Hyperframe = gráficas por código → nuestro equivalente hoy = PNGs canvas + compose;
  ffmpeg une y renderiza; Scribe/whisper = timestamps por palabra para cortes precisos.)
- **🎵 Música de TU biblioteca (nuevo):** el operador tiene **562 pistas royalty-free (1.92 GB)**. Se pueden
  QUEMAR en el compose (el ffmpeg-api ya soporta pista de audio — `withAudioTrack` está cableado): selector
  de pista (o sugerencia por mood) + volumen bajo la voz. **Candado:** solo pistas con licencia verificada
  del operador; la doctrina "música comercial de plataforma se añade al publicar" sigue para las demás;
  label IA ON no cambia. (Pendiente: dónde viven — subir a storage por proyecto o biblioteca global.)

### ⑥ Publicar (sin cambios)
Agenda/campaña, música de catálogo si no se quemó una propia, label IA.

## 4 · Modo D — «Traigo mi video» (misma esencia, dos pantallas distintas)

Mismo flow y pantallas ①②⑤⑥; solo cambian ③ y ④:
- **③ Subir y entender:** sube su(s) mp4 (abogado: entrevistas; velera: lo que grabó con nuestro guion de ②)
  → re-host → transcript con **timestamps por palabra** (whisper, ya construido).
- **④ Plan de cortes (cajas, misma filosofía):** el LLM propone sobre el transcript — qué se queda y por qué,
  cortes de muletillas/silencios, gancho de apertura, momentos para elementos nombrados y CTA — el usuario
  edita/aprueba → compose hace los trims + concat. **Nunca destructivo** (el original se conserva).
- ⑤ y ⑥ idénticas (captions karaoke con SU marca, música, publicar). Referencia técnica: video-use (MIT):
  "lee el transcript, no mira frames"; FFmpeg procesa/une/renderiza; Scribe da la palabra exacta.

## 5 · Cambios de código (etapas — cada una shippeable, verify EXIT 0, push inmediato)

| Etapa | Qué entrega | Toca |
|---|---|---|
| **V2.a — Cajas + Ajustes** | ① selector de tipo/ambiente/referencia + ② develop devuelve el prompt ESTRUCTURADO por cajas (schema `scenes[]` en design_spec) + UI de tarjetas editables + indicador de pasos | `prompts.ts` (instrucción → scenes[]), `parse.ts`, `produce/route.ts` (nuevos extras), drawer→flow UI |
| **V2.b — Keyframes + encadenado** | ③ galería Nano Banana Pro (generar/regenerar/editar/subir, cadena de consistencia) + ④ `end_image_url` en Kling; los 3 tipos A/B/C funcionan aquí (los presets son config, no código) | `video-routing.ts` (+endImageUrl), `api/estudio/keyframes` (nuevo), `keyframe-gallery.tsx` (nuevo), `video-generate` (modo encadenado), ledger (+costo imagen) |
| **V2.c — Edición enriquecida** | ⑤ música de biblioteca (storage + selector + compose con audio) + elementos nombrados (overlays en timestamps) | `video-compose` (audio track + image overlays), UI en ReelAssembler, storage de pistas |
| **V2.d — Modo D** | ③④ de footage propio (upload video + plan de cortes editable + trims) | upload video, `api/estudio/edit-plan` (nuevo), compose con trims |

Cero migraciones de BD en V2.a/b (todo vive en `design_spec`/`asset` JSONB + brand-assets).

## 6 · Costos típicos (ledger registra los reales)

| Tipo | Composición | ~Costo |
|---|---|---|
| Presentadora 28s (5 clips) | 6 keyframes $0.90 + 5 clips Kling $4.70 + compose | **~$5.75** |
| Animado 50-60s (10-12 escenas) | ~13 keyframes $1.95 + 11 clips Kling $9.25 + compose | **~$11.30** |
| UGC one-take 15s (Sora 2) | 1-2 keyframes + $4.50 | **~$4.80** |
| Traigo mi video | whisper ¢ + compose | **<$0.50** |

⚠️ `MEDIA_BUDGET_USD=20/mes` da ~3 reels de presentadora. Decisión pendiente: subirlo/configurable.

## 7 · Decisiones del operador (para firmar)

1. **¿V2.a + V2.b primero** y probamos con «Someone Else's Decision» re-desarrollada? (recomendado)
2. **El Director**: ¿pantalla completa (flow tipo wizard de fases) o el drawer actual expandido? Mi
   recomendación: pantalla completa — la galería de keyframes + cajas no caben cómodas en el drawer.
3. **Música:** ¿de dónde salen las 562 pistas (origen/licencia) y las subimos a storage del proyecto o
   biblioteca global de Papandi?
4. **Presupuesto:** ¿subir `MEDIA_BUDGET_USD` a $50/mes o configurable por proyecto?
5. La tensión **opener sagrado × duración** sigue abierta: ¿el asistente puede PROPONERTE recortes del
   opener en ② (tú decides caja por caja)?
6. **Sí — pásame el transcript completo del video de YouTube** (y el segundo si lo tienes): alimenta el
   diseño de elementos nombrados (V2.c). Déjalos en `specs/AvatarHype Classes/` o pégalos en el chat.

## 8 · Qué NO haremos

- Pipelines distintos por tipo (este spec los mata — un flujo, presets).
- Clonar caras/voces de personas reales sin consentimiento. Testimonios falsos (C4). Música sin licencia.
- Auto-publicar. Cobrar regeneraciones como créditos.
- Construir V2.c/d antes de que V2.a+b prueben el encadenado en un reel real.
