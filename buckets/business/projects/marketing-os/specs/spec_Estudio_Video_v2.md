# spec_Estudio_Video_v2 — Keyframes encadenados + Asistente director + Footage propio

> **Estado: ✍️ PARA FIRMA (2026-07-12). NO construir hasta firma del operador.**
> Contexto completo: `docs/research/00_CONTEXTO_MAESTRO.md` (leerlo = tener todo el contexto).
> Fuentes directas: método AvatarHype (`specs/AvatarHype Classes/`), APIs verificadas en fal (2026-07-12),
> la prueba real de «Someone Else's Decision», y video-use (github.com/browser-use/video-use, MIT).

---

## 0 · Diagnóstico — por qué v1 no basta

La prueba del operador (2026-07-12, 5 clips Kling de «Someone Else's Decision») confirmó:

1. **Sin continuidad:** los 5 clips arrancan desde la MISMA foto-retrato del personaje (así es v1). Cinco
   tomas sueltas — no fluye, no emociona, no parece real.
2. **Sin control fino:** el operador solo aprueba el guion; lo VISUAL se decide todo dentro del prompt de
   texto → la primera vez que ve algo visual ya costó ~$1/clip.
3. El guion venía sobrecargado (~120 palabras en 28s) y la campaña sin concepto real — ya mitigado
   (guard `under/over` + lección de concepto), pero refuerza el punto: **faltan compuertas humanas baratas
   ANTES de gastar en video.**

**La solución (método AvatarHype + APIs verificadas): keyframes-first con encadenado.** Primero el plan,
luego las IMÁGENES (baratas, $0.15), y solo al final el video (caro, ~$1/clip). La continuidad se garantiza
por construcción: **el último frame del clip N ES el primer frame del clip N+1.**

**Desbloqueo técnico verificado (2026-07-12):**
- Kling v3 Pro i2v (el endpoint QUE YA USAMOS) acepta `start_image_url` + **`end_image_url`** + `elements`
  (identidad). → El encadenado es posible HOY sin cambiar de proveedor.
- Veo 3.1 tiene endpoint first-last-frame ($0.40/s con audio). Sora 2 i2v hace UGC one-take con diálogo
  lip-sync ($0.30-0.70/s). Nano Banana Pro genera/edita keyframes a $0.15 con cadenas de consistencia
  ("keep X identical, change Y") y es el único difusor que renderiza TEXTO legible.

---

## 1 · Principios de diseño (los candados de esta v2)

1. **HÍBRIDO (decisión del operador):** automatizar lo posible, pero el usuario participa en compuertas
   claras. Tres compuertas: **guion → keyframes → clips.** Regenerar un keyframe cuesta $0.15; regenerar un
   clip ~$1. La compuerta va donde el error es barato de corregir.
2. **Keyframes-first:** nada de video sin keyframes aprobados (en modo encadenado).
3. **Continuidad por construcción:** un solo set de keyframes; cada frontera de clips COMPARTE la imagen.
4. **La imagen es el ancla** (doctrina i2v vigente): los prompts de video describen SOLO movimiento/cámara;
   la apariencia vive en los keyframes; la identidad la refuerza `elements` (retrato del cast).
5. **Glass-box:** cada keyframe muestra su prompt; cada costo visible ANTES; el QA reporta qué cuidó.
6. **Todo por fal** (misma llave, misma cola async, mismo ledger `MEDIA_BUDGET_USD`).
7. **Las doctrinas existentes NO cambian:** arco que vende, C4/C12/C1, safe zones, captions karaoke en
   post (jamás generados), música al publicar, EN-first, dedupe de slot, gate por-pieza del cast.
8. **Anti-anuncio (filosofía AvatarHype):** "si parece anuncio, está mal; si parece contenido real, está
   bien" — micro-momentos concretos, imperfección controlada, integración creíble del producto.

---

## 2 · Los MODOS de producción (elegibles por pieza)

El drawer de una pieza de video ofrece **el modo del reel** (hoy solo existe el A):

| Modo | Qué es | Motor | Cuándo |
|---|---|---|---|
| **A. Presentadora (avatar)** | La cara de la marca habla a cámara — v1 mejorado con encadenado | Kling v3 i2v start+end + elements | contenido de marca con personaje del cast |
| **B. Animado / cinemático** | Mini-cortometraje estilo Pixar/Apple/Claymation/Sci-fi/Wes Anderson que vende con datos (workflow 8 pasos AvatarHype) | Nano Banana Pro (keyframes) + Kling start+end con prompt de transición por estilo | ads de conversión, productos físicos, explicar mecanismos |
| **C. UGC hiperrealista** | Persona "real" en un micro-momento (12-16s, one-take) | Sora 2 i2v / Veo 3.1 (prompt 14 bloques) | top-funnel, parecer contenido no-anuncio |
| **D. Footage propio** | El usuario SUBE sus videos; Papandi los post-produce con su marca | whisper + ffmpeg compose (ya construidos) | abogado con entrevistas; velera que filma nuestro guion |

Los modos B y C usan las **estructuras de prompt del curso** (ya destiladas en el CONTEXTO MAESTRO §6),
adaptadas a los candados Papandi (C4: cero testimonios falsos → mecanismo/datos reales de 0.2).

---

## 3 · El pipeline v2 (modos A y B — generación completa)

```
P0 INTAKE ASISTIDO → P1 GUION ✋ → P2 STORYBOARD → P3 KEYFRAMES ✋ → P4 CLIPS ✋ → P5 POST → P6 PUBLICAR
                      compuerta 1                    compuerta 2      compuerta 3
```

### P0 — Intake asistido (el "asistente director")
En el drawer, ANTES de desarrollar: formato/modo (A/B/C) · estilo (modo B: Pixar/Apple/…) · G1 (ya existe:
duración/ritmo/cámara/loop/CTA) · **referencia visual opcional**: el usuario sube un screenshot
(TikTok/Pinterest/foto propia) → un paso "6C decompose" (LLM visión) extrae Character/Context/Camera/
Clothing/Light → alimenta los keyframes. El asistente es conversacional-ligero: propone, el usuario ajusta
(patrón del copywriter del curso: analiza → pregunta "¿te cuadra?" → genera).

### P1 — Guion (compuerta 1: ya existe "desarrollada → aprobada")
El develop actual, con la instrucción por MODO:
- Modo A: la instrucción de video vigente (arco que vende + doctrina completa).
- Modo B: **los 9 patrones** (hook = verdad MÁS GRANDE, dato con cifra, bisagra reflexiva, cierre circular)
  + bloques con timing (HOOK 0-5s / DEVELOPMENT / INSIGHT / PRODUCTO / BENEFICIOS / CIERRE). Los "datos
  WOW" salen de 0.2/keywords/esencia — con fuente real o marcados (C4-compatible).
- Modo C: micro-momento + guion 12-16s + comportamiento (estructura UGC Engine).

### P2 — Storyboard (nuevo artefacto, dentro de design_spec)
El develop (o un segundo paso LLM) emite `design_spec.scenes[]`:
```json
{ "n": 1, "block": "HOOK", "vo": "narración exacta", "seconds": 5,
  "type": "narrativa|conceptual", "ref_mode": "A|B|C|D",
  "frame_type": "single|start_end",
  "start_frame_prompt": "…", "end_frame_prompt": "…",
  "motion_prompt": "solo movimiento/cámara para el video",
  "transition_to_next": "cómo conecta" }
```
Reglas del curso embebidas: escenas 4-6s (clip ≈5s) · UNA idea visual por escena · money shot entre escena
2-4 · variedad de planos (wide/close/macro/cenital/conceptual) · escena final retoma la primera transformada
(= loop de G1) · **check de encadenabilidad**: el `end_frame_prompt` de N y el `start_frame_prompt` de N+1
son LA MISMA imagen (o visualmente continuos si hay corte duro deliberado).

### P3 — Keyframes (compuerta 2: galería aprobar/regenerar — LA compuerta nueva clave)
- Generación: Nano Banana Pro. **Primer keyframe:** si modo A → parte del retrato del cast (edit: "same
  person, [escena/acción]"); si modo B → describe el personaje a fondo UNA vez (STYLE LOCK del estilo).
  **Siguientes:** `/edit` de la imagen anterior — "Use image from Scene X. Keep [personaje/set] identical.
  Change [acción/plano]" (cadena de consistencia del curso).
- Por escena `start_end`: par (start, end). La FRONTERA entre escenas comparte imagen (el end de N ES el
  start de N+1 — misma URL, cero costo extra).
- Trucos del curso aplicados: variante "you can see her teeth well" antes de clips con diálogo cerca
  (mejor lip-sync) · flip horizontal para contraplanos (modo podcast futuro) · el producto REAL entra por
  foto de referencia (`[REFERENCE IMAGE]`), jamás inventado.
- **UI: galería de keyframes en el drawer** — cada uno con su prompt visible (glass-box), botones
  regenerar ($0.15) / editar prompt / subir imagen propia (reemplazo manual SIEMPRE posible). Aprobar la
  galería desbloquea P4.
- Costo típico: 6 escenas ≈ 7 imágenes únicas ≈ **~$1.05** (vs ~$1/clip de video — corregir aquí es barato).

### P4 — Clips (compuerta 3: la existente "Generar video →" con costo visible)
Por escena: Kling v3 i2v `{ start_image_url: kf_start, end_image_url: kf_end, elements: [retrato cast],
prompt: motion_prompt (SOLO movimiento; modo B: prompt de transición por estilo — "create a seamless Pixar
animated transition between the first shot and the second shot… sound effects"), duration, generate_audio }`.
La narración sigue viajando entre comillas (audio nativo EN). Cola/presupuesto/variantes: lo ya construido.
Modo C: Sora 2 i2v one-take (un solo clip 12-16s, prompt 14 bloques, keyframe start opcional).
**Nota de secuencia:** el encadenado NO exige generar en serie — los keyframes ya fijan las fronteras, así
que los clips se generan EN PARALELO (la continuidad viene de las imágenes, no del orden).

### P5 — Post (ya construido + 1 extra)
Armar (concat) + captions karaoke + gancho (G2 vigente). **Extra nuevo (barato): "elementos nombrados"** —
con los timestamps por palabra ya disponibles, insertar overlays (PNG/imagen del producto/icono) en el
momento exacto en que la narración los dice (patrón video-use / los videos de YouTube del operador),
vía el mismo `ffmpeg-api/compose` (tracks + keyframes con timing). Cero infra nueva.

### P6 — Publicar (sin cambios)
Música del catálogo de la plataforma + label IA ON + agenda/campaña.

---

## 4 · Modo D — Footage propio (el camino del abogado y la velera)

**Principio: nunca destructivo.** El original se conserva; cada edición produce una variante nueva.

```
D1 SUBIR (mp4 → brand-assets, re-host)      [extender el upload existente a video]
D2 ENTENDER (whisper word-align — ya existe) → transcript con timestamps por palabra
D3 PLAN DE EDICIÓN glass-box (LLM sobre el transcript + fases 0-2):
   - cortes propuestos: muletillas, silencios largos (gaps entre palabras), tangentes
   - qué se queda (los "keeps" con su razón)
   - estilo de captions (karaoke de la marca) + gancho de apertura propuesto
   - overlays de marca: logo sutil, elementos nombrados, CTA final con la ESENCIA
   ✋ COMPUERTA: el usuario ve el plan (timeline simple), quita/añade cortes, aprueba
D4 COMPONER (ffmpeg-api/compose — ya existe): trims + concat + PNGs karaoke + overlays
D5 REEL FINAL re-hosteado + variantes por canal (safe zones por plataforma)
```
- Para la velera: el flujo es "te doy el guion (P1 de modo A) → grábalo con tu teléfono → súbelo → D2-D5".
- Para el abogado: sube las entrevistas de noticieros → D3 encuentra los mejores momentos (el LLM lee el
  transcript — el enfoque video-use: "lee el transcript, no mira frames") → clips cortos con captions +
  marca para su tráfico.
- v2 de este modo (después): detección de escenas con modelo de visión, b-roll automático, color grade.

---

## 5 · Cambios de código (por etapa, orden de construcción)

### Etapa V2.a — Encadenado con keyframes (modo A mejorado) ← EL QUICK WIN
| Archivo | Cambio |
|---|---|
| `lib/gateway/video-routing.ts` | `falImageToVideoBody`: aceptar `endImageUrl` → `end_image_url` |
| `lib/estudio/prompts.ts` | instrucción video: emitir `scenes[]` con `start/end_frame_prompt` + `motion_prompt` (reemplaza la fusión actual guion→prompt único por clip) |
| `app/api/estudio/keyframes/route.ts` (nuevo) | genera/regenera keyframes vía Nano Banana Pro (`/edit` en cadena), guarda en `design_spec.keyframes[]` con re-host |
| `components/estudio/keyframe-gallery.tsx` (nuevo) | galería aprobar/regenerar/editar/subir en el drawer |
| `app/api/estudio/video-generate/route.ts` | modo encadenado: por escena usa (kf_start, kf_end) aprobados; paraleliza |
| `lib/api/server/media-ledger.ts` | registrar costo de imágenes NB Pro ($0.15) en el ledger |

### Etapa V2.b — Asistente director + modo B (animado) y modo C (UGC)
6C-decompose de referencia subida (visión) · instrucciones de guion por modo (9 patrones / UGC 14 bloques)
· estilos con STYLE LOCK + prompts de transición · Sora 2 en el catálogo de modelos (`VIDEO_MODELS`).

### Etapa V2.c — Modo D (footage propio)
Upload de video · plan de edición glass-box + UI de timeline simple · compose de trims (el endpoint ya
soporta keyframes con offsets) · variantes por canal.

### Etapa V2.d — Elementos nombrados + b-roll (post enriquecido)
Overlays en timestamps de palabras (producto/iconos) · biblioteca de b-roll del proyecto (fotos reales del
usuario re-usadas como cutaways i2v cortos).

**Regla de construcción vigente:** verify EXIT 0 antes de cada commit; push inmediato; UI nunca llama
`supabase.from()` directo; migraciones solo con OK del operador (V2.a no necesita ninguna — todo vive en
`design_spec`/`asset` JSONB + brand-assets).

---

## 6 · Costos por modo (estimados verificados 2026-07-12; el ledger los registra reales)

| Modo | Composición | Costo típico |
|---|---|---|
| A encadenado (28s, 5 clips) | ~7 keyframes NB Pro $1.05 + 5 clips Kling ~$4.70 + compose ~$0.10 | **~$5.85** |
| B animado (50-60s, 10-12 escenas) | ~13 keyframes $1.95 + 11 clips Kling ~$9.25 (o Veo ~$22) + compose | **~$11.30** (Kling) |
| C UGC one-take (15s Sora 2 720p) | 1-2 keyframes + $4.50 | **~$4.80** |
| D footage propio | whisper ¢ + compose ~$0.10-0.35 | **<$0.50** |

⚠️ El tope actual `MEDIA_BUDGET_USD=20/mes` da ~3 reels modo A o ~1.5 modo B. **Decisión pendiente:** subirlo
o hacerlo configurable por proyecto.

---

## 7 · Decisiones que necesito del operador (para firmar)

1. **¿Etapa V2.a primero?** (encadenado modo A — resuelve TU queja de hoy con el mínimo código). Mi
   recomendación: sí, y probar con la misma pieza «Someone Else's Decision» re-desarrollada.
2. **Modo B estilos v1:** ¿arrancamos solo con Apple-realista + Pixar (los 2 más útiles para Papandi) y
   dejamos Claymation/Sci-fi/Wes Anderson para después?
3. **Presupuesto:** ¿subimos `MEDIA_BUDGET_USD` (ej. $50/mes) o configurable por proyecto?
4. **La tensión opener sagrado × duración** sigue abierta (un opener de 45 palabras = 18-22s hablados): ¿el
   asistente puede proponer RECORTES del opener en la compuerta 1 (tú decides), o sigue intocable?
5. **Los 2 scripts de YouTube** que ibas a pasar (el de folders y el del café) — cuando los tengas, los
   integro al diseño de "elementos nombrados" (V2.d).

## 8 · Qué NO haremos (guardrails)

- No clonar caras/voces de personas reales sin flujo de consentimiento (ToS + riesgo legal).
- No testimonios/reviews falsos en ads (las plantillas ADS IMAGEN se adaptan: estructura sí, contenido
  honesto — mecanismo, timeline de uso esperado, comparación funcional). C4 vigente.
- No música quemada. No auto-publicar. No cobrar regeneraciones como "créditos" (mandato UX del research).
- No construir V2.b/c/d antes de que V2.a pruebe el encadenado en un reel real.
