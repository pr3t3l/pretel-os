# Phase 5 — Ajustar / Optimizar (el loop)

**Project**: business/marketing-os
**Phase ID**: phase-5
**Status**: spec drafted v1.0
**Last updated**: 2026-06-06
**Implementation correction:** Targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase). Persist outputs in `project_phase_artifacts` (`phase = 'review'`), decisions in `project_decisions`, learnings/best-practices in `project_lessons`. **Phase 5 es la fase que cierra y reinicia el loop por avatar: NO edita la estrategia activa — emite Strategy #N+1** (`strategies` row nueva, `status='active'`) y marca la anterior `superseded` (`strategies.superseded_by`).

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
| 5.2 — Decisión de acción (lookup determinístico) | `optimization_plan.action` | 30 min | Algoritmo flag→acción + operador aprueba | Auto + flag excepciones |
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

## 4. Sub-paso 5.2 — Decisión de acción (lookup determinístico)

### Tabla flag → acción → re-trigger (LOCKED, override por `decision_record`)

Esta tabla es el corazón del loop. Cada flag mapea al nivel de re-trigger correcto — el error clásico es re-hacer todo (Phase 0) cuando solo el contenido fatigó (Phase 2).

| `phase_5_flag` | Acción | Re-trigger | Emite Strategy #N+1 |
|---|---|---|---|
| `ctr_falling_30pct_14d` | Refrescar hooks/contenido | **Phase 2** (nuevos hooks/pilares) | Sí |
| `conversion_falling_30pct` | Revisar oferta (no convierte) | **Phase 1** (nueva oferta) | Sí |
| `ltv_cac_below_3` | Subir precio / retención / organic-only | **Phase 1** (pricing) o decisión organic-only | Sí |
| `cac_up_40pct` | Revisar targeting/canales | **Phase 3** (targeting) | No (ajuste in-place permitido) si solo es targeting; Sí si requiere oferta nueva |
| `avatar_underperforming` | Pausar avatar / reasignar presupuesto | **Pausar** esta estrategia (`status='archived'`), concentrar en avatars ganadores | No (se archiva, no se versiona) |
| `avatar_changed_qualitatively` | El avatar mutó (señales cualitativas) | **Phase 0** (re-research del avatar) | Sí (tras Phase 0→1→2) |
| `12_months_elapsed` | Forced refresh | **Phase 0** | Sí |
| (lista vacía, todo sano) | Mantener + escalar | Ninguno — escalar presupuesto del ganador | No |

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
- El re-trigger NO empieza desde cero: hereda los artefactos avatar-agnósticos de Foundation (Phase 0.1–0.2.5) salvo que el flag sea `avatar_changed_qualitatively` o `12_months_elapsed` (esos sí re-hacen Foundation)
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
  "action": { "...del 5.2..." },
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
- Sub-gates 5.1–5.3 cerrados
- Cada `phase_5_flag` direccionado en el diagnóstico
- `action` + `re_trigger_phase` decididos desde la tabla LOCKED (o `decision_record` por override)
- Si `emits_new_strategy_version`: nueva `strategies` row activa, anterior superseded, re-trigger disparado
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
      "implication": "El re-trigger elegido no resuelve la causa raíz. Escalar el nivel (ej: de Phase 2 a Phase 1, o de Phase 1 a Phase 0). Posible que el avatar no sea viable.",
      "auto_action": "require decision_record escalating re-trigger level or pausing avatar"
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
| D2 | ¿Re-trigger a qué nivel? | Tabla LOCKED flag→acción→fase. Cada flag mapea al nivel mínimo que resuelve la causa (no re-hacer todo). |
| D3 | Foundation se preserva | El re-trigger hereda Phase 0.1–0.2.5 (avatar-agnóstico) salvo `avatar_changed` o `12m_elapsed`. |
| D4 | Avatars perdedores | `pause_avatar` archiva la estrategia y reasigna presupuesto — feature de la orquestación paralela. |
| D5 | maintain_and_scale | Flags vacíos = éxito: no versiona, escala el ganador. |
| D6 | Learnings por estrategia | `project_lessons`/`decisions`/best-practices llevan `strategy_id` — materializan los nodos del diagrama. |
| D7 | Causa raíz recurrente | LOOP-004: si un flag reaparece ≥3 versiones, escalar nivel de re-trigger o pausar avatar. |

---

## 12. Apéndice — checklist operacional V1

```
[ ] G-Phase-5-PRE: 3 checks (metrics_snapshot firmado, results_summary con flags, estrategia active)
[ ] 5.1 — diagnosis: cada flag direccionado + root_cause_hypothesis
[ ] 5.2 — action + re_trigger_phase desde tabla LOCKED, rationale cita flags
[ ] 5.3 — si versiona: nueva strategies row (version+1, active) + anterior superseded (misma transacción)
[ ] 5.3 — re-trigger disparado en la fase correcta; artefactos nuevos anclados al strategy_id nuevo
[ ] 5.3 — decision_record con ambos strategy_id
[ ] Transversal — ≥1 project_lesson con strategy_id si action != maintain_and_scale
[ ] Transversal — hooks ganadores promovidos a hook library (tag hook-winner)
[ ] Signal rules evaluadas (LOOP-001/002/003/004)
[ ] optimization_plan.json consolidado
[ ] operator_signoff: true
```
