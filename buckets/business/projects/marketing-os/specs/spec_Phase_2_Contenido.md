# Phase 2 — Contenido

**Project**: business/marketing-os
**Phase ID**: phase-2
**Status**: spec drafted v1.1 (post audit R4)
**Last updated**: 2026-06-01
**Implementation correction:** This methodology now targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase), not a Python/FastMCP module inside `pretel-os`. Persist outputs in `project_phase_artifacts`, decisions in `project_decisions`, and learnings in `project_lessons`. n8n is not part of the MVP; revisit only for Phase 3 distribution/publication.

**Audit references**:
- Phase 0 v1.5 (R1, decision `7f87df56`) — consume `avatars[].forces_of_progress`, `awareness_distribution`, `negative_personas`, `dmu`, `business_context.channel`, `buyer_persona.jobs_to_be_done`
- Phase 1 v1.5 (R2, decision `9215573a`) — consume `offer_spec.json`, `offer_statement.md`, `multi_avatar_strategy`, `positioning_variants[].language_pack`, `phase_2_handoff`, `stack.force_coverage`, `risk_urgency_displacement.displacement_framing`
- Alineación Phase 0 ↔ Phase 1 (R3, decision `ef0b2c75`) — incorpora `target_cac_usd` persistido, `pricing_tiers[]` estructurado, `urgency.aligned_with_trigger`
- Auditoría Phase 2 R4 (2026-05-10) — A1-ISSUE-1 (force_coverage consumido + REINFORCE-001), A1-ISSUE-2 (JTBD anclado en brand voice + pilares + hooks), A1-ISSUE-3 (Vaynerchuk ratio + VAYNER-001), A1-ISSUE-4 (displacement_framing en PILLAR_D), A1-ISSUE-7/8 (L11 + Pinterest), A2-ISSUE-1/2/3/4 (V1/V2 disambiguación, evaluador, filesystem↔pretel-os, lookup table IDs explícitos)
- BP-001 (`fea3dbd8`) — V1 100% manual de operador antes de cualquier sub-workflow
- Lesson `17112600` — `domain` de pretel-os best_practices solo acepta `workflow|process|convention|communication`; signal-rules se persisten como `domain: workflow` con prefijo `SIGNAL-RULE` en título

---

## 0. Contexto y propósito

Phase 2 convierte la oferta (Phase 1) en piezas de contenido que respetan simultáneamente: (a) el awareness level del prospecto (Schwartz, mapeado en Phase 0.2), (b) la fase del Customer Journey del avatar (5 stages), (c) la función específica de cada canal del `business_context.channel`, (d) las 4 fuerzas del avatar (cada fuerza requiere un formato distinto), (e) las `negative_personas` (auto-rechazo de copy que apele a anti-target), (f) los gaps explícitos de `phase_2_handoff` heredados de Phase 1 (objections / anxieties / habits / pulls uncovered).

**Output canónico**: `content_plan.json` (matriz Customer Journey × awareness level × canal × formato × fuerza_atacada) + `content_assets/` (los assets reales: long-forms, derivatives, hooks library, emails, copy, CTAs).

### Pertenencia a una Estrategia (D-009/D-010, ver `Overall_WF.md`)

Cada `content_plan.json` **pertenece a una `strategies` row** (una estrategia versionada por avatar), no al proyecto plano. Esto materializa la jerarquía Project → Avatar → **Strategy** → Contenido.

- **`separate_strategies` (default):** Phase 1 y Phase 2 corren **N veces, una por avatar**. Cada corrida produce su propio `content_plan.json` enganchado a su `strategy_id` (un avatar, una versión). Es el caso limpio de la orquestación paralela.
- **`unified_C_*`:** un solo `content_plan.json` sirve a varios avatars (`covers_avatars`), enganchado a la estrategia unificada cuyo `covers_avatar_ids` lista todos. La diferenciación por avatar ocurre vía `language_packs` dentro del plan único.
- El plan declara `linked_to.strategy_id` + `strategy_version`. Decisiones, lessons y `signal_rules_triggered` de Phase 2 se persisten con `strategy_id` (no solo `project_id`), para que el loop de Phase 5 aprenda por estrategia.

**Spine teórico**:
- Schwartz "Breakthrough Advertising" (5 awareness levels — Unaware / Problem Aware / Solution Aware / Product Aware / Most Aware; este sistema colapsa Product+Most en "Most Aware" siguiendo el mapping ya hecho en Phase 0.2)
- Christensen Forces of Progress (contenido se diseña por fuerza atacada, no por intuición temática)
- Vaynerchuk "Jab Jab Jab Right Hook" (proporción contenido valor vs venta; Content Model: 1 keynote → 64 piezas, V1 reduce a 1:5 mínimo)
- Drive Big School (cada canal con función específica — SEO captura crónica, RRSS amplifica, email convierte, ads escalan)
- Permission marketing (Godin) — email solo a quienes opted-in, contenido orgánico antes que interrupción

**Principios operacionales**:
- Brand voice es declaración del operador (sub-paso 2.0), **nunca se automatiza** — paralelo a Phase 0.1 Business Context Gate y Phase 1.3 Risk Reversal
- Contenido se ancla en `forces_of_progress`, no en "ideas de contenido" sueltas
- `phase_2_handoff` de Phase 1 es contrato vinculante: cada uncovered explícito debe ser cubierto por ≥1 asset, no hay "lo veo en Phase 5"
- `negative_personas.signals_to_detect` se evalúan contra cada asset antes de publicar; matches bloquean
- Cada asset tiene `parent_pillar` + `force_attacked` + `awareness_level` + `language_pack_id` + `channel` — sin estos campos el asset no entra al plan

---

## 1. Estructura: 6 sub-pasos (1 declaración + 5 producción) + 1 transversal

| Sub-paso | Output | Estimado V1 | V1 (asistencia operador) | V2 (skill registrado) |
|---|---|---|---|---|
| 2.0 — Brand Voice Declaration | `brand_voice.json` | 1–2 h (única vez por producto) | Manual 100% (Claude propone arquetipo desde JTBD; operador decide) | Manual 100% (irreducible) |
| 2.1 — Awareness Mapping & Content Mix | `content_mix.json` | 30–60 min | Claude lee dashboard Phase 0.2 + offer_strategy_tag y propone mix; operador firma | `awareness-mix-suggester` (drafta desde signal rules) |
| 2.2 — Customer Journey × Canal Matrix | `channel_journey_matrix.json` | 1–2 h | Claude aplica lookup table `channel_function` y propone matrix; operador valida | Sub-workflow drafta matrix completo |
| 2.3 — Forces-aware Content Pillars | `pillars.json` (4 obligatorios) | 2–3 h | Templates + Claude copilot del operador | `content-pillars-builder` (skill autónomo) |
| 2.4 — Atomization | `atomization_map.json` | 1 h/pillar | Templates por formato + Claude copilot | `content-atomizer` (skill autónomo) |
| 2.5 — Hook Library | `hook_library.json` (≥10 hooks/pilar) | 2 h | Templates + research competitivo + Claude copilot | `hook-library-generator` (skill autónomo) |
| **Transversal** — Negative persona auto-filter | `negative_filter_report.json` por asset | continuo | Algoritmo determinístico (no LLM) — corre en V1 igual que V2/V3 | Igual que V1 |

**Aclaración V1 vs V2** (A2-ISSUE-1, audit R4): en V1 todos los sub-pasos 2.1–2.5 son operador + Claude actuando como copilot — consistente con BP-001 (`fea3dbd8`). Los nombres `content-pillars-builder`, `content-atomizer`, `hook-library-generator`, `awareness-mix-suggester` referencian skills propuestos para V2 cuando ya existan ≥3 ciclos manuales con un producto real. La tabla declara V1 y V2 explícitamente para evitar la lectura de "el skill ya existe" antes de tiempo.

---

## 2. Pre-condición — Gate de entrada G-Phase-2-PRE

Phase 2 NO arranca a menos que se cumplan los **14 checks**. Si cualquier check falla, el handler responde `{status: 'blocked', reason: '...'}`.

**Checks de Phase 1 cierre:**
1. ✅ `offer_spec.json` existe con `metadata.operator_signoff: true`
2. ✅ `offer_statement.md` existe (uno si `single_avatar` o `unified_C_*`, N si `separate_strategies`) y cada uno ≤350 palabras
3. ✅ `offer_spec.multi_avatar_strategy` ∈ {`single_avatar`, `unified_C_clean`, `unified_C_language_packs`, `unified_C_avatar_specific_bonuses`, `separate_strategies`} declarado
4. ✅ Si `multi_avatar_strategy ∈ {unified_C_language_packs, separate_strategies, unified_C_avatar_specific_bonuses}`: `positioning_variants[]` poblado con `language_pack.vocabulary_register`, ≥5 `key_phrases` y ≥3 `avoid_phrases` por avatar (heredado de G-Phase-1.4)
5. ✅ `offer_spec.metadata.phase_2_handoff` documentado: `objections_uncovered`, `anxieties_uncovered`, `habits_unattacked`, `pulls_underamplified` poblados explícitamente (cero uncovered permitido solo si OFFER-001 acknowledged en Phase 1)

**Checks de Phase 0 todavía válidos:**
6. ✅ `product_brief_v2.demand.awareness_distribution` poblado y `most_aware_pct + solution_aware_pct + problem_aware_pct + unaware_pct ∈ [95, 105]` (suma 100 ±5%)
7. ✅ `product_brief_v2.business_context.channel` declarado con ≥1 canal real (no placeholder)
8. ✅ TODOS los avatars en `product_brief_v2.avatars` tienen `forces_of_progress` completo (heredado de G-Phase-1-PRE check 7 post-R3)
9. ✅ `negative_personas.json` accesible y leído por el handler (lista de `signals_to_detect` cargada)
10. ✅ Si `business_context.business_type === "B2B"`: `dmu.json` poblado (champion + decision_maker + ≥1 influencer + ≥1 end_user)

**Checks de coherencia hacia atrás (consumo explícito de Phase 1, A1-ISSUE-1 + A1-ISSUE-4 audit R4):**
11. ✅ `offer_spec.stack.force_coverage` poblado y accesible: `pulls_amplified[]`, `anxieties_attacked[]`, `habits_broken[]`, `weakest_axis_boosted` — Phase 2 lee este campo para distinguir "qué reforzar" (lo cubierto por la oferta) vs "qué resolver" (lo uncovered del `phase_2_handoff`). Sin este campo, los pilares duplicarán o entrarán en disonancia con el offer_statement.
12. ✅ `offer_spec.risk_urgency_displacement.displacement_framing` poblado: `habit_being_displaced`, `replacement_narrative`, `cost_of_continuing_current_path`. PILLAR_D (habit) hereda estos campos literales — sin esto, PILLAR_D reinventa el framing y rompe consistencia cross-asset.

**Check del sub-paso 2.0 (gate interno propio):**
13. ✅ `brand_voice.json` declarado y firmado por operador (sub-paso 2.0 cerrado). Sin esto, 2.1–2.5 no arrancan.

**Check de pertenencia a estrategia (D-010):**
14. ✅ Existe la `strategies` row destino y su `strategy_id` está disponible para `content_plan.linked_to`. En `separate_strategies` se valida que esta corrida de Phase 2 corresponde a UN avatar (el `avatar_id` de la estrategia); en `unified_C_*` se valida que `covers_avatar_ids` de la estrategia == `covers_avatars` del offer_spec. Sin esto, el plan no puede anclarse y STRATEGY-LINK-001 bloquea Phase 2 close.

---

## 3. Sub-paso 2.0 — Brand Voice Declaration

### Propósito
Declarar la voz/tono de marca **antes** de delegar generación de contenido a cualquier LLM. La voz de marca es identidad, no decoración: si el LLM la inventa, cada asset es estilísticamente inconsistente y el avatar percibe ruido. Este sub-paso es el paralelo de Phase 0.1 (Business Context Gate) y Phase 1.3 (Risk Reversal) — declaración irreducible del operador.

### Output: `brand_voice.json`

```json
{
  "voice_id": "voice_v1_YYYYMMDD",
  "schema_version": "2.0",
  "linked_to_product": "marketing-os/{product_slug}",
  "archetype_primary": "hero | magician | outlaw | sage | jester | caregiver | ruler | creator | innocent | explorer | lover | everyman",
  "archetype_secondary": "uno opcional para HÍBRIDOS — las marcas reales suelen ser combinaciones ('el sabio rebelde' = sage+outlaw, 'el cuidador mágico' = caregiver+magician). Los 12 arquetipos junguianos SÍ cubren bien el espacio de personalidad (por eso aquí NO se usa `other` — ver Overall_WF §Pattern A: esto es un sistema razonablemente cerrado), pero la combinación primary+secondary es obligatoria cuando la marca no cae limpio en uno solo.",
  "archetype_rationale": "OBLIGATORIO citar buyer_persona.jobs_to_be_done[N].job_id + literal del emotional_job + literal del social_job. El archetype debe ser coherente con esos dos jobs. Sin cita explícita el campo se rechaza (regla dura, audit R4 A1-ISSUE-2)",
  "brand_promise": "Compromiso Principal de Marca (CPM) en formato: 'Ayudo a [cliente] a [logro] vía [método] sin [dolor]'. Una sola frase que ancla la promesa central de marca; complementa al archetype (no lo reemplaza). FLAG-6 — brand_voice schema_version 2.0.",
  "tone_descriptors": [
    "3-5 adjetivos concretos — ej: 'directo, sin jerga corporativa, irreverente sin grosería, datos por encima de opinión'"
  ],
  "vocabulary_register": "formal | profesional | casual | callejero | técnico | emocional",
  "voice_consistency_with_language_packs": {
    "compatibility_check": "el archetype + tone debe ser compatible con cada language_pack.vocabulary_register",
    "conflicts_detected": ["avatar_X language_pack es 'técnico' pero archetype 'jester' — resolver"]
  },
  "lexicon": {
    "preferred_terms": [
      "10-20 términos/frases que SIEMPRE se usan en lugar de alternativas — ej: 'cliente' no 'usuario', 'invertir' no 'gastar'"
    ],
    "prohibited_terms": [
      "10-20 términos/frases prohibidos — ej: 'revolucionario', 'increíble', 'único', 'sinergia', 'disrupción'"
    ],
    "example_pairs": [
      { "say": "te entrego X listo para usar", "dont_say": "te ofrecemos una solución integral" }
    ]
  },
  "stylistic_rules": {
    "sentence_length_target_words": "8-15 (corto, escaneable)",
    "paragraph_length_target_lines": "2-4",
    "second_person_usage": "siempre tú/usted (declarar) — coherente con language_pack.vocabulary_register",
    "emoji_policy": "none | sparing (≤1 por asset) | liberal — declarar por canal",
    "exclamation_marks_policy": "evitar | hasta 1 por asset | libre"
  },
  "competitor_voice_avoidance": {
    "competitors_referenced": [
      { "name": "...", "their_voice": "ej: corporativo-optimista", "we_avoid_to_differentiate": "..." }
    ]
  },
  "consistency_check_rules": [
    "regla 1 testeable sobre cualquier asset — ej: 'no contiene ningún término de lexicon.prohibited_terms'",
    "regla 2 — ej: 'al menos 1 término de lexicon.preferred_terms aparece'",
    "regla 3 — ej: 'no usa más de 1 signo de exclamación si emoji_policy=sparing'"
  ],
  "operator_signoff": true,
  "declared_at": "ISO date"
}
```

### Reglas duras

- `archetype_primary` obligatorio (no "mixed", no "ninguno") — decisión de identidad
- `archetype_rationale` cita `buyer_persona.jobs_to_be_done[N].job_id` + literal del `emotional_job` + literal del `social_job` (A1-ISSUE-2 audit R4). Sin cita explícita, el campo se rechaza — el archetype anclado en JTBD garantiza coherencia con el Dream Outcome de Phase 1.1.
- `brand_promise` obligatorio en formato CPM "Ayudo a [cliente] a [logro] vía [método] sin [dolor]" (FLAG-6, schema_version 2.0). Complementa al archetype — **no reabre ni reemplaza el enum cerrado de arquetipos** (R-7 se mantiene); es un campo aditivo que ancla la promesa central de marca en una sola frase. Coherente con el Dream Outcome de Phase 1.1 y con `offer_statement`.
- ≥3 `tone_descriptors`, todos concretos (no "profesional" solo — "profesional pero conversacional, evita jerga MBA")
- `lexicon.prohibited_terms` debe incluir los adjetivos vacíos clásicos: "revolucionario", "increíble", "único", "innovador" (Phase 1.4 regla del statement los prohíbe; Phase 2 los hereda)
- `consistency_check_rules` ≥3 reglas, cada una testeable programáticamente (string match, regex, length count) — sin esto VOICE-001 no puede evaluar
- Si hay >1 `language_pack` en `positioning_variants`, `voice_consistency_with_language_packs.conflicts_detected` debe listar conflictos o estar vacío explícitamente

### Nota — evaluador de `consistency_check_rules` (A2-ISSUE-2 audit R4)

En V1 las reglas se evalúan manualmente: el operador lee cada regla y la aplica al hook/asset a mano. En V2/V3 se evalúan vía un check engine determinístico (sin LLM). Cada regla declara estructura:

```json
{
  "rule_id": "...",
  "type": "string_match | regex | length_count | term_presence | term_absence",
  "target_field": "asset.text | asset.title | hook.text",
  "expression": "...",
  "expected": true
}
```

El check engine solo reporta pass/fail por regla; nunca reescribe el asset. Cualquier reescritura es decisión del operador o del sub-workflow generador (no del evaluador).

### Persistencia: filesystem + pretel-os (A2-ISSUE-3 audit R4)

El archivo `brand_voice.json` vive en filesystem en `content_assets/_meta/brand_voice.json` (contiene lexicon de 20+ términos, demasiado verboso para una columna de pretel-os). La elección del `archetype_primary` + `archetype_rationale` se registra **adicionalmente** como `decision_record` en pretel-os con `tags: ['brand-voice', '{product_slug}', 'archetype']` y `derived_from_lessons` apuntando a las lessons de brand voice de productos previos si las hay. Mismo patrón que `offer_spec.json` (vive en filesystem, decisión arquitectónica vive en pretel-os): el filesystem es el detalle, pretel-os es el aprendizaje cross-producto.

### Lectura previa pretel-os
- `lessons` con tags `['brand-voice', 'tone', 'archetype', 'copy']`
- `best_practice_search(query="brand voice consistency archetype")`
- `decision_search(query="brand voice")` por producto

### Escrituras
- `decision_record` por elección del `archetype_primary` con rationale
- `decision_record` por cada `prohibited_terms` adicional que NO sea de los adjetivos vacíos default (ej: prohibir el slang del competidor)

### Gate G-Phase-2.0
- `brand_voice.json` poblado completamente
- `operator_signoff: true`
- ≥3 `consistency_check_rules` testeables
- Compatibilidad con `language_packs` verificada (conflictos listados o array vacío)

### V1/V2/V3
| Versión | Quién decide |
|---|---|
| V1, V2, V3 | **Operador siempre** — identidad de marca es irreducible. Claude puede sugerir arquetipo desde JTBD pero la elección final es humana. |

---

## 4. Sub-paso 2.1 — Awareness Mapping & Content Mix

### Propósito
Decidir qué % del contenido total va a cada nivel de Schwartz, ancladonte en el `awareness_distribution` ya calculado en Phase 0.2. **No es 1:1 con la distribución de demanda** — es función de la `offer_strategy` taggeada por DEMAND-001/002 en Phase 0.2.

### Heurísticas de mapping (LOCKED)

**Caso A — `offer_strategy: capture_existing_demand`** (DEMAND-001 disparó: alta transactional, baja informational):
- Most Aware: 50–60% del contenido (capturar intent existente)
- Solution Aware: 25–35% (comparativos)
- Problem Aware: 10–15% (educacional ligero)
- Unaware: 0–5% (no invertir aquí)

**Caso B — `offer_strategy: create_demand`** (DEMAND-002 disparó: alta informational, baja transactional):
- Most Aware: 10–20% (poco intent existente)
- Solution Aware: 25–35%
- Problem Aware: 35–45% (mayoría del esfuerzo aquí: educar)
- Unaware: 10–20% (entretenimiento + identidad que lleva a Problem Aware)

**Caso default — sin signal rule disparada**: espejo de `awareness_distribution` ±10% por nivel.

### Output: `content_mix.json`

```json
{
  "linked_to_demand_dashboard": "product_brief_v2.demand.awareness_distribution",
  "offer_strategy_tag": "capture_existing_demand | create_demand | default",
  "target_mix": {
    "most_aware_pct": 0,
    "solution_aware_pct": 0,
    "problem_aware_pct": 0,
    "unaware_pct": 0
  },
  "demand_alignment_delta": {
    "most_aware_delta_pct": 0,
    "solution_aware_delta_pct": 0,
    "problem_aware_delta_pct": 0,
    "unaware_delta_pct": 0,
    "max_abs_delta_pct": 0,
    "justification_if_max_delta_gt_30": "obligatorio si max_abs_delta > 30, con cita a offer_strategy_tag o decision_record"
  },
  "rationale": "1-2 oraciones — por qué este mix dado el offer_strategy y la realidad del avatar"
}
```

### Reglas duras

- Los 4 % suman 100 ±2
- Si `max_abs_delta_pct > 30` (mix se aleja >30 puntos de la demand distribution) → `justification_if_max_delta_gt_30` obligatorio o se dispara CONTENT-004
- No se permite Unaware = 0% en `create_demand` (caso B): es la pista para nuevos prospectos

### Sub-workflow `awareness-mix-suggester` (asistido)

```
1. Lee awareness_distribution de Phase 0.2
2. Lee offer_strategy_tag (de signal rules DEMAND-001/002 de Phase 0.2)
3. Aplica heurística A/B/default
4. Propone target_mix con delta_alignment
5. Operador ajusta y firma
```

### Gate G-Phase-2.1
- `target_mix` con 4 valores poblados, suma 100 ±2
- `offer_strategy_tag` extraído de Phase 0.2 signal rules
- Si `max_abs_delta_pct > 30` → justification poblado y registrado como `decision_record`

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + Claude lee dashboard y propone, operador aprueba. |
| V2 | Sub-workflow drafta desde signal rules de Phase 0.2 directo. |
| V3 | Auto + flag si delta > 30 sin precedente. |

---

## 5. Sub-paso 2.2 — Customer Journey × Canal Matrix

### Propósito
Mapear cada combinación `(canal declarado, customer_journey_stage, awareness_level)` a un formato + frecuencia. El error clásico es producir contenido por canal sin pensar el journey, terminando con SEO de retención y email de awareness (ambos invertidos).

### Lookup table `channel_function` (LOCKED, override por `decision_record`)

Esta tabla está registrada como `best_practice` en pretel-os con `domain: workflow`, `scope: project:business/marketing-os`, prefijo `LOOKUP-TABLE` en título y nombre canónico `channel_function` (A2-ISSUE-4 audit R4). Phase 2.2 la consulta vía `best_practice_search(query='lookup-table channel function')` antes de proponer matrix.

| Canal | Función primaria | Awareness levels servidos | Customer Journey stages servidas |
|---|---|---|---|
| SEO (blog, evergreen) | Captura crónica + educación | Problem Aware, Solution Aware | Consciencia, Consideración, Retención |
| Email (permission-based) | Conversión + retención | Solution Aware, Most Aware | Decisión, Retención, Advocacy |
| RRSS orgánico (IG, TikTok, X, FB) | Amplificación + identidad | Unaware, Problem Aware | Consciencia, Advocacy |
| Pinterest (orgánico + paid) | Descubrimiento visual + intent diferido | Problem Aware, Solution Aware | Consciencia, Consideración (clave para productos físicos, novedad visual, lifestyle) |
| Paid social (Meta/TikTok Ads) | Escala + interrupción | Solution Aware, Most Aware | Consciencia, Decisión |
| Paid search (Google Ads) | Captura intent caliente | Most Aware | Decisión |
| YouTube long-form (orgánico) | Educación profunda + autoridad | Problem Aware, Solution Aware | Consideración, Decisión |
| YouTube paid (TrueView, in-stream) | Escala + interrupción con story | Solution Aware, Most Aware | Consciencia, Decisión |
| LinkedIn orgánico (B2B) | Identidad profesional + thought leadership | Problem Aware, Solution Aware | Consciencia, Consideración |
| Podcast / audio | Confianza + intimidad | Problem Aware, Solution Aware | Consideración, Retención |
| Influencer marketing | Transferencia de confianza | Unaware, Problem Aware, Solution Aware | Consciencia, Consideración |
| Affiliates | Captura intent + comisión | Solution Aware, Most Aware | Decisión |

**Nota de extensión** (A1-ISSUE-8 audit R4): si un canal declarado en `business_context.channel` no aparece en esta tabla, registrar `decision_record` con la función asignada por el operador, basada en hábitos del avatar de Phase 0.3 (`buyer_persona.behaviors.online_communities` + `media_consumed`). El `decision_record` se promueve a entrada permanente de la lookup table tras ≥3 productos que lo usen — patrón cross-pollination de pretel-os.

### Output: `channel_journey_matrix.json`

```json
{
  "channels_declared": ["..."],
  "matrix": [
    {
      "channel": "SEO",
      "journey_stage": "consideracion",
      "awareness_level": "solution_aware",
      "format_primary": "comparativo long-form | listicle | how-to",
      "format_secondary": "video embebido | infografía",
      "frequency_per_week_v1": 1,
      "kpi_primary": "organic_traffic | time_on_page | scroll_depth | ranking_position | completion_rate | avg_watch_time_s | saves | shares | open_rate | click_rate | avg_position | impressions | other  [Extensible Vocabulary]",
      "kpi_primary_custom": "obligatorio si kpi_primary=other. La semilla es por-canal (FLAG-4, promovida bajo gobernanza Pattern A): social → completion_rate, avg_watch_time_s, saves, shares; email → open_rate, click_rate; SEO → avg_position, impressions (más los SEO genéricos organic_traffic/time_on_page/scroll_depth/ranking_position). El KPI correcto depende del canal — ej: 'comentarios cualitativos' (validar mensaje). Un custom que prediga conversión en un canal se promueve (Overall_WF §Pattern A). El set abierto sigue siendo por-canal.",
      "rationale": "1 oración — por qué esta combinación es válida dada la función del canal"
    }
  ],
  "channels_unused_explanation": [
    { "channel": "X", "reason": "decision_record_id justificando por qué no se usa este canal aunque está declarado en business_context.channel" }
  ]
}
```

### Reglas duras

- TODOS los canales en `business_context.channel` aparecen en `matrix` ≥1 vez, O en `channels_unused_explanation` con `decision_record` (sin esto CONTENT-003 dispara warning)
- TODOS los 5 customer journey stages (consciencia, consideración, decisión, retención, advocacy) cubiertos por ≥1 entrada de matrix — excepto retención y advocacy si producto es pre-PMF (`product.expected_repeat_rate === "one-shot"`)
- Cada entrada con `kpi_primary` declarado (sin esto Phase 4 no sabe qué medir)
- `frequency_per_week_v1` realista para el operador solo — exceder >5 piezas/semana por canal en V1 es flag automático de over-commitment

### Lectura previa
- `business_context.channel`
- `awareness_distribution` y `content_mix.target_mix` (sub-paso 2.1)
- `avatars[].customer_journey_position` (Phase 0.3)
- `lessons` con tags `['channel-function', 'customer-journey']`

### Escrituras
- `decision_record` por cada canal declarado pero no usado en matrix
- `decision_record` por override de la lookup table de función natural

### Gate G-Phase-2.2
- ≥1 entrada por canal declarado o explicación documentada
- Customer Journey stages cubiertos según etapa del producto
- KPI por entrada declarado

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + lookup table. Operador valida cada combinación. |
| V2 | Sub-workflow drafta matrix completo desde lookup + content_mix. |
| V3 | Auto + flag canales no usados sin justificación. |

---

## 6. Sub-paso 2.3 — Forces-aware Content Pillars

### Propósito
4 pilares de contenido, **uno por fuerza** de Christensen (ongoing_pains, triggers, anxiety, habit). El error clásico es agrupar pilares por tema ("blog de SEO", "Reels de TikTok") — esto descubre canal pero no estrategia. Pilares por fuerza garantizan que cada palanca psicológica del avatar recibe contenido específico.

### Los 4 pilares obligatorios

| Pillar ID | Fuerza atacada | Función | Canal primario sugerido | Formato típico |
|---|---|---|---|---|
| **PILLAR_A** | `ongoing_pains` (push crónico) | Captura demanda existente, evergreen | SEO + YouTube long-form | Long-form artículo, how-to, listicle, comparativo |
| **PILLAR_B** | `triggers` (push agudo, evento) | Captura demanda en momento exacto | Paid ads + landing pages dedicadas | Ad creativo + LP por trigger, email de campaña |
| **PILLAR_C** | `anxiety` (frenos al cambio) | Reduce fricción de compra | Email + RRSS orgánico + RRSS paid | Testimonios, casos de éxito, demos, behind-the-scenes, garantía explicada |
| **PILLAR_D** | `habit` (inercia status quo) | Rompe estado actual | SEO + RRSS + email | Comparativos vs status quo, framing de displacement, "X vs no-hacer-nada", cost-of-inaction stories |

### Distinción reinforce vs resolve (A1-ISSUE-1 audit R4)

Cada pilar tiene **dos modos** de actuar sobre las fuerzas, derivados de Phase 1:

- **REINFORCE**: la fuerza ya está cubierta por el offer stack (`offer_spec.stack.force_coverage` la lista). El contenido del pilar **amplifica la mensajería del offer_statement**, no la reinventa. Ejemplo: si `force_coverage.anxieties_attacked` incluye `anx_1` (cubierta por bonus money-back de la oferta), PILLAR_C sobre `anx_1` **reusa** las palabras del offer_statement / risk_reversal.statement, no crea narrativa paralela.
- **RESOLVE**: la fuerza está en `phase_2_handoff.{anxieties|habits|...}_uncovered` o `pulls_underamplified` (la oferta NO la cubre, Phase 1 explícitamente la delegó a copy). El contenido del pilar **ataca la fuerza con copy propio** porque es el único mecanismo que la cubre.

Sin esta distinción, dos modos de fallo (documentados en audit R4 A1-ISSUE-1):
1. **Duplicación**: PILLAR_C produce 5 piezas sobre money-back redundantes con lo que el offer_statement ya dice.
2. **Inconsistencia**: PILLAR_C ataca `anx_1` con un mensaje distinto al del bonus, creando dissonance entre copy y oferta.

### Re-impacto evergreen por cambio de ángulo motivacional (G18, Curso 6)

PILLAR_C (anxiety / fricción de compra) es el hogar natural del **re-impacto a no-convertidores**: leads que consumieron contenido pero no convirtieron. Es una palanca barata porque **no requiere re-build del plan** — reusa los assets existentes con un ángulo distinto.

- **Misma fuerza, distinto beneficio**: el re-impacto ataca la **MISMA** fuerza/anxiety con un **ángulo motivacional distinto** — se cambia el **beneficio** comunicado, **no el producto**. Ejemplo: el mismo curso vendido primero por "ahorra tiempo" se re-impacta por "evita el error caro que comete el 80%".
- **Urgencia calibrada por ticket** (ventana de re-impacto): ticket **bajo** = 15 min–1 h; ticket **medio** = 48 h; ticket **alto** = 3–7 días. El precio del producto fija qué tan agresiva es la ventana antes de reciclar el ángulo.
- Estos derivatives de re-impacto se etiquetan en su `content_type` como `cta` o `hybrid` y heredan el `language_pack` del avatar no-convertidor. La ventana de urgencia por ticket viaja como metadata al handoff de Phase 3 (secuencia `evergreen_reimpact`).

### Output: `pillars.json`

```json
{
  "pillars": [
    {
      "id": "PILLAR_A",
      "name": "ej: 'Cómo resolver [ongoing_pain] sin [obstáculo común]'",
      "force_attacked": "ongoing_pain",
      "specific_targets": [
        { "force_id": "ongoing_pain_2", "literal": "del avatar.forces_of_progress.push_of_situation.ongoing_pains[2]" }
      ],
      "jtbd_anchor": {
        "job_id": "JTB-1 (de buyer_persona.jobs_to_be_done)",
        "frustration_with_current_literal": "literal de jobs_to_be_done[].frustration_with_current — anchor del content_brief, no parafrasear",
        "social_job_for_identity_callouts": "literal de jobs_to_be_done[].social_job — base de hooks tipo 'Si eres [identidad]'"
      },
      "forces_already_covered_by_offer": {
        "reinforces": [
          { "force_id": "ongoing_pain_2", "covered_by_offer_element": "core_deliverable | bonus_X | offer_statement", "reuse_phrasing_from": "offer_statement.md sección Y" }
        ],
        "does_not_address": [
          { "force_id": "ongoing_pain_5", "must_resolve_with_pillar_copy": true }
        ]
      },
      "avatar_coverage": ["avatar_1", "avatar_2"],
      "language_pack_assignments": { "avatar_1": "language_pack_avatar_1", "avatar_2": "..." },
      "channel_primary": "SEO",
      "channels_secondary": ["YouTube"],
      "format_primary": "long-form article",
      "frequency_v1": "3 artículos/mes",
      "kpi_primary": "organic_traffic + ranking_position en keywords transaccionales",
      "kpi_secondary": "time_on_page > 2min",
      "content_brief": "qué tipo de problema cubre, qué tono usar (cita brand_voice), qué keywords objetivo (de Phase 0.2), cuál JTBD ancla (cita job_id + literal de frustration_with_current)",
      "anchor_to_offer": "qué CTA dirige al offer_statement.md — ej: bloque 'próximo paso' al final del artículo",
      "addresses_phase_2_handoff": ["objection_3 | anxiety_2 | habit_1 | pull_4 — del phase_2_handoff de Phase 1"]
    },
    {
      "id": "PILLAR_B",
      "name": "...",
      "force_attacked": "trigger",
      "specific_targets": [
        { "force_id": "trigger_1", "literal": "...", "aligned_with_urgency": "si offer_spec.risk_urgency_displacement.urgency.aligned_with_trigger == trigger_1, este pillar amplifica el momentum de la oferta" }
      ],
      "char_limits_per_platform": {
        "google_ads_headline_max": 30,
        "google_ads_long_headline_max": 90,
        "google_ads_description_max": 90,
        "note": "PILLAR_B vive en paid ads + landing pages; el ad copy nace dentro del límite de plataforma (Curso 5, G4) para que Phase 3 no rebote assets. Declarar un sub-objeto por cada plataforma de ads destino (Meta/TikTok tienen sus propios límites)."
      },
      "forces_already_covered_by_offer": { "reinforces": [], "does_not_address": [] },
      "...": "..."
    },
    {
      "id": "PILLAR_D",
      "name": "...",
      "force_attacked": "habit",
      "specific_targets": [
        { "force_id": "habit_1", "literal": "del avatar.forces_of_progress.habit_of_present[0]" }
      ],
      "displacement_inheritance": {
        "habit_being_displaced_id": "habit_1 — heredado literal de offer_spec.risk_urgency_displacement.displacement_framing.habit_being_displaced (A1-ISSUE-4 audit R4)",
        "replacement_narrative_literal": "frase exacta de displacement_framing.replacement_narrative — debe aparecer literal en ≥1 derivative del pilar (consistency cross-asset)",
        "cost_of_continuing_current_path_literal": "frase exacta de displacement_framing.cost_of_continuing_current_path — base de cost-of-inaction stories del pilar"
      },
      "forces_already_covered_by_offer": { "reinforces": [], "does_not_address": [] },
      "...": "..."
    }
  ]
}
```

### Reglas duras

- **4 pilares obligatorios, uno por fuerza** — no se permite saltarse ninguno (sin esto FORCES-001 bloquea)
- Cada `specific_targets[]` apunta a un `force_id` real de `avatar.forces_of_progress` (no inventado)
- Cada `addresses_phase_2_handoff[]` referencia exactamente los IDs documentados en `offer_spec.metadata.phase_2_handoff` — la unión de todos los `addresses_phase_2_handoff` debe cubrir TODOS los uncovered (sin esto CONTENT-002 alert)
- **Cada pilar declara `forces_already_covered_by_offer.reinforces[]` y `does_not_address[]`** derivados de `offer_spec.stack.force_coverage` (A1-ISSUE-1 audit R4). Sin estos campos el pilar no entra al plan — riesgo de duplicación o disonancia con offer_statement. REINFORCE-001 dispara warning si un asset cubre una fuerza listada en `reinforces` con phrasing >50% distinto al del offer_statement.
- **Cada pilar declara `jtbd_anchor`** con `job_id` + literal de `frustration_with_current` + literal de `social_job` (A1-ISSUE-2 audit R4). El `content_brief` debe citar estos literales — no parafrasear. Sin esto, el contenido pierde anchor aspiracional con el Dream Outcome de Phase 1.1.
- **PILLAR_D obligatoriamente declara `displacement_inheritance`** con los tres campos heredados literales de `offer_spec.risk_urgency_displacement.displacement_framing` (A1-ISSUE-4 audit R4). El `replacement_narrative_literal` debe aparecer textualmente en ≥1 derivative del pilar por ciclo (consistency cross-asset).
- Si `business_context.business_type === "B2B"` → cada pilar declara `dmu_role_target` (champion / decision_maker / influencer / end_user) explícito
- Si `multi_avatar_strategy === "separate_strategies"` → cada avatar corre su propia Phase 2 (un `content_plan.json` por estrategia/avatar); el `language_pack_assignments` de cada plan apunta al avatar de esa estrategia
- PILLAR_B (triggers) DEBE alinearse con `risk_urgency_displacement.urgency.aligned_with_trigger` cuando esa urgency no es `none` — coherencia entre la oferta y la campaña que la captura

### Sub-workflow `content-pillars-builder`

Skill propuesto para V2 (no V1).

**Inputs**:
- `forces_of_progress` por avatar
- `phase_2_handoff` de Phase 1
- `brand_voice.json`
- `content_mix.json`
- `channel_journey_matrix.json`
- `offer_statement.md`(s)

**Algoritmo**:
```
1. Para cada force (ongoing_pain, trigger, anxiety, habit):
   a. Selecciona el top force_id del avatar (mayor frequency o urgency)
   b. Lookup channel_primary desde tabla de Sección 6
   c. Lookup format_primary desde channel_journey_matrix
   d. Calcula frequency_v1 = floor(content_mix.target_mix[awareness] × budget_pieces / 4)
2. Mapea cada uncovered de phase_2_handoff al pilar correspondiente:
   - objections_uncovered → PILLAR_A o PILLAR_C
   - anxieties_uncovered → PILLAR_C
   - habits_unattacked → PILLAR_D
   - pulls_underamplified → PILLAR_A o PILLAR_B
3. Verifica cobertura: union(addresses_phase_2_handoff) == phase_2_handoff (todos)
4. Si business_type=B2B: asigna dmu_role_target por pilar
5. Operador valida y firma
```

### Gate G-Phase-2.3
- 4 pilares poblados
- Cada pilar con `specific_targets` reales, `channel_primary`, `format_primary`, `frequency_v1`, `kpi_primary`, `content_brief`, `anchor_to_offer`
- Cobertura 100% de `phase_2_handoff` (cada uncovered mapeado a ≥1 pilar)
- Si B2B: cada pilar con `dmu_role_target`
- PILLAR_B coherente con `urgency.aligned_with_trigger` (si aplica)

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + plantilla. Operador llena los 4 pilares con asistencia de Claude. |
| V2 | `content-pillars-builder` drafta los 4, operador ajusta. |
| V3 | Auto + flag desviaciones. |

---

## 7. Sub-paso 2.4 — Atomization

### Propósito
Cada pilar produce **1 pieza long-form anchor** + **N derivatives**. Sin atomización, el costo por pieza es prohibitivo y el operador abandona el plan en semana 3. Modelo Vaynerchuk: 1 keynote → 64 piezas. V1 reduce a 1:5 mínimo (1 long-form → ≥5 derivatives).

### Ratio mínimo por canal/formato (LOCKED) — lookup table `atomization_ratio_minimum_per_anchor_format`

Registrada como `best_practice` en pretel-os con `domain: workflow`, prefijo `LOOKUP-TABLE` y nombre canónico `atomization_ratio_minimum_per_anchor_format` (A2-ISSUE-4 audit R4).

| Long-form anchor (1 unidad) | Derivatives mínimos V1 (≥5 total) |
|---|---|
| Artículo SEO ≥1500 palabras | 1 thread (X/LinkedIn) + 1 carrusel (IG/LinkedIn) + 1 short (TikTok/Reels) + 1 email + 1 quote graphic |
| Video YouTube ≥10 min | 2 shorts + 1 thread + 1 email + 1 carrusel + 1 podcast clip (audio) |
| Episodio podcast ≥20 min | 1 transcript-to-article + 2 shorts + 1 carrusel + 1 email + 1 quote graphic |

### Estructura de guión de video por intervalos (G6, Cursos 5 + 7)

El video es el formato de mayor fricción de producción; sin plantilla de intervalos queda sin guía. Cada derivative de video declara `video_script_structure` con sus intervalos. El `hook_id_assigned` alimenta el **primer intervalo** (el gancho). La plantilla depende de `kind`:

| kind | Intervalos | Uso |
|---|---|---|
| **paid** (PILLAR_B — paid social, paid search, YouTube paid) | 0-2s hook / 2-5s producto / 5-8s prueba-o-precio / 8-10s CTA | Ad corto: cada segundo cuenta, CTA explícito al cierre (Curso 5). |
| **organic** (RRSS orgánico, YouTube/Reels/TikTok orgánico) | gancho 3-5s / cuerpo 15-45s con micro-ganchos / cierre 4-6s | El cuerpo intercala micro-ganchos para sostener retención; cierre suave con `anchor_to_offer` (Curso 7). |

### Output: `atomization_map.json`

```json
{
  "atomizations": [
    {
      "pillar_id": "PILLAR_A",
      "long_form": {
        "asset_id": "asset_pillar_A_001",
        "format": "seo_article",
        "channel": "blog",
        "target_keyword": "del Phase 0.2 keyword research",
        "target_awareness_level": "problem_aware",
        "target_journey_stage": "consideracion",
        "estimated_word_count": 1800,
        "structured_data": {
          "schema_type": "Article | HowTo | FAQPage | Product | Review | … (schema.org) — opcional, solo para long-form SEO de PILLAR_A",
          "jsonld_validated": true,
          "note": "factor de Rich Results y elegibilidad para AI Overview (BigSEO). Todo long-form SEO de PILLAR_A declara su schema_type y valida el JSON-LD antes de publicar."
        }
      },
      "derivatives": [
        {
          "derivative_id": "asset_pillar_A_001_d1",
          "format": "twitter_thread",
          "channel": "X",
          "target_awareness_level": "solution_aware",
          "language_pack_id": "language_pack_avatar_1",
          "hook_id_assigned": "hook_A_07",
          "parent_long_form": "asset_pillar_A_001",
          "content_type": "value | cta | hybrid",
          "content_type_rationale": "value = sin pedido de venta, hybrid = valor con anchor_to_offer suave, cta = pedido directo (oferta, lead form, demo)"
        },
        {
          "derivative_id": "asset_pillar_A_001_d4",
          "format": "email",
          "channel": "email",
          "target_awareness_level": "solution_aware",
          "language_pack_id": "language_pack_avatar_1",
          "hook_id_assigned": "hook_A_07",
          "parent_long_form": "asset_pillar_A_001",
          "content_type": "value | cta | hybrid",
          "subject_line": {
            "variants": ["≤5 variantes, cada una ≤40 chars — el subject line es el HOOK del canal email y decide la tasa de apertura (Curso 6)"],
            "pre_header": "texto de preview ≤90 chars que complementa el subject (no lo repite)",
            "one_variant_with_emoji": true,
            "spam_words_checked": true,
            "ab_test_pair": ["las 2 mejores variantes a testear"]
          }
        },
        {
          "derivative_id": "asset_pillar_B_001_d1",
          "format": "ad_copy",
          "channel": "Google Ads",
          "target_awareness_level": "most_aware",
          "language_pack_id": "language_pack_avatar_1",
          "hook_id_assigned": "hook_B_03",
          "parent_long_form": "asset_pillar_B_001",
          "content_type": "cta",
          "char_limits_per_platform": {
            "google_ads_headline_max": 30,
            "google_ads_long_headline_max": 90,
            "google_ads_description_max": 90,
            "note": "el copy nace dentro del límite de plataforma (Curso 5) para que Phase 3 no rebote assets; declarar por cada plataforma de destino del ad"
          }
        },
        {
          "derivative_id": "asset_pillar_A_001_d3",
          "format": "short_video",
          "channel": "TikTok",
          "target_awareness_level": "problem_aware",
          "language_pack_id": "language_pack_avatar_1",
          "hook_id_assigned": "hook_A_07",
          "parent_long_form": "asset_pillar_A_001",
          "content_type": "value",
          "video_script_structure": {
            "kind": "paid | organic",
            "intervals": [
              { "interval": "0-2s", "role": "hook", "fed_by": "hook_id_assigned alimenta este primer intervalo" }
            ],
            "note": "ver tabla de Sección 7 'Estructura de guión de video por intervalos' — la plantilla de intervalos depende de kind (paid PILLAR_B vs orgánico) y del formato"
          }
        }
      ]
    }
  ]
}
```

### Reglas duras

- Cada `pillar_id` tiene ≥1 `long_form` + ≥5 `derivatives` (V1) — sin esto ATOMIZATION-001 warning
- Cada derivative referencia un `parent_long_form.asset_id` real
- Cada derivative con `language_pack_id` asignado (si aplica multi-avatar) — el contenido se reescribe en el registro del language_pack, no se traduce literal
- Cada derivative con `hook_id_assigned` que existe en `hook_library.json` (sub-paso 2.5) — sin esto el derivative no se publica
- Cada derivative con `content_type ∈ {value, cta, hybrid}` declarado (A1-ISSUE-3 audit R4)
- **Subject line como artefacto de primera clase en `format=email`** (G3, Curso 6): cada derivative `format=email` declara `subject_line` con `variants` (≤5, cada una ≤40 chars), `pre_header`, `one_variant_with_emoji: true`, `spam_words_checked: true` y `ab_test_pair` (las 2 mejores). El subject line es el "hook" del canal email (equivalente al `hook_library` para los demás canales) y decide la tasa de apertura. **Regla dura: un derivative `format=email` sin `subject_line` poblado no se publica** (ATOMIZATION-002 bloquea).
- **Límites de caracteres de ads como restricción estructural en `format=ad_copy`** (G4, Curso 5): cada derivative `format=ad_copy` declara `char_limits_per_platform` por plataforma de destino. Para Google Ads: headlines ≤30 chars, long headlines/descriptions ≤90 chars. El copy nace dentro del límite para que Phase 3 no rebote assets en plataforma. Ver también PILLAR_B (Sección 6), que declara estos límites a nivel pilar.
- **Estructura de guión de video por intervalos en derivatives de video** (G6, Cursos 5 + 7): cada derivative de video (`format ∈ {short_video, video, reel, …}`) declara `video_script_structure` con `kind ∈ {paid, organic}` y sus `intervals` según la tabla "Estructura de guión de video por intervalos" de arriba. El `hook_id_assigned` alimenta el primer intervalo (el gancho). Paid (PILLAR_B) = 0-2s hook / 2-5s producto / 5-8s prueba-o-precio / 8-10s CTA; orgánico = gancho 3-5s / cuerpo 15-45s con micro-ganchos / cierre 4-6s.
- **Schema.org / JSON-LD opcional en long-form SEO de PILLAR_A** (G5, BigSEO): el `long_form` de PILLAR_A puede declarar `structured_data: { schema_type, jsonld_validated: true }`. Cuando se declara, **todo long-form SEO de PILLAR_A declara su `schema_type` (schema.org) y valida el JSON-LD antes de publicar** — es factor de Rich Results y elegibilidad para AI Overview. Campo opcional en V1 (no bloqueante); el `entity_coverage_checklist` queda diferido a V2 (Sección 16).
- **Vaynerchuk jab-jab-jab-right-hook ratio [Context-Adjusted Threshold]**: por pilar, en canales orgánicos, `count(content_type=value) : count(content_type=cta) ≥ ratio_objetivo`. Hybrid cuenta como 0.5 value + 0.5 cta. El **3:1 es el DEFAULT por canal**, no una ley global (es heurística de Vaynerchuk de hace ~10 años): LinkedIn B2B / audiencia caliente toleran más CTA (ej. 2:1); IG/TikTok B2C / audiencia fría necesitan más jabs (ej. 5:1). **El ratio objetivo se ajusta por la fatiga REAL que Phase 4 ya mide (CTR decay por canal/avatar)** — la detección de fatiga observada reemplaza la regla teórica. VAYNER-001 dispara warning si el ratio cae bajo el objetivo de ESE canal. Excepciones declaradas:
  - PILLAR_B en paid ads = 100% CTA por naturaleza (paid social, paid search, YouTube paid) — el ratio no aplica al asset-level pero sí al canal-level: si el operador SOLO usa paid en PILLAR_B, debe haber jabs en otros pilares en el mismo canal o el feed se quema.
  - SEO long-form anchor = jab por naturaleza con `anchor_to_offer` suave; cuenta automáticamente como `content_type: hybrid` sin necesidad de rationale extra.
- **Default documentado 25/25/50 para RRSS orgánico B2C** (FLAG-5, Curso 7, dentro del marco Pattern B): para RRSS **orgánico B2C** el corpus aporta un reparto de referencia **25% viral / 25% captación / 50% conversión** (más agresivo en CTA que el 3:1). **NO sobrescribe el 3:1 ni el mecanismo per-channel** (que es superior y ya contempla ajuste por canal) ni toca el "alarm-stays-on" de VAYNER-001: es un **valor por defecto documentado** para ese canal/segmento, que el operador puede usar como punto de partida y que sigue recalibrándose por la fatiga real medida en Phase 4. Para los demás canales/segmentos rige el default 3:1 ajustado por canal.
- No mezclar `target_awareness_level` arbitrariamente: el long-form puede ser Problem Aware y los derivatives Solution Aware, pero el orden Schwartz se respeta (un derivative no puede asumir Most Aware si el long-form es Unaware)

### Sub-workflow `content-atomizer`

Skill propuesto para V2.

**Inputs**: `pillars.json` + `brand_voice.json` + `language_packs` + `hook_library.json` + un long-form asset texto.

**Algoritmo**:
```
1. Lee long-form, extrae 5-10 puntos clave
2. Para cada formato derivative (thread, carrusel, short, email, quote):
   a. Selecciona hook compatible (channel + force + awareness)
   b. Selecciona language_pack si multi-avatar
   c. Aplica brand_voice.consistency_check_rules al draft
   d. Genera draft del derivative
3. Operador valida y firma
4. Si VOICE-001 falla en cualquier draft → regenerar
```

### Gate G-Phase-2.4
- Cada pilar con `atomization_map` poblado (≥1 long_form + ≥5 derivatives V1)
- Cada derivative con `hook_id_assigned` + `language_pack_id` (si aplica)
- Orden Schwartz respetado entre long_form y derivatives

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + plantillas por formato. Operador escribe el long-form, Claude propone derivatives con hooks de la library. |
| V2 | `content-atomizer` genera N derivatives desde 1 long-form. |
| V3 | Auto + flag inconsistencias de voice. |

---

## 8. Sub-paso 2.5 — Hook Library

### Propósito
Banco reutilizable de **ganchos** (primeras 1–3 oraciones / segundos de un asset). El hook decide si el avatar consume el asset; sin biblioteca de hooks pre-testeada, cada pieza nueva re-inventa el primer segundo y pierde la mayoría de impresiones.

### Output: `hook_library.json`

```json
{
  "hooks": [
    {
      "hook_id": "hook_A_01",
      "template": "problem_agitate_solve | before_after_bridge | aida | pas | curiosity_gap | pattern_interrupt | contrarian | most_people_think | identity_callout | specific_number",
      "text": "El texto exacto del hook (≤2 oraciones / ≤15 segundos en video)",
      "force_attacked": "ongoing_pain | trigger | anxiety | habit | pull",
      "specific_target": "force_id del avatar",
      "awareness_level": "unaware | problem_aware | solution_aware | most_aware",
      "compatible_pillars": ["PILLAR_A"],
      "compatible_channels": ["X", "LinkedIn", "blog_intro"],
      "compatible_formats": ["thread", "article_lead", "ad_copy"],
      "language_pack_compatible": ["language_pack_avatar_1"],
      "brand_voice_check_passed": true,
      "negative_persona_safe": true,
      "performance_data": {
        "uses_count": 0,
        "best_ctr_observed": null,
        "best_engagement_observed": null,
        "last_used": null,
        "status": "untested | tested | winner | retired"
      }
    }
  ],
  "templates_used_count": {
    "problem_agitate_solve": 0,
    "before_after_bridge": 0,
    "...": 0
  }
}
```

### Reglas duras (V1)

- **≥10 hooks por pilar** (40 total mínimo entre los 4 pilares) — sin esto HOOK-001 warning
- ≥4 templates distintos representados (no 40 hooks de "problem_agitate_solve")
- Cada hook con `brand_voice_check_passed: true` (evaluación contra `consistency_check_rules`) — false bloquea el hook del catálogo
- Cada hook con `negative_persona_safe: true` (no matchea ningún `signals_to_detect`) — false bloquea
- `language_pack_compatible` declarado explícitamente (un hook puede ser compatible con N language_packs o solo 1)
- Hook con `awareness_level` distinto al `compatible_pillars[0].force_attacked` natural debe justificarse (ej: hook de "anxiety" en PILLAR_A "ongoing_pain" requiere rationale)

### Templates canónicos (referencia)

| Template | Estructura | Mejor para |
|---|---|---|
| Problem-Agitate-Solve (PAS) | Plantea problema → intensifica → resuelve | Problem Aware, ongoing_pain |
| Before-After-Bridge (BAB) | Estado actual → estado deseado → puente | Solution Aware, pull |
| AIDA | Atención → interés → deseo → acción | Most Aware, ads |
| Curiosity gap | Información incompleta que exige clic | Unaware, RRSS |
| Pattern interrupt | Rompe expectativa con afirmación | Unaware, scroll-stopping |
| Contrarian | Niega creencia popular | Habit, displacement |
| "Most people think X..." | Reframe via expectativa común | Habit, anxiety |
| Identity callout | "Si eres [identidad]..." | Trigger, RRSS — **identidad debe extraerse literal de `buyer_persona.jobs_to_be_done[].social_job`** (A1-ISSUE-2 audit R4); inventar identidad rompe coherencia con Phase 1 |
| Specific number | "73% de [audiencia] no sabe que..." | Problem Aware, autoridad |

### Sub-workflow `hook-library-generator`

Skill propuesto para V2.

**Inputs**: `pillars.json` + `forces_of_progress` + `language_packs` + `brand_voice.json` + `competitor_scan.md` (hooks que ya están saturados en el nicho).

**Algoritmo**:
```
1. Para cada pillar:
   a. Para cada force_id en specific_targets:
      i. Genera N candidate hooks por template (PAS, BAB, AIDA, etc.)
      ii. Aplica brand_voice.consistency_check_rules
      iii. Aplica negative_persona.signals_to_detect (rechaza si match)
      iv. Aplica competitor_voice_avoidance (rechaza si demasiado similar a competidor)
   b. Selecciona top-10 con cobertura ≥4 templates
2. Operador valida, marca winners, retira loser
3. Hooks ganadores se promueven a best_practice con tag 'hook-winner' tras ≥3 uses con CTR > baseline
```

### Gate G-Phase-2.5
- ≥10 hooks por pilar, ≥4 templates representados
- 100% `brand_voice_check_passed: true` y `negative_persona_safe: true`
- `language_pack_compatible` declarado por hook
- Hook library serializada en `content_assets/hooks/library.json` (path absoluto persistido en `content_plan.json`)

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + templates + research competitivo. Operador escribe 10/pilar con Claude proponiendo variaciones. |
| V2 | `hook-library-generator` produce 30/pilar, operador filtra a 10 winners. |
| V3 | Auto + ranking continuo por performance_data acumulada. |

---

## 9. Transversal — Negative persona auto-filter

### Propósito
Antes de que cualquier asset entre al `content_plan.json` o se publique, se evalúa contra `negative_personas.json`. Match = bloqueo automático. Es defensa de honestidad arquitectural (Phase 0.3 declaró a quién NO vender; Phase 2 honra esa declaración).

### Algoritmo (determinístico, no LLM)

```
Para cada asset (long_form o derivative o hook):
  Para cada negative_persona en negative_personas.json:
    Para cada signal in negative_persona.signals_to_detect:
      Si asset.text contiene signal (case-insensitive, fuzzy match opcional):
        - Marcar asset.negative_persona_safe = false
        - Registrar en negative_filter_report.json: { asset_id, negative_persona_id, signal_matched, action: negative_persona.action_when_detected }
        - Si action == "auto-disqualify" → bloquear asset del plan
        - Si action == "manual review" → flag al operador, no bloquea automáticamente
        - Si action == "redirect to free content" → mover asset a tier "free funnel only"
```

### Output: `negative_filter_report.json` (acumulado por ciclo de Phase 2)

```json
{
  "evaluated_at": "ISO date",
  "assets_evaluated_count": 0,
  "assets_blocked_count": 0,
  "blocks": [
    {
      "asset_id": "...",
      "negative_persona_id": "neg_1",
      "signal_matched": "...",
      "action": "auto-disqualify",
      "blocked_at": "ISO date"
    }
  ]
}
```

### Reglas
- No se permite `operator_signoff` en `content_plan.json` si `assets_blocked_count > 0` sin que cada bloqueo tenga `decision_record` justificando override (rara vez correcto)

---

## 10. Output canónico de Phase 2: `content_plan.json` + `content_assets/`

### `content_plan.json` (consolidación)

```json
{
  "plan_id": "plan_v1_YYYYMMDD",
  "linked_to": {
    "strategy_id": "strategy_uuid",
    "strategy_version": 1,
    "offer_id": "offer_v1_YYYYMMDD",
    "product_brief_v2_path": "...",
    "primary_avatar_id": "avatar_1",
    "covers_avatars": ["avatar_1", "avatar_2"],
    "multi_avatar_strategy": "single_avatar | unified_C_clean | unified_C_language_packs | unified_C_avatar_specific_bonuses | separate_strategies"
  },
  "brand_voice": { "...del 2.0..." },
  "content_mix": { "...del 2.1..." },
  "channel_journey_matrix": { "...del 2.2..." },
  "pillars": [ "...del 2.3..." ],
  "atomization_map": { "...del 2.4..." },
  "hook_library_path": "content_assets/hooks/library.json",
  "language_pack_assignments_global": {
    "avatar_1": "language_pack_avatar_1",
    "avatar_2": "language_pack_avatar_2"
  },
  "negative_persona_filter_report_path": "content_assets/_meta/negative_filter_report.json",
  "phase_2_handoff_coverage": {
    "objections_uncovered_addressed": [
      { "phase_1_uncovered_id": "obj_3", "covered_by_pillar": "PILLAR_C", "covered_by_asset_ids": ["asset_pillar_C_002"] }
    ],
    "anxieties_uncovered_addressed": [],
    "habits_unattacked_addressed": [],
    "pulls_underamplified_addressed": [],
    "coverage_complete": true
  },
  "phase_3_handoff": {
    "tracking_requirements": {
      "utm_scheme_per_pillar": { "PILLAR_A": "utm_campaign=pillar_a_{slug}&utm_source={channel}&utm_medium={format}" },
      "pixel_events_required": ["page_view", "scroll_50", "cta_click", "lead_form_submit"],
      "conversion_event_definition": "qué cuenta como conversión (ej: lead_form_submit con email válido)"
    },
    "exclusion_lists_needed": [
      { "negative_persona_id": "neg_1", "platform_list_name": "negative_neg_1_excl" }
    ],
    "audience_targeting_per_channel": {
      "Meta": "ICP B2C_cluster: behavioral_signals + interests; exclude exclusion_lists",
      "LinkedIn": "ICP B2B_account: industry + company_size + buying_stage; exclude deal_breakers",
      "Google Ads": "keywords transactional+comparative (de Phase 0.2); negative_keywords desde negative_personas"
    },
    "publishing_calendar_skeleton": [
      { "week": 1, "channel": "blog", "pillar_id": "PILLAR_A", "asset_id": "asset_pillar_A_001", "scheduled_for": "ISO date" }
    ],
    "evergreen_reimpact_sequences": [
      {
        "pillar_id": "PILLAR_C",
        "targets": "leads que consumieron pero no convirtieron",
        "angle_switch": "misma fuerza, distinto beneficio (cambiar beneficio comunicado, no producto)",
        "ticket_tier": "low | medium | high",
        "urgency_window": "low: 15min-1h | medium: 48h | high: 3-7d",
        "note": "G18, Curso 6 — no requiere re-build del plan; reusa assets existentes. Phase 3 lo agenda como secuencia evergreen_reimpact."
      }
    ]
  },
  "signal_rules_triggered": [],
  "metadata": {
    "hours_invested": 0,
    "usd_invested": 0,
    "completed_at": "ISO date",
    "operator_signoff": true,
    "phase_3_ready": true
  }
}
```

### `content_assets/` (file system layout)

```
content_assets/
├── _meta/
│   ├── brand_voice.json
│   ├── content_mix.json
│   ├── channel_journey_matrix.json
│   ├── pillars.json
│   ├── atomization_map.json
│   └── negative_filter_report.json
├── hooks/
│   └── library.json
├── pillars/
│   ├── pillar_A/
│   │   ├── long_form/
│   │   │   └── asset_pillar_A_001.md
│   │   └── derivatives/
│   │       ├── thread_X/
│   │       ├── carousel_IG/
│   │       ├── short_TikTok/
│   │       ├── email/
│   │       └── quote_graphic/
│   ├── pillar_B/
│   ├── pillar_C/
│   └── pillar_D/
└── emails/
    └── (sequence/campaign-level emails referenciados desde pillars)
```

---

## 11. Gate global G-Phase-2

Phase 2 se cierra cuando:
- Sub-gates 2.0, 2.1, 2.2, 2.3, 2.4, 2.5 cerrados
- `content_plan.json` consolidado, paths apuntando a assets reales en `content_assets/`
- 4 pilares poblados con cobertura 100% de `phase_2_handoff` de Phase 1
- `content_mix.target_mix` con suma 100 ±2 y delta justificado si >30 puntos vs demand
- TODOS los canales en `business_context.channel` cubiertos por matrix o con `decision_record`
- `hook_library.json` con ≥10 hooks/pilar, ≥4 templates, 100% brand_voice + negative_persona safe
- `negative_filter_report.assets_blocked_count: 0` (o cada bloque con override `decision_record`)
- Phase 3 handoff (UTM scheme, pixel events, exclusion lists, audience targeting per channel, calendar skeleton) poblado
- `research_metadata.hours_invested` y `usd_invested` cuantificados
- Operador firma `metadata.operator_signoff: true`

---

## 12. Capa transversal — Signal rules de Phase 2

Reglas heurísticas que disparan contra outputs estructurados. Persistidas como `best_practice_record` con `domain: workflow`, `scope: project:business/marketing-os`, prefijo `SIGNAL-RULE` en título (per lesson `17112600` — el enum `domain` de pretel-os no acepta `signal-rule`).

```json
{
  "rules": [
    {
      "id": "VOICE-001",
      "applicable_phase": "phase-2.0 + transversal",
      "condition": "asset.brand_voice_check_passed == false",
      "severity": "alert",
      "signal": "Asset viola brand_voice.consistency_check_rules",
      "implication": "Regenerar el asset aplicando lexicon.preferred_terms y eliminando prohibited_terms. No publicar hasta pasar.",
      "auto_action": "block asset from content_plan"
    },
    {
      "id": "CONTENT-001",
      "applicable_phase": "phase-2.3",
      "condition": "pillars.length < 4 OR any pillar.force_attacked missing from {ongoing_pain, trigger, anxiety, habit}",
      "severity": "alert",
      "signal": "Plan no cubre las 4 fuerzas — falta pilar",
      "implication": "Cada fuerza requiere mecanismo de contenido propio. Plan incompleto convierte solo a parte del avatar.",
      "auto_action": "block Phase 2.4 entry"
    },
    {
      "id": "CONTENT-002",
      "applicable_phase": "phase-2.3",
      "condition": "phase_2_handoff_coverage.coverage_complete == false",
      "severity": "alert",
      "signal": "Hay uncovered de Phase 1 sin asset que los resuelva",
      "implication": "Phase 1 delegó explícitamente N objections/anxieties/habits/pulls a Phase 2 vía copy. Si Phase 2 no los cubre, el gap nunca se cierra. Mapear cada uncovered a ≥1 pilar+asset.",
      "auto_action": "block Phase 2 close"
    },
    {
      "id": "CONTENT-003",
      "applicable_phase": "phase-2.2",
      "condition": "any channel in business_context.channel NOT in channel_journey_matrix AND NOT in channels_unused_explanation",
      "severity": "warning",
      "signal": "Canal declarado en Phase 0.1 sin contenido planeado ni explicación",
      "implication": "Operador declaró el canal pero no lo usa — o falta plan o el canal debió desactivarse en Phase 0.1.",
      "auto_action": "require decision_record"
    },
    {
      "id": "CONTENT-004",
      "applicable_phase": "phase-2.1",
      "condition": "content_mix.demand_alignment_delta.max_abs_delta_pct > 30 AND justification_if_max_delta_gt_30 is empty",
      "severity": "warning",
      "signal": "Mix de awareness se desvía >30 puntos de demand sin justificación",
      "implication": "Posible que el operador esté priorizando intuición sobre evidencia. Justificar con offer_strategy_tag o reconsiderar.",
      "auto_action": "require decision_record"
    },
    {
      "id": "CONTENT-005",
      "applicable_phase": "phase-2.5",
      "condition": "any pillar.hooks_count < 10",
      "severity": "warning",
      "signal": "Pilar con <10 hooks",
      "implication": "Sin variedad mínima de hooks, todos los assets del pilar terminan con la misma apertura. Hook fatigue acelerado.",
      "auto_action": "warn before Phase 2 close"
    },
    {
      "id": "ATOMIZATION-001",
      "applicable_phase": "phase-2.4",
      "condition": "any pillar.atomization.derivatives.length < 5",
      "severity": "warning",
      "signal": "Pilar con <5 derivatives por long-form",
      "implication": "Costo por pieza prohibitivo. Atomizar mínimo 1:5 para sostener cadencia V1.",
      "auto_action": "warn before Phase 2.5 entry"
    },
    {
      "id": "ATOMIZATION-002",
      "applicable_phase": "phase-2.4",
      "condition": "any derivative.format == 'email' AND (derivative.subject_line is null OR subject_line.variants is empty OR any subject_line.variants[i].length > 40 OR subject_line.variants.length > 5 OR subject_line.ab_test_pair is empty)",
      "severity": "alert",
      "signal": "Derivative de email sin subject_line poblado o fuera de límites (≤5 variantes, cada una ≤40 chars, ab_test_pair presente)",
      "implication": "El subject line es el hook del canal email y decide la tasa de apertura (Curso 6, G3). Un derivative format=email sin subject_line válido no se publica. Poblar variants (≤5, ≤40 chars c/u), pre_header, one_variant_with_emoji, spam_words_checked y ab_test_pair.",
      "auto_action": "block email derivative publication"
    },
    {
      "id": "FORCES-001",
      "applicable_phase": "phase-2.3",
      "condition": "any force in {ongoing_pain, trigger, anxiety, habit} has zero assets across all pillars",
      "severity": "alert",
      "signal": "Una fuerza con 0 contenido mapeado",
      "implication": "Equivalente a CONTENT-001 pero a nivel asset, no pillar. Cobertura incompleta.",
      "auto_action": "block Phase 2 close"
    },
    {
      "id": "NEGATIVE-001",
      "applicable_phase": "phase-2 transversal",
      "condition": "negative_filter_report.assets_blocked_count > 0 AND any block without decision_record override",
      "severity": "alert",
      "signal": "Asset matchea negative_persona signal sin override justificado",
      "implication": "Honestidad arquitectural: Phase 0.3 declaró a quién NO vender. Asset que apela a negative_persona viola el contrato. Regenerar o registrar override con motivo.",
      "auto_action": "block asset publication"
    },
    {
      "id": "COVERAGE-001",
      "applicable_phase": "phase-2.3",
      "condition": "any avatar in linked_to.covers_avatars without ≥1 pillar where language_pack_assignments includes avatar_id",
      "severity": "alert",
      "signal": "Avatar declarado en covers_avatars sin asset que use su language_pack",
      "implication": "Si la oferta cubre N avatars (Phase 1) pero el contenido habla solo a 1, el resto no convierte. Asignar language_packs a ≥1 pilar por avatar.",
      "auto_action": "block Phase 2 close"
    },
    {
      "id": "TRIGGER-ALIGN-001",
      "applicable_phase": "phase-2.3",
      "condition": "risk_urgency_displacement.urgency.aligned_with_trigger != null AND PILLAR_B.specific_targets does NOT include that trigger_id",
      "severity": "warning",
      "signal": "Urgency de la oferta anclada a trigger X pero PILLAR_B no lo amplifica",
      "implication": "Coherencia rota entre oferta y campaña que la captura. PILLAR_B (triggers) debe incluir el trigger sobre el que se construyó la urgency. Sin esto, la urgency es invisible en el contenido.",
      "auto_action": "require pillar_B specific_targets update or decision_record"
    },
    {
      "id": "HANDOFF-001",
      "applicable_phase": "phase-2 close",
      "condition": "phase_3_handoff.tracking_requirements OR exclusion_lists_needed OR audience_targeting_per_channel is empty",
      "severity": "alert",
      "signal": "Phase 3 handoff incompleto",
      "implication": "Phase 3 no puede arrancar sin tracking + exclusion lists + targeting per channel. Cerrar Phase 2 sin esto traslada el trabajo a Phase 3 y rompe el contrato.",
      "auto_action": "block Phase 2 close"
    },
    {
      "id": "REINFORCE-001",
      "applicable_phase": "phase-2.3 + phase-2.4",
      "condition": "asset.force_id IN pillar.forces_already_covered_by_offer.reinforces[] AND phrasing_overlap_with_offer_statement < 50%",
      "severity": "warning",
      "signal": "Asset cubre fuerza ya atacada por la oferta pero usa phrasing >50% distinto al offer_statement",
      "implication": "Riesgo de disonancia entre copy del contenido y mensajería de la oferta. Reusar las palabras del offer_statement / risk_reversal.statement / displacement_framing.replacement_narrative cuando la fuerza ya está cubierta. Si el operador conscientemente quiere reframing, registrar decision_record. Audit R4 A1-ISSUE-1.",
      "auto_action": "warn before Phase 2 close; require operator_acknowledgment or decision_record"
    },
    {
      "id": "VAYNER-001",
      "applicable_phase": "phase-2.4",
      "condition": "for any pillar in {organic channels}: value:cta ratio < ratio_objetivo_del_canal (default 3:1 [Context-Adjusted Threshold], ajustado por la fatiga real medida en Phase 4 por canal/avatar)",
      "severity": "warning",
      "signal": "Pilar bajo el ratio jab/right-hook objetivo de ese canal",
      "implication": "Audiencia se quema si el feed orgánico tiene demasiado CTA — pero el umbral depende del canal/audiencia, no es 3:1 universal. Recomponer atomization con más derivatives content_type=value. El objetivo se recalibra con el CTR decay observado (Phase 4). Excepción PILLAR_B en paid ads no aplica.",
      "auto_action": "warn before Phase 2 close"
    },
    {
      "id": "STRATEGY-LINK-001",
      "applicable_phase": "phase-2 close",
      "condition": "content_plan.linked_to.strategy_id is null OR (multi_avatar_strategy == 'unified_C_*' AND strategy.covers_avatar_ids != offer_spec.covers_avatars) OR (multi_avatar_strategy == 'separate_strategies' AND content_plan covers >1 avatar)",
      "severity": "alert",
      "signal": "content_plan no está anclado a una estrategia válida, o la granularidad no coincide con multi_avatar_strategy",
      "implication": "El plan debe pertenecer a una strategies row (D-010). En separate_strategies, un plan = un avatar; en unified_C_*, el covers de la estrategia debe igualar el covers del offer. Sin esto, los resultados/learnings de Phase 5 no se atribuyen a la estrategia correcta.",
      "auto_action": "block Phase 2 close"
    }
  ]
}
```

---

## 13. Re-trigger de Phase 2

Phase 2 se re-ejecuta cuando:
- Phase 0 hace re-trigger (avatar cambió → forces nuevas → pilares nuevos)
- Phase 1 hace re-trigger (oferta nueva → `phase_2_handoff` nuevo → pilares re-mapeados)
- Phase 5 detecta engagement rate por pilar cae ≥40% sostenido en 14 días (hook fatigue o cambio de awareness)
- Phase 5 detecta CTR por hook template cae homogéneamente (saturación de patrón en el feed del avatar)
- Operador declara cambio de brand_voice (raro, requiere `decision_record` por todos los assets afectados)

**Sin refresh por calendario** (coherente con el principio de Phase 0/5: actuar por evidencia, no por reloj). El contenido se refresca cuando hay **señales reales de fatiga** (engagement/CTR cayendo, saturación de hooks), no por una fecha. Si se quiere una cadencia mínima, que sea un **recordatorio de revisión** barato — no un re-build automático.

**Re-impacto evergreen (no es re-trigger de plan):** distinto de un re-trigger, para leads que consumieron pero **no convirtieron** se generan derivatives de **re-impacto** que atacan la **MISMA fuerza con un ángulo motivacional distinto** (cambiar el beneficio comunicado, no el producto). Vive en PILLAR_C (ver Sección 6) y **no requiere re-build del plan** — reusa assets existentes. Urgencia calibrada por ticket: bajo 15 min–1 h, medio 48 h, alto 3–7 días (Curso 6, G18).

Cada re-trigger queda como `decision_record` con motivo + evidencia.

---

## 14. Decisiones cerradas en Phase 2 v1.0

| # | Decisión | Resolución |
|---|---|---|
| D1 | ¿Brand voice se declara antes o durante 2.1? | **Antes (sub-paso 2.0)**. Gate independiente. Paralelo a Phase 0.1 y Phase 1.3 — decisión humana irreducible. |
| D2 | ¿Pilares por canal o por fuerza? | **Por fuerza (Christensen)**. 4 pilares fijos: ongoing_pain, trigger, anxiety, habit. Canal y formato son atributos, no organización. |
| D3 | Ratio de atomización mínimo | **1:5** (1 long-form → ≥5 derivatives) en V1. Vaynerchuk 1:64 es target V3. |
| D4 | Hooks mínimos por pilar | **≥10**, ≥4 templates distintos. <10 → HOOK-001 warning. |
| D5 | Cobertura de `phase_2_handoff` | **100% obligatoria**. Cada uncovered de Phase 1 mapea a ≥1 asset; CONTENT-002 bloquea Phase 2 close si falta. |
| D6 | Negative persona filter | **Determinístico, no LLM**. Algoritmo de string/signal match con acción declarada en `negative_personas.action_when_detected`. |
| D7 | Awareness mix vs demand distribution | **Función del `offer_strategy_tag`** (DEMAND-001/002 de Phase 0.2). Default = espejo ±10%; capture_existing_demand = sesgo Most/Solution Aware; create_demand = sesgo Problem/Unaware. |
| D8 | Multi-avatar en contenido | **Cobertura obligatoria de TODOS los `covers_avatars`** (COVERAGE-001). Cada avatar con ≥1 pilar que use su language_pack. |
| D9 | PILLAR_B alineación con urgency | **Coherencia obligatoria** si `urgency.aligned_with_trigger != null` (TRIGGER-ALIGN-001 warning si no). |
| D10 | Phase 3 handoff completo en Phase 2 close | **Sí**: tracking, exclusion lists, audience targeting, calendar skeleton. HANDOFF-001 bloquea Phase 2 sin esto. |
| D11 | Reinforce vs resolve por pilar (audit R4) | **Distinción obligatoria**. Cada pilar declara `forces_already_covered_by_offer.{reinforces, does_not_address}` derivado de `offer_spec.stack.force_coverage`. REINFORCE-001 dispara warning si phrasing diverge >50% del offer_statement en una fuerza ya cubierta. |
| D12 | JTBD anclado en brand voice + pilares + hooks (audit R4) | `archetype_rationale` cita `job_id` + `emotional_job` + `social_job` (regla dura, no ejemplo). PILLAR_A `jtbd_anchor` con `frustration_with_current` literal. Hook "identity callout" extrae identidad de `social_job`. |
| D13 | Vaynerchuk ratio 3:1 jab:right-hook (audit R4) | Cada derivative declara `content_type ∈ {value, cta, hybrid}`. En canales orgánicos, ratio mínimo 3:1 value:cta por pilar. VAYNER-001 dispara warning. PILLAR_B en paid = excepción. SEO long-form anchor = hybrid automático. |
| D14 | PILLAR_D consume `displacement_framing` literal (audit R4) | `displacement_inheritance` con `habit_being_displaced_id`, `replacement_narrative_literal`, `cost_of_continuing_current_path_literal` heredados de Phase 1.3. `replacement_narrative` debe aparecer textualmente en ≥1 derivative por ciclo. |
| D15 | Pertenencia a Estrategia (D-009/D-010, 2026-06-06) | Cada `content_plan.json` pertenece a una `strategies` row vía `linked_to.strategy_id` + `strategy_version`. En `separate_strategies` (default) Phase 2 corre una vez por avatar (un plan = un avatar); en `unified_C_*` un plan cubre varios avatars. STRATEGY-LINK-001 bloquea si el plan no se ancla o la granularidad no coincide. `separate_strategies` reemplaza `separate_offers` en todo el spec. |

---

## 15. Lecciones registradas en Phase 2 spec design

| ID | Lección |
|---|---|
| L1 | Pilares organizados por fuerza (no por canal/tema) hereda la rigurosidad de Christensen al contenido. |
| L2 | Atomización 1:5 mínimo: el costo por pieza individual mata el plan en semana 3 sin ratio mínimo declarado. |
| L3 | Hook library separada del pillar permite testing + reuso cross-pillar; meter hooks dentro de cada pillar perpetúa re-invención. |
| L4 | Brand voice declarado ANTES de cualquier generación = paralelo a Business Context Gate y Risk Reversal. Patrón "declaración humana irreducible". |
| L5 | Awareness mix no es 1:1 con demand distribution — es función de `offer_strategy_tag` (capture vs create demand). |
| L6 | `phase_2_handoff` de Phase 1 es contrato vinculante, no sugerencia. Sin cobertura forzada, los gaps se acumulan ciclo tras ciclo. |
| L7 | Negative persona filter debe ser determinístico, no LLM: signal match es testeable, audit-able y rápido. |
| L8 | Coherencia entre `urgency.aligned_with_trigger` (Phase 1.3) y PILLAR_B (Phase 2.3) es heredada — sin amplificación en contenido, la urgency es invisible. |
| L9 | Phase 3 handoff completo en Phase 2 close evita "lo veo en Phase 3" anti-pattern. Tracking, exclusion lists, audience targeting son outputs de Phase 2, no descubrimientos de Phase 3. |
| L10 | Canal declarado en Phase 0.1 sin uso en Phase 2 = falla de declaración temprana (mejor desactivar el canal en 0.1 que arrastrarlo). |
| L11 | Schwartz son 5 awareness levels (Unaware / Problem / Solution / Product / Most Aware), pero Marketing OS los colapsa a 4 alineado con Phase 0.2: Product+Most → "Most Aware". Razón: en research de keywords el delta entre Product Aware y Most Aware no es discriminable con Keyword Planner — ambos son intent transaccional. La distinción se reabrirá en V2 si Phase 4 muestra que el merge oculta señal. (Audit R4 A1-ISSUE-7.) |
| L12 | Reinforce vs resolve evita el modo de fallo "PILLAR_C produce 5 piezas sobre money-back redundantes con el offer_statement". Distinguir entre "qué la oferta ya cubre" (reusar phrasing) y "qué Phase 1 delegó a copy" (atacar con copy propio). |
| L13 | Vaynerchuk no es solo atomización (1 keynote → N piezas); el corazón es el ratio jab:right-hook. Sin regla 3:1 en canales orgánicos, el feed se quema en ~4 semanas independientemente de la calidad de cada pieza. |
| L14 | `displacement_framing` de Phase 1.3 es contrato heredado por PILLAR_D, no inspiración. El `replacement_narrative` debe aparecer literal en ≥1 derivative para garantizar consistency cross-asset (lector que ve la oferta y el contenido reconoce la misma frase). |

---

## 16. Pendientes y diferidos

### Pendientes para implementación V1
- Skill `content-pillars-builder` registrado en pretel-os (`domain: workflow`)
- Skill `content-atomizer` registrado en pretel-os
- Skill `hook-library-generator` registrado en pretel-os
- 16 signal rules sembradas (VOICE-001, CONTENT-001/002/003/004/005, ATOMIZATION-001/002, FORCES-001, NEGATIVE-001, COVERAGE-001, TRIGGER-ALIGN-001, HANDOFF-001, REINFORCE-001, VAYNER-001, STRATEGY-LINK-001) como `best_practice_record` con `domain: workflow`
- Lookup table `channel_function` (Sección 5, "función natural de canal") registrada como `best_practice` con `domain: workflow`
- Lookup table `atomization_ratio_minimum_per_anchor_format` (Sección 7) registrada como `best_practice`
- Template library inicial de hooks (9 templates de la tabla en 2.5) registrada como best_practices con tags `['hook-template']`

### Diferidos
- Performance ranking de hooks (sub-paso 2.5 `performance_data`) requiere datos de Phase 4 — activable a partir del ciclo 2
- Auto-ranking de derivatives por CTR observado: diferido a V2 con sub-workflow
- Promoción de hooks a `best_practice` con tag `hook-winner` (≥3 uses, CTR > baseline): proceso V2
- A/B testing systematic de hook templates: diferido a Phase 5 (Ajustar) — Phase 2 solo provee la library
- B2B content adaptado a DMU multi-role (champion vs decision_maker vs end_user) con copy distinto: activable cuando inicie Alfredo-as-freelance (GAP-4 ya tracked en Phase 0)

---

## 17. Apéndice — checklist operacional V1

Para el primer ciclo manual de Phase 2 con un producto real:

```
[ ] G-Phase-2-PRE: 14 checks de entrada verificados (incluye check 11 force_coverage + check 12 displacement_framing + check 14 strategy_id disponible)
[ ] 2.0 — brand_voice.json declarado (archetype + tone + lexicon + ≥3 consistency_check_rules)
[ ] 2.0 — archetype_rationale cita JTB job_id + emotional_job + social_job (audit R4)
[ ] 2.0 — brand_promise (CPM "Ayudo a [cliente] a [logro] vía [método] sin [dolor]") declarado — FLAG-6
[ ] 2.0 — compatibilidad voice ↔ language_packs verificada (conflictos listados o array vacío)
[ ] 2.0 — decision_record en pretel-os con tag ['brand-voice', '{product_slug}', 'archetype'] registrado
[ ] 2.0 — operator_signoff: true en brand_voice.json
[ ] 2.1 — content_mix.json con 4 % sumando 100 ±2
[ ] 2.1 — offer_strategy_tag extraído de Phase 0.2 signal rules
[ ] 2.1 — si max_abs_delta_pct > 30 → decision_record con justificación
[ ] 2.2 — channel_journey_matrix.json con cada canal de business_context.channel cubierto o explicado
[ ] 2.2 — KPI por entrada de matrix declarado
[ ] 2.2 — 5 customer journey stages cubiertos (o documentado por qué retención/advocacy se omiten en pre-PMF)
[ ] 2.3 — pillars.json con 4 pilares (uno por fuerza)
[ ] 2.3 — cada pilar con specific_targets a force_id real del avatar
[ ] 2.3 — cada pilar con jtbd_anchor (job_id + frustration_with_current literal + social_job literal) — audit R4
[ ] 2.3 — cada pilar con forces_already_covered_by_offer.{reinforces, does_not_address} derivado de offer.stack.force_coverage — audit R4
[ ] 2.3 — PILLAR_D con displacement_inheritance (3 campos literales heredados de Phase 1.3) — audit R4
[ ] 2.3 — cobertura 100% de phase_2_handoff (objections/anxieties/habits/pulls uncovered → asset_ids)
[ ] 2.3 — si B2B: cada pilar con dmu_role_target
[ ] 2.3 — PILLAR_B coherente con urgency.aligned_with_trigger (si aplica)
[ ] 2.3 — cada avatar de covers_avatars tiene ≥1 pilar con su language_pack
[ ] 2.4 — atomization_map con ≥1 long_form + ≥5 derivatives por pilar
[ ] 2.4 — cada derivative con hook_id_assigned existente + language_pack_id + content_type ∈ {value, cta, hybrid} — audit R4
[ ] 2.4 — Vaynerchuk ratio ≥3:1 value:cta por pilar en canales orgánicos (VAYNER-001) — audit R4
[ ] 2.4 — cada derivative format=email con subject_line poblado (≤5 variantes ≤40 chars + pre_header + 1 con emoji + spam_words_checked + ab_test_pair) — ATOMIZATION-002 (G3)
[ ] 2.4 — cada derivative format=ad_copy con char_limits_per_platform (Google Ads ≤30/≤90) — G4
[ ] 2.4 — cada derivative de video con video_script_structure por intervalos (hook_id alimenta el primer intervalo) — G6
[ ] 2.4 — long_form SEO de PILLAR_A con structured_data (schema_type + jsonld_validated) si aplica — G5
[ ] 2.4 — PILLAR_D: replacement_narrative_literal aparece textual en ≥1 derivative — audit R4
[ ] 2.5 — hook_library.json con ≥10 hooks/pilar y ≥4 templates representados
[ ] 2.5 — 100% hooks con brand_voice_check_passed + negative_persona_safe
[ ] 2.5 — hooks serializados en content_assets/hooks/library.json
[ ] Transversal — negative_filter_report con assets_blocked_count == 0 (o overrides con decision_record)
[ ] Phase 3 handoff completo: UTM scheme + pixel events + exclusion_lists_needed + audience_targeting_per_channel + calendar_skeleton
[ ] Signal rules evaluadas: ninguna alert sin resolver
[ ] content_plan.json consolidado, paths apuntando a content_assets/ reales
[ ] content_plan.linked_to.strategy_id + strategy_version poblados; granularidad coincide con multi_avatar_strategy (STRATEGY-LINK-001)
[ ] hours/usd invertidos cuantificados
[ ] operator_signoff: true
```
