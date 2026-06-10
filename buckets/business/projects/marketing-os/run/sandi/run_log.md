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
| Phase 0 | **Rollup global** | 🔄 pendiente firma | `product_brief_v2.json` (gate global: todo ✓ salvo firma del operador) |
| Phase 1–5 | — | pendiente | — (al firmar: dispara build trigger D-024; sim sigue con Phase 1) |

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
