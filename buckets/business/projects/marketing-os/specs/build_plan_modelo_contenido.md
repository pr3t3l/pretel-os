# Build Plan — Modelo de contenido (PILAR → ÁNGULO → PIEZA)

**Estado:** v1 — para EJECUTAR tras la firma de `spec_Modelo_Contenido.md` (ratifica C17 en `_audit_change_ledger.md`). **NO construir hasta firma.**
**Decide:** el orden de ejecución, tests por fase, la migración de datos, y **cómo el cambio se relaciona con la producción de video** (input-side vs output-side).
**Fuentes:** `spec_Modelo_Contenido.md` (autoridad) · `_audit_change_ledger.md` C17 · mapa de la cadena de producción (explorador, esta sesión, con archivo:línea) · `spec_Estudio_Produccion_Publicacion.md` · `docs/research/doctrina-video-2026.md`.

---

## 0. La decisión de diseño que este plan resuelve — dónde vive "la idea" (Seam 2)

Al morir el derivado desaparece su `note` (la idea concreta por pieza, hoy en el prompt de develop como *"IDEA DE LA PIEZA — desarrolla ESTA idea, no inventes otra"*, `prompts.ts:250`). La pregunta del operador: **¿dónde vive la idea en el modelo nuevo?**

**Decisión: la idea se ABSORBE en el gancho.** El gancho deja de ser "solo la primera frase" y pasa a ser el ÁNGULO completo:
```
Hook = { text (la apertura, 1-2 frases) · angle (el take específico: qué explora esta pieza, 1 línea) · template · pillar }
```
Por qué: es coherente con la doctrina del Cerebro de Ganchos (*el gancho ES la sustancia, sagrado*) y **preserva la especificidad anti-genérica que daba el `note`** — solo la reubica en su dueño natural. El `note` no se pierde: se muda adentro del gancho. *(Opción rechazada: gancho pelado + que el modelo improvise el cuerpo → riesgo genérico, contra el lever #1 "brief genérico = output genérico".)*

Con eso: **gancho(text+angle) + pilar(+anchor) + canal = brief completo**, sin `note` ni derivado. El `angle` viaja con el gancho a cualquier canal (sigue siendo agnóstico); el canal solo cambia el formato.

*Nota:* el `angle` puede además cargar el `intent` (value/cta/hybrid) → alimenta el ratio dar:pedir con más precisión que derivarlo solo del modo del pilar.

---

## 1. El árbol de prompts (antes → después)

**Antes (3 llamadas generativas):** 2.3 pilares · 2.4 atomización (ancla + derivados + ratio) · 2.5 ganchos.
**Después (2 llamadas):** 2.3 pilares (+ ancla + ratio) · ~~2.4~~ (borrada) · 2.5 ganchos (+ angle).

```json
// 2.3 enriquecido — absorbe el ancla y el ratio del difunto 2.4
{ "ratio_policy_plain":"3:1 — de cada 4, 3 dan y 1 pide (5:1 si viene quemado)",
  "pillars":[{ "id":"PILLAR_A","name":"...","force_attacked":"ongoing_pains","mode":"resolve",
    "message":"...","anchor":{"title_working":"..."},"channels":["blog_seo","social"] }, ...×4 ] }

// 2.5 enriquecido — el gancho gana su angle (absorbe el note)
{ "hooks":[{ "hook_id":"H_A_01","template":"contrarian","text":"la apertura, 1-2 frases",
    "angle":"el take específico que abre esta pieza (1 línea) — la idea, antes en note","pillar":"PILLAR_A" }, ...10/pilar ] }
```

---

## 2. Fases de ejecución (ordenadas, con tests)

### P1 — Schema + prompts (la raíz)
- `content-plan.ts`: `Pillar` gana `anchor`; `Hook` gana `angle`; `PillarSet` gana `ratio_policy_plain`; **borrar** `Atomization`/`AtomizationMap`/`atomGateReady` (se va el candado "1 ancla + ≥5 derivados"). `pillarsGateReady` (4 fuerzas) se queda.
- `canon.ts`: quitar `"2.4"` de `P2Step`/`P2_STEP_IDS`/`P2_GUION`/`P2_ARTIFACT`; borrar `shapes["2.4"]`, su caso en `parseP2Proposal`, `composeAtomMsg`; **enriquecer** `shapes["2.3"]` (anchor + ratio) y `shapes["2.5"]` (angle).
- `config.ts`: quitar la fila del paso 2.4.
- **Tests:** `phase2-canon.test.ts` (shapes nuevas, sin 2.4); gate = 4 fuerzas.
- **Verif:** `npm run verify`; el wizard corre 2.0→2.1→2.2→2.3→2.5.

### P2 — El contrato de develop (Seams 1-7 del explorador)
- `brief.ts`: `Target` pasa de `{pillar_id, derivative_index}` → **`{pillar_id, hook_id, channel}`**; `buildBrief` lee el gancho por id (borrar `rotateHook`), `kind` desde `channel`, `idea` desde `hook.angle`, `anchor` desde `pillar.anchor`.
- `produce/route.ts`: body `{projectId, avatarKey, pillarId, hookId, channel, visualHook?, hookTemplateId?, publishDate?}`; cargar el gancho por id; **validar** `hookId ∈ pilar` y `channel` habilitado en la matriz 2.2 (Seam 7); `type = channelToContentType(channel)`.
- `prompts.ts`: *"IDEA DE LA PIEZA"* ahora sale de `hook.angle`; *"PIEZA ANCLA"* de `pillar.anchor`.
- **Tests:** `brief.test.ts` (nuevo Target, sin rotateHook); integridad en produce.
- **Verif:** desarrollar UNA pieza (gancho×canal) end-to-end en prod, sin derivado; el cuerpo abre con SU gancho (coherencia).

### P3 — El sorteo del set inicial (`plan.ts`, la reescritura grande)
- `buildPublicationPlan`: iterar **pilares × canales habilitados**; elegir ángulos (mayormente distintos, para señal) pesados por **rol de canal** (carrusel=educar, Reel=alcance, imagen=relleno) + **journey** (2.2) + **ratio** (`pieceIntent`/`ratioStatus`, ya construido en Etapa E); respetar cadencias/ventanas/topes; emitir **slots ○ VACÍOS** (ángulo×canal×fecha, sin contenido).
- **Tests:** `plan.test.ts` (slots ○; ratio respetado; mezcla por rol de canal; no se agota — es generativo).
- **Verif:** el calendario se llena con slots ○ desde el pozo, no desde 28 derivados.

### P4 — UI (biblioteca de ángulos + calendario)
- `estudio/page.tsx`: "ideas (derivados) por pilar" → **"biblioteca de ángulos por pilar, desarrollable a cualquier canal"**; el botón *Desarrollar* abre selector de canal (de los habilitados en 2.2).
- `calendar/page.tsx`: estados de slot ○◐●✓; desarrollar **desde el slot** (ancla la fecha → integridad temporal); slots vencidos sin desarrollar se **reprograman con aviso**.
- Botón **«Desarrollar mi semana»** (lote ~5-7) + **una-por-una** (default en debug — nunca 28 a ciegas).
- **Verif visual** en papandi.com por el operador.

### P5 — Migración de datos
- Proyectos con `atomization_map` firmado → copiar `long_form.title_working` a `pillars[].anchor`; los derivados se **descartan** (su sustancia ya vive en los ganchos).
- Ganchos existentes sin `angle` → best-effort: derivar un `angle` de su `text` (una llamada barata por avatar) o dejar `null` y que el develop use el pilar. **Sin pérdida de sustancia.**

---

## 3. La relación con la producción de video (la pregunta del operador)

**El cambio de modelo toca el INPUT de develop; la producción de video cuelga del OUTPUT de develop. Son ortogonales y se encuentran en el paso develop.**

```
[content model]  hook×canal+angle ──▶ develop ──▶ design_spec + character + clips ──▶ [video/Etapa G]
   (INPUT-side, ESTE plan)              ▲                                              (OUTPUT-side)
                                    se encuentran aquí
```

- **INPUT-side (este build plan):** re-cablear de dónde develop saca su brief (gancho×canal, no derivado).
- **OUTPUT-side (Etapa G — mayormente PLANEADO):** develop emite `design_spec` (`video_prompts` 1-por-clip, `hook_text_overlay`, `camera.movement`) → `video-generate` (Kling/Seedance/Veo; multi-shot packing ≤512 chars o singles; personaje D-V2 vía image-to-video con `start_image_url`+`elements.frontal_image_url`) → `video-status` (cosecha variantes acumulativas).

**Estado real de la personalización de video (del mapa del explorador):**

| Pieza | Estado | Dónde vive |
|---|---|---|
| Apertura visual (16 ganchos) | ✅ **construido** | `visual-hooks.ts` → `visualHook` en el develop |
| Movimiento de cámara | ⚠️ **parcial** (en el prompt, sin botón UI) | `design_spec.camera.movement` |
| CTA de cierre | ⚠️ **parcial** | guion + overlay |
| Audio nativo + voz del personaje | ✅ **construido** | Kling desde narración + `kit.voice.descriptor` |
| Multi-shot packing + personaje persistente | ✅ **construido** | `video-routing.ts` + image-to-video |
| Captions karaoke (WhisperX/FFmpeg/Creatomate) | ❌ **planeado** | post-producción |
| Safe zones + overlay de texto en VIDEO | ❌ **planeado** (`overlay-composer` existe solo para IMAGEN) | editor |
| Botones ritmo / loop / duración | ❌ **planeado** | rodaje |
| Frame chaining (último frame → start del siguiente, FLUX Kontext) | ❌ **planeado** | post-producción |
| Concat automático de clips (FFmpeg) | ❌ **planeado** (hoy el operador monta en CapCut) | post-producción |

**Lo que el operador debe saber:** el cambio de modelo **NO rompe la generación de video** — el video consume lo que develop PRODUCE (`design_spec` + personaje + clips), y eso sigue existiendo. Solo cambia de dónde develop saca su INPUT. La única condición nueva: el **canal** (ahora explícito) es lo que enciende el tipo video y sus opciones. Por eso **este plan es el prerrequisito limpio** para que la Etapa D (biblioteca de ángulos como superficie) y la Etapa G (los 8 botones de personalización + post-producción) se enchufen sin pelear con el derivado.

---

## 4. ¿Está alineado el módulo de contenido? — el mapa honesto

| Capa | Estado |
|---|---|
| **Modelo de generación** (2.3 pilares + 2.5 ganchos+angle) | Diseño LISTO; falta el build (P1) |
| **Contrato de develop** (input gancho×canal) | Hay que re-cablear (P2 — Seams 1-7) |
| **El sorteo / calendario** (set inicial generativo) | Hay que reescribir (P3) |
| **UI** (biblioteca de ángulos + slots) | Hay que construir (P4) — es la Etapa D vuelta grano del sistema |
| **Generación de video** (design_spec→Kling→variantes) | COMPATIBLE, no se rompe; cuelga del output |
| **Personalización de video** (8 botones + post-producción) | Etapa G — 1 construido, 2 parciales, 5+ planeados (output-side, separado) |

**Respuesta corta:** el módulo de contenido queda alineado *como diseño* con este plan; lo que falta DESARROLLAR es (a) este rework (P1-P5, input-side), (b) la Etapa D (biblioteca de ángulos = UI de P4), y (c) la Etapa G (personalización de video, output-side, un backlog grande y en su mayoría planeado). (a) es prerrequisito de (b) y (c).

---

## 5. Verificación global
- `npm run verify` verde por fase; deploy continuo (commit+push, Vercel auto).
- **End-to-end:** firmar 2.x → calendario con slots ○ (vacíos) → desarrollar un slot (gancho×canal) bajo demanda → pieza coherente (el cuerpo abre con SU gancho) → si es video: `design_spec` → Kling → variante cosechada.
- Métrica de éxito del modelo: abrir la misma combinación no duplica llamadas; el `hook_id` viaja a la pieza (atribución del loop de automejora, §6 de la spec).
