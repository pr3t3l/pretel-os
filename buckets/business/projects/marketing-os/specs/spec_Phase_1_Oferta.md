# Phase 1 — Oferta

**Project**: business/marketing-os
**Phase ID**: phase-1
**Status**: spec drafted v1.5
**Last updated**: 2026-06-01
**Implementation correction:** This methodology now targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase), not a Python/FastMCP module inside `pretel-os`. Persist outputs in `project_phase_artifacts`, decisions in `project_decisions`, and learnings in `project_lessons`. FastAPI is future-only for heavy jobs, complex agents, or public API needs.

**Audit references**:
- Phase 0 v1.5 (Categoría A integrada) — outputs consumidos en G-Phase-1-PRE
- Auditoría externa Phase 1 (2026-05-10) — 3 regresiones + bug matemático + 6 mediums integrados
- Mejoras operador 2026-05-10 — tabla ratio derivada, margin gate, sub-workflows, condición 5 multi-avatar, escala 1-10000
- Auditoría alineación Phase 0 ↔ Phase 1 (2026-05-10) — ISSUE-A1 (G-PRE check 7 a "TODOS los avatars"), ISSUE-A2 (sub-paso 1.4.0 language_packs), ISSUE-A3 (comparable obligatorio en core_deliverable.value_rationale), ISSUE-A4 (urgency.aligned_with_trigger)

---

## 0. Contexto y propósito

Phase 1 convierte el conocimiento del avatar (Phase 0) en una oferta tan asimétrica en valor percibido vs precio que rechazarla se sienta estúpido. Output canónico: `offer_spec.json` + `offer_statement.md` (uno por avatar o variante, según estrategia multi-avatar).

**Spine teórico**:
- Hormozi $100M Offers (Value Equation, Stack, Risk Reversal, Urgency)
- Christensen JTBD (Dream Outcome viene del job, no del producto)
- Christensen Forces of Progress (oferta ataca anxiety + habit, no solo amplifica push + pull)
- Drive Big School: 3-traits check (relevante/diferente/creíble) como auditoría final, no como spine

**Principios operacionales**:
- Dream Outcome se ancla en JTBD, no en pain points (oferta aspiracional, no defensiva)
- Bonuses mapean explícitamente a Forces of Progress, no solo a "objection_n"
- Risk reversal y urgency 100% manuales en todas las versiones (decisión ética irreductible)
- Ambos gates obligatorios: perceived_value_ratio + gross_margin_pct
- Composite value score con escala 1–10000 (más legible que 0.01–100)

---

## 1. Estructura: 4 sub-pasos + 2 sub-workflows transversales

| Sub-paso | Output | Estimado V1 | Sub-workflow asistente |
|---|---|---|---|
| 1.1 — Dream Outcome + Value Equation | `value_equation.json` (uno por avatar) | 1–2 h/avatar | `value-equation-optimizer` |
| 1.2 — Offer Stack | `offer_stack.json` | 2–3 h | `offer-stack-builder` |
| 1.3 — Risk Reversal + Urgency + Displacement | `risk_urgency.json` | 1 h | Manual 100% |
| 1.4 — Pricing + Naming + Statement | `offer_statement.md` + pricing block | 1–2 h | Asistido por LLM |
| **Transversal** — Multi-avatar strategy | `multi_avatar_decision.json` (después de 1.1) | 30 min | Algoritmo determinístico |

---

## 2. Pre-condición — Gate de entrada G-Phase-1-PRE

Phase 1 NO arranca a menos que se cumplan los **10 checks** (vs 4 anteriores). Si cualquier check falla, el handler responde `{status: 'blocked', reason: '...'}`.

**Checks de Phase 0 cierre:**
1. ✅ `product_brief_v2.json` existe y `operator_signoff: true`
2. ✅ `demand.validation_status` ∈ {green, yellow}. Si es red → STOP, volver a Phase 0
3. ✅ `evidence_findings.hypotheses_refuted` tiene ≥1 entrada (EVIDENCE-001)
4. ✅ `evidence_findings.hypotheses_refuted_critical_count < 2` (EVIDENCE-002 — si ≥2 críticas refutadas → pivot, no refinamiento)
5. ✅ ECONOMICS-001 pasa: `expected_ltv_usd / target_cac_usd >= 3.0` (o `decision_record` justifica organic-only)

**Checks de artefactos Phase 0 v1.5:**
6. ✅ `icp.json` existe con bloque correspondiente al business_type poblado
7. ✅ **TODOS** los avatars en `product_brief_v2.avatars` tienen `forces_of_progress` completo (≥3 ongoing_pains, ≥3 triggers, ≥3 pull, ≥3 anxiety, ≥3 habit cada uno). Phase 0 G-0.3 ya lo exige; defensa en profundidad: el algoritmo multi-avatar transversal (sec 4) evalúa las 4 condiciones hard entre **todos** los avatars, y si alguno tiene forces parciales la decisión multi-avatar se contamina con datos faltantes.
8. ✅ Cada `buyer_persona` tiene `jobs_to_be_done` con ≥1 functional + ≥1 emotional job
9. ✅ `negative_personas.json` existe (≥1 o `decision_record` justificando `none`)
10. ✅ Si `business_context.business_type === "B2B"`: `dmu.json` poblado con champion + decision_maker + ≥1 influencer + ≥1 end_user

---

## 3. Sub-paso 1.1 — Dream Outcome + Value Equation

### Propósito
Cuantificar el valor percibido aplicando la Value Equation de Hormozi, anclando el Dream Outcome en JTBD del avatar (no en pain points).

### Convención de scoring (LOCKED — no se altera)

**Todos los ejes: 10 = óptimo, 1 = pésimo.**

| Eje | 10 significa | 1 significa |
|---|---|---|
| dream | Sueño aspiracional total | Beneficio marginal |
| likelihood | Certeza casi total | Apuesta a ciegas |
| time | Inmediato | Años de espera |
| effort | Cero esfuerzo / done-for-you total | Sacrificio enorme |

### Fórmula y escala

```
composite_value_score = dream × likelihood × time × effort
```

Sin división, sin /100. Rango: **1 a 10,000**. Más legible para el operador que la escala original 0.01–100.

**Thresholds operativos (LOCKED)**:

| Composite | Categoría | Acción |
|---|---|---|
| < 100 | Inaceptable | **Bloqueo duro**. Fricción ≥ beneficio. Rechazar, volver a 1.1 con `value-equation-optimizer`. |
| 100 – 1,000 | Débil | **Bloqueo blando**. Pasa solo con `decision_record` justificando + plan de optimización documentado. |
| 1,000 – 3,000 | Estándar operativo | **OK con flag**. Avanza pero registra como "oferta promedio" — primer candidato a iterar en Phase 5. |
| 3,000 – 6,000 | Sólida | Avanza sin flag. |
| > 6,000 | Excepcional (Hormozi-tier) | Avanza con tag `hormozi-tier` para reuso en otros productos como referencia. |

### Output: `value_equation.json` — uno por avatar

```json
{
  "avatar_id": "avatar_1",
  "dream_outcome": {
    "statement": "1 oración desde POV del avatar, aspiracional, anclada en JTBD",
    "jtbd_source": "JTB-1 (emotional_job + functional_job)",
    "pull_amplified": "pull_of_new_solution #2 del avatar",
    "evidence_path": "buyer_persona.jobs_to_be_done[0] + avatars[0].forces_of_progress.pull_of_new_solution",
    "score": 8,
    "score_rationale": "por qué 8 y no 10 — qué falta para ser un dream outcome de 10"
  },
  "likelihood_of_achievement": {
    "objections_addressed": ["objection_1 → cómo el producto la resuelve"],
    "anxieties_addressed": ["anxiety_1 → cómo el producto la calma"],
    "proof_assets_available": ["testimonios | demo | trial | garantía | track record"],
    "score": 6,
    "score_rationale": "qué evidencia falta para subir a 9-10"
  },
  "time_delay": {
    "current_time_to_outcome": "X días/semanas/horas",
    "reduction_levers": ["qué del producto/proceso acorta este tiempo"],
    "score": 7,
    "score_rationale": "por qué no instantáneo (10)"
  },
  "effort_sacrifice": {
    "what_avatar_must_do": ["pasos que el avatar debe ejecutar"],
    "what_avatar_must_give_up": ["tiempo, dinero, hábitos, identidad"],
    "done_for_you_levers": ["qué partes del proceso entregamos hechas"],
    "score": 7,
    "score_rationale": "por qué no cero esfuerzo (10)"
  },
  "composite_value_score": 2352,
  "weakest_axis": "likelihood",
  "phase_1_focus": "subir likelihood — diseñar el offer stack para atacar este eje",
  "category": "estandar_operativo | debil | solida | excepcional | inaceptable"
}
```

**Ancla crítica**: `dream_outcome.evidence_path` apunta a JTBD + pull, **no a pain points**. Pain = "me duele X" (defensivo). JTBD = "estoy tratando de lograr Y" (aspiracional). Hormozi siempre es aspiracional.

### Sub-workflow `value-equation-optimizer`

Skill registrado en pretel-os (`domain: marketing-offer`, `scope: project:business/marketing-os`).

**Algoritmo**:
```
1. Operador puntúa los 4 ejes (1-10, convención "10=óptimo")
2. Calcula composite = dream × likelihood × time × effort
3. Identifica weakest_axis
4. Sesgo Hormozi: propone reducir fricción del denominador ANTES que inflar promesa del numerador
   - Si time_score < 6: "¿qué del producto/proceso puede entregar resultado más rápido?"
   - Si effort_score < 6: "¿qué del producto puede ser done-for-you vs do-it-yourself?"
5. SOLO si denominador ya optimizado, sugiere aumentar numerador
   - Si likelihood < 6: testimonios, garantías, casos de éxito
   - Si dream < 6: reframe del outcome desde JTBD (no del producto)
6. Re-puntúa, recalcula composite
7. Si composite < 100 después de optimización → flag al operador con 3 opciones:
   - Subir precio significativamente (cambia ratio)
   - Pivotar el avatar (no es target real)
   - Pivotar el producto (no resuelve el job)
```

### Lectura previa pretel-os
- `product_brief_v2.json` completo (incluye JTBD, Forces of Progress, ICP)
- `best_practice_search(query="value equation hormozi offer", scope="project:business/marketing-os")`
- `lessons` con tags `['offer', 'value-equation', 'jtbd', 'dream-outcome']`

### Escrituras
- `decision_record` por la elección del `weakest_axis` y `phase_1_focus`
- `save_lesson` si la reducción del denominador desbloqueó algo no obvio

### Gate G-Phase-1.1
- Un `value_equation.json` por avatar
- Cada `score_rationale` cita ≥1 elemento del `product_brief_v2`
- `dream_outcome.jtbd_source` y `pull_amplified` poblados (no pain points)
- `weakest_axis` y `phase_1_focus` registrados como `decision_record`
- `composite_value_score >= 100` (o `decision_record` justificando bloqueo blando)

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + Claude asiste. Operador puntúa, Claude challenges con preguntas socráticas ("¿por qué likelihood 6 si no tienes testimonios?"). |
| V2 | Sub-workflow drafta scores desde JTBD + Forces of Progress, operador valida. |
| V3 | Auto + flag excepciones (scores muy fuera de distribución cross-producto). |

---

## 4. Transversal — Multi-avatar strategy (después de 1.1)

### Default invertido (D-009, 2026-06-06)

**La estrategia por-avatar es el DEFAULT, no la excepción.** El diferenciador central de Sandi es mantener N avatars en paralelo, cada uno con su propia estrategia (ver `Overall_WF.md` §"Core Differentiator"). Por eso este sub-paso **no decide si separar** — asume que cada avatar merece su propia estrategia — sino que decide si existe **evidencia suficiente para *unificar*** dos o más avatars bajo una sola oferta como **optimización** (ahorra trabajo cuando los avatars son casi idénticos).

En otras palabras: la carga de la prueba se invierte. Antes había que justificar separar; ahora hay que **justificar unificar**. Si la evidencia de unificación no se cumple, cada avatar sigue su propia estrategia (Phase 1→5 independiente), que es el comportamiento esperado del sistema.

### Propósito
Después de 1.1, evaluar — con evidencia de los `value_equation.json` ya producidos — si dos o más avatars comparten lo suficiente para **colapsar en una oferta unificada** (optimización), o si cada uno conserva su estrategia independiente (default).

### Criterio de UNIFICACIÓN (5 condiciones)

Estas condiciones miden si dos o más avatars son **lo bastante parecidos como para unificarlos** sin perder efectividad. Si NO se cumplen, el default (estrategia por-avatar) se mantiene.

**Condiciones HARD (deben cumplir las 4 para habilitar cualquier unificación):**
1. Mismo `functional_job` (JTBD) entre los avatars evaluados
2. Mismo `weakest_axis` en `value_equation.json`
3. ≥2 de 3 top anxieties compartidas entre avatars
4. ≥2 de 3 top habits compartidas entre avatars

**Condición SOFT (modifica la forma de la unificación, no la bloquea):**
5. ≥70% solapamiento de vocabulario en `buyer_persona.behaviors.online_communities` + `avatars.daily_routine`

### Regla de decisión

El default es `separate_strategies` (cada avatar su propia estrategia). Solo se *colapsa* hacia una forma unificada si la evidencia lo permite:

| Condiciones | Estrategia | Schema implicación |
|---|---|---|
| ≥2 hard ❌ | **Default — estrategias separadas**: cada avatar conserva su propio `offer_spec.json` y su propio loop Phase 1→5 | `multi_avatar_strategy: "separate_strategies"` |
| Exactamente 1 hard ❌ | **Unificación con avatar_specific bonuses**: 1 oferta, 1 stack base + 1-2 bonuses específicos por avatar para cerrar gap | `multi_avatar_strategy: "unified_C_avatar_specific_bonuses"` |
| 4 hard ✅ + soft ❌ | **Unificación con language_packs**: 1 oferta, 1 stack, 1 precio, N statements lingüísticos | `multi_avatar_strategy: "unified_C_language_packs"` |
| 4 hard ✅ + soft ✅ | **Unificación limpia**: 1 oferta, 1 stack, 1 statement | `multi_avatar_strategy: "unified_C_clean"` |
| 1 solo avatar | N/A | `multi_avatar_strategy: "single_avatar"` |

**Nota:** `separate_strategies` (default) reemplaza el antiguo `separate_offers`. El cambio no es solo de nombre: antes "separar" era el fallback indeseado cuando fallaban condiciones; ahora es el **comportamiento base esperado**, alineado con la orquestación paralela. Cada estrategia separada se persiste como un registro `strategies` independiente por avatar (ver `Overall_WF.md`).

### Output: `multi_avatar_decision.json`

```json
{
  "evaluated_avatars": ["avatar_1", "avatar_2", "avatar_3"],
  "hard_conditions": {
    "functional_job_match": true,
    "weakest_axis_match": true,
    "anxieties_overlap_count": 3,
    "habits_overlap_count": 2
  },
  "soft_condition": {
    "vocabulary_overlap_pct": 65,
    "passed": false
  },
  "decision": "unified_C_language_packs",
  "rationale": "4 hard cumplen, soft falla — mismo stack y precio, statements separados por registro lingüístico",
  "language_packs_required": ["avatar_1", "avatar_2", "avatar_3"]
}
```

### Aplicado a productos del proyecto

| Producto | Estrategia probable |
|---|---|
| Declassified Cases | `unified_C_clean` (1-2 avatars B2C que comparten functional_job) |
| Velas hija | `single_avatar` |
| Alfredo-as-freelance B2B | `separate_strategies` (DMU comparte functional_job pero weakest_axis muy distintos) |

### Escrituras
- `decision_record` con la elección de `multi_avatar_strategy` y rationale

### Nacimiento de la(s) Estrategia(s) (D-009/D-010)

El `multi_avatar_decision.json` determina **cuántas `strategies` rows se crean** (ver `Overall_WF.md` §"Strategy Lifecycle"). Es aquí — después de 1.1 y la decisión multi-avatar, antes de 1.2 — donde nace la entidad Estrategia:

- **`separate_strategies` (default):** se crea **una `strategies` row por avatar** (`version_number = 1`, `status = 'active'`, `covers_avatar_ids = [avatar_id]`). Los sub-pasos 1.2–1.4 corren N veces, cada corrida anclando su `offer_spec.json` a su `strategy_id`.
- **`unified_C_*`:** se crea **una sola `strategies` row** con `avatar_id` = primario y `covers_avatar_ids` = todos los avatars cubiertos. Los sub-pasos 1.2–1.4 corren una vez; el `offer_spec.json` se ancla a esa estrategia.
- **`single_avatar`:** una `strategies` row trivial.

Cada `strategies` row se persiste con `multi_avatar_strategy` espejando el del `offer_spec`. El `offer_spec.json` declara `linked_to.strategy_id` + `strategy_version` (consumido por Phase 2 check 14 y por toda la cadena Phase 3→5).

### Gate G-Phase-1-multi-avatar
- `multi_avatar_decision.json` existe y poblado
- `strategies` row(s) creada(s) según la regla de granularidad de arriba (`version_number=1`, `status='active'`)
- Si `separate_strategies` (default) → sub-pasos 1.2–1.4 se ejecutan N veces (una por avatar), cada corrida produce un `offer_spec.json` anclado a su `strategy_id` independiente
- Si cualquier variante de unified_C → sub-pasos 1.2–1.4 se ejecutan una sola vez con outputs adaptados, anclados a la estrategia unificada

---

## 5. Sub-paso 1.2 — Offer Stack

### Propósito
Construir el conjunto core + bonuses cuyo valor percibido stackeado cumpla **ambos** gates: ratio adecuado al business_type × purchase_type **Y** gross margin saludable según delivery_format.

### Tabla derivada de ratio_target (no hardcoded, calculada)

`ratio_target` se calcula desde `business_context`:

| business_type | purchase_type / sales_cycle | ratio_target | Justificación |
|---|---|---|---|
| B2B | reflexiva | 3× | Decisión racional, ROI demostrable en hoja de cálculo |
| B2B | mixta | 4× | Decisor racional pero champion con componente emocional |
| B2C | reflexiva | 5× | Punto medio Hormozi clásico |
| B2C | mixta | 6× | Compra con análisis pero gatillada emocionalmente |
| B2C | impulsiva | 7× | Compra emocional, necesita "victoria abrumadora" |
| Hybrid | cualquiera | 5× | Default conservador |

Override por `decision_record` permitido pero requiere justificación explícita.

### Margin gate (por delivery_format)

Segundo gate obligatorio simultáneo al ratio gate.

| `product.delivery_format` | `gross_margin_pct` mínimo | Justificación |
|---|---|---|
| digital_download | ≥ 70% | COGS marginal ≈ 0, fallar este margen es señal de pricing equivocado |
| service | ≥ 50% | Tiempo entregado es COGS real, margen menor que digital es aceptable |
| physical | ≥ 30% | COGS material + producción + envío; mínimo 30% para sustentar ops + marketing |
| hybrid (físico + digital) | ≥ 40% | Ponderado entre físico y digital |

Override por `decision_record` permitido (ej: producto loss-leader como entry point, justificado con LTV downstream).

### Output: `offer_stack.json`

```json
{
  "avatar_target": "avatar_1 | primary",
  "core_deliverable": {
    "name": "qué reciben efectivamente",
    "description": "1-2 oraciones",
    "perceived_value_usd": 0,
    "value_rationale": "por qué vale eso — comparable de mercado real, citado",
    "delivery_cost_to_us_usd": 0
  },
  "bonuses": [
    {
      "id": "bonus_1",
      "name": "nombre concreto y específico",
      "force_attacked": "pull_amplify | anxiety_reduce | habit_break | weakest_axis_boost",
      "specific_target": "anxiety #2 del avatar OR habit #1 OR pull #3 OR weakest_axis",
      "hormozi_category": "speed | done_for_you | identity | community_access | results_guarantee",
      "addresses_objection": "obj_id o null",
      "perceived_value_usd": 0,
      "value_rationale": "comparable de mercado real",
      "delivery_cost_to_us_usd": 0,
      "avatar_specific": null
    }
  ],
  "stack_economics": {
    "perceived_value_total_usd": 0,
    "delivery_cost_total_usd": 0,
    "price_point_usd": 0,
    "stack_to_price_ratio": 0,
    "stack_to_price_ratio_target": 5,
    "gross_margin_usd": 0,
    "gross_margin_pct": 0,
    "gross_margin_target_pct": 70,
    "ratio_gate_passed": true,
    "margin_gate_passed": true
  },
  "force_coverage": {
    "pulls_amplified": ["pull_1", "pull_3"],
    "anxieties_attacked": ["anx_1", "anx_2"],
    "habits_broken": ["habit_2"],
    "weakest_axis_boosted": "likelihood via testimonios + garantía"
  },
  "phase_2_handoff": {
    "objections_uncovered": ["obj_3 — Phase 2 lo resuelve con copy"],
    "anxieties_uncovered": [],
    "habits_unattacked": [],
    "pulls_underamplified": []
  }
}
```

### Reglas duras

- ≥3 bonuses, ≤7
- **≥1 bonus debe tener `force_attacked: anxiety_reduce`** (sin esto la oferta solo amplifica pull → no convierte indecisos)
- **≥1 bonus debe tener `force_attacked: habit_break`** (sin esto la oferta no rompe inercia → status quo gana)
- Cada bonus mapea a `specific_target` concreto (no "objection_n" abstracto)
- `value_rationale` con comparable de mercado real (citado), no inventado
- **`core_deliverable.value_rationale` debe citar ≥1 comparable de mercado real** (mismo estándar que bonuses; ISSUE-A3, audit 2026-05-10). Sin esto, `core_deliverable.perceived_value_usd` es la base inflable de toda la stack economics y el `ratio_gate` pasa engañosamente. Comparable preferido: precio listado de competidor de `competitive_landscape.pricing_tiers[]` que entrega un deliverable equivalente.
- Bonuses con `delivery_cost_to_us_usd > 30% de perceived_value_usd` se flaguean como ineficientes
- `avatar_specific` ≠ null solo si `multi_avatar_strategy === "unified_C_avatar_specific_bonuses"`

### Sub-workflow `offer-stack-builder`

Skill registrado en pretel-os.

**Inputs**:
- `business_context` (de Phase 0.1)
- `buyer_persona.economic_capacity` (de Phase 0.3)
- `competitive_landscape.pricing_tiers` (de Phase 0.4)
- `value_equation.json` (de Phase 1.1)
- `forces_of_progress` del avatar
- `core_deliverable` declarado por operador
- `price_point_target` declarado por operador
- `delivery_cost_per_unit` declarado por operador

**Algoritmo**:
```
1. Lookup ratio_target desde tabla (business_type × purchase_type)
2. Lookup gross_margin_target_pct desde tabla (delivery_format)
3. Calcula perceived_value_needed = price_point_target × ratio_target
4. Calcula gap = perceived_value_needed − core_deliverable.perceived_value_usd
5. Propone bonuses para llenar el gap, priorizando en orden:
   a. Bonus que ataca weakest_axis del value_equation
   b. Bonus anxiety_reduce (cubrir top anxiety no atendida)
   c. Bonus habit_break (cubrir top habit no atendida)
   d. Bonus con delivery_cost_to_us <= 5% de perceived_value (alto leverage)
   e. Categorización Hormozi: speed/DFY/identity/community/results
6. Para cada bonus propuesto, calcula impacto en margen
7. Itera hasta que AMBOS gates pasen:
   - stack_to_price_ratio >= ratio_target
   - gross_margin_pct >= gross_margin_target_pct
8. Si converge → "stack terminado"
9. Si no converge en 7 iteraciones → flag "trade-off requerido", operador elige:
   - Subir precio (cambia ratio favorablemente)
   - Bajar costo de bonuses (cambia margen favorablemente)
   - Aceptar margen menor con decision_record (ej: loss-leader strategy)
   - Reconsiderar core_deliverable.perceived_value_usd (puede estar subestimado)
```

### Lectura previa
- `value_equation.json` (sub-paso 1.1)
- `multi_avatar_decision.json` (sub-paso transversal)
- `product_brief_v2.pain_objections` + `forces_of_progress`
- `competitive_landscape.pricing_tiers`

### Escrituras
- `decision_record` por override de `ratio_target` o `gross_margin_target_pct`
- `decision_record` por cada bonus con `delivery_cost > 30% perceived_value`
- `save_lesson` si trade-off requerido reveló insight (ej: "perceived_value de core estaba subestimado")

### Gate G-Phase-1.2
- ≥3 bonuses, ≤7
- `ratio_gate_passed: true` Y `margin_gate_passed: true` (ambos)
- ≥1 bonus `anxiety_reduce`, ≥1 bonus `habit_break`
- Cada bonus con `force_attacked` y `specific_target` poblados
- `phase_2_handoff` documentado (cero uncovered es sospechoso — signal rule OFFER-001)
- Si margen falla y operador overrides → `decision_record` con LTV justification

---

## 6. Sub-paso 1.3 — Risk Reversal + Urgency + Displacement Framing

### Propósito
Bajar 3 barreras finales: miedo al riesgo (risk reversal ataca anxiety), inercia del momento (urgency genuina), inercia del status quo (displacement framing ataca habit).

### Output: `risk_urgency.json`

```json
{
  "risk_reversal": {
    "type": "money_back | conditional_money_back | results_based | better_than_money_back | none",
    "statement": "1-2 oraciones — la garantía exacta como aparecerá en el offer statement",
    "conditions": "qué tiene que cumplir el cliente",
    "honesty_check": "¿esta garantía es real y honraríamos? Si dudas, no la publiques",
    "anxieties_addressed": ["anxiety_id que esta garantía cierra"]
  },
  "urgency": {
    "type": "deadline | quantity | bonus_expiration | price_increase | none",
    "statement": "qué hace que actuar HOY sea distinto a actuar en 30 días",
    "is_genuine": true,
    "genuine_reason": "capacidad limitada | lanzamiento | ventana estacional | etc.",
    "aligned_with_trigger": "trigger_id de avatar.forces_of_progress.push_of_situation.triggers, o null si type=none",
    "alignment_rationale": "por qué la urgencia conecta con este trigger específico del avatar — defensa contra urgency fabricada"
  },
  "scarcity": {
    "type": "quantity_limited | access_limited | time_limited | none",
    "statement": "...",
    "is_genuine": true,
    "genuine_reason": "..."
  },
  "displacement_framing": {
    "habit_being_displaced": "habit_1 del avatar — el comportamiento status quo",
    "replacement_narrative": "1 oración que enmarca tu oferta como reemplazo del status quo, no como adición",
    "cost_of_continuing_current_path": "qué pierden si no cambian (usado en copy de Phase 2)",
    "habits_attacked_by_framing": ["habit_1", "habit_2"]
  }
}
```

### Reglas duras (honestidad arquitectural)

- `is_genuine: true` es campo obligatorio, NO booleano automático
- Si no puedes escribir `genuine_reason` real → el campo correspondiente va a `"none"`
- Urgencia/escasez fabricada **prohibida a nivel arquitectural**
- `decision_record` requerido si se usa urgency/scarcity activa
- `risk_reversal.type: "none"` permitido pero requiere `decision_record` justificando (productos digitales bajos generalmente sí pueden ofrecer garantía sin perderlo todo)
- **Displacement framing es obligatorio** (no opcional): si no hay habit que desplazar, la oferta es "agregar más" → no rompe status quo → no convierte indecisos

### Gate G-Phase-1.3
- Risk reversal `type` definido (puede ser "none" con justificación)
- Si urgency o scarcity ≠ "none" → `genuine_reason` poblado y verificable
- Si urgency ≠ "none" → `aligned_with_trigger` apunta a un `trigger_id` real de `avatar.forces_of_progress.push_of_situation.triggers` y `alignment_rationale` justifica la conexión (ISSUE-A4, audit 2026-05-10 — ancla evidencial contra urgency fabricada)
- `decision_record` registrado para cualquier urgency/scarcity activa
- `displacement_framing` poblado con `habit_being_displaced` y `replacement_narrative` (no skippable)
- `risk_reversal.anxieties_addressed` mapea a anxieties del avatar (no inventadas)

### V1/V2/V3
| Versión | Quién decide |
|---|---|
| V1, V2, V3 | **Manual siempre** — decisión ética irreductible |

---

## 7. Sub-paso 1.4 — Pricing + Naming + Statement

### Propósito
Cerrar la oferta en 3 piezas: precio justificado contra competidores Y value equation, nombre testeable, página única que alimenta TODO copy de Phase 2.

### Sub-paso 1.4.0 — Poblar `language_packs` (pre-requisito de los statements) (ISSUE-A2, audit 2026-05-10)

Si `multi_avatar_strategy ∈ {unified_C_language_packs, separate_strategies, unified_C_avatar_specific_bonuses}`, **antes** de escribir cualquier `offer_statement.md` el operador debe poblar `positioning_variants[]` con un `language_pack` por avatar.

**Fuentes (lectura)**:
- `buyer_persona.behaviors.online_communities` (frases reales del avatar en su hábitat)
- `avatars[avatar_id].daily_routine` (registro lingüístico contextual)
- `avatars[avatar_id].forces_of_progress.anxiety_about_new` y `habit_of_present` (vocabulario emocional)

**Reglas duras por language_pack**:
- ≥5 `key_phrases` (frases que el avatar SÍ usa, citables al copy de Phase 2)
- ≥3 `avoid_phrases` (frases que le suenan ajenas o lo desconectan)
- `vocabulary_register` declarado: `casual | profesional | técnico | emocional`

**Gate**: `positioning_variants[].language_pack` poblado para cada avatar declarado en `language_packs_required` del `multi_avatar_decision.json`. Sin esto, 1.4 no avanza a escribir statements.

**Por qué este paso explícito**: el `multi_avatar_decision.json` (post-1.1) declara `language_packs_required: [avatar_ids]` pero no los crea, y el output canónico (sec 8) los exige poblados. Sin sub-paso explícito, el operador V1 llega a escribir el statement y descubre que no sabe cuándo (o si) creó los packs.

### Output A: bloque `pricing` dentro de `offer_spec.json`

```json
{
  "price_point_usd": 0,
  "price_anchor": {
    "anchor_type": "dream_outcome_value | competitor_higher | total_stack | cost_of_inaction",
    "anchor_statement": "ej: 'el valor del stack es $480, lo entregamos por $97'"
  },
  "price_rationale": "por qué este precio. Cita value_equation, stack ratio, Y competitive_position.",
  "competitive_position": {
    "competitors_referenced": [
      {
        "name": "Competidor A",
        "price_usd": 67,
        "their_stack_estimate_usd": 150
      }
    ],
    "your_price_usd": 47,
    "your_tier_chosen": "below_market | at_market | premium",
    "tier_rationale": "ej: '5× stack value justifica premium aunque competidor está a $67'"
  },
  "tiers": [
    {
      "tier_name": "base | mid | premium",
      "price_usd": 0,
      "delta_value": "qué incluye más",
      "is_decoy": false
    }
  ],
  "tier_strategy": "single_tier | good_better_best | anchor_decoy"
}
```

### Reglas duras de pricing

- No competir por precio bajo (excepto en estrategia explícita de market entry con `decision_record`)
- Si `composite_value_score >= 3000`, el precio puede subir; bajar precio solo cuando `likelihood` (eje 2) es débil
- `good_better_best` aumenta ticket promedio ~30% para productos digitales (heurística, no ley)
- Validación cruzada `tier_strategy` ↔ `tiers.length`:
  - `single_tier` → `tiers.length === 1`
  - `good_better_best` → `tiers.length === 3`
  - `anchor_decoy` → `tiers.length >= 2`, primer tier marcado `is_decoy: true`

### Output B: `offer_statement.md` — página única (≤350 palabras)

Si `multi_avatar_strategy ∈ {unified_C_language_packs, separate_strategies}` → un statement por avatar/language_pack.

Estructura obligatoria:

```markdown
# [NOMBRE DE LA OFERTA]

## Para [avatar específico]

Si [problema/situación del avatar — del JTBD situation, no del pain]...

Te entrego [core deliverable + dream outcome aspiracional en 1 oración].

## Lo que recibes

- [Core deliverable] — valor $X
- Bonus 1: [nombre] — valor $X (ataca [anxiety/habit/pull])
- Bonus 2: [nombre] — valor $X
- Bonus 3: [nombre] — valor $X

**Valor total: $XXX**
**Tu inversión hoy: $XX**

## Reemplaza esto, no agregues más a tu vida

[displacement_framing.replacement_narrative — 1-2 oraciones que enmarcan la oferta como reemplazo del habit]

## Sin riesgo

[Risk reversal statement]

## [Si aplica:] Por qué actuar ahora

[Urgency/scarcity statement con genuine_reason — opcional]

## Próximo paso

[CTA específico, una sola acción]
```

### Reglas duras del statement

- ≤350 palabras (página única real)
- Lenguaje del avatar, no del producto (sale de `buyer_persona.behaviors.online_communities` — términos exactos)
- Si `language_pack` aplica: respetar `vocabulary_register`, usar `key_phrases`, evitar `avoid_phrases`
- Cero adjetivos vacíos ("revolucionario", "increíble", "único") — se reemplazan con specifics
- Dream outcome statement viene de JTBD, no de pain points (test: ¿la oración apela a aspiración o solo a alivio?)

### Output C: `offer_name`

**Test del nombre**: si el operador no puede pronunciarlo en una frase del tipo *"compré [nombre] y [outcome del JTBD]"*, el nombre falla.

### Gate G-Phase-1.4
- Si aplica multi-avatar: 1.4.0 cerrado (`positioning_variants[].language_pack` poblado para cada `language_packs_required`, ≥5 key_phrases y ≥3 avoid_phrases por pack)
- `pricing.price_rationale` cita value_equation, stack ratio Y competitive_position
- `competitive_position` poblado con análisis vs ≥1 competidor de Phase 0.4
- `tier_strategy` validado contra `tiers.length`
- `offer_statement.md` ≤350 palabras
- Si multi-avatar → un statement por avatar/language_pack
- Operador puede leer el statement en voz alta en ≤60 segundos sin tropezar
- Avatar test: ¿el avatar entendería esto sin diccionario? (si no, simplificar)
- Drive 3-traits check final: relevante (al avatar), diferente (vs competencia), creíble (sin claims vacíos)

---

## 8. Output canónico de Phase 1: `offer_spec.json`

```json
{
  "offer_id": "offer_v1_yyyymmdd",
  "linked_to": {
    "strategy_id": "strategy_uuid",
    "strategy_version": 1,
    "product_brief_path": "...",
    "primary_avatar_id": "avatar_1",
    "covers_avatars": ["avatar_1", "avatar_2", "avatar_3"]
  },
  "multi_avatar_strategy": "single_avatar | unified_C_clean | unified_C_language_packs | unified_C_avatar_specific_bonuses | separate_strategies",
  "value_equation_per_avatar": {
    "avatar_1": { "...del 1.1..." },
    "avatar_2": { "...del 1.1..." }
  },
  "stack": { "...del 1.2..." },
  "risk_urgency_displacement": { "...del 1.3..." },
  "pricing": { "...del 1.4..." },
  "name": "string",
  "positioning_variants": [
    {
      "avatar_id": "avatar_1",
      "angle": "1 oración del posicionamiento para este avatar",
      "language_pack": {
        "vocabulary_register": "casual | profesional | técnico | emocional",
        "key_phrases": ["frases que SÍ usa este avatar"],
        "avoid_phrases": ["frases que NO usa o le suenan ajenas"]
      }
    }
  ],
  "statement_paths_by_avatar": {
    "avatar_1": "offer_statement_avatar_1.md"
  },
  "signal_rules_triggered": [],
  "metadata": {
    "hours_invested": 0,
    "usd_invested": 0,
    "completed_at": "ISO date",
    "operator_signoff": true,
    "phase_2_handoff": {
      "objections_uncovered": [],
      "anxieties_uncovered": [],
      "habits_unattacked": [],
      "pulls_underamplified": []
    }
  }
}
```

---

## 9. Gate global G-Phase-1

Phase 1 se cierra cuando:
- Sub-gates 1.1, multi-avatar, 1.2, 1.3, 1.4 cerrados
- `offer_spec.json` consolidado
- `composite_value_score >= 100` para cada avatar (o `decision_record` justificando)
- Ambos economic gates pasados: ratio + margin (o `decision_record` con LTV justification)
- `phase_2_handoff` documentado (cero uncovered es sospechoso — OFFER-001 dispara warning)
- Operador firma `operator_signoff: true`

---

## 10. Capa transversal — Signal rules de Phase 1

Reglas heurísticas que disparan contra outputs estructurados. Viven como `best_practice_record` con `domain: signal-rule`, `applicable_phase: phase-1.X`.

```json
{
  "rules": [
    {
      "id": "VALUE-001",
      "applicable_phase": "phase-1.1",
      "condition": "composite_value_score < 100",
      "severity": "alert",
      "signal": "Oferta inaceptable — fricción supera beneficio",
      "implication": "Volver a 1.1 con sub-workflow value-equation-optimizer. NO avanzar a 1.2.",
      "auto_action": "block Phase 1.2 entry"
    },
    {
      "id": "VALUE-002",
      "applicable_phase": "phase-1.1",
      "condition": "composite_value_score >= 100 AND composite_value_score < 1000",
      "severity": "warning",
      "signal": "Oferta débil — pasa solo con plan de optimización",
      "implication": "Avanza pero requiere decision_record con plan documentado de iteración.",
      "auto_action": "require decision_record before Phase 1.2"
    },
    {
      "id": "STACK-001",
      "applicable_phase": "phase-1.2",
      "condition": "ratio_gate_passed == false OR margin_gate_passed == false",
      "severity": "alert",
      "signal": "Stack falla uno de los dos gates económicos",
      "implication": "Iterar con offer-stack-builder hasta que ambos pasen, o registrar decision_record justificando override.",
      "auto_action": "block Phase 1.3 entry"
    },
    {
      "id": "STACK-002",
      "applicable_phase": "phase-1.2",
      "condition": "anxieties_attacked.length == 0 OR habits_broken.length == 0",
      "severity": "alert",
      "signal": "Stack solo amplifica pull — no ataca anxiety ni habit",
      "implication": "Oferta convierte solo a quienes ya querían comprar. Indecisos no convierten. Agregar ≥1 bonus anxiety_reduce y ≥1 habit_break.",
      "auto_action": "block Phase 1.3 entry"
    },
    {
      "id": "OFFER-001",
      "applicable_phase": "phase-1.2",
      "condition": "phase_2_handoff.objections_uncovered.length == 0 AND avatar.objections_universal.length >= 3",
      "severity": "warning",
      "signal": "Stack cubre 100% de objeciones — improbable",
      "implication": "Posible que algunas se ignoraron en lugar de atacarse. Revisar.",
      "auto_action": "require operator_acknowledgment"
    },
    {
      "id": "PRICING-001",
      "applicable_phase": "phase-1.4",
      "condition": "competitive_position.competitors_referenced.length == 0",
      "severity": "warning",
      "signal": "Pricing sin análisis competitivo",
      "implication": "Phase 0.4 produjo pricing tiers — Phase 1.4 debe usarlos.",
      "auto_action": "require competitive_position population"
    }
  ]
}
```

---

## 11. Re-trigger de Phase 1

Phase 1 se re-ejecuta cuando:
- Phase 0 hace re-trigger (cambio de avatar → nueva oferta)
- Phase 5 detecta conversion rate cae ≥30% sostenido con mismo tráfico
- Operador prueba un avatar secundario nuevo no cubierto por la estrategia actual
- LTV/CAC real (Phase 4) diverge ≥50% del estimado en Phase 0 ECONOMICS-001

Cada re-trigger queda como `decision_record` con motivo + evidencia.

---

## 12. Decisiones cerradas en Phase 1 v1.5

| # | Decisión | Resolución |
|---|---|---|
| D1 | Stack-to-price ratio default | Tabla derivada por business_type × purchase_type (3× B2B reflexiva → 7× B2C impulsiva). Override por decision_record. |
| D2 | Composite value score gate mínimo | <100 bloqueo duro, 100–1000 bloqueo blando, 1000+ avanza. Escala 1–10,000. |
| D3 | Múltiples ofertas simultáneas por avatar | **Default invertido (D-009, 2026-06-06):** estrategia por-avatar es el default; el algoritmo de 5 condiciones decide si hay evidencia para *unificar* como optimización. `separate_strategies` (default) reemplaza `separate_offers`. Cada estrategia separada = un `strategies` row versionado. |
| D4 | Convención scoring Value Equation | 10 = óptimo en todos los ejes. Fórmula multiplicativa, sin división. Rango 1–10,000. |
| D5 | Dream Outcome anclaje | JTBD (emotional + functional) + pull, NO pain points. Oferta aspiracional, no defensiva. |
| D6 | Bonus mapping | Forces of Progress (pull_amplify, anxiety_reduce, habit_break, weakest_axis_boost), NO solo "objection_n". |
| D7 | Anxiety y habit coverage obligatorios | ≥1 bonus anxiety_reduce, ≥1 bonus habit_break (regla dura). |
| D8 | Displacement framing | Obligatorio en 1.3, no opcional. Rompe habit del status quo. |
| D9 | Margin gate | 70% digital / 50% service / 30% physical / 40% hybrid. Ambos gates obligatorios (ratio + margin). |
| D10 | Risk reversal / urgency manual permanente | V1, V2, V3 — siempre humano. Decisión ética irreductible. |
| D11 | Bonus Hormozi categorization | speed / done_for_you / identity / community_access / results_guarantee — campo opcional pero recomendado para detectar gaps. |

---

## 13. Lecciones registradas en Phase 1 spec design

| ID | Lección |
|---|---|
| L1 | Dream Outcome viene del JOB (Christensen), no del pain (defensivo). Hormozi es aspiracional. |
| L2 | El 70% de ofertas que fallan, fallan por no atacar anxiety + habit. Solo amplifican pull. |
| L3 | Stack-to-price ratio NO es universal — depende de business_type × purchase_type. |
| L4 | Margen y ratio son gates separados — ofertas pueden pasar uno y fallar el otro. |
| L5 | Reducir denominador (time + effort) supera a inflar numerador (dream + likelihood) en composite. |
| L6 | Multi-avatar no es decisión a priori — se decide después de 1.1 con evidencia. |
| L7 | Vocabulary mismatch entre avatars no requiere ofertas separadas — requiere language_packs. |
| L8 | Displacement framing es la pieza más subestimada de Hormozi — sin ella, la oferta es "agregar más". |
| L9 | Escalar composite a 1–10,000 (no 0.01–100) mejora legibilidad operativa significativamente. |
| L10 | Honestidad arquitectural en risk reversal y urgency: no es opcional, no es automatizable. |

---

## 14. Pendientes y diferidos

### Pendientes para implementación V1
- Skill `value-equation-optimizer` registrado en pretel-os
- Skill `offer-stack-builder` registrado en pretel-os
- 6 signal rules sembradas (VALUE-001/002, STACK-001/002, OFFER-001, PRICING-001)
- Tabla `ratio_target` por business_type × purchase_type registrada como best_practice
- Tabla `margin_target_pct` por delivery_format registrada como best_practice

### Diferidos
- Hormozi bonus categorization (MED-3 audit): campo opcional en V1, obligatorio en V2 cuando haya volumen para detectar patrones cross-producto
- "Better than money back" risk reversal type (pago extra si funciona): explorar en ciclo 2 después de validar money_back básico

---

## 15. Apéndice — checklist operacional V1

Para el primer ciclo manual de Phase 1 con un producto real:

```
[ ] G-Phase-1-PRE: 10 checks de entrada verificados
[ ] 1.1 — value_equation.json por avatar (Dream anclado en JTBD)
[ ] 1.1 — composite >= 100 (o decision_record si bloqueo blando)
[ ] 1.1 — weakest_axis identificado y registrado como decision_record
[ ] Multi-avatar — multi_avatar_decision.json producido con 5 condiciones evaluadas
[ ] Multi-avatar — strategies row(s) creada(s) (1 por avatar en separate_strategies; 1 unificada en unified_C_*); version_number=1, status=active
[ ] offer_spec.linked_to.strategy_id + strategy_version poblados
[ ] 1.2 — core_deliverable con perceived_value y delivery_cost reales
[ ] 1.2 — bonuses (3-7) con force_attacked y specific_target poblados
[ ] 1.2 — ≥1 bonus anxiety_reduce, ≥1 bonus habit_break
[ ] 1.2 — ratio_gate_passed: true
[ ] 1.2 — margin_gate_passed: true
[ ] 1.2 — phase_2_handoff documentado (uncovered explícitos)
[ ] 1.3 — risk_reversal con anxieties_addressed mapeadas
[ ] 1.3 — urgency/scarcity con is_genuine: true y genuine_reason real (o "none")
[ ] 1.3 — displacement_framing con habit_being_displaced y replacement_narrative
[ ] 1.4 — pricing con competitive_position poblado
[ ] 1.4 — tier_strategy validado contra tiers.length
[ ] 1.4 — offer_statement.md ≤350 palabras
[ ] 1.4 — si multi-avatar: un statement por avatar/language_pack
[ ] 1.4 — Drive 3-traits check: relevante, diferente, creíble
[ ] Signal rules evaluadas: ninguna alert sin resolver
[ ] offer_spec.json consolidado
[ ] hours/usd invertidos cuantificados
[ ] operator_signoff: true
```
