# Doctrina de video corto 2026 — investigación

> Investigación web (julio 2026) sobre mejores prácticas **verificadas** de Reels / TikTok / YouTube Shorts,
> con el objetivo de convertirlas en un **catálogo de personalizaciones** elegibles con botones antes de
> desarrollar un video (mismo patrón UX que la "apertura visual" de `lib/estudio/visual-hooks.ts`).
>
> **Tiers de evidencia** usados en todo el doc:
> - **[OFICIAL]** — data publicada por la plataforma (TikTok for Business, Meta).
> - **[ESTUDIO]** — estudio independiente con metodología conocida (MediaScience, Verizon+Publicis, BBC, Preply, Adobe).
> - **[HERRAMIENTA]** — blog de herramienta/agencia con data propia no auditada (OpusClip, Submagic, VirVid…). Señal útil, no ley.
> - **[PRÁCTICA]** — consenso de creadores sin data dura. Se marca como tal.

---

## 1. Hallazgos

### 1.1 Captions / subtítulos

**El mute es el modo por defecto de consumo.**

- 85% del video en Facebook se ve sin sonido (data de Meta) y 92% de los espectadores móviles ven con el sonido apagado (estudio Verizon + Publicis Media) — recopilado en [Kapwing — Subtitle Statistics](https://www.kapwing.com/resources/subtitle-statistics/) **[ESTUDIO]**; 75% de video móvil en mute según [Digiday](https://digiday.com/sponsored/75-percent-of-people-watch-mobile-videos-on-mute/) **[ESTUDIO]**.
- Generacional: 80% de los 18-25 años usa subtítulos "a veces o casi siempre" (BBC) y 50% de los estadounidenses los activa "casi siempre" (Preply) — vía [Kapwing](https://www.kapwing.com/resources/subtitle-statistics/) **[ESTUDIO]**.
- Matiz TikTok: 88% de sus usuarios dice que el **sonido es vital** en la plataforma — [TikTok for Business](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads) **[OFICIAL]**. Conclusión operativa: **diseñar para ambos mundos** — audio nativo que funciona solo + captions que sostienen el mute. No son alternativas.

**Captions = retención medible.**

- Los espectadores son **80% más propensos a terminar** un video con subtítulos (Verizon + Publicis) — vía [Kapwing](https://www.kapwing.com/resources/subtitle-statistics/) **[ESTUDIO]**.
- Estudio interno de Facebook: captions suben el view time **+12% en promedio** — [3Play Media](https://www.3playmedia.com/blog/captions-increase-viewership-for-facebook-video-ads/) **[OFICIAL-Meta]**; ads con captions convirtieron 12.5% vs 6.9% sin ellas — [Instapage](https://instapage.com/blog/closed-captioning-mute-videos) **[ESTUDIO]**.
- TikTok: los text boxes aparecen en **86% de los ads** y se asocian a **+64% de lift en conversión** — [Stackmatix citando TikTok Creative Center](https://www.stackmatix.com/blog/tiktok-creative-center-best-practices) **[OFICIAL vía tercero]**; "añadir captions impacta positivamente view time, brand affinity, likability, recall" — [TikTok creative best practices](https://ads.tiktok.com/help/article/creative-best-practices) **[OFICIAL]**.

**El estilo que retiene: karaoke palabra-a-palabra.**

- Mecánica: el texto aparece **palabra por palabra sincronizado al audio** (aparece/desaparece, 1-4 palabras por golpe), grande, ALL-CAPS, bold, blanco con **una palabra clave resaltada** (amarillo o verde) — la anatomía del estilo "Hormozi": [Ascynd — guía del estilo](https://ascynd.io/en/blog/hormozi-captions) y [Submagic](https://www.submagic.co/blog/how-to-make-alex-hormozi-captions) **[HERRAMIENTA]**.
- Por qué funciona: da al ojo un **punto de fijación nuevo cada 250-400 ms** (vs cada 2-4 s del subtítulo estático), justo en el acantilado de abandono de 1.5-3.5 s que muestran los eye-trackings — [EMAX Studio](https://emax.studio/blog/word-by-word-ai-captions-vs-static-subtitles) **[HERRAMIENTA]**. Convierte ver en leer activamente; la palabra resaltada es el ancla — [Ascynd](https://ascynd.io/en/blog/hormozi-captions) **[HERRAMIENTA]**.
- Resultados reportados: creadores que migraron a captions animados palabra-a-palabra reportan **+15-40% de duración media de vista** — [Ascynd](https://ascynd.io/en/blog/hormozi-captions) **[HERRAMIENTA]**.
- Quién popularizó el estilo: **CapCut** (auto-captions), **Submagic**, **Captions.ai** — comparativa en [With Love, Internet](https://withloveinternet.com/blog/short-form-videos-submagic-vs.-captions.ai-vs.capcut) **[HERRAMIENTA]**.
- Legibilidad: si hay texto en pantalla, ritmo máximo ~**5-10 palabras por segundo** — [MBADV citando TikTok](https://www.mbadv.agency/tiktok-ads/adding-text-overlays-and-ctas-in-tiktok-ads) **[OFICIAL vía tercero]**.

**Dónde va el texto: safe zones (lienzo 1080×1920).**

- **Instagram Reels [OFICIAL Meta, spec unificada 2026]**: dejar libre el **14% superior (~270 px)**, el **35% inferior (~670 px)** y **6% por lado (~65 px)** — [Behaviour Digital](https://behaviour.digital/post/meta-reels-safe-zone-14-top-35-bottom-6-sides-the-2026-official-guide), [AdsUploader](https://adsuploader.com/blog/meta-ads-safe-zones). Verificable con el "Safe Zone Guardrail" del Ads Manager.
- **TikTok**: las guías divergen — ~130 px arriba / ~250 px abajo / ~60 px lados según [Kreatli](https://kreatli.com/guides/safe-zone-guide) hasta 108 px arriba / **480 px abajo** / 60-120 px lados según [Orson Lord](https://orsonlord.com/articles/free-safe-zone-overlays-for-reels-tiktok-and-shorts) **[HERRAMIENTA]**. Unión conservadora: top ≥150 px, bottom ≥480 px, lado derecho ≥120 px (ahí vive la botonera).
- **YouTube Shorts**: mantener lo importante en la **banda central 1080×1440**; evitar el 10-15% inferior — [Kreatli](https://kreatli.com/guides/safe-zone-guide) **[HERRAMIENTA]**.
- **Regla práctica multiplataforma** (la unión de las tres): el caption karaoke vive en el **centro / ligeramente bajo el centro (45-65% de la altura)**; el hook de texto en el **tercio superior pero debajo del 14%**; **nada crítico en el 35% inferior**. (Síntesis de las fuentes de arriba.)

### 1.2 Ritmo de cortes

- **La regla 2-4 s es real**: los shorts de alto rendimiento promedian **un corte o pattern-interrupt cada 2-4 segundos** (jump cut, zoom, caption, efecto de sonido) — [VirVid](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time) **[HERRAMIENTA]**; la "regla de los 3 segundos": algo nuevo debe pasar ~cada 3 s (movimiento, ángulo, sonido, gráfico o giro emocional) — [Scenith](https://scenith.in/blogs/three-second-rule) **[HERRAMIENTA]**.
- **La atención móvil cae tras 2.7 s sin cambio** (estudio Adobe Creative Cloud 2025, citado por Scenith) — [Scenith](https://scenith.in/blogs/three-second-rule) **[ESTUDIO vía tercero]**.
- **El abandono se concentra al inicio**: 50-60% del drop-off total ocurre en los **primeros 3 segundos**; la meta que el algoritmo premia es **retención media ≥70%** — [OpusClip](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention) y [VirVid](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time) **[HERRAMIENTA, data propia]**.
- **Variedad de plano**: videos con cambios de escena frecuentes retienen **+32%** vs plano estático — [TechWithLandon](https://medium.com/@techwithlandon/want-over-70-retention-on-your-short-form-videos-heres-how-to-do-it-5ce7bae94a43) **[HERRAMIENTA]**; la edición rápida sube atención y retención del mensaje al eliminar el "cognitive downtime" (investigación de la University of Florida, citada por RenderCut) — [RenderCut](https://rendercut.io/b-rolls-increase-engagement-in-social-videos/) **[ESTUDIO vía tercero]**.
- **Advertencia anti-sobreedición**: el exceso de zooms/whooshes/cortes cansa (sobre todo a audiencias mayores) y se percibe caótico — [AIR Media-Tech](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8) **[HERRAMIENTA]**. El cambio debe ser **motivado** (acompaña la narración), no ruido.
- **Duración óptima 2026** — [Joyspace, data study](https://joyspace.ai/ideal-video-length-social-platform-2026) **[HERRAMIENTA]**:
  - TikTok viral: **11-18 s** (máximo completion + replays).
  - Reels: sweet spot viral **7-15 s**; "de valor" 30-45 s; Reels >3 min no se muestran a audiencias nuevas.
  - Shorts: **30-60 s**.
  - Los videos de **15-30 s** logran retención >80% — [OpusClip](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention) **[HERRAMIENTA]**.
  - Matiz honesto: en TikTok los videos >1 min acumulan **más watch time total** y ganan reach (data Buffer vía [Marketing Dive](https://www.marketingdive.com/news/research-tiktok-longer-videos-get-more-reach/743067/) **[ESTUDIO]**) — pero eso aplica a contenido narrativo largo bien paceado; para piezas de producto donde la señal es completion, el rango corto manda.

### 1.3 El primer segundo

- **63% de los ads con mejor CTR comunican su mensaje clave en los primeros 3 s** — reporte TikTok × CreatorIQ — [CreatorIQ](https://www.creatoriq.com/press/releases/tiktok-creatoriq-release-special-report-with-data-backed-keys-to-success-for-advertisers?hs_amp=true) **[OFICIAL]**.
- **90% del ad recall y 80% del awareness se capturan en los primeros 6 s** — [TikTok for Business](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads) **[OFICIAL]**; el estudio de laboratorio subyacente (343 sujetos, in-lab) es de MediaScience — [MediaScience](https://www.mediascience.com/case-studies/understanding-attention-on-tiktok-ads/) **[ESTUDIO]**.
- **Mostrar una persona en los primeros 2 s: +50% de hooking power y +32% de reconocimiento** — [TikTok × CreatorIQ](https://www.creatoriq.com/press/releases/tiktok-creatoriq-release-special-report-with-data-backed-keys-to-success-for-advertisers?hs_amp=true) **[OFICIAL]**.
- Movimiento en frame + texto overlay dentro de los primeros 3 s: **+38% de retención media** — [CapCut](https://www.capcut.com/create/short-form-video-hooks-first-3-second-patterns) **[HERRAMIENTA]**.
- El acantilado del eye-tracking está en **1.5-3.5 s**: si el ojo no tiene "algo siguiente" que fijar, se va — [EMAX Studio](https://emax.studio/blog/word-by-word-ai-captions-vs-static-subtitles) **[HERRAMIENTA]**.

**Lectura interna**: esto valida el catálogo `visual-hooks.ts` (acción física que interrumpe el patrón en el primer segundo) y la regla "tienes ~1 segundo, no 3" de `developTypeInstruction`. El primer frame ideal apila: **persona con expresión fuerte + acción ya iniciada + texto de gancho + alto contraste** — cada elemento tiene data propia arriba.

### 1.4 Otros multiplicadores verificados

- **B-roll / cutaways**: en A/B tests, los videos con B-roll superan a los estáticos en watch time y CTR; además el cutaway esconde el corte — [Captions.ai](https://captions.ai/blog/practical-guide-b-roll-video) y [RenderCut](https://rendercut.io/b-rolls-increase-engagement-in-social-videos/) **[HERRAMIENTA]**.
- **Punch-ins (zoom de golpe)**: el zoom digital disimula cortes y añade interés sin desorientar; alternar plano abierto / punch-in es el patrón estándar del short moderno — [OpusClip](https://www.opus.pro/blog/best-auto-zoom-in-tools), [Veed](https://www.veed.io/learn/jump-cuts) **[HERRAMIENTA]**.
- **Loops (el video termina donde empieza)**: cada vuelta cuenta como view en TikTok y "completar el loop se ha vuelto el indicador #1 de éxito en TikTok — por encima de comentarios o views" (Derick Rhodes, VP de Vimeo) — [Vimeo](https://vimeo.com/blog/post/does-looping-video-increase-views) **[ESTUDIO/experto]**. El watch time se multiplica con cada replay — [Influencers Time](https://www.influencers-time.com/looping-videos-boost-viewer-retention-and-algorithm-success/) **[HERRAMIENTA]**. Caveat del propio artículo de Vimeo: el loop por sí solo no garantiza nada — funciona cuando el contenido lo justifica (curiosity gap, transformación, acción circular).
- **CTA**: las CTA cards logran **+45% recall y +19% likeability** — [TikTok for Business](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads) **[OFICIAL]**; los verbos de acción ("Shop Now", "Start Free Trial") superan consistentemente a los pasivos ("Learn More") — [MBADV](https://www.mbadv.agency/tiktok-ads/adding-text-overlays-and-ctas-in-tiktok-ads) **[OFICIAL vía tercero]**. En orgánico, el CTA **nativo** (una frase hablada + overlay breve al final) evita el look de anuncio.
- **Sonido**: 88% de usuarios TikTok considera el sonido vital — [TikTok](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads) **[OFICIAL]**. El audio nativo del clip (voz + ambiente) es parte del gancho; el video debe funcionar **con y sin** sonido.
- **Contraste / color dominante en el primer frame**: práctica ya presente en la doctrina interna (primer frame apilado) y coherente con los hooks visuales; no se encontró data independiente que lo aísle — **[PRÁCTICA]**.

### 1.5 Qué genera la IA vs qué monta el editor

- **Los generadores no renderizan texto fiable.** Los modelos de difusión de video producen texto garabateado o borroso — [Rendi](https://www.rendi.dev/blog/best-video-generation-apis) **[HERRAMIENTA]**. Kling 3.0 anuncia mejoras de texto nativo — [Kling](https://kling.ai/blog/best-ai-video-generator-2026-kling-ai) — pero la best practice publicada incluso por guías del propio ecosistema Kling sigue siendo: **cero texto en el prompt de rodaje; componer el texto real en el editor** ("Remove all specific text requests from your Kling prompt… Composite real brand text on top in your video editor") — [KlingMotion](https://www.klingmotion.com/kling-3-0) **[HERRAMIENTA]**.
- **El caption karaoke es imposible en generación**: exige sincronía por-palabra con el audio final. Es **siempre capa de edición**. Esto confirma la arquitectura actual de Papandi (prompts limpios + zona limpia + `overlay-composer.tsx`).
- **Vías programáticas para captions automáticos (fase futura de Papandi)**:
  - **APIs render-por-JSON** con auto-transcripción y captions animados palabra-a-palabra: [Creatomate](https://creatomate.com/blog/how-to-automatically-add-subtitles-to-videos-using-an-api) (endpoint específico de subtítulos animados), [JSON2Video](https://json2video.com/video-automation/programmatic-video/), [Shotstack](https://samautomation.work/blog/best-video-apis-developers-2026/) (timeline JSON con overlays).
  - **Code-first**: [Remotion](https://www.plainlyvideos.com/blog/best-video-editing-api) — React, control por pixel; requiere infra de render propia (~$50-100/mes).
  - **DIY open-source**: [WhisperX](https://localaimaster.com/blog/whisperx-guide) da timestamps **por palabra** (±50 ms con forced alignment) → subtítulos `.ass` con tags karaoke `\k` — [whisper.cpp #884](https://github.com/ggml-org/whisper.cpp/issues/884) — → burn-in con [FFmpeg](https://32blog.com/en/ffmpeg/ffmpeg-whisper-auto-subtitles).
  - **SaaS empaquetado**: [Submagic](https://www.submagic.co/ai-caption) — el look "trendy" (emoji, highlight, animaciones) listo.
- **Hoy en Papandi**: `components/estudio/overlay-composer.tsx` compone el hook estático sobre **imagen** (preview CSS + export canvas). El equivalente de **video** necesitará: (a) preview del caption sobre el clip, (b) export server-side (Creatomate o FFmpeg+WhisperX). Decisión de spec futura — este doc solo fija el catálogo de elecciones.

---

## 2. Catálogo de personalizaciones propuesto (botones pre-develop)

Patrón UX existente: el selector de "apertura visual" (16 ganchos de `VISUAL_HOOKS` + "Papandi decide"). Estas personalizaciones extienden ese patrón y viajan en `DevelopExtras` igual que `visualHook`.

Leyenda "a dónde viaja": **rodaje** = dentro de los `video_prompts` (Kling/Veo) · **design_spec** = el JSON de la pieza · **editor** = capa de edición post-generación (overlay/captions) — nunca el generador.

| # | Personalización | Opciones (botones) | Default | A dónde viaja | Fuente |
|---|---|---|---|---|---|
| 1 | **Estilo de captions** | Karaoke grande (palabra-a-palabra, ALL-CAPS, highlight amarillo) · Blanco minimal (frases de 2-4 palabras) · Sin captions | Karaoke grande | **editor** (sincronía por palabra con la narración del guion) + `design_spec.captions` registra la elección. Los prompts de rodaje NO cambian (el texto jamás se genera) | [Kapwing](https://www.kapwing.com/resources/subtitle-statistics/), [EMAX](https://emax.studio/blog/word-by-word-ai-captions-vs-static-subtitles), [Ascynd](https://ascynd.io/en/blog/hormozi-captions) |
| 2 | **Ritmo de corte** | Rápido ~2 s · Normal 3-4 s · Respirado 5-6 s | Normal 3-4 s | **rodaje/guion**: duración y número de clips + micro-evento a mitad de clips >4 s + `design_spec.pacing` | [VirVid](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time), [Scenith/Adobe](https://scenith.in/blogs/three-second-rule) |
| 3 | **Energía de cámara** | Punch-ins · Handheld vivo · Locked (estable) | Punch-ins | **rodaje**: `camera.movement` de cada clip del design_spec | [OpusClip](https://www.opus.pro/blog/best-auto-zoom-in-tools), [Veed](https://www.veed.io/learn/jump-cuts) |
| 4 | **Loop** | Sí (el fin = el inicio) · No | No (sugerir Sí si gancho = `curiosity_gap` o `match_cut`) | **rodaje**: el prompt del último clip termina en el MISMO encuadre/acción del frame 1 del clip 1; el guion lo marca | [Vimeo](https://vimeo.com/blog/post/does-looping-video-increase-views) |
| 5 | **Posición del texto** | Tercio superior (bajo el 14%) · Centro | Hook: tercio superior · Captions: centro | **editor**: coordenadas del overlay (respetando safe zones) + **rodaje**: la "zona limpia" de cada prompt apunta a la banda elegida | [Meta oficial](https://behaviour.digital/post/meta-reels-safe-zone-14-top-35-bottom-6-sides-the-2026-official-guide), [Kreatli](https://kreatli.com/guides/safe-zone-guide) |
| 6 | **Duración total** | Micro 7-15 s · Estándar 15-30 s · Valor 30-45 s | Estándar 15-30 s | **rodaje/guion**: número de clips (2-3 / 3-5 / 5-6) y presupuesto de palabras por clip | [Joyspace](https://joyspace.ai/ideal-video-length-social-platform-2026), [OpusClip](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention) |
| 7 | **CTA de cierre** | Hablado + overlay · Solo overlay · Sin CTA | Hablado + overlay | **guion** (última línea hablada, con verbo de acción de la ESENCIA) + **editor** (overlay final) | [TikTok oficial](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads) |
| 8 | **Apertura visual** | (ya existe: 16 ganchos de `VISUAL_HOOKS`) | Papandi decide | **rodaje**: clip 1 (ya cableado vía `visualHook` en `DevelopExtras`) | `lib/estudio/visual-hooks.ts` |

Notas de diseño del catálogo:

1. **"Papandi decide" en todas** — default inteligente derivado del tipo de pieza, el gancho retórico y la apertura visual elegida (ej.: gancho `curiosity_gap` sugiere Loop=Sí + Micro 7-15 s).
2. **Tooltip de una línea por botón** con el dato que lo respalda ("80% más probable que terminen tu video" en Karaoke) — glass-box, coherente con el moat de Papandi.
3. Las elecciones #1, #5 y #7 **no tocan los prompts de rodaje** (capa editor); #2, #3, #4 y #6 **sí** los moldean. Esa separación es la misma doctrina texto-vs-fondo que ya rige imágenes.

---

## 3. Cambios recomendados a las reglas actuales del develop (`developTypeInstruction`, caso "video")

### Se confirma (no tocar)

| Regla actual | Veredicto | Evidencia |
|---|---|---|
| 15-35 s techo duro, "NUNCA 45-60s" | **Confirmada** | 15-30 s retiene >80%; viral TikTok 11-18 s, Reels 7-15 s — [Joyspace](https://joyspace.ai/ideal-video-length-social-platform-2026), [OpusClip](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention) |
| Movimiento obligatorio + cámara con golpe + acción en el primer segundo | **Confirmada** | 63% de ads top comunican en <3 s; atención cae a los 2.7 s; drop-off 50-60% en 3 s — [CreatorIQ](https://www.creatoriq.com/press/releases/tiktok-creatoriq-release-special-report-with-data-backed-keys-to-success-for-advertisers?hs_amp=true), [Scenith](https://scenith.in/blogs/three-second-rule), [OpusClip](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention) |
| Cara comunica antes de hablar / persona en frame 1 | **Confirmada y reforzada** | Persona en <2 s = +50% hooking power — [TikTok×CreatorIQ](https://www.creatoriq.com/press/releases/tiktok-creatoriq-release-special-report-with-data-backed-keys-to-success-for-advertisers?hs_amp=true) |
| `hook_text_overlay` ≤8 palabras | **Confirmada** | Legibilidad 5-10 palabras/s: 8 palabras en un frame de ~1.5 s está en rango — [MBADV/TikTok](https://www.mbadv.agency/tiktok-ads/adding-text-overlays-and-ctas-in-tiktok-ads) |
| El texto NUNCA lo renderiza el generador | **Confirmada** | Incluso guías pro-Kling lo mandan a post — [KlingMotion](https://www.klingmotion.com/kling-3-0), [Rendi](https://www.rendi.dev/blog/best-video-generation-apis) |
| Repetir personaje/set/voz completos por clip | **Confirmada** (sin fuente externa nueva; mitigación correcta al no-recuerdo entre clips, verificada en el test vivo 2026-07-01) | interna |

### Se ajusta o se añade

1. **Micro-evento dentro del clip** (ajuste a "3-5 clips de 4-10s"): la frontera de clip da un cambio cada 4-10 s, pero la data pide **cambio cada 2-4 s**. Añadir: *"en todo clip >4 s, el prompt incluye UN cambio visible a mitad (punch-in, giro, objeto que entra al cuadro, cambio de fase de la acción)"* — [VirVid](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time), [Scenith](https://scenith.in/blogs/three-second-rule).
2. **Safe zones numéricas** (sustituye "zona limpia para overlays", hoy vaga): *"nada crítico en el 14% superior ni el 35% inferior del encuadre; la acción y el espacio para texto viven en la banda central"* — [Meta oficial](https://behaviour.digital/post/meta-reels-safe-zone-14-top-35-bottom-6-sides-the-2026-official-guide), [Kreatli](https://kreatli.com/guides/safe-zone-guide).
3. **Duración parametrizada** (botón #6): mantener 15-30 s como default, permitir Micro 7-15 s (viral) y Valor 30-45 s — [Joyspace](https://joyspace.ai/ideal-video-length-social-platform-2026).
4. **Loop opcional** (botón #4): línea condicional — *"el último clip termina en el MISMO encuadre/acción del primer frame del clip 1 (loop invisible)"* — [Vimeo](https://vimeo.com/blog/post/does-looping-video-increase-views).
5. **CTA nativo explícito en video** (botón #7): *"el cierre = 1 frase hablada de CTA nacida de la ESENCIA + [texto en pantalla] con verbo de acción"* — [TikTok](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads).
6. **Captions como capa declarada**: añadir al bloque de [texto en pantalla]: *"los subtítulos karaoke NO van en el guion ni en los prompts — son capa de edición sincronizada a la NARRACIÓN exacta del guion (que es su fuente literal)"*. Hoy es implícito; el botón #1 lo vuelve contrato.

---

## 4. Fuentes (lista completa)

**Oficiales / plataforma**

1. [TikTok for Business — Creative Best Practices](https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads) — 90% recall en 6 s; CTA cards +45%/+19%; 88% sonido vital.
2. [TikTok — Creative best practices for performance ads](https://ads.tiktok.com/help/article/creative-best-practices) — captions boost view time/recall.
3. [TikTok × CreatorIQ — Special Report](https://www.creatoriq.com/press/releases/tiktok-creatoriq-release-special-report-with-data-backed-keys-to-success-for-advertisers?hs_amp=true) — 63% mensaje en <3 s; persona en <2 s +50%.
4. [Behaviour Digital — Meta Reels Safe Zone 14/35/6 (guía 2026)](https://behaviour.digital/post/meta-reels-safe-zone-14-top-35-bottom-6-sides-the-2026-official-guide)
5. [AdsUploader — Meta Ads Safe Zones](https://adsuploader.com/blog/meta-ads-safe-zones)
6. [3Play Media — Facebook: captions +12% view time](https://www.3playmedia.com/blog/captions-increase-viewership-for-facebook-video-ads/)

**Estudios / prensa**

7. [Kapwing — Subtitle Statistics](https://www.kapwing.com/resources/subtitle-statistics/) — agrega Meta 85%, Verizon+Publicis 92%/80%, BBC 80% Gen Z, Preply 50%.
8. [Digiday — 75% of mobile videos on mute](https://digiday.com/sponsored/75-percent-of-people-watch-mobile-videos-on-mute/)
9. [MediaScience — Understanding attention on TikTok](https://www.mediascience.com/case-studies/understanding-attention-on-tiktok-ads/)
10. [Vimeo — Does looping video increase views?](https://vimeo.com/blog/post/does-looping-video-increase-views)
11. [Marketing Dive — Longer clips gaining traction on TikTok (Buffer)](https://www.marketingdive.com/news/research-tiktok-longer-videos-get-more-reach/743067/)
12. [Instapage — Closed captioning y videos en mute](https://instapage.com/blog/closed-captioning-mute-videos)

**Herramientas / blogs con data propia**

13. [Scenith — The 3-Second Rule (cita Adobe 2025: 2.7 s)](https://scenith.in/blogs/three-second-rule)
14. [VirVid — 70%+ retention en Shorts](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time)
15. [OpusClip — Ideal YouTube Shorts length (data-backed)](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention)
16. [OpusClip — Auto zoom / punch-in tools](https://www.opus.pro/blog/best-auto-zoom-in-tools)
17. [Joyspace — Ideal video length per platform 2026 (data study)](https://joyspace.ai/ideal-video-length-social-platform-2026)
18. [EMAX Studio — Word-by-word captions vs static (eye-tracking)](https://emax.studio/blog/word-by-word-ai-captions-vs-static-subtitles)
19. [Ascynd — Hormozi-style captions (guía exacta)](https://ascynd.io/en/blog/hormozi-captions)
20. [Submagic — How to make Alex Hormozi captions](https://www.submagic.co/blog/how-to-make-alex-hormozi-captions)
21. [With Love, Internet — Submagic vs Captions.ai vs CapCut](https://withloveinternet.com/blog/short-form-videos-submagic-vs.-captions.ai-vs.capcut)
22. [Kreatli — Safe Zone Hub (Reels/TikTok/Shorts)](https://kreatli.com/guides/safe-zone-guide)
23. [Orson Lord — Free safe-zone overlays](https://orsonlord.com/articles/free-safe-zone-overlays-for-reels-tiktok-and-shorts)
24. [MBADV — Text overlays y CTAs en TikTok Ads](https://www.mbadv.agency/tiktok-ads/adding-text-overlays-and-ctas-in-tiktok-ads)
25. [Stackmatix — TikTok Creative Center best practices](https://www.stackmatix.com/blog/tiktok-creative-center-best-practices)
26. [AIR Media-Tech — Advanced retention editing](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8)
27. [Captions.ai — Practical guide to B-roll](https://captions.ai/blog/practical-guide-b-roll-video)
28. [RenderCut — B-rolls y engagement (cita U. Florida)](https://rendercut.io/b-rolls-increase-engagement-in-social-videos/)
29. [TechWithLandon — 70% retention (+32% scene changes)](https://medium.com/@techwithlandon/want-over-70-retention-on-your-short-form-videos-heres-how-to-do-it-5ce7bae94a43)
30. [Veed — Jump cuts y punch-ins](https://www.veed.io/learn/jump-cuts)
31. [Influencers Time — Looping videos y retención](https://www.influencers-time.com/looping-videos-boost-viewer-retention-and-algorithm-success/)
32. [CapCut — First 3-second hook patterns](https://www.capcut.com/create/short-form-video-hooks-first-3-second-patterns)

**Generación IA y captions programáticos**

33. [Kling — Best AI video generator 2026](https://kling.ai/blog/best-ai-video-generator-2026-kling-ai)
34. [KlingMotion — Kling 3.0 (texto: componer en post)](https://www.klingmotion.com/kling-3-0)
35. [Rendi — Best video generation APIs (límite de texto en difusión)](https://www.rendi.dev/blog/best-video-generation-apis)
36. [Creatomate — Auto-subtitles via API](https://creatomate.com/blog/how-to-automatically-add-subtitles-to-videos-using-an-api)
37. [JSON2Video — Programmatic video](https://json2video.com/video-automation/programmatic-video/)
38. [Samautomation — Shotstack vs Creatomate vs JSON2Video](https://samautomation.work/blog/best-video-apis-developers-2026/)
39. [Plainly — Best video editing APIs (Remotion)](https://www.plainlyvideos.com/blog/best-video-editing-api)
40. [Local AI Master — WhisperX (timestamps por palabra)](https://localaimaster.com/blog/whisperx-guide)
41. [32blog — FFmpeg + Whisper auto-subtitles](https://32blog.com/en/ffmpeg/ffmpeg-whisper-auto-subtitles)
42. [whisper.cpp #884 — Karaoke .ass output](https://github.com/ggml-org/whisper.cpp/issues/884)
43. [Submagic — AI caption generator](https://www.submagic.co/ai-caption)

---

*Documento de investigación — julio 2026. Sin código; el catálogo §2 y los ajustes §3 alimentan el próximo spec del Estudio (F-Video).*
