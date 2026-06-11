# Run: Sandi — log

**Qué es:** el primer run de la metodología marketing-os. Sandi (el sistema de marketing AI-first) usándose a sí mismo como caso de prueba. Sirve de ejemplo trabajado (CAG) + fixture de eval.

## Estado

| Fase | Sub-paso | Estado | Artefacto |
|---|---|---|---|
| Phase 0 | 0.1 Business Context | ✅ cerrado | `business_context.json` |
| Phase 0 | 0.2 Mercado | ✅ cerrado | `demand_quantification.md` |
| Phase 0 | 0.2.5 ICP | ✅ cerrado (v2) | `icp.json` (D-023, supersede D-022) |
| Phase 0 | 0.3 Persona + Avatares | ✅ cerrado (D-027) | `buyer_persona.json` (D-025) · `avatars.json` signed_v2 (4 avatares) · `negative_personas.json` (2) · `evidence_firsthand.md` · Priya 1er ciclo (D-026) |
| Phase 0 | 0.4 Competencia | ✅ cerrado (D-028) | `competitor_scan.md` · `pricing_tiers.json` · hueco = intersección completa (categoría propia) |
| Phase 0 | **Rollup global** | ✅ **FIRMADO (D-029)** | `product_brief_v2.json` — **PHASE 0 CERRADA**; build trigger D-024 disparado |
| Phase 1 | G-Phase-1-PRE | ✅ passed 2026-06-11 (10/10) | registrado en `value_equations.json.gate_pre_check` (check 10: dmu N/A por criterio hybrid-gate D-023) |
| Phase 1 | 1.1 Value Equation | 🔄 Priya ✅ FIRMADA (D-031) · Dana/Marcus/Héctor draft | `value_equations.json` — Priya 960 (débil, bloqueo blando sancionado D-031, weakest=likelihood) · Dana 1260 · Marcus 1680 · Héctor 672 (todos weakest=likelihood salvo Héctor=effort); **esperando firma del SET** |
| Phase 1 | Multi-avatar transversal | 🔄 draft propuesto | `multi_avatar_decision.json` — **separate_strategies** (3 de 4 hard fallan; la evidencia confirma D-009) · `strategies.json` — strat_priya_v1 lista para nacer (demand_type=**mixed** propuesto, primer uso de E1); **esperando firma del set** |
| Phase 1 | 1.2–1.4 | ⏳ pendientes | 1.2 stack (ataca likelihood — el gap es estructural: pre-PMF sin prueba ×3 avatares) · pricing créditos + modelo de costo IA (dependencia parqueada 0.1; insumo real: `project_llm_calls` en prod) · 1.3 risk/urgency · 1.4 naming DEFINITIVO |
| Phase 2–5 | — | ⏳ | spec Phase 1 validada vs corpus 2026-06-11 (v1.6, D-030) — cabo suelto R5 cerrado |

## Hechos clave capturados
- **Idea:** SaaS AI-first que guía a no-expertos de "tengo una idea" a "tengo estrategia de marketing accionable".
- **Diferenciador (la joya):** orquestación paralela multi-avatar — N avatares, cada uno con su estrategia versionada y su loop Phase 1→5.
- **Business context:** híbrido con lead B2C (individuos), ciclo reflexivo, suscripción+créditos, internacional con foco US/inglés, multimodal.
- **Nombre:** "Sandi" es working name (aleatorio); dudas por competencia/dominio → finalizar en Phase 1.4.
- **Mercado (0.2):** enorme (36M PYMEs, 5.6M nuevas/año, 29.8M solopreneurs); ~la mitad sin estrategia formal → **educar es la cuña**; espacio "AI marketing tool" saturado; `offer_strategy = create_demand`. Veredicto 🟢/🟡.
- **ICP (0.2.5, cerrado v2 — D-023, supersede D-022):** beachhead = **expertos en lo suyo** (la velera, el del gym, el de n8n, el coach) con **oferta propia ya monetizando** (local/boca-a-boca/marketplace/online cuentan), que **no saben empezar o escalar su marketing online**, con >1 público. 3 must-have: `own_craft_offer_monetized` · `multi_audience` (selector de la joya D-009) · `diy_going_online`. 2 deal-breakers: `no_own_offer` (afiliado/dropship/MLM) · `marketing_delegated` (agencia = puerta B2B futura). Gate passed sobre bloque B2C; `B2B_only` parked. Claims-incompatibles → `negative_personas` en 0.3. Cierra el bloque 1 del BMC. **Nota de método:** D-022 cayó el mismo día por un malentendido semántico ("expertise" ≠ solo productos de conocimiento) que el paso 0.3 destapó — el wizard reformula exactamente para esto.
- **Producto (principios definidos):** Setup Agent guiado (no chat libre); glass-box (no caja negra); educación adaptativa + `user_knowledge_profile`; conexión humana portable (SOUL + patrones + memoria + evals, model-agnostic); memoria de agente por proyecto (plan interno mutable + lessons/best-practices/decisions). Privacidad 3-capas.

## Dependencias parqueadas
- Modelo de costo de IA por avatar/ciclo → insumo de Phase 1 Pricing y del sistema de créditos.

## Notas
- Este run se construyó vía la simulación del Setup Agent (formato wizard guiado) — ver `specs/spec_Phase_0_Setup_Agent.md`.
- **0.3 (cerrado — D-025/026/027):** persona primario = "el experto en lo suyo que ya vende y está perdido en el marketing online" (6 dolores con fuente real). 4 avatares: 🧁 Dana (Lanzadora digital) · ⚙️ Marcus (Estancado, 2 públicos) · 📦 Priya (Enjaulada del marketplace) · 🚜 Héctor (Ruta local, fricción digital alta). **Priya enciende el primer ciclo.** 2 anti-personas: claims-imposibles (ético) + delegador total (high-support-cost). Cluster pre-launch ≠ anti-target (2ª ola / Módulo A).
- **2026-06-10 — giro en 0.3, RESUELTO (D-023):** al abrir el paso de persona, el corte por profesión no le cuadró al operador y emergió el malentendido semántico de "expertise". Aclaración del operador: experto en LO SUYO (craft), monetización requerida se mantiene, "empezar/escalar" refiere al marketing online. Enmienda firmada vía `decision_supersede` (D-022 → D-023). Avatares candidatos (ambos ya monetizan; eje = madurez del marketing online): **Lanzador digital** (vende local, "¿cómo empiezo online?") / **Estancado** (vende online, "¿cómo crezco?").
