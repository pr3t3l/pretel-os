# Phase 5 — Ajustar / Optimizar (el loop)

**Project**: business/marketing-os
**Phase ID**: phase-5
**Status**: spec drafted v1.0
**Last updated**: 2026-06-06
**Implementation correction:** Targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase). Persist outputs in `project_phase_artifacts` (`phase = 'phase_5'`; el legacy `review` queda como alias deprecado — ver `Overall_WF.md`). Decisions en `project_decisions`, learnings/best-practices en `project_lessons`. **Phase 5 es la fase que cierra y reinicia el loop por avatar: NO edita la estrategia activa — emite Strategy #N+1** (`strategies` row nueva, `status='active'`) y marca la anterior `superseded` (`strategies.superseded_by`).

**Reference**: `Overall_WF.md` §"Strategy Lifecycle" (la fuente de verdad del loop). `spec_Phase_4_Medir.md` §5 (`phase_5_flags`). Consume las condiciones de re-trigger de Phases 0/1/2/3.

---

## 0. Contexto y propósito

Phase 5 lee los `phase_5_flags` y `results_summary` de Phase 4 y decide la **acción de optimización** para cada estrategia. Es el cierre del ciclo de aprendizaje: detecta fatiga, fallos económicos, o avatars perdedores, y dispara el re-trigger correcto **al nivel correcto** (Phase 0, 1, 2 o 3). El producto de Phase 5 no es una edición — es **una nueva versión de la estrategia** que preserva el histórico para aprender.

**Por qué versionar y no editar:** el diferenciador del sistema (orquestación paralela) depende de poder aprender de la historia de cada avatar. Si Phase 5 sobrescribiera la estrategia, se perdería la traza de qué funcionó y qué no. Emitir Strategy #N+1 (apuntando a #N vía `superseded_by`) mantiene el árbol Project → Avatar → Strategy #1, #2, #3… del diagrama de jerarquía.

**Output canónico**: `optimization_plan.json` (la decisión + el re-trigger) + (cuando aplica) una nueva `strategies` row + `project_lessons`/`project_decisions`/best-practices ancladas a la estrategia.

---

## 1. Estructura: 3 sub-pasos + 1 transversal

| Sub-paso | Output | Estimado V1 | V1 | V2 |
|---|---|---|---|---|
| 5.1 — Diagnóstico (leer flags) | `optimization_plan.diagnosis` | 30 min | Claude lee results_summary + flags | Auto |
| 5.1.b — Diagnóstico abierto (cuando nada encaja) | `optimization_plan.open_diagnosis` | 30–60 min | Claude razona causa raíz desde datos + operador valida | Auto + flag excepciones |
| 5.2 — Decisión de acción (registro de banderas) | `optimization_plan.action` | 30 min | Vía rápida flag→acción + operador aprueba | Auto + flag excepciones |
| 5.3 — Emisión de Strategy #N+1 (si aplica) | nueva `strategies` row + re-trigger | 15 min | Claude crea versión, marca anterior superseded | Auto |
| **Transversal** — Crystallize learnings | `project_lessons` + best-practices | continuo | Operador + Claude | Reflection-style auto |

---

## 2. Pre-condición — Gate de entrada G-Phase-5-PRE

1. ✅ `metrics_snapshot.json` existe con `metadata.operator_signoff: true`
2. ✅ `strategies.results_summary` poblado con `phase_5_flags` (puede ser lista vacía)
3. ✅ La `strategies` row objetivo está en `status='active'` (no se optimiza una estrategia ya superseded)

---

## 3. Sub-paso 5.1 — Diagnóstico

### Output: `optimization_plan.diagnosis`

```json
{
  "strategy_id": "strategy_uuid",
  "strategy_version": 1,
  "avatar_id": "avatar_1",
  "flags_read": ["ctr_falling_30pct_14d", "ltv_cac_below_3"],
  "economics_health": "red",
  "ctr_trend": "falling",
  "conversion_trend": "flat",
  "cross_avatar_rank": "2 of 3 active strategies",
  "root_cause_hypothesis": "1-2 oraciones — qué se rompió y por qué"
}
```

### Reglas duras
- Cada flag de `results_summary.phase_5_flags` debe ser direccionado en el diagnóstico (ninguno se ignora)
- `root_cause_hypothesis` obligatorio cuando hay ≥1 flag (no "optimizar genéricamente")

---

## 3b. Sub-paso 5.1.b — Diagnóstico abierto (cuando nada encaja)

### Propósito
Esta es la rama que hace que el sistema **piense** en vez de solo mirar un catálogo fijo. Se activa cuando Phase 4 emitió `unexplained_anomaly` (una métrica se movió pero ninguna bandera conocida la explica). En vez de forzar el problema en una bandera existente, Phase 5 **razona la causa raíz desde cero**.

> Sin esta rama, el loop quedaría entrenado a mirar solo las banderas semilla — ciego ante cualquier fallo no enumerado. El producto es AI-first: la inteligencia tiene que estar aquí, no en una tabla.

### Procedimiento
```
1. Reunir contexto: datos crudos del metrics_snapshot + historia de versiones de
   ESTA estrategia (results_summary de #1..#N) + project_lessons del proyecto +
   results_summary de los otros avatars (¿es solo este avatar o todos?).
2. Hipotetizar 1-3 causas raíz candidatas (LLM razona, no busca en lista).
3. Por cada candidata: ¿qué nivel de re-trigger resolvería? (mismo árbol Phase 0-3.)
4. Proponer la acción + un test barato para validar la hipótesis antes de comprometer
   una versión nueva cara (ej: un cambio de targeting de bajo costo en Phase 3).
5. Operador aprueba la hipótesis y la acción.
```

### Output: `optimization_plan.open_diagnosis`
```json
{
  "trigger": "unexplained_anomaly",
  "metric_moved": "ej: revenue_per_customer cae 18% con CTR/CAC/conversión estables",
  "candidate_root_causes": [
    { "hypothesis": "competidor lanzó gratis el módulo avanzado → se cae el upsell",
      "evidence": "...", "proposed_action": "rediseñar upsell", "re_trigger": "phase-1",
      "cheap_validation": "encuesta a 10 clientes recientes antes de versionar" }
  ],
  "selected_hypothesis": 0,
  "promote_if_validated": true
}
```

### Regla de promoción (el puente — ver `Overall_WF.md` §"Flag Registry" tier 3)
- Si la hipótesis se **valida** (la acción funcionó) o el patrón **se repite** en otra estrategia/avatar → se **promueve a bandera nueva** en el registro canónico, con su producer rule declarada. Mismo lifecycle que las `signal_rules` de Phase 0 (`save_lesson` → repite ≥3 → `best_practice`).
- Así el catálogo de banderas **crece desde la realidad**; las semilla nunca son el techo.

### Gate G-Phase-5.1.b
- Si hay `unexplained_anomaly`: `open_diagnosis` poblado con ≥1 causa raíz candidata + acción + validación barata
- `selected_hypothesis` y `promote_if_validated` declarados

---

## 4. Sub-paso 5.2 — Decisión de acción (registro de banderas)

### El registro de banderas es la vía rápida (NO un catálogo cerrado)

Esta tabla es la **semilla** del registro canónico (`Overall_WF.md` §"Flag Registry") — la **vía rápida determinística** para fallos conocidos. **No es exhaustiva ni "LOCKED"**: cuando llega `unexplained_anomaly`, Phase 5 NO busca aquí — va a la rama de diagnóstico abierto (§5.1.b) y, si valida una causa nueva, la **promueve** a este registro. Es decir: la tabla crece sola.

El principio sigue siendo: **re-trigger al nivel mínimo que resuelve la causa** — el error clásico es re-hacer todo (Phase 0) cuando solo el contenido fatigó (Phase 2).

| `phase_5_flag` | Origen | Acción | Re-trigger (nivel) | Emite Strategy #N+1 |
|---|---|---|---|---|
| `ctr_falling_30pct_14d` | P4 métrica | Refrescar hooks/contenido | **Phase 2** (ese avatar) | Sí |
| `conversion_falling_30pct` | P4 métrica | Revisar oferta (no convierte) | **Phase 1** (ese avatar) | Sí |
| `ltv_cac_below_3` | P4 métrica | Subir precio / retención / organic-only | **Phase 1** o decisión organic-only | Sí |
| `cac_up_40pct` | P4 métrica | Arreglar targeting primero | **Phase 3, MISMA versión activa** (re-genera `publish_plan`, la estrategia NO se supersede → D-010 se respeta). Escala a Phase 1 solo si persiste (LOOP-004) | No (Phase 3); Sí solo al escalar |
| `avatar_underperforming` | P4 métrica | Pausar avatar / reasignar presupuesto | **Archivar** esta estrategia (`status='archived'`), concentrar en ganadores | No (se archiva) |
| `avatar_changed_qualitatively` | **Operador** (manual) | Re-research de ESE avatar | **Phase 0.3↓, solo ese avatar** (Foundation 0.1–0.2.5 intacta) | Sí |
| `foundation_drift` | P4 métrica (cross-avatar/mercado/competencia) | Re-research del cimiento compartido | **Phase 0.1–0.2.5, todo el proyecto** | Sí (todos los avatars) |
| `unexplained_anomaly` | P4 métrica | **Razonar** la causa (§5.1.b) | Depende del diagnóstico; puede promover bandera nueva | Depende |
| (lista vacía, todo sano) | — | Mantener + escalar presupuesto del ganador | Ninguno | No |

**Fix clave vs la versión anterior (advisor M1 + M4 + 12-meses):**
- `cac_up_40pct` ya **no** permite "edición in-place" ambigua: es un re-trigger de **Phase 3 dentro de la misma versión** (la estrategia no se toca, solo su `publish_plan`), y solo escala a versión nueva si el targeting no lo arregla. Consistente con D-010.
- `avatar_changed_qualitatively` re-hace **solo la rama del avatar** (0.3↓), nunca la Foundation compartida — antes contaminaba a los otros avatars.
- **Eliminado `12_months_elapsed`**: no se reconstruye por calendario. La reconstrucción de cimientos la dispara `foundation_drift` (por evidencia).

### Output: `optimization_plan.action`

```json
{
  "action": "tune_content | new_offer | reprice | retarget | pause_avatar | restart_phase_0 | maintain_and_scale",
  "re_trigger_phase": "phase-0 | phase-1 | phase-2 | phase-3 | none",
  "emits_new_strategy_version": true,
  "rationale": "por qué este nivel de re-trigger y no otro (cita el/los flags)",
  "budget_reallocation": "si pause_avatar o maintain_and_scale: cómo se mueve el presupuesto entre avatars"
}
```

### Reglas duras
- El `re_trigger_phase` debe corresponder a la tabla (override solo con `decision_record`)
- `maintain_and_scale` (flags vacíos) NO emite versión nueva — escala el ganador. Esto es el caso de éxito.
- `pause_avatar` archiva la estrategia (`status='archived'`), no la versiona — el avatar puede reactivarse después con `decision_record`

### Gate G-Phase-5.2
- `action` + `re_trigger_phase` decididos desde la tabla; `rationale` cita flags

---

## 5. Sub-paso 5.3 — Emisión de Strategy #N+1

### Propósito
Cuando `emits_new_strategy_version: true`, crear la siguiente versión de la estrategia (preservando la anterior) y disparar el re-trigger.

### Procedimiento (transaccional)

```
1. INSERT nueva strategies row:
   - mismo project_id, avatar_id, covers_avatar_ids, multi_avatar_strategy
   - version_number = anterior + 1
   - status = 'active'
   - results_summary = '{}'  (se llenará en la nueva Phase 4)
2. UPDATE estrategia anterior:
   - status = 'superseded'
   - superseded_by = <id de la nueva>
   (El índice parcial uniq_active_strategy_per_avatar garantiza 1 sola active por avatar:
    el paso 2 debe ejecutarse en la misma transacción que el paso 1.)
3. Disparar el re-trigger en la fase indicada (Phase 0/1/2/3), que produce los
   artefactos de la nueva versión, todos anclados al strategy_id nuevo.
4. decision_record con strategy_id (nuevo y anterior), action, re_trigger_phase, rationale.
```

### Reglas duras
- Orden transaccional: nunca dos estrategias `active` para el mismo avatar simultáneamente (lo garantiza `uniq_active_strategy_per_avatar`)
- **Herencia de Foundation según el NIVEL del re-trigger (fix advisor M4):**
  - Re-trigger nivel **avatar** (`ctr_falling`, `conversion_falling`, `ltv_cac`, `avatar_changed_qualitatively`): **hereda la Foundation compartida intacta** (0.1–0.2.5) y re-hace solo desde donde aplique para ESE avatar. `avatar_changed_qualitatively` re-hace desde 0.3↓ **solo de ese avatar** — NUNCA toca la Foundation, porque es compartida y dañaría a los otros N-1 avatars.
  - Re-trigger nivel **foundation** (`foundation_drift`): **sí** re-hace 0.1–0.2.5 a nivel proyecto, lo que cascada a todos los avatars (es el único caso que justifica rehacer el cimiento).
- La nueva estrategia arranca su propio loop Phase 1→4; el histórico de la anterior queda consultable

### Gate G-Phase-5.3
- Nueva `strategies` row creada con `version_number` incrementado, anterior `superseded`
- Re-trigger disparado en la fase correcta
- `decision_record` con ambos `strategy_id`

---

## 6. Transversal — Crystallize learnings

### Propósito
Cada ciclo cerrado produce aprendizaje. Lo que funcionó/falló se persiste **por estrategia** (los nodos "Learnings", "Decisions", "Best Practices" del diagrama).

### Escrituras
- `project_lessons` con `strategy_id` + `avatar_id`: qué se aprendió de este ciclo (ej: "hook tipo contrarian fatiga en 10 días para avatar Estudiante")
- `project_decisions` con `strategy_id`: la decisión de optimización tomada
- Best-practices (lessons con tag `best-practice`): patrones que se repiten ≥3 ciclos se promueven (ej: "para B2C impulsivo, refrescar hooks cada 14 días preventivamente")
- Hooks ganadores (`results_summary.winning_hooks`) se promueven a la hook library con tag `hook-winner` (cierra el loop con Phase 2.5)
- **Promoción de bandera nueva (el puente del registro vivo):** si una `open_diagnosis` (§5.1.b) validó una causa raíz que no estaba en el registro, se registra como **bandera nueva** en `Overall_WF.md` §"Flag Registry" — con `name | producer | action | re-trigger scope`. A partir de ahí pasa de "razonamiento" (lento) a "vía rápida" (determinística). Así el catálogo de banderas crece desde la realidad y el sistema deja de re-pensar problemas ya resueltos.

### Regla
- Si `action != maintain_and_scale`, al menos 1 `project_lesson` con `strategy_id` debe escribirse (un ciclo que ajustó algo sin aprender nada es sospechoso — paralelo a EVIDENCE-001 de Phase 0)

---

## 7. Output canónico de Phase 5: `optimization_plan.json`

```json
{
  "plan_id": "optimization_v1_YYYYMMDD",
  "linked_to": {
    "strategy_id_evaluated": "strategy_uuid_v1",
    "strategy_id_new": "strategy_uuid_v2",
    "avatar_id": "avatar_1"
  },
  "diagnosis": { "...del 5.1..." },
  "open_diagnosis": { "...del 5.1.b, solo si hubo unexplained_anomaly..." },
  "action": { "...del 5.2..." },
  "flags_promoted": [],
  "new_strategy_emitted": {
    "emitted": true,
    "new_version_number": 2,
    "previous_superseded": true,
    "re_trigger_dispatched": "phase-2"
  },
  "learnings_written": ["lesson_uuid_1"],
  "decisions_written": ["decision_uuid_1"],
  "best_practices_promoted": [],
  "signal_rules_triggered": [],
  "metadata": { "hours_invested": 0, "usd_invested": 0, "completed_at": "ISO date", "operator_signoff": true }
}
```

---

## 8. Gate global G-Phase-5
- Sub-gates 5.1–5.3 cerrados (5.1.b solo si hubo `unexplained_anomaly`)
- Cada `phase_5_flag` direccionado en el diagnóstico
- `action` + `re_trigger_phase` decididos desde el registro de banderas (`Overall_WF.md`), o vía `open_diagnosis` si fue `unexplained_anomaly`, o `decision_record` por override
- Si `unexplained_anomaly` y la causa se validó: bandera nueva promovida al registro
- Si `emits_new_strategy_version`: nueva `strategies` row activa, anterior superseded, re-trigger disparado al **nivel correcto** (avatar 0.3↓ vs foundation 0.1–0.2.5)
- Si `action != maintain_and_scale`: ≥1 `project_lesson` con `strategy_id`
- `operator_signoff: true`

---

## 9. Signal rules de Phase 5

```json
{
  "rules": [
    {
      "id": "LOOP-001",
      "applicable_phase": "phase-5.2",
      "condition": "phase_5_flags non-empty AND re_trigger_phase == 'none'",
      "severity": "alert",
      "signal": "Hay flags pero no se disparó re-trigger",
      "implication": "Un problema detectado por Phase 4 quedó sin acción. Mapear cada flag a la tabla flag→acción.",
      "auto_action": "block Phase 5 close"
    },
    {
      "id": "LOOP-002",
      "applicable_phase": "phase-5.3",
      "condition": "emits_new_strategy_version == true AND previous strategy still status='active'",
      "severity": "alert",
      "signal": "Se creó versión nueva sin superseder la anterior",
      "implication": "Violación del invariante 'una sola estrategia active por avatar'. La transacción debe superseder la anterior.",
      "auto_action": "block Phase 5 close (rollback)"
    },
    {
      "id": "LOOP-003",
      "applicable_phase": "phase-5 transversal",
      "condition": "action != maintain_and_scale AND learnings_written.length == 0",
      "severity": "warning",
      "signal": "Ciclo ajustado sin aprendizaje registrado",
      "implication": "Optimizar sin crystallizar el aprendizaje pierde la ventaja del loop. Escribir ≥1 lesson con strategy_id.",
      "auto_action": "require operator_acknowledgment"
    },
    {
      "id": "LOOP-004",
      "applicable_phase": "phase-5.2",
      "condition": "same flag triggered ≥3 consecutive versions for same avatar",
      "severity": "warning",
      "signal": "El mismo problema reaparece versión tras versión",
      "implication": "El re-trigger elegido no resuelve la causa raíz. Escalar el nivel (ej: de Phase 2 a Phase 1, o de Phase 1 a Phase 0). Posible que el avatar no sea viable. Si el flag recurrente es de vía rápida, considerar abrir diagnóstico (§5.1.b) — la causa real puede no ser la que la bandera asume.",
      "auto_action": "require decision_record escalating re-trigger level or pausing avatar"
    },
    {
      "id": "LOOP-005",
      "applicable_phase": "phase-5.1.b",
      "condition": "phase_5_flags includes 'unexplained_anomaly' AND optimization_plan.open_diagnosis is empty",
      "severity": "alert",
      "signal": "Anomalía sin explicación pero no se abrió diagnóstico — el sistema no pensó",
      "implication": "unexplained_anomaly NO se puede forzar en una bandera existente ni ignorar. Obliga a la rama de diagnóstico abierto (§5.1.b). Sin esto, el loop vuelve a ser un catálogo ciego.",
      "auto_action": "block Phase 5 close until open_diagnosis poblado"
    }
  ]
}
```

---

## 10. Re-trigger de Phase 5
Phase 5 corre cada vez que Phase 4 produce un snapshot con `phase_5_flags`. Es el latido del loop: mide → diagnostica → ajusta → nueva versión → mide. En `maintain_and_scale`, Phase 5 corre pero no versiona (solo escala presupuesto).

---

## 11. Decisiones cerradas en Phase 5 v1.0

| # | Decisión | Resolución |
|---|---|---|
| D1 | ¿Phase 5 edita o versiona? | **Versiona.** Emite Strategy #N+1, marca la anterior superseded. Preserva histórico (D-010). |
| D2 | ¿Re-trigger a qué nivel? | **Registro de banderas vivo** (`Overall_WF.md`), no tabla cerrada. Cada bandera mapea al nivel mínimo que resuelve la causa. Las banderas semilla son la vía rápida; el registro crece por promoción. |
| D3 | Foundation se preserva (fix M4) | Re-trigger nivel **avatar** (incl. `avatar_changed_qualitatively`) hereda Foundation intacta y re-hace solo 0.3↓ de ESE avatar. Solo `foundation_drift` re-hace 0.1–0.2.5 a nivel proyecto. |
| D4 | Avatars perdedores | `pause_avatar` archiva la estrategia y reasigna presupuesto — feature de la orquestación paralela. |
| D5 | maintain_and_scale | Flags vacíos = éxito: no versiona, escala el ganador. |
| D6 | Learnings por estrategia | `project_lessons`/`decisions`/best-practices llevan `strategy_id` — materializan los nodos del diagrama. |
| D7 | Causa raíz recurrente | LOOP-004: si un flag reaparece ≥3 versiones, escalar nivel de re-trigger o pausar avatar. |
| D8 | Diagnóstico abierto (no solo catálogo) | `unexplained_anomaly` (P4 ANOMALY-001) obliga a §5.1.b: razonar la causa raíz, no buscar en lista. LOOP-005 lo enforce. El sistema PIENSA cuando las banderas conocidas no explican. |
| D9 | Registro vivo (promoción) | Causas raíz validadas en §5.1.b se promueven a banderas nuevas (lifecycle tipo signal-rule de Phase 0). El catálogo crece desde la realidad; las 8 semilla no son el techo. |
| D10 | Sin refresh por calendario (Coca-Cola) | Eliminado `12_months_elapsed`. La Foundation se reconstruye por `foundation_drift` (evidencia), no por fecha. **Revisar ≠ reconstruir:** *revisar* es continuo (freshness SEO, revisión quincenal de RRSS, benchmark competitivo periódico) y **alimenta las banderas**; *reconstruir* el cimiento (0.1–0.2.5) solo lo dispara `foundation_drift`. Eliminar el calendario no elimina el mantenimiento continuo — lo separa del versionado. *(Resuelve la tensión aparente con el corpus que insiste en freshness continuo.)* |
| D11 | `cac_up_40pct` no edita in-place (fix M1) | Re-trigger de Phase 3 dentro de la MISMA versión activa (re-genera publish_plan, la estrategia no se supersede → D-010 intacto). Solo escala a Phase 1 (versión nueva) si persiste. |

---

## 12. Apéndice — checklist operacional V1

```
[ ] G-Phase-5-PRE: 3 checks (metrics_snapshot firmado, results_summary con flags, estrategia active)
[ ] 5.1 — diagnosis: cada flag direccionado + root_cause_hypothesis
[ ] 5.1.b — si hay unexplained_anomaly: open_diagnosis con ≥1 causa candidata + validación barata (LOOP-005)
[ ] 5.2 — action + re_trigger_phase desde el registro de banderas, rationale cita flags
[ ] 5.2 — nivel correcto: avatar (0.3↓ ese avatar) vs foundation (0.1–0.2.5 proyecto); cac_up = Phase 3 misma versión
[ ] 5.3 — si versiona: nueva strategies row (version+1, active) + anterior superseded (misma transacción)
[ ] 5.3 — re-trigger disparado en la fase correcta; artefactos nuevos anclados al strategy_id nuevo
[ ] 5.3 — decision_record con ambos strategy_id
[ ] Transversal — ≥1 project_lesson con strategy_id si action != maintain_and_scale
[ ] Transversal — hooks ganadores promovidos a hook library (tag hook-winner)
[ ] Transversal — si open_diagnosis validó causa nueva: bandera promovida al registro (Overall_WF)
[ ] Signal rules evaluadas (LOOP-001/002/003/004/005)
[ ] optimization_plan.json consolidado
[ ] operator_signoff: true
```
