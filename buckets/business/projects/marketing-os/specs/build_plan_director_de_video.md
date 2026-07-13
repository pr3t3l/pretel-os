# build_plan_director_de_video — Plan de construcción (las 4 etapas)

> **Estado: 🟡 EN CONSTRUCCIÓN — Etapas 1+2 SHIPPEADAS (2026-07-13, pantalla completa). Etapa 1 probada por el operador (2 rondas, guion aprobado). Sigue: PRUEBA REAL 2.6 (~$6).** Spec madre: `spec_Director_de_Video.md` (pre-check
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

- [ ] 3.1 Música: script de subida (562 pistas → bucket global `music-library`, TUS) + índice
      `music_tracks` (filename, duración, mood del nombre) + README de licencia (respuesta del correo del
      operador) + selector con preview en ⑤ + compose con track de audio (volumen ~20-25%, fade-out;
      verificar param `volume` del schema — fallback pre-procesar mp3).
- [ ] 3.2 Elementos nombrados: UI asignar imagen→palabra (del transcript ya alineado) + compose overlays
      `{timestamp, duration, x, y}`. (Insumo pendiente: los 2 transcripts de YouTube del operador.)
- [ ] 3.3 Feedback capa 1+2: tabla `piece_events` (migración, LA ÚNICA del plan — con OK del operador) +
      eventos (diff de cajas al aprobar, keyframe regen, variante elegida, funnel, música) + 👍/👎 al
      terminar el reel.
- [ ] 3.4 Referencia visual: `api/estudio/reference-decompose` (visión → 6C) + campo en ① + pre-llenado.
- [ ] 3.4b Personas UGC ↔ Identidad (pedido del operador 2026-07-13): «Guardar esta persona en
      Identidad» desde la galería (promueve una UGC generada al cast, con su ancla) + selector inverso
      («usar una persona del cast») en el tipo UGC — para reviews que repiten actriz a propósito.
- [ ] 3.5 `verify` · push · criterio: un reel suena con música bajo la voz + un overlay aparece en el
      segundo exacto de su palabra.

## Etapa 4 — «Traigo mi video» (modo D)

- [ ] 4.1 Subida directa navegador→storage (TUS resumable; límites ≤10 min/≤1 GB/3 archivos) + registro.
- [ ] 4.2 `api/estudio/edit-plan` (NUEVO): whisper (ya existe) → plan de cortes glass-box (keeps con razón,
      cortes de muletillas/silencios por gaps de palabras, gancho, CTA) → cajas editables (misma UI de ②).
- [ ] 4.3 Compose con trims (offsets por segmento) + concat + captions de marca + música → reel(s).
- [ ] 4.4 `verify` · push · criterio: un mp4 de 3-5 min del operador sale como reel corto con captions.

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
