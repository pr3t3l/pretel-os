# Run: Sandi — log

**Qué es:** el primer run de la metodología marketing-os. Sandi (el sistema de marketing AI-first) usándose a sí mismo como caso de prueba. Sirve de ejemplo trabajado (CAG) + fixture de eval.

## Estado

| Fase | Sub-paso | Estado | Artefacto |
|---|---|---|---|
| Phase 0 | 0.1 Business Context | ✅ cerrado | `business_context.json` |
| Phase 0 | 0.2 Mercado | ✅ cerrado | `demand_quantification.md` |
| Phase 0 | 0.2.5 ICP | ✅ cerrado | `icp.json` (D-022) |
| Phase 0 | 0.3 Persona + Avatares | ⏭️ siguiente | — |
| Phase 0 | 0.4 Competencia | pendiente | — |
| Phase 1–5 | — | pendiente | — |

## Hechos clave capturados
- **Idea:** SaaS AI-first que guía a no-expertos de "tengo una idea" a "tengo estrategia de marketing accionable".
- **Diferenciador (la joya):** orquestación paralela multi-avatar — N avatares, cada uno con su estrategia versionada y su loop Phase 1→5.
- **Business context:** híbrido con lead B2C (individuos), ciclo reflexivo, suscripción+créditos, internacional con foco US/inglés, multimodal.
- **Nombre:** "Sandi" es working name (aleatorio); dudas por competencia/dominio → finalizar en Phase 1.4.
- **Mercado (0.2):** enorme (36M PYMEs, 5.6M nuevas/año, 29.8M solopreneurs); ~la mitad sin estrategia formal → **educar es la cuña**; espacio "AI marketing tool" saturado; `offer_strategy = create_demand`. Veredicto 🟢/🟡.
- **ICP (0.2.5, cerrado — D-022):** beachhead = solopreneurs/creadores que venden su expertise y le hablan a >1 público (US, con ingreso, online-native). 3 must-have: expertise propia monetizando · ≥2 públicos (el selector de la joya D-009) · online-native DIY. 2 deal-breakers: sin oferta propia (afiliado/dropship/MLM) · marketing delegado (agencia = puerta B2B futura). Gate passed sobre bloque B2C; `B2B_only` parked explícito. Claims-incompatibles (get-rich-quick, salud-milagro) → se deciden en 0.3 como `negative_personas`. Cierra también el bloque 1 del BMC (Customer Segments).
- **Producto (principios definidos):** Setup Agent guiado (no chat libre); glass-box (no caja negra); educación adaptativa + `user_knowledge_profile`; conexión humana portable (SOUL + patrones + memoria + evals, model-agnostic); memoria de agente por proyecto (plan interno mutable + lessons/best-practices/decisions). Privacidad 3-capas.

## Dependencias parqueadas
- Modelo de costo de IA por avatar/ciclo → insumo de Phase 1 Pricing y del sistema de créditos.

## Notas
- Este run se construyó vía la simulación del Setup Agent (formato wizard guiado) — ver `specs/spec_Phase_0_Setup_Agent.md`.
- **2026-06-10 — giro en 0.3 (pendiente de confirmar):** al abrir el paso de persona, el operador rechazó el corte por profesión (coach/consultor/course creator) y propuso recorte **situacional** del beachhead: dueños de una **oferta propia (producto O servicio)** intentando venderla online sin saber cómo — "empezar" (ej. curso de n8n, sin arrancar) o "escalar" (ej. velas, estancado). Esto **enmienda D-022** (MH-1 exigía expertise + ya monetizando) → v2 propuesta en chat, **no aplicada** hasta confirmación. Los dos ejemplos del operador pasan el test 2-de-3 (trigger + lenguaje distintos) como candidatos a avatares: "Lanzador" / "Estancado".
