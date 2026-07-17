# build_plan_craft_reels — plan de construcción del spec_Craft_Reels

> **Trinity:** spec = `spec_Craft_Reels.md` (firmado 2026-07-15) · plan = ESTE doc · tasks = los checkboxes de cada fase.
> **Fuentes operativas:** el spec (doctrina completa embebida) · `docs/research/2026-07-15_craft_reels_etapas_y_perfiles.md` (evidencia) · mapa del sistema 2026-07-15 (trace de código).
> **Repo de código:** `sandia-marketing` (todo commit se pushea YA — Vercel auto-deploya).
> **Regla de fases:** cada fase termina en verify+build+push y una PRUEBA REAL del operador antes de arrancar la siguiente.

---

## Mapeo investigación UX → decisiones de diseño (aplica a todas las fases)

| Hallazgo (fuente) | Decisión en Papandi |
|---|---|
| Galería visual > opciones abstractas (Arcads: eliges actor CON ambiente incluido) | Chips con FOTO/miniatura para quién y momento; cero dropdowns abstractos en ruta default |
| Progressive disclosure: −30-50% tiempo a primera acción sin perder descubribilidad | "▸ Ajustes finos" colapsado (`details`); default "Papandi decide" en todo |
| Anti-patrón #1 HeyGen: costo/créditos opacos, jobs fallidos que cobran | Costo visible ANTES de cada gasto (ya es doctrina D-V4); fallos loguean $0 (ya) |
| Anti-patrón #2 HeyGen: renders eternos sin expectativa | Cada botón de gasto muestra ~tiempo esperado ("~40s", "~2-4 min/clip") |
| Compuertas human-in-the-loop: decisión en 2 segundos, approve/edit/reject por ítem | Compuerta ② con línea de venta + sello del auditor arriba; editar/regenerar POR BEAT |
| Regeneración parcial > regenerar todo | "↻ este beat" / "↻ este momento" / "▶ solo este clip" (ya existe el patrón en clips) |
| Defaults que recuerdan | Elecciones del brief persisten por proyecto (última selección = próximo default) |
| Plataforma con consecuencias visibles | Chip IG/TikTok/YT con su doctrina en 1 línea (ASR keywords / sends / loop) |

---

## F1 — LA CHISPA (sin UX nueva; el siguiente reel ya sale distinto)

**Objetivo:** matar "la persona parece muerta" con 4 cambios sobre los prompts actuales. Cero pantallas nuevas.

### F1.1 Capa de actuación (determinística, sin LLM extra)
- [ ] `lib/estudio/performance.ts` (NUEVO, puro): bloques VERBATIM del spec §2.C — `PHYSICS`, `BEHAVIOUR`, `TONE` (por tipo: ugc/presentadora), `NEGATIVE` (≤10 términos).
- [ ] `Scene` gana 4 campos opcionales `physics/behaviour/tone/negative` (`coerceScenes` tolerante; vacío ⇒ default).
- [ ] `composeMotionPrompt(scene, opts:{anchor?, continuity?, tipoReel?})` recompuesto al orden §3.1: `[anchor + FICHA] + accion + Physics + Behaviour + Tone + camara + Framing + Audio + guion + Negative + safe zones`.
- [ ] Callers actualizados: `video-generate/route.ts`, `director/page.tsx` (glass-box "Ver el prompt compuesto").

### F1.2 Keyframes mid-action
- [ ] `keyframes/route.ts` prefijo KEEP: "Change ONLY the pose…" → "Show the SAME person in a NEW moment of the action — pose caught MID-ACTION (mid-gesture, reaching, turning), never a symmetric at-rest portrait:".
- [ ] `lib/estudio/prompts.ts` reglas `primer_frame`/`ultimo_frame`: pose en mitad de la acción; clip 1 primer frame = el gancho visual (acción iniciada + expresión fuerte); brazo selfie visible en conceptos selfie.
- [ ] `composeKeyframePrompt` acepta la Ficha (inyección tras styleLock).

### F1.3 Ficha de Continuidad
- [ ] `lib/estudio/continuity.ts` (NUEVO, puro): `buildContinuityPrompt(scenes, voz, identidad)` + `coerceContinuity` — bloque 80-120 palabras: PERSONA (outfit exacto) / LUGAR (props + producto) / LUZ / VOZ / ESTILO.
- [ ] `produce/route.ts` post-parseDevelop: llamada `complete()` barata (`estudio_continuity@v1`) → `design_spec.continuity` (JSONB, cero migración).
- [ ] Inyección VERBATIM (mismos bytes) en motion + keyframe prompts (criterio #8 del spec: diff byte-idéntico entre clips).

### F1.4 El Auditor (Actor-Critic-Boss)
- [ ] `lib/estudio/auditor.ts` (NUEVO, puro): `buildAuditorPrompt` (evalúa contra criterios, NO genera; modelo distinto) + `coerceAuditIssues` schema `{issues:[{category,severity,clip,evidence,fix}]}` con las 9 categorías del spec §2.D.
- [ ] `produce/route.ts`: auditor → boss aplica fixes critical/major (1 ronda en F1) → `design_spec.audit = {issues, fixed, summary}`.
- [ ] Sello 1 línea en Director ②: "✓ Auditado: N correcciones…" desde `audit.summary`.

### F1.5 Tests + cierre
- [ ] Tests puros: orden de bloques en compose · Ficha byte-idéntica en N escenas · `coerceAuditIssues` · keyframe mid-action · actualizar tests existentes de scenes.
- [ ] `npm run verify` + `npm run build` + push. **Prueba real del operador** (develop + 2 clips vs un reel viejo).

---

## F2 — EL BRIEF + EL CASTING (la UX nueva)

### F2.1 Identidad → Casting (`identidad/page.tsx` + `cast-library.tsx` + `cast.ts`)
- [ ] Separador visual y de vocabulario: sección "Audiencias" (personas 0.3) vs "Cast" (quién sale en cámara).
- [ ] **Avatar en 2 pasos**: (A) retrato ancla → editar prompt glass-box → regenerar → **aprobar la CARA** (gate); (B) botón «Generar su mundo → 6 momentos (~$0.90)» habilitado SOLO con cara aprobada.
- [ ] **Catálogo de momentos** (~10: cama+teléfono, cocina, carro parqueado, espejo baño, caminando, escritorio, gimnasio, taller, tienda, custom): el usuario elige 6; Papandi pre-marca según el mundo del comprador (del brief 0.x). Cada momento: prompt editable antes de gastar, regenerar individual, o subir foto real.
- [ ] Generación de momentos: cadena de edición desde el ancla (misma cara) + 6C + doctrina mid-action + dial de realismo. Persistencia: `CastCharacter.momentos[] {id, key, image_url, prompt, aprobado}` en el artifact cast existente (JSONB).
- [ ] **Sets → Lugares** (rename UI + docs; el modelo de datos no cambia): estantes "Personas" y "Lugares"; nota de uso (escenario de momentos / b-roll / sin-persona).
- [ ] **Dial Pulida↔Real** por avatar (`realismo: "real"|"pulida"`, default real) — se inyecta en generación de momentos, keyframes y motion.
- [ ] Prompt del retrato ancla: se mantiene nítido para identidad facial (NO cambia a lo-fi — el ancla es técnica; el realismo vive en momentos/keyframes).

### F2.2 La pantalla ① EL BRIEF (`director/page.tsx` paso 1, reescrito)
- [ ] **¿Quién?** — cards con FOTO de personajes aprobados + "🎲 Papandi inventa una persona"; preselección: cast_override de campaña > default de marca. Estado vacío: CTA "Aprueba un personaje en Identidad →".
- [ ] **¿En qué momento?** — cards con MINIATURA de los momentos del avatar elegido + "✨ Papandi elige" (default). Sin momentos (avatar viejo): chips de texto de los 12 CONCEPTS + banner "genera su mundo en Identidad".
- [ ] **¿Plataforma?** — chips IG Reel / TikTok / YT Short con su consecuencia en 1 línea (spec §1.4); preselección: el canal de Ángulos (URL).
- [ ] **Tu toque** — textarea opcional.
- [ ] **▸ Ajustes finos** (`details` colapsado): G1 (5 selects), tipo de reel (presentadora/ugc/animado+estilo), estilo de apertura manual, referencia 6C, dial realismo por-pieza. Default TODO "Papandi decide".
- [ ] **Fix seam G1**: persistencia unificada — las elecciones del brief se guardan en `design_spec` al desarrollar Y como default de proyecto (última elección); muere la divergencia `estudio_choices` vs estado local.
- [ ] Botón único: «Papandi produce el guion y el plan → ~$0.02 · ~40s».
- [ ] El momento elegido viaja al pipeline (ambiente + arranque); "Papandi elige" deja la decisión al Director (F3) o al develop actual (mientras F3 no exista).

### F2.3 Ángulos adelgaza (`angulos/page.tsx`)
- [ ] Quitar del card de VIDEO: 🎬 Apertura visual y 💬 Estilo de apertura (quedan intactos para no-video).
- [ ] Retrocompat: `estudio_choices` viejos se leen como defaults de Ajustes finos.
- [ ] El botón de video va directo al Estudio con el contexto por URL (como hoy).

---

## F3 — EL PIPELINE DE ROLES COMPLETO + COMPUERTA ② NUEVA

### F3.1 Partir la llamada única (`produce/route.ts` + nuevos servicios)
- [ ] `lib/estudio/roles/estratega.ts` — brief destilado (spec §2.A, schema estructurado, anti-relleno null).
- [ ] `lib/estudio/roles/guionista.ts` — beats + 9 patrones + gancho 3 capas (spec §2.B); CAG 3-5 guiones vivos (extraer de `AvatarHype Classes/` a un módulo de ejemplos).
- [ ] `lib/estudio/roles/director.ts` — PASO 0 (money shot, arco, contraste, cierre circular) + cajas por clip + capa de actuación + Ficha (spec §2.C). El Auditor de F1 se recablea al final de esta cadena (2 iteraciones).
- [ ] Ruta `produce` orquesta: estratega → guionista → director → auditor→boss → scenes (mismas `design_spec.scenes[]`). Telemetría por rol en `project_llm_calls` (promptVersion por rol).
- [ ] Doctrina de canal como restricción dura por rol (TikTok keywords habladas / IG compartible / YT loop).

### F3.2 Compuerta ② nueva (`director/page.tsx` paso 2)
- [ ] Header: **línea de venta** (`Vendes → Beneficio → CTA`) + **sello del auditor** (card colapsable con issues corregidos).
- [ ] Guion agrupado POR BEAT (hook/problema/mecanismo/prueba/CTA) con presupuesto de tiempo; cajas de escena bajo su beat.
- [ ] **Gancho de 3 capas** como bloque editable (visual / hablada + 2 variantes / texto overlay).
- [ ] **↻ Regenerar este beat** (re-corre guionista+director SOLO para ese beat, con el resto como contexto fijo).
- [ ] Plan visual visible: money shot ⭐ en su clip, arco en 1 línea, chip del momento por clip.

---

## F4 — PULIDO DE EDICIÓN Y PLATAFORMA

- [ ] **Zoom progresivo** 1.5-2%/s en talking heads (filtro scale ramp en el burn; toggle default ON en el editor).
- [ ] **Warning de cadencia** en la línea de tiempo: >3s sin cambio visual → marca ámbar (puro cliente).
- [ ] **Loop check**: si el Director marcó cierre circular, badge de empate último↔primer frame.
- [ ] Doctrina de plataforma visible end-to-end (chips del brief → beats del guionista → plan del director).
- [ ] Dial de realismo aplicado también al burn (grano sutil opcional).

## F5 — EL ANALISTA (spec §7 — se especifica fino al llegar)

- [ ] Registro manual de hook rate / hold rate por pieza (insights del operador) sobre `piece_events`.
- [ ] Diagnóstico posicional (mal hook → 3 capas del gancho; mal hold → cuerpo) como recomendación en la pieza.
- [ ] La librería de ganchos del proyecto aprende de resultados (qué capa funcionó) — alimenta al Guionista.
- [ ] (Futuro: conexión de métricas reales IG/TikTok.)

---

## Riesgos y decisiones abiertas

- **Latencia del pipeline F3** (4 llamadas ≈ 40-90s): mitigar con narración de progreso por rol ("El guionista está escribiendo…") — el patrón thinking-narration ya existe en el wizard.
- **Costo LLM por reel** ≤ $0.10 (criterio #4): elegir tiers por rol (estratega/auditor baratos; guionista/director premium).
- **Momentos de avatares viejos**: fallback a CONCEPTS hasta que el usuario genere el mundo (sin bloquear).
- **El catálogo de 16 VISUAL_HOOKS** pasa a vocabulario interno del Director (no muere: es su léxico de aperturas).
- **kie-Veo3** (tarea pendiente aparte) no bloquea nada de esto.
