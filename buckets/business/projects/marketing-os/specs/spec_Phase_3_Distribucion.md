# Phase 3 — Publicar / Distribuir

**Project**: business/marketing-os
**Phase ID**: phase-3
**Status**: spec drafted v1.0
**Last updated**: 2026-06-06
**Implementation correction:** This methodology targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase). Persist outputs in `project_phase_artifacts` (`phase = 'distribution'`), decisions in `project_decisions`, learnings in `project_lessons`. Every artifact, decision and lesson of this phase carries `strategy_id` + `avatar_id` (the strategy it belongs to). n8n / external schedulers are future-only; the MVP produces the publish plan + tracking config, the operator (or a thin scheduler) executes.

**Reference**: `Overall_WF.md` §"Strategy Lifecycle" + §"Canonical Project Hierarchy". `spec_Phase_2_Contenido.md` §10 (`phase_3_handoff`).

---

## 0. Contexto y propósito

Phase 3 toma los assets aprobados de Phase 2 y los pone en el mundo: calendario de publicación, configuración de tracking (UTMs, pixel events, conversion events), exclusion lists de negative personas, y targeting por canal. **No crea contenido** — ejecuta y mide la salida del contenido ya creado.

**Pertenencia a una Estrategia (D-009/D-010):** Phase 3 corre **dentro de una estrategia**. En `separate_strategies` (default) cada avatar tiene su propia Phase 3 (su propio calendario, sus propias campañas, su propio tracking). En `unified_C_*`, una Phase 3 distribuye el plan único diferenciando por `language_pack`/avatar dentro de las campañas. El `publish_plan.json` declara `linked_to.strategy_id` + `strategy_version`.

**Output canónico**: `publish_plan.json` (calendario + campañas + tracking config) + `tracking_manifest.json` (el contrato que Phase 4 consume para medir).

**Spine operacional**:
- Drive Big School: cada canal ejecuta su función (SEO captura, RRSS amplifica, email convierte, ads escalan) — heredado de la lookup `channel_function` de Phase 2.2.
- Permission marketing (Godin): email solo a opted-in; orgánico antes que interrupción.
- Tracking-first: nada se publica sin UTM + conversion event definido — sin esto Phase 4 no puede atribuir resultados a la estrategia.

---

## 1. Estructura: 4 sub-pasos

| Sub-paso | Output | Estimado V1 | V1 | V2 |
|---|---|---|---|---|
| 3.1 — Tracking setup | `tracking_manifest.json` | 1–2 h | Manual (operador configura UTM + pixel + conversion events) | Sub-workflow genera UTMs + valida pixel |
| 3.2 — Exclusion lists + targeting | bloque `targeting` | 1 h | Manual desde `negative_personas` + ICP | Auto-sync a plataformas vía API |
| 3.3 — Publishing calendar | `publish_plan.calendar[]` | 1–2 h | Operador agenda desde `publishing_calendar_skeleton` | Scheduler (n8n/cron) publica |
| 3.4 — Go-live checklist | `publish_plan.go_live` | 30 min | Manual irreducible (gate humano antes de publicar) | Manual siempre |

---

## 2. Pre-condición — Gate de entrada G-Phase-3-PRE

Phase 3 NO arranca a menos que se cumplan:

1. ✅ `content_plan.json` existe con `metadata.operator_signoff: true` y `metadata.phase_3_ready: true`
2. ✅ `content_plan.linked_to.strategy_id` poblado y la `strategies` row está en `status = 'active'`
3. ✅ `content_plan.phase_3_handoff` completo: `tracking_requirements`, `exclusion_lists_needed`, `audience_targeting_per_channel`, `publishing_calendar_skeleton` (heredado de HANDOFF-001 de Phase 2)
4. ✅ `negative_filter_report.assets_blocked_count == 0` (o cada bloqueo con `decision_record` override) — no se publica contenido que apele al anti-target
5. ✅ Todos los assets referenciados en el calendario existen en `content_assets/` (paths reales, no placeholders)

---

## 3. Sub-paso 3.1 — Tracking setup

### Propósito
Hacer cada pieza atribuible. Sin tracking consistente, Phase 4 mide ruido y Phase 5 optimiza a ciegas.

### Output: `tracking_manifest.json`

```json
{
  "linked_to": { "strategy_id": "strategy_uuid", "strategy_version": 1, "plan_id": "plan_v1_YYYYMMDD" },
  "utm_scheme": {
    "per_pillar": { "PILLAR_A": "utm_campaign=pillar_a_{slug}&utm_source={channel}&utm_medium={format}" },
    "per_avatar": { "avatar_1": "utm_content={avatar_slug}" }
  },
  "pixel_events": ["page_view", "scroll_50", "cta_click", "lead_form_submit"],
  "conversion_event": {
    "definition": "lead_form_submit con email válido | purchase | demo_booked",
    "value_usd": 0,
    "attribution_window_days": 7
  },
  "channels_instrumented": [
    { "channel": "blog", "tracking_method": "GA4 + UTM", "verified": false }
  ]
}
```

### Reglas duras
- Cada canal del calendario tiene `tracking_method` + `verified` (un canal sin verificar bloquea su publicación)
- `conversion_event.definition` no puede ser vago ("engagement"); debe ser un evento medible
- El `utm_scheme.per_avatar` es obligatorio si la estrategia cubre >1 avatar (atribución por avatar — sin esto Phase 4/5 no puede comparar avatars)

### Gate G-Phase-3.1
- `tracking_manifest.json` poblado, todos los canales con `verified: true` antes de go-live

---

## 4. Sub-paso 3.2 — Exclusion lists + targeting

### Propósito
Configurar a quién SÍ y a quién NO se le muestra el contenido pago, honrando `negative_personas` (Phase 0.3) y el ICP (Phase 0.2.5).

### Output: bloque `targeting` dentro de `publish_plan.json`

```json
{
  "exclusion_lists": [
    { "negative_persona_id": "neg_1", "platform": "Meta", "list_name": "negative_neg_1_excl", "synced": false }
  ],
  "audience_per_channel": {
    "Meta": { "demand_type": "generate", "definition": "ICP B2C_cluster: behavioral_signals + interests; exclude exclusion_lists" },
    "LinkedIn": { "demand_type": "generate", "definition": "ICP B2B_account: industry + company_size + buying_stage; exclude deal_breakers" },
    "Google Ads": { "demand_type": "capture", "definition": "keywords transactional+comparative (Phase 0.2); negative_keywords desde negative_personas" }
  }
}
```

### Reglas duras
- Cada `negative_persona` con `action_when_detected ∈ {auto-disqualify}` produce una exclusion list en cada plataforma paga usada
- En estrategias multi-avatar separadas: el targeting de una estrategia NO debe solaparse con el avatar de otra estrategia activa (evita canibalización entre avatars del mismo proyecto) — DISTRIB-002
- **`demand_type` por canal obligatorio** (G1, aprobado vía FLAG-1) — cada entrada de `audience_per_channel` declara `demand_type ∈ {capture, generate, mixed}`: los canales de **demanda capturada** (search/Google Ads — el deseo ya existe, se intercepta intención) convierten MUY distinto a los de **demanda generada** (social/Meta/LinkedIn — se crea el deseo desde cero). Comparar sus CVR directamente es un error: este campo lo previene y hace legible la selección de canal y el flag `cac_up_40pct` aguas abajo. Hereda el `strategies.demand_type` de la estrategia (FLAG-1) y lo desglosa por canal cuando el mix es mezclado *(Cursos 1, 2, 5)*

### Gate G-Phase-3.2
- Exclusion lists definidas para cada negative_persona auto-disqualify
- Targeting por canal poblado citando ICP

---

## 5. Sub-paso 3.3 — Publishing calendar

### Propósito
Convertir el `publishing_calendar_skeleton` de Phase 2 en un calendario fechado real, respetando frecuencias `frequency_v1` por pilar y el ratio Vaynerchuk (no quemar el feed).

### Output: `publish_plan.calendar[]`

```json
[
  {
    "scheduled_for": "ISO date",
    "channel": "blog",
    "pillar_id": "PILLAR_A",
    "asset_id": "asset_pillar_A_001",
    "avatar_id": "avatar_1",
    "content_type": "value | cta | hybrid",
    "format": "9:16 | 16:9 | 1:1 | article | email",
    "entry_type": "one_off_post | automated_sequence",
    "derived_from_asset_id": null,
    "repurpose_format": null,
    "utm_resolved": "utm_campaign=pillar_a_x&utm_source=blog&utm_medium=article&utm_content=estudiante",
    "status": "scheduled | published | failed"
  },
  {
    "scheduled_for": "ISO date (trigger date or sequence start)",
    "channel": "email",
    "pillar_id": "PILLAR_C",
    "asset_id": "asset_seq_onboarding_001",
    "avatar_id": "avatar_1",
    "content_type": "value | cta | hybrid",
    "format": "email",
    "entry_type": "automated_sequence",
    "sequence_kind": "onboarding | nurturing | sales | evergreen_reimpact",
    "trigger": "lead_form_submit | tag_added | date | manual",
    "length": 5,
    "urgency_window": "bajo: 15min-1h | medio: 48h | alto: 3-7 días",
    "utm_resolved": "utm_campaign=seq_onboarding&utm_source=email&utm_medium=email&utm_content=estudiante",
    "status": "scheduled | published | failed"
  }
]
```

### Reglas duras
- El ratio value:cta objetivo por canal (Phase 2.4, default 3:1 ajustable por fatiga) se verifica **a nivel calendario por canal orgánico** (DISTRIB-001) — no solo a nivel plan
- Cada entrada con `utm_resolved` derivado del `tracking_manifest` (no UTMs ad-hoc)
- `frequency_v1` por pilar respetada (±1 pieza/semana)
- **`format` (aspect-ratio) obligatorio por entrada** — `9:16 | 16:9 | 1:1 | article | email`. Es una decisión de distribución, no de contenido: declara cómo sale el mismo asset en cada plataforma. Sin `format` el calendario no especifica el formato de salida (un asset puede ir 16:9 en YouTube y 9:16 en Reels) *(Curso 7)*
- **Reutilización cross-platform (1 asset madre → N filas):** un asset aprobado de Phase 2 puede generar múltiples entradas del calendario vía `derived_from_asset_id` (apunta al `asset_id` madre) + `repurpose_format`. Misma madre, distinto `channel` + `format` + `utm_resolved`. Refleja "video largo → N piezas cortas". **Cada formato derivado cuenta como una entrada propia para DISTRIB-001** (el ratio value:cta se cuenta sobre filas del calendario, no sobre assets madre) *(Curso 7 §6.6)*
- **Secuencias de email schedulables:** cada entrada declara `entry_type ∈ {one_off_post, automated_sequence}`. El spine "email convierte" se honra agendando secuencias, no solo posts sueltos. Para `entry_type = automated_sequence` (solo canal email) son obligatorios `sequence_kind ∈ {onboarding, nurturing, sales, evergreen_reimpact}`, `trigger` (qué dispara la secuencia) y `length` (nº de emails). La ventana de urgencia por ticket viaja como metadata (`urgency_window`: bajo 15min-1h, medio 48h, alto 3-7 días) *(Curso 6 §2.2)*

### Gate G-Phase-3.3
- Calendario fechado para ≥4 semanas (1 ciclo), ratio Vaynerchuk verificado por canal

---

## 6. Sub-paso 3.4 — Go-live checklist

### Propósito
Gate humano irreducible antes de publicar. Paralelo a Phase 1.3 (risk reversal) y Phase 2.0 (brand voice): la decisión de "esto sale al mundo" es del operador.

### Output: `publish_plan.go_live`

```json
{
  "tracking_verified": true,
  "exclusion_lists_synced": true,
  "negative_filter_clear": true,
  "first_week_assets_ready": true,
  "operator_signoff": true,
  "go_live_at": "ISO date"
}
```

### V1/V2/V3
| Versión | Quién decide |
|---|---|
| V1, V2, V3 | **Operador siempre** — publicar es decisión humana |

---

## 7. Output canónico de Phase 3: `publish_plan.json`

```json
{
  "plan_id": "publish_v1_YYYYMMDD",
  "linked_to": {
    "strategy_id": "strategy_uuid",
    "strategy_version": 1,
    "content_plan_id": "plan_v1_YYYYMMDD",
    "primary_avatar_id": "avatar_1",
    "covers_avatars": ["avatar_1"]
  },
  "tracking_manifest_path": "content_assets/_meta/tracking_manifest.json",
  "targeting": { "...del 3.2..." },
  "calendar": [ "...del 3.3..." ],
  "go_live": { "...del 3.4..." },
  "phase_4_handoff": {
    "conversion_event": "...del tracking_manifest...",
    "kpis_to_track_per_pillar": { "PILLAR_A": ["organic_traffic", "ranking_position"] },
    "economics_baseline": { "target_cac_usd": 0, "expected_ltv_usd": 0, "source": "product_brief_v2.economics" },
    "measurement_start": "ISO date"
  },
  "signal_rules_triggered": [],
  "metadata": { "hours_invested": 0, "usd_invested": 0, "completed_at": "ISO date", "operator_signoff": true }
}
```

El `phase_4_handoff.economics_baseline` traslada el `target_cac_usd` / `expected_ltv_usd` de Phase 0 para que Phase 4 los compare contra datos reales (cierra el loop ECONOMICS-001).

---

## 8. Gate global G-Phase-3
- Sub-gates 3.1–3.4 cerrados
- `publish_plan.json` consolidado, anclado a `strategy_id` activo
- `tracking_manifest` con todos los canales `verified: true`
- Exclusion lists sincronizadas para cada negative_persona auto-disqualify
- Calendario ≥4 semanas con ratio Vaynerchuk verificado
- `phase_4_handoff` poblado (conversion event + KPIs + economics baseline)
- `operator_signoff: true`

---

## 9. Signal rules de Phase 3

```json
{
  "rules": [
    {
      "id": "DISTRIB-001",
      "applicable_phase": "phase-3.3",
      "condition": "for any organic channel in calendar: value:cta ratio < ratio_objetivo_del_canal (default 3:1 [Context-Adjusted Threshold], ajustado por fatiga real de Phase 4 — mismo objetivo que VAYNER-001). El ratio se cuenta sobre filas del calendario (cada `format` derivado vía `derived_from_asset_id`/`repurpose_format` es una fila propia), no sobre assets madre",
      "severity": "warning",
      "signal": "Calendario rompe el ratio jab/right-hook objetivo de ese canal",
      "implication": "El feed se quema si hay demasiado CTA — umbral por canal, no 3:1 universal. Reordenar el calendario con más piezas value.",
      "auto_action": "warn before go-live"
    },
    {
      "id": "DISTRIB-002",
      "applicable_phase": "phase-3.2",
      "condition": "targeting of strategy overlaps with avatar of another active strategy in same project",
      "severity": "warning",
      "signal": "Solapamiento de targeting entre estrategias del mismo proyecto",
      "implication": "Dos estrategias de avatars distintos compiten por la misma audiencia (canibalización + CAC inflado). Segmentar o unificar.",
      "auto_action": "require decision_record"
    },
    {
      "id": "TRACKING-001",
      "applicable_phase": "phase-3.1",
      "condition": "any channel in calendar with verified == false at go-live",
      "severity": "alert",
      "signal": "Canal sin tracking verificado al momento de publicar",
      "implication": "Phase 4 no podrá atribuir resultados de ese canal a la estrategia. No publicar hasta verificar.",
      "auto_action": "block go-live for that channel"
    }
  ]
}
```

---

## 10. Re-trigger de Phase 3
- Phase 2 hace re-trigger (assets nuevos → calendario nuevo)
- Phase 5 emite Strategy #N+1 → Phase 3 se re-ejecuta para la nueva versión (calendario + tracking nuevos)
- Operador agrega un canal nuevo no instrumentado

Cada re-trigger queda como `decision_record` con `strategy_id`.

---

## 11. Decisiones cerradas en Phase 3 v1.0

| # | Decisión | Resolución |
|---|---|---|
| D1 | ¿Phase 3 crea contenido? | **No.** Solo distribuye + instrumenta. Contenido es Phase 2. |
| D2 | Tracking-first | Nada se publica sin UTM + conversion event definido (TRACKING-001 bloquea). |
| D3 | Go-live es gate humano | Operador siempre firma `go_live`, en todas las versiones. |
| D4 | Pertenencia a estrategia | `publish_plan` ancla a `strategy_id`; en separate_strategies cada avatar tiene su propia Phase 3. |
| D5 | Economics baseline al handoff | `target_cac_usd`/`expected_ltv_usd` de Phase 0 viajan a Phase 4 para validar ECONOMICS-001 con datos reales. |

---

## 12. Apéndice — checklist operacional V1

```
[ ] G-Phase-3-PRE: 5 checks (content_plan listo, strategy_id activo, phase_3_handoff completo, negative_filter clear, assets reales)
[ ] 3.1 — tracking_manifest.json con conversion_event medible + UTM por pilar (+ por avatar si multi-avatar)
[ ] 3.1 — todos los canales verified: true
[ ] 3.2 — exclusion lists por negative_persona auto-disqualify
[ ] 3.2 — targeting por canal citando ICP
[ ] 3.2 — demand_type (capture|generate|mixed) declarado por canal en audience_per_channel (G1/FLAG-1)
[ ] 3.3 — calendario ≥4 semanas, UTM resuelto por entrada
[ ] 3.3 — format (9:16|16:9|1:1|article|email) declarado por entrada
[ ] 3.3 — entry_type por entrada; automated_sequence con sequence_kind + trigger + length
[ ] 3.3 — repurposing cross-platform (derived_from_asset_id) si 1 asset madre → N formatos
[ ] 3.3 — ratio Vaynerchuk verificado por canal orgánico, contado sobre filas del calendario (DISTRIB-001)
[ ] 3.4 — go_live con operator_signoff
[ ] phase_4_handoff: conversion event + KPIs + economics_baseline
[ ] publish_plan.json anclado a strategy_id + strategy_version
[ ] hours/usd invertidos cuantificados
```
