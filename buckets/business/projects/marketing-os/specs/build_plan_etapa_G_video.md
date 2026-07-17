# Build Plan — Etapa G: Personalización de video + Post-producción (output-side)

**Estado:** v2 — **G1 + G2 CONSTRUIDOS y en prod (2026-07-11); G3 (frame chaining) pendiente/opcional.** Pivote EN-first del operador (2026-07-11): el mercado primario es inglés → el lip-sync nativo de Kling funciona (el hueco era español); el develop ya escribe "en el idioma del mercado". Implementación: G1 = `lib/estudio/video-prefs.ts` (5 botones ritmo/cámara/loop/duración/CTA → `AJUSTES DEL REEL` en el system del develop; UI en /angulos, persistido en estudio-choices) + `design_spec.clip_narrations` (la narración exacta por clip — fuente de los captions). G2 = TODO vía fal con la misma llave/cola (verificado contra su OpenAPI): `video-align` (whisper `chunk_level=word` = timestamps POR PALABRA sobre el reel armado; fallback proporcional determinista) + `lib/video/captions.ts` (beats 1-3 palabras + .srt/.ass karaoke) + `lib/video/caption-png.ts` (beats y gancho como PNG client-side, safe zones 14/35) + `video-compose` (ffmpeg-api/compose: concat en orden + quemado de overlays por lanes) → entra por la MISMA cola pending → `video-status` cosecha (acepta `{video_url}`) y RE-HOSTEA el reel durable → variantes «Reel armado»/«Reel final» → «Usar esta». UI: `components/estudio/reel-assembler.tsx` en el drawer. Nota de la 1ª prueba: si el concat sale MUDO, el botón «rearmar con pista de audio» activa `withAudioTrack` (comportamiento del video-track de compose sin documentar). Documentación aprobada por el operador 2026-07-06.
**Decide:** los botones de personalización pre-generación + el pipeline de post-producción en la web (captions karaoke, concat, overlays, frame chaining).
**Fuentes:** `docs/research/doctrina-video-2026.md` (catálogo de 8 personalizaciones, safe zones, costos, fuentes verificadas) · `docs/app/ensamblador-de-prompts.md` (design_spec, dialectos) · mapa de producción (explorador, esta sesión) · decisiones del operador (rondas 2-4 + 2026-07-06).

---

## 0. Dónde encaja (no re-cablea el modelo, lo consume)

El modelo de contenido (P1-P5) toca el **INPUT** del develop. Etapa G es **OUTPUT-side**: cuelga de lo que el develop YA produce (`design_spec`, `video_prompts` por clip, `hook_text_overlay`, la narración del guion) y de lo que Kling YA genera (los clips). No re-cablea nada del modelo.

---

## 1. Los 8 botones de personalización (pre-generación) — `doctrina-video-2026.md §2`

| # | Botón | Opciones | Default | Dónde viaja | Estado |
|---|---|---|---|---|---|
| 1 | Estilo de captions | karaoke · minimal · sin | karaoke | editor + `design_spec.captions` | ❌ planeado |
| 2 | Ritmo de corte | rápido 2s · normal 3-4s · respirado 5-6s | normal | rodaje/guion (nº clips + micro-evento) | ❌ planeado |
| 3 | Energía de cámara | punch-ins · handheld · locked | punch-ins | `design_spec.camera.movement` | ⚠️ parcial (en prompt, sin UI) |
| 4 | Loop | sí · no | no (sí si gancho=curiosity/match_cut) | rodaje (último clip = frame 1) | ❌ planeado |
| 5 | Posición del texto | tercio superior · centro | hook arriba / captions centro | editor (safe zones) + rodaje | ❌ planeado |
| 6 | Duración total | micro 7-15s · estándar 15-30s · valor 30-45s | estándar | rodaje/guion (nº clips + word budget) | ❌ planeado |
| 7 | CTA de cierre | hablado+overlay · solo overlay · sin | hablado+overlay | guion + editor | ⚠️ parcial |
| 8 | Apertura visual | 16 ganchos (`visual-hooks.ts`) | — | rodaje / clip 1 | ✅ construido |

Los botones que tocan el **GUION** (2, 4, 6, 7) entran al prompt del develop **antes** de generar; los de **EDITOR** (1, 5) son post-producción.

---

## 2. El pipeline de post-producción (in-app, mayormente DETERMINISTA)

```
clips ─▶ concat (FFmpeg, si son singles) ─▶ WhisperX ALINEA la narración conocida ─▶ captions karaoke ─▶ overlay (hook + safe zones) ─▶ export
```

- **Captions:** WhisperX **no transcribe — ALINEA** el texto YA conocido del guion (forced alignment ±50ms) → karaoke sincronizado a la palabra. La fuente literal es la narración del develop; por eso es barato y exacto.
- **Concat:** FFmpeg `concat` cuando son **singles** (nuestro caso por defecto — los prompts ricos superan los 512 chars de `multi_prompt`). El `multi_prompt` de Kling ya viene unido.
- **Overlay:** `hook_text_overlay` (≤8 palabras) en **safe zones** (14% superior / 35% inferior / 6% lados — Meta oficial). El `overlay-composer` existe para IMAGEN; falta la **versión VIDEO** (preview sobre clip + export).
- **Costo ≈ 5% del de generar.** Render: Creatomate/Shotstack (~$0.10-0.60/min) o worker FFmpeg propio.
- **Dónde vive:** en la web (post-producción casi autónoma), no en CapCut.

---

## 3. Frame chaining — el caso "toma continua sin cortes" (lo último)

- **Extracción del último frame:** **canvas client-side ($0)** — cargar el clip, saltar al final, dibujar a canvas, exportar imagen.
- **Uso:** esa imagen = `start_image_url` del clip N+1 (image-to-video Kling).
- **Catches (por eso va al final):** la generación se vuelve **SECUENCIAL** (clip N+1 espera a clip N) + **deriva generacional** por eslabón + el develop debe cerrar cada clip **"en posición de entrega"**. Opción calidad: **FLUX Kontext** limpia/varía el frame antes de encadenar.
- **Alternativa barata (default, ya en el modelo):** clips que cierran en **beat limpio** → los cortes funcionan sin cadena; el set se mantiene por **imagen + descripción repetida**. Frame chaining SOLO para el efecto de una sola toma que fluye. **Un reel normal son cortes — no lo necesita.**

---

## 4. Fases de build

- **G1** — botones que tocan el guion (2, 4, 6, 7) al prompt del develop + su UI. Barato: extiende lo ya parcial (cámara, CTA).
- **G2** — pipeline de post-producción: concat + WhisperX align + captions karaoke + `overlay-composer` VIDEO + export. El grueso.
- **G3** — frame chaining (toma continua) con orquestación secuencial + FLUX Kontext. El más caro; opcional.

---

## 5. Verificación
- **G1:** un reel desarrollado respeta el botón elegido (ritmo/duración/CTA/loop) en el guion.
- **G2:** captions karaoke sincronizados a la narración exacta; overlay dentro de safe zones; export reproducible; costo ≈5%.
- **G3:** dos clips encadenados fluyen sin corte visible; deriva controlada.

---

## 6. Fuera de alcance
- TTS/voz clonada (descartado — audio nativo de Kling).
- Música con licencia (fase posterior).
