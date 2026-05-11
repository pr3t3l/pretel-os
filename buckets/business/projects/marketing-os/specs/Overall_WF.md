# Marketing OS — Overall Workflow

**Project**: business/marketing-os
**Document type**: lifecycle overview
**Status**: living document — evoluciona conforme se cierran specs por fase
**Last updated**: 2026-05-10
**Audit history**:
- 2026-05-10 R1 — `audit_marketing_os_phase_0.md` — Categoría A integrada al spec Phase 0 v1.5. Persistida como `decision_record` `7f87df56` (D-002).
- 2026-05-10 R2 — Auditoría externa Phase 1 + mejoras operador → spec Phase 1 v1.5. Persistida como `decision_record` `9215573a` (D-003).
- 2026-05-10 R3 — Auditoría alineación Phase 0 ↔ Phase 1: GAP-AL1, GAP-AL2, ISSUE-A1–A4 integrados a specs + DOC-1/DOC-2/DOC-3 corregidos en este documento. Persistida como `decision_record` `ef0b2c75` (D-004).
- 2026-05-10 R4 — Auditoría Phase 2 (dos auditores): A1-ISSUE-1/2/3/4 bloqueantes (force_coverage, JTBD anchor, Vaynerchuk ratio, displacement_inheritance) + A1-ISSUE-7/8 doc (L11, Pinterest) + A2-ISSUE-1/2/3/4 clarity (V1/V2 disambiguación, evaluador, persistencia, lookup IDs). Spec Phase 2 bumped a v1.1. Persistida como `decision_record` `fe833af2` (D-005). Diferidos a captura como lessons del primer ciclo: A1-ISSUE-9 (voice versioning), A1-ISSUE-10 (ICP en copy B2B). Diferidos a V2: A1-ISSUE-5 (email sequences), A1-ISSUE-6 (pre-PMF rule combinada).

---

## 0. Propósito de este documento

Mapa de alto nivel del Marketing Lifecycle completo. Para cada fase, este documento describe:
- Qué problema resuelve
- Qué consume y qué produce (input/output contracts a alto nivel)
- Por qué viene en ese orden y no en otro
- Cuál es el principio teórico que la respalda
- Cuál es la decisión humana inevitable que esa fase contiene

**Lo que este documento NO es**: el spec detallado por fase. Cada fase tiene su propio `spec_Phase_N_*.md` con gates, schemas, signal rules y planes V1/V2/V3. Esos specs son la fuente de verdad ejecutable; este documento es el contexto narrativo.

**Cuándo leer este documento**:
- Al iniciar una nueva sesión sobre Marketing OS para recordar el todo
- Antes de cambiar de chat (este es el contexto mínimo de transferencia)
- Antes de empezar el spec de la siguiente fase
- Cuando un colaborador (humano o IA) necesita entender el sistema

---

## 1. Filosofía operacional

### Híbrido determinístico/agéntico

El orquestador NO improvisa qué fase ejecutar siguiente. El orden de fases es código. Cada PhaseHandler sabe qué leer de pretel-os antes de actuar y qué escribir después. La creatividad LLM ocurre **dentro** de cada handler, nunca en la elección de qué fase viene.

Modo de fallo evitado: OpenClaw fallaba porque el LLM decidía qué hacer siguiente. Marketing OS no permite eso.

### KPI primario: dinero

Todas las métricas instrumentales (engagement, alcance, CTR, vistas) son medios. La fase 4 (Medir) consolida todo a un único `revenue_attributed` por campaña. Sin revenue atribuible, una campaña no se considera exitosa por más que tenga métricas suaves bonitas.

### Aprendizaje compuesto cross-producto

Las lessons, decisions y best_practices producidas por un producto (ej: Declassified) se vuelven contexto de entrada para el siguiente producto (ej: velas, freelance). Un producto nunca empieza desde cero.

### Manual antes que automático

**Regla dura**: ningún PhaseHandler automatizado se construye sin que el operador haya ejecutado esa fase manualmente al menos 3 veces para productos reales, con cada decisión registrada y al menos una best_practice destilada del manual.

### Reglas heurísticas como sistema nervioso

Cada fase tiene un `signal_rules.json` que se ejecuta contra los outputs estructurados del sub-paso. Las reglas viven como `best_practice_record` con `domain: signal-rule`. Son el output más valioso del sistema — más que cualquier oferta o campaña individual.

### Honestidad arquitectural

- Urgencia/escasez fabricada PROHIBIDA por el sistema (Phase 1.3)
- Risk reversal sólo si se honraría realmente
- Claims en copy con evidencia o se tachan
- Esto es compromiso del sistema, no opción del operador

### Capas conceptuales: ICP, Persona, Avatar

| Capa | Nivel | Para qué sirve | Quién la lee downstream |
|---|---|---|---|
| **ICP** | Organizacional (B2B) / cluster de alto valor (B2C) | Filtrar audiencias publicitarias y leads | Targeting (Phase 3), Lead form filters |
| **Buyer Persona** | Individuo arquetípico dentro del ICP | Value equation, oferta core | Phase 1 (Oferta) |
| **Avatar** | Variante contextual del individuo | Copy específico al contexto vital | Phase 2 (Content) |

Mezclarlas en una sola entidad rompe B2B y pierde precisión en B2C.

---

## 2. Mapa del lifecycle

```
                  ┌────────────────────────────────┐
                  │ product_brief.json v1.5 (input) │
                  └───────────────┬────────────────┘
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │  Phase 0 — Research + ICP                       │
        │  → product_brief_v2.json                        │
        │  (business_ctx + demand + icp + persona +       │
        │   avatars + JTBD + Forces of Progress +         │
        │   negative_personas + dmu[B2B] + competitors)   │
        └─────────────────────────────┬───────────────────┘
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  Phase 1 — Oferta                               │
        │  → offer_spec.json + offer_statement.md         │
        └─────────────────────────────┬───────────────────┘
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  Phase 2 — Contenido                            │
        │  → content_plan.json + content_assets/          │
        └─────────────────────────────┬───────────────────┘
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  Phase 3 — Publicar / Distribuir                │
        │  → distribution_plan.json + posts published     │
        └─────────────────────────────┬───────────────────┘
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  Phase 4 — Medir                                │
        │  → metrics_snapshot.json + revenue attribution  │
        └─────────────────────────────┬───────────────────┘
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  Phase 5 — Ajustar / Optimizar                  │
        │  → optimization_plan.json + lessons + rules     │
        └───────┬─────────────────────────────────┬───────┘
                │                                 │
                ▼                                 ▼
         (re-trigger Phase X)              (next cycle)
```

Phases 0–2 son **planeación**. Phases 3–5 son **ejecución y aprendizaje**.

Los re-triggers fluyen de Phase 5 hacia atrás: si Phase 5 detecta que el avatar cambió (CTR/CPA degradados), dispara re-trigger de Phase 0. Si detecta que la oferta perdió fuerza, dispara re-trigger de Phase 1.

---

## 3. Phase 0 — Research + ICP

### Problema que resuelve
Casi todo el marketing fallido es marketing dirigido al avatar equivocado con suposiciones no verificadas sobre el mercado. Phase 0 obliga a tener evidencia antes de actuar.

### Input
`product_brief.json` v1.5 — declaración del operador con producto, hipótesis sobre audiencia/problema, LTV esperado, objetivo de marketing, constraints de geo/idioma/budget.

### Output canónico
`product_brief_v2.json` — incluye business_context, demand quantification con TAM/SAM/SOM y awareness mapping, ICP layer, buyer_persona con JTBD, avatars (1–4) con Forces of Progress, negative_personas, DMU (solo B2B), competitive landscape con substitutos, evidence findings (hipótesis confirmadas vs refutadas).

### Sub-pasos
1. **0.1 Business Context Gate** — declaración B2B/B2C, ciclo, canal, monetización, scope. Nunca se automatiza.
2. **0.2 Cuantificación de demanda** — keywords con volumen real + awareness mapping + TAM/SAM/SOM. Clasificación 🟢/🟡/🔴.
3. **0.2.5 ICP layer** — firmographics (B2B) o cluster comportamental (B2C). Filtros + deal-breakers.
4. **0.3 Persona + Avatar + JTBD + Forces + Negative** — 1 persona primario (en pre-PMF) + 1–4 avatars + Forces of Progress (push/pull/anxiety/habit) + negative_personas + DMU si B2B.
5. **0.4 Competencia segmentada por canal** — SEO, RRSS, Ads + substitutos (Porter Force #4) + pricing tier por competidor.

### Decisión humana inevitable: dos distintas

Phase 0 contiene **dos** decisiones humanas que el operador debe hacer explícitas:

1. **EXCLUSIONES PERMANENTES** — "¿A quién decido NO venderle nunca?"
   Decisión ética/estratégica. Se materializa en `negative_personas.json` y se hereda a todos los ciclos futuros del producto. Ejemplos: minorías protegidas, nichos que requieren claims no respaldables, segmentos contrarios a los valores del operador, perfiles con LTV negativo / alto costo de soporte.

2. **PRIORIZACIÓN DEL PRIMER CICLO** — "¿A cuál de mis 1–4 avatars le hablo primero/más fuerte?"
   Decisión táctica de foco para concentrar recursos. **NO elimina los otros avatars** del `product_brief_v2` — solo declara cuál es el avatar primario del primer ciclo. Los otros entran en ciclos posteriores cuando el primario esté validado o cuando exista evidencia de que pelean por recursos sin canibalizarse.

Ningún algoritmo decide ninguna de las dos por el operador.

### Spec detallado
`specs/marketing-os/spec_Phase_0_Research_ICP.md`

---

## 4. Phase 1 — Oferta

### Problema que resuelve
Sin una oferta estructurada, el copy de Phase 2 vende características; con oferta estructurada vende transformación. Phase 1 convierte conocimiento del avatar (incluyendo JTBD y las 4 fuerzas) en una propuesta cuyo valor percibido es 3–10× el precio.

### Input
`product_brief_v2.json` — necesita avatar específico con Forces of Progress completo, JTBD del persona, pain/objections universales, negative_personas (para no inventar bonuses que apelen a anti-target).

### Output canónico
`offer_spec.json` (value equation + stack + risk reversal + urgency + pricing + naming) + `offer_statement.md` (la página única que alimenta TODO copy de Phase 2).

### Sub-pasos
1. **1.1 Dream Outcome + Value Equation** — fórmula Hormozi: Valor = (Dream × Likelihood) / (Time × Effort). Dream Outcome sale del JTBD `emotional_job` + `functional_job`, no de features del producto. Score 1–10 por eje, identifica weakest_axis.
2. **1.2 Offer Stack** — core + 3–7 bonuses. Cada bonus mapeado explícitamente a una fuerza: bonus_atacar_anxiety, bonus_romper_habit, bonus_amplificar_pull. Stack-to-price ratio target 3–10×.
3. **1.3 Risk Reversal + Urgency** — garantía honesta + urgency/scarcity solo si genuine_reason existe. **Nunca se automatiza** (decisión ética).
4. **1.4 Pricing + Naming + Statement** — precio justificado contra value equation y pricing tier de competidores (Phase 0.4), nombre testeable, página única ≤350 palabras.

### Spine teórico
- Hormozi $100M Offers (value equation + stack)
- Christensen JTBD (Dream Outcome viene del job, no del producto)
- Christensen Forces of Progress (Phase 1 ataca anxiety + habit, no solo amplifica push + pull — clave que la mayoría de ofertas miss)

### Decisión humana inevitable
"¿Cuánto vale esto realmente?" El precio es un acto de definición del valor que el operador entrega. Ningún algoritmo decide por él.

### Pre-condiciones
- Phase 0 cerrada con `operator_signoff: true`
- `demand.validation_status` ∈ {green, yellow}
- `evidence_findings.hypotheses_refuted` ≥1 entrada
- `evidence_findings.hypotheses_refuted_critical_count` < 2 (si ≥2 críticas refutadas → pivot, no refinamiento)
- ECONOMICS-001 pasa (LTV/CAC ≥ 3.0) o `decision_record` justifica organic-only

### Spec detallado
`specs/marketing-os/spec_Phase_1_Oferta.md` (v1.5 — post-audit)

---

## 5. Phase 2 — Contenido

### Problema que resuelve
Una oferta sin distribución es invisible. Phase 2 convierte la oferta en piezas de contenido que respetan: (a) la fase del Customer Journey del avatar (5 stages: consciencia → consideración → decisión → retención → advocacy), (b) el awareness level del prospecto (Schwartz, ya mapeado en Phase 0.2), (c) la lógica de cada canal, (d) las 4 fuerzas (cada fuerza requiere formato distinto), (e) las negative_personas (para auto-rechazar copy que apele a anti-target).

### Input
`offer_spec.json` + `offer_statement.md` + avatars con Forces of Progress (de Phase 0) + business_context + awareness_distribution dashboard (de Phase 0.2) + negative_personas + dmu (si B2B) + `multi_avatar_strategy` (de Phase 1) + `positioning_variants[]` con `language_packs` (de Phase 1, si aplica) + `offer_statements[]` (N si `separate_offers`, 1 si `unified_C_*`, según strategy). Sin estos campos el handler de Phase 2 no sabe si escribir 1 copy o N copies, ni en qué registro lingüístico.

### Output canónico
`content_plan.json` (matriz Customer Journey × awareness level × canal × formato × fuerza_atacada) + `content_assets/` (los assets reales: copy, scripts, hooks, headlines, body text, CTAs).

### Sub-pasos previstos
1. **2.1 Awareness Mapping** — usa el `awareness_distribution` ya calculado en Phase 0.2. Define qué proporción de contenido va a cada nivel de Schwartz.
2. **2.2 Customer Journey × Canal Matrix** — 5 stages × canales: SEO/email para conversión+retención, RRSS para conciencia+advocacy, ads para amplificación.
3. **2.3 Forces-aware Content Pillars**:
   - Contenido para `ongoing_pains` → SEO + evergreen (estratégico, captura crónica)
   - Contenido para `triggers` → ads con timing + landing pages (táctico, captura momento)
   - Contenido para `anxiety` → testimonios, casos de éxito, demos, garantías
   - Contenido para `habit` → comparativos vs status quo, framing de displacement
4. **2.4 Atomization** — pillar → derivados (un long-form se convierte en N short-forms, threads, carousels, emails).
5. **2.5 Hook Library** — banco de hooks testeables, ranqueables, reusables. Hooks etiquetados por fuerza que atacan.

### Spine teórico
- Schwartz "Breakthrough Advertising" (5 awareness levels — ya mapeados en Phase 0.2)
- Drive currículum (filosofía de atracción vs interrupción)
- Vaynerchuk "Jab Jab Jab Right Hook" (proporción contenido valor vs venta)
- Christensen Forces of Progress (contenido por fuerza, no por intuición)

### Decisión humana inevitable
"¿Qué tono uso?" El tono de marca es identidad, no decoración. El operador lo declara antes de delegar generación al LLM.

### Pre-condiciones
- Phase 1 cerrada con `operator_signoff: true`
- `expected_uncovered_objections` de Phase 1 documentadas (Phase 2 las resuelve con copy)

### Spec detallado
`specs/marketing-os/spec_Phase_2_Contenido.md` (v1.0 drafted 2026-05-10)

---

## 6. Phase 3 — Publicar / Distribuir

### Problema que resuelve
Producir contenido sin sistema de publicación es producir desperdicio. Phase 3 ejecuta la distribución programada, multi-canal, con tracking que cierra el loop con Phase 4 y con exclusion lists configuradas desde negative_personas.

### Input
`content_plan.json` + `content_assets/` + `business_context.channel` + `negative_personas` (para exclusion lists en Meta/Google Ads) + `icp` (para targeting en LinkedIn Sales Navigator / Meta).

### Output canónico
`distribution_plan.json` (calendario, canales, pixel/UTM strategy, exclusion lists, targeting per ICP) + posts publicados con IDs trackeables (post_id, campaign_id, utm parameters).

### Sub-pasos previstos
1. **3.1 Tracking infrastructure** — pixel + UTMs + conversion events configurados ANTES de publicar primer post.
2. **3.2 Audience configuration** — ICP filters en plataformas + exclusion lists desde negative_personas.
3. **3.3 Calendar planning** — qué se publica cuándo, frecuencia por canal (sale del Drive: cada canal tiene función distinta).
4. **3.4 Distribution execution** — vía n8n hacia FB/IG/Pinterest/TikTok/email/etc.
5. **3.5 Cross-promotion mapping** — qué post en canal X dirige a qué activo en canal Y.

### Spine teórico
- Cada canal con función específica (Drive: SEO captura, redes amplifican, email convierte)
- Permission marketing (Godin) para email
- Native content per platform (Vaynerchuk)

### Decisión humana inevitable
"¿Qué canal abandono?" Foco requiere matar canales que parecen prometedores pero diluyen. Phase 3 obliga al operador a comprometerse.

### Pre-condiciones
- Phase 2 cerrada
- Tracking infrastructure verificada funcionando (pixel fire test, UTM resolución, conversion event registro)
- Cuentas/conexiones n8n activas para los canales declarados

### Spec detallado
`specs/marketing-os/spec_Phase_3_Distribucion.md` (pendiente)

---

## 7. Phase 4 — Medir

### Problema que resuelve
Lo que no se mide no se optimiza. Lo que se mide mal optimiza la cosa equivocada. Phase 4 conecta cada acción de Phase 3 con su impacto real en revenue y valida los estimados de LTV/CAC declarados en Phase 0.

### Input
Posts publicados (Phase 3) + tracking infrastructure + ventas/conversiones reales + LTV/CAC estimados de Phase 0.

### Output canónico
`metrics_snapshot.json` por ventana temporal (diaria, semanal, mensual) con atribución revenue por campaign_id + comparación contra LTV/CAC estimado en Phase 0.

### Sub-pasos previstos
1. **4.1 Data ingestion** — APIs de FB Insights, IG Insights, GA4, Pinterest, TikTok, Stripe/Shopify para revenue.
2. **4.2 Attribution modeling** — last-click default V1; multi-touch en V2 cuando haya volumen.
3. **4.3 Funnel decomposition** — para cada campaign_id: impresiones → clicks → leads → conversiones → revenue. Leads que matchean negative_personas se flaguean como "low-quality" antes de calcular conversion rates.
4. **4.4 Cohort tracking** — comportamiento de leads agrupados por trigger/canal/avatar (LTV downstream).
5. **4.5 Phase 0 reality check** — comparar LTV/CAC real vs estimado en Phase 0. Disparar re-trigger Phase 0 si delta >50%.

### Spine teórico
- Lean Analytics (Croll & Yoskovitz) — métricas por etapa
- Hormozi LTV:CAC > 3:1 como salud financiera mínima

### Decisión humana inevitable
"¿Esta métrica es señal o ruido?" Variancia natural en métricas pequeñas puede confundirse con tendencia. Phase 4 incluye thresholds estadísticos pero la decisión de actuar la toma el operador.

### Pre-condiciones
- Phase 3 ejecutándose con tracking activo ≥7 días
- Revenue source conectado (Stripe, Shopify, manual log mínimo)

### Spec detallado
`specs/marketing-os/spec_Phase_4_Medir.md` (pendiente)

---

## 8. Phase 5 — Ajustar / Optimizar

### Problema que resuelve
Las métricas sin acción son trivia. Phase 5 convierte datos en cambios concretos: qué se mantiene, qué se mata, qué se itera, qué se escala — y qué se aprende para futuros ciclos cross-producto.

### Input
`metrics_snapshot.json` (Phase 4) + signal rules acumuladas + lessons abiertas.

### Output canónico
`optimization_plan.json` con acciones por categoría (kill/iterate/scale/hold) + lessons promocionadas a best_practices + re-triggers a fases anteriores cuando aplique.

### Sub-pasos previstos
1. **5.1 Performance review** — clasificación 4-cuadrantes: high traffic + high conversion / high traffic + low conversion / low traffic + high conversion / low both.
2. **5.2 Hypothesis generation** — para cada cuadrante problemático, hipótesis testeable (no "el copy podría ser mejor" — "cambiar hook de X a Y debería subir CTR de N% a N+M%").
3. **5.3 Action plan** — A/B tests, kills, scales, escalations.
4. **5.4 Re-trigger detection** — si hay degradación severa, dispara re-trigger de Phase 0/1/2 según señal. Re-trigger Phase 1 cuando: conversion rate cae ≥30% sostenido con mismo tráfico, LTV/CAC real (Phase 4) diverge ≥50% del estimado en Phase 0 ECONOMICS-001, o avatar secundario no cubierto por la estrategia actual requiere oferta. Ver `spec_Phase_1_Oferta.md` sec 11.
5. **5.5 Knowledge consolidation** — lessons recurrentes (≥3 ciclos) se promueven a best_practices con domain `signal-rule` o domain del producto.

### Spine teórico
- Lean Startup (Ries) — build-measure-learn
- Hacking Growth (Ellis) — growth loops + prioritized experimentation (ICE/PIE scoring)

### Decisión humana inevitable
"¿Cuándo aceptar que algo no funciona?" Sesgo de confirmación + sunk cost hacen que operadores persistan con campañas muertas. Phase 5 incluye criterios duros de kill pero la ejecución requiere disciplina humana.

### Pre-condiciones
- Phase 4 con ≥1 ventana de medición cerrada
- Volumen mínimo de datos para significancia (definido en spec por sub-paso)

### Spec detallado
`specs/marketing-os/spec_Phase_5_Ajustar.md` (pendiente)

---

## 9. Cross-cutting concerns

### Productos a servir (orden de prioridad)
1. **Declassified Cases** — banco de pruebas, validación end-to-end del lifecycle (B2C)
2. **Alfredo-as-freelance** — segundo cliente, B2B, valida lifecycle en contexto de servicio (activa GAP-4 DMU)
3. **Velas de hija** — tercer cliente, producto físico local, valida adaptabilidad del lifecycle (B2C)
4. **Futuros clientes** — el meta-producto: el sistema de marketing en sí

### Generalización vía product_brief
El sistema NO se hardcodea a Declassified. El `product_brief.json` es input estandarizado. Cualquier producto futuro entra por la misma puerta.

### Stack tecnológico
- **pretel-os core** — PostgreSQL + pgvector + FastMCP server
- **Marketing OS module** — Python PhaseHandlers tipo SDD Planner
- **LiteLLM gateway** — todos los LLM calls pasan por aquí (cascade Sonnet 4.6 → Haiku 4.5 → gpt-4o-mini)
- **n8n** — ejecución externa (publicación, scraping, webhooks). NO orquesta lifecycle.
- **Storage** — `marketing_os/runs/{run_id}/` para artefactos transient + pretel-os DB para state durable

---

## 10. Estado actual del proyecto

| Fase | Spec | Skill registrado | Ciclo manual | V2 |
|---|---|---|---|---|
| 0 | ✅ drafted v1.5 (post-audit) | pendiente | 0 | — |
| 1 | ✅ drafted v1.5 (post-audit) | pendiente | 0 | — |
| 2 | ✅ drafted v1.1 (post-audit R4, 2026-05-10) | pendiente | 0 | — |
| 3 | pendiente | — | 0 | — |
| 4 | pendiente | — | 0 | — |
| 5 | pendiente | — | 0 | — |

### Decisiones arquitecturales registradas en pretel-os
- D-001 (id `e258360a`): Marketing OS vive como módulo dentro de pretel-os, no como cliente externo
- D-002 (id `7f87df56`): Auditoría 2026-05-10 R1 — Categoría A aceptada e integrada al spec Phase 0 v1.5 (ICP layer, TAM/SAM/SOM, JTBD, LTV/CAC gate, negative_personas, Forces of Progress opción C, awareness mapping, hipótesis críticas refutadas)
- D-003 (id `9215573a`): Auditoría 2026-05-10 R2 — Phase 1 spec v1.5 (integración outputs Phase 0 v1.5 + auditoría externa + mejoras operador: tabla ratio derivada, margin gate, sub-workflows, condición 5 multi-avatar, escala 1–10000)
- D-004 (id `ef0b2c75`): Auditoría 2026-05-10 R3 — Alineación Phase 0 ↔ Phase 1 (GAP-AL1 `target_cac_usd` persistido, GAP-AL2 `pricing_tiers[]` estructurado, ISSUE-A1 forces en TODOS los avatars, ISSUE-A2 sub-paso 1.4.0 language_packs, ISSUE-A3 comparable en core_deliverable, ISSUE-A4 urgency.aligned_with_trigger, DOC-1/2/3 Overall_WF)
- D-005 (id `fe833af2`): Phase 2 spec drafted v1.0 + auditoría R4 integrada v1.1 (force_coverage por pilar + REINFORCE-001, JTBD anchor en brand voice + PILLAR_A + identity hooks, Vaynerchuk ratio 3:1 + content_type por derivative + VAYNER-001, displacement_inheritance literal en PILLAR_D, V1/V2 disambiguación tabla sub-pasos, brand_voice doble persistencia filesystem + decision_record, Pinterest + YouTube paid + Influencer + Affiliates en channel_function lookup, L11 collapse Schwartz 5→4)

### Best practices registradas
- BP-001 (id `fea3dbd8`): No construir agente de marketing sin ciclo manual documentado de su fase

### Pendientes globales
- DDL de ChatGPT (Entity, Offer, Audience, Campaign, ContentAsset, MetricSnapshot, Learning, Decision, AgentRun) para integrar con schema actual de pretel-os
- Skill `keyword-research-tiered` registrado en pretel-os
- 7 signal rules iniciales sembradas como best_practices con `domain: signal-rule` (DEMAND-001 a 004, EVIDENCE-001 y 002, ECONOMICS-001)
- 8 tasks abiertas con tag `marketing-os-audit-202605` por gaps diferidos (Categorías B y C)
- Specs Phases 1–5

---

## 11. Cómo usar este documento al empezar un chat nuevo

1. Leer este `Overall_WF.md` completo (5 min)
2. Leer el spec de la fase en la que estás trabajando (`spec_Phase_N_*.md`)
3. Consultar pretel-os: `decision_search` por `project=marketing-os`, `lessons` con tag `marketing-os`, `best_practice_search` con scope del proyecto
4. Verificar tasks abiertas: `task_list(project='business/marketing-os', status='open')`
5. Continuar desde donde quedó la fase

Esa secuencia reemplaza "déjame contarte el contexto del proyecto". El contexto vive en archivos, no en chats.
