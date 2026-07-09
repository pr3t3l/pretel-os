# Reconciliación documental C17 — work-order

> **Por qué existe:** C17 (firmado 2026-07-06) invirtió el modelo de contenido y **reconstruimos toda
> la superficie de producción/distribución** (Estudio→Ángulos, Media nueva, Calendario→Agenda, el
> derivado/28/plan-finito muertos). La doctrina se aplicó limpio solo en 2 sitios; **el resto de la
> doc sigue describiendo el mundo viejo**, y la re-arquitectura **nunca se documentó como spec** (solo
> en build_plans). Este doc es el checklist maestro de la reconciliación. Fuente: 2 auditorías
> exhaustivas (2026-07-08). **No se construye nada nuevo hasta cerrar P0+los 2 specs nuevos.**

## La verdad de referencia (C17)
El **ÁNGULO** (gancho 2.5, rico y sagrado) es la unidad · **PIEZA = ángulo × canal** · el plan es
**generativo/infinito** (las «28» = solo el sorteo inicial) · el **PILAR** es la raíz diagnóstica del
loop. Superficies: **Ángulos** (`/angulos`, produce, media dentro) · **Media** (`/media`, biblioteca) ·
**Agenda** (`/agenda`, `scheduled_posts` reales + radar). MUERTO: derivado/atomización/2.4/
«multiplicación», `AtomizationMap`, `rotateHook`, `buildPublicationPlan`, `/estudio`-productor,
`/calendar` computado.

---

## A. LOS 2 SPECS QUE FALTAN (el hueco de raíz — esto es lo gordo)

- [ ] **`spec_Superficies_Produccion.md`** (NUEVO) — Ángulos + Media + Agenda + tabla `scheduled_posts`.
      La re-arquitectura C17 solo vive en build_plans; ningún `spec_` la captura, por eso TODOS los
      specs apuntan al trío muerto «Estudio/Calendario/Biblioteca». **Cosecha** la doctrina buena de
      `spec_Estudio_Produccion_Publicacion` (§0 honestidad, §3.2–3.6 calidad/imagen/video, §4 wrapper,
      §5 biblioteca, §9 pricing). Es la autoridad nueva a la que apuntan los demás.
- [ ] **`spec_Campanas.md`** (NUEVO — recordatorio del operador «no lo podemos olvidar»). La capa
      evento→ventana→piezas con coherencia (R1 `docs/research/campanas-marketing-real.md`), re-expresada
      sobre C17: `scheduled_posts.campaign_id`, la cascada de override de personaje/set por campaña
      (Identidad §2.2), la oferta disparada por radar. Diseñada, sin spec, sin construir.

## B. P0 — dead model presentado como VIVO (riesgo alto, frenar ya)
- [x] `spec_Estudio_Produccion_Publicacion.md` — banner SUPERSEDED (2026-07-08).
- [x] `specs/build_plan_estudio_produccion.md` — banner SUPERSEDED (2026-07-08).
- [x] `docs/app/pipeline-de-ideas.md` — banner SUPERSEDED (2026-07-08); reescribir al modelo ángulo/generativo.
- [ ] `spec_Phase_Identidad.md §1.5` — reescribir al modelo generativo (quitar `buildPublicationPlan`,
      las 28, `rotateHook`, «pieza de 2.4»; conservar slot-vacío + develop bajo demanda + ○◐●✓).
      Renombrar Estudio/Calendario → Ángulos/Media/Agenda. **Bloquea la firma de Identidad.**
- [ ] `spec_Phase_2_Contenido.md` — la mitad no hecha de C17: §8 «Hook Library → el ÁNGULO es la
      unidad» + banner; subir header (dice v1.3/2026-06-27); §0 output («derivatives» como asset muere).
- [ ] `docs/app/ensamblador-de-prompts.md` — arreglar el núcleo del compilador (sigue vivo el derivado):
      Capa 0 obligatorios (quitar 2.4, línea 28) · Capa 1 (`Target={pillar,hook_id,channel}`, sin
      `rotateHook`, línea 30) · Capa 2 (`kind` del canal, línea 32) · el fixture §3 (124–130, 282) ·
      §4 fixes #2/#9 · Anexo A filas 6–10 · Anexo B (420, 452) · Anexo C: borrar §2.4, añadir
      `anchor`+`ratio_policy_plain` a §2.3. **Preservar** las secciones C17.1 (molde) ya correctas.
- [ ] `specs/build_plan_inteligencia_temporal_calendario.md` — quitar «2.4 multiplicación»; nota: la
      superficie calendario (M4) la reemplaza **Agenda/`scheduled_posts`** (conservar el motor temporal).
- [ ] `spec_Inteligencia_Temporal.md` — remapear §8/§9 (Estudio §6 calendario, Estudio §3.1 pieza,
      «biblioteca») → Agenda/Media/ángulo; el plan es generativo. (El motor radar/temporalidad sobrevive.)

## C. P1 — referencias muertas de carga / contradicciones
- [ ] `docs/research/campanas-marketing-real.md` — «plan finito / nada de contenido infinito» (302–303
      contradice C17), 28 piezas 2.4, «derivados de 2.4» (250, 267), `rotateHook` (306); reconciliar el
      modelo de campaña con `scheduled_posts`. (Alimenta `spec_Campanas`.)
- [ ] `specs/build_plan_produccion_v3_motor_coherencia.md` — «Gancho por derivado (rotación)» (124);
      «Estudio v2 grid» (60) → Ángulos/Media.
- [ ] `specs/build_plan_experiencia_canonica.md` — R4 «2.4 atomización» (131), pilar «multiplicador» (110)
      → 2.3 anchor+ratio / 2.5 ángulos.
- [ ] `specs/lookup_posting_cadence_2026.md` — «atomización (2.4) produce cada derivado» (50, 53) → ángulo×canal.
- [ ] `docs/app/README.md` — la entrada de índice de `pipeline-de-ideas` (11) describe el modelo muerto.

## D. P2 — snapshots, cross-refs, menor
- [ ] `docs/app/design-audit-2026-07.md` — cubrir `/angulos`, `/media`, `/agenda`; marcar `/estudio` y
      `/calendar` como fallbacks pre-swap.
- [ ] `specs/build_plan_modelo_contenido.md` — nota: P3/P4 (`buildPublicationPlan` generativo + calendario
      auto) lo supera el modelo `scheduled_posts`/Agenda de `build_plan_media_calendario.md`.
- [ ] `docs/research/doctrina-por-canal.md` — re-apuntar `CHANNEL_MAX_PER_DAY`/`plan.ts` (5, 155, 217)
      al modelo de cadencia/`scheduled_posts`.
- [ ] `README.md` (raíz) — añadir `scheduled_posts` a la lista de tablas.
- [ ] `docs/research/doctrina-video-2026.md` — verificar (no reescribir) que las expectativas por tipo
      leen contra el **ángulo**; `Overall_WF.md` residuos históricos (no requiere acción).
- [ ] Cosméticos varios: `spec_AI_Gateway_Wrapper`, `spec_Production_Support_and_Pricing`,
      `spec_Phase_3_Distribucion`, `spec_Admin_Cost_Intelligence`, `spec_Phase_0_Setup_Agent`
      (cross-refs «Estudio/Calendario» → superficies nuevas).

## D-bis. FASE 2 — el estado REAL capa por capa (auditoría de CÓDIGO, la que faltaba)

La auditoría por-términos no vio esto: **C17 es una migración A MEDIAS**. `content-plan.ts` + `canon.ts`
(el wizard) muestran additive+migrate hechos, **contract NO**. El mundo viejo sigue enchufado:

| Capa (2.x) | Estado real en el código | El doc debe decir |
|---|---|---|
| 2.0 voz · 2.1 reparto · 2.2 matriz | sin cambio de modelo | (los canales se expanden a formatos en `/angulos` vía `channelFormatOptions`, downstream) |
| **2.3 pilares** | ✅ ganó `anchor` + `ratio_policy_plain` (migró de 2.4) | el pilar LLEVA su ancla + la política de ratio |
| **2.4 atomización** | ❌ **SIGUE VIVA Y COMPLETA en el wizard** (`P2_STEP_IDS`, `P2_GUION["2.4"]`, `composeAtomMsg`, `AtomizationMap`, `atomGateReady` «1 ancla+5 derivados») — solo la consume `/estudio` muerto | MUERTA; el operador NO debería firmar derivados |
| **ratio** | ❌ pedido DOS veces (2.3 C17 + 2.4 viejo) — duplicado | vive solo en 2.3 |
| **2.5 ganchos** | 🟡 el *shape* reescrito a «ángulo completo» (40, 10/pilar), **pero** educación + `hooksGateReady`(≥10) + `composeHooksMsg` siguen «banco de aperturas» | el gancho ES el ángulo (la unidad), no una apertura |
| **mensajería de fase** | ❌ apertura «6 paradas… de pilares a piezas», `msgVictoriaPaso`/`msgCierreFase` narran la atomización | 5 paradas; sin «de pilares a piezas» |

**El CONTRACT pendiente (código — es el P5 de C17, entrelazado con el swap):**
- [ ] Quitar 2.4 del wizard: `P2_STEP_IDS`, `P2_GUION`, `P2_ARTIFACT`, `buildP2System`, `parseP2Proposal`, `composeAtomMsg`, la mensajería (apertura/victoria/cierre). **Bloqueado por el swap** (`/estudio` lee 2.4).
- [ ] Dedup ratio (dejar en 2.3, quitar de 2.4). **NO bloqueado por el swap** — se puede ya.
- [ ] Terminar el reframe de 2.5: educación + `hooksGateReady` + `composeHooksMsg` → «el ángulo es la unidad». **NO bloqueado.**
- [ ] Borrar `Atomization`/`AtomizationMap`/`atomGateReady` de `content-plan.ts` (contract). **Bloqueado por el swap.**

**Consecuencia para los docs:** `spec_Phase_2_Contenido` y `Overall_WF.md` no necesitan «arreglar §8» — necesitan **describir el modelo objetivo por capa** (2.3 con ancla+ratio, 2.4 muerta, 2.5 = ángulo) y **marcar honestamente que el contract está pendiente con el swap**. Es más profundo que lo que la auditoría por-términos reportó.

## E. Cierre
- [ ] Fila en `_audit_change_ledger.md` que registre la reconciliación (C18: doc-debt C17 saldada).
- [ ] Ledger C17 row: marcar sus landing-targets como hechos.

---

## Orden de ejecución
1. **Los 2 specs nuevos (A)** — son la autoridad; sin ellos, «arreglar cross-refs» apunta al vacío.
2. **P0 (B)** — desactivar el modelo muerto presentado como vivo (Identidad §1.5 desbloquea su firma).
3. **P1 (C)** — incluye alimentar `spec_Campanas` desde la research.
4. **P2 (D)** — barrido cosmético.
5. **Cierre (E)** — ledger.

Deploy: los docs viven en pretel-os (main); commit por bloque.
