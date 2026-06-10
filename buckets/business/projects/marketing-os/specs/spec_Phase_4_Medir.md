# Phase 4 — Medir

**Project**: business/marketing-os
**Phase ID**: phase-4
**Status**: spec drafted v1.0
**Last updated**: 2026-06-06
**Implementation correction:** Targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase). Persist outputs in `project_phase_artifacts` (`phase = 'phase_4'`; el legacy `review` queda como alias deprecado — ver `Overall_WF.md` §"Phase ↔ Supabase mapping"). Decisions en `project_decisions`, learnings en `project_lessons`. **El output de Phase 4 también escribe `strategies.results_summary`** (la columna jsonb de "Resultados" del diagrama de jerarquía). Cada artefacto/decisión/lección lleva `strategy_id` + `avatar_id`.

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
| 4.1 — Métricas raw por canal/pilar | `metrics_snapshot.raw` | 1 h/snapshot | Manual (operador pega datos de GA4/plataformas) | Pull vía conector multi-plataforma (p.ej. Windsor.ai: GA4 + Google Ads + Meta/TikTok/LinkedIn → URL conector JSON/CSV). Candidato a `tracking_manifest`/V2, no contrato V1 |
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
      "kpi_primary_value": 0,
      "completion_rate": 0,
      "avg_watch_time_s": 0,
      "saves": 0,
      "shares": 0
    }
  ],
  "per_search_term": [
    { "term": "ejemplo query", "channel": "google_ads", "avatar_id": "avatar_1", "spend_usd": 0, "conversions": 0, "category": "profitable | informational | out_of_model | non_converting" }
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
- **Métricas de algoritmo en social (opcionales por canal):** para pilares en canales sociales, poblar `completion_rate`, `avg_watch_time_s`, `saves`, `shares`. Para video corto, `completion_rate` es **indicador LÍDER de fatiga** — su caída precede a la del CTR (indicador tardío). Snapshot **quincenal** (alineado con la revisión cada 15 días). *(Curso 7 Fase 4)*
- **`per_search_term` (bloque opcional, solo canales de pago):** clasificar cada término con `spend_usd > 0` en una `category` ∈ `{profitable, informational, out_of_model, non_converting}` (`category` es **[Extensible Vocabulary]** — sembrada con estos cuatro miembros + `other`). `non_converting` (`spend_usd > 0 AND conversions == 0`) y `out_of_model` son desperdicio de presupuesto que el funnel agregado oculta y que Phase 5 acciona vía la bandera `paid_search_waste` (ver §8). *(Curso 5 C8)*

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
- **[Context-Adjusted Threshold]** `ltv_cac_ratio` NO se compara contra un 3.0 plano (eso es estándar SaaS y marcaría "red" a un producto físico de compra única perfectamente viable por margen unitario). El umbral es **tabla por modelo de negocio**:

  | modelo (de `product_brief.expected_repeat_rate` + `delivery_format`) | LTV:CAC mínimo default |
  |---|---|
  | subscription / recurring | 3.0 |
  | occasional repeat | 2.5 |
  | one-shot, margen unitario alto (≥60%) | 2.0 |
  | one-shot, margen bajo | 3.0 |

- **La alarma no se apaga, solo se razona.** `ratio < umbral_del_modelo` → no es veredicto automático `red`: cerca o bajo el umbral, se razona el contexto con **evidencia dura** (margen unitario real, recurrencia real, etapa) antes del veredicto. Si tras razonar con evidencia sigue insano → `red`. *(Esto suaviza el falso-red sin abrir la puerta al autoengaño — ver Overall_WF §Pattern B y `EVIDENCE-001`.)*
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
    "ctr_falling_30pct_14d", "conversion_falling_30pct", "ltv_cac_below_3",
    "cac_up_40pct", "avatar_underperforming", "foundation_drift", "unexplained_anomaly",
    "zero_click_informational_decay", "paid_search_waste"
  ]
}
```

### Reglas duras
- `phase_5_flags` es un **conjunto ABIERTO** (jsonb), no un enum cerrado. Sus valores y su contrato viven en el **registro canónico de banderas** (`Overall_WF.md` §"Flag Registry"). Phase 4 es el **productor** de las banderas de origen métrico; Phase 5 las consume. Ninguna fase mantiene su propia copia del catálogo (evita el drift que causó el orphan M3).
- **Regla productor-binding**: toda bandera métrica que Phase 4 emite debe tener su signal rule en §8. Si no hay regla que la produzca, la bandera no existe. (Las banderas de origen NO-métrico — `avatar_changed_qualitatively` del operador, etc. — no las emite Phase 4; ver el registro.) Las banderas nuevas de origen Phase 4 quedan declaradas producer-bound aquí: `zero_click_informational_decay` (productor AIO-TRAFFIC-001) y `paid_search_waste` (productor PAID-SEARCH-WASTE-001) — ambas con su signal rule en §8 y pendientes de promoción al registro canónico (`Overall_WF.md` §"Flag Registry").
- Cuando las métricas se mueven materialmente pero **ninguna bandera conocida encaja**, Phase 4 emite `unexplained_anomaly` (ANOMALY-001) — esa es la señal que obliga a Phase 5 a **razonar** la causa raíz en vez de buscar en una lista.
- En proyectos multi-avatar, comparar `results_summary` entre estrategias activas: si un avatar rinde <30% del mejor avatar sostenido → `avatar_underperforming`; si **todos** caen a la vez → `foundation_drift` (el cimiento compartido se movió, no un avatar).
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
    "recommended_action_hint": "maintain_and_scale | tune_content | retarget | new_offer | pause_avatar | rebuild_avatar (0.3↓) | rebuild_foundation (0.1-0.2.5) | open_diagnosis"
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
      "condition": "ltv_cac_ratio < umbral_del_modelo (tabla por modelo de negocio, NO 3.0 plano — ver Reglas duras 4.2 [Context-Adjusted Threshold])",
      "severity": "alert",
      "signal": "Unit economics reales bajo el umbral del modelo (valida ECONOMICS-001 de Phase 0 con datos reales)",
      "implication": "Cerca/bajo el umbral → razonar contexto con evidencia (margen unitario, recurrencia, etapa) ANTES del veredicto red. Si sigue insano tras razonar: adquisición pagada insostenible → Phase 5 dispara subir precio (Phase 1), subir retención (LTV), o pasar a organic-only. La alarma no se apaga; el veredicto se razona.",
      "auto_action": "if reasoned-insano: set economics_health=red; flag phase_5 ltv_cac_below_3"
    },
    {
      "id": "ECONOMICS-LIVE-002",
      "applicable_phase": "phase-4.2",
      "condition": "abs(cac_vs_baseline_pct) >= 50 OR abs(ltv_vs_baseline_pct) >= 50",
      "severity": "warning",
      "signal": "CAC/LTV real diverge ≥50% del estimado en Phase 0",
      "implication": "El supuesto económico de Phase 0 era incorrecto. Candidato a re-trigger de Phase 1 (oferta) — heredado de Phase 1 §11.",
      "auto_action": "flag phase_5 ltv_cac_below_3"
    },
    {
      "id": "CONVERSION-001",
      "applicable_phase": "phase-4.3",
      "condition": "conversion_trend == falling AND conversion_rate drop >= 30% sustained 14d (vs trailing baseline)",
      "severity": "alert",
      "signal": "La conversión a venta cae ≥30% sostenido — el punto ciego de negocio que faltaba (advisor crítico)",
      "implication": "La oferta dejó de convertir. Phase 5 debe re-triggerar Phase 1 (nueva oferta). Sin esta regla, la métrica de negocio más importante no dispara nada.",
      "auto_action": "flag phase_5 conversion_falling_30pct"
    },
    {
      "id": "CAC-TREND-001",
      "applicable_phase": "phase-4.2",
      "condition": "cac sube >= 40% vs el snapshot ANTERIOR (tendencia mes-a-mes, distinto de ECONOMICS-LIVE-002 que compara vs baseline)",
      "severity": "warning",
      "signal": "CAC se dispara en tendencia aunque siga bajo el baseline",
      "implication": "El costo de adquisición empeora rápido. Phase 5 arregla targeting (Phase 3, misma versión) antes de tocar la oferta. Ej: baseline $10, snapshot previo $6, ahora $8.4 (+40%) — sigue < $10 pero subiendo.",
      "auto_action": "flag phase_5 cac_up_40pct"
    },
    {
      "id": "FOUNDATION-DRIFT-001",
      "applicable_phase": "phase-4.3",
      "condition": "decaimiento simultáneo en TODOS los avatars activos del proyecto, O cambio material en los datos de mercado de la Foundation, O competitive shift tier-1",
      "severity": "alert",
      "signal": "Los cimientos compartidos (mercado/segmento) se movieron — no es un avatar, es el proyecto",
      "implication": "Phase 5 re-triggerea Foundation (Phase 0.1–0.2.5) a nivel proyecto. NO confundir con un avatar individual que cae (eso es nivel avatar). Reemplaza el viejo 'refresh cada 12 meses' por evidencia real.",
      "auto_action": "flag phase_5 foundation_drift"
    },
    {
      "id": "ANOMALY-001",
      "applicable_phase": "phase-4.3",
      "condition": "una métrica clave se mueve materialmente (ej: revenue/cliente, retención, mix de awareness) pero NINGUNA bandera conocida del registro encaja",
      "severity": "warning",
      "signal": "Movimiento real sin explicación en el catálogo de banderas conocidas",
      "implication": "Phase 5 NO debe forzar esto en una bandera existente. Emitir unexplained_anomaly obliga a la rama de diagnóstico abierto (Phase 5 §5.1.b): razonar la causa raíz desde datos crudos + historia + lecciones, y si se valida, promoverla al registro como bandera nueva. Esto es lo que hace que el sistema PIENSE en vez de solo mirar 8 banderas.",
      "auto_action": "flag phase_5 unexplained_anomaly (con el detalle de qué métrica se movió)"
    },
    {
      "id": "FATIGUE-001",
      "applicable_phase": "phase-4.3",
      "condition": "ctr_trend == falling AND ctr drop >= 30% sustained 14d",
      "severity": "warning",
      "signal": "Fatiga de contenido/hook (CTR cae ≥30% sostenido)",
      "implication": "Hook fatigue o cambio de awareness. Phase 5 debe re-triggerar Phase 2 (contenido/hooks nuevos). En social/video corto, `completion_rate` (per_pillar) es el indicador LÍDER y su caída precede a la del CTR — vigilarlo da aviso temprano antes de que esta regla dispare.",
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
    },
    {
      "id": "AIO-TRAFFIC-001",
      "applicable_phase": "phase-4.3",
      "condition": "impresiones estables AND CTR/clics de query informacional cayendo AND AI Overview presente en SERP",
      "severity": "warning",
      "signal": "Decaimiento de tráfico zero-click: la respuesta de IA en el SERP captura el clic de la query informacional aunque el ranking/impresiones se sostengan",
      "implication": "No es fatiga de contenido ni caída de ranking — es un shift de SERP-feature (AI Overview). Phase 5 mueve el mix de contenido hacia intención transaccional + construye autoridad Top-10 para alimentar (no perder ante) AI Overview, en lugar de forzar la causa a una bandera de ranking. Sin esta regla, una caída de tráfico informacional orgánico por razón ajena al ranking cae a unexplained_anomaly.",
      "auto_action": "flag phase_5 zero_click_informational_decay"
    },
    {
      "id": "PAID-SEARCH-WASTE-001",
      "applicable_phase": "phase-4.3",
      "condition": "en per_search_term existe >= 1 término con category ∈ {non_converting, out_of_model} AND spend_usd > 0",
      "severity": "warning",
      "signal": "Presupuesto de búsqueda pagada quemándose en términos que no convierten o quedan fuera del modelo de negocio",
      "implication": "Desperdicio que el funnel agregado oculta. Phase 5 acciona depuración de términos/negativos en Phase 3 (mismo targeting, misma versión activa) antes de tocar oferta o contenido. La bandera es de origen métrico Phase 4 y queda declarada producer-bound (regla productor-binding de §5).",
      "auto_action": "flag phase_5 paid_search_waste (con el detalle de los términos out_of_model/non_converting y su spend_usd)"
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
| D4 | LTV:CAC gate con datos reales | ECONOMICS-LIVE-001 valida ECONOMICS-001 de Phase 0. El umbral **NO es `< 3.0` plano** sino la **tabla por modelo de negocio** (§4.2 [Context-Adjusted Threshold]); bajo el umbral del modelo y tras razonar el contexto → red → Phase 5 actúa. *(El flag canónico sigue siendo `ltv_cac_below_3` — la clave del registro no cambia; el corpus C1 respalda "CPA < margen", viabilidad atada al margen real, no a un ratio SaaS fijo.)* |
| D5 | `phase_5_flags` como contrato | Conjunto ABIERTO (jsonb) cuyo catálogo vive en el registro canónico (`Overall_WF.md`). Phase 4 es el productor de las banderas métricas; cada una con su signal rule (productor-binding, mata el orphan M3). |
| D6 | Matar avatars perdedores | AVATAR-PERF-001 es feature, no bug: la orquestación paralela permite pausar avatars débiles y concentrar presupuesto. |
| D7 | Punto ciego de conversión (fix crítico) | CONVERSION-001 emite `conversion_falling_30pct` → Phase 1. Antes la métrica de negocio más importante no disparaba nada. |
| D8 | Tendencia ≠ baseline (fix M3) | CAC-TREND-001 (mes-a-mes, emite `cac_up_40pct`) es distinto de ECONOMICS-LIVE-002 (vs baseline). Ambos coexisten. |
| D9 | Foundation drift por evidencia, no calendario | FOUNDATION-DRIFT-001 (decaimiento cross-avatar / mercado / competencia) emite `foundation_drift`. Reemplaza el viejo refresh de 12 meses. |
| D10 | Pensar cuando nada encaja | ANOMALY-001 emite `unexplained_anomaly` cuando una métrica se mueve sin bandera conocida → fuerza el diagnóstico abierto de Phase 5 (§5.1.b). El sistema razona, no solo mira un catálogo. |

---

## 11. Apéndice — checklist operacional V1

```
[ ] G-Phase-4-PRE: 4 checks (publish_plan firmado, strategy_id activo, attribution_window cerrada, tracking verificado)
[ ] 4.1 — metrics_snapshot.raw por pilar+canal con avatar_id
[ ] 4.1 — negative_quality_leads_excluded contado antes de conversion_rate
[ ] 4.1 — (social) completion_rate / avg_watch_time_s / saves / shares poblados donde aplique (completion_rate = indicador líder de fatiga)
[ ] 4.1 — (pago) per_search_term clasificado por category; non_converting/out_of_model con spend>0 marcados
[ ] 4.2 — unit economics (CAC, LTV, ratio, payback) vs baseline; economics_health clasificado
[ ] 4.2 — funnel por awareness con drop_off_stage
[ ] 4.3 — strategies.results_summary escrito con phase_5_flags (conjunto abierto)
[ ] 4.3 — conversión evaluada (CONVERSION-001) — no dejar el punto ciego de negocio
[ ] 4.3 — comparación cross-avatar: un avatar cae → AVATAR-PERF-001; todos caen → FOUNDATION-DRIFT-001
[ ] 4.3 — tráfico informacional zero-click evaluado (AIO-TRAFFIC-001) si hay AI Overview en SERP
[ ] 4.3 — desperdicio de búsqueda pagada evaluado (PAID-SEARCH-WASTE-001)
[ ] 4.3 — si una métrica se movió sin bandera conocida → emitir unexplained_anomaly (ANOMALY-001)
[ ] metrics_snapshot.json anclado a strategy_id + avatar_id
[ ] phase_5_handoff con recommended_action_hint
[ ] Signal rules evaluadas: ninguna alert sin flag a Phase 5
[ ] operator_signoff: true
```
