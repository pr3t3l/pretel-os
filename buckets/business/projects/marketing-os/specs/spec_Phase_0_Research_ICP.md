# Phase 0 — Business Context + Market Research + ICP

**Project**: business/marketing-os
**Phase ID**: phase-0
**Status**: spec drafted, post-audit v1.5 + alignment patches (GAP-AL1, GAP-AL2)
**Last updated**: 2026-06-01
**Implementation correction:** This methodology now targets `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase), not a Python/FastMCP module inside `pretel-os`. Persist outputs in `project_phase_artifacts`, decisions in `project_decisions`, and learnings in `project_lessons`. Legacy references to handlers, n8n, or pretel-os DB writes are methodology/history, not MVP runtime.

**Audit reference**:
- `audit_marketing_os_phase_0.md` (2026-05-10) — Categoría A integrada
- Auditoría alineación Phase 0 ↔ Phase 1 (2026-05-10) — GAP-AL1 (`target_cac_usd` persistido), GAP-AL2 (`competitive_landscape.pricing_tiers[]` estructurado)

---

## 0. Contexto y propósito

Phase 0 es el cimiento sobre el que descansa el Marketing Lifecycle completo. Su objetivo: producir un conjunto completo de artefactos que cualquier fase posterior necesita para no operar a ciegas. **Sin un Phase 0 honesto, todo el trabajo posterior amplifica suposiciones equivocadas a escala.**

**Output canónico**: `product_brief_v2.json` — input contract de Phase 1 (Oferta).

### Capa Foundation (agnóstica del avatar) vs capa por-avatar

Phase 0 se divide en dos capas conceptuales (ver `Overall_WF.md` §"Canonical Project Hierarchy"):

- **Foundation — agnóstica del avatar (sub-pasos 0.1, 0.2, 0.2.5).** Business Context (La Idea), Demand Quantification (El Mercado) e ICP (El Segmento) describen el proyecto, el mercado y el segmento. Son **idénticos sin importar a qué avatar le hables después** y se calculan **una sola vez por proyecto**, compartidos por todos los avatars. Viven a nivel `projects`, con `avatar_id` null.
- **Por-avatar — empieza en 0.3.** Buyer Persona (universal del proyecto) + Avatars (unidades de orquestación independientes). Aquí arranca la bifurcación: cada avatar tendrá luego su propia estrategia (Phase 1→5) versionada en el tiempo.

Esta separación es lo que permite la **orquestación paralela de múltiples avatars**: una base común barata + N loops por-avatar encima de ella.

**Principios operacionales**:
- Hipótesis del operador SE PRESERVAN en `operator_hypotheses_original`; no se sobrescriben con evidencia
- Si todas las hipótesis se confirmaron → research superficial (signal rule EVIDENCE-001)
- ICP (organización/cluster) y Buyer Persona (individuo) son artefactos separados
- Negative persona es artefacto estructurado, no prosa
- Forces of Progress reemplaza purchase_triggers (incluye fuerzas de freno: anxiety + habit)

---

## 1. Estructura: 5 sub-pasos secuenciales + capa transversal

| Sub-paso | Output | Estimado V1 | Manual / automatizable |
|---|---|---|---|
| 0.1 — Business Context Gate | `business_context.json` | 5–15 min | Manual siempre |
| 0.2 — Cuantificación de demanda (con awareness mapping) | `demand_quantification.md` | 1–3 h | Híbrido V1, sub-workflow V2 |
| 0.2.5 — ICP layer | `icp.json` | 30–60 min | Manual V1, drafted V2 |
| 0.3 — Persona + Avatar + JTBD + Forces + Negative | 5 artefactos | 3–5 h | Híbrido V1, drafted V2 |
| 0.4 — Competencia segmentada por canal | `competitor_scan.md` | 2–3 h | Híbrido V1, drafted V2 |
| **Transversal** — `signal_rules.json` | Reglas heurísticas activas | continuo | best_practices con `domain: signal-rule` |

Cada sub-paso tiene su propio gate. Si uno falla, no avanza el siguiente.

---

## 2. Input contract — `product_brief.json` v1.5

Lo que el operador entrega antes de que arranque Phase 0.

```json
{
  "product": {
    "name": "string",
    "description": "string (1-3 oraciones)",
    "url_or_artifact": "URL al producto real o sample",
    "price_point_usd": 0.00,
    "delivery_format": "digital_download | physical | service",
    "expected_repeat_rate": "one-shot | occasional | subscription | recurring",
    "expected_ltv_usd": 0.00,
    "expected_ltv_basis": "1-2 oraciones — cómo estimaste el LTV (precio × repeat × retention − costo)",
    "target_cac_usd": null,
    "target_cac_basis": "auto:ltv/3 | manual:operator_override — si null al cierre de Phase 0, el handler autocalcula expected_ltv_usd / 3 y persiste en product_brief_v2.json"
  },
  "marketing_objective": {
    "primary": "leads | sales | MQL | brand-awareness | retention",
    "primary_kpi": "ej: 10 ventas/mes | 50 leads/semana | $5K MRR",
    "horizon_months": 0
  },
  "operator_hypotheses": {
    "audience": "free-text — corazonada de quién compra",
    "audience_critical": true,
    "problem": "free-text — qué problema crees que resuelve",
    "problem_critical": true,
    "competitors": ["nombre o URL"]
  },
  "constraints": {
    "languages": ["es", "en"],
    "geographies": ["US", "MX"],
    "research_budget_hours": 0,
    "research_budget_usd": 0
  }
}
```

**Cambios v1.5 vs v1**:
- `expected_ltv_usd` + `expected_repeat_rate` + `expected_ltv_basis` obligatorios (GAP-5)
- `marketing_objective` obligatorio (Big School Fase 1, gap del currículum)
- `audience_critical` y `problem_critical` flags — habilitan signal rule de hipótesis críticas refutadas (GAP-17)
- `target_cac_usd` + `target_cac_basis` agregados (GAP-AL1, audit 2026-05-10) — si `null` al cierre de Phase 0, el handler autocalcula `expected_ltv_usd / 3` y persiste el valor en `product_brief_v2.json`. El operador puede overridear vía `decision_record`. Sin esto, ECONOMICS-001 en Phase 1 G-PRE falla por null reference en lugar de por unit economics.

---

## 3. Sub-paso 0.1 — Business Context Gate

### Propósito
Bloquear el resto de Phase 0 hasta que el operador declare explícitamente el frame del negocio. Sin esto, todo el research queda mal calibrado: B2B vs B2C cambia ciclo, lenguaje, canales y métricas.

### Output: `business_context.json`

```json
{
  "business_type": "B2B | B2C | hybrid",
  "sales_cycle": "impulsivo | reflexivo | mixto",
  "channel": "online_only | online_offline | offline_only",
  "monetization_model": "transaccional | suscripción | leadgen | afiliación | servicio",
  "market_scope": "local | regional | nacional | internacional",
  "business_type_evidence": "1-2 oraciones — por qué esa clasificación",
  "implications_acknowledged": [
    "ej: 'B2C impulsivo → copy emocional, no racional'",
    "ej: 'Hooks visuales > argumentos racionales'",
    "ej: 'CTA inmediato, no funnel largo'"
  ],
  "dmu_required": false
}
```

`dmu_required` se setea automáticamente a `true` cuando `business_type === "B2B"`. Esto activa el output `dmu.json` adicional en sub-paso 0.3 (GAP-4).

### Lectura previa de pretel-os
- `decisions where project='marketing-os' and tags @> ['business-context']`
- `lessons where applicable_buckets @> ['business'] and tags @> ['b2b' or 'b2c']`
- `best_practice_search(domain='signal-rule', applicable_phase='phase-0.1')`

### Escrituras
- `decision_record` si hay ambigüedad real en la clasificación

### Gate G-Phase-0.1
- Cada campo poblado, ningún placeholder
- `business_type_evidence` es una oración real, no "obvio"
- ≥2 implicaciones explícitas escritas

### V1/V2/V3
| Versión | Quién decide | Por qué |
|---|---|---|
| V1, V2, V3 | **Operador siempre** | Es declaración del frame de negocio. Nunca se automatiza. |

---

## 4. Sub-paso 0.2 — Cuantificación de demanda

### Propósito
Pasar de "creo que hay mercado" a números duros: TAM/SAM/SOM cuantificados + búsquedas mensuales por intención + mapping a awareness levels (Schwartz).

### Output: `demand_quantification.md` — 3 secciones obligatorias

**A. Demanda digital (intención activa) con awareness mapping**

Tabla con mínimo **5 keywords por intención**, ideal 10–15 por intención. Si una intención tiene <5 → registrar `decision_record` explicando si es nicho real o gap de research.

| keyword | volumen mensual | intención | awareness_level | dificultad | fuente |
|---|---|---|---|---|---|
| "comprar caso detective digital" | 500 | transaccional | Most Aware | 35 | Keyword Planner |
| "X vs Y mystery box" | 200 | comparativo | Solution Aware | 28 | Keyword Planner |
| "cómo resolver acertijos" | 1200 | informacional | Problem Aware | 12 | Ahrefs |

**Mapping intención → awareness level (Schwartz)** (GAP-11):
- **Transactional** ("comprar X marca Y") = Most Aware
- **Comparative** ("X vs Y", "mejor X para Y") = Solution Aware
- **Informational** ("cómo resolver Z", "qué es Z") = Problem Aware
- **Latent** (no busca activamente; detectado vía social listening) = Unaware

Al final de la tabla, dashboard de distribución:
```
% del demand por awareness level:
- Most Aware: __%
- Solution Aware: __%
- Problem Aware: __%
- Unaware: __% (estimado, no medible directo)
```

Este dashboard es input directo a Phase 2 Content para distribuir contenido por awareness.

**B. Demanda demográfica — TAM / SAM / SOM (GAP-2)**

Trio obligatorio. Cada uno con cita de fuente + método de cálculo (top-down vs bottom-up).

| Métrica | Definición | Fuente / Método |
|---|---|---|
| **TAM** | Población total que encaja con persona en geo declarado (boundary of ambition) | Census, Statista, Eurostat |
| **SAM** | Subconjunto accesible vía canales declarados (idioma, plataforma, ticket) | Cálculo bottom-up: TAM × (% que habla idioma) × (% en plataforma activa) |
| **SOM** | Realista capturable en 12 meses con budget actual (1–5% de SAM como sanity check) | Bottom-up + benchmarks de competidores |

**C. Cruce y conclusión** — clasificación obligatoria:

- 🟢 **Validada**: SOM cuantificable + búsquedas suficientes + math gate pasa
- 🟡 **Marginal**: hay SOM pero búsquedas bajas (mercado dormido — requiere generar demanda) o viceversa
- 🔴 **No validada**: SOM < threshold o math gate falla → **STOP**, replantear `product_brief.json`

### Fuentes y método: keyword-research-tiered (4 capas)

Este sub-paso ejecuta el skill registrado `keyword-research-tiered` (domain: marketing-research, scope: project:business/marketing-os).

| Capa | Método | Costo | Automatizable |
|---|---|---|---|
| 1. Brainstorm semilla | 5–10 seeds del operador desde hipótesis + business_context | $0 | NO (requiere operador) |
| 2. Expansión gratis | Google autocomplete + PAA + Related searches + YouTube autocomplete + Amazon search bar + Reddit/Quora + TikTok/IG hashtags | $0 | Parcialmente hoy, totalmente en V2 |
| 3. Validación de volumen | Keyword Planner (gratis) → Ubersuggest ($30/mo) → Semrush/Ahrefs ($130+/mo) | $0–$130+/mo | API en V2 |
| 4. Refinamiento | Filtrar volumen 0, clasificar intención + awareness, documentar fuente | tiempo | Híbrido permanente |

**V1 stack recomendado**: Capa 1 + Capa 2 manual + Keyword Planner. Costo: $0.
**V2 spec**: Capa 2 debe extraer ≥50 keywords brutas antes de filtrar (GAP-14, anotación para V2).

### Lectura previa pretel-os
- `business_context.json`
- `lessons` tags `['demand', 'keyword-research']`
- Demanda de productos previos del mismo nicho
- `best_practice_search(domain='signal-rule', applicable_phase='phase-0.2')`

### Escrituras
- `decision_record` con la clasificación 🟢/🟡/🔴 (rojo pausa Phase 0)
- `decision_record` si alguna intención tiene <5 keywords (justificar nicho vs gap)
- `save_lesson` si hipótesis del operador se refutó

### Gate G-Phase-0.2
- ≥5 keywords por intención, ≥3 intenciones cubiertas
- Cada keyword mapeada a awareness level
- Dashboard de distribución por awareness level poblado
- TAM, SAM, SOM cuantificados con fuente
- Clasificación 🟢/🟡/🔴 registrada como `decision_record`
- Si 🔴 → STOP

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual con asistencia. Operador hace queries en Keyword Planner/Semrush, pega resultados; Claude estructura tabla, propone awareness mapping, calcula SAM/SOM. |
| V2 | Sub-workflow `keyword-research-pipeline` en n8n. Capa 2 scraped automáticamente (≥50 keywords brutas). Capa 3 vía API si hay budget. Capa 4 LLM clasifica, operador aprueba. |
| V3 | Sub-workflow corre solo, operador revisa output final + excepciones flagueadas. |

**Promoción V1→V2**: ≥3 ciclos manuales completos + ≥1 best_practice codificando el método.

---

## 5. Sub-paso 0.2.5 — ICP layer (GAP-1)

### Propósito
Capa intermedia entre demanda y persona. ICP = Ideal Customer Profile a nivel cuenta/cluster (organización en B2B, segmento de alto valor en B2C). NO es lo mismo que buyer_persona.

**Diferenciación crítica**:
- **ICP** = nivel **organizacional/cluster**. Firmographics + technographics (B2B) o cluster comportamental de alto valor (B2C). Es lo que filtras en lead forms y configuras en LinkedIn Sales Navigator/Meta audiences.
- **Buyer Persona** = nivel **individual** dentro del ICP. Psychographics + role-based pains. Es a quien le hablas en el copy.

### Output: `icp.json`

```json
{
  "icp_type": "B2B_account | B2C_cluster",
  "B2B_only": {
    "industry": ["..."],
    "company_size_employees": [10, 200],
    "annual_revenue_usd": [1000000, 50000000],
    "geography": [],
    "tech_stack_required": [],
    "tech_stack_excluded": [],
    "buying_stage": "expansion | maturity | distress",
    "must_have_filters": ["3 firmographic obligatorios"],
    "deal_breakers": ["2 disqualifiers — auto-filter"]
  },
  "B2C_only": {
    "demographic_cluster": "ej: mujeres 28-45 hispanohablantes en US",
    "psychographic_cluster": "ej: consumo activo de true crime + disposable income $200/mo+",
    "behavioral_signals": ["repeat-buying", "category-active", "newsletter-opted-in"],
    "ltv_estimated_usd": 0,
    "cluster_size_population": 0,
    "must_have_filters": ["3 señales obligatorias"],
    "deal_breakers": ["2 anti-señales"]
  },
  "evidence_basis": "CRM data | top-customer interviews | analytics | secondary research"
}
```

Solo se llena el bloque que aplica según `business_context.business_type`. Si es `hybrid`, ambos.

### Lectura previa pretel-os
- `business_context.json`
- `demand_quantification.md`
- `lessons` tags `['icp', 'firmographics', 'cluster']`

### Escrituras
- `decision_record` por elección del ICP (justificación de filtros + deal-breakers)

### Gate G-Phase-0.2.5
- Bloque correspondiente al `business_type` poblado completamente
- ≥3 must-have filters
- ≥2 deal-breakers
- `evidence_basis` declarado (no especulación libre)

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual. Operador declara filtros con justificación. |
| V2 | Handler propone filtros desde análisis de top-customers (post-PMF) o competitor benchmarks. |
| V3 | Auto + flag excepciones cuando un nuevo cluster emerge en data real. |

---

## 6. Sub-paso 0.3 — Persona + Avatar + JTBD + Forces + Negative

### Propósito
Pasar de "tengo ICP" a "este es el ser humano específico que decide y/o usa". 5 artefactos producidos en orden estricto.

### Reglas para número de personas y avatars

**Buyer personas por etapa del producto:**

| Etapa | Personas en V1 |
|---|---|
| Pre-PMF (sin ventas validadas) | 1 primario |
| Post-PMF (10+ clientes pagando) | 2–3 |
| Establecido (100+ clientes) | 3–5 |

**Avatars por persona según tipo de producto:**

| Tipo de producto | Avatars/persona |
|---|---|
| Producto con uso uniforme (vela aromática, caso detective digital) | 1–2 |
| Producto con uso situacional variable (educacional, fitness, finanzas) | 2–4 |
| Producto B2B con compra colectiva | 3–5 (= roles de DMU) |

**Sin cap duro de avatars (D-011, 2026-06-06).** La versión previa imponía un máximo de 5 avatars por producto; ese tope era un artefacto de asumir un operador humano que no puede sostener muchos avatars a mano, y **contradice la tesis de orquestación paralela** (`Overall_WF.md` §"Core Differentiator"). Cada avatar es una **unidad de orquestación independiente** con su propio loop Phase 1→5; el sistema mantiene N en paralelo. El operador puede *priorizar* cuáles activar primero (orden de ejecución), pero no hay límite estructural en cuántos existen. Las tablas de "avatars por persona según tipo de producto" arriba quedan como **guía orientativa de cuántos suelen ser cualitativamente distintos**, no como techo.

**Test operacional para crear un avatar nuevo** — sigue vigente como **criterio de calidad/distinción** (no como cap). Criterio: 2 de 3 deben ser cualitativamente distintos:
1. ¿El **trigger de compra o ongoing pain** del avatar nuevo es cualitativamente distinto?
2. ¿El **canal** donde se encuentran es distinto?
3. ¿El **lenguaje** que usan para describir el problema es distinto?

Si solo 1 de 3 → es el mismo avatar con variante menor; ajusta el existente en lugar de crear uno nuevo. Esto evita avatars redundantes, pero no limita el número de avatars *genuinamente distintos*.

### Output A: `buyer_persona.json` — analítico, universals del segmento

```json
{
  "id": "persona_primary",
  "linked_to_icp": "icp_id",
  "demographics": {
    "age_range": [28, 45],
    "gender_skew": "femenino | masculino | balanced",
    "income_range_usd_year": [40000, 80000],
    "geography": ["US-Hispanic-FL", "US-Hispanic-TX"],
    "language_primary": "es"
  },
  "psychographics": {
    "values": [],
    "fears": [],
    "aspirations": [],
    "self_image": "cómo se ven a sí mismos"
  },
  "behaviors": {
    "online_communities": ["handles concretos: r/subreddit, FB group name, IG hashtag activo"],
    "media_consumed": ["podcasts/canales/medios específicos"],
    "decision_pattern": "consulta a otros | decide solo | compra impulsiva"
  },
  "economic_capacity": {
    "discretionary_budget_usd_month": 0,
    "price_sensitivity": "alta | media | baja"
  },
  "jobs_to_be_done": [
    {
      "job_id": "JTB-1",
      "functional_job": "qué tarea/problema resuelve (literal)",
      "emotional_job": "cómo quiere SENTIRSE al hacerlo",
      "social_job": "cómo quiere SER VISTO al hacerlo",
      "situation": "circunstancia/contexto que activa el job",
      "current_solution": "qué 'contrata' ahora para hacerlo (puede ser nada)",
      "frustration_with_current": "por qué la solución actual no es suficiente"
    }
  ],
  "pain_points_universal": [
    {
      "pain": "...",
      "literal_quote": "...",
      "source_1": "Amazon review URL | Reddit thread | foro",
      "source_2": "Reddit thread URL | survey | interview",
      "frequency_observed": "12/50 reviews mencionan variante de esto"
    }
  ],
  "objections_universal": [
    "3 objeciones comunes (precio, tiempo, confianza, resultado, conveniencia)"
  ]
}
```

**Reglas**:
- Mínimo 1 functional + 1 emotional job (GAP-3)
- 5 pain_points_universal con ≥1 fuente cada uno (V1) — GAP-10 sube a ≥2 fuentes en ciclo 2 post-PMF
- Hipótesis del operador refutadas se registran como `save_lesson`

### Output B: `avatars.json` — array de avatars (humanización + contextual + Forces of Progress)

```json
[
  {
    "id": "avatar_1",
    "name": "string — nombre realista del geo/idioma",
    "age": 34,
    "occupation": "específica, no 'profesional'",
    "family_context": "casada con 2 hijos pequeños | soltero | divorciado",
    "daily_routine": "3-5 oraciones — cómo es un día típico",
    "current_goal": "qué quiere lograr esta semana/mes",
    "current_obstacle": "qué se interpone",
    "where_we_meet": "el momento específico en que el avatar encontraría tu producto",
    "pain_points_contextual": [
      "2-3 pain points específicos del contexto vital del avatar"
    ],
    "forces_of_progress": {
      "push_of_situation": {
        "ongoing_pains": [
          {
            "pain": "...",
            "frequency": "diaria | semanal | crónica",
            "channel_implication": "captura via SEO/contenido evergreen"
          }
        ],
        "triggers": [
          {
            "event": "ej: termina la temporada escolar y tiene 2 semanas libres",
            "type": "estacional | situacional | emocional | financiero",
            "urgency": "alta | media | baja",
            "channel_implication": "captura via ads en momento exacto"
          }
        ]
      },
      "pull_of_new_solution": [
        "3 atractivos de tu producto vs alternativas"
      ],
      "anxiety_about_new": [
        "3 miedos al cambio — Phase 1 offer stack debe atacarlos"
      ],
      "habit_of_present": [
        "3 razones de inercia — Phase 1 offer stack debe romperlos"
      ]
    },
    "purchase_type": "reflexiva | impulsiva | mixta",
    "customer_journey_position": "consciencia | consideración | decisión | retención | advocacy"
  }
]
```

**Diferenciación Forces of Progress**:
- **push (ongoing_pains)** → estratégico, captura vía SEO/contenido evergreen
- **push (triggers)** → táctico, captura vía ads de alta intención en momento exacto
- **pull** → posicionamiento + propuesta de valor de Phase 1
- **anxiety** → Phase 1 offer stack ataca con risk reversal + prueba social
- **habit** → Phase 1 offer stack rompe con framing displacement + urgencia genuina

**Mínimos**:
- ≥3 ongoing_pains
- ≥3 triggers
- ≥3 pull, ≥3 anxiety, ≥3 habit

**Customer Journey 5 stages** (GAP-7 parcial): consciencia → consideración → decisión → **retención** → **advocacy**. La extracción a archivo separado se difiere a Phase 2 si Phase 2 lo requiere.

### Output C: `negative_personas.json` (GAP-6) — anti-personas estructuradas

```json
[
  {
    "id": "neg_1",
    "description": "quién NO es cliente target",
    "exclusion_basis": "ético | económico | LTV-bajo | high-support-cost",
    "signals_to_detect": [
      "ej: job title 'student'",
      "ej: company size <5",
      "ej: budget declared <$Z"
    ],
    "action_when_detected": "auto-disqualify | manual review | redirect to free content"
  }
]
```

**Por qué artefacto separado**:
- Phase 2 Content handler lo lee para auto-rechazar copy que apele a esos perfiles
- Phase 3 Distribución lo usa para configurar exclusion lists en Meta/Google Ads
- Phase 4 Medir lo usa para flagear leads negativos como "low-quality" antes de calcular conversion rates

**Mínimo V1**: 1 negative persona declarada. Operador puede declarar `none` con `decision_record` justificando.

### Output D: `dmu.json` — SOLO si `business_type === "B2B"` (GAP-4)

```json
{
  "champion": {
    "title": "...",
    "pains": [],
    "wins_if_we_win": "qué gana esta persona internamente si nos contratan"
  },
  "decision_maker": {
    "title": "...",
    "criteria": ["criterios de decisión rankeados"],
    "veto_triggers": ["qué los hace decir que no automáticamente"]
  },
  "influencers": [
    {
      "title": "...",
      "concerns": []
    }
  ],
  "gatekeepers": [
    {
      "function": "legal | finance | procurement",
      "blockers": []
    }
  ],
  "end_users": [
    {
      "role": "...",
      "daily_pain": []
    }
  ]
}
```

**Mínimo B2B**: champion + decision_maker + ≥1 influencer + ≥1 end_user. Gatekeepers opcional pero recomendado.

### Diferenciación clave: ICP vs persona vs avatar

| Artefacto | Nivel | Uso downstream |
|---|---|---|
| `icp.json` | Organizacional / cluster | Targeting de audiencias en LinkedIn/Meta, lead form filters |
| `buyer_persona.json` | Individuo arquetípico | Phase 1 Oferta — value equation por persona |
| `avatars.json` | Variante contextual del individuo | Phase 2 Content — copy específico al contexto |
| `negative_personas.json` | Anti-target | Phase 3 Distribución — exclusion lists |
| `dmu.json` (B2B only) | Roles de decisión dentro del ICP | Phase 2 Content — copy específico por rol |

### Lectura previa pretel-os
- `business_context.json` + `demand_quantification.md` + `icp.json`
- `lessons` tags `['persona', 'avatar', 'jtbd', 'forces-of-progress', 'pain-points']`
- `best_practice_search(domain='signal-rule', applicable_phase='phase-0.3')`

### Escrituras
- `decision_record` por elección del persona primario
- `decision_record` por cada avatar creado (justificación con test 2-de-3)
- `decision_record` por cada negative persona declarada
- `save_lesson` por hipótesis del operador refutadas

### Gate G-Phase-0.3
- Avatar tiene nombre, no genérico ("Mujer 30-45" falla)
- Cada pain point del persona tiene cita textual con ≥1 fuente (V1)
- Cada avatar tiene Forces of Progress completo (≥3 ongoing_pains, ≥3 triggers, ≥3 pull, ≥3 anxiety, ≥3 habit)
- Cada persona tiene ≥1 functional + ≥1 emotional JTBD
- Operador puede contar el avatar en 60 segundos sin leer el JSON
- Si >1 avatar: `decision_record` con test 2-de-3 documentado
- Si `business_type === "B2B"`: `dmu.json` poblado con champion + decision_maker + ≥1 influencer + ≥1 end_user
- ≥1 negative persona declarada (o `decision_record` justificando `none`)

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + research asistido. Claude busca en redes/foros/reseñas y trae material crudo, operador interpreta y escribe los JSONs. |
| V2 | Handler drafta JSONs desde signals automatizados, operador valida. |
| V3 | Auto + flag excepciones (ej: trigger novedoso, comunidad no detectada). |

---

## 7. Sub-paso 0.4 — Competencia segmentada por canal

### Propósito
La competencia no es homogénea. Quien rankea en SEO no es quien tiene el mejor IG. Tienes 4 tipos de enemigos distintos (3 directos + substitutos).

### Output: `competitor_scan.md` — 5 secciones

1. **Competidores SEO** (3–5) — quien rankea para tus keywords transaccionales top
2. **Competidores RRSS** (3–5) — marcas/influencers/cuentas que ya tienen tu audiencia
3. **Competidores publicitarios** (3–5) — quién pauta en Meta Ad Library / Google Ads Transparency
4. **Substitutos** (3–5, GAP-9) — productos/categorías que resuelven el mismo JTBD por mecanismo distinto
5. **Síntesis cross-canal**: huecos identificados (ángulo nadie cubre, formato nadie usa, geo nadie domina)

Cada entrada de competidores directos: nombre, URL, **price_point_usd**, posicionamiento en una oración, top-3 fortalezas, top-3 debilidades, **qué se puede modelar (no copiar) y qué se debe evitar**.

Cada entrada de substituto: categoría, ejemplo, por qué los clientes los "contratan" en lugar de tu categoría, qué los hace mejores/peores que tu producto en el JTBD específico.

### Pricing tier de competencia
Cada competidor directo con `price_point_usd` poblado. Esto alimenta directo Phase 1 pricing — sabes en qué tier compites.

**Output estructurado obligatorio (GAP-AL2, audit 2026-05-10)**: además del markdown narrativo, los pricing tiers se promueven a `product_brief_v2.competitive_landscape.pricing_tiers[]` como array JSON. Cada entrada:

```json
{
  "competitor_name": "...",
  "channel": "SEO | RRSS | Ads | Substitute",
  "price_usd": 0,
  "their_stack_estimate_usd": 0,
  "tier": "low | mid | premium"
}
```

Phase 1.2 (`offer-stack-builder` algoritmo input #3) y Phase 1.4 (`competitive_position`) consumen este array directo. Parsear `competitor_scan.md` en runtime es frágil y queda prohibido.

### Lectura previa pretel-os
- `buyer_persona.json` + `avatars.json` + `icp.json` + JTBD del persona (sub-paso 0.3)
- Keywords transaccionales (sub-paso 0.2)
- `best_practice_search(domain='signal-rule', applicable_phase='phase-0.4')`

### Escrituras
- `decision_record` por elección del hueco a atacar (la diferenciación elegida)

### Gate G-Phase-0.4
- ≥3 competidores en cada uno de los 4 tipos (SEO, RRSS, Ads, Substitutos)
- Cada competidor directo con `price_point_usd` poblado
- `pricing_tiers[]` poblado en el rollup (≥1 entrada por competidor directo, con `tier` clasificado)
- Substitutos identificados con JTBD justification
- Síntesis identifica ≥2 huecos accionables
- `decision_record` del hueco a atacar registrado

### V1/V2/V3
| Versión | Cómo opera |
|---|---|
| V1 | Manual + asistencia. Claude hace scraping ligero de Meta Ad Library, operador interpreta posicionamiento. |
| V2 | Handler drafta scan, operador valida. |
| V3 | Auto + flag excepciones. |

---

## 8. Capa transversal — `signal_rules.json`

### Propósito
Reglas heurísticas que disparan automáticamente cuando los datos de cualquier sub-paso las activan. Son el output más valioso del sistema — más que cualquier oferta o campaña individual.

### Persistencia
Las reglas viven como `best_practice_record` con:
- `domain: 'signal-rule'`
- `scope: 'project:business/marketing-os'`
- Tags incluyen `applicable_phase` (ej: `phase-0.2`, `phase-1.3`)

### Lifecycle de una regla
1. Operador detecta patrón en un ciclo manual → `save_lesson`
2. Patrón se repite en ≥3 ciclos → promover a `best_practice_record` con domain `signal-rule`
3. Cada handler de sub-paso consulta `best_practice_search(domain='signal-rule', applicable_phase='phase-0.X')` antes de cerrar gate
4. Reglas obsoletas se desactivan vía `best_practice_deactivate`

### Reglas iniciales para Phase 0

```json
{
  "rules": [
    {
      "id": "DEMAND-001",
      "applicable_phase": "phase-0.2",
      "condition": "transactional_count >= 30 AND informational_count == 0",
      "severity": "info",
      "signal": "Mercado con demanda capturada — el público ya sabe qué quiere",
      "implication": "Vas a competir en precio/posicionamiento, no en educación. Phase 2 (Contenido) debe priorizar copy comparativo sobre educacional.",
      "auto_action": "tag offer_strategy: 'capture_existing_demand'"
    },
    {
      "id": "DEMAND-002",
      "applicable_phase": "phase-0.2",
      "condition": "informational_count >= 30 AND transactional_count <= 5",
      "severity": "warning",
      "signal": "Mercado curioso pero no comprador — alta investigación, baja intención",
      "implication": "Necesitas generar demanda y educar antes de vender. Ciclo de venta más largo.",
      "auto_action": "tag offer_strategy: 'create_demand'; flag pricing strategy reconsideration"
    },
    {
      "id": "DEMAND-003",
      "applicable_phase": "phase-0.2",
      "condition": "any_intent_count < 5",
      "severity": "warning",
      "signal": "Intención subrepresentada en research",
      "implication": "Posible nicho real, posible research insuficiente. Operador debe documentar cuál.",
      "auto_action": "require decision_record explicando si es nicho o gap de research"
    },
    {
      "id": "DEMAND-004",
      "applicable_phase": "phase-0.2",
      "condition": "som_population * price_point_usd * conversion_rate_optimistic < 5000",
      "severity": "alert",
      "signal": "Mercado obtenible (SOM) + ticket no soportan negocio viable",
      "implication": "Aunque convirtieras al máximo el SOM al máximo precio: ingreso máximo teórico < $5K en horizonte. Reconsiderar producto, geo, o ticket.",
      "auto_action": "block Phase 1 entry until decision_record justifying"
    },
    {
      "id": "EVIDENCE-001",
      "applicable_phase": "phase-0",
      "condition": "hypotheses_refuted_count == 0",
      "severity": "warning",
      "signal": "Todas las hipótesis del operador se confirmaron",
      "implication": "Probabilidad alta de que el research fue confirmation-biased o superficial. Research honesto casi siempre refuta algo.",
      "auto_action": "require operator_acknowledgment before signoff"
    },
    {
      "id": "EVIDENCE-002",
      "applicable_phase": "phase-0",
      "condition": "hypotheses_refuted_count >= 2 AND any_refuted_tagged_critical",
      "severity": "alert",
      "signal": "≥2 hipótesis críticas refutadas — esto es pivot, no refinamiento",
      "implication": "Si audiencia y problema se refutaron ambos, el product_brief.json v1 debe rehacerse antes de Phase 1.",
      "auto_action": "block Phase 1 entry; require product_brief.json v1.5 rewrite"
    },
    {
      "id": "ECONOMICS-001",
      "applicable_phase": "phase-0",
      "condition": "expected_ltv_usd / target_cac_usd < 3.0",
      "severity": "alert",
      "signal": "Unit economics no soportan adquisición pagada saludable",
      "implication": "El modelo solo funciona vía orgánico (SEO/contenido). SEM/Ads no será sostenible. Reconsiderar precio, retention, o canales.",
      "auto_action": "block Phase 1 entry until decision_record justifies path (organic-only OR price-up OR retention-up)"
    }
  ]
}
```

`target_cac_usd` se persiste como campo en `product.target_cac_usd` (input v1.5) y se promueve al rollup `product_brief_v2.economics.target_cac_usd`. Si el operador lo deja `null` en el input, el handler autocalcula `expected_ltv_usd / 3` (mínimo Hormozi) al cierre de Phase 0 y registra `target_cac_basis: "auto:ltv/3"`. Override manual permitido vía `decision_record` (ej: ratio 5:1 más agresivo). Phase 1 G-PRE check 5 lee este campo directo, no lo calcula en runtime.

### Cómo se ejecutan las reglas
- En V1: handler/Claude evalúa reglas manualmente y reporta al operador
- En V2: cada PhaseHandler invoca un evaluador de reglas que corre contra los outputs estructurados del sub-paso
- En V3: reglas evaluadas automáticamente, severity `alert` bloquea el gate

---

## 9. Output canónico de Phase 0: `product_brief_v2.json`

Consolidación de todo. Es el input contract de Phase 1 (Oferta).

```json
{
  "product_brief_v1": { "...inputs originales del operador..." },
  "operator_hypotheses_original": { "...preservadas para auditar contra evidencia..." },
  "marketing_objective": { "...del v1..." },
  "economics": {
    "expected_ltv_usd": 0.00,
    "expected_ltv_basis": "...heredado del v1...",
    "target_cac_usd": 0.00,
    "target_cac_basis": "auto:ltv/3 | manual:operator_override — resuelto al cierre de Phase 0"
  },
  "business_context": { "...del 0.1..." },
  "demand": {
    "validation_status": "green | yellow | red",
    "tam_population": 0,
    "sam_population": 0,
    "som_population": 0,
    "monthly_search_volume_total": 0,
    "awareness_distribution": {
      "most_aware_pct": 0,
      "solution_aware_pct": 0,
      "problem_aware_pct": 0,
      "unaware_pct": 0
    },
    "summary_path": "demand_quantification.md"
  },
  "icp": { "...del 0.2.5..." },
  "buyer_persona": { "...del 0.3 output A — incluye JTBD..." },
  "avatars": [ "...array del 0.3 output B — incluye Forces of Progress..." ],
  "negative_personas": [ "...del 0.3 output C..." ],
  "dmu": { "...del 0.3 output D — solo B2B..." },
  "competitive_landscape": {
    "differentiation_angle": "...del 0.4 — la decisión registrada del hueco a atacar...",
    "summary_path": "competitor_scan.md",
    "pricing_tiers": [
      {
        "competitor_name": "...",
        "channel": "SEO | RRSS | Ads | Substitute",
        "price_usd": 0,
        "their_stack_estimate_usd": 0,
        "tier": "low | mid | premium"
      }
    ]
  },
  "signal_rules_triggered": [
    "lista de signal rule IDs disparadas durante Phase 0 con sus implicaciones"
  ],
  "evidence_findings": {
    "hypotheses_confirmed": [],
    "hypotheses_refuted": [],
    "hypotheses_refuted_critical_count": 0
  },
  "research_metadata": {
    "hours_invested": 0,
    "usd_invested": 0,
    "completed_at": "ISO date",
    "operator_signoff": true
  }
}
```

---

## 10. Gate global G-Phase-0

Phase 0 se cierra cuando:
- Sub-gates 0.1, 0.2, 0.2.5, 0.3, 0.4 cerrados
- `product_brief_v2.json` consolidado, paths apuntando a archivos reales
- `evidence_findings.hypotheses_refuted` tiene ≥1 entrada (si todas las hipótesis se confirmaron, flag de revisión)
- `evidence_findings.hypotheses_refuted_critical_count < 2` (si ≥2 críticas refutadas, EVIDENCE-002 bloquea)
- ECONOMICS-001 verificado: `expected_ltv_usd / target_cac_usd >= 3.0` (o `decision_record` justificando organic-only)
- `research_metadata.hours_invested` y `usd_invested` cuantificados
- Todas las reglas con severity `alert` resueltas (no pueden quedar bloqueando)
- Operador firma `operator_signoff: true`

---

## 11. Re-trigger de Phase 0

Phase 0 se ejecuta:
- **Una vez** al inicio de cada producto nuevo
- **Re-trigger** cuando se cumpla cualquiera de:
  - CTR cae ≥30% sostenido por 14 días en campañas que antes funcionaban
  - CPL/CPA sube ≥40% sostenido
  - Conversiones bajan con mismo tráfico
  - Operador detecta cambio cualitativo en feedback (señales de que el avatar cambió)
  - Pasaron 12 meses desde el último Phase 0 (forced refresh)
  - **GAP-16 (diferido a Cat C)**: competitive shift — competidor tier-1 entra/sale del mercado o pivota material

Cada re-trigger queda como `decision_record` con motivo + evidencia.

---

## 12. Decisiones cerradas en Phase 0

| # | Decisión | Resolución |
|---|---|---|
| D1 | ¿Un solo persona o permitir 2 (primario + secundario)? | **1 primario en V1**. Reglas detalladas en sección 6. |
| D2 | ¿Phase 0 contiene budget de horas/costo de research? | **Sí, campo obligatorio**. |
| D3 | ¿Phase 0 corre una vez por producto, o se re-corre periódicamente? | **Una vez al inicio + re-trigger según condiciones de sección 11.** |
| D4 | ¿Forces of Progress reemplaza purchase_triggers? | **Opción C**: `forces_of_progress` con `push_of_situation` separando `ongoing_pains` (estratégicos) de `triggers` (tácticos). Preserva vocabulario Big School + agrega rigor Christensen. |
| D5 | ¿ICP separado de buyer_persona? | **Sí**, sub-paso 0.2.5 nuevo. ICP = nivel organizacional/cluster. Persona = nivel individuo. |
| D6 | ¿LTV:CAC gate en Phase 0 o solo en Phase 4? | **En Phase 0** vía signal rule ECONOMICS-001 con valores estimados. Phase 4 valida con datos reales. |
| D7 | ¿Negative persona como prosa o como artefacto estructurado? | **Artefacto estructurado** `negative_personas.json`. Phase 2/3/4 lo leen programáticamente. |
| D8 | ¿Customer Journey artefacto separado o embebido en avatar? | **Embebido en avatar (sub-paso 0.3) con 5 stages** (consciencia → consideración → decisión → retención → advocacy). Extracción a archivo separado se difiere si Phase 2 lo requiere. |
| D9 | ¿Hard cap de 5 avatars? | **Eliminado (D-011, 2026-06-06).** Contradecía la orquestación paralela. Sin límite estructural; el test 2-de-3 se mantiene como criterio de distinción, no como techo. |
| D10 | ¿La capa Foundation (0.1–0.2.5) es agnóstica del avatar? | **Sí.** Business Context, Demand e ICP se calculan una vez por proyecto y se comparten entre todos los avatars (`avatar_id` null). La bifurcación por-avatar empieza en 0.3. |

---

## 13. Lecciones registradas en Phase 0 spec design

| ID conceptual | Lección |
|---|---|
| L1 | Las hipótesis del operador SE PRESERVAN; no se sobrescriben con evidencia |
| L2 | Pain points deben venir DESPUÉS de persona/avatar, no antes (dependen de 4 pilares previos) |
| L3 | ICP, Persona y Avatar son tres artefactos distintos con tres lectores downstream distintos |
| L4 | Forces of Progress > purchase_triggers — captura push + pull + anxiety + habit, no solo activadores |
| L5 | Triggers (eventos) ≠ ongoing_pains (crónicos) — distinción informa cómo se gasta el budget |
| L6 | Competencia es heterogénea: SEO ≠ RRSS ≠ Ads ≠ Substitutos — 4 secciones obligatorias |
| L7 | Business Context es declaración del operador, nunca se automatiza |
| L8 | Confirmation bias: si todas las hipótesis se confirman, el research fue superficial |
| L9 | Math gate: SOM × precio_max × conversion_rate_optimista < $5K → STOP |
| L10 | Unit economics gate: LTV/CAC < 3.0 → STOP o revisar canal-mix |
| L11 | Negative persona es artefacto, no prosa — Phase 2/3/4 lo leen programáticamente |
| L12 | JTBD captura "qué contratan" mejor que pain points — Phase 1 Hormozi lo necesita para "Dream Outcome" |
| L13 | Awareness levels (Schwartz) ya están en intenciones de búsqueda — mapping trivial, output a Phase 2 |

---

## 14. Pendientes y diferidos

### Pendientes globales
- DDL de ChatGPT (Entity, Offer, Audience, Campaign, ContentAsset, MetricSnapshot, Learning, Decision, AgentRun) para integrar con schema actual de pretel-os
- Skill `keyword-research-tiered` registrado en pretel-os
- Signal rules iniciales sembradas como best_practices con `domain: signal-rule`
- Specs Phases 1–5

### Diferidos de auditoría (Categoría B/C/D)

| Gap | Categoría | Cuándo activar |
|---|---|---|
| GAP-4 DMU | B | Cuando inicie producto B2B (Alfredo-as-freelance) |
| GAP-12 Interviews obligatorias | B | Post-PMF (≥10 ventas validadas) de cualquier producto |
| GAP-9 Substitutos refinamiento | C (parcialmente integrado en sección 7) | Después del primer ciclo manual |
| GAP-10 VoC ≥2 fuentes | C | Promover a obligatorio en ciclo 2 |
| GAP-13 Segmentation variables | C | Cuando aparezcan avatars secundarios |
| GAP-14 V2 keyword expansion ≥50 brutas | C | Spec de V2 sub-workflow |
| GAP-15 Más signal rules (PERSONA-001, JTBD-001, etc.) | C | Backlog continuo |
| GAP-16 Competitive shift re-trigger | C | Cuando exista mecanismo de detección |

### Tareas a registrar en pretel-os tasks table
- 1 task por cada gap diferido con tag `marketing-os-audit-202605` y `priority: medium`
- 1 task `marketing-os-audit-202605-decision` con resumen de qué se aceptó

---

## 15. Apéndice — checklist operacional V1

Para el primer ciclo manual con un producto real:

```
[ ] product_brief.json v1.5 escrito (incluye expected_ltv_usd + marketing_objective + critical flags)
[ ] 0.1 — business_context.json declarado
[ ] 0.2 — keywords brainstorm (Capa 1)
[ ] 0.2 — keywords expansión gratis (Capa 2)
[ ] 0.2 — keywords validación volumen (Capa 3)
[ ] 0.2 — keywords clasificadas + filtradas + awareness mapping (Capa 4)
[ ] 0.2 — TAM / SAM / SOM cuantificados con fuente
[ ] 0.2 — dashboard awareness distribution poblado
[ ] 0.2 — clasificación 🟢/🟡/🔴 registrada
[ ] 0.2.5 — icp.json (B2B o B2C según business_context)
[ ] 0.3 — buyer_persona.json escrito (incluye JTBD ≥1 functional + ≥1 emotional)
[ ] 0.3 — avatars.json escrito (1-4 según tipo de producto, con Forces of Progress completo)
[ ] 0.3 — pain points (universales con ≥1 fuente cada uno)
[ ] 0.3 — negative_personas.json (≥1 o decision_record justificando none)
[ ] 0.3 — dmu.json (solo si B2B)
[ ] 0.4 — 3 competidores por canal (SEO, RRSS, Ads) + 3 substitutos
[ ] 0.4 — pricing tier de competidores poblado
[ ] 0.4 — síntesis cross-canal con hueco a atacar
[ ] signal rules evaluadas — DEMAND-004, EVIDENCE-002, ECONOMICS-001 verificadas
[ ] evidence_findings poblado (hipótesis confirmadas + refutadas + critical count)
[ ] product_brief_v2.json consolidado
[ ] hours/usd invertidos cuantificados
[ ] operator_signoff: true
```
