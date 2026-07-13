# build_plan_director_de_video — Plan de construcción (las 4 etapas)

> **Estado: 🟢 ETAPAS 1+2 CERRADAS CON ÉXITO (2026-07-13) — primer reel end-to-end de Papandi producido y quemado. Sigue: Etapa 3.** Spec madre: `spec_Director_de_Video.md` (pre-check
> completo). Patrón de entrega: igual que G1/G2a/G2b — cada etapa se construye, `npm run verify` EXIT 0,
> commit+push (Vercel deploya), prueba real, y SOLO entonces la siguiente. Repo: `sandia-marketing`.
>
> **Para arrancar la Etapa 1 faltan 2 inputs del operador:** ①pantalla completa vs drawer ②su «dale».
> Pre-condición acordada: el operador borra las piezas de prueba (cero legacy).

---

## Etapa 1 — Cajas + Ajustes (el Director existe, sin gastar en imágenes aún)

**Entrega:** el botón «Desarrollar para X» abre el flujo ①→②; el develop devuelve `scenes[]` (cajas
editables por clip); el usuario edita y aprueba. Cero costo nuevo (misma llamada LLM de siempre).

- [x] 1.1 `lib/estudio/scenes.ts` (NUEVO, puro+tests): tipos `Scene` (cajas: guion, producto, encuadre,
      sujeto, camara, iluminacion, audio, primer_frame, ultimo_frame, seconds, block) + `coerceScenes()`
      (tolerante) + `composeMotionPrompt(scene)` (encuadre+cámara+acción+`"guion"` — SOLO movimiento) +
      `composeKeyframePrompt(scene, "start"|"end")` (sujeto+iluminación+frame+estilo) + `sceneBudget(scene)`
      (palabras/seg over/under — reusa la lógica de `clipWordBudget`).
- [x] 1.2 `lib/estudio/concepts.ts` (NUEVO, puro+tests): el catálogo determinístico de 12 formatos
      {key, nombre, línea, ejemplo, sirve_para, escena_base} + «Papandi decide» (reglas por intent+canal)
      + «Otro» (texto libre).
- [x] 1.3 `lib/estudio/prompts.ts`: la instrucción de video emite `scenes[]` en ===SPEC=== (reemplaza
      `video_prompts`/`clip_narrations` — la caja guion ES la narración) + recibe TIPO de reel + CONCEPTO
      + AMBIENTE + **intent dar/pedir EXPLÍCITO con sus 2 reglas** + presets por tipo (UGC realismo /
      Animado style-lock / Presentadora cast). La doctrina existente (arco, movimiento, safe zones,
      canal) NO cambia — cambia el FORMATO de salida.
- [x] 1.4 `app/api/estudio/produce/route.ts`: body gana `{tipoReel, concepto, conceptoCustom, ambiente}`;
      **offer_statement ESTRUCTURADO** (is_for_you_if + what_you_get bullets) cuando intent=pedir;
      registra `concept_custom` en qa_flags (el evento formal llega en Etapa 3).
- [x] 1.5 `lib/estudio/parse.ts`: parsea `scenes[]`; `clipWordBudget` lee scenes (el formato viejo ya no
      existe — piezas borradas); guard mínimo anti-crash.
- [x] 1.6 UI del Director (decisión de ubicación del operador): indicador de pasos ①-⑥ + pantalla ①
      (chips tipo/concepto/ambiente + los 5 botones G1 SE MUDAN aquí) + pantalla ② (tarjetas por clip,
      cajas editables colapsables, **contador de voz EN VIVO**, caja «Tu producto en esta pieza» ⭐,
      «Aprobar guion y prompts →»). La tarjeta de /angulos pierde los botones G1.
- [x] 1.7 `verify` EXIT 0 · commit+push · **criterio DONE:** re-desarrollar «Someone Else's Decision»
      produce cajas; editar una caja cambia el prompt compuesto; el contador avisa over/under en vivo.

## Etapa 2 — Keyframes + encadenado (la continuidad — resuelve la queja original)

**Entrega:** pantalla ③ (galería) + ④ (clips encadenados). El reel de prueba sale CONTINUO.

- [~] 2.1 (end_image_url + modo escenas ✅; sora-2/veo-flf al catálogo PENDIENTE de verificar sus schemas — 2.1b) `lib/gateway/video-routing.ts`: `falImageToVideoBody` acepta `endImageUrl` → `end_image_url`;
      `VIDEO_MODELS` gana `sora-2` (i2v pro, $0.30-0.70/s) y `veo-3.1-flf` (first-last-frame, $0.40/s);
      `planGeneration` modo escenas: 1 clip = 1 job (sin packing; `multi_prompt` muere con el legacy).
- [x] 2.2 `app/api/estudio/keyframes/route.ts` (NUEVO): genera el set de keyframes vía
      `fal-ai/nano-banana-pro` (primera imagen desde el retrato del cast si tipo=Presentadora; siguientes
      vía `/edit` "keep identical, change…"), **frontera compartida** (end N = start N+1, misma URL),
      re-host a brand-assets, guarda `design_spec.keyframes[]` {scene, role, url, prompt, approved};
      soporta regenerar UNO y subir propia. Costo al ledger ($0.15/img).
- [x] 2.3 `components/estudio/keyframe-gallery.tsx` (NUEVO): galería con prompt visible por imagen +
      regenerar/editar prompt/subir + la frontera se muestra UNA vez (glass-box del encadenado) +
      «Aprobar imágenes →» (compuerta 2).
- [x] 2.4 `app/api/estudio/video-generate/route.ts`: modo encadenado — por escena
      `{start_image_url, end_image_url, prompt: composeMotionPrompt, elements: cast}` en PARALELO;
      presupuesto incluye imágenes ya gastadas; variantes/cola/anti-doble-click intactos.
- [x] 2.5 `verify` EXIT 0 · commit+push · **criterio DONE:** el frame de la frontera N/N+1 es la MISMA
      imagen y la cara es consistente en los 5 clips.
- [x] 2.6 **PRUEBA REAL — ÉXITO 9.8/10 (operador, 2026-07-13):** transición 1→2 «perfecta perfecta», mensaje muy bueno, loop perfecto. Inconsistencia menor cazada y corregida a futuro: FÍSICA DEL SELFIE (frame vacío = cámara flotante; el preset UGC ya lo prohíbe — el loop cierra con ELLA en posición). + auto-cosecha de la cola cada 20s. Falta solo: armar+captions del reel completo (⑤, en el panel): re-desarrollar «Someone Else's Decision» → cajas →
      keyframes → 5 clips → armar+captions. Checklist doctrina-video-2026 §1 + continuidad. El resultado
      decide ajustes antes de Etapa 3.

## Etapa 3 — Edición enriquecida (música + elementos nombrados + feedback + referencia)

- [x] 3.1 Música — CONSTRUIDO 2026-07-13 (licencia confirmada por correo → quemar SÍ está permitido).
      Diseño final MÁS SIMPLE que el planeado: sin bucket nuevo ni tabla `music_tracks` — las pistas
      viven en `brand-assets/_music/` + `index.json` (id/nombre/mood, el mood sale de la carpeta madre
      del pack). `scripts/upload-music.mjs "<carpeta>"` sube todo (idempotente, `--dry` disponible).
      Selector con filtro de mood + preview `<audio>` en ⑤; el QUEMADOR PROPIO (video-burn) mezcla la
      pista BAJO la voz con `filter_complex` (volume 0.22 + fade-out 1.5s + amix duration=first +
      stream_loop si la pista es corta) — no fal compose (concat-only). Solo acepta URLs del catálogo
      propio. **CERRADO 2026-07-13 (noche):** las 562 pistas encontradas en el disco del operador
      (`Downloads/Sound Effects Populares-…`) y subidas — 561 arriba (1 saltada >25MB), 21 moods
      (calma/épico/story/vibra oscura/…), índice público verificado HTTP 200. La mezcla ffmpeg se
      validó LOCAL con los args exactos de la ruta (stream_loop + amix termina; salida = duración
      del video). Falta solo la prueba con un reel real del operador.
- [x] 3.2 Elementos nombrados — CONSTRUIDO 2026-07-13 (noche), v1 SIN esperar los transcripts (eran
      insumo de diseño; la mecánica no dependía de ellos — si al verlos cambia el gusto, se ajusta).
      El QUEMADOR PROPIO acepta `overlays[]` (≤6, solo storage propio): -loop 1 acotado con -t
      (sin tope ffmpeg quedaba COLGADO — cazado local), scale2ref con `main_w` (relativo al video),
      overlay centrado con enable=between. UI en ⑤: alinear la voz → elegir LA PALABRA (dropdown
      con timestamps) + imagen (keyframe de la pieza o subir ≤3MB vía element-upload) + duración +
      tamaño. Compatible con música en el mismo filter_complex. VALIDADO LOCAL con frames: el
      elemento está en t=3 y no está en t=6.
- [x] 3.3 Feedback capa 1+2 — CONSTRUIDO 2026-07-13. Tabla `piece_events` (migración
      20260713120000, aplicada en prod con el OK del operador; admin-only como project_api_calls, RLS
      sin policies) + `logPieceEvent` best-effort. Server: develop/keyframes/clips/burn (con costo,
      regen, new_person, ugc_cast, estilo de captions elegido y música). Cliente vía
      `/api/estudio/event` (whitelist + pertenencia por RLS): scenes_approved (con `edited`),
      keyframes_approved, cast_saved, reel_feedback. UI 👍/👎 + nota opcional al pie del ensamblador
      cuando existe el Reel final. (El diff caja-por-caja al aprobar queda para capa 2 fina.)
- [x] 3.4 Referencia visual — CONSTRUIDO 2026-07-13 (noche). El wrapper LLM se extendió a VISIÓN
      (`LlmMessage.images[]` → bloques de imagen en la ruta Anthropic; OpenRouter los ignora,
      documentado). `/api/estudio/reference-decompose`: screenshot (jpeg/png/webp ≤3MB — límite de
      body de Vercel) → Sonnet visión → 6C (ambiente/luz/encuadre/cámara/estilo/paleta) → guía
      compuesta en español, EDITABLE en ① (glass-box C17) → viaja al develop como `referenciaVisual`
      (instrucción: es el LOOK, jamás el contenido — ni marcas ni personas). Evento
      `reference_decomposed` con costo.
- [x] 3.4b Personas UGC ↔ Identidad — CONSTRUIDO 2026-07-13. «💾 Guardar esta persona en Identidad»
      en la galería ③ (solo piezas de persona generada; promueve el primer keyframe CON persona al
      cast como personaje aprobado, idempotente por URL, con su prompt glass-box). Selector inverso en
      ① (tipo UGC, foto-chips): 🎲 nueva o una del elenco → `ugc_cast_id` viaja en el design_spec; el
      develop cambia el sujeto a imagen-de-referencia (sin re-describir la cara), keyframes la usa de
      ancla y video-generate la refuerza vía elements (sin el set de marca, que pelearía con el UGC).
- [x] 3.5b Palabras gigantes (hooks tipográficos estilo CapCut) — CONSTRUIDO 2026-07-13 (noche),
      pedido del operador con screenshots de referencia («hook one», «ESTO es un VISUAL HOOK»).
      `lib/video/word-sticker.ts`: cada palabra es un STICKER independiente renderizado EN CANVAS
      en el navegador (WYSIWYG, $0) con 5 efectos (impacto 3D / neón / sticker / glitch / cómic) +
      color/fuente/tamaño/rotación (horneada en el PNG vía bbox rotado). Panel «Palabras gigantes»
      en el preview de estilo del ensamblador: arrastre libre X+Y, entrada desde el inicio o CON su
      palabra alineada, duración. Al quemar: se renderiza en alta res (2× el ancho final, tope
      2000px) → sube vía element-upload → entra como overlay con `xPct` (CENTRO libre) en video-burn
      (expresión `overlay=x=W*xPct-w/2:y=H*yPct-h/2` validada LOCAL con frame extraído). Tope
      combinado 6 imágenes (elementos + palabras). Los 5 renders validados en navegador (dimensiones
      reales + fuentes cargadas). Commit 3833d79.
- [~] 3.5 `verify` EXIT 0 (411 tests) + build de producción EXIT 0 · push (3833d79) · **ETAPA 3
      COMPLETA en código** (música + elementos + feedback + referencia + personas + palabras
      gigantes); el criterio («un reel suena con música bajo la voz + un overlay/palabra aparece en
      el segundo exacto de su palabra») está validado LOCAL con los args exactos de la ruta — falta
      la corrida REAL del operador sobre su reel en prod. Revisión adversarial multi-agente del
      diff completo de la noche EN CURSO (2026-07-13).

## Etapa 4 — «Traigo mi video» (modo D)

- [x] 4.1 — CONSTRUIDO 2026-07-13 (noche). Subida DIRECTA navegador→storage vía TUS resumable
      (`lib/api/upload-media.ts`, tus-js-client, chunk 6MB exacto, token de la sesión del usuario —
      el archivo JAMÁS pasa por Vercel). Límites ≤10 min / ≤1GB validados client-side (duración
      medida con `<video>` antes de subir). Políticas de storage verificadas (authenticated inserta
      en brand-assets). `own-footage-init` crea la pieza del slot SIN LLM (dedupe + insertPiece
      `production_mode=video_propio`; el video va en `asset.url` para el whitelist de video-align).
      OJO: si el límite GLOBAL de Storage (Settings → Upload file size limit) es menor que el
      archivo, TUS recibe 413 — el error del cliente dice exactamente qué tocar.
- [x] 4.2 — CONSTRUIDO. `/api/estudio/edit-plan`: whisper word-level (autodetecta idioma — el video
      propio puede venir en ES; caché en asset.align) → `lib/video/edit-plan.ts` `planFromWords`
      DETERMINISTA sin LLM (corta en pausas >0.9s, parte segmentos >16s en puntuación, desmarca
      ruido; cada segmento con su razón glass-box: «recorta 2.3s de silencio antes») + 7 tests.
      El plan vive EDITABLE en `design_spec.edit_plan`. (El gancho/CTA del plan original quedan
      para v2 — v1 corta silencios y deja elegir tomas, que es el 80% del valor.)
- [x] 4.3 — CONSTRUIDO. `/api/estudio/video-edit`: ffmpeg PROPIO (ensureFfmpeg compartido en
      `lib/api/server/ffmpeg.ts`) aplica trim+atrim+concat de lo conservado → variante «Reel
      armado» (grupo 90) → el ensamblador de SIEMPRE hace ⑤ (captions karaoke de la VOZ REAL del
      operador vía whisper del reel cortado + música + feedback). Filtro validado LOCAL (12s →
      segmentos 1-3 + 5-8 = salida 5.00s exactos). UI: `OwnFootageDirector` en el Director
      (botón «🎞 Traigo mi video» ACTIVADO en ①; subir con % → plan con checkboxes y ▶ seek a la
      toma → aplicar → ensamblador); restore al recargar detecta piezas own_footage.
- [~] 4.4 `verify` EXIT 0 (411 tests) + build de producción EXIT 0 · push (b139e5e) · criterio
      PENDIENTE DE PRUEBA REAL: un mp4 de 3-5 min del operador → reel corto con captions.

## Transversales (no bloquean la Etapa 1)

- [ ] T1 `MEDIA_BUDGET_USD` → $50 (pendiente OK del operador; recomendado antes de la prueba 2.6).
- [ ] T2 Firma de datos: persistir `status='signed'` + llenar `distinct_because` (decisión aparte).
- [ ] T3 Tendencias (cron semanal) — después de Etapa 3 (usa `concept_custom` + el catálogo vivo).
- [ ] T4 Bake-off proveedores (fal-Kling vs kie-Veo-Fast vs apimart) — después de la prueba 2.6.
- [ ] T5 spec_Momentos — arranca junto a Etapa 3 (decisiones propias en su spec).

## Orden y dependencias

```
[decisión UI + dale] → Etapa 1 → Etapa 2 → PRUEBA REAL 2.6 → Etapa 3 → Etapa 4
                                              ↘ T4 bake-off        ↘ T3/T5
```
Regla de entrega: cada checkbox = commit propio con verify EXIT 0 y push inmediato (Vercel deploya).
Nada se marca DONE sin su criterio cumplido. Los costos reales van al ledger y se comparan con §6 del spec.
