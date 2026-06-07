# Phase 4 — Medir

**Project**: business/marketing-os
**Phase ID**: phase-4
**Status**: spec drafted v1.0
**Last updated**: 2026-06-06
**Implementation correction:** Targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase). Persist outputs in `project_phase_artifacts` (`phase = 'review'`), decisions in `project_decisions`, learnings in `project_lessons`. **El output de Phase 4 también escribe `strategies.results_summary`** (la columna jsonb de "Resultados" del diagrama de jerarquía). Cada artefacto/decisión/lección lleva `strategy_id` + `avatar_id`.

**Reference**: `Overall_WF.md` §"Strategy Lifecycle". `spec_Phase_3_Distribucion.md` §7 (`phase_4_handoff`). Cierra los gates ECONOMICS-001 (Phase 0) y los re-triggers de Phases 0/1/2/3.

---

## 0. Contexto y propósito

Phase 4 mide lo que Phase 3 publicó y lo convierte en **Resultados estructurados por estrategia**. Es el ojo del loop: produce las señales que Phase 5 consume para decidir si la estrategia se mantiene, se ajusta o se reinicia (emitiendo Strategy #N+1).

**Pertenencia a una Estrategia (D-009/D-010):** las métricas se atribuyen **por `strategy_id`** (gracias al UTM por avatar de Phase 3). Esto es lo que permite comparar avatars: la estrategia del Estudiante y la del Panadero tienen `results_summary` independientes. Comparar avatars es trivial para la IA (cada uno su dashboard) y es la base de la orquestación paralela.

**Output canónico**: `metrics_snapshot.json` (snapshot fechado de KPIs) + escritura de `strategies.results_summary` (rollup vivo).

**Spine operacional**:
- Unit economics (Hormozi/estándar): CAC, LTV, LTV:CAC, payback — validados contra el `economics_baseline` de Phase 0.
- Funnel por awareness (Schwartz): medir conversión por nivel, no solo total.
- Atribución honesta: leads de negative_personas se flaguean como low-quality ANTES de calcular conversion rates (Phase 0.3 contrato).

---

## 1. Estructura: 3 sub-pasos

| Sub-paso | Output | Estimado V1 | V1 | V2 |
|---|---|---|---|---|
| 4.1 — Métricas raw por canal/pilar | `metrics_snapshot.raw` | 1 h/snapshot | Manual (operador pega datos de GA4/plataformas) | Sub-workflow pull vía API |
| 4.2 — Unit economics + funnel | `metrics_snapshot.economics` + `funnel` | 1 h | Claude calcula desde raw + baseline | Auto |
| 4.3 — Results rollup a la estrategia | `strategies.results_summary` | 30 min | Claude consolida + operador firma | Auto |

---

## 2. Pre-condición — Gate de entrada G-Phase-4-PRE

1. ✅ `publish_plan.json` existe con `metadata.operator_signoff: true` y `go_live.operator_signoff: true`
2. ✅ `publish_plan.linked_to.strategy_id` activo y `phase_4_handoff` poblado (conversion event + KPIs + economics_baseline)
3. ✅ Ha transcurrido el `attribution_window_days` desde `measurement_start` (no se mide antes de que la ventana de atribución cierre — medir demasiado pronto produce CAC/LTV ruidosos)
4. ✅ `tracking_manifest` con canales `verified: true` (sin tracking verificado no hay datos atribuibles)

---

## 3. Sub-paso 4.1 — Métricas raw por canal/pilar

### Output: `metrics_snapshot.raw`

```json
{
  "snapshot_at": "ISO date",
  "period": { "from": "ISO", "to": "ISO" },
  "per_pillar": [
    {
      "pillar_id": "PILLAR_A",
      "channel": "blog",
      "avatar_id": "avatar_1",
      "impressions": 0,
      "clicks": 0,
      "ctr": 0,
      "conversions": 0,
      "conversion_rate": 0,
      "cost_usd": 0,
      "kpi_primary_value": 0
    }
  ],
  "per_hook": [
    { "hook_id": "hook_A_07", "uses": 0, "ctr": 0, "status": "tested | winner | retired" }
  ],
  "negative_quality_leads_excluded": 0
}
```

### Reglas duras
- Cada entrada con `avatar_id` (atribución por avatar — sin esto no se puede comparar avatars)
- `negative_quality_leads_excluded` contado y restado ANTES de `conversion_rate` (honestidad de Phase 0.3)
- KPI primario de cada pilar (definido en Phase 2.3 / Phase 3 handoff) poblado

### Gate G-Phase-4.1
- Raw poblado para cada pilar+canal activo en el calendario, con atribución por avatar

---

## 4. Sub-paso 4.2 — Unit economics + funnel

### Output: `metrics_snapshot.economics` + `metrics_snapshot.funnel`

```json
{
  "economics": {
    "cac_actual_usd": 0,
    "ltv_actual_usd": 0,
    "ltv_cac_ratio": 0,
    "payback_days": 0,
    "baseline": { "target_cac_usd": 0, "expected_ltv_usd": 0, "source": "phase_3_handoff.economics_baseline" },
    "cac_vs_baseline_pct": 0,
    "ltv_vs_baseline_pct": 0,
    "economics_health": "green | yellow | red"
  },
  "funnel": {
    "by_awareness": { "most_aware": { "visitors": 0, "conversions": 0, "rate": 0 } },
    "drop_off_stage": "qué etapa pierde más prospectos"
  }
}
```

### Reglas duras
- `ltv_cac_ratio` se compara contra 3.0 (ECONOMICS-001 de Phase 0): `< 3.0` → `economics_health: red`
- `cac_vs_baseline_pct` y `ltv_vs_baseline_pct`: divergencia ≥50% dispara re-trigger candidate flag para Phase 1 (heredado de Phase 1 §11)
- El funnel se mide por awareness level, no solo total (un funnel total sano puede ocultar un nivel roto)

### Gate G-Phase-4.2
- Unit economics calculados contra baseline; `economics_health` clasificado
- Funnel por awareness poblado con `drop_off_stage` identificado

---

## 5. Sub-paso 4.3 — Results rollup a la estrategia

### Propósito
Consolidar el snapshot en `strategies.results_summary` — el campo "Resultados" del diagrama de jerarquía. Este es el dato vivo que Phase 5 lee.

### Escritura: `strategies.results_summary`

```json
{
  "last_snapshot_at": "ISO date",
  "snapshots_count": 1,
  "economics_health": "green | yellow | red",
  "ltv_cac_ratio": 0,
  "best_pillar": "PILLAR_A",
  "worst_pillar": "PILLAR_C",
  "winning_hooks": ["hook_A_07"],
  "fatigued_hooks": ["hook_C_02"],
  "ctr_trend": "rising | flat | falling",
  "conversion_trend": "rising | flat | falling",
  "phase_5_flags": [
    "ctr_falling_30pct_14d | cac_up_40pct | ltv_cac_below_3 | avatar_underperforming"
  ]
}
```

### Reglas duras
- `phase_5_flags` es el contrato vinculante hacia Phase 5: cada flag mapea a una condición de re-trigger documentada (Phases 0/1/2/3 §re-trigger)
- En proyectos multi-avatar, comparar `results_summary` entre estrategias activas: si un avatar rinde <30% del mejor avatar sostenido, flag `avatar_underperforming` (candidato a pausar esa estrategia y reasignar presupuesto)
- `strategies.results_summary` se actualiza, no se sobrescribe el histórico: cada snapshot incrementa `snapshots_count`; el snapshot fechado completo vive en `metrics_snapshot.json` (artifact)

### Gate G-Phase-4.3
- `strategies.results_summary` escrito con `phase_5_flags` poblado (lista vacía permitida si todo sano)
- `operator_signoff` en el snapshot

---

## 6. Output canónico de Phase 4: `metrics_snapshot.json`

```json
{
  "snapshot_id": "metrics_v1_YYYYMMDD",
  "linked_to": { "strategy_id": "strategy_uuid", "strategy_version": 1, "publish_plan_id": "publish_v1_YYYYMMDD", "avatar_id": "avatar_1" },
  "raw": { "...del 4.1..." },
  "economics": { "...del 4.2..." },
  "funnel": { "...del 4.2..." },
  "results_summary_written": true,
  "phase_5_handoff": {
    "phase_5_flags": ["..."],
    "economics_health": "green | yellow | red",
    "recommended_action_hint": "maintain | tune_content | new_offer | pause_avatar | restart_phase_0"
  },
  "signal_rules_triggered": [],
  "metadata": { "hours_invested": 0, "usd_invested": 0, "completed_at": "ISO date", "operator_signoff": true }
}
```

---

## 7. Gate global G-Phase-4
- Sub-gates 4.1–4.3 cerrados
- `metrics_snapshot.json` anclado a `strategy_id`, con atribución por avatar
- `strategies.results_summary` escrito (incluye `phase_5_flags`)
- Unit economics validados contra baseline (`economics_health` clasificado)
- `negative_quality_leads_excluded` contabilizado antes de conversion rates
- `operator_signoff: true`

---

## 8. Signal rules de Phase 4

```json
{
  "rules": [
    {
      "id": "ECONOMICS-LIVE-001",
      "applicable_phase": "phase-4.2",
      "condition": "ltv_cac_ratio < 3.0",
      "severity": "alert",
      "signal": "Unit economics reales bajo el umbral 3:1 (valida ECONOMICS-001 de Phase 0 con datos reales)",
      "implication": "Adquisición pagada insostenible. Phase 5 debe disparar: subir precio (Phase 1), subir retención (LTV), o pasar a organic-only.",
      "auto_action": "set economics_health=red; flag phase_5 ltv_cac_below_3"
    },
    {
      "id": "ECONOMICS-LIVE-002",
      "applicable_phase": "phase-4.2",
      "condition": "abs(cac_vs_baseline_pct) >= 50 OR abs(ltv_vs_baseline_pct) >= 50",
      "severity": "warning",
      "signal": "CAC/LTV real diverge ≥50% del estimado en Phase 0",
      "implication": "El supuesto económico de Phase 0 era incorrecto. Candidato a re-trigger de Phase 1 (oferta) — heredado de Phase 1 §11.",
      "auto_action": "flag phase_5 candidate re-trigger phase-1"
    },
    {
      "id": "FATIGUE-001",
      "applicable_phase": "phase-4.3",
      "condition": "ctr_trend == falling AND ctr drop >= 30% sustained 14d",
      "severity": "warning",
      "signal": "Fatiga de contenido/hook (CTR cae ≥30% sostenido)",
      "implication": "Hook fatigue o cambio de awareness. Phase 5 debe re-triggerar Phase 2 (contenido/hooks nuevos).",
      "auto_action": "flag phase_5 ctr_falling_30pct_14d"
    },
    {
      "id": "AVATAR-PERF-001",
      "applicable_phase": "phase-4.3",
      "condition": "in multi-avatar project: this strategy's key metric < 30% of best active strategy, sustained",
      "severity": "warning",
      "signal": "Avatar rinde muy por debajo de otros avatars del proyecto",
      "implication": "Candidato a pausar esta estrategia y reasignar presupuesto a avatars ganadores. No es fracaso del sistema — es la orquestación paralela funcionando (matar perdedores rápido).",
      "auto_action": "flag phase_5 avatar_underperforming"
    }
  ]
}
```

---

## 9. Re-trigger de Phase 4
- Phase 3 publica → Phase 4 mide tras `attribution_window_days`
- Cadencia recurrente: Phase 4 corre por snapshot (semanal/quincenal) mientras la estrategia esté `active` — cada snapshot actualiza `results_summary`
- Phase 5 emite Strategy #N+1 → Phase 4 mide la nueva versión (baseline se resetea al nuevo plan)

---

## 10. Decisiones cerradas en Phase 4 v1.0

| # | Decisión | Resolución |
|---|---|---|
| D1 | ¿Dónde viven los "Resultados"? | En `strategies.results_summary` (rollup vivo) + `metrics_snapshot.json` (histórico fechado). Materializa el nodo "Resultados" del diagrama. |
| D2 | Atribución por avatar | Obligatoria (UTM por avatar de Phase 3). Sin esto no se comparan avatars ni funciona la orquestación paralela. |
| D3 | Negative-quality leads | Se excluyen ANTES de calcular conversion rates (contrato de honestidad de Phase 0.3). |
| D4 | LTV:CAC gate con datos reales | ECONOMICS-LIVE-001 valida ECONOMICS-001 de Phase 0. `< 3.0` → red → Phase 5 actúa. |
| D5 | `phase_5_flags` como contrato | Cada flag mapea a una condición de re-trigger documentada; Phase 5 los consume determinísticamente. |
| D6 | Matar avatars perdedores | AVATAR-PERF-001 es feature, no bug: la orquestación paralela permite pausar avatars débiles y concentrar presupuesto. |

---

## 11. Apéndice — checklist operacional V1

```
[ ] G-Phase-4-PRE: 4 checks (publish_plan firmado, strategy_id activo, attribution_window cerrada, tracking verificado)
[ ] 4.1 — metrics_snapshot.raw por pilar+canal con avatar_id
[ ] 4.1 — negative_quality_leads_excluded contado antes de conversion_rate
[ ] 4.2 — unit economics (CAC, LTV, ratio, payback) vs baseline; economics_health clasificado
[ ] 4.2 — funnel por awareness con drop_off_stage
[ ] 4.3 — strategies.results_summary escrito con phase_5_flags
[ ] 4.3 — comparación cross-avatar si proyecto multi-avatar (AVATAR-PERF-001)
[ ] metrics_snapshot.json anclado a strategy_id + avatar_id
[ ] phase_5_handoff con recommended_action_hint
[ ] Signal rules evaluadas: ninguna alert sin flag a Phase 5
[ ] operator_signoff: true
```
