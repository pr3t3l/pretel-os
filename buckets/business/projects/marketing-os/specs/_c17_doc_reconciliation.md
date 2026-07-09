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

- [x] **`spec_Superficies_Produccion.md`** ✅ (2026-07-08) — Ángulos + Media + Agenda + `scheduled_posts`,
      con la doctrina buena cosechada del Estudio superseded. Es la autoridad nueva a la que apuntan los demás.
- [x] **`spec_Campanas.md`** ✅ (2026-07-09) — la capa evento→ventana→arco re-expresada sobre C17: pieza de
      campaña = ángulo × canal (mismo `/api/estudio/produce`, sin `CampaignPiece`/`kind`), `scheduled_posts.campaign_id`
      (aditiva), cascada de cast vía `CastOverride`/`resolveCast` (Identidad §2.2, cero código nuevo), oferta que
      legitima la urgencia C12, arco propuesto (chips fantasma → reales), evergreen generativo intacto. Conserva las
      decisiones de R1 §2; reemplaza su §3 (modelo muerto).

## B. P0 — dead model presentado como VIVO (riesgo alto, frenar ya)
- [x] `spec_Estudio_Produccion_Publicacion.md` — banner SUPERSEDED (2026-07-08).
- [x] `specs/build_plan_estudio_produccion.md` — banner SUPERSEDED (2026-07-08).
- [x] `docs/app/pipeline-de-ideas.md` — banner SUPERSEDED (2026-07-08); reescribir al modelo ángulo/generativo.
- [x] `spec_Phase_Identidad.md §1.5` ✅ reescrito a C17 (generativo, sin buildPublicationPlan/28/rotateHook);
      §0/§1/§4/Fuentes renombrados Estudio/Calendario → Ángulos/Media/Agenda. Ya no bloquea la firma.
- [x] `spec_Phase_2_Contenido.md` ✅ header v2.0 (C17) + nota de doc + banner §8 (el ÁNGULO es la unidad) +
      §0 output («derivatives» como asset muere). (Las §§ de atomización quedan como historia; §7 ya tiene banner.)
- [x] `docs/app/ensamblador-de-prompts.md` ✅ (2026-07-09) — enfoque de integridad para un snapshot de 1052
      líneas: **banner de reconciliación C17** arriba (tabla de traducción muerto→vivo) + cirugía en los
      enunciados CORE (Capa 0 «3 obligatorios 2.0/2.3/2.5», Capa 1 `Target={pillar_id,hook_id,channel}` sin
      rotación, Capa 2 `kind` del canal, regla de oro sin «rotación», §2.1 clase B sin «derivado») + Anexo C
      (§2.4 ⚰️ MUERTO con banner, `anchor`+`ratio_policy_plain` añadidos a §2.3, §2.5 = «el gancho ES el
      ángulo») + nota de cabecera en fixture §3 y Anexo A (filas 6–10 históricas). Fix falso «4 obligatorios»
      en la nota de pipeline. **Preservadas** las secciones C17.1 (molde) ya correctas. Inventario histórico
      A/B conservado bajo el banner.
- [x] `specs/build_plan_inteligencia_temporal_calendario.md` ✅ (2026-07-09) — banner: M1-M3+M5 (motor
      temporal) sobreviven en producción; M4 (calendario CALCULADO vía `buildPublicationPlan`) jubilado por el
      swap → **Agenda/`scheduled_posts`**; radar (`/api/radar/upcoming`) lo consume la Agenda; «2.4
      multiplicación» del gate/DB anotada muerta; nota C17 en M4.
- [x] `spec_Inteligencia_Temporal.md` ✅ (2026-07-09) — banner (motor intacto) + remapeo de superficies:
      cabecera «Consumidores», §6.2 ofensiva, §8.1/§8.3 mapa de migración, §9 UI → **Agenda/Media/Ángulos**;
      pieza = ángulo×canal; plan generativo (sin «cola»); enganche de campaña → `spec_Campanas`. §§1-7/§10 (el
      motor) intactas.

## C. P1 — referencias muertas de carga / contradicciones
- [x] `docs/research/campanas-marketing-real.md` ✅ (2026-07-09) — banner en §3 que la marca SUPERSEDED por
      `spec_Campanas.md` (ahí se reconcilia `PlanSlot`/`buildCampaignSlots`/`rotateHook`/`kit_variant`/«plan
      finito»/derivados 2.4 → `scheduled_posts`/ángulo×canal/`CastOverride`/evergreen generativo). §1/§2
      (hallazgos + decisiones) siguen VÁLIDOS y citados por el spec — se conservan como registro de investigación.
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

**El CONTRACT (código — el P5 de C17) — ✅ HECHO (swap aprobado por el operador, 2026-07-08):**
- [x] SWAP: nav → Ángulos/Media/Agenda; `/estudio` + `/calendar` jubiladas; radar-redirect → /agenda (sandia `49057dd`, `8718ea2`).
- [x] Borrado `lib/calendar/plan.ts` (buildPublicationPlan/buildGenerativePlan finitos) (`614e111`).
- [x] `brief.ts`/`produce`/`suggest-hooks` a solo-C17 (fuera `rotateHook`, `derivative_index`, el path legacy) (`fa31872`).
- [x] Quitado el paso **2.4** del wizard (canon + step-proposal + phase2-thread + phase-2/page); ratio ya no se pide dos veces (`54dceff`).
- [x] Borrado `Atomization`/`AtomizationMap`/`atomGateReady` de `content-plan.ts` + reframe de la educación de 2.5 (`3cb27cb`).

**El código ya no tiene el modelo viejo.** Queda solo la reconciliación DOCUMENTAL (abajo).

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
